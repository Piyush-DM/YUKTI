"""What an incomplete or contested run may conclude (decided 2026-11-09).

  * any failed kernel makes the run incomplete, and an incomplete run always needs human review;
  * an incomplete run never emits ADVANCE, but may still REJECT or HOLD;
  * a mandatory or critical requirement the kernels disagree on needs human review;
  * a clean run reports degradation mode "none", not "retry".
"""

import json
import unittest
from pathlib import Path
from unittest import mock

from daale.client import CompletionRecord, DaaleModelError
from daale.pipeline import DaalePipeline

ROOT = Path(__file__).resolve().parents[1]


def load(relative_path):
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


class StubClient:
    """Looks like a live client and answers from the fixtures, optionally rewritten or failing."""

    def __init__(self, rewrite=None, fail=None):
        self.rewrite = rewrite or (lambda purpose, output: output)
        self.fail = fail or {}

    def complete_json(self, purpose, model, messages, schema):
        if purpose in self.fail:
            raise self.fail[purpose]
        output = self.rewrite(purpose, load(f"fixtures/{purpose}_output.json"))
        return CompletionRecord(
            purpose=purpose,
            output=output,
            requested_model=model,
            served_model=model,
            request_id=f"req-{purpose}",
            usage={"total_tokens": 10},
        )


def approve_everything(purpose, output):
    """Every assessing kernel says SATISFIED and the adversary finds nothing: the policy ADVANCEs."""
    if purpose == "adversary":
        output["findings"] = []
        return output
    for finding in output["findings"]:
        if finding["finding_type"] == "REQUIREMENT_ASSESSMENT":
            finding["status"] = "SATISFIED"
    return output


class IntegrityRuleTests(unittest.TestCase):
    def setUp(self):
        self.case = load("cases/vendor_alpha.json")
        self.policy = load("policies/vendor_post_technical_dd_v0_1.json")
        sleeper = mock.patch("daale.pipeline.time.sleep")
        sleeper.start()
        self.addCleanup(sleeper.stop)

    def run_pipeline(self, **client_args):
        pipeline = DaalePipeline(client=StubClient(**client_args), model_by_kernel={"default": "test/model"})
        return pipeline.run(self.case, self.policy)

    def test_a_clean_run_reports_no_degradation_and_needs_no_extra_review(self):
        integrity = self.run_pipeline().decision_packet["execution_integrity"]
        self.assertEqual(integrity["degradation_mode"], "none")
        self.assertFalse(integrity["requires_human_review"])
        self.assertEqual(integrity["human_review_reasons"], [])

    def test_any_failed_kernel_forces_human_review(self):
        result = self.run_pipeline(fail={"outsider": DaaleModelError("boom")})
        integrity = result.decision_packet["execution_integrity"]
        self.assertTrue(integrity["requires_human_review"])
        self.assertEqual(integrity["human_review_reasons"], ["kernels failed: OUTSIDER"])
        self.assertTrue(result.trace["execution_state"]["requires_human_review"])

    def test_an_incomplete_run_can_still_reject(self):
        result = self.run_pipeline(fail={"outsider": DaaleModelError("boom")})
        self.assertEqual(result.decision_packet["policy_state"], "REJECT")

    def test_an_incomplete_run_cannot_advance(self):
        control = self.run_pipeline(rewrite=approve_everything)
        self.assertEqual(control.decision_packet["policy_state"], "ADVANCE")
        self.assertFalse(control.decision_packet["execution_integrity"]["requires_human_review"])

        blocked = self.run_pipeline(rewrite=approve_everything, fail={"contrarian": DaaleModelError("boom")})
        packet = blocked.decision_packet
        self.assertEqual(packet["policy_state"], "ESCALATE")
        self.assertEqual(packet["triggered_rule"]["rule_id"], "INCOMPLETE-RUN-ADVANCE-BLOCKED")
        self.assertEqual(packet["policy_state_before_integrity_check"], "ADVANCE")
        self.assertIn("P050-ALL-MANDATORY-SATISFIED", packet["other_matching_rule_ids"])
        reasons = packet["execution_integrity"]["human_review_reasons"]
        self.assertIn("kernels failed: CONTRARIAN", reasons)
        self.assertIn("ADVANCE blocked because the run is incomplete", reasons)

    def test_a_contested_mandatory_requirement_holds_and_needs_review(self):
        def one_dissenter(purpose, output):
            output = approve_everything(purpose, output)
            if purpose == "historian":
                for finding in output["findings"]:
                    if finding["finding_type"] == "REQUIREMENT_ASSESSMENT" and finding["target_id"] == "R3":
                        finding["status"] = "NOT_SATISFIED"
            return output

        result = self.run_pipeline(rewrite=one_dissenter)
        packet = result.decision_packet
        self.assertEqual(packet["policy_state"], "HOLD")
        integrity = packet["execution_integrity"]
        self.assertTrue(integrity["requires_human_review"])
        self.assertEqual(integrity["human_review_reasons"], ["kernels disagree on R3"])
        gaps = result.trace["gap_report"]
        self.assertIn(
            ("requirement_kernels_disagree", "R3"),
            [(w["type"], w["requirement_id"]) for w in gaps["validation_warnings"]],
        )
        self.assertEqual(gaps["summary"]["total_requirement_disagreements"], 1)

    def test_a_requirement_no_kernel_assessed_is_flagged_in_the_gap_report(self):
        def forget_r4(purpose, output):
            output["findings"] = [
                finding
                for finding in output["findings"]
                if not (finding["finding_type"] == "REQUIREMENT_ASSESSMENT" and finding["target_id"] == "R4")
            ]
            return output

        gaps = self.run_pipeline(rewrite=forget_r4).trace["gap_report"]
        self.assertEqual([g["requirement_id"] for g in gaps["unassessed_requirements"]], ["R4"])
        self.assertIn("requirement_not_assessed", [w["type"] for w in gaps["validation_warnings"]])

    def test_a_refused_run_says_why_it_needs_a_human(self):
        result = self.run_pipeline(fail={"adversary": DaaleModelError("boom")})
        integrity = result.decision_packet["execution_integrity"]
        self.assertTrue(integrity["requires_human_review"])
        self.assertEqual(
            integrity["human_review_reasons"],
            ["pipeline degraded: adversary-failed", "kernels failed: ADVERSARY"],
        )


if __name__ == "__main__":
    unittest.main()
