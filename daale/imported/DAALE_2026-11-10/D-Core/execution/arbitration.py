"""D-Core Arbitration Contract: resolving conflicting candidate proposals.

This module implements the arbitration logic for the D-Core's governance
sequence: VALIDATE -> ORDER -> ARBITRATE -> COMMIT.

When multiple candidates propose different states for the same object (or
when a single candidate's payload contains internally conflicting findings),
the arbiter decides which proposal, if any, becomes canonical.

The arbitration contract is the "highest-priority unresolved specification"
in the project: what does D-Core do when kernels genuinely conflict?
(e.g. Analyst says INVEST, Adversary says REJECT, Forecaster gives 62%)

This implementation follows these principles:
- Workers propose; D-Core commits (core invariant)
- Arbitration is deterministic and auditable
- The policy engine's deterministic rules are the primary arbitration mechanism
- Conflicting candidates for the same object are resolved by provenance,
  specificity, and origin authority
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from daale.execution.commit import Candidate, CandidateState, GateCheck, CheckStatus


class ArbitrationOutcome(Enum):
    """Result of arbitration between conflicting candidates."""

    # One candidate wins and is forwarded to commit gate
    CANDIDATE_SELECTED = "candidate-selected"
    # No candidate can be selected; escalation required
    ESCALATE = "escalate"
    # All candidates rejected; insufficient basis
    REJECT_ALL = "reject-all"


class ConflictKind(Enum):
    """Classification of the conflict between candidates."""

    # Different decision states for same object (e.g. ADVANCE vs REJECT)
    DECISION_CONFLICT = "decision-conflict"
    # Same decision state but different rationales/evidence
    RATIONALE_CONFLICT = "rationale-conflict"
    # Candidates from different origins for same object
    ORIGIN_CONFLICT = "origin-conflict"
    # Internal contradiction within a single candidate's payload
    INTERNAL_CONTRADICTION = "internal-contradiction"


@dataclass(frozen=True)
class ArbitrationCheck:
    """One arbitration check with its outcome."""

    name: str
    passed: bool
    detail: str
    conflict_kind: ConflictKind | None = None


@dataclass(frozen=True)
class ArbitrationResult:
    """Complete arbitration result for a set of candidates."""

    outcome: ArbitrationOutcome
    selected_candidate: Candidate | None
    rejected_candidates: tuple[Candidate, ...]
    checks: tuple[ArbitrationCheck, ...]
    conflict_kind: ConflictKind | None = None

    @property
    def is_decisive(self) -> bool:
        """Whether arbitration produced a committable candidate."""
        return self.outcome is ArbitrationOutcome.CANDIDATE_SELECTED


# Origin precedence for arbitration (higher = more authoritative)
# Deterministic origins are tied; non-deterministic origins rank below
_ORIGIN_PRECEDENCE: dict[str, int] = {
    "dcore": 100,
    "rfabric": 100,
    "algorithm": 100,
    "human": 90,
    "llm": 50,
    "external": 10,
}


def _origin_precedence(origin: str) -> int:
    """Return precedence rank for an origin (higher = more authoritative)."""
    return _ORIGIN_PRECEDENCE.get(origin, 0)


def _extract_policy_state(payload: Mapping[str, Any]) -> str | None:
    """Extract the policy state from a candidate payload."""
    return payload.get("policy_state")


def _extract_provenance_breadth(candidate: Candidate) -> int:
    """Measure how many distinct evidence/claim IDs a candidate's provenance covers."""
    return len(candidate.provenance)


def _has_internal_contradiction(candidate: Candidate) -> tuple[bool, str]:
    """Check if a candidate's own payload contains contradictory findings.

    Returns (has_contradiction, detail).
    """
    payload = candidate.payload
    provisional = payload.get("provisional_claim_statuses", {})
    requirement_summary = payload.get("requirement_summary", {})

    # Check: claim status CONTRADICTED but requirement SATISFIED on same evidence
    for claim_id, status in provisional.items():
        if status == "CONTRADICTED":
            for req_id, req_data in requirement_summary.items():
                if req_data.get("status") == "SATISFIED":
                    shared_evidence = set(provisional.get(claim_id, {}).get("evidence_ids", [])) & set(req_data.get("evidence_ids", []))
                    if shared_evidence:
                        return True, f"Claim {claim_id} contradicted but requirement {req_id} satisfied on shared evidence {shared_evidence}"

    # Check: multiple conflicting claim statuses for same claim (shouldn't happen in valid payload)
    if len(provisional) != len(set(provisional.keys())):
        return True, "Duplicate claim IDs in provisional_claim_statuses"

    return False, ""


def _compare_candidates(a: Candidate, b: Candidate) -> int:
    """Compare two candidates for arbitration precedence.

    Returns positive if a > b, negative if a < b, 0 if equal.
    Higher precedence wins.

    Precedence rules (in order):
    1. Origin precedence (deterministic > human > llm > external)
    2. Provenance breadth (more evidence/claims cited = more grounded)
    3. Policy state specificity (REJECT/ADVANCE > HOLD/ESCALATE > UNKNOWN)
    """
    # Rule 1: Origin precedence
    a_prec = _origin_precedence(a.origin)
    b_prec = _origin_precedence(b.origin)
    if a_prec != b_prec:
        return a_prec - b_prec

    # Rule 2: Provenance breadth
    a_breadth = _extract_provenance_breadth(a)
    b_breadth = _extract_provenance_breadth(b)
    if a_breadth != b_breadth:
        return a_breadth - b_breadth

    # Rule 3: Policy state specificity
    state_rank = {"REJECT": 4, "ADVANCE": 4, "ESCALATE": 3, "HOLD": 2, "UNKNOWN": 1}
    a_state = _extract_policy_state(a.payload) or "UNKNOWN"
    b_state = _extract_policy_state(b.payload) or "UNKNOWN"
    a_rank = state_rank.get(a_state, 0)
    b_rank = state_rank.get(b_state, 0)
    if a_rank != b_rank:
        return a_rank - b_rank

    return 0


def arbitrate_candidates(
    candidates: tuple[Candidate, ...],
    contract_valid: bool = True,
) -> ArbitrationResult:
    """Arbitrate between multiple candidates for the same object.

    This is the core arbitration contract. It implements deterministic
    resolution of conflicting proposals following the principles:
    - Deterministic, auditable, no hidden authority
    - Policy engine rules are primary; arbitration is tiebreaker
    - All decisions traceable to provenance and origin
    """
    if not candidates:
        return ArbitrationResult(
            outcome=ArbitrationOutcome.REJECT_ALL,
            selected_candidate=None,
            rejected_candidates=(),
            checks=(ArbitrationCheck(
                name="no-candidates",
                passed=True,
                detail="no candidates proposed",
                conflict_kind=None,
            ),),
        )

    if len(candidates) == 1:
        candidate = candidates[0]

        # Check for internal contradiction
        has_contradiction, detail = _has_internal_contradiction(candidate)
        if has_contradiction:
            return ArbitrationResult(
                outcome=ArbitrationOutcome.ESCALATE,
                selected_candidate=None,
                rejected_candidates=(candidate,),
                checks=(ArbitrationCheck(
                    name="internal-contradiction",
                    passed=False,
                    detail=detail,
                    conflict_kind=ConflictKind.INTERNAL_CONTRADICTION,
                ),),
                conflict_kind=ConflictKind.INTERNAL_CONTRADICTION,
            )

        # Single candidate: check contract validity
        if not contract_valid:
            return ArbitrationResult(
                outcome=ArbitrationOutcome.REJECT_ALL,
                selected_candidate=None,
                rejected_candidates=(candidate,),
                checks=(ArbitrationCheck(
                    name="contract-invalid",
                    passed=False,
                    detail="candidate's package failed CHOIR contract validation",
                    conflict_kind=None,
                ),),
            )

        return ArbitrationResult(
            outcome=ArbitrationOutcome.CANDIDATE_SELECTED,
            selected_candidate=candidate,
            rejected_candidates=(),
            checks=(ArbitrationCheck(
                name="single-candidate",
                passed=True,
                detail=f"single candidate {candidate.candidate_id} selected by default",
                conflict_kind=None,
            ),),
        )

    # Multiple candidates: detect conflict kind
    states = {_extract_policy_state(c.payload) for c in candidates}
    origins = {c.origin for c in candidates}

    conflict_kind = None
    if len(states) > 1:
        conflict_kind = ConflictKind.DECISION_CONFLICT
    elif len(origins) > 1:
        conflict_kind = ConflictKind.ORIGIN_CONFLICT
    else:
        conflict_kind = ConflictKind.RATIONALE_CONFLICT

    # Sort by precedence
    sorted_candidates = sorted(candidates, key=lambda c: (
        _origin_precedence(c.origin),
        _extract_provenance_breadth(c),
        {"REJECT": 4, "ADVANCE": 4, "ESCALATE": 3, "HOLD": 2, "UNKNOWN": 1}.get(
            _extract_policy_state(c.payload) or "UNKNOWN", 0
        ),
    ), reverse=True)

    winner = sorted_candidates[0]
    losers = sorted_candidates[1:]

    # Verify winner doesn't have internal contradiction
    has_contradiction, detail = _has_internal_contradiction(winner)
    if has_contradiction:
        return ArbitrationResult(
            outcome=ArbitrationOutcome.ESCALATE,
            selected_candidate=None,
            rejected_candidates=candidates,
            checks=(ArbitrationCheck(
                name="winner-internal-contradiction",
                passed=False,
                detail=detail,
                conflict_kind=ConflictKind.INTERNAL_CONTRADICTION,
            ),),
            conflict_kind=ConflictKind.INTERNAL_CONTRADICTION,
        )

    # Check if losers have equal precedence (genuine tie)
    if losers and _compare_candidates(winner, losers[0]) == 0:
        return ArbitrationResult(
            outcome=ArbitrationOutcome.ESCALATE,
            selected_candidate=None,
            rejected_candidates=candidates,
            checks=(ArbitrationCheck(
                name="equal-precedence-tie",
                passed=False,
                detail=f"candidates {winner.candidate_id} and {losers[0].candidate_id} have equal arbitration precedence",
                conflict_kind=conflict_kind,
            ),),
            conflict_kind=conflict_kind,
        )

    return ArbitrationResult(
        outcome=ArbitrationOutcome.CANDIDATE_SELECTED,
        selected_candidate=winner,
        rejected_candidates=tuple(losers),
        checks=(
            ArbitrationCheck(
                name="conflict-detected",
                passed=True,
                detail=f"detected {conflict_kind.value} among {len(candidates)} candidates",
                conflict_kind=conflict_kind,
            ),
            ArbitrationCheck(
                name="precedence-resolution",
                passed=True,
                detail=f"selected {winner.candidate_id} (origin={winner.origin}, "
                       f"provenance_breadth={_extract_provenance_breadth(winner)}, "
                       f"state={_extract_policy_state(winner.payload)})",
                conflict_kind=conflict_kind,
            ),
            ArbitrationCheck(
                name="loser-rejection",
                passed=True,
                detail=f"rejected {len(losers)} lower-precedence candidate(s)",
                conflict_kind=conflict_kind,
            ),
        ),
        conflict_kind=conflict_kind,
    )


# Exported API
__all__ = [
    "ArbitrationOutcome",
    "ConflictKind",
    "ArbitrationCheck",
    "ArbitrationResult",
    "arbitrate_candidates",
]