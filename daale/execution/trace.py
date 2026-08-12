"""The canonical execution trace: ordered events, recorded as they happen.

Research freeze §9: "Components record their own working as they compute; views
only format it. Nothing is reconstructed after the fact." This module is the
place the D-Core records its working.

The v0 plan states the same requirement as a principle -- "every dispatch,
candidate, validation, rejection, commit and state transition must be
replayable" -- and as an acceptance criterion: identical input, version and
configuration must produce an identical canonical output *and trace*.

Determinism
-----------

No clock and no randomness. Events carry a monotonically increasing sequence
number and nothing else that varies between runs, which is what lets two
executions of the same package be compared event for event. A timestamp here
would make every trace unique and the comparison worthless -- commitment X1
names "no clock" first for exactly this reason.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Event kinds. Constants rather than an enum because they are trace vocabulary,
# not a closed set the code branches on -- a reader of a trace needs to
# recognise them, and nothing dispatches on them.
EXECUTION_OPENED = "execution-opened"
CONTRACT_VALIDATED = "contract-validated"
CONTRACT_VIOLATION = "contract-violation"
CANDIDATE_PROPOSED = "candidate-proposed"
CANDIDATE_VALIDATED = "candidate-validated"
CANDIDATE_COMMITTED = "candidate-committed"
CANDIDATE_REJECTED = "candidate-rejected"
CANDIDATE_REVIEW_REQUIRED = "candidate-review-required"
INSUFFICIENT_BASIS = "insufficient-basis"
EXECUTION_CLOSED = "execution-closed"


@dataclass(frozen=True)
class ExecutionEvent:
    """One recorded step, in the order it occurred."""

    sequence: int
    execution_id: str
    kind: str
    subject: str
    detail: str


@dataclass
class ExecutionTrace:
    """An append-only sequence of execution events.

    Append-only is the point, and it matches how institutional history is
    treated everywhere else in this repository (``DECISION-004``). A trace that
    can be edited after the fact explains nothing.
    """

    execution_id: str
    _events: list[ExecutionEvent] = field(default_factory=list)

    def record(self, kind: str, subject: str, detail: str = "") -> ExecutionEvent:
        """Append one event and return it."""
        event = ExecutionEvent(
            sequence=len(self._events),
            execution_id=self.execution_id,
            kind=kind,
            subject=subject,
            detail=detail,
        )
        self._events.append(event)
        return event

    @property
    def events(self) -> tuple[ExecutionEvent, ...]:
        """Every event recorded so far, in order."""
        return tuple(self._events)

    def of_kind(self, kind: str) -> tuple[ExecutionEvent, ...]:
        """Every event of one kind, in order."""
        return tuple(event for event in self._events if event.kind == kind)

    def render(self) -> str:
        """Lay the trace out as text. A projection; it decides nothing."""
        return "\n".join(
            f"{event.sequence:>3}  {event.kind:<26} {event.subject}"
            + (f" -- {event.detail}" if event.detail else "")
            for event in self._events
        )
