"""The kernel runtime.

Responsibilities, and nothing beyond them:

- dispatch kernels, one at a time, in a fixed order
- collect their artifacts
- validate those artifacts against the IR they claim to have read
- expose an execution trace

Execution is sequential and single-threaded. That is not a limitation being
tolerated -- it is what makes the run trivially reproducible.
"""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Sequence

from choir_prototype.core.contracts import Artifact, Kernel
from choir_prototype.core.ir import ChoirIR


class ArtifactValidationError(Exception):
    """Raised when a kernel returns an artifact the runtime cannot accept."""


@dataclass(frozen=True)
class TraceEntry:
    """One recorded step of the run.

    ``inputs`` and ``outputs`` name what crossed the boundary at this step, so a
    reader can follow data through the pipeline rather than inferring it.
    ``notes`` carries anything that would otherwise be lost -- the predicates a
    kernel wanted but did not find, the checks the validator ran.
    """

    step: int
    stage: str
    component: str
    action: str
    detail: str
    inputs: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class RunResult:
    """Everything the runtime produced for one packet."""

    ir: ChoirIR
    artifacts: tuple[Artifact, ...]
    trace: tuple[TraceEntry, ...]


class Trace:
    """An append-only execution log.

    Steps are numbered rather than timestamped. A clock would make two runs of
    the same packet differ, which would defeat the point.
    """

    def __init__(self) -> None:
        """Start an empty trace."""
        self._entries: list[TraceEntry] = []

    def record(
        self,
        stage: str,
        component: str,
        action: str,
        detail: str,
        inputs: tuple[str, ...] = (),
        outputs: tuple[str, ...] = (),
        notes: tuple[str, ...] = (),
    ) -> None:
        """Append one step."""
        self._entries.append(
            TraceEntry(
                step=len(self._entries) + 1,
                stage=stage,
                component=component,
                action=action,
                detail=detail,
                inputs=inputs,
                outputs=outputs,
                notes=notes,
            )
        )

    def entries(self) -> tuple[TraceEntry, ...]:
        """Return the trace so far."""
        return tuple(self._entries)


def validate_artifact(artifact: Artifact, ir: ChoirIR) -> None:
    """Check an artifact is well formed and grounded in the IR it was given.

    The important check is the last one: a kernel may only cite claims and
    evidence that actually exist in the IR. Without it, a kernel could invent a
    reference and the report would carry a citation to nothing.
    """
    if not artifact.kernel_name:
        raise ArtifactValidationError("Artifact has no kernel name.")

    if not artifact.findings and not artifact.unresolved_questions:
        raise ArtifactValidationError(
            f"Kernel '{artifact.kernel_name}' returned neither findings nor "
            "unresolved questions; it must say something."
        )

    if not artifact.confidence.limiting_factor:
        raise ArtifactValidationError(
            f"Kernel '{artifact.kernel_name}' returned a confidence with no "
            "limiting factor, which means it was not derived."
        )

    known = ir.known_ids()
    for finding in artifact.findings:
        for reference in (*finding.claim_ids, *finding.evidence_ids):
            if reference not in known:
                raise ArtifactValidationError(
                    f"Kernel '{artifact.kernel_name}' finding '{finding.id}' "
                    f"cites unknown id '{reference}'."
                )

    for reference in artifact.evidence_references:
        if reference not in known:
            raise ArtifactValidationError(
                f"Kernel '{artifact.kernel_name}' references unknown evidence "
                f"'{reference}'."
            )


def predicate_coverage(
    ir: ChoirIR, kernel: Kernel
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return the predicates this kernel wanted, split into found and missing."""
    wanted = getattr(kernel, "PREDICATES", ())
    present = {claim.predicate for claim in ir.claims}
    found = tuple(name for name in wanted if name in present)
    missing = tuple(name for name in wanted if name not in present)
    return found, missing


def run_kernels(ir: ChoirIR, kernels: Sequence[Kernel], trace: Trace) -> RunResult:
    """Dispatch every kernel over the IR and collect validated artifacts."""
    trace.record(
        stage="4. kernel execution",
        component="runtime",
        action="dispatch-start",
        detail=f"{len(kernels)} kernels queued over IR {ir.metadata.packet_id}",
        inputs=(f"ir:{ir.metadata.packet_id}",),
        notes=tuple(kernel.name for kernel in kernels),
    )

    artifacts: list[Artifact] = []
    for kernel in kernels:
        found, missing = predicate_coverage(ir, kernel)
        trace.record(
            stage="4. kernel execution",
            component=kernel.name,
            action="kernel-start",
            detail=f"reading {len(found)} of {len(found) + len(missing)} predicates",
            inputs=found,
            notes=((f"missing from packet: {', '.join(missing)}",) if missing else ()),
        )

        artifact = kernel.run(ir)

        cited = sorted(
            {
                reference
                for finding in artifact.findings
                for reference in (*finding.claim_ids, *finding.evidence_ids)
            }
        )
        trace.record(
            stage="4. kernel execution",
            component=kernel.name,
            action="kernel-returned",
            detail=(
                f"{len(artifact.findings)} finding(s), "
                f"confidence {artifact.confidence.band.value}, "
                f"{len(artifact.unresolved_questions)} unresolved"
            ),
            outputs=tuple(finding.id for finding in artifact.findings),
            notes=(
                f"cites {len(cited)} IR object(s)",
                f"confidence limited by: {artifact.confidence.limiting_factor}",
            ),
        )

        validate_artifact(artifact, ir)
        artifacts.append(artifact)
        trace.record(
            stage="4. kernel execution",
            component="runtime",
            action="artifact-validated",
            detail=f"{kernel.name} artifact accepted",
            inputs=tuple(cited),
            notes=(
                "every cited id exists in the IR",
                "kernel produced findings or unresolved questions",
                "confidence carries a limiting factor (so it was derived)",
            ),
        )

    trace.record(
        stage="4. kernel execution",
        component="runtime",
        action="dispatch-complete",
        detail=f"{len(artifacts)} artifacts collected",
        outputs=tuple(artifact.kernel_name for artifact in artifacts),
    )
    return RunResult(ir=ir, artifacts=tuple(artifacts), trace=trace.entries())
