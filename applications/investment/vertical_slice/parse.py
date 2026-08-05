"""Document intake: sample document -> ``InvestmentPacket``.

**No reasoning occurs here**, and no interpretation either. This layer holds the
same discipline as ``choir_prototype/domains/investment/translator.py``: it maps
one shape onto another and preserves what the document said, including things
the document got wrong. A source label that no source defines survives intake,
because that is a fact about the document and the kernels downstream must be
able to see it.

Consequently the only errors raised here are *structural* -- a missing key, a
wrong JSON type, a field that is not a string. Vocabulary is deliberately not
validated: ``kind`` and ``status`` values the translator does not recognise fall
through to its own defaults (``ASSERTED`` and ``UNKNOWN``), which is the
conservative reading and is the translator's decision to make, not this
module's.

The document format is the deal packet serialised. It is not free text, and this
module performs no extraction. See
``docs/architecture/DECISION-002_document_intake_for_the_vertical_slice.md``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from choir_prototype.domains.investment.packets import (
    DataPoint,
    InvestmentPacket,
    NotedConflict,
    SourceDocument,
)

DOCUMENT_VERSION = "yukti-investment-document/0.1"

# The one fixed sample document this slice runs. Not a search path, not a
# registry: one document, named here, per the slice's scope.
SAMPLE_DOCUMENT = (
    Path(__file__).resolve().parent / "documents" / "orbital-series-b.json"
)


def read_document(path: Path = SAMPLE_DOCUMENT) -> str:
    """Return the document's raw text.

    Read separately from parsing so the pipeline can persist the original input
    byte-for-byte as its first artifact, rather than a re-serialisation of it.
    """
    return path.read_text(encoding="utf-8")


def parse_document(text: str, origin: str) -> InvestmentPacket:
    """Parse document text into the packet shape the investment domain uses.

    ``origin`` names the document in error messages only. It does not enter the
    packet: the pipeline identifies runs by packet id, and adding a second
    identifier would create two answers to the same question.
    """
    try:
        raw = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{origin}: not valid JSON -- {exc}") from exc

    document = _require_object(raw, origin, "document")

    version = _require_str(document, "document_version", origin)
    if version != DOCUMENT_VERSION:
        raise ValueError(
            f"{origin}: document_version is {version!r}, expected {DOCUMENT_VERSION!r}"
        )

    return InvestmentPacket(
        id=_require_str(document, "id", origin),
        title=_require_str(document, "title", origin),
        company_name=_require_str(document, "company_name", origin),
        sector=_require_str(document, "sector", origin),
        stage=_require_str(document, "stage", origin),
        sources=tuple(
            SourceDocument(
                label=_require_str(entry, "label", where),
                origin=_require_str(entry, "origin", where),
                kind=_require_str(entry, "kind", where),
            )
            for entry, where in _entries(document, "sources", origin)
        ),
        data_points=tuple(
            DataPoint(
                metric=_require_str(entry, "metric", where),
                value=_require_str(entry, "value", where),
                source_labels=_require_str_tuple(entry, "source_labels", where),
                status=_require_str(entry, "status", where),
            )
            for entry, where in _entries(document, "data_points", origin)
        ),
        stated_assumptions=_require_str_tuple(document, "stated_assumptions", origin),
        noted_conflicts=tuple(
            NotedConflict(
                metric=_require_str(entry, "metric", where),
                note=_require_str(entry, "note", where),
            )
            for entry, where in _entries(document, "noted_conflicts", origin)
        ),
    )


def load_sample_packet(path: Path = SAMPLE_DOCUMENT) -> InvestmentPacket:
    """Read and parse the fixed sample document in one step."""
    return parse_document(read_document(path), origin=str(path))


def _require_object(value: Any, origin: str, where: str) -> dict[str, Any]:
    """Return ``value`` as a JSON object, or fail naming where it was found."""
    if not isinstance(value, dict):
        raise ValueError(f"{origin}: {where} must be a JSON object")
    return value


def _entries(
    document: dict[str, Any], key: str, origin: str
) -> list[tuple[dict[str, Any], str]]:
    """Return each object in a JSON array, paired with a locator for errors."""
    value = document.get(key)
    if not isinstance(value, list):
        raise ValueError(f"{origin}: '{key}' must be a JSON array")
    return [
        (_require_object(entry, origin, f"{key}[{index}]"), f"{origin} {key}[{index}]")
        for index, entry in enumerate(value)
    ]


def _require_str(source: dict[str, Any], key: str, origin: str) -> str:
    """Return a required string field, or fail naming the field."""
    value = source.get(key)
    if not isinstance(value, str):
        raise ValueError(f"{origin}: '{key}' is required and must be a string")
    return value


def _require_str_tuple(
    source: dict[str, Any], key: str, origin: str
) -> tuple[str, ...]:
    """Return a required array-of-strings field, in document order."""
    value = source.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{origin}: '{key}' must be a JSON array of strings")
    return tuple(value)
