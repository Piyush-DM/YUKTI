"""One verdict per policy requirement, whatever order the kernels answered in.

Before 2026-11-09 the verdict for a requirement was whichever kernel happened to come last,
and a requirement nobody assessed was missing from the summary instead of being UNKNOWN.
"""

import copy
import json
import unittest
from pathlib import Path

from daale.pipeline import BASE_KERNELS
from daale.policy_engine import aggregate_requirement_assessments, apply_policy

ROOT = Path(__file__).resolve().parents[1]
ASSESSORS = ("ANALYST", "FIRST_PRINCIPLES", "HISTORIAN")  # the fixture kernels that assess requirements


def load(relative_path):
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def all_outputs():
    outputs = {k: {"output": load(f"fixtures/{k.lower()}_output.json")} for k in BASE_KERNELS}
    outputs["ADVERSARY"] = {"output": load("fixtures/adversary_output.json")}
    return outputs


def assessments(outputs, kernel, requirement=None):
    return [
        finding
        for finding in outputs[kernel]["output"]["findings"]
        if finding["finding_type"] == "REQUIREMENT_ASSESSMENT"
        and requirement in (None, finding["target_id"])
    ]


def everyone_says(outputs, status):
    for kernel in ASSESSORS:
        for finding in assessments(outputs, kernel):
            finding["status"] = status


def base_only(outputs):
    return {k: v for k, v in outputs.items() if k != "ADVERSARY"}


class AggregationTests(unittest.TestCase):
    def setUp(self):
        self.case = load("cases/vendor_alpha.json")
        self.policy = load("policies/vendor_post_technical_dd_v0_1.json")

    def test_the_sample_kernels_agree_and_keep_their_known_verdicts(self):
        outputs = all_outputs()
        summary = aggregate_requirement_assessments(self.policy, base_only(outputs))
        self.assertEqual(
            {requirement: entry["status"] for requirement, entry in summary.items()},
            {"R1": "NOT_SATISFIED", "R2": "NOT_SATISFIED", "R3": "UNKNOWN", "R4": "UNKNOWN"},
        )
        self.assertFalse(any(entry["disagreement"] for entry in summary.values()))
        self.assertEqual(list(summary["R1"]["assessed_by"]), list(ASSESSORS))
        packet = apply_policy(self.case, self.policy, outputs)
        self.assertEqual(packet["triggered_rule"]["rule_id"], "P080-CRITICAL-FAILURE")

    def test_disagreement_makes_a_requirement_unknown_and_is_recorded(self):
        outputs = all_outputs()
        everyone_says(outputs, "SATISFIED")
        assessments(outputs, "HISTORIAN", "R3")[0]["status"] = "NOT_SATISFIED"
        summary = aggregate_requirement_assessments(self.policy, base_only(outputs))
        contested = summary["R3"]
        self.assertEqual(contested["status"], "UNKNOWN")
        self.assertTrue(contested["disagreement"])
        self.assertEqual(
            contested["assessed_by"],
            {"ANALYST": "SATISFIED", "FIRST_PRINCIPLES": "SATISFIED", "HISTORIAN": "NOT_SATISFIED"},
        )
        self.assertIn("disagree", contested["rationale"])
        self.assertEqual(summary["R1"]["status"], "SATISFIED")

    def test_a_contested_requirement_cannot_advance_and_holds_instead(self):
        outputs = all_outputs()
        everyone_says(outputs, "SATISFIED")
        outputs["ADVERSARY"]["output"]["findings"] = []
        control = apply_policy(self.case, self.policy, outputs)
        self.assertEqual(control["policy_state"], "ADVANCE")

        assessments(outputs, "HISTORIAN", "R3")[0]["status"] = "NOT_SATISFIED"
        packet = apply_policy(self.case, self.policy, outputs)
        self.assertEqual(packet["policy_state"], "HOLD")
        self.assertEqual(packet["triggered_rule"]["rule_id"], "P060-MANDATORY-UNKNOWN")
        self.assertEqual(packet["metrics"]["details"]["requirement_disagreement_ids"], ["R3"])

    def test_a_requirement_nobody_assessed_is_unknown_and_listed(self):
        outputs = all_outputs()
        for kernel in ASSESSORS:
            outputs[kernel]["output"]["findings"] = [
                finding
                for finding in outputs[kernel]["output"]["findings"]
                if not (finding["finding_type"] == "REQUIREMENT_ASSESSMENT" and finding["target_id"] == "R4")
            ]
        packet = apply_policy(self.case, self.policy, outputs)
        self.assertEqual(set(packet["requirement_summary"]), {"R1", "R2", "R3", "R4"})
        self.assertEqual(packet["requirement_summary"]["R4"]["status"], "UNKNOWN")
        self.assertEqual(packet["requirement_summary"]["R4"]["assessed_by"], {})
        self.assertEqual(packet["metrics"]["details"]["unassessed_requirement_ids"], ["R4"])

    def test_the_order_the_kernels_are_listed_in_changes_nothing(self):
        outputs = all_outputs()
        assessments(outputs, "HISTORIAN", "R1")[0]["status"] = "SATISFIED"  # a dissenter
        forward = apply_policy(self.case, self.policy, outputs)
        backward = apply_policy(self.case, self.policy, dict(reversed(list(outputs.items()))))
        for key in ("policy_state", "triggered_rule", "metrics", "requirement_summary"):
            self.assertEqual(forward[key], backward[key], key)

    def test_the_summary_and_the_metrics_come_from_the_same_verdicts(self):
        packet = apply_policy(self.case, self.policy, all_outputs())
        critical = {r["requirement_id"] for r in self.policy["requirements"] if r["critical"]}
        failed = {r for r, entry in packet["requirement_summary"].items() if entry["status"] == "NOT_SATISFIED"}
        self.assertEqual(sorted(failed & critical), packet["metrics"]["details"]["failed_critical_requirement_ids"])

    def test_a_kernel_that_contradicts_itself_has_no_verdict(self):
        outputs = all_outputs()
        twin = copy.deepcopy(assessments(outputs, "ANALYST", "R1")[0])
        twin["finding_id"] = "ANALYST-R1-TWIN"
        twin["status"] = "SATISFIED"
        outputs["ANALYST"]["output"]["findings"].append(twin)
        summary = aggregate_requirement_assessments(self.policy, base_only(outputs))
        self.assertEqual(summary["R1"]["assessed_by"]["ANALYST"], "UNKNOWN")
        self.assertTrue(summary["R1"]["disagreement"])


class UnanimousDefiniteTests(unittest.TestCase):
    """``requirement_aggregation: unanimous_definite`` -- UNKNOWN abstains, it does not dissent."""

    def setUp(self):
        self.policy = dict(load("policies/vendor_post_technical_dd_v0_1.json"))
        self.policy["requirement_aggregation"] = "unanimous_definite"

    def verdict(self, analyst, first_principles, historian):
        outputs = all_outputs()
        for kernel, status in zip(ASSESSORS, (analyst, first_principles, historian)):
            assessments(outputs, kernel, "R3")[0]["status"] = status
        return aggregate_requirement_assessments(self.policy, base_only(outputs))["R3"]

    def test_one_abstention_does_not_overturn_an_agreed_verdict(self):
        entry = self.verdict("SATISFIED", "SATISFIED", "UNKNOWN")
        self.assertEqual(entry["status"], "SATISFIED")
        self.assertFalse(entry["disagreement"])
        self.assertEqual(entry["abstained"], ["HISTORIAN"])

    def test_a_real_dissent_still_makes_the_requirement_unknown(self):
        entry = self.verdict("SATISFIED", "SATISFIED", "NOT_SATISFIED")
        self.assertEqual(entry["status"], "UNKNOWN")
        self.assertTrue(entry["disagreement"])

    def test_a_verdict_needs_more_kernels_deciding_than_abstaining(self):
        self.assertEqual(self.verdict("SATISFIED", "UNKNOWN", "UNKNOWN")["status"], "UNKNOWN")
        self.assertEqual(self.verdict("UNKNOWN", "UNKNOWN", "UNKNOWN")["status"], "UNKNOWN")

    def test_abstention_cannot_hide_a_failure(self):
        self.assertEqual(self.verdict("NOT_SATISFIED", "NOT_SATISFIED", "UNKNOWN")["status"], "NOT_SATISFIED")

    def test_a_policy_without_the_field_keeps_the_unanimous_rule(self):
        del self.policy["requirement_aggregation"]
        entry = self.verdict("SATISFIED", "SATISFIED", "UNKNOWN")
        self.assertEqual(entry["status"], "UNKNOWN")
        self.assertNotIn("abstained", entry)


class ClaimAggregationTests(unittest.TestCase):
    """Claim statuses in the packet come from every kernel, not from whichever answered last."""

    def setUp(self):
        self.case = load("cases/vendor_alpha.json")
        self.policy = load("policies/vendor_post_technical_dd_v0_1.json")

    def claims(self, outputs, kernel, claim="C1"):
        return [
            finding
            for finding in outputs[kernel]["output"]["findings"]
            if finding["finding_type"] == "CLAIM_ASSESSMENT" and finding["target_id"] == claim
        ]

    def everyone_says_claim(self, outputs, status):
        for kernel in BASE_KERNELS:
            for finding in self.claims(outputs, kernel):
                finding["status"] = status

    def test_one_dissenting_kernel_does_not_decide_the_claim(self):
        outputs = all_outputs()
        self.everyone_says_claim(outputs, "CONTRADICTED")
        last = list(base_only(outputs))[-1]
        for finding in self.claims(outputs, last):
            finding["status"] = "SUPPORTED"  # the last kernel dissents, which used to win
        packet = apply_policy(self.case, self.policy, outputs)
        self.assertEqual(packet["provisional_claim_statuses"]["C1"], "INSUFFICIENT_EVIDENCE")
        entry = packet["claim_summary"]["C1"]
        self.assertTrue(entry["disagreement"])
        self.assertEqual(entry["assessed_by"][last], "SUPPORTED")

    def test_agreeing_kernels_keep_their_status(self):
        outputs = all_outputs()
        self.everyone_says_claim(outputs, "CONTRADICTED")
        packet = apply_policy(self.case, self.policy, outputs)
        self.assertEqual(packet["provisional_claim_statuses"]["C1"], "CONTRADICTED")
        self.assertFalse(packet["claim_summary"]["C1"]["disagreement"])

    def test_the_order_the_kernels_are_listed_in_changes_nothing(self):
        outputs = all_outputs()
        self.everyone_says_claim(outputs, "CONTRADICTED")
        for finding in self.claims(outputs, list(base_only(outputs))[0]):
            finding["status"] = "SUPPORTED"
        forward = apply_policy(self.case, self.policy, outputs)
        backward = apply_policy(self.case, self.policy, dict(reversed(list(outputs.items()))))
        self.assertEqual(forward["claim_summary"], backward["claim_summary"])
        self.assertEqual(forward["provisional_claim_statuses"], backward["provisional_claim_statuses"])

    def test_a_claim_nobody_assessed_is_insufficient_evidence(self):
        outputs = all_outputs()
        for kernel in BASE_KERNELS:
            outputs[kernel]["output"]["findings"] = [
                finding
                for finding in outputs[kernel]["output"]["findings"]
                if not (finding["finding_type"] == "CLAIM_ASSESSMENT" and finding["target_id"] == "C1")
            ]
        packet = apply_policy(self.case, self.policy, outputs)
        self.assertEqual(packet["provisional_claim_statuses"]["C1"], "INSUFFICIENT_EVIDENCE")
        self.assertEqual(packet["claim_summary"]["C1"]["assessed_by"], {})

    def test_legacy_mode_reproduces_the_old_last_kernel_wins_packet(self):
        outputs = all_outputs()
        self.everyone_says_claim(outputs, "CONTRADICTED")
        last = list(base_only(outputs))[-1]
        for finding in self.claims(outputs, last):
            finding["status"] = "SUPPORTED"
        packet = apply_policy(self.case, self.policy, outputs, legacy_claim_statuses=True)
        self.assertEqual(packet["provisional_claim_statuses"]["C1"], "SUPPORTED")
        self.assertNotIn("claim_summary", packet)


if __name__ == "__main__":
    unittest.main()
