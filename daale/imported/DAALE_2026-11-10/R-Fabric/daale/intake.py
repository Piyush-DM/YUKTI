"""Deterministic intake: the user's material in, a validated R-Fabric case out.

No model is involved and nothing is interpreted. The user supplies the decision
question, the claims, and the documents. Intake does only what can be done
without judgement and can be checked afterwards:

- read each document as text and record a SHA-256 of its exact bytes;
- cut it into evidence items at paragraph boundaries, every item an exact
  substring of the document, with its line range (and its nearest Markdown
  heading, for ``.md`` files);
- assign evidence and source identifiers in manifest order;
- validate the result against the case schema.

What it deliberately does not do: invent claims, summarise, classify, guess a
page number, or fabricate a collection date. A field the material does not
supply is left out, not filled in. Formats it cannot read as text (PDF, Word,
scans) are refused with a message rather than half-parsed, because
``extraction_method`` would then be a lie.

Manifest (JSON)::

    {
      "case_id": "DD-2026-014",
      "decision_stage": "post_technical_due_diligence_approval",
      "decision_question": "Should we approve Vendor X?",
      "claims": [{"claim_id": "C1", "text": "Vendor X meets our security baseline."}],
      "documents": [
        {"path": "docs/security_report.md",
         "document_id": "DOC-SEC-1", "title": "Security report",
         "source_type": "DOCUMENT", "document_version": "2.1",
         "collected_at": "2026-10-02T09:00:00Z"}
      ]
    }

A document gives exactly one of ``path`` (a file, relative to the manifest) or
``text`` (the content inline, as the HTTP service receives it).
``decision_stage`` must equal the policy's ``decision_stage``; the engine
refuses a case whose stage differs from the policy it is run under.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import url2pathname

from .schemas import CASE_SCHEMA
from .validation import DaaleValidationError, validate_schema

SUPPORTED_SUFFIXES = {".txt", ".md"}
SOURCE_TYPES = {"DOCUMENT", "SYSTEM_RECORD", "INTERVIEW", "DECLARATION", "OTHER"}

MANIFEST_KEYS = {"case_id", "decision_stage", "decision_question", "claims", "documents"}
DOCUMENT_KEYS = {
    "path", "text", "format", "document_id", "title", "source_type",
    "document_version", "collected_at",
}

DEFAULT_MIN_CHARS = 200
DEFAULT_MAX_CHARS = 1500
DEFAULT_MAX_EVIDENCE = 30

_SEPARATOR = re.compile(r"\n[ \t]*\n+")
_HEADING = re.compile(r"^#{1,6}[ \t]+(.+?)[ \t]*#*[ \t]*$", re.MULTILINE)


class IntakeError(ValueError):
    """The material cannot be turned into a case, and why."""


def _sha256(data):
    return hashlib.sha256(data).hexdigest()


def _normalise(raw, path):
    if b"\x00" in raw:
        raise IntakeError(f"{path}: contains binary data; intake reads text files only")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise IntakeError(f"{path}: not valid UTF-8 text ({error})") from error
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _trimmed(text, start, end):
    while start < end and text[start].isspace():
        start += 1
    while end > start and text[end - 1].isspace():
        end -= 1
    return start, end


def _paragraph_spans(text):
    spans = []
    position = 0
    for match in _SEPARATOR.finditer(text):
        spans.append((position, match.start()))
        position = match.end()
    spans.append((position, len(text)))
    trimmed = (_trimmed(text, s, e) for s, e in spans)
    return [(s, e) for s, e in trimmed if e > s]


def _split_long(text, start, end, max_chars):
    """Cut an over-long paragraph at a sentence end, else a space, else hard."""
    pieces = []
    while end - start > max_chars:
        window = text[start:start + max_chars]
        cut = max_chars
        sentence = max(window.rfind(". "), window.rfind("? "), window.rfind("! "), window.rfind(".\n"))
        if sentence >= max_chars // 2:
            cut = sentence + 1
        else:
            space = max(window.rfind(" "), window.rfind("\n"))
            if space >= max_chars // 2:
                cut = space
        pieces.append((start, start + cut))
        start, _ = _trimmed(text, start + cut, end)
    pieces.append((start, end))
    return pieces


def chunk_spans(text, min_chars=DEFAULT_MIN_CHARS, max_chars=DEFAULT_MAX_CHARS):
    """Evidence spans for ``text``: ``(start, end)`` offsets, in document order.

    Every span is ``text[start:end]`` exactly. Paragraphs shorter than
    ``min_chars`` are joined to the one after them while the result stays within
    ``max_chars``; a paragraph longer than ``max_chars`` is cut at a sentence end.
    """
    if min_chars < 0 or max_chars < 1 or min_chars > max_chars:
        raise IntakeError("chunk limits must satisfy 0 <= min_chars <= max_chars")

    spans = []
    for start, end in _paragraph_spans(text):
        spans.extend(_split_long(text, start, end, max_chars))

    chunks = []
    current = None
    for start, end in spans:
        if current is None:
            current = [start, end]
        elif current[1] - current[0] < min_chars and end - current[0] <= max_chars:
            current[1] = end
        else:
            chunks.append((current[0], current[1]))
            current = [start, end]
    if current is not None:
        chunks.append((current[0], current[1]))
    return chunks


def _heading_at(headings, offset):
    """The nearest Markdown heading at or before ``offset``, if any."""
    found = None
    for position, title in headings:
        if position > offset:
            break
        found = title
    return found


def _check_keys(mapping, allowed, label):
    unknown = sorted(set(mapping) - allowed)
    if unknown:
        raise IntakeError(f"{label}: unknown field(s) {unknown}; allowed: {sorted(allowed)}")


def build_case(
    manifest,
    base_dir,
    min_chars=DEFAULT_MIN_CHARS,
    max_chars=DEFAULT_MAX_CHARS,
    max_evidence=DEFAULT_MAX_EVIDENCE,
    allow_paths=True,
):
    """Build and validate a case from a manifest dict and the files it names.

    ``allow_paths=False`` refuses file paths outright, for input that comes from
    outside (the HTTP service): a caller must never choose which server file is read.
    """
    if not isinstance(manifest, dict):
        raise IntakeError("manifest must be a JSON object")
    _check_keys(manifest, MANIFEST_KEYS, "manifest")
    missing = sorted(MANIFEST_KEYS - set(manifest))
    if missing:
        raise IntakeError(f"manifest is missing required field(s): {missing}")

    claims = manifest["claims"]
    if not isinstance(claims, list) or not claims:
        raise IntakeError("manifest 'claims' must be a non-empty list; claims are supplied by the user")
    for claim in claims:
        if not isinstance(claim, dict):
            raise IntakeError("each claim must be an object with claim_id and text")
        _check_keys(claim, {"claim_id", "text"}, "claim")
    claim_ids = [c.get("claim_id") for c in claims]
    if len(set(claim_ids)) != len(claim_ids):
        raise IntakeError(f"duplicate claim_id values: {sorted({i for i in claim_ids if claim_ids.count(i) > 1})}")

    documents = manifest["documents"]
    if not isinstance(documents, list) or not documents:
        raise IntakeError("manifest 'documents' must be a non-empty list")

    base = Path(base_dir).resolve() if base_dir is not None else None
    evidence = []

    for index, document in enumerate(documents, start=1):
        if not isinstance(document, dict):
            raise IntakeError(f"document {index}: must be an object")
        _check_keys(document, DOCUMENT_KEYS, f"document {index}")
        if ("path" in document) == ("text" in document):
            raise IntakeError(f"document {index}: give exactly one of 'path' or 'text'")

        if "path" in document:
            if not allow_paths or base is None:
                raise IntakeError(
                    f"document {index}: file paths are not accepted here; send the content as 'text'"
                )
            path = (base / document["path"]).resolve()
            if base != path and base not in path.parents:
                raise IntakeError(f"document {index}: {document['path']!r} escapes the manifest directory")
            if path.suffix.lower() not in SUPPORTED_SUFFIXES:
                raise IntakeError(
                    f"{path.name}: {path.suffix or 'no extension'} is not supported. Intake reads "
                    f"{sorted(SUPPORTED_SUFFIXES)} only; convert PDF, Word or scanned files to text first "
                    "so the extraction method recorded is true."
                )
            if not path.is_file():
                raise IntakeError(f"document {index}: file not found: {path}")
            raw = path.read_bytes()
            name, suffix, uri = path.name, path.suffix.lower(), path.as_uri()
        else:
            # Text sent inline (the HTTP service has no shared filesystem). The
            # bytes hashed are exactly the text received; there is no source_uri
            # because there is no file to re-read.
            inline = document["text"]
            if not isinstance(inline, str):
                raise IntakeError(f"document {index}: 'text' must be a string")
            raw = inline.encode("utf-8")
            name = document.get("title") or f"document-{index}"
            suffix = ".md" if document.get("format") == "markdown" else ".txt"
            uri = None

        text = _normalise(raw, name)
        if not text.strip():
            raise IntakeError(f"{name}: the document is empty")

        source_type = document.get("source_type", "DOCUMENT")
        if source_type not in SOURCE_TYPES:
            raise IntakeError(f"document {index}: source_type must be one of {sorted(SOURCE_TYPES)}")

        content_hash = _sha256(raw)
        source = {
            "source_id": f"S{index}",
            "source_type": source_type,
            "title": document.get("title") or name,
            "document_id": document.get("document_id") or f"DOC-{index}",
            "extraction_method": "PARSER",
            # Derived from the bytes, not invented, when the user gives no version.
            "document_version": document.get("document_version") or f"sha256:{content_hash[:12]}",
            "content_hash": content_hash,
        }
        if uri:
            source["source_uri"] = uri
        if document.get("collected_at"):
            source["collected_at"] = document["collected_at"]

        headings = (
            [(m.start(), m.group(1)) for m in _HEADING.finditer(text)]
            if suffix == ".md" else []
        )

        for start, end in chunk_spans(text, min_chars, max_chars):
            item_source = dict(source)
            item_source["paragraph"] = (
                f"lines {text.count(chr(10), 0, start) + 1}-{text.count(chr(10), 0, end) + 1}"
            )
            section = _heading_at(headings, start)
            if section:
                item_source["section"] = section
            evidence.append(
                {
                    "evidence_id": f"E{len(evidence) + 1}",
                    "text": text[start:end],
                    "source": item_source,
                }
            )

    if len(evidence) > max_evidence:
        raise IntakeError(
            f"{len(evidence)} evidence items exceeds the limit of {max_evidence}. Every kernel must "
            f"classify every claim against every evidence item ({len(claims)} claims x {len(evidence)} "
            f"items = {len(claims) * len(evidence)} relations per kernel), which exceeds what a model "
            "call reliably returns. Trim the material, raise --max-chars so items are larger, or "
            "raise --max-evidence knowingly."
        )

    case = {
        "case_id": manifest["case_id"],
        "decision_stage": manifest["decision_stage"],
        "decision_question": manifest["decision_question"],
        "claims": [{"claim_id": c["claim_id"], "text": c["text"]} for c in claims],
        "evidence": evidence,
    }
    try:
        validate_schema(case, CASE_SCHEMA, "Case built by intake")
    except DaaleValidationError as error:
        raise IntakeError(str(error)) from error
    return case


def load_manifest(path):
    path = Path(path)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise IntakeError(f"manifest not found: {path}") from error
    except json.JSONDecodeError as error:
        raise IntakeError(f"manifest is not valid JSON: {error}") from error


def build_case_from_file(manifest_path, **limits):
    manifest_path = Path(manifest_path)
    return build_case(load_manifest(manifest_path), manifest_path.resolve().parent, **limits)


def verify_provenance(case):
    """Re-check a case against the files on disk. Returns a list of problems.

    For every evidence item: the source file still exists, its bytes still hash
    to the recorded ``content_hash``, and the evidence text is still an exact
    substring of the document.
    """
    problems = []
    cache = {}
    for item in case["evidence"]:
        source = item["source"]
        uri = source.get("source_uri")
        label = f"{item['evidence_id']} ({source.get('document_id', source['source_id'])})"
        if not uri or not source.get("content_hash"):
            problems.append(f"{label}: no source_uri/content_hash recorded, so it cannot be verified")
            continue
        path = Path(url2pathname(urlparse(uri).path))
        if uri not in cache:
            if not path.is_file():
                cache[uri] = (None, None)
            else:
                raw = path.read_bytes()
                cache[uri] = (_sha256(raw), _normalise(raw, path.name))
        digest, text = cache[uri]
        if digest is None:
            problems.append(f"{label}: source file is missing: {path}")
        elif digest != source["content_hash"]:
            problems.append(f"{label}: file changed since intake (hash mismatch)")
        elif item["text"] not in text:
            problems.append(f"{label}: evidence text is not found in the source file")
    return problems


def describe(case):
    claims, items = len(case["claims"]), len(case["evidence"])
    documents = len({e["source"]["source_id"] for e in case["evidence"]})
    return (
        f"case {case['case_id']}: {claims} claim(s), {items} evidence item(s) from "
        f"{documents} document(s); {claims * items} relations required per kernel"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build an R-Fabric case from a material manifest.")
    parser.add_argument("manifest")
    parser.add_argument("--out", help="write the case JSON here (default: print it)")
    parser.add_argument("--min-chars", type=int, default=DEFAULT_MIN_CHARS)
    parser.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS)
    parser.add_argument("--max-evidence", type=int, default=DEFAULT_MAX_EVIDENCE)
    args = parser.parse_args(argv)

    try:
        case = build_case_from_file(
            args.manifest,
            min_chars=args.min_chars,
            max_chars=args.max_chars,
            max_evidence=args.max_evidence,
        )
    except IntakeError as error:
        print(f"Intake failed: {error}", file=sys.stderr)
        return 1

    problems = verify_provenance(case)
    if problems:
        print("Provenance check failed:\n  " + "\n  ".join(problems), file=sys.stderr)
        return 1

    print(describe(case), file=sys.stderr)
    payload = json.dumps(case, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
