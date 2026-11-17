"""Resuming an incomplete run: only what failed runs again, and nothing is trusted blindly."""

import copy
import json
import threading
import unittest
from collections import Counter
from pathlib import Path
from unittest import mock

from daale.budget import BudgetExhausted
from daale.client import CompletionRecord, DaaleModelError
from daale.pipeline import BASE_KERNELS, DaalePipeline, ResumeError, budget_shortfall
from daale.replay import compare
from daale.trace import hash_value

ROOT = Path(__file__).resolve().parents[1]


def load_json(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class Client:
    """Answers from the fixtures; can be told to fail some kernels; counts calls per kernel."""

    def __init__(self, fail=(), remaining=None):
        self.calls = Counter()
        self.fail = set(fail)
        self.remaining = remaining
        self._lock = threading.Lock()

    def requests_remaining(self, model=None):
        return self.remaining

    def complete_json(self, purpose, model, messages, schema):
        with self._lock:
            self.calls[purpose] += 1
        if purpose in self.fail:
            raise DaaleModelError("provider unavailable", status_code=400)
        return CompletionRecord(
            purpose, load_json(f"fixtures/{purpose}_output.json"), model, f"served/{model}",
            f"req-{purpose}-{self.calls[purpose]}", {"total_tokens": 100},
        )


class ResumeTests(unittest.TestCase):
    def setUp(self):
        self.case = load_json("cases/vendor_alpha.json")
        self.policy = load_json("policies/vendor_post_technical_dd_v0_1.json")
        patcher = mock.patch("daale.pipeline.time.sleep")
        patcher.start()
        self.addCleanup(patcher.stop)
        # An incomplete run: OUTSIDER fails, so the run is incomplete.
        self.first_client = Client(fail={"outsider"})
        self.first = self.pipeline(self.first_client).run(self.case, self.policy)

    def pipeline(self, client, models=None):
        return DaalePipeline(client=client, model_by_kernel=models or {"default": "m"})

    def test_the_starting_point_is_an_incomplete_run(self):
        self.assertEqual(self.first.trace["execution_state"]["failed_kernels"], ["OUTSIDER"])
        self.assertTrue(self.first.decision_packet["execution_integrity"]["requires_human_review"])

    def test_only_the_failed_kernel_and_the_adversary_run_again(self):
        client = Client()
        result = self.pipeline(client).resume(self.first.trace)
        self.assertEqual(dict(client.calls), {"outsider": 1, "adversary": 1})
        integrity = result.decision_packet["execution_integrity"]
        self.assertEqual(integrity["base_kernels_failed"], [])
        self.assertEqual(integrity["adversary"], "ran")

    def test_the_resumed_decision_equals_a_full_run(self):
        resumed = self.pipeline(Client()).resume(self.first.trace)
        full = self.pipeline(Client()).run(self.case, self.policy)
        for key in ("policy_state", "triggered_rule", "metrics", "requirement_summary",
                    "provisional_claim_statuses"):
            self.assertEqual(resumed.decision_packet[key], full.decision_packet[key], key)
        self.assertFalse(resumed.decision_packet["execution_integrity"]["requires_human_review"])

    def test_the_new_trace_says_what_it_continues_and_what_it_reused(self):
        result = self.pipeline(Client()).resume(self.first.trace)
        resumed = result.trace["resumed_from"]
        self.assertEqual(resumed["run_id"], self.first.trace["run"]["run_id"])
        self.assertEqual(resumed["rerun_kernels"], ["OUTSIDER", "ADVERSARY"])
        self.assertEqual(set(resumed["reused_kernels"]), set(BASE_KERNELS) - {"OUTSIDER"})
        self.assertEqual(resumed["prior_decision"]["rule_id"], "DEGRADED-EXECUTION"
                         if self.first.decision_packet["triggered_rule"]["rule_id"] == "DEGRADED-EXECUTION"
                         else self.first.decision_packet["triggered_rule"]["rule_id"])
        calls = result.trace["model_calls"]
        self.assertIn("reused_from_run", calls["analyst"])
        self.assertNotIn("reused_from_run", calls["outsider"])
        self.assertNotIn("reused_from_run", calls["adversary"])
        events = [e["event_type"] for e in result.trace["execution_state"]["audit_events"]]
        self.assertEqual(events.count("kernel-reused"), 5)
        self.assertIn("kernel-failed", events)  # the earlier failures stay in the record

    def test_reused_outputs_are_exactly_what_was_recorded(self):
        result = self.pipeline(Client()).resume(self.first.trace)
        for kernel in set(BASE_KERNELS) - {"OUTSIDER"}:
            key = kernel.lower()
            self.assertEqual(
                result.trace["provisional_findings"][key], self.first.trace["provisional_findings"][key]
            )
            self.assertEqual(
                result.trace["hashes"][f"{key}_output_sha256"],
                self.first.trace["hashes"][f"{key}_output_sha256"],
            )

    def test_a_resumed_trace_replays_to_the_same_decision(self):
        result = self.pipeline(Client()).resume(self.first.trace)
        same, differences = compare(result.trace)
        self.assertTrue(same, differences)

    def test_a_failed_adversary_alone_is_resumed_without_rerunning_any_kernel(self):
        client = Client(fail={"adversary"})
        first = self.pipeline(client).run(self.case, self.policy)
        self.assertEqual(first.trace["execution_state"]["failed_kernels"], ["ADVERSARY"])
        second_client = Client()
        result = self.pipeline(second_client).resume(first.trace)
        self.assertEqual(dict(second_client.calls), {"adversary": 1})
        self.assertEqual(result.decision_packet["policy_state"], "REJECT")

    def test_a_run_that_is_already_complete_is_refused(self):
        complete = self.pipeline(Client()).run(self.case, self.policy)
        with self.assertRaisesRegex(ResumeError, "Nothing to resume"):
            self.pipeline(Client()).resume(complete.trace)

    # -- nothing is trusted blindly ------------------------------------------

    def test_a_tampered_kernel_output_is_refused_before_any_request(self):
        trace = copy.deepcopy(self.first.trace)
        trace["provisional_findings"]["analyst"]["summary"] = "edited after the fact"
        client = Client()
        with self.assertRaisesRegex(ResumeError, "altered"):
            self.pipeline(client).resume(trace)
        self.assertEqual(sum(client.calls.values()), 0)

    def test_a_tampered_case_is_refused_before_any_request(self):
        trace = copy.deepcopy(self.first.trace)
        trace["case"]["evidence"][0]["text"] = "something else entirely"
        client = Client()
        with self.assertRaisesRegex(ResumeError, "altered"):
            self.pipeline(client).resume(trace)
        self.assertEqual(sum(client.calls.values()), 0)

    def test_a_tampered_decision_is_refused(self):
        trace = copy.deepcopy(self.first.trace)
        trace["decision_packet"]["policy_state"] = "ADVANCE"
        with self.assertRaisesRegex(ResumeError, "altered"):
            self.pipeline(Client()).resume(trace)

    def test_a_recorded_output_that_no_longer_validates_is_run_again_not_reused(self):
        trace = copy.deepcopy(self.first.trace)
        bad = trace["provisional_findings"]["analyst"]
        bad["case_id"] = "OTHER"
        trace["hashes"]["analyst_output_sha256"] = hash_value(bad)  # hash agrees; validation does not
        trace["hashes"]["decision_packet_sha256"] = hash_value(trace["decision_packet"])
        client = Client()
        result = self.pipeline(client).resume(trace)
        self.assertEqual(client.calls["analyst"], 1)
        self.assertNotIn("ANALYST", result.trace["resumed_from"]["reused_kernels"])

    # -- the budget -----------------------------------------------------------

    def test_resume_checks_the_budget_for_only_what_it_will_send(self):
        # Two requests left: enough for OUTSIDER plus the adversary, far short of a full run.
        client = Client(remaining=2)
        self.assertIsNone(budget_shortfall(client, {"default": "m"}, kernels=["OUTSIDER", "ADVERSARY"]))
        self.assertIsNotNone(budget_shortfall(client, {"default": "m"}))
        result = self.pipeline(client).resume(self.first.trace)
        self.assertEqual(dict(client.calls), {"outsider": 1, "adversary": 1})
        self.assertTrue(result.decision_packet)

    def test_resume_refuses_when_even_that_is_too_much(self):
        client = Client(remaining=1)
        with self.assertRaisesRegex(BudgetExhausted, "Nothing was sent"):
            self.pipeline(client).resume(self.first.trace)
        self.assertEqual(sum(client.calls.values()), 0)

    def test_a_resume_that_fails_again_stays_incomplete(self):
        client = Client(fail={"outsider"})
        result = self.pipeline(client).resume(self.first.trace)
        self.assertEqual(result.decision_packet["execution_integrity"]["base_kernels_failed"], ["OUTSIDER"])
        self.assertNotEqual(result.decision_packet["policy_state"], "ADVANCE")
        self.assertTrue(result.decision_packet["execution_integrity"]["requires_human_review"])


if __name__ == "__main__":
    unittest.main()
