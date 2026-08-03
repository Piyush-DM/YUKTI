"""The institutional synthesizer.

Consumes every kernel artifact and produces one institutional recommendation.

There is no model call here and no hidden judgement. The synthesizer counts,
compares, and applies rules that are written out below as named constants. Its
job is to combine independent conclusions honestly, which mostly means being
willing to return an answer nobody wanted:

- If the kernels genuinely disagree and neither side dominates, the output is
  CONTESTED. It does not pick a side to look decisive.
- If too few kernels could see enough to conclude anything, the output is
  INSUFFICIENT_BASIS. It does not extrapolate from the ones that could.
"""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Sequence
from enum import Enum

from choir_prototype.core.contracts import (
    Artifact,
    ConfidenceBand,
    Stance,
    lowest_band,
)
from choir_prototype.core.ir import Topic

# A recommendation needs at least this many kernels that reached a usable
# confidence band. Below it, the packet has not been assessed.
MINIMUM_USABLE_KERNELS = 2

# When kernels disagree, one side must lead by at least this much weight for
# the disagreement to be treated as settled rather than live.
DOMINANCE_MARGIN = 3


class Recommendation(Enum):
    """The institutional outcomes this prototype can reach."""

    PROCEED = "proceed"
    PROCEED_WITH_CONDITIONS = "proceed with conditions"
    DECLINE = "decline"
    CONTESTED = "contested"
    INSUFFICIENT_BASIS = "insufficient basis"


@dataclass(frozen=True)
class Position:
    """One kernel's stance on one topic."""

    kernel_name: str
    stance: Stance
    statement: str
    finding_id: str


@dataclass(frozen=True)
class TopicView:
    """Every kernel position on a single topic."""

    topic: Topic
    positions: tuple[Position, ...]


@dataclass(frozen=True)
class TallyLine:
    """One finding's contribution to the weighted tally, with running totals.

    Recorded as the tally is computed so the explanation can replay the
    arithmetic rather than recompute it.
    """

    kernel_name: str
    finding_id: str
    stance: Stance
    kernel_band: ConfidenceBand
    weight: int
    running_support: int
    running_oppose: int
    running_conditional: int


@dataclass(frozen=True)
class RuleEvaluation:
    """One decision rule, whether it fired, and what it concluded."""

    name: str
    condition: str
    observed: str
    fired: bool
    outcome: str


@dataclass(frozen=True)
class Synthesis:
    """The institutional output."""

    recommendation: Recommendation
    rationale: tuple[str, ...]
    agreements: tuple[TopicView, ...]
    disagreements: tuple[TopicView, ...]
    confidence: ConfidenceBand
    confidence_limiting_factor: str
    remaining_uncertainty: tuple[str, ...]
    support_weight: int
    oppose_weight: int
    conditional_count: int
    usable_kernels: tuple[str, ...]
    tally_detail: tuple[TallyLine, ...]
    rules_evaluated: tuple[RuleEvaluation, ...]
    topic_views: tuple[TopicView, ...]


def synthesize(artifacts: Sequence[Artifact]) -> Synthesis:
    """Combine kernel artifacts into one institutional recommendation."""
    views = _topic_views(artifacts)
    agreements = tuple(view for view in views if _is_agreement(view))
    disagreements = tuple(view for view in views if _is_disagreement(view))

    usable = tuple(
        artifact.kernel_name
        for artifact in artifacts
        if artifact.confidence.band is not ConfidenceBand.INSUFFICIENT
    )

    support_weight, oppose_weight, conditional_count, tally_detail = _tally(artifacts)
    recommendation, rationale, rules_evaluated = _decide(
        usable_count=len(usable),
        total_kernels=len(artifacts),
        support_weight=support_weight,
        oppose_weight=oppose_weight,
        conditional_count=conditional_count,
        disagreement_count=len(disagreements),
    )

    confidence, limiting_factor = _synthesis_confidence(
        artifacts=artifacts,
        usable_count=len(usable),
        disagreement_count=len(disagreements),
    )

    return Synthesis(
        recommendation=recommendation,
        rationale=rationale,
        agreements=agreements,
        disagreements=disagreements,
        confidence=confidence,
        confidence_limiting_factor=limiting_factor,
        remaining_uncertainty=_remaining_uncertainty(artifacts),
        support_weight=support_weight,
        oppose_weight=oppose_weight,
        conditional_count=conditional_count,
        usable_kernels=usable,
        tally_detail=tally_detail,
        rules_evaluated=rules_evaluated,
        topic_views=views,
    )


def _topic_views(artifacts: Sequence[Artifact]) -> tuple[TopicView, ...]:
    """Group every finding by topic, preserving kernel dispatch order."""
    grouped: dict[Topic, list[Position]] = {}
    for artifact in artifacts:
        for finding in artifact.findings:
            grouped.setdefault(finding.topic, []).append(
                Position(
                    kernel_name=artifact.kernel_name,
                    stance=finding.stance,
                    statement=finding.statement,
                    finding_id=finding.id,
                )
            )

    return tuple(
        TopicView(topic=topic, positions=tuple(positions))
        for topic, positions in sorted(grouped.items())
    )


def _is_agreement(view: TopicView) -> bool:
    """True when two or more kernels reached the same non-neutral stance."""
    stances = {
        position.stance
        for position in view.positions
        if position.stance is not Stance.NEUTRAL
    }
    return len(view.positions) >= 2 and len(stances) == 1


def _is_disagreement(view: TopicView) -> bool:
    """True when kernels took directly opposing stances on one topic.

    CONDITIONAL is not treated as opposition. A kernel saying "yes, if" and a
    kernel saying "yes" are not in conflict; only SUPPORTS against OPPOSES is.
    """
    stances = {position.stance for position in view.positions}
    return Stance.SUPPORTS in stances and Stance.OPPOSES in stances


def _tally(
    artifacts: Sequence[Artifact],
) -> tuple[int, int, int, tuple[TallyLine, ...]]:
    """Weight findings by the confidence of the kernel that produced them.

    A finding from a kernel that could barely see anything carries less weight
    than one from a kernel with audited evidence. INSUFFICIENT kernels weigh
    zero, so they cannot move the recommendation at all.

    Every step is recorded in a TallyLine so the explanation view can show the
    running totals instead of asserting the final ones.
    """
    support = 0
    oppose = 0
    conditional = 0
    lines: list[TallyLine] = []

    for artifact in artifacts:
        weight = artifact.confidence.band.weight
        for finding in artifact.findings:
            contribution = 0
            if finding.stance is Stance.SUPPORTS:
                support += weight
                contribution = weight
            elif finding.stance is Stance.OPPOSES:
                oppose += weight
                contribution = weight
            elif finding.stance is Stance.CONDITIONAL:
                conditional += 1
            lines.append(
                TallyLine(
                    kernel_name=artifact.kernel_name,
                    finding_id=finding.id,
                    stance=finding.stance,
                    kernel_band=artifact.confidence.band,
                    weight=contribution,
                    running_support=support,
                    running_oppose=oppose,
                    running_conditional=conditional,
                )
            )

    return support, oppose, conditional, tuple(lines)


def _decide(
    usable_count: int,
    total_kernels: int,
    support_weight: int,
    oppose_weight: int,
    conditional_count: int,
    disagreement_count: int,
) -> tuple[Recommendation, tuple[str, ...], tuple[RuleEvaluation, ...]]:
    """Apply the decision rules in order, recording why each fired or did not.

    The rules and their order are unchanged. What is new is that every rule is
    recorded whether or not it fired, so the explanation can show the rules that
    were considered and rejected -- usually more informative than the one that
    happened to fire.
    """
    rationale: list[str] = []
    rules: list[RuleEvaluation] = []
    margin = abs(support_weight - oppose_weight)

    fired = usable_count < MINIMUM_USABLE_KERNELS
    rules.append(
        RuleEvaluation(
            name="R1 insufficient-basis",
            condition=f"usable kernels < {MINIMUM_USABLE_KERNELS}",
            observed=f"{usable_count} usable of {total_kernels}",
            fired=fired,
            outcome="INSUFFICIENT_BASIS" if fired else "fall through",
        )
    )
    if fired:
        rationale.append(
            f"Only {usable_count} of {total_kernels} kernels reached a usable "
            f"confidence band; {MINIMUM_USABLE_KERNELS} are required."
        )
        rationale.append(
            "The packet has not been assessed. This is a statement about the "
            "evidence supplied, not about the opportunity."
        )
        return Recommendation.INSUFFICIENT_BASIS, tuple(rationale), tuple(rules)

    rationale.append(
        f"{usable_count} of {total_kernels} kernels reached a usable confidence band."
    )
    rationale.append(
        f"Weighted support {support_weight} against opposition {oppose_weight}, "
        f"with {conditional_count} conditional finding(s)."
    )

    fired = bool(disagreement_count) and margin < DOMINANCE_MARGIN
    rules.append(
        RuleEvaluation(
            name="R2 live-disagreement",
            condition=f"disagreements > 0 and margin < {DOMINANCE_MARGIN}",
            observed=f"{disagreement_count} disagreement(s), margin {margin}",
            fired=fired,
            outcome="CONTESTED" if fired else "fall through",
        )
    )
    if fired:
        rationale.append(
            f"{disagreement_count} topic(s) carry directly opposing kernel "
            f"findings and neither side leads by the {DOMINANCE_MARGIN}-point "
            "margin required to treat the disagreement as settled."
        )
        rationale.append(
            "Both positions are reported. The disagreement is live, not resolved."
        )
        return Recommendation.CONTESTED, tuple(rationale), tuple(rules)

    if disagreement_count:
        rationale.append(
            f"{disagreement_count} topic(s) carry opposing findings, but the "
            f"leading side is ahead by {margin}, clearing the "
            f"{DOMINANCE_MARGIN}-point margin."
        )

    fired = support_weight > oppose_weight and bool(conditional_count)
    rules.append(
        RuleEvaluation(
            name="R3 proceed-with-conditions",
            condition="support > opposition and conditional findings > 0",
            observed=(
                f"support {support_weight}, opposition {oppose_weight}, "
                f"conditional {conditional_count}"
            ),
            fired=fired,
            outcome="PROCEED_WITH_CONDITIONS" if fired else "fall through",
        )
    )
    if fired:
        rationale.append(
            "Support leads, but conditional findings remain outstanding; those "
            "become the conditions."
        )
        return Recommendation.PROCEED_WITH_CONDITIONS, tuple(rationale), tuple(rules)

    fired = support_weight > oppose_weight
    rules.append(
        RuleEvaluation(
            name="R4 proceed",
            condition="support > opposition",
            observed=f"support {support_weight}, opposition {oppose_weight}",
            fired=fired,
            outcome="PROCEED" if fired else "fall through",
        )
    )
    if fired:
        rationale.append("Support leads with no conditional findings outstanding.")
        return Recommendation.PROCEED, tuple(rationale), tuple(rules)

    fired = oppose_weight > support_weight
    rules.append(
        RuleEvaluation(
            name="R5 decline",
            condition="opposition > support",
            observed=f"support {support_weight}, opposition {oppose_weight}",
            fired=fired,
            outcome="DECLINE" if fired else "fall through",
        )
    )
    if fired:
        rationale.append("Opposition leads on weighted findings.")
        return Recommendation.DECLINE, tuple(rationale), tuple(rules)

    rules.append(
        RuleEvaluation(
            name="R6 balanced-fallback",
            condition="support == opposition",
            observed=f"support {support_weight}, opposition {oppose_weight}",
            fired=True,
            outcome="CONTESTED",
        )
    )
    rationale.append("Support and opposition are exactly balanced.")
    return Recommendation.CONTESTED, tuple(rationale), tuple(rules)


def _synthesis_confidence(
    artifacts: Sequence[Artifact],
    usable_count: int,
    disagreement_count: int,
) -> tuple[ConfidenceBand, str]:
    """Derive institutional confidence from the kernels that contributed.

    The minimum is taken rather than the average: an institutional conclusion is
    no more reliable than the weakest kernel supporting it.
    """
    if usable_count < MINIMUM_USABLE_KERNELS:
        return ConfidenceBand.INSUFFICIENT, "too few kernels reached a usable band"

    usable = [
        artifact
        for artifact in artifacts
        if artifact.confidence.band is not ConfidenceBand.INSUFFICIENT
    ]
    band = lowest_band([artifact.confidence.band for artifact in usable])
    weakest = min(
        usable, key=lambda item: (item.confidence.band.weight, item.kernel_name)
    )
    limiting_factor = (
        f"weakest contributing kernel is {weakest.kernel_name} "
        f"({weakest.confidence.limiting_factor})"
    )

    if disagreement_count:
        limiting_factor = (
            f"{disagreement_count} unresolved topic disagreement(s); {limiting_factor}"
        )

    return band, limiting_factor


def _remaining_uncertainty(artifacts: Sequence[Artifact]) -> tuple[str, ...]:
    """Collect every unresolved question and assumption, attributed and sorted."""
    items: list[str] = []
    for artifact in artifacts:
        for question in artifact.unresolved_questions:
            items.append(f"[{artifact.kernel_name}] {question}")
        for assumption in artifact.assumptions:
            items.append(f"[{artifact.kernel_name}] Assumed: {assumption}")
    return tuple(sorted(items))
