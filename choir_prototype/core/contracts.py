"""The kernel contract, the artifact it returns, and derived confidence.

Every kernel implements the same interface: it takes a ChoirIR and returns an
Artifact. Kernels never see each other, never see the original packet, and never
see the synthesizer.

The one rule enforced here that is worth stating explicitly: **confidence is
derived, never authored**. There is no constructor path that lets a kernel type
in a confidence value. It must call `derive_confidence` and pass the structural
inputs, which are recorded on the result so the report can show the derivation.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from choir_prototype.core.ir import ChoirIR, Evidence, Topic


class Stance(Enum):
    """What a finding says about the investment decision."""

    SUPPORTS = "supports"
    OPPOSES = "opposes"
    CONDITIONAL = "conditional"
    NEUTRAL = "neutral"


class ConfidenceBand(Enum):
    """Ordinal confidence. Deliberately coarse -- the inputs justify no more."""

    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    INSUFFICIENT = "insufficient"

    @property
    def weight(self) -> int:
        """Weight used by the synthesizer. INSUFFICIENT contributes nothing."""
        return _BAND_WEIGHT[self]


_BAND_WEIGHT = {
    ConfidenceBand.HIGH: 3,
    ConfidenceBand.MODERATE: 2,
    ConfidenceBand.LOW: 1,
    ConfidenceBand.INSUFFICIENT: 0,
}

_ORDERED_BANDS = (
    ConfidenceBand.HIGH,
    ConfidenceBand.MODERATE,
    ConfidenceBand.LOW,
    ConfidenceBand.INSUFFICIENT,
)

# Quality of the weakest evidence item maps to a starting band. Weakest, not
# average: a conclusion is no stronger than the flimsiest thing holding it up.
_QUALITY_RANK_TO_BAND = {
    3: ConfidenceBand.HIGH,
    2: ConfidenceBand.MODERATE,
    1: ConfidenceBand.LOW,
    0: ConfidenceBand.LOW,
}

# A kernel that found fewer than this share of the inputs it looks for cannot
# reach a usable conclusion, however good the evidence it did find.
MINIMUM_COVERAGE = 0.5


@dataclass(frozen=True)
class Confidence:
    """A derived confidence band, with the inputs that produced it.

    ``derivation`` records each rule that fired while computing the band, in
    order. It exists so a reader can follow the arithmetic rather than trust the
    result: the inspection view replays these lines instead of recomputing them.
    """

    band: ConfidenceBand
    limiting_factor: str
    evidence_floor: str
    coverage: str
    contradictions: int
    derivation: tuple[str, ...]

    def summary(self) -> str:
        """One line suitable for a report."""
        return f"{self.band.value} (limited by: {self.limiting_factor})"


def derive_confidence(
    evidence: Sequence[Evidence],
    expected_inputs: int,
    found_inputs: int,
    contradiction_count: int,
) -> Confidence:
    """Compute a confidence band from structural facts about the reasoning.

    The rules, in order:

    1. No supporting evidence at all -> INSUFFICIENT.
    2. Coverage below MINIMUM_COVERAGE -> INSUFFICIENT. A kernel that could not
       find most of what it looks for has not done its job, regardless of how
       good the fragments it did find are.
    3. Otherwise start from the *weakest* evidence item.
    4. Downgrade one band per contradiction, floored at LOW. Contradictions
       reduce confidence but do not by themselves make a finding unusable.

    The limiting factor is always named, so the report can say what would
    improve the answer rather than just how good it currently is.
    """
    coverage_ratio = found_inputs / expected_inputs if expected_inputs else 0.0
    coverage = f"{found_inputs}/{expected_inputs} expected inputs present"
    steps: list[str] = [
        f"rule 0: inputs -- {len(evidence)} evidence item(s), "
        f"coverage {found_inputs}/{expected_inputs} "
        f"({coverage_ratio:.0%}), {contradiction_count} contradiction(s)"
    ]

    if not evidence:
        steps.append("rule 1: no evidence at all -> INSUFFICIENT (stop)")
        return Confidence(
            band=ConfidenceBand.INSUFFICIENT,
            limiting_factor="no supporting evidence in packet",
            evidence_floor="none",
            coverage=coverage,
            contradictions=contradiction_count,
            derivation=tuple(steps),
        )
    steps.append("rule 1: evidence present -> continue")

    if coverage_ratio < MINIMUM_COVERAGE:
        steps.append(
            f"rule 2: coverage {coverage_ratio:.0%} < {MINIMUM_COVERAGE:.0%} "
            "minimum -> INSUFFICIENT (stop)"
        )
        return Confidence(
            band=ConfidenceBand.INSUFFICIENT,
            limiting_factor="incomplete input coverage",
            evidence_floor=_weakest(evidence).quality.value,
            coverage=coverage,
            contradictions=contradiction_count,
            derivation=tuple(steps),
        )
    steps.append(
        f"rule 2: coverage {coverage_ratio:.0%} >= {MINIMUM_COVERAGE:.0%} "
        "minimum -> continue"
    )

    weakest = _weakest(evidence)
    band = _QUALITY_RANK_TO_BAND[weakest.quality.rank]
    limiting_factor = f"weakest evidence is {weakest.quality.value} ({weakest.id})"
    steps.append(
        f"rule 3: weakest evidence is {weakest.id} ({weakest.quality.value}) "
        f"-> start at {band.value}"
    )

    if contradiction_count:
        before = band
        band = _downgrade(band, steps=contradiction_count, floor=ConfidenceBand.LOW)
        limiting_factor = f"{contradiction_count} contradicted claim(s) in scope"
        steps.append(
            f"rule 4: {contradiction_count} contradiction(s) -> downgrade "
            f"{before.value} to {band.value} (floor: low)"
        )
    else:
        steps.append("rule 4: no contradictions -> no downgrade")

    if coverage_ratio < 1.0 and band is ConfidenceBand.HIGH:
        band = ConfidenceBand.MODERATE
        limiting_factor = "partial input coverage"
        steps.append("rule 5: partial coverage caps high -> moderate")
    else:
        steps.append("rule 5: no coverage cap applied")

    steps.append(f"result: {band.value} (limited by: {limiting_factor})")

    return Confidence(
        band=band,
        limiting_factor=limiting_factor,
        evidence_floor=weakest.quality.value,
        coverage=coverage,
        contradictions=contradiction_count,
        derivation=tuple(steps),
    )


def _weakest(evidence: Sequence[Evidence]) -> Evidence:
    """Return the lowest-quality evidence item, breaking ties by id."""
    return sorted(evidence, key=lambda item: (item.quality.rank, item.id))[0]


def _downgrade(
    band: ConfidenceBand, steps: int, floor: ConfidenceBand
) -> ConfidenceBand:
    """Move a band down the ordinal scale, not past the floor."""
    index = _ORDERED_BANDS.index(band)
    floor_index = _ORDERED_BANDS.index(floor)
    return _ORDERED_BANDS[min(index + steps, floor_index)]


def lowest_band(bands: Sequence[ConfidenceBand]) -> ConfidenceBand:
    """Return the weakest band in a sequence.

    The synthesizer takes the minimum rather than the average: an institutional
    conclusion is no more reliable than the weakest kernel it rests on.
    """
    if not bands:
        return ConfidenceBand.INSUFFICIENT
    return max(bands, key=lambda band: _ORDERED_BANDS.index(band))


@dataclass(frozen=True)
class Finding:
    """One structured conclusion from one kernel."""

    id: str
    topic: Topic
    stance: Stance
    statement: str
    claim_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class Artifact:
    """Everything a kernel returns. This is the only kernel output."""

    kernel_name: str
    findings: tuple[Finding, ...]
    evidence_references: tuple[str, ...]
    confidence: Confidence
    assumptions: tuple[str, ...]
    unresolved_questions: tuple[str, ...]


class Kernel(Protocol):
    """The interface every kernel implements.

    A kernel reads the IR and returns an Artifact. It takes no other input and
    performs no I/O, which is what makes the run deterministic and replayable.

    ``PREDICATES`` declares, up front, which claim predicates this kernel reads.
    It is not used to dispatch or filter anything -- the kernel still walks the
    IR itself. It exists so the runtime can report which inputs a kernel was
    looking for and which the packet did not supply, which is the difference
    between "3/5 coverage" and "3/5 coverage, missing cash and burn".
    """

    name: str
    PREDICATES: tuple[str, ...]

    def run(self, ir: ChoirIR) -> Artifact:
        """Analyse the IR and return a structured artifact."""
        ...
