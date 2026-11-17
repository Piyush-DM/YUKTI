"""A proposer may flag a candidate for human review; the gate then escalates it instead of committing.

Added with the DECISION-005 ruling (2026-11-09). The flag can only add an escalation: it never lets
a candidate commit, and it does not change which origins may commit on their own.
"""

from __future__ import annotations

import unittest

from daale.execution import CandidateState, DCore, ReasoningStateStore
from daale.execution import trace as events
from daale.tests.test_execution import CHOIR_VERSION, candidate, package


class GateFlagTests(unittest.TestCase):
    def decide(self, **overrides):
        core = DCore(ReasoningStateStore())
        identity = core.open_execution(CHOIR_VERSION, package())
        outcome = core.admit(candidate(execution_id=identity.execution_id, **overrides))
        return core, outcome

    def test_an_unflagged_deterministic_candidate_still_commits(self) -> None:
        _, outcome = self.decide()
        self.assertIs(outcome.state, CandidateState.COMMITTED)

    def test_a_flagged_candidate_escalates_whatever_its_origin(self) -> None:
        for origin in ("rfabric", "dcore", "algorithm"):
            with self.subTest(origin=origin):
                core, outcome = self.decide(origin=origin, needs_review=True)
                self.assertIs(outcome.state, CandidateState.REVIEW_REQUIRED)
                summary = core.close()
                self.assertEqual(summary.committed, ())
                self.assertEqual(summary.review_required, ("cnd-001",))
                self.assertTrue(summary.insufficient_basis)

    def test_the_flag_never_lets_a_candidate_commit(self) -> None:
        # An origin outside the allow-list escalates with the flag and without it.
        for flagged in (False, True):
            with self.subTest(flagged=flagged):
                _, outcome = self.decide(origin="llm", needs_review=flagged)
                self.assertIs(outcome.state, CandidateState.REVIEW_REQUIRED)

    def test_a_failed_check_still_rejects_a_flagged_candidate(self) -> None:
        # No provenance fails a blocking check; escalation does not soften a rejection.
        _, outcome = self.decide(needs_review=True, provenance=())
        self.assertIs(outcome.state, CandidateState.REJECTED)

    def test_the_trace_says_why_it_was_escalated(self) -> None:
        core, _ = self.decide(needs_review=True)
        details = [e.detail for e in core.close().trace if e.kind == events.CANDIDATE_REVIEW_REQUIRED]
        self.assertEqual(details, ["flagged for human review by its proposer"])

    def test_an_unlisted_origin_still_says_its_origin_was_the_reason(self) -> None:
        core, _ = self.decide(origin="llm")
        details = [e.detail for e in core.close().trace if e.kind == events.CANDIDATE_REVIEW_REQUIRED]
        self.assertEqual(details, ["origin 'llm' is not deterministic"])


if __name__ == "__main__":
    unittest.main()
