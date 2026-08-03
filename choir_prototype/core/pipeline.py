"""The end-to-end pipeline.

    Investment Packet
            |
            v
    Domain Translation
            |
            v
    CHOIR Intermediate Representation
            |
            v
    Independent Reasoning Kernels
            |
            v
    Structured Artifacts
            |
            v
    Institutional Synthesizer
            |
            v
    Institutional Recommendation

One function, read top to bottom. Every stage boundary is a real boundary: the
kernels receive only the IR, and the synthesizer receives only the artifacts.
"""

from __future__ import annotations

from typing import Any

from choir_prototype.core.domain import Domain
from choir_prototype.core.runtime import RunResult, Trace, run_kernels
from choir_prototype.core.synthesizer import Synthesis, synthesize


def execute(packet: Any, domain: Domain) -> tuple[RunResult, Synthesis]:
    """Run the full pipeline over one packet, using one domain's binding.

    Deterministic: no clock, no randomness, no I/O, no concurrency. The same
    packet produces the same report on every run.

    The only domain-supplied things are ``domain.translate``,
    ``domain.describe`` and ``domain.kernels``. Everything after translation is
    shared code that has no idea which domain it is serving.
    """
    trace = Trace()
    summary = domain.describe(packet)

    trace.record(
        stage="1. packet intake",
        component="pipeline",
        action="packet-loaded",
        detail=f"packet {summary.packet_id}: {summary.title}",
        outputs=(f"packet:{summary.packet_id}",),
        notes=summary.notes,
    )

    trace.record(
        stage="2. translation",
        component="translator",
        action="translate-start",
        detail=f"mapping {summary.record_count} data points to IR",
        inputs=(f"packet:{summary.packet_id}",),
        notes=("translator performs no reasoning; it maps shapes only",),
    )
    ir = domain.translate(packet)
    trace.record(
        stage="2. translation",
        component="translator",
        action="translate-complete",
        detail=(
            f"{len(ir.entities)} entities, {len(ir.claims)} claims, "
            f"{len(ir.evidence)} evidence, {len(ir.relationships)} relationships"
        ),
        outputs=(f"ir:{ir.metadata.packet_id}",),
        notes=(
            f"{len(ir.contradicted_claim_ids())} claim(s) marked contradicted",
            f"{len(ir.assumptions)} assumption(s) carried through",
        ),
    )

    trace.record(
        stage="3. handoff",
        component="pipeline",
        action="ir-sealed",
        detail="kernels receive the IR and nothing else",
        inputs=(f"ir:{ir.metadata.packet_id}",),
        notes=(
            "kernels cannot see the packet",
            "kernels cannot see each other's artifacts",
            "kernels cannot see the synthesizer",
        ),
    )

    result = run_kernels(ir, domain.kernels, trace)

    trace.record(
        stage="5. synthesis",
        component="synthesizer",
        action="synthesis-start",
        detail=f"{len(result.artifacts)} artifacts received",
        inputs=tuple(artifact.kernel_name for artifact in result.artifacts),
        notes=("synthesizer sees artifacts only, never the IR or the packet",),
    )
    synthesis = synthesize(result.artifacts)
    trace.record(
        stage="5. synthesis",
        component="synthesizer",
        action="synthesis-complete",
        detail=(
            f"{synthesis.recommendation.value} at "
            f"{synthesis.confidence.value} confidence"
        ),
        outputs=(synthesis.recommendation.name,),
        notes=(
            f"{len(synthesis.agreements)} agreement(s), "
            f"{len(synthesis.disagreements)} disagreement(s)",
            f"decided by rule {_deciding_rule(synthesis)}",
            f"confidence limited by: {synthesis.confidence_limiting_factor}",
        ),
    )

    # The trace kept growing after run_kernels captured it, so re-snapshot.
    final = RunResult(ir=result.ir, artifacts=result.artifacts, trace=trace.entries())
    return final, synthesis


def _deciding_rule(synthesis: Synthesis) -> str:
    """Name the decision rule that fired, for the trace."""
    for rule in synthesis.rules_evaluated:
        if rule.fired:
            return rule.name
    return "(none)"
