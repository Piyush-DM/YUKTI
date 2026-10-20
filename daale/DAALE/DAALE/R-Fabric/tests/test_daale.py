import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from daale.client import FixtureClient
from daale.pipeline import DaalePipeline, BASE_KERNELS
from daale.trace import write_trace
from daale.validation import DaaleValidationError, validate_adversary_output


ROOT = Path(__file__).resolve().parents[1]


def load_json(relative_path):
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def make_base_fixtures(overrides=None):
    """Create base kernel fixtures with optional per-kernel finding overrides."""
    base = {}
    for kernel in BASE_KERNELS:
        fixture = load_json(f"fixtures/{kernel.lower()}_output.json")
        key = kernel.lower()
        if overrides and key in overrides:
            fixture = deepcopy(fixture)
            fixture["findings"] = overrides[key]
        base[key] = fixture
    return base


class DaalePipelineTests(unittest.TestCase):
    def setUp(self):
        self.case = load_json("cases/vendor_alpha.json")
        self.policy = load_json("policies/vendor_post_technical_dd_v0_1.json")
        self.adversary = load_json("fixtures/adversary_output.json")

    def run_pipeline(self, base_overrides=None, adversary=None):
        base_fixtures = make_base_fixtures(base_overrides)
        client = FixtureClient(
            {
                **base_fixtures,
                "adversary": adversary or self.adversary,
            }
        )
        pipeline = DaalePipeline(
            client=client,
            model_by_kernel={"default": "offline-test"},
        )
        return pipeline.run(self.case, self.policy)

    def test_failed_critical_requirement_rejects(self):
        result = self.run_pipeline()
        self.assertEqual(result.decision_packet["policy_state"], "REJECT")
        self.assertEqual(
            result.decision_packet["triggered_rule"]["rule_id"],
            "P080-CRITICAL-FAILURE",
        )

    def test_high_adversarial_challenge_escalates_before_rejection(self):
        adversary = deepcopy(self.adversary)
        adversary["findings"][0]["severity"] = "HIGH"
        result = self.run_pipeline(adversary=adversary)
        self.assertEqual(result.decision_packet["policy_state"], "ESCALATE")
        self.assertEqual(
            result.decision_packet["triggered_rule"]["rule_id"],
            "P100-HIGH-CHALLENGE",
        )

    def test_unknown_mandatory_requirements_hold(self):
        unknown_findings = [
            {
                "finding_id": "TEST-001",
                "finding_type": "REQUIREMENT_ASSESSMENT",
                "target_type": "REQUIREMENT",
                "target_id": "R1",
                "evidence_ids": [],
                "content": "No evidence addresses this requirement.",
                "status": "UNKNOWN",
                "severity": "MEDIUM",
                "confidence": 0.5,
            },
            {
                "finding_id": "TEST-002",
                "finding_type": "REQUIREMENT_ASSESSMENT",
                "target_type": "REQUIREMENT",
                "target_id": "R2",
                "evidence_ids": [],
                "content": "No evidence addresses this requirement.",
                "status": "UNKNOWN",
                "severity": "MEDIUM",
                "confidence": 0.5,
            },
            {
                "finding_id": "TEST-003",
                "finding_type": "REQUIREMENT_ASSESSMENT",
                "target_type": "REQUIREMENT",
                "target_id": "R3",
                "evidence_ids": [],
                "content": "No evidence addresses this requirement.",
                "status": "UNKNOWN",
                "severity": "MEDIUM",
                "confidence": 0.5,
            },
            {
                "finding_id": "TEST-004",
                "finding_type": "REQUIREMENT_ASSESSMENT",
                "target_type": "REQUIREMENT",
                "target_id": "R4",
                "evidence_ids": [],
                "content": "No evidence addresses this requirement.",
                "status": "UNKNOWN",
                "severity": "MEDIUM",
                "confidence": 0.5,
            },
        ]
        # Need complete evidence matrix for each kernel
        for kernel in BASE_KERNELS:
            kernel_fixture = load_json(f"fixtures/{kernel.lower()}_output.json")
            evidence_relations = [f for f in kernel_fixture["findings"] if f["finding_type"] == "EVIDENCE_RELATION"]
            unknown_findings.extend(evidence_relations)
        overrides = {k.lower(): unknown_findings for k in BASE_KERNELS}
        result = self.run_pipeline(base_overrides=overrides)
        self.assertEqual(result.decision_packet["policy_state"], "HOLD")
        self.assertEqual(
            result.decision_packet["triggered_rule"]["rule_id"],
            "P060-MANDATORY-UNKNOWN",
        )

    def test_all_mandatory_requirements_satisfied_advances(self):
        satisfied_findings = [
            {
                "finding_id": "TEST-001",
                "finding_type": "REQUIREMENT_ASSESSMENT",
                "target_type": "REQUIREMENT",
                "target_id": "R1",
                "evidence_ids": ["E1"],
                "content": "E1 establishes this requirement is met.",
                "status": "SATISFIED",
                "severity": "LOW",
                "confidence": 0.9,
            },
            {
                "finding_id": "TEST-002",
                "finding_type": "REQUIREMENT_ASSESSMENT",
                "target_type": "REQUIREMENT",
                "target_id": "R2",
                "evidence_ids": ["E1"],
                "content": "E1 establishes this requirement is met.",
                "status": "SATISFIED",
                "severity": "LOW",
                "confidence": 0.9,
            },
            {
                "finding_id": "TEST-003",
                "finding_type": "REQUIREMENT_ASSESSMENT",
                "target_type": "REQUIREMENT",
                "target_id": "R3",
                "evidence_ids": ["E1"],
                "content": "E1 establishes this requirement is met.",
                "status": "SATISFIED",
                "severity": "LOW",
                "confidence": 0.9,
            },
            {
                "finding_id": "TEST-004",
                "finding_type": "REQUIREMENT_ASSESSMENT",
                "target_type": "REQUIREMENT",
                "target_id": "R4",
                "evidence_ids": ["E1"],
                "content": "E1 establishes this requirement is met.",
                "status": "SATISFIED",
                "severity": "LOW",
                "confidence": 0.9,
            },
        ]
        # Need complete evidence matrix for each kernel
        for kernel in BASE_KERNELS:
            kernel_fixture = load_json(f"fixtures/{kernel.lower()}_output.json")
            evidence_relations = [f for f in kernel_fixture["findings"] if f["finding_type"] == "EVIDENCE_RELATION"]
            satisfied_findings.extend(evidence_relations)
        overrides = {k.lower(): satisfied_findings for k in BASE_KERNELS}
        result = self.run_pipeline(base_overrides=overrides)
        self.assertEqual(result.decision_packet["policy_state"], "ADVANCE")
        self.assertEqual(
            result.decision_packet["triggered_rule"]["rule_id"],
            "P050-ALL-MANDATORY-SATISFIED",
        )

    def test_incomplete_evidence_matrix_is_rejected(self):
        incomplete_findings = [
            {
                "finding_id": "TEST-001",
                "finding_type": "EVIDENCE_RELATION",
                "target_type": "CLAIM",
                "target_id": "C1",
                "evidence_ids": ["E1"],
                "content": "E1 supports the claim.",
                "relation": "SUPPORTS",
                "severity": "LOW",
                "confidence": 0.8,
            },
        ]
        overrides = {k.lower(): incomplete_findings for k in BASE_KERNELS}
        with self.assertRaises(DaaleValidationError):
            self.run_pipeline(base_overrides=overrides)

    def test_invented_adversary_evidence_id_is_rejected(self):
        adversary = deepcopy(self.adversary)
        adversary["findings"][0]["evidence_ids"].append("E999")
        with self.assertRaises(DaaleValidationError):
            validate_adversary_output(adversary, self.case, self.policy)

    def test_trace_filenames_are_unique(self):
        first = self.run_pipeline()
        second = self.run_pipeline()
        with tempfile.TemporaryDirectory() as directory:
            first_path = write_trace(first.trace, directory)
            second_path = write_trace(second.trace, directory)
            self.assertNotEqual(first_path, second_path)
            self.assertTrue(first_path.exists())
            self.assertTrue(second_path.exists())


if __name__ == "__main__":
    unittest.main()