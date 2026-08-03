"""Inspection views.

Four ways to look inside a run, for someone who has never seen CHOIR before:

    ir          what the packet became
    artifacts   what each kernel saw, concluded, and could not conclude
    synthesis   how the recommendation was actually computed
    trace       every step, with what crossed each boundary

Like ``report.py``, every view here is a **projection**. Nothing is recomputed.
The confidence derivations, tally lines and rule evaluations printed below were
recorded by the components that performed them; these functions only format
what is already in the record. If an inspection view could compute a different
answer than the pipeline did, it would be worse than useless.
"""

from __future__ import annotations

from choir_prototype.core.ir import ChoirIR
from choir_prototype.core.runtime import RunResult
from choir_prototype.core.synthesizer import Synthesis

WIDTH = 78


def _rule(character: str = "-") -> str:
    return character * WIDTH


def _title(text: str) -> list[str]:
    return [_rule("="), text.upper(), _rule("=")]


# --------------------------------------------------------------------------
# IR inspection
# --------------------------------------------------------------------------


def inspect_ir(ir: ChoirIR) -> str:
    """Show what the packet became, and what the kernels will therefore see."""
    lines = _title("IR inspection")
    lines.append(f"Packet     : {ir.metadata.packet_id}")
    lines.append(f"Translator : {ir.metadata.translator}")
    lines.append(f"IR version : {ir.metadata.ir_version}")
    lines.append("")
    lines.append(
        f"{len(ir.entities)} entities | {len(ir.claims)} claims | "
        f"{len(ir.evidence)} evidence | {len(ir.assumptions)} assumptions | "
        f"{len(ir.relationships)} relationships"
    )

    lines.append("")
    lines.append(_rule())
    lines.append("ENTITIES")
    for entity in ir.entities:
        attributes = ", ".join(
            f"{key}={value}" for key, value in sorted(entity.attributes.items())
        )
        lines.append(f"  {entity.id:<14} {entity.kind:<9} {entity.label}")
        if attributes:
            lines.append(f"  {'':<14} {attributes}")

    lines.append("")
    lines.append(_rule())
    lines.append("CLAIMS  (subject <- predicate = value)")
    contradicted = ir.contradicted_claim_ids()
    for claim in ir.claims:
        flag = "  <-- CONTRADICTED" if claim.id in contradicted else ""
        lines.append(
            f"  {claim.id:<9} {claim.subject_id:<13} {claim.predicate:<27} "
            f"= {claim.value}{flag}"
        )
        backing = ", ".join(claim.evidence_ids) or "NONE"
        lines.append(
            f"  {'':<9} uncertainty={claim.uncertainty.value:<10} evidence: {backing}"
        )

    lines.append("")
    lines.append(_rule())
    lines.append("EVIDENCE  (and the claims each one backs)")
    for item in ir.evidence:
        backs = [claim.id for claim in ir.claims if item.id in claim.evidence_ids]
        lines.append(f"  {item.id:<17} [{item.quality.value:<9}] {item.source}")
        lines.append(
            f"  {'':<17} backs {len(backs)} claim(s): {', '.join(backs) or '(none)'}"
        )

    lines.append("")
    lines.append(_rule())
    lines.append("RELATIONSHIPS  (grouped by kind)")
    by_kind: dict[str, list[str]] = {}
    for relationship in ir.relationships:
        note = f"  -- {relationship.note}" if relationship.note else ""
        by_kind.setdefault(relationship.kind.value, []).append(
            f"    {relationship.source_id} -> {relationship.target_id}{note}"
        )
    for kind, rows in sorted(by_kind.items()):
        lines.append(f"  {kind} ({len(rows)}):")
        lines.extend(rows)

    if ir.assumptions:
        lines.append("")
        lines.append(_rule())
        lines.append("ASSUMPTIONS")
        for assumption in ir.assumptions:
            lines.append(f"  {assumption.id}: {assumption.statement}")
            lines.append(f"  {'':<8} basis: {assumption.basis}")

    lines.append("")
    lines.append(_rule())
    lines.append("INTEGRITY CHECKS")
    lines.extend(_ir_integrity(ir))
    return "\n".join(lines)


def _ir_integrity(ir: ChoirIR) -> list[str]:
    """Report structural facts a reader would otherwise have to hunt for."""
    known = ir.known_ids()

    unbacked = [claim.id for claim in ir.claims if not claim.evidence_ids]
    dangling = sorted(
        {
            evidence_id
            for claim in ir.claims
            for evidence_id in claim.evidence_ids
            if evidence_id not in known
        }
    )
    uncited = [
        item.id
        for item in ir.evidence
        if not any(item.id in claim.evidence_ids for claim in ir.claims)
    ]

    def _check(label: str, ids: list[str]) -> str:
        detail = f" ({', '.join(ids)})" if ids else ""
        return f"  {label:<29}: {len(ids)}{detail}"

    return [
        _check("claims with no evidence", unbacked),
        _check("claims citing missing sources", dangling),
        _check("evidence backing no claim", uncited),
        f"  {'contradicted claims':<29}: {len(ir.contradicted_claim_ids())}",
    ]


# --------------------------------------------------------------------------
# Artifact inspection
# --------------------------------------------------------------------------


def _coverage_from_trace(
    result: RunResult, kernel_name: str
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Recover which inputs a kernel sought and which were missing.

    Read from the trace the runtime already wrote, not by re-importing the
    kernel and recomputing. Inspection is a projection of the record; asking the
    kernels again would make this view capable of disagreeing with the run it
    claims to describe -- and would couple the core to a domain's kernel module.
    """
    for entry in result.trace:
        if entry.component == kernel_name and entry.action == "kernel-start":
            missing: tuple[str, ...] = ()
            for note in entry.notes:
                if note.startswith("missing from packet: "):
                    missing = tuple(
                        name.strip()
                        for name in note.removeprefix("missing from packet: ").split(
                            ","
                        )
                    )
            return entry.inputs, missing
    return (), ()


def inspect_artifacts(result: RunResult) -> str:
    """Show what each kernel looked for, found, concluded and could not conclude."""
    lines = _title("Artifact inspection")
    lines.append(
        "Each kernel below ran in isolation over the same IR. None could observe"
    )
    lines.append("another. Their agreement, where it occurs, is independent.")

    for artifact in result.artifacts:
        lines.append("")
        lines.append(_rule("="))
        lines.append(f"KERNEL: {artifact.kernel_name}")
        lines.append(_rule("="))

        found, missing = _coverage_from_trace(result, artifact.kernel_name)
        lines.append("INPUTS SOUGHT")
        for predicate in found:
            claim = next(
                (c for c in result.ir.claims if c.predicate == predicate), None
            )
            value = claim.value if claim else "?"
            claim_id = claim.id if claim else "?"
            lines.append(f"  found   {predicate:<28} = {value:<12} ({claim_id})")
        for predicate in missing:
            lines.append(f"  MISSING {predicate:<28}   not supplied by packet")

        lines.append("")
        lines.append("CONFIDENCE DERIVATION")
        for step in artifact.confidence.derivation:
            lines.append(f"  {step}")
        lines.append(f"  coverage recorded: {artifact.confidence.coverage}")

        lines.append("")
        lines.append("FINDINGS")
        if not artifact.findings:
            lines.append("  (none -- this kernel could not conclude anything)")
        for finding in artifact.findings:
            lines.append(f"  {finding.id}  [{finding.stance.value}]  {finding.topic}")
            lines.append(f"    {finding.statement}")
            lines.append(f"    from claims: {', '.join(finding.claim_ids) or '(none)'}")
            lines.append(
                f"    via evidence: {', '.join(finding.evidence_ids) or '(none)'}"
            )

        if artifact.assumptions:
            lines.append("")
            lines.append("ASSUMPTIONS MADE")
            for assumption in artifact.assumptions:
                lines.append(f"  - {assumption}")

        lines.append("")
        lines.append("COULD NOT CONCLUDE")
        if not artifact.unresolved_questions:
            lines.append("  (nothing outstanding)")
        for question in artifact.unresolved_questions:
            lines.append(f"  - {question}")

    return "\n".join(lines)


# --------------------------------------------------------------------------
# Synthesis explanation
# --------------------------------------------------------------------------


def inspect_synthesis(synthesis: Synthesis) -> str:
    """Show exactly how the recommendation was computed, step by step."""
    lines = _title("Synthesis explanation")
    lines.append("How the institutional recommendation was reached, in order.")

    lines.append("")
    lines.append(_rule())
    lines.append("STEP 1 -- EVERY FINDING, BY TOPIC")
    lines.append("Topics with two or more kernels are where agreement can appear.")
    for view in synthesis.topic_views:
        marker = ""
        if view in synthesis.disagreements:
            marker = "   <-- DISAGREEMENT"
        elif view in synthesis.agreements:
            marker = "   <-- AGREEMENT"
        count = len(view.positions)
        plural = "kernel" if count == 1 else "kernels"
        lines.append("")
        lines.append(f"  {view.topic} ({count} {plural}){marker}")
        for position in view.positions:
            lines.append(
                f"    {position.kernel_name:<19} {position.stance.value:<11} "
                f"{position.finding_id}"
            )

    lines.append("")
    lines.append(_rule())
    lines.append("STEP 2 -- WEIGHTED TALLY")
    lines.append("Each finding is weighted by its kernel's confidence band:")
    lines.append("  high=3  moderate=2  low=1  insufficient=0")
    lines.append("An insufficient kernel weighs 0, so it cannot move the decision.")
    lines.append("")
    lines.append(
        f"  {'finding':<20} {'kernel':<19} {'stance':<12} "
        f"{'+w':>3}  {'sup':>4} {'opp':>4} {'cond':>5}"
    )
    lines.append(f"  {_rule()[:70]}")
    for line in synthesis.tally_detail:
        lines.append(
            f"  {line.finding_id:<20} {line.kernel_name:<19} "
            f"{line.stance.value:<12} {line.weight:>3}  "
            f"{line.running_support:>4} {line.running_oppose:>4} "
            f"{line.running_conditional:>5}"
        )
    lines.append("")
    lines.append(
        f"  TOTALS: support {synthesis.support_weight}, "
        f"opposition {synthesis.oppose_weight}, "
        f"conditional {synthesis.conditional_count}"
    )

    lines.append("")
    lines.append(_rule())
    lines.append("STEP 3 -- DECISION RULES, IN ORDER")
    lines.append("The first rule that fires decides. Rules below it never run.")
    lines.append("")
    for rule in synthesis.rules_evaluated:
        status = "FIRED" if rule.fired else "  no "
        lines.append(f"  [{status}] {rule.name}")
        lines.append(f"           if: {rule.condition}")
        lines.append(f"           observed: {rule.observed}")
        lines.append(f"           -> {rule.outcome}")
    unreached = 6 - len(synthesis.rules_evaluated)
    if unreached > 0:
        lines.append(f"  ({unreached} later rule(s) never evaluated)")

    lines.append("")
    lines.append(_rule())
    lines.append("STEP 4 -- INSTITUTIONAL CONFIDENCE")
    lines.append(
        f"  contributing kernels: {', '.join(synthesis.usable_kernels) or '(none)'}"
    )
    lines.append(
        "  rule: take the MINIMUM band across contributing kernels, not the mean."
    )
    lines.append(
        "        A conclusion is no more reliable than the weakest kernel under it."
    )
    lines.append(f"  result: {synthesis.confidence.value}")
    lines.append(f"  limited by: {synthesis.confidence_limiting_factor}")

    lines.append("")
    lines.append(_rule())
    lines.append("STEP 5 -- RESULT")
    lines.append(f"  {synthesis.recommendation.value.upper()}")
    for index, reason in enumerate(synthesis.rationale, start=1):
        lines.append(f"    {index}. {reason}")

    if synthesis.remaining_uncertainty:
        lines.append("")
        lines.append("  Carried forward unresolved:")
        for item in synthesis.remaining_uncertainty:
            lines.append(f"    - {item}")

    return "\n".join(lines)


# --------------------------------------------------------------------------
# Trace inspection
# --------------------------------------------------------------------------


def inspect_trace(result: RunResult) -> str:
    """Show every recorded step, grouped by pipeline stage."""
    lines = _title("Execution trace")
    lines.append("Every step the pipeline recorded, in order, with what crossed each")
    lines.append("boundary. Steps are numbered rather than timestamped so that")
    lines.append("two runs of the same packet produce an identical trace.")

    current_stage = ""
    for entry in result.trace:
        if entry.stage != current_stage:
            current_stage = entry.stage
            lines.append("")
            lines.append(_rule())
            lines.append(f"STAGE {current_stage}")
            lines.append(_rule())

        lines.append("")
        lines.append(f"  [{entry.step:>2}] {entry.component} :: {entry.action}")
        lines.append(f"       {entry.detail}")
        if entry.inputs:
            lines.append(f"       in  <- {', '.join(entry.inputs)}")
        if entry.outputs:
            lines.append(f"       out -> {', '.join(entry.outputs)}")
        for note in entry.notes:
            lines.append(f"       .  {note}")

    return "\n".join(lines)


def inspect_all(result: RunResult, synthesis: Synthesis) -> str:
    """Every inspection view, in pipeline order."""
    return "\n\n\n".join(
        (
            inspect_ir(result.ir),
            inspect_artifacts(result),
            inspect_synthesis(synthesis),
            inspect_trace(result),
        )
    )
