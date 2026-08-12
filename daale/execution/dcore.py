"""The D-Core: canonical authority, and the exact point where v0 stops.

The v0 plan's design rule for this component is "the D-Core owns authority, not
necessarily compute volume". That is the whole shape of what follows. The
D-Core here validates, orders, versions, commits, traces and terminates. It
computes no reasoning at all.

Where this stops, and why it stops there
----------------------------------------

The plan gives the D-Core nine responsibilities. Eight of them are implemented
below. The ninth -- emitting a judgment -- is not, and cannot be, while
``DECISION-005`` is open.

A judgment requires evaluated results, and evaluation requires deciding *who
evaluates*: whether DAALE calls the frozen prototype's kernels, or evaluates
for itself. Those are options **B** and **A** of ``DECISION-005`` verbatim, and
there is no neutral third answer, because "who evaluates" is precisely the
question that ADR asks. Choosing either by implication is the thing the ADR
exists to prevent.

So this module has **no evaluator and no stub for one.** A placeholder that
raised ``NotImplementedError`` would still assert that the evaluator belongs
inside DAALE, which is itself one of the answers. Instead the D-Core takes
candidates from whoever produced them and decides whether they may become
canonical. That is a complete and coherent component: the candidate-to-commit
protocol means the commit authority never needs to evaluate anything. The
unresolved choice only bites when something has to *produce* canonical
reasoning candidates for a real CHOIR package, and that is Phase 3 onward.

What it does emit
-----------------

``INSUFFICIENT_BASIS`` when nothing was committed. That is the floor case, not
CHOIR's full basis rule -- the full rule lives in the frozen synthesizer and
reaching it needs the evaluator. The distinction is recorded on the summary
itself rather than left for a reader to infer, because a system that reported a
judgment it had not computed would be the exact failure the plan's "proposals
are not facts" principle is about.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from daale.execution import trace as events
from daale.execution.commit import (
    Candidate,
    CandidateState,
    GateOutcome,
    apply_outcome,
    run_gate,
)
from daale.execution.contract import ContractResult, validate_package
from daale.execution.identity import ExecutionIdentity, identify
from daale.execution.state import (
    ExecutionLease,
    ReasoningStateStore,
    Snapshot,
)
from daale.execution.trace import ExecutionTrace


class ContractRejected(RuntimeError):
    """A package failed CHOIR contract validation and no execution was opened.

    Carries the violations and the trace, so a caller can report exactly what
    was wrong rather than only that something was.
    """

    def __init__(self, identity: ExecutionIdentity, result: ContractResult) -> None:
        super().__init__(
            f"package rejected: {len(result.violations)} contract violation(s)"
        )
        self.identity = identity
        self.result = result


@dataclass(frozen=True)
class ExecutionSummary:
    """What one execution did, in terms a reviewer can check.

    ``emits_judgment`` is always ``False`` in v0 and carries the reason with
    it. It is stated rather than omitted so that a consumer cannot mistake a
    completed execution for an adjudicated one.
    """

    identity: ExecutionIdentity
    committed: tuple[str, ...]
    rejected: tuple[str, ...]
    review_required: tuple[str, ...]
    insufficient_basis: bool
    emits_judgment: bool
    judgment_unavailable_because: str
    trace: tuple[events.ExecutionEvent, ...]


# Stated once, so every summary gives the same reason in the same words.
_NO_EVALUATOR = (
    "no evaluator: whether DAALE calls the frozen kernels or evaluates for "
    "itself is options B and A of DECISION-005, which is open"
)


class DCore:
    """Canonical control plane for one execution at a time."""

    def __init__(self, store: ReasoningStateStore) -> None:
        self._store = store
        self._identity: ExecutionIdentity | None = None
        self._lease: ExecutionLease | None = None
        self._trace: ExecutionTrace | None = None
        self._contract: ContractResult | None = None
        self._committed: list[str] = []
        self._rejected: list[str] = []
        self._review: list[str] = []

    # -- lifecycle ---------------------------------------------------------

    def open_execution(
        self, choir_version: str, package: Mapping[str, Any]
    ) -> ExecutionIdentity:
        """Validate a package, name the execution, and take write authority.

        Identity is computed before validation, so that a rejected package
        still has a stable name to report violations against. A rejection that
        cannot be referred to later is not much of an audit record.
        """
        if self._identity is not None:
            raise RuntimeError("an execution is already open on this D-Core")

        identity = identify(choir_version, package)
        trace = ExecutionTrace(identity.execution_id)
        trace.record(
            events.EXECUTION_OPENED,
            identity.execution_id,
            f"choir_version={choir_version} input_digest={identity.input_digest[:16]}",
        )

        result = validate_package(package)
        for violation in result.violations:
            trace.record(
                events.CONTRACT_VIOLATION,
                violation.subject,
                f"{violation.code}: {violation.detail}",
            )

        if not result.valid:
            self._trace = trace
            raise ContractRejected(identity, result)

        trace.record(
            events.CONTRACT_VALIDATED,
            identity.execution_id,
            f"{len(result.violations)} violations",
        )

        self._identity = identity
        self._trace = trace
        self._contract = result
        self._lease = self._store.open_execution(identity.execution_id)
        return identity

    def admit(self, candidate: Candidate) -> GateOutcome:
        """Put one candidate through the commit gate and apply the decision."""
        identity, lease, trace = self._require_open()

        self._store.propose(candidate.candidate_id)
        trace.record(
            events.CANDIDATE_PROPOSED,
            candidate.candidate_id,
            f"from {candidate.origin}",
        )

        decided, checks = run_gate(
            candidate, self._store, identity.execution_id, self._contract
        )
        if decided is CandidateState.VALIDATED:
            trace.record(events.CANDIDATE_VALIDATED, candidate.candidate_id)

        outcome = apply_outcome(candidate, decided, checks, self._store, lease)

        if outcome.state is CandidateState.COMMITTED:
            self._committed.append(candidate.object_id)
            trace.record(
                events.CANDIDATE_COMMITTED,
                candidate.candidate_id,
                f"{candidate.object_id} v"
                f"{self._store.current_version(candidate.object_id)}",
            )
        elif outcome.state is CandidateState.REVIEW_REQUIRED:
            self._review.append(candidate.candidate_id)
            trace.record(
                events.CANDIDATE_REVIEW_REQUIRED,
                candidate.candidate_id,
                f"origin '{candidate.origin}' is not deterministic",
            )
        else:
            self._rejected.append(candidate.candidate_id)
            trace.record(
                events.CANDIDATE_REJECTED,
                candidate.candidate_id,
                "; ".join(f"{c.name}: {c.detail}" for c in outcome.failures),
            )

        return outcome

    def take_snapshot(self) -> Snapshot:
        """Freeze canonical state for timeline and replay."""
        _, lease, _ = self._require_open()
        return self._store.take_snapshot(lease)

    def close(self) -> ExecutionSummary:
        """Terminate the execution and report what it established."""
        identity, lease, trace = self._require_open()

        insufficient = not self._committed
        if insufficient:
            trace.record(
                events.INSUFFICIENT_BASIS,
                identity.execution_id,
                "nothing was committed to canonical state",
            )

        trace.record(
            events.EXECUTION_CLOSED,
            identity.execution_id,
            f"committed={len(self._committed)} rejected={len(self._rejected)} "
            f"review={len(self._review)}",
        )
        self._store.close_execution(lease)

        summary = ExecutionSummary(
            identity=identity,
            committed=tuple(self._committed),
            rejected=tuple(self._rejected),
            review_required=tuple(self._review),
            insufficient_basis=insufficient,
            emits_judgment=False,
            judgment_unavailable_because=_NO_EVALUATOR,
            trace=trace.events,
        )
        self._identity = None
        self._lease = None
        return summary

    # -- reads -------------------------------------------------------------

    @property
    def trace(self) -> ExecutionTrace | None:
        """The trace for the current or most recent execution."""
        return self._trace

    def _require_open(
        self,
    ) -> tuple[ExecutionIdentity, ExecutionLease, ExecutionTrace]:
        """Return the open execution's context, or refuse."""
        if self._identity is None or self._lease is None or self._trace is None:
            raise RuntimeError("no execution is open; call open_execution first")
        return self._identity, self._lease, self._trace
