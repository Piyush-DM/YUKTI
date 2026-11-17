"""Behaviour that only matters with a real provider behind the pipeline.

The offline suite uses FixtureClient, which hides several live-path defects: it
carries an ``outputs`` dict the pipeline used to probe, it never rate-limits,
and it returns instantly. FakeLiveClient below has none of those properties,
so these tests exercise the path a live run takes without spending a request.
"""

import json
import threading
import time
import unittest
from collections import Counter
from pathlib import Path
from unittest import mock

from daale.client import CompletionRecord, DaaleModelError, FixtureClient
from daale.execution_contract import (
    DegradationMode,
    FailureMode,
    classify_failure,
    worse_degradation,
)
from daale.pipeline import ADVERSARIAL_KERNEL, BASE_KERNELS, DaalePipeline
from daale.prompts import KERNEL_SYSTEM_PROMPTS, build_kernel_messages
from daale.validation import DaaleValidationError

ROOT = Path(__file__).resolve().parents[1]


def load_json(relative_path):
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


class FakeLiveClient:
    """Looks like a network client: no ``outputs``, no ``is_fixture``."""

    def __init__(self, fail=None, jitter=False):
        self.calls = Counter()
        self.fail = fail or {}
        self.jitter = jitter
        self._lock = threading.Lock()

    def complete_json(self, purpose, model, messages, schema):
        with self._lock:
            self.calls[purpose] += 1
        if self.jitter:
            # Later kernels answer first, so completion order is the reverse
            # of declaration order.
            time.sleep(0.05 * (len(BASE_KERNELS) - BASE_KERNELS.index(purpose.upper())
                               if purpose.upper() in BASE_KERNELS else 0))
        if purpose in self.fail:
            raise self.fail[purpose]
        output = load_json(f"fixtures/{purpose}_output.json")
        return CompletionRecord(
            purpose=purpose,
            output=output,
            requested_model=model,
            served_model=f"provider/{model}",
            request_id=f"req-{purpose}",
            usage={"total_tokens": 10},
        )


class LiveReadinessTests(unittest.TestCase):
    def setUp(self):
        self.case = load_json("cases/vendor_alpha.json")
        self.policy = load_json("policies/vendor_post_technical_dd_v0_1.json")
        sleeper = mock.patch("daale.pipeline.time.sleep")
        sleeper.start()
        self.addCleanup(sleeper.stop)

    def pipeline(self, client, models=None):
        return DaalePipeline(
            client=client,
            model_by_kernel={"default": "test/model"} if models is None else models,
        )

    # -- every kernel runs, once -------------------------------------------

    def test_each_kernel_is_called_exactly_once_and_adversary_runs(self):
        client = FakeLiveClient()
        self.pipeline(client).run(self.case, self.policy)
        self.assertEqual(
            set(client.calls), {k.lower() for k in BASE_KERNELS} | {"adversary"}
        )
        self.assertEqual(set(client.calls.values()), {1})

    def test_trace_records_the_adversary_call_and_integrity(self):
        result = self.pipeline(FakeLiveClient()).run(self.case, self.policy)
        self.assertIn("adversary", result.trace["model_calls"])
        self.assertEqual(
            result.trace["model_calls"]["adversary"]["served_model"],
            "provider/test/model",
        )
        self.assertEqual(result.decision_packet["execution_integrity"]["adversary"], "ran")
        steps = {s["step"]: s["status"] for s in result.trace["pipeline_steps"]}
        self.assertEqual(steps["r_fabric_adversarial"], "completed")

    # -- progress is visible -----------------------------------------------

    def test_progress_is_logged_per_kernel_with_tokens(self):
        with self.assertLogs("daale.pipeline", "INFO") as captured:
            self.pipeline(FakeLiveClient()).run(self.case, self.policy)
        text = "\n".join(captured.output)
        for kernel in BASE_KERNELS + [ADVERSARIAL_KERNEL]:
            self.assertIn(f"{kernel}: ok in", text)
        self.assertIn("total_tokens=10", text)

    def test_failures_and_the_status_code_are_logged(self):
        error = DaaleModelError("quota exceeded", status_code=429)
        client = FakeLiveClient(fail={"outsider": error})
        with self.assertLogs("daale.pipeline", "INFO") as captured:
            self.pipeline(client).run(self.case, self.policy)
        text = "\n".join(captured.output)
        self.assertIn("OUTSIDER: attempt 1 failed", text)
        self.assertIn("HTTP 429", text)
        self.assertIn("waiting", text)

    def test_logs_never_contain_the_prompt_or_case_text(self):
        with self.assertLogs("daale.pipeline", "DEBUG") as captured:
            self.pipeline(FakeLiveClient()).run(self.case, self.policy)
        text = "\n".join(captured.output)
        self.assertNotIn(self.case["evidence"][0]["text"], text)

    # -- outputs derived from the run, not constants -----------------------

    def test_adversarial_summary_comes_from_the_adversary(self):
        expected = load_json("fixtures/adversary_output.json")["summary"]
        result = self.pipeline(FakeLiveClient()).run(self.case, self.policy)
        self.assertTrue(expected)
        self.assertEqual(result.decision_packet["adversarial_summary"], expected)

    def test_decision_does_not_depend_on_completion_order(self):
        steady = self.pipeline(FakeLiveClient()).run(self.case, self.policy)
        shuffled = self.pipeline(FakeLiveClient(jitter=True)).run(self.case, self.policy)
        keys = ("policy_state", "triggered_rule", "metrics",
                "requirement_summary", "provisional_claim_statuses")
        for key in keys:
            self.assertEqual(steady.decision_packet[key], shuffled.decision_packet[key], key)

    def test_offline_skip_is_reported_as_skipped_not_clean(self):
        fixtures = {
            k.lower(): load_json(f"fixtures/{k.lower()}_output.json") for k in BASE_KERNELS
        }
        result = self.pipeline(FixtureClient(fixtures)).run(self.case, self.policy)
        self.assertEqual(
            result.decision_packet["execution_integrity"]["adversary"],
            "skipped-no-fixture",
        )
        self.assertNotIn("adversary", result.trace["model_calls"])

    # -- failures are reported, not papered over ---------------------------

    def test_adversary_failure_is_refused_not_passed_as_unchallenged(self):
        client = FakeLiveClient(fail={"adversary": DaaleModelError("boom")})
        result = self.pipeline(client).run(self.case, self.policy)
        packet = result.decision_packet
        self.assertEqual(packet["policy_state"], "ESCALATE")
        self.assertEqual(packet["triggered_rule"]["rule_id"], "DEGRADED-EXECUTION")
        self.assertEqual(packet["execution_integrity"]["adversary"], "failed")
        self.assertIn(ADVERSARIAL_KERNEL, result.trace["execution_state"]["failed_kernels"])

    def test_one_failed_base_kernel_degrades_and_is_named(self):
        client = FakeLiveClient(fail={"outsider": DaaleModelError("boom")})
        result = self.pipeline(client).run(self.case, self.policy)
        integrity = result.decision_packet["execution_integrity"]
        self.assertEqual(integrity["base_kernels_failed"], ["OUTSIDER"])
        self.assertEqual(integrity["degradation_mode"], "degrade")
        self.assertNotIn("outsider", result.trace["model_calls"])

    def test_invalid_model_output_retries_then_degrades_instead_of_raising(self):
        bad = {k.lower(): {"case_id": "wrong"} for k in BASE_KERNELS}
        client = FixtureClient({**bad, "adversary": load_json("fixtures/adversary_output.json")})
        result = self.pipeline(client).run(self.case, self.policy)
        self.assertEqual(result.decision_packet["policy_state"], "ESCALATE")
        self.assertEqual(
            len(result.trace["execution_state"]["failed_kernels"]), len(BASE_KERNELS)
        )

    # -- retries are worth their requests -----------------------------------

    def test_a_rejected_reply_is_sent_back_with_the_reason_on_retry(self):
        seen = {}

        class RejectsOnce(FakeLiveClient):
            def complete_json(client, purpose, model, messages, schema):
                record = super().complete_json(purpose, model, messages, schema)
                if purpose == "analyst":
                    seen.setdefault("analyst", []).append(messages)
                    if client.calls["analyst"] == 1:
                        record.output["case_id"] = "WRONG-CASE"
                return record

        client = RejectsOnce()
        result = self.pipeline(client).run(self.case, self.policy)
        self.assertEqual(client.calls["analyst"], 2)
        retry_messages = seen["analyst"][1]
        self.assertEqual([m["role"] for m in retry_messages], ["system", "user", "assistant", "user"])
        self.assertIn("rejected by validation", retry_messages[-1]["content"])
        self.assertIn("case_id mismatch", retry_messages[-1]["content"])
        self.assertIn("WRONG-CASE", retry_messages[2]["content"])
        self.assertEqual(result.decision_packet["execution_integrity"]["base_kernels_failed"], [])

    def test_a_truncated_reply_is_retried_once_not_repeatedly(self):
        error = DaaleModelError("cut off at the completion token limit")
        error.truncated = True
        self.assertEqual(classify_failure(error), FailureMode.OUTPUT_TRUNCATED)
        client = FakeLiveClient(fail={"contrarian": error})
        with mock.patch("daale.pipeline.time.sleep") as sleep:
            result = self.pipeline(client).run(self.case, self.policy)
        # Retried once, with a nudge to answer directly (see test_resilience.py); not six times.
        self.assertEqual(client.calls["contrarian"], 2)
        self.assertEqual(
            result.decision_packet["execution_integrity"]["base_kernels_failed"], ["CONTRARIAN"]
        )

    # -- configuration and classification ----------------------------------

    def test_no_model_configured_fails_before_any_call(self):
        client = FakeLiveClient()
        with self.assertRaises(DaaleValidationError):
            self.pipeline(client, models={}).run(self.case, self.policy)
        self.assertEqual(sum(client.calls.values()), 0)

    def test_blank_model_is_not_accepted(self):
        with self.assertRaises(DaaleValidationError):
            self.pipeline(FakeLiveClient(), models={"default": "  "}).run(
                self.case, self.policy
            )

    def test_rate_limit_is_classified_by_status_not_message_text(self):
        error = DaaleModelError("OpenRouter error after 3 attempts", status_code=429)
        self.assertEqual(classify_failure(error), FailureMode.PROVIDER_RATE_LIMIT)
        server = DaaleModelError("upstream", status_code=503)
        self.assertEqual(classify_failure(server), FailureMode.TRANSIENT_PROVIDER_ERROR)

    def test_degradation_severity_is_ordered_by_severity_not_alphabet(self):
        self.assertEqual(
            worse_degradation(DegradationMode.RETRY, DegradationMode.ABORT),
            DegradationMode.ABORT,
        )
        self.assertEqual(
            worse_degradation(DegradationMode.DEGRADE, DegradationMode.ESCALATE),
            DegradationMode.ESCALATE,
        )

    # -- prompts ------------------------------------------------------------

    def test_adversary_prompt_does_not_demand_what_its_validator_rejects(self):
        self.assertNotIn("MUST produce an EVIDENCE_RELATION", KERNEL_SYSTEM_PROMPTS["ADVERSARY"])

    def test_kernel_prompt_states_this_cases_real_matrix_size(self):
        messages = build_kernel_messages("ANALYST", self.case, self.policy, None, False)
        expected = len(self.case["claims"]) * len(self.case["evidence"])
        self.assertIn(f"exactly {expected} EVIDENCE_RELATION", messages[1]["content"])
        for claim in self.case["claims"]:
            self.assertIn(claim["claim_id"], messages[1]["content"])


if __name__ == "__main__":
    unittest.main()
