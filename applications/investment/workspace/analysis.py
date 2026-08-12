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
import shutil
import tempfile
from dataclasses import dataclass
from datetime import date
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
from applications.investment.workspace.cases import Case, CaseStore, JudgmentRecord

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
    """The institutional judgment, as the workspace presents it.

    Identified, dated, and marked with whether a later analysis has replaced it.
    A superseded judgment is still readable in full -- that is the point of
    keeping it.
    """

    judgment_id: str
    recorded_on: str
    superseded_by: str
    is_current: bool
    material_digest: str
    snapshot_id: str
    material_version: int
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


def request_judgment(
    store: CaseStore, case_id: str, recorded_on: str | None = None
) -> Judgment:
    """Run the engine over one case and record the judgment it reached.

    **Nothing is ever overwritten.** Each judgment is written once, into its own
    directory, and stays there. A later analysis supersedes it and leaves it
    resolvable, so a decision recorded against it can still be verified after
    the material has moved on.

    An analysis that reproduces the current judgment's record returns that
    judgment rather than creating a second one. The engine is deterministic, so
    an identical digest means the material reached exactly the same conclusion.
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

    # The slice reads a document from disk and writes its artifacts under
    # <output_root>/<packet id>. Both happen inside a scratch directory here, so
    # a failed run cannot leave a half-written judgment in the case, and the
    # finished artifacts are moved into place in one step.
    with tempfile.TemporaryDirectory() as scratch:
        document_path = Path(scratch) / "document.json"
        document_path.write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        produced = Path(scratch) / "produced"
        run = execute_slice(document_path, output_root=produced)

        _, record = store.append_judgment(
            case_id,
            record_digest=run.record_digest,
            recorded_on=recorded_on or date.today().isoformat(),
        )
        destination = store.judgment_directory(case_id, record.judgment_id)
        if not destination.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(run.output_directory), str(destination))

    return read_judgment(store, store.load(case_id), record.judgment_id)


def has_judgment(store: CaseStore, case_id: str) -> bool:
    """True when the case has reached at least one judgment."""
    return bool(store.load(case_id).judgments)


def rendered_report(
    store: CaseStore, case_id: str, judgment_id: str | None = None
) -> str:
    """Return one judgment's execution report, verbatim.

    Defaults to the judgment in force. Pass an id to read a superseded one --
    which is what a reader auditing an old decision is doing.
    """
    return _judgment_file(store, case_id, judgment_id, REPORT_FILE).read_text(
        encoding="utf-8"
    )


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


@dataclass(frozen=True)
class DigestCheck:
    """Whether one recorded decision can still be verified.

    Two independent claims, deliberately not collapsed:

    - **Reasoning identity** -- the judgment's record is on disk and carries the
      digest the decision cited.
    - **Material identity** -- the judgment was formed from the material the
      decision cited, and that material state is still in the case's registry.

    A decision can satisfy the first and fail the second. That is precisely the
    failure this layer exists to make visible, so ``resolves`` requires both.
    """

    entry_id: str
    judgment_id: str
    cited_digest: str
    found_digest: str
    artifacts_present: bool
    cited_material: str = ""
    found_material: str = ""
    snapshot_present: bool = False

    @property
    def record_resolves(self) -> bool:
        """True when the judgment's reasoning record is present and matches."""
        return self.artifacts_present and self.cited_digest == self.found_digest

    @property
    def material_resolves(self) -> bool:
        """True when the material the decision rested on is identified and intact.

        Decisions predating the material layer cite no material digest. They are
        reported as unresolved on this axis rather than silently passed: an
        unverifiable claim should not read as a verified one.
        """
        return (
            bool(self.cited_material)
            and self.snapshot_present
            and self.cited_material == self.found_material
        )

    @property
    def resolves(self) -> bool:
        """True when both the reasoning and the material behind a decision hold."""
        return self.record_resolves and self.material_resolves


def verify_ledger(store: CaseStore, case_id: str) -> tuple[DigestCheck, ...]:
    """Check that every decision on this case still resolves to its judgment.

    This is the institutional invariant made checkable. A decision cites a
    judgment id and a record digest; both must still lead to artifacts on disk
    that carry that digest, however many times the case has been re-analysed
    since. If this ever returns a failing check, a committee decision has become
    undefendable, which is the one failure this product cannot absorb.
    """
    case = store.load(case_id)
    checks: list[DigestCheck] = []
    for entry in case.ledger:
        directory = store.judgment_directory(case_id, entry.judgment_id)
        metadata_path = directory / "metadata.json"
        present = metadata_path.is_file() and (directory / RECORD_FILE).is_file()
        found = ""
        if present:
            found = str(
                json.loads(metadata_path.read_text(encoding="utf-8")).get(
                    "record_digest", ""
                )
            )

        snapshot = case.snapshot(entry.snapshot_id) if entry.snapshot_id else None
        checks.append(
            DigestCheck(
                entry_id=entry.entry_id,
                judgment_id=entry.judgment_id,
                cited_digest=entry.record_digest,
                found_digest=found,
                artifacts_present=present,
                cited_material=entry.material_digest,
                found_material=snapshot.material_digest if snapshot else "",
                snapshot_present=snapshot is not None,
            )
        )
    return tuple(checks)


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


def _resolve(case: Case, judgment_id: str | None) -> JudgmentRecord:
    """Return the requested judgment, or the one in force by default."""
    if judgment_id is None:
        current = case.current_judgment()
        if current is None:
            raise KeyError(f"{case.case_id} has no judgment")
        return current
    found = case.judgment(judgment_id)
    if found is None:
        raise KeyError(f"{case.case_id} has no judgment '{judgment_id}'")
    return found


def _judgment_file(
    store: CaseStore, case_id: str, judgment_id: str | None, name: str
) -> Path:
    """Locate one file inside one judgment's immutable artifact directory."""
    record = _resolve(store.load(case_id), judgment_id)
    return store.judgment_directory(case_id, record.judgment_id) / name


def read_judgment(
    store: CaseStore, case: Case, judgment_id: str | None = None
) -> Judgment:
    """Project one judgment's persisted record into the institutional view.

    Defaults to the judgment in force. A superseded judgment reads exactly as it
    did the day it was reached, because its record was never rewritten.
    """
    entry = _resolve(case, judgment_id)
    directory = store.judgment_directory(case.case_id, entry.judgment_id)
    record = json.loads((directory / RECORD_FILE).read_text(encoding="utf-8"))
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

    snapshot = case.snapshot(entry.snapshot_id)

    return Judgment(
        judgment_id=entry.judgment_id,
        recorded_on=entry.recorded_on,
        superseded_by=entry.superseded_by,
        is_current=entry.is_current,
        material_digest=entry.material_digest,
        snapshot_id=entry.snapshot_id,
        material_version=snapshot.version if snapshot else 0,
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
        record_digest=entry.record_digest,
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
