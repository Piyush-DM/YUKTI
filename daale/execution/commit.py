"""The candidate-to-commit protocol: propose freely, commit only through here.

Phase 2 of the v0 plan. The lifecycle it specifies:

    PROPOSED  ->  VALIDATED  ->  COMMITTED
                            \\->  REJECTED / REVIEW_REQUIRED

and the invariant the whole architecture rests on: **anything may propose; only
the D-Core commits.** That is what keeps a parallel worker, a language model or
a human reviewer from becoming the hidden authority for institutional
reasoning. None of them writes canonical state; they submit candidates, and the
gate below decides.

The seven checks
----------------

Transcribed from the plan §7, in its order. Each is a named check with its own
result, because "the candidate was rejected" is not a useful audit record and
"the candidate was rejected by ``inputs-not-superseded``" is.

One of the seven cannot run yet, and says so rather than passing. Check 4,
plan conformance, needs the execution planner from Phase 3, which does not
exist. Reporting it as ``INACTIVE`` keeps it visible in every gate record; a
check quietly returning ``True`` because it has nothing to check is how a gate
comes to look stronger than it is.

Escalation
----------

A candidate that passes every active check is not automatically canonical. Its
origin decides: a deterministic origin commits, anything else escalates to
``REVIEW_REQUIRED``.

The rule is an **allow-list, and that is the substance of it.** Under a
deny-list, an origin nobody thought to name -- a new adapter, a new tool, a
coprocessor added in Phase 6 -- would commit to canonical state silently, and
the gate would report a pass. Under an allow-list the same unnamed origin
escalates and somebody has to decide about it.

Codified in ``docs/architecture/DECISION-007_candidate_escalation_rule.md``,
which supersedes the assumption this was first recorded as. Changing
``DETERMINISTIC_ORIGINS`` grants canonical write authority to a new class of
producer and requires an approved decision.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from daale.execution.contract import ContractResult
from daale.execution.state import (
    ExecutionLease,
    ReasoningStateStore,
    StaleWrite,
)


class CandidateState(Enum):
    """Where a candidate sits in the lifecycle."""

    PROPOSED = "proposed"
    VALIDATED = "validated"
    COMMITTED = "committed"
    REJECTED = "rejected"
    REVIEW_REQUIRED = "review-required"


class CheckStatus(Enum):
    """The outcome of one gate check.

    ``INACTIVE`` exists so that a check which cannot run is distinguishable
    from one that ran and passed.
    """

    PASSED = "passed"
    FAILED = "failed"
    INACTIVE = "inactive"


# Origins whose output is reproducible and may commit directly. Anything not
# listed escalates for review. Allow-list by decision, not by convenience:
# DECISION-007. Adding to it grants canonical write authority and needs approval.
DETERMINISTIC_ORIGINS: frozenset[str] = frozenset({"dcore", "rfabric", "algorithm"})

REFERENCES_CURRENT_EXECUTION = "references-current-execution"
INPUTS_NOT_SUPERSEDED = "inputs-exist-and-are-not-superseded"
STRUCTURE_VALID = "structure-valid-under-choir"
RESPECTS_PLAN = "respects-active-execution-plan"
PROVENANCE_PRESENT = "required-provenance-present"
NO_STALE_WRITE = "no-stale-write-or-race"
TERMINAL_STATE = "terminal-state-assigned"


@dataclass(frozen=True)
class Candidate:
    """A proposed change to canonical state. Not yet anything.

    ``read_versions`` is what the proposer saw when it computed ``payload``.
    Carrying it is what makes a race detectable at the gate rather than
    discoverable afterwards in an inconsistent record.
    """

    candidate_id: str
    execution_id: str
    object_id: str
    payload: Mapping[str, Any]
    provenance: tuple[str, ...]
    read_versions: Mapping[str, int]
    origin: str


@dataclass(frozen=True)
class GateCheck:
    """One named check, its status, and why."""

    name: str
    status: CheckStatus
    detail: str

    @property
    def blocking(self) -> bool:
        """Only a failure blocks. An inactive check is visible, not fatal."""
        return self.status is CheckStatus.FAILED


@dataclass(frozen=True)
class GateOutcome:
    """What the gate decided about one candidate, and on what basis."""

    candidate: Candidate
    state: CandidateState
    checks: tuple[GateCheck, ...]

    @property
    def failures(self) -> tuple[GateCheck, ...]:
        """Every check that blocked this candidate."""
        return tuple(check for check in self.checks if check.blocking)

    @property
    def inactive(self) -> tuple[GateCheck, ...]:
        """Every check that could not run."""
        return tuple(
            check for check in self.checks if check.status is CheckStatus.INACTIVE
        )


def _check_execution(candidate: Candidate, execution_id: str) -> GateCheck:
    """Check 1: the candidate belongs to the execution now in force."""
    if candidate.execution_id == execution_id:
        return GateCheck(REFERENCES_CURRENT_EXECUTION, CheckStatus.PASSED, execution_id)
    return GateCheck(
        REFERENCES_CURRENT_EXECUTION,
        CheckStatus.FAILED,
        f"candidate references {candidate.execution_id}, open execution is "
        f"{execution_id}",
    )


def _check_inputs(candidate: Candidate, store: ReasoningStateStore) -> GateCheck:
    """Check 2: every input it claims to have read still exists."""
    missing = [
        object_id
        for object_id in candidate.read_versions
        if store.current_version(object_id) is None
    ]
    if missing:
        return GateCheck(
            INPUTS_NOT_SUPERSEDED,
            CheckStatus.FAILED,
            f"inputs no longer present: {', '.join(sorted(missing))}",
        )
    return GateCheck(
        INPUTS_NOT_SUPERSEDED,
        CheckStatus.PASSED,
        f"{len(candidate.read_versions)} input(s) present",
    )


def _check_structure(contract: ContractResult | None) -> GateCheck:
    """Check 3: the candidate's package is valid under CHOIR."""
    if contract is None:
        return GateCheck(
            STRUCTURE_VALID, CheckStatus.PASSED, "no package submitted with candidate"
        )
    if contract.valid:
        return GateCheck(STRUCTURE_VALID, CheckStatus.PASSED, "contract satisfied")
    codes = ", ".join(sorted({v.code for v in contract.violations}))
    return GateCheck(STRUCTURE_VALID, CheckStatus.FAILED, f"violations: {codes}")


def _check_plan() -> GateCheck:
    """Check 4: the candidate respects the active execution plan.

    Inactive. The planner is Phase 3 and does not exist, so there is no plan to
    respect. Declared rather than dropped so that every gate record shows this
    check was not run.
    """
    return GateCheck(
        RESPECTS_PLAN,
        CheckStatus.INACTIVE,
        "no execution planner in v0 Phase 2; requires Phase 3",
    )


def _check_provenance(candidate: Candidate) -> GateCheck:
    """Check 5: the candidate says what it was derived from.

    The plan's acceptance criteria require every committed result to trace back
    to input objects. A candidate with no provenance cannot, so it never
    becomes canonical.
    """
    if candidate.provenance:
        return GateCheck(
            PROVENANCE_PRESENT,
            CheckStatus.PASSED,
            f"derived from {', '.join(candidate.provenance)}",
        )
    return GateCheck(
        PROVENANCE_PRESENT,
        CheckStatus.FAILED,
        "no provenance declared; a committed object must name its inputs",
    )


def _check_freshness(candidate: Candidate, store: ReasoningStateStore) -> GateCheck:
    """Check 6: no input has moved since the candidate read it."""
    stale = [
        f"{object_id}@{seen}!={store.current_version(object_id)}"
        for object_id, seen in candidate.read_versions.items()
        if store.current_version(object_id) != seen
    ]
    if stale:
        return GateCheck(
            NO_STALE_WRITE, CheckStatus.FAILED, f"stale: {', '.join(sorted(stale))}"
        )
    return GateCheck(NO_STALE_WRITE, CheckStatus.PASSED, "inputs unchanged since read")


def run_gate(
    candidate: Candidate,
    store: ReasoningStateStore,
    execution_id: str,
    contract: ContractResult | None = None,
) -> tuple[CandidateState, tuple[GateCheck, ...]]:
    """Run the seven checks and decide the candidate's state.

    Returns the decision without applying it. Applying it is a canonical write
    and therefore belongs to the D-Core, which holds the lease.
    """
    checks = (
        _check_execution(candidate, execution_id),
        _check_inputs(candidate, store),
        _check_structure(contract),
        _check_plan(),
        _check_provenance(candidate),
        _check_freshness(candidate, store),
    )

    if any(check.blocking for check in checks):
        decided = CandidateState.REJECTED
    elif candidate.origin in DETERMINISTIC_ORIGINS:
        decided = CandidateState.VALIDATED
    else:
        decided = CandidateState.REVIEW_REQUIRED

    terminal = GateCheck(
        TERMINAL_STATE,
        CheckStatus.PASSED,
        f"decided: {decided.value}",
    )
    return decided, checks + (terminal,)


def apply_outcome(
    candidate: Candidate,
    decided: CandidateState,
    checks: tuple[GateCheck, ...],
    store: ReasoningStateStore,
    lease: ExecutionLease,
) -> GateOutcome:
    """Commit a validated candidate, or record the decision unapplied.

    Only a ``VALIDATED`` candidate reaches canonical state. A rejection or an
    escalation leaves the store untouched, which is what makes a proposal
    genuinely non-authoritative.
    """
    if decided is not CandidateState.VALIDATED:
        return GateOutcome(candidate, decided, checks)

    try:
        store.commit(
            lease,
            candidate.object_id,
            candidate.payload,
            candidate.provenance,
            candidate.read_versions,
        )
    except StaleWrite as exc:
        # The store is the last word on freshness. If it disagrees with check
        # 6, the store wins: it holds the state, and losing that race here
        # would be the silent overwrite the whole protocol exists to prevent.
        raced = GateCheck(NO_STALE_WRITE, CheckStatus.FAILED, str(exc))
        return GateOutcome(candidate, CandidateState.REJECTED, checks + (raced,))

    return GateOutcome(candidate, CandidateState.COMMITTED, checks)
