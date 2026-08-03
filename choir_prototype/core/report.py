"""The execution report.

Renders the run as plain text. The report is a *projection* of what the runtime
recorded -- it does not recompute, re-weigh, or re-describe anything. Every line
below is read from the IR, an artifact, the synthesis, or the trace.

That constraint is what makes the report trustworthy: it cannot disagree with
the reasoning, because it has no independent view of it.
"""

from __future__ import annotations

from choir_prototype.core.contracts import Artifact
from choir_prototype.core.ir import ChoirIR
from choir_prototype.core.runtime import RunResult
from choir_prototype.core.synthesizer import Synthesis, TopicView

WIDTH = 78


def render(result: RunResult, synthesis: Synthesis) -> str:
    """Render the full execution report."""
    lines: list[str] = []
    lines.extend(_header(result.ir))
    lines.extend(_translation(result.ir))
    lines.extend(_recommendation(synthesis))
    lines.extend(_confidence(synthesis))
    lines.extend(_kernel_findings(result.artifacts))
    lines.extend(_agreements(synthesis))
    lines.extend(_disagreements(synthesis))
    lines.extend(_remaining_uncertainty(synthesis))
    lines.extend(_supporting_evidence(result.ir, result.artifacts))
    lines.extend(_execution_trace(result))
    return "\n".join(lines)


def _rule(character: str = "-") -> str:
    return character * WIDTH


def _section(title: str) -> list[str]:
    return ["", _rule("="), title.upper(), _rule("=")]


def _header(ir: ChoirIR) -> list[str]:
    return [
        _rule("="),
        "CHOIR PROTOTYPE V0 -- INSTITUTIONAL REASONING REPORT",
        _rule("="),
        f"Packet      : {ir.metadata.packet_id}",
        f"Title       : {ir.metadata.packet_title}",
        f"Domain      : {ir.metadata.domain}",
        f"Translator  : {ir.metadata.translator}",
        f"IR version  : {ir.metadata.ir_version}",
    ]


def _translation(ir: ChoirIR) -> list[str]:
    lines = _section("1. Translation into the intermediate representation")
    lines.append(
        f"{len(ir.entities)} entities, {len(ir.claims)} claims, "
        f"{len(ir.evidence)} evidence items, {len(ir.assumptions)} assumptions, "
        f"{len(ir.relationships)} relationships."
    )
    lines.append("")
    lines.append("Entities:")
    for entity in ir.entities:
        lines.append(f"  {entity.id:<14} {entity.kind:<10} {entity.label}")

    lines.append("")
    lines.append("Claims:")
    for claim in ir.claims:
        backing = ", ".join(claim.evidence_ids) or "(no evidence)"
        lines.append(
            f"  {claim.id:<10} {claim.predicate:<28} = {claim.value:<12} "
            f"[{claim.uncertainty.value}]"
        )
        lines.append(f"             backed by: {backing}")

    contradicted = ir.contradicted_claim_ids()
    if contradicted:
        lines.append("")
        lines.append("Contradicted claims flagged during translation:")
        for relationship in ir.relationships:
            if relationship.target_id in contradicted and relationship.note:
                lines.append(f"  {relationship.target_id}: {relationship.note}")

    if ir.assumptions:
        lines.append("")
        lines.append("Assumptions carried from the packet:")
        for assumption in ir.assumptions:
            lines.append(f"  {assumption.id}: {assumption.statement}")

    return lines


def _recommendation(synthesis: Synthesis) -> list[str]:
    lines = _section("2. Recommendation")
    lines.append(synthesis.recommendation.value.upper())
    lines.append("")
    lines.append("Rationale:")
    for step, reason in enumerate(synthesis.rationale, start=1):
        lines.append(f"  {step}. {reason}")
    return lines


def _confidence(synthesis: Synthesis) -> list[str]:
    lines = _section("3. Confidence")
    lines.append(f"Band            : {synthesis.confidence.value}")
    lines.append(f"Limited by      : {synthesis.confidence_limiting_factor}")
    lines.append(f"Contributing    : {', '.join(synthesis.usable_kernels) or '(none)'}")
    lines.append(
        f"Weighted tally  : support {synthesis.support_weight}, "
        f"opposition {synthesis.oppose_weight}, "
        f"conditional {synthesis.conditional_count}"
    )
    lines.append("")
    lines.append(
        "Confidence is derived from evidence quality, input coverage and "
        "contradiction count. No kernel may assign it."
    )
    return lines


def _kernel_findings(artifacts: tuple[Artifact, ...]) -> list[str]:
    lines = _section("4. Kernel findings")
    lines.append("Kernels ran independently and could not observe one another.")

    for artifact in artifacts:
        lines.append("")
        lines.append(_rule())
        lines.append(f"KERNEL: {artifact.kernel_name}")
        lines.append(f"  confidence : {artifact.confidence.band.value}")
        lines.append(f"  limited by : {artifact.confidence.limiting_factor}")
        lines.append(f"  coverage   : {artifact.confidence.coverage}")
        lines.append(f"  weakest ev.: {artifact.confidence.evidence_floor}")

        if artifact.findings:
            lines.append("  findings:")
            for finding in artifact.findings:
                lines.append(
                    f"    [{finding.stance.value:<11}] "
                    f"({finding.topic}) {finding.statement}"
                )
                citations = ", ".join((*finding.claim_ids, *finding.evidence_ids))
                lines.append(f"                  cites: {citations or '(none)'}")
        else:
            lines.append("  findings: (none)")

        if artifact.assumptions:
            lines.append("  assumptions:")
            for assumption in artifact.assumptions:
                lines.append(f"    - {assumption}")

        if artifact.unresolved_questions:
            lines.append("  unresolved:")
            for question in artifact.unresolved_questions:
                lines.append(f"    - {question}")

    return lines


def _topic_block(views: tuple[TopicView, ...], empty_message: str) -> list[str]:
    if not views:
        return [empty_message]
    lines: list[str] = []
    for view in views:
        lines.append("")
        lines.append(f"Topic: {view.topic}")
        for position in view.positions:
            lines.append(
                f"  {position.kernel_name:<20} {position.stance.value:<11} "
                f"{position.statement}"
            )
    return lines


def _agreements(synthesis: Synthesis) -> list[str]:
    lines = _section("5. Agreements")
    lines.append(
        "Topics where two or more independent kernels reached the same stance."
    )
    lines.extend(
        _topic_block(synthesis.agreements, "(no topic drew agreement from two kernels)")
    )
    return lines


def _disagreements(synthesis: Synthesis) -> list[str]:
    lines = _section("6. Disagreements")
    lines.append("Topics where kernels reached directly opposing stances.")
    lines.extend(_topic_block(synthesis.disagreements, "(no direct disagreements)"))
    return lines


def _remaining_uncertainty(synthesis: Synthesis) -> list[str]:
    lines = _section("7. Remaining uncertainty")
    if not synthesis.remaining_uncertainty:
        lines.append("(none recorded)")
        return lines
    for item in synthesis.remaining_uncertainty:
        lines.append(f"  - {item}")
    return lines


def _supporting_evidence(ir: ChoirIR, artifacts: tuple[Artifact, ...]) -> list[str]:
    lines = _section("8. Supporting evidence")

    referenced: set[str] = set()
    for artifact in artifacts:
        referenced.update(artifact.evidence_references)
        for finding in artifact.findings:
            referenced.update(finding.evidence_ids)

    for item in ir.evidence:
        used = "used" if item.id in referenced else "not cited"
        lines.append(f"  {item.id:<18} [{item.quality.value:<9}] {item.source}")
        lines.append(f"  {'':<18} status: {used}")

    return lines


def _execution_trace(result: RunResult) -> list[str]:
    lines = _section("9. Execution trace")
    lines.append(
        "Summary view. For inputs, outputs and per-step notes, run with "
        "--inspect trace."
    )
    lines.append("")

    current_stage = ""
    for entry in result.trace:
        if entry.stage != current_stage:
            current_stage = entry.stage
            lines.append(f"  -- stage {current_stage} --")
        lines.append(
            f"  {entry.step:>3}. {entry.component:<18} {entry.action:<20} "
            f"{entry.detail}"
        )
    return lines
