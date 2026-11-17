"""Tests for the R-Fabric bridge: the DECISION-005 ruling, made mechanical.

The property that matters most here is the one ``test_execution.py`` already
assumed by making ``"rfabric"`` its candidate fixture's default origin: a
finished R-Fabric trace, translated by this bridge, passes every active gate
check and commits. A regression here is a regression in the ruling itself, not
just in a translation helper.
"""

from __future__ import annotations

import unittest

from daale import rfabric
from daale.execution import CandidateState, ContractRejected, ReasoningStateStore


def sample_trace(**overrides):
    """A minimal but realistic R-Fabric trace, shaped like a real run's output.

    Trimmed from an actual offline run of the vendor due-diligence case: two
    claims, three evidence items, four policy requirements, one analyst pass,
    one adversary pass, and the deterministic policy decision they produced.
    """
    trace = {
        "run": {"run_id": "run-test0000000000000000000000000"},
        "choir_contract_version": "CHOIR-CONTRACT-DRAFT-0.1",
        "daale_version": "0.1.0",
        "case": {
            "case_id": "DD-TEST",
            "decision_stage": "post_technical_due_diligence_approval",
            "decision_question": "Is the vendor ready for approval?",
            "claims": [
                {"claim_id": "C1", "text": "Controls are complete."},
                {"claim_id": "C2", "text": "Risk profile is acceptable."},
            ],
            "evidence": [
                {
                    "evidence_id": "E1",
                    "text": "Revenue grew 18 percent.",
                    "source": {
                        "source_id": "S1",
                        "source_type": "DOCUMENT",
                        "title": "Financial statement",
                    },
                },
                {
                    "evidence_id": "E3",
                    "text": "Security questionnaire is incomplete.",
                    "source": {
                        "source_id": "S3",
                        "source_type": "SYSTEM_RECORD",
                        "title": "Evidence register",
                    },
                },
            ],
        },
        "policy": {
            "policy_id": "VENDOR-POST-TECH-DD",
            "policy_version": "0.1",
            "requirements": [
                {
                    "requirement_id": "R1",
                    "description": "A completed security questionnaire is supplied.",
                    "mandatory": True,
                    "critical": True,
                },
            ],
        },
        "provisional_findings": {
            "analyst": {
                "case_id": "DD-TEST",
                "claim_analyses": [
                    {
                        "claim_id": "C1",
                        "provisional_status": "CONTRADICTED",
                        "evidence_relations": [
                            {
                                "evidence_id": "E3",
                                "relation": "CONTRADICTS",
                                "rationale": "questionnaire incomplete",
                            },
                            {
                                "evidence_id": "E1",
                                "relation": "IRRELEVANT",
                                "rationale": "unrelated to controls",
                            },
                        ],
                        "uncertainties": [],
                    },
                    {
                        "claim_id": "C2",
                        "provisional_status": "INSUFFICIENT_EVIDENCE",
                        "evidence_relations": [
                            {
                                "evidence_id": "E1",
                                "relation": "SUPPORTS",
                                "rationale": "revenue growth is favourable",
                            },
                            {
                                "evidence_id": "E3",
                                "relation": "WEAKENS",
                                "rationale": "security gap raises risk",
                            },
                        ],
                        "uncertainties": ["no customer-concentration threshold defined"],
                    },
                ],
                "requirement_assessments": [
                    {
                        "requirement_id": "R1",
                        "status": "NOT_SATISFIED",
                        "evidence_ids": ["E3"],
                        "rationale": "questionnaire incomplete",
                    }
                ],
                "assumptions": ["The evidence register is complete."],
            }
        },
        "decision_packet": {
            "case_id": "DD-TEST",
            "decision_stage": "post_technical_due_diligence_approval",
            "policy_id": "VENDOR-POST-TECH-DD",
            "policy_version": "0.1",
            "policy_state": "REJECT",
            "triggered_rule": {
                "rule_id": "P080-CRITICAL-FAILURE",
                "priority": 80,
                "description": "Reject on critical failure.",
            },
            "other_matching_rule_ids": [],
            "metrics": {"failed_critical_requirements": 1},
            "requirement_summary": {
                "R1": {
                    "status": "NOT_SATISFIED",
                    "evidence_ids": ["E3"],
                    "rationale": "questionnaire incomplete",
                }
            },
            "provisional_claim_statuses": {"C1": "CONTRADICTED", "C2": "INSUFFICIENT_EVIDENCE"},
            "adversarial_summary": "The security gap is the deciding factor.",
            "authority_notice": (
                "This is a deterministic DAALE policy state, not an autonomous "
                "institutional decision. Authorized human review is required."
            ),
        },
    }
    trace.update(overrides)
    return trace


class TestBuildChoirPackage(unittest.TestCase):
    """The A2 translation: every identifier traced back to something R-Fabric validated."""

    def test_the_package_is_admissible_under_commitment_a2(self) -> None:
        from daale.execution import validate_package

        package = rfabric.build_choir_package(sample_trace())
        result = validate_package(package)
        self.assertTrue(result.valid, result.violations)

    def test_choir_version_is_rfabrics_own_draft_not_the_canonical_freeze(self) -> None:
        """Overclaiming compliance with the frozen v0.1 freeze is the one thing
        this bridge must never do -- see the module docstring."""
        package = rfabric.build_choir_package(sample_trace())
        self.assertEqual(package["choir_version"], "CHOIR-CONTRACT-DRAFT-0.1")
        self.assertNotEqual(package["choir_version"], "0.1")

    def test_case_claims_and_policy_requirements_both_become_claims(self) -> None:
        package = rfabric.build_choir_package(sample_trace())
        claim_ids = {claim["id"] for claim in package["claims"]}
        self.assertEqual(claim_ids, {"C1", "C2", "R1"})

    def test_evidence_relations_become_relationships(self) -> None:
        package = rfabric.build_choir_package(sample_trace())
        pairs = {(rel["source"], rel["target"]) for rel in package["relationships"]}
        self.assertIn(("C1", "E3"), pairs)
        self.assertIn(("C2", "E1"), pairs)

    def test_no_claim_or_evidence_id_is_invented(self) -> None:
        """Every identifier must come from the case, the policy, or a
        validated finding -- never synthesised out of nothing."""
        package = rfabric.build_choir_package(sample_trace())
        evidence_ids = {item["id"] for item in package["evidence"]}
        self.assertEqual(evidence_ids, {"E1", "E3"})


class TestAdmit(unittest.TestCase):
    """The ruling, exercised: R-Fabric evaluates, D-Core commits."""

    def test_a_finished_trace_commits_under_origin_rfabric(self) -> None:
        admission = rfabric.admit(sample_trace())
        self.assertIs(admission.outcome.state, CandidateState.COMMITTED)
        self.assertEqual(admission.outcome.candidate.origin, "rfabric")
        self.assertEqual(admission.summary.committed, ("rfabric-judgment:DD-TEST",))
        self.assertFalse(admission.summary.insufficient_basis)

    def test_the_committed_payload_is_the_full_decision_packet(self) -> None:
        trace = sample_trace()
        admission = rfabric.admit(trace)
        self.assertEqual(
            dict(admission.outcome.candidate.payload), trace["decision_packet"]
        )

    def test_committing_never_emits_a_judgment(self) -> None:
        """The DECISION-005 boundary holds even for a candidate that commits.

        Committing a policy state is not adjudicating one; the summary must
        say so regardless of whether the candidate was accepted."""
        admission = rfabric.admit(sample_trace())
        self.assertFalse(admission.summary.emits_judgment)
        self.assertIn("DECISION-005", admission.summary.judgment_unavailable_because)

    def test_provenance_names_every_claim_and_cited_evidence_item(self) -> None:
        admission = rfabric.admit(sample_trace())
        self.assertEqual(
            set(admission.outcome.candidate.provenance), {"C1", "C2", "E3"}
        )

    def test_a_trace_with_no_findings_produces_no_provenance_and_is_rejected(
        self,
    ) -> None:
        """A candidate that cannot trace back to anything must never commit --
        the same invariant ``test_execution.py`` defends generically, exercised
        here through the real translation path."""
        empty = sample_trace()
        empty["decision_packet"]["provisional_claim_statuses"] = {}
        empty["decision_packet"]["requirement_summary"] = {}
        admission = rfabric.admit(empty)
        self.assertIs(admission.outcome.state, CandidateState.REJECTED)
        self.assertIsNone(
            ReasoningStateStore().canonical("rfabric-judgment:DD-TEST")
        )

    def test_a_malformed_translation_raises_contract_rejected_not_a_silent_pass(
        self,
    ) -> None:
        """If a claim somehow cited an evidence id the case never declared,
        the gate must refuse the package outright rather than admit it."""
        broken = sample_trace()
        broken["provisional_findings"]["analyst"]["claim_analyses"][0][
            "evidence_relations"
        ].append(
            {
                "evidence_id": "E404",
                "relation": "CONTRADICTS",
                "rationale": "cites evidence the case never declared",
            }
        )
        with self.assertRaises(ContractRejected) as caught:
            rfabric.admit(broken)
        self.assertIn(
            "dangling-reference", [v.code for v in caught.exception.result.violations]
        )


if __name__ == "__main__":
    unittest.main()
