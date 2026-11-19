"""Deterministic tripwires for evidence text that tries to command the reviewer. Not a defence by itself.

Evidence is untrusted text written by someone with an interest in the outcome. A model that reads it can be
talked into treating a sentence inside it as an instruction (live: HISTORIAN marked R2 SATISFIED "per the
explicit instruction" found in a management letter, in two runs of two). Nothing here can make that
impossible. What it does is cheap, model-free and recorded:

  * ``screen_evidence`` flags evidence items whose text is addressed to a model or an automated reviewer,
    tries to override earlier instructions, dictates a verdict, forbids objections, forges a role marker, or
    hides characters or an encoded payload. A flag is a fact about the document, not a reason to delete it:
    an attempt to steer the review is itself relevant evidence about the author, and the text stays in the
    case unchanged.
  * ``adopted_injected_verdicts`` checks the kernels' answers against what a flagged item dictated. A kernel
    that assigns exactly the dictated verdict while citing the flagged item has, on the face of it, taken
    the instruction. That check does not depend on what the model wrote, only on what it concluded.

Known limits (each is pinned in tests/test_evidence_integrity.py): a paraphrase, another language, a
look-alike alphabet (Cyrillic for Latin letters), or an instruction split across two items is not detected.
A detector built from patterns is a tripwire for the crude attacks and a record for the rest. The policy
decides what a flag means; with no policy asking for it, nothing in the engine changes.
"""

import re
import unicodedata

_SNIPPET = 160

# Text addressed to a model or an automated reviewer, not about one.
_ADDRESSES_MODEL = (
    r"\b(?:note|message|instruction|instructions|attention|reminder|request|memo)s?\s+(?:to|for)\s+"
    r"(?:the\s+|any\s+|this\s+)?(?:ai|a\.i\.|llm|language\s+model|(?:ai|reviewing|review)\s+model|model|"
    r"assistant|automated\s+(?:reviewer|system|review)|reviewing\s+(?:system|model|ai))\b",
    r"\b(?:ai|llm|language\s+model|assistant)\s*[:,]\s*(?:please\s+|you\s+(?:must|should|will)\s+)?"
    r"(?:ignore|disregard|mark|set|do\s+not|don't|treat|rate|conclude)\b",
    r"\bif\s+you\s+are\s+an?\s+(?:ai|llm|language\s+model|assistant)\b",
    r"\bsystem\s+(?:override|note|message)\s*:",
)
_OVERRIDES = (
    r"\b(?:ignore|disregard|forget|override|bypass)\b[^.]{0,50}\b(?:previous|prior|above|earlier|other|any|all)\b"
    r"[^.]{0,40}\b(?:instructions?|evidence|findings?|rules?|polic(?:y|ies)|assessments?|challenges?)\b",
)
_SUPPRESSES = (
    r"\b(?:do\s+not|don't|never|must\s+not)\b[^.]{0,30}\b(?:raise|issue|add|report|flag|mention|record)\b"
    r"[^.]{0,30}\b(?:challenges?|contradictions?|concerns?|findings?|objections?)\b",
)
_ROLE_MARKUP = (
    r"(?:^|\n)\s*(?:system|assistant|developer)\s*[:>]",
    r"<\s*/?\s*(?:system|assistant|instructions?)\s*>",
    r"\[/?(?:inst|sys)\]",
    r"(?:^|\n)\s*#{2,}\s*(?:system|instructions?|new\s+instructions?)\b",
)
_VERDICT_WORDS = {
    "satisfied": "SATISFIED",
    "met": "SATISFIED",
    "passed": "SATISFIED",
    "not satisfied": "NOT_SATISFIED",
    "not_satisfied": "NOT_SATISFIED",
    "supported": "SUPPORTED",
    "contradicted": "CONTRADICTED",
    "unknown": "UNKNOWN",
}
# "mark requirement R2 as SATISFIED", "set C1 to supported", "rate R3 = not satisfied"
_DICTATES = (
    r"\b(?:mark|set|rate|record|assess|classify|label|score|treat|consider)\b[^.]{0,60}?"
    r"\b(?:requirement|req\.?|claim)?\s*\b([rc]\d+)\b[^.]{0,30}?\b(?:as|to|=)\s*"
    r"(satisfied|not[ _]satisfied|supported|contradicted|unknown|met|passed)\b",
)
_ENCODED = r"[A-Za-z0-9+/]{64,}={0,2}"

_RULES = (
    ("addresses_model", _ADDRESSES_MODEL),
    ("overrides_prior_instructions", _OVERRIDES),
    ("suppresses_review", _SUPPRESSES),
    ("role_markup", _ROLE_MARKUP),
)


def normalise(text):
    """Text as a reader would see it: compatibility-normalised, invisible characters removed, lower case."""
    text = unicodedata.normalize("NFKC", str(text))
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Cf")
    return re.sub(r"[ \t\r\f\v]+", " ", text).casefold()


def _hidden_characters(text):
    return any(
        unicodedata.category(ch) == "Cf" or (unicodedata.category(ch) == "Cc" and ch not in "\n\t\r")
        for ch in str(text)
    )


def _dictated_verdicts(norm):
    found = []
    for pattern in _DICTATES:
        for match in re.finditer(pattern, norm):
            verdict = _VERDICT_WORDS[match.group(2).replace("  ", " ")]
            found.append({"target_id": match.group(1).upper(), "status": verdict, "text": match.group(0)[:_SNIPPET]})
    return found


def screen_evidence(case):
    """One entry per flagged evidence item: ``{"evidence_id", "flags", "spans", "dictated"}``.

    ``dictated`` lists the (target, verdict) pairs the text tells a reviewer to record. Items with no flag
    are omitted. The case is not modified.
    """
    flagged = []
    for item in case.get("evidence", []):
        raw = item.get("text", "")
        norm = normalise(raw)
        flags, spans = [], []
        for name, patterns in _RULES:
            for pattern in patterns:
                match = re.search(pattern, norm)
                if match:
                    flags.append(name)
                    spans.append(match.group(0)[:_SNIPPET].strip())
                    break
        dictated = _dictated_verdicts(norm)
        if dictated:
            flags.append("dictates_verdict")
            spans.extend(entry["text"] for entry in dictated)
        if _hidden_characters(raw):
            flags.append("hidden_characters")
        if re.search(_ENCODED, norm.replace("\n", "")) and len(raw) > 0:
            # a long unbroken run of base64-looking characters is not prose
            flags.append("encoded_payload")
        if flags:
            flagged.append({
                "evidence_id": item["evidence_id"],
                "flags": sorted(set(flags)),
                "spans": spans,
                "dictated": dictated,
            })
    return flagged


def adopted_injected_verdicts(flagged, base_outputs):
    """Kernel findings that record exactly what a flagged item dictated while citing that item.

    ``base_outputs`` maps kernel id to ``{"output": {...}}``. Returns one entry per such finding. A kernel
    that merely reports the instruction (a CHALLENGE or a RISK) is not listed: only an assessment that
    assigns the dictated status to the dictated target and cites the flagged item.
    """
    adopted = []
    for item in flagged:
        for dictated in item["dictated"]:
            for kernel_id, data in base_outputs.items():
                for finding in data["output"].get("findings", []):
                    if finding.get("finding_type") not in ("REQUIREMENT_ASSESSMENT", "CLAIM_ASSESSMENT"):
                        continue
                    if (
                        finding.get("target_id") == dictated["target_id"]
                        and finding.get("status") == dictated["status"]
                        and item["evidence_id"] in finding.get("evidence_ids", [])
                    ):
                        adopted.append({
                            "kernel": kernel_id,
                            "finding_id": finding.get("finding_id"),
                            "evidence_id": item["evidence_id"],
                            "target_id": dictated["target_id"],
                            "status": dictated["status"],
                        })
    return adopted
