"""A HIGH contradiction counts only when it quotes two cited evidence items verbatim (policy field
``contradiction_grounding: quoted``). Added 2026-11-17."""

import copy
import json
import unittest
from pathlib import Path

from daale.pipeline import BASE_KERNELS
from daale.policy_engine import apply_policy, contradiction_is_grounded
from daale.schemas import KERNEL_OUTPUT_SCHEMA
from daale.validation import validate_case_and_policy, validate_schema

ROOT = Path(__file__).resolve().parents[1]


def load(relative_path):
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


TEXT = {
    "E1": "Reported net debt to EBITDA was 1.2 times, down from 1.9 times a year earlier.",
    "E2": "The company has issued corporate guarantees of 24.0 billion rupees for an unconsolidated joint venture.",
    "E3": "Capital expenditure in FY26 was 3,100 million rupees.",
}


def candidate(quotes, evidence_ids=("E1", "E2")):
    return {"contradiction_id": "X", "evidence_ids": list(evidence_ids), "quotes": quotes}


class GroundingTests(unittest.TestCase):
    def test_two_verbatim_quotes_ground_a_contradiction(self):
        c = candidate([{"evidence_id": "E1", "quote": "net debt to EBITDA was 1.2 times"},
                       {"evidence_id": "E2", "quote": "guarantees of 24.0 billion rupees"}])
        self.assertTrue(contradiction_is_grounded(c, TEXT))

    def test_case_spacing_and_curly_quotes_are_ignored(self):
        c = candidate([{"evidence_id": "E1", "quote": "NET  DEBT to EBITDA\nwas 1.2 times"},
                       {"evidence_id": "E2", "quote": "corporate guarantees of 24.0 billion rupees"}])
        self.assertTrue(contradiction_is_grounded(c, TEXT))

    def test_an_ellipsis_joins_fragments_each_of_which_must_be_present(self):
        good = candidate([{"evidence_id": "E1", "quote": "Reported net debt ... down from 1.9 times"},
                          {"evidence_id": "E2", "quote": "guarantees of 24.0 billion rupees"}])
        bad = candidate([{"evidence_id": "E1", "quote": "Reported net debt ... up from 1.9 times"},
                         {"evidence_id": "E2", "quote": "guarantees of 24.0 billion rupees"}])
        self.assertTrue(contradiction_is_grounded(good, TEXT))
        self.assertFalse(contradiction_is_grounded(bad, TEXT))

    def test_a_paraphrase_is_not_grounded(self):
        c = candidate([{"evidence_id": "E1", "quote": "leverage looks low at one point two"},
                       {"evidence_id": "E2", "quote": "guarantees of 24.0 billion rupees"}])
        self.assertFalse(contradiction_is_grounded(c, TEXT))

    def test_one_quote_is_not_enough(self):
        c = candidate([{"evidence_id": "E1", "quote": "net debt to EBITDA was 1.2 times"}])
        self.assertFalse(contradiction_is_grounded(c, TEXT))

    def test_two_quotes_from_the_same_item_are_not_enough(self):
        c = candidate([{"evidence_id": "E1", "quote": "net debt to EBITDA was 1.2 times"},
                       {"evidence_id": "E1", "quote": "down from 1.9 times a year earlier"}])
        self.assertFalse(contradiction_is_grounded(c, TEXT))

    def test_a_quote_from_an_item_the_finding_does_not_cite_does_not_count(self):
        c = candidate([{"evidence_id": "E1", "quote": "net debt to EBITDA was 1.2 times"},
                       {"evidence_id": "E3", "quote": "Capital expenditure in FY26"}])
        self.assertFalse(contradiction_is_grounded(c, TEXT))

    def test_a_very_short_quote_does_not_count(self):
        c = candidate([{"evidence_id": "E1", "quote": "1.2 times"},
                       {"evidence_id": "E2", "quote": "guarantees of 24.0 billion rupees"}])
        self.assertFalse(contradiction_is_grounded(c, TEXT))

    def test_no_quotes_at_all_is_not_grounded(self):
        self.assertFalse(contradiction_is_grounded(candidate([]), TEXT))


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.case = load("cases/vendor_alpha.json")
        self.policy = load("policies/vendor_post_technical_dd_v0_1.json")
        self.outputs = {k: {"output": load(f"fixtures/{k.lower()}_output.json")} for k in BASE_KERNELS}
        self.outputs["ADVERSARY"] = {"output": load("fixtures/adversary_output.json")}
        self.outputs["ADVERSARY"]["output"]["findings"] = []
        ev = {item["evidence_id"]: item["text"] for item in self.case["evidence"]}
        self.ids = list(ev)[:2]
        self.words = [ev[i][:40] for i in self.ids]

    def contradiction(self, quotes):
        return {"finding_id": "ADV-1", "finding_type": "CONTRADICTION", "target_type": "CLAIM",
                "target_id": "C1", "evidence_ids": self.ids, "content": "x", "severity": "HIGH",
                "confidence": 0.9, **({"quotes": quotes} if quotes is not None else {})}

    def grounded_quotes(self):
        return [{"evidence_id": i, "quote": w} for i, w in zip(self.ids, self.words)]

    def quoted_policy(self):
        policy = copy.deepcopy(self.policy)
        policy["contradiction_grounding"] = "quoted"
        return policy

    def run_policy(self, policy, quotes):
        self.outputs["ADVERSARY"]["output"]["findings"] = [self.contradiction(quotes)]
        return apply_policy(self.case, policy, self.outputs)["metrics"]

    def test_by_default_an_unquoted_high_contradiction_still_counts_and_no_new_metric_appears(self):
        metrics = self.run_policy(self.policy, None)
        self.assertEqual(metrics["high_unresolved_contradictions"], 1)
        self.assertNotIn("ungrounded_high_contradictions", metrics)

    def test_under_quoted_grounding_an_unquoted_one_is_set_aside_and_recorded(self):
        metrics = self.run_policy(self.quoted_policy(), None)
        self.assertEqual(metrics["high_unresolved_contradictions"], 0)
        self.assertEqual(metrics["ungrounded_high_contradictions"], 1)
        self.assertEqual(metrics["details"]["ungrounded_contradiction_ids"], ["ADV-1"])

    def test_under_quoted_grounding_a_quoted_one_counts(self):
        metrics = self.run_policy(self.quoted_policy(), self.grounded_quotes())
        self.assertEqual(metrics["high_unresolved_contradictions"], 1)
        self.assertEqual(metrics["ungrounded_high_contradictions"], 0)

    def test_the_field_validates_and_an_unknown_value_is_refused(self):
        validate_case_and_policy(self.case, self.quoted_policy())
        bad = copy.deepcopy(self.policy)
        bad["contradiction_grounding"] = "trust-me"
        with self.assertRaises(Exception):
            validate_case_and_policy(self.case, bad)

    def test_a_finding_with_quotes_passes_the_kernel_output_schema(self):
        output = copy.deepcopy(load("fixtures/adversary_output.json"))
        output["findings"] = [self.contradiction(self.grounded_quotes())]
        validate_schema(output, KERNEL_OUTPUT_SCHEMA, "adversary output")

    def test_the_shipped_v0_4_policy_validates(self):
        validate_case_and_policy(load("cases/inv_stress_1.json"), load("policies/investment_quality_screen_v0_4.json"))


if __name__ == "__main__":
    unittest.main()
