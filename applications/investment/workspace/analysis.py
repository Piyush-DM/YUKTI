"""Requesting an institutional judgment, and reading one back.

This is the only place in the product that touches the reasoning engine, and it
touches it in exactly one way: it composes the case material into the document
format the vertical slice already accepts, hands it to
``vertical_slice.execute_slice``, and then *reads the persisted record back* to
build what the screen shows.

Reading the record back rather than keeping the live objects is deliberate. The
prototype's central guarantee is that a view is a projection of the record and
can never disagree with the reasoning (commitment E9, and the
``projection-integrity`` check). Building the institutional view from
``05-record.json`` extends that guarantee into the product: the workspace
cannot display a conclusion the record does not contain, because the record is
the only thing it has.

Nothing here reasons. Every judgment on the screen was computed by the engine;
this module relabels it into institutional language and groups it the way a
committee reads. Where a label is missing it falls through to the engine's own
wording rather than inventing one.
"""

from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from applications.investment.vertical_slice.parse import (
    DOCUMENT_VERSION,
    read_document,
)
from applications.investment.vertical_slice.run import (
    RECORD_FILE,
    REPORT_FILE,
    execute_slice,
)
from applications.investment.workspace import diligence
from applications.investment.workspace.cases import Case, CaseStore

# Stances the engine reports, in institutional wording.
_STANCE_LABELS = {
    "supports": "Supports",
    "opposes": "Opposes",
    "conditional": "Conditional",
    "neutral": "Neutral",
}

# Confidence bands, in institutional wording.
_BAND_LABELS = {
    "high": "High",
    "moderate": "Moderate",
    "low": "Low",
    "insufficient": "Insufficient",
}

# What each outcome means for the committee. The engine names the outcome; this
# says what the institution is being told to do about it, which is the thing a
# reader actually needs and the thing a bare enum value does not carry.
_OUTCOME_GUIDANCE = {
    "proceed": "The material supports proceeding.",
    "proceed with conditions": (
        "The material supports proceeding, subject to the conditions below "
        "being resolved."
    ),
    "decline": "The material does not support proceeding.",
    "contested": (
        "Review areas reached opposing conclusions and the margin between them "
        "is too narrow to call. This is a reported disagreement, not a failure."
    ),
    "insufficient basis": (
        "Too little of the diligence schedule was available to reach a "
        "judgment. The case needs more material, not more analysis."
    ),
}


@dataclass(frozen=True)
class FindingView:
    """One conclusion, as it appears under a review area."""

    stance: str
    topic: str
    statement: str
    evidence_labels: tuple[str, ...]


@dataclass(frozen=True)
class ReviewAreaView:
    """What one review area concluded, and how far it could see."""

    review_area: str
    confidence: str
    confidence_note: str
    coverage: str
    findings: tuple[FindingView, ...]
    unresolved_questions: tuple[str, ...]
    assumptions: tuple[str, ...]


@dataclass(frozen=True)
class TopicPositionView:
    """Where the review areas landed on one topic."""

    topic: str
    positions: tuple[tuple[str, str, str], ...]  # (review area, stance, statement)


@dataclass(frozen=True)
class Judgment:
    """The institutional judgment, as the workspace presents it."""

    recommendation: str
    outcome_guidance: str
    confidence: str
    confidence_note: str
    rationale: tuple[str, ...]
    conditions: tuple[FindingView, ...]
    review_areas: tuple[ReviewAreaView, ...]
    agreements: tuple[TopicPositionView, ...]
    disagreements: tuple[TopicPositionView, ...]
    unresolved_questions: tuple[str, ...]
    remaining_uncertainty: tuple[str, ...]
    outstanding_schedule_items: tuple[str, ...]
    record_digest: str


class MaterialIncomplete(ValueError):
    """The case cannot be analysed yet, and the reason is the user's to fix."""


def request_judgment(store: CaseStore, case_id: str) -> Judgment:
    """Run the engine over one case and return the judgment it reached.

    The engine artifacts land beside the case file, so the audit trail for a
    judgment sits next to the material that produced it.
    """
    case = store.load(case_id)
    if not case.sources:
        raise MaterialIncomplete(
            "Add at least one source to the register before requesting analysis."
        )
    if not case.figures:
        raise MaterialIncomplete(
            "Record at least one figure from the diligence schedule before "
            "requesting analysis."
        )

    document = compose_document(case)

    # The slice reads a document from disk, so the composed document is written
    # to a temporary file and the slice's own verbatim copy becomes the record.
    with tempfile.TemporaryDirectory() as scratch:
        document_path = Path(scratch) / f"{case.case_id}.json"
        document_path.write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        execute_slice(document_path, output_root=store.root)

    return read_judgment(store, case)


def has_judgment(store: CaseStore, case_id: str) -> bool:
    """True when an analysis has been run and its record is on disk."""
    return (store.directory(case_id) / RECORD_FILE).is_file()


def rendered_report(store: CaseStore, case_id: str) -> str:
    """Return the full execution report for the audit view, verbatim."""
    return (store.directory(case_id) / REPORT_FILE).read_text(encoding="utf-8")


def compose_document(case: Case) -> dict[str, Any]:
    """Build the engine document from the case material.

    A shape mapping and nothing more, held to the same discipline as the rest of
    the intake path: what the institution recorded is what the engine sees.
    Case metadata that exists for people rather than for reasoning -- the owner,
    the date the case was opened, the requested decision, the thesis -- is
    deliberately not passed through. It would change the document, and therefore
    the record digest, without changing a single conclusion.
    """
    return {
        "document_version": DOCUMENT_VERSION,
        "id": case.case_id,
        "title": case.title,
        "company_name": case.company,
        "sector": case.sector,
        "stage": case.stage,
        "sources": [
            {"label": source.label, "origin": source.origin, "kind": source.kind}
            for source in case.sources
        ],
        "data_points": [
            {
                "metric": figure.metric,
                "value": figure.value,
                "source_labels": list(figure.source_labels),
                "status": figure.status,
            }
            for figure in case.figures
        ],
        "stated_assumptions": list(case.assumptions),
        "noted_conflicts": [
            {"metric": conflict.metric, "note": conflict.note}
            for conflict in case.flagged_conflicts
        ],
    }


def reference_material() -> dict[str, Any]:
    """Return the worked example's material, in the shape the intake form posts.

    This is the case the reference implementation carries, offered so a first
    time user can walk the whole workflow without first typing fifteen figures.
    It is labelled as reference material everywhere it appears; it is a worked
    example, not a demonstration fixture, and it is read from the reference
    implementation's own document rather than copied here.
    """
    document = json.loads(read_document())
    return {
        "sources": document["sources"],
        "figures": [
            {
                "metric": point["metric"],
                "value": point["value"],
                "status": point["status"],
                "source_labels": point["source_labels"],
            }
            for point in document["data_points"]
        ],
        "assumptions": document["stated_assumptions"],
        "flagged_conflicts": document["noted_conflicts"],
    }


def read_judgment(store: CaseStore, case: Case) -> Judgment:
    """Project the persisted record into the institutional judgment view."""
    record = json.loads(
        (store.directory(case.case_id) / RECORD_FILE).read_text(encoding="utf-8")
    )
    synthesis = record["synthesis"]
    artifacts = record["artifacts"]
    evidence_labels = _evidence_labels(record["ir"])

    review_areas = tuple(
        _review_area_view(artifact, evidence_labels) for artifact in artifacts
    )

    conditions = tuple(
        finding
        for area in review_areas
        for finding in area.findings
        if finding.stance == _STANCE_LABELS["conditional"]
    )

    unresolved = tuple(
        question for area in review_areas for question in area.unresolved_questions
    )

    outstanding = tuple(
        f"{entry.label} ({entry.review_area})"
        for entry in diligence.outstanding(case.recorded_metrics())
    )

    recommendation = str(synthesis["recommendation"])

    return Judgment(
        recommendation=recommendation.title(),
        outcome_guidance=_OUTCOME_GUIDANCE.get(recommendation, ""),
        confidence=_band(synthesis["confidence"]),
        confidence_note=_prose(synthesis["confidence_limiting_factor"]),
        rationale=tuple(_prose(line) for line in synthesis["rationale"]),
        conditions=conditions,
        review_areas=review_areas,
        agreements=tuple(_topic_view(view) for view in synthesis["agreements"]),
        disagreements=tuple(_topic_view(view) for view in synthesis["disagreements"]),
        unresolved_questions=unresolved,
        remaining_uncertainty=tuple(
            _prose(line) for line in synthesis["remaining_uncertainty"]
        ),
        outstanding_schedule_items=outstanding,
        record_digest=_digest_from_metadata(store, case.case_id),
    )


def _digest_from_metadata(store: CaseStore, case_id: str) -> str:
    """Read the record digest the slice already computed, rather than re-hashing."""
    metadata_path = store.directory(case_id) / "metadata.json"
    if not metadata_path.is_file():
        return ""
    return str(
        json.loads(metadata_path.read_text(encoding="utf-8")).get("record_digest", "")
    )


def _evidence_labels(ir: dict[str, Any]) -> dict[str, str]:
    """Map evidence ids to the source description a reader will recognise."""
    return {entry["id"]: entry["source"] for entry in ir["evidence"]}


def _review_area_view(
    artifact: dict[str, Any], evidence_labels: dict[str, str]
) -> ReviewAreaView:
    """Relabel one engine artifact as a review area."""
    confidence = artifact["confidence"]
    return ReviewAreaView(
        review_area=diligence.label_for_review_area(str(artifact["kernel_name"])),
        confidence=_band(confidence["band"]),
        confidence_note=_prose(confidence["limiting_factor"]),
        coverage=_prose(confidence["coverage"]),
        findings=tuple(
            FindingView(
                stance=_STANCE_LABELS.get(
                    str(finding["stance"]), str(finding["stance"])
                ),
                topic=diligence.label_for_topic(str(finding["topic"])),
                statement=_prose(finding["statement"]),
                evidence_labels=tuple(
                    evidence_labels.get(evidence_id, evidence_id)
                    for evidence_id in finding["evidence_ids"]
                ),
            )
            for finding in artifact["findings"]
        ),
        unresolved_questions=tuple(
            _prose(question) for question in artifact["unresolved_questions"]
        ),
        assumptions=tuple(_prose(entry) for entry in artifact["assumptions"]),
    )


def _topic_view(view: dict[str, Any]) -> TopicPositionView:
    """Relabel one topic grouping from the synthesis."""
    return TopicPositionView(
        topic=diligence.label_for_topic(str(view["topic"])),
        positions=tuple(
            (
                diligence.label_for_review_area(str(position["kernel_name"])),
                _STANCE_LABELS.get(str(position["stance"]), str(position["stance"])),
                _prose(position["statement"]),
            )
            for position in view["positions"]
        ),
    )


def _band(value: Any) -> str:
    """Relabel a confidence band."""
    return _BAND_LABELS.get(str(value), str(value))


def _prose(value: Any) -> str:
    """Relabel internal names inside a sentence the engine composed."""
    return diligence.institutional_text(str(value))
