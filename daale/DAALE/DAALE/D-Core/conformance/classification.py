"""Why each unexercised commitment is unexercised. Classification, not repair.

Phase 0 established that eight of the twenty-eight frozen §3 commitments have no
evidence behind them. That is a finding, not a work list. This module says *what
kind of gap each one is*, and stops there.

The distinction is load-bearing. "Unexercised" reads like a to-do, and acting on
it that way would be the failure the research freeze §1 exists to prevent:
implementing an open research programme to make a conformance report look
tidier. §9 states the rule directly -- "Every §4 item is a research programme,
not a task. Do not partially implement one to make a current problem easier."
Four of these eight are §4 items.

Every classification cites the document that justifies it. None is inferred from
the code, because the reason a commitment is unimplemented is recorded in the
research corpus, not discoverable from an absence.

What this module must never do
------------------------------

* Implement a commitment. Classification is the deliverable.
* Close ``E12`` by finding something plausible and citing it. ``E12`` is an
  evidence discrepancy -- the freeze marks it demonstrated and this repository
  cites nothing -- and it stays surfaced until an architect adjudicates it.
* Reach into CHOIR v1 for a definition that would close a v0 gap. v0 closes
  against v0; reconciliation is a later, separate act.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Category(Enum):
    """The kinds of gap a frozen commitment can have.

    Each value names a distinct *reason* a commitment lacks evidence, and each
    implies a different next act -- research, a ruling, or adjudication. They
    are deliberately not a severity scale.
    """

    RESEARCH_OPEN = "research-open"
    PROTOTYPE_LIMIT = "prototype-limit"
    SPECIFIED_NOT_IMPLEMENTED = "specified-not-implemented"
    DECISION_REQUIRED = "decision-required"
    EVIDENCE_DISCREPANCY = "evidence-discrepancy"


# What each category means, and what would move a commitment out of it.
CATEGORY_MEANINGS = {
    Category.RESEARCH_OPEN: (
        "Blocked by a named open research question. Moves only on research "
        "evidence or falsification, never on implementation convenience."
    ),
    Category.PROTOTYPE_LIMIT: (
        "The V0.1 prototype's own recorded limit, carried forward deliberately. "
        "Moves when the limit is lifted in a versioned change."
    ),
    Category.SPECIFIED_NOT_IMPLEMENTED: (
        "Specified in the research corpus and not built. Moves when an approved "
        "specification authorises building it."
    ),
    Category.DECISION_REQUIRED: (
        "Blocked on an architectural choice nobody has made. Moves when the "
        "decision note is approved."
    ),
    Category.EVIDENCE_DISCREPANCY: (
        "The freeze records this as demonstrated while the repository cites "
        "nothing. Moves only on adjudication -- either the evidence is named, "
        "or the recorded status is corrected."
    ),
}


@dataclass(frozen=True)
class Classification:
    """One unexercised commitment, its category, and the source that says so."""

    commitment_id: str
    category: Category
    source: str
    rationale: str


# ---------------------------------------------------------------------------
# The eight, classified. Order follows the register.
# ---------------------------------------------------------------------------

CLASSIFICATIONS: tuple[Classification, ...] = (
    Classification(
        "E3",
        Category.SPECIFIED_NOT_IMPLEMENTED,
        "CHOIR_v0.1_RESEARCH_FREEZE.md section 3.1 (status S)",
        "Three confidence axes are specified in research and not built. The "
        "prototype derives one confidence value per artifact, so there is no "
        "place for the axes to be kept separate or to be collapsed.",
    ),
    Classification(
        "E4",
        Category.RESEARCH_OPEN,
        "CHOIR_v0.1_RESEARCH_FREEZE.md section 4.1 (falsifier F3)",
        "Typed defeat is the programme's principal empirical hypothesis and "
        "the single highest-value open question. The freeze records it as "
        "frozen 'as a specification commitment, not as a demonstrated "
        "property', and resolving it may force a core change.",
    ),
    Classification(
        "E5",
        Category.RESEARCH_OPEN,
        "CHOIR_v0.1_RESEARCH_FREEZE.md section 4.2 (gap G5)",
        "The influence-versus-causation falsifier is untested. Until it runs, "
        "there is nothing to demonstrate that influence stays second-order.",
    ),
    Classification(
        "E6",
        Category.PROTOTYPE_LIMIT,
        "CHOIR_v0.1_RESEARCH_FREEZE.md section 4.3",
        "Recorded as a carried prototype limit: 'No ambiguity representation. "
        "The IR cannot hold an unresolved reading.' The commitment cannot be "
        "exercised while the IR has nowhere to put an unresolved reading.",
    ),
    Classification(
        "E7",
        Category.RESEARCH_OPEN,
        "CHOIR_v0.1_RESEARCH_FREEZE.md section 4.2 (gap G8)",
        "Saturation cost at corpus scale is unmeasured and the freeze records "
        "that it could be prohibitive. Status A -- assumed, not demonstrated -- "
        "and the measurement is the research programme.",
    ),
    Classification(
        "E10",
        Category.DECISION_REQUIRED,
        "docs/architecture/DECISION-001_reasoning_execution_substrate.md",
        "No retrieval layer exists. DECISION-001 leaves Option C -- model-backed "
        "extraction upstream of the IR, where a proposing model concludes "
        "nothing -- explicitly available but unmade: 'that is a different "
        "decision'. Nothing can demonstrate this commitment until it is taken.",
    ),
    Classification(
        "E11",
        Category.SPECIFIED_NOT_IMPLEMENTED,
        "CHOIR_v0.1_RESEARCH_FREEZE.md section 3.1 (status S)",
        "Computed evidence independence is specified and not built. The "
        "prototype treats evidence items as independent without computing "
        "whether they are, so correlated evidence is not discounted.",
    ),
    Classification(
        "E12",
        Category.EVIDENCE_DISCREPANCY,
        "CHOIR_v0.1_RESEARCH_FREEZE.md section 3.1 (status D) versus this repository",
        "The freeze marks this demonstrated. The conformance lock finds nothing "
        "in the repository cited for it. Exactly one of two things is true: the "
        "evidence exists and was never recorded, or the recorded status is "
        "optimistic. Both are adjudications about the freeze, and neither is "
        "the lock's to make. Preserved and flagged until ruled on.",
    ),
)


def classification_for(commitment_id: str) -> Classification | None:
    """Return the classification for a commitment, or None if it has evidence."""
    for entry in CLASSIFICATIONS:
        if entry.commitment_id == commitment_id:
            return entry
    return None


def by_category() -> dict[Category, tuple[str, ...]]:
    """Group the classified commitments by category, in register order."""
    grouped: dict[Category, list[str]] = {category: [] for category in Category}
    for entry in CLASSIFICATIONS:
        grouped[entry.category].append(entry.commitment_id)
    return {category: tuple(ids) for category, ids in grouped.items()}
