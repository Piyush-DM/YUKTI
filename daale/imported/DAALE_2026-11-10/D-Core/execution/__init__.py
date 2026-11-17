"""DAALE execution: the D-Core, its state store, its trace, and the commit gate.

Phases 1 and 2 of the DAALE v0 execution plan.

* **Phase 1 — single-threaded D-Core.** Deterministic control plane, canonical
  state model, execution identity and trace.
* **Phase 2 — commit protocol.** The candidate lifecycle and the seven-check
  commit gate.

The invariant everything here serves: **anything may propose; only the D-Core
commits.** A canonical write requires a lease the store issues to one open
execution at a time, and the D-Core is the only holder.

There is no evaluator, deliberately. See ``dcore`` for the exact
``DECISION-005`` boundary and why no placeholder was left in its place.

Nothing in this package imports ``choir_prototype`` or ``applications``.
"""

from daale.execution.commit import (
    DETERMINISTIC_ORIGINS,
    Candidate,
    CandidateState,
    CheckStatus,
    GateCheck,
    GateOutcome,
    apply_outcome,
    run_gate,
)
from daale.execution.contract import (
    IDENTIFIED_SECTIONS,
    IR_SECTIONS,
    ContractResult,
    ContractViolation,
    validate_package,
)
from daale.execution.dcore import (
    ContractRejected,
    DCore,
    ExecutionSummary,
)
from daale.execution.identity import (
    EXECUTION_SCHEME,
    ExecutionIdentity,
    compute_execution_id,
    compute_input_digest,
    identify,
)
from daale.execution.state import (
    CanonicalObject,
    ExecutionLease,
    ReasoningStateStore,
    Snapshot,
    StaleWrite,
    UnauthorizedWrite,
)
from daale.execution.trace import ExecutionEvent, ExecutionTrace

__all__ = [
    "DETERMINISTIC_ORIGINS",
    "EXECUTION_SCHEME",
    "IDENTIFIED_SECTIONS",
    "IR_SECTIONS",
    "Candidate",
    "CandidateState",
    "CanonicalObject",
    "CheckStatus",
    "ContractRejected",
    "ContractResult",
    "ContractViolation",
    "DCore",
    "ExecutionEvent",
    "ExecutionIdentity",
    "ExecutionLease",
    "ExecutionSummary",
    "ExecutionTrace",
    "GateCheck",
    "GateOutcome",
    "ReasoningStateStore",
    "Snapshot",
    "StaleWrite",
    "UnauthorizedWrite",
    "apply_outcome",
    "compute_execution_id",
    "compute_input_digest",
    "identify",
    "run_gate",
    "validate_package",
]
