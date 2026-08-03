"""Deterministic replay.

Two distinct claims are checked here, and they are not the same claim:

1. **Execution determinism.** Running the same packet again produces the same
   record -- same IR, same artifacts, same synthesis, same trace.
2. **Projection integrity.** Rendering the *same* record twice produces the same
   text. This is what makes the report and the inspection views trustworthy: they
   read the record, they do not re-derive it. If rendering were doing any
   reasoning of its own, this check would be the one to catch it.

A system could pass (1) and fail (2) -- that would mean the renderer has state.
A system could pass (2) and fail (1) -- that would mean the pipeline has state.
Both are checked separately.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, fields, is_dataclass
from enum import Enum
from typing import Any

from choir_prototype.core.inspection import inspect_all
from choir_prototype.core.domain import Domain
from choir_prototype.core.pipeline import execute
from choir_prototype.core.report import render
from choir_prototype.core.runtime import RunResult
from choir_prototype.core.synthesizer import Synthesis


def _canonical(value: Any) -> Any:
    """Reduce a record to primitives in a fixed order, for hashing."""
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _canonical(getattr(value, field.name))
            for field in sorted(fields(value), key=lambda item: item.name)
        }
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(key): _canonical(value[key]) for key in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def record_digest(result: RunResult, synthesis: Synthesis) -> str:
    """Hash the structured record: IR, artifacts, synthesis and trace."""
    payload = {
        "ir": _canonical(result.ir),
        "artifacts": _canonical(result.artifacts),
        "synthesis": _canonical(synthesis),
        "trace": _canonical(result.trace),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def text_digest(text: str) -> str:
    """Hash rendered output."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ReplayCheck:
    """One verification and its result."""

    name: str
    description: str
    passed: bool
    digest: str
    detail: str


@dataclass(frozen=True)
class ReplayReport:
    """The outcome of verifying a packet."""

    packet_id: str
    runs: int
    checks: tuple[ReplayCheck, ...]

    @property
    def passed(self) -> bool:
        """True when every check passed."""
        return all(check.passed for check in self.checks)


def verify(packet: Any, domain: Domain, runs: int = 3) -> ReplayReport:
    """Execute a packet repeatedly and verify both determinism claims."""
    executions = [execute(packet, domain) for _ in range(runs)]

    record_digests = [record_digest(result, synth) for result, synth in executions]
    report_digests = [render(result, synth) for result, synth in executions]
    report_hashes = [text_digest(text) for text in report_digests]
    inspect_hashes = [
        text_digest(inspect_all(result, synth)) for result, synth in executions
    ]

    # Projection integrity: same record in, same text out, rendered twice.
    first_result, first_synthesis = executions[0]
    reprojected = text_digest(render(first_result, first_synthesis))

    checks = (
        ReplayCheck(
            name="execution-determinism",
            description=f"{runs} executions produce an identical record",
            passed=len(set(record_digests)) == 1,
            digest=record_digests[0],
            detail=f"{len(set(record_digests))} distinct record digest(s)",
        ),
        ReplayCheck(
            name="report-determinism",
            description=f"{runs} executions render an identical report",
            passed=len(set(report_hashes)) == 1,
            digest=report_hashes[0],
            detail=f"{len(set(report_hashes))} distinct report digest(s)",
        ),
        ReplayCheck(
            name="inspection-determinism",
            description=f"{runs} executions render identical inspection views",
            passed=len(set(inspect_hashes)) == 1,
            digest=inspect_hashes[0],
            detail=f"{len(set(inspect_hashes))} distinct inspection digest(s)",
        ),
        ReplayCheck(
            name="projection-integrity",
            description="re-rendering one record reproduces the same report",
            passed=reprojected == report_hashes[0],
            digest=reprojected,
            detail=(
                "renderer holds no state; it reads the record"
                if reprojected == report_hashes[0]
                else "RENDERER IS NOT A PURE PROJECTION"
            ),
        ),
    )

    return ReplayReport(
        packet_id=domain.describe(packet).packet_id, runs=runs, checks=checks
    )


def render_replay(report: ReplayReport) -> str:
    """Format a replay verification for the terminal."""
    width = 78
    lines = [
        "=" * width,
        "DETERMINISTIC REPLAY VERIFICATION",
        "=" * width,
        f"Packet : {report.packet_id}",
        f"Runs   : {report.runs}",
        "",
    ]

    for check in report.checks:
        status = "PASS" if check.passed else "FAIL"
        lines.append(f"[{status}] {check.name}")
        lines.append(f"       {check.description}")
        lines.append(f"       {check.detail}")
        lines.append(f"       sha256: {check.digest}")
        lines.append("")

    lines.append("-" * width)
    lines.append(
        "RESULT: all checks passed"
        if report.passed
        else "RESULT: FAILED -- the run is not deterministic"
    )
    lines.append("-" * width)
    lines.append("")
    lines.append(
        "The record digest is stable across runs, so any two people running this"
    )
    lines.append("packet can compare one hash and know they saw the same reasoning.")
    return "\n".join(lines)
