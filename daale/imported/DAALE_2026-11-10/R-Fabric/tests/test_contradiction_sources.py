"""Whose CONTRADICTION findings count toward high_unresolved_contradictions.

Before 2026-11-17 only the adversary's did. A policy may set ``contradiction_sources`` to ``any_kernel``.
"""

import copy
import json
import unittest
from pathlib import Path

from daale.pipeline import BASE_KERNELS
from daale.policy_engine import apply_policy
from daale.validation import validate_case_and_policy

ROOT = Path(__file__).resolve().parents[1]


def load(relative_path):
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def contradiction(finding_id, evidence_ids, severity="HIGH"):
    return {
        "finding_id": finding_id, "finding_type": "CONTRADICTION", "target_type": "CLAIM", "target_id": "C1",
        "evidence_ids": evidence_ids, "content": "two items state incompatible facts", "severity": severity,
        "confidence": 0.9,
    }


class ContradictionSourceTests(unittest.TestCase):
    def setUp(self):
        self.case = load("cases/vendor_alpha.json")
        self.policy = load("policies/vendor_post_technical_dd_v0_1.json")
        self.outputs = {k: {"output": load(f"fixtures/{k.lower()}_output.json")} for k in BASE_KERNELS}
        self.outputs["ADVERSARY"] = {"output": load("fixtures/adversary_output.json")}
        self.outputs["ADVERSARY"]["output"]["findings"] = []  # the adversary raises nothing

    def add(self, kernel, finding):
        self.outputs[kernel]["output"]["findings"].append(finding)

    def metric(self, policy=None):
        packet = apply_policy(self.case, policy or self.policy, self.outputs)
        return packet["metrics"]["high_unresolved_contradictions"], packet["metrics"]["details"]["high_contradiction_ids"]

    def any_kernel(self):
        policy = copy.deepcopy(self.policy)
        policy["contradiction_sources"] = "any_kernel"
        return policy

    def test_by_default_a_base_kernel_contradiction_is_not_counted(self):
        self.add("CONTRARIAN", contradiction("K1", ["E1", "E2"]))
        self.assertEqual(self.metric(), (0, []))

    def test_any_kernel_counts_a_high_contradiction_from_a_base_kernel(self):
        self.add("CONTRARIAN", contradiction("K1", ["E1", "E2"]))
        self.assertEqual(self.metric(self.any_kernel()), (1, ["CONTRARIAN:K1"]))

    def test_a_contradiction_below_high_is_not_counted(self):
        self.add("CONTRARIAN", contradiction("K1", ["E1", "E2"], severity="MEDIUM"))
        self.assertEqual(self.metric(self.any_kernel())[0], 0)

    def test_the_same_contradiction_from_two_kernels_counts_once(self):
        self.add("CONTRARIAN", contradiction("K1", ["E1", "E2"]))
        self.add("OUTSIDER", contradiction("K2", ["E2", "E1"]))
        count, ids = self.metric(self.any_kernel())
        self.assertEqual(count, 1)
        self.assertEqual(len(ids), 1)

    def test_different_contradictions_each_count(self):
        self.add("CONTRARIAN", contradiction("K1", ["E1", "E2"]))
        self.add("OUTSIDER", contradiction("K2", ["E2", "E3"]))
        self.assertEqual(self.metric(self.any_kernel())[0], 2)

    def test_the_adversarys_own_contradiction_still_counts_alongside(self):
        self.outputs["ADVERSARY"]["output"]["findings"].append(contradiction("ADV-1", ["E1", "E2"]))
        self.add("CONTRARIAN", contradiction("K1", ["E2", "E3"]))
        count, ids = self.metric(self.any_kernel())
        self.assertEqual(count, 2)
        self.assertIn("ADV-1", ids)

    def test_the_policy_field_is_accepted_and_an_unknown_value_is_refused(self):
        validate_case_and_policy(self.case, self.any_kernel())
        bad = copy.deepcopy(self.policy)
        bad["contradiction_sources"] = "everyone"
        with self.assertRaises(Exception):
            validate_case_and_policy(self.case, bad)


if __name__ == "__main__":
    unittest.main()
