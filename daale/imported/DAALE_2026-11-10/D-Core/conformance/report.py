"""Rendering the conformance lock. A projection, and nothing more.

The research freeze §9 states the rule this module obeys: "Components record
their own working as they compute; views only format it. Nothing is
reconstructed after the fact." Every value printed here was decided in
``lock.py``. This module makes no judgement, resolves no evidence, and computes
no outcome -- it reads a ``ConformanceReport`` and lays it out.

That is also commitment A8 applied to DAALE's own first artifact. A conformance
lock whose renderer could disagree with its own result would be a poor advert
for the property it exists to check.

Output is deterministic: no clock, no paths that vary by machine, commitments in
the order the freeze states them. Two runs against the same tree produce
byte-identical text, which is what makes the artifact worth committing to a
review.
"""

from __future__ import annotations

import json
from typing import Any

from daale.conformance.classification import classification_for
from daale.conformance.lock import CommitmentResult, ConformanceReport, Outcome

_RULE = "=" * 78
_THIN = "-" * 78

_OUTCOME_LABELS = {
    Outcome.CONFORMING: "CONFORMING",
    Outcome.UNEXERCISED: "UNEXERCISED",
    Outcome.UNRESOLVED: "UNRESOLVED",
}


def _commitment_block(result: CommitmentResult) -> list[str]:
    """Render one commitment, its outcome, and every citation behind it."""
    commitment = result.commitment
    label = _OUTCOME_LABELS[result.outcome]
    lines = [
        f"{commitment.commitment_id:<4} [{commitment.status.value}] {label}",
        f"     {commitment.statement}",
    ]

    for item in result.evidence:
        mark = "ok  " if item.resolved else "MISS"
        lines.append(
            f"       {mark} {item.evidence.kind.value:<8} "
            f"{item.evidence.name} -- {item.detail}"
        )

    if not result.evidence:
        lines.append("       --   no evidence cited")

    return lines


def render(report: ConformanceReport) -> str:
    """Render the full conformance lock as inspectable text."""
    lines = [
        _RULE,
        "DAALE CONFORMANCE LOCK -- CHOIR v0.1 FROZEN COMMITMENTS",
        _RULE,
        "",
        "Source of commitments : CHOIR_v0.1_RESEARCH_FREEZE.md section 3",
        "Subject               : choir_prototype (read, never imported)",
        f"Commitments           : {len(report.results)}",
        "",
        "Status D = demonstrated - A = assumed - S = specified, not implemented",
        "",
    ]

    group = ""
    for result in report.results:
        if result.commitment.group != group:
            group = result.commitment.group
            lines.extend([_THIN, group.upper(), _THIN])
        lines.extend(_commitment_block(result))
        lines.append("")

    lines.extend(
        [
            _RULE,
            "SUMMARY",
            _RULE,
            f"  conforming   : {len(report.conforming)}",
            f"  unexercised  : {len(report.unexercised)}",
            f"  unresolved   : {len(report.unresolved)}",
            "",
        ]
    )

    if report.unresolved:
        lines.append("BROKEN LINKS -- cited evidence no longer exists:")
        for result in report.unresolved:
            missing = ", ".join(
                item.evidence.name for item in result.evidence if not item.resolved
            )
            lines.append(f"  {result.commitment.commitment_id}: {missing}")
        lines.append("")

    if report.unsupported_claims:
        lines.append("TRACEABILITY HOLES -- marked demonstrated, but nothing is cited:")
        for result in report.unsupported_claims:
            lines.append(
                f"  {result.commitment.commitment_id}: {result.commitment.statement}"
            )
        lines.append("")

    if report.unexercised:
        lines.append("UNEXERCISED, CLASSIFIED -- why each gap exists, not a work list:")
        for result in report.unexercised:
            entry = classification_for(result.commitment.commitment_id)
            label = entry.category.value if entry else "unclassified"
            lines.append(f"  {result.commitment.commitment_id:<4} {label}")
            if entry is not None:
                lines.append(f"       source: {entry.source}")
        lines.append("")

    lines.extend(
        [
            _THIN,
            f"STATUS: {'HOLDS' if report.holds else 'BROKEN'}"
            f" -- {'every citation resolves' if report.holds else 'see broken links'}",
            _THIN,
            "",
            "The lock verifies that the evidence the freeze relies on still",
            "exists. It does not re-run the reasoning: --replay and the",
            "prototype suite already do that, and a second answer to the same",
            "question is worse than none.",
            "",
        ]
    )

    return "\n".join(lines)


def _classification_of(commitment_id: str) -> dict[str, str] | None:
    """Return the recorded classification for a commitment, if it has one."""
    entry = classification_for(commitment_id)
    if entry is None:
        return None
    return {
        "category": entry.category.value,
        "source": entry.source,
        "rationale": entry.rationale,
    }


def as_dict(report: ConformanceReport) -> dict[str, Any]:
    """Return the same result as machine-readable data."""
    return {
        "scheme": "daale-conformance/1",
        "source": "CHOIR_v0.1_RESEARCH_FREEZE.md section 3",
        "subject": "choir_prototype",
        "holds": report.holds,
        "summary": {
            "commitments": len(report.results),
            "conforming": len(report.conforming),
            "unexercised": len(report.unexercised),
            "unresolved": len(report.unresolved),
        },
        "commitments": [
            {
                "id": result.commitment.commitment_id,
                "group": result.commitment.group,
                "statement": result.commitment.statement,
                "status": result.commitment.status.value,
                "outcome": result.outcome.value,
                "classification": _classification_of(result.commitment.commitment_id),
                "evidence": [
                    {
                        "kind": item.evidence.kind.value,
                        "name": item.evidence.name,
                        "resolved": item.resolved,
                        "detail": item.detail,
                    }
                    for item in result.evidence
                ],
            }
            for result in report.results
        ],
    }


def as_json(report: ConformanceReport) -> str:
    """Serialise the report deterministically."""
    return json.dumps(as_dict(report), indent=2, sort_keys=False) + "\n"
