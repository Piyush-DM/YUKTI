"""Execute the vertical slice and persist every stage.

The run is one straight line with no branches, read top to bottom in
``execute_slice``. Each stage writes its output before the next one starts, so a
reader can open any single file and see exactly what that stage produced without
re-running anything or trusting the final report's account of it.

Determinism. The pipeline itself is deterministic by construction (no clock, no
randomness, no I/O, no concurrency -- ``choir_prototype/README.md``). This module
adds the I/O the prototype refuses to do, and keeps the property by writing no
timestamp, no host detail and no run counter: the output directory is named by
packet id, JSON keys are sorted, and newlines are LF on every platform. Running
the slice twice over the same document overwrites the artifacts with identical
bytes.

Serialisation reuses ``choir_prototype.core.replay._canonical`` rather than
defining a second one. It is private, and importing it is deliberate: it is the
exact reduction the record digest is computed over, so the persisted record and
the digest that vouches for it cannot drift apart. A local copy would be a
second answer to the same question, and the first time the two disagreed the
artifacts would silently stop matching the hash.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from choir_prototype.core.pipeline import execute
from choir_prototype.core.replay import _canonical, record_digest, text_digest
from choir_prototype.core.report import render
from choir_prototype.domains import investment

from applications.investment.vertical_slice.parse import (
    SAMPLE_DOCUMENT,
    parse_document,
    read_document,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_ROOT = REPOSITORY_ROOT / "reports" / "vertical-slice"

# Stage number -> filename. The numbers are the pipeline order, so an `ls` of
# the output directory reads as the pipeline itself.
DOCUMENT_FILE = "01-document.json"
PACKET_FILE = "02-packet.json"
IR_FILE = "03-ir.json"
ARTIFACTS_FILE = "04-artifacts.json"
RECORD_FILE = "05-record.json"
REPORT_FILE = "06-report.txt"
METADATA_FILE = "metadata.json"

STAGE_FILES = (
    DOCUMENT_FILE,
    PACKET_FILE,
    IR_FILE,
    ARTIFACTS_FILE,
    RECORD_FILE,
    REPORT_FILE,
)


@dataclass(frozen=True)
class SliceRun:
    """What one execution of the slice produced.

    Carries digests rather than the objects themselves: the objects are on disk,
    and a caller that wants them should read the artifact, which is the whole
    point of persisting them.
    """

    packet_id: str
    output_directory: Path
    record_digest: str
    report_digest: str
    artifact_paths: tuple[Path, ...]


def execute_slice(
    document_path: Path = SAMPLE_DOCUMENT,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
) -> SliceRun:
    """Carry one document through the pipeline, writing each stage to disk."""
    # Stage 1 -- the document, as supplied.
    document_text = read_document(document_path)

    # Stage 2 -- parsing. Shape mapping only; see parse.py.
    packet = parse_document(document_text, origin=str(document_path))

    # Stages 3 to 5 -- translation, kernels, synthesis. This is the frozen
    # prototype called as a library; nothing here is new.
    result, synthesis = execute(packet, investment.DOMAIN)

    # Stage 6 -- the report, projected from the record. Recomputes nothing.
    report_text = render(result, synthesis)

    record = {
        "ir": _canonical(result.ir),
        "artifacts": _canonical(result.artifacts),
        "synthesis": _canonical(synthesis),
        "trace": _canonical(result.trace),
    }
    digest = record_digest(result, synthesis)
    report_hash = text_digest(report_text)

    directory = output_root / packet.id
    directory.mkdir(parents=True, exist_ok=True)

    _write_text(directory / DOCUMENT_FILE, document_text)
    _write_json(directory / PACKET_FILE, _canonical(packet))
    _write_json(directory / IR_FILE, record["ir"])
    _write_json(directory / ARTIFACTS_FILE, record["artifacts"])
    _write_json(directory / RECORD_FILE, record)
    _write_text(directory / REPORT_FILE, report_text + "\n")

    paths = tuple(directory / name for name in STAGE_FILES)
    _write_json(
        directory / METADATA_FILE,
        _metadata(packet.id, digest, report_hash, paths),
    )

    return SliceRun(
        packet_id=packet.id,
        output_directory=directory,
        record_digest=digest,
        report_digest=report_hash,
        artifact_paths=paths,
    )


def _metadata(
    packet_id: str,
    digest: str,
    report_hash: str,
    paths: tuple[Path, ...],
) -> dict[str, Any]:
    """Describe the run: what produced it, and how to check it did not change.

    ``record_digest`` is the prototype's own hash over the structured record,
    taken over the compact form ``json.dumps(record, sort_keys=True,
    separators=(",", ":"))``. It is therefore *not* the file hash of
    ``05-record.json``, which is written indented for reading. Both are listed
    so neither has to be guessed.
    """
    return {
        "packet_id": packet_id,
        "domain": investment.DOMAIN.name,
        "document_format": "yukti-investment-document/0.1",
        "record_digest": digest,
        "report_digest": report_hash,
        "stages": [
            {
                "stage": index,
                "file": path.name,
                "sha256": _file_digest(path),
            }
            for index, path in enumerate(paths, start=1)
        ],
    }


def _write_text(path: Path, text: str) -> None:
    """Write text with LF newlines, so output matches across platforms."""
    path.write_text(text, encoding="utf-8", newline="\n")


def _write_json(path: Path, payload: Any) -> None:
    """Write JSON with sorted keys, so two runs produce identical bytes."""
    _write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _file_digest(path: Path) -> str:
    """Hash a written artifact, so a reader can verify it independently."""
    return hashlib.sha256(path.read_bytes()).hexdigest()
