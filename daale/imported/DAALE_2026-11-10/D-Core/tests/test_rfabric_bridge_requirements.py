"""How the bridge relates a requirement to the evidence it cites, and how it passes on the review flag.

The bridge used to label every requirement that was not SATISFIED as WEAKENS, so a requirement the
evidence directly failed looked the same as one the evidence merely could not settle. And a packet
that said a human must review it was committed anyway.
"""

from __future__ import annotations

import unittest

from daale import rfabric
from daale.execution import CandidateState, validate_package
from daale.tests.test_rfabric_bridge import sample_trace


def package_for(status):
    trace = sample_trace()
    trace["decision_packet"]["requirement_summary"]["R1"] = {
        "status": status,
        "evidence_ids": ["E3"],
        "rationale": "x",
    }
    return rfabric.build_choir_package(trace)


def relations_from_r1(package):
    return {rel["relation"] for rel in package["relationships"] if rel["source"] == "R1"}


class RequirementRelationTests(unittest.TestCase):
    def test_a_satisfied_requirement_is_supported_by_what_it_cites(self) -> None:
        self.assertEqual(relations_from_r1(package_for("SATISFIED")), {"SUPPORTS"})

    def test_a_requirement_the_evidence_fails_is_contradicted_by_it(self) -> None:
        self.assertEqual(relations_from_r1(package_for("NOT_SATISFIED")), {"CONTRADICTS"})

    def test_a_requirement_the_evidence_cannot_settle_is_only_context(self) -> None:
        self.assertEqual(relations_from_r1(package_for("UNKNOWN")), {"CONTEXTUAL"})

    def test_a_requirement_missing_from_the_summary_is_unknown_and_cites_nothing(self) -> None:
        trace = sample_trace()
        trace["decision_packet"]["requirement_summary"] = {}
        package = rfabric.build_choir_package(trace)
        requirement = next(claim for claim in package["claims"] if claim["id"] == "R1")
        self.assertEqual(requirement["requirement_status"], "UNKNOWN")
        self.assertEqual([r for r in package["relationships"] if r["source"] == "R1"], [])

    def test_every_mapping_still_yields_an_admissible_package(self) -> None:
        for status in ("SATISFIED", "NOT_SATISFIED", "UNKNOWN"):
            with self.subTest(status=status):
                result = validate_package(package_for(status))
                self.assertTrue(result.valid, result.violations)


class ReviewFlagBridgeTests(unittest.TestCase):
    """R-Fabric's packet gained fields; the bridge passes the review flag on to the gate."""

    def test_the_aggregation_fields_on_a_requirement_do_not_trouble_the_bridge(self) -> None:
        trace = sample_trace()
        trace["decision_packet"]["requirement_summary"]["R1"].update(
            {"assessed_by": {"ANALYST": "NOT_SATISFIED"}, "disagreement": False}
        )
        admission = rfabric.admit(trace)
        self.assertIs(admission.outcome.state, CandidateState.COMMITTED)
        self.assertFalse(admission.outcome.candidate.needs_review)

    def test_a_packet_that_asks_for_human_review_is_held_not_committed(self) -> None:
        trace = sample_trace()
        trace["decision_packet"].update(
            {
                "policy_state": "ESCALATE",
                "policy_state_before_integrity_check": "ADVANCE",
                "triggered_rule": {
                    "rule_id": "INCOMPLETE-RUN-ADVANCE-BLOCKED",
                    "priority": -1,
                    "description": "The policy reached ADVANCE, but OUTSIDER failed.",
                },
                "execution_integrity": {
                    "requires_human_review": True,
                    "human_review_reasons": ["kernels failed: OUTSIDER"],
                },
            }
        )
        admission = rfabric.admit(trace)
        self.assertIs(admission.outcome.state, CandidateState.REVIEW_REQUIRED)
        self.assertTrue(admission.outcome.candidate.needs_review)
        self.assertEqual(admission.summary.committed, ())
        self.assertEqual(len(admission.summary.review_required), 1)

    def test_a_packet_that_does_not_ask_for_review_commits_as_before(self) -> None:
        trace = sample_trace()
        trace["decision_packet"]["execution_integrity"] = {
            "requires_human_review": False,
            "human_review_reasons": [],
        }
        admission = rfabric.admit(trace)
        self.assertIs(admission.outcome.state, CandidateState.COMMITTED)


if __name__ == "__main__":
    unittest.main()
