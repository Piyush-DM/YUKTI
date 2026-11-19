"""Which provider failures retry, which fall back, and which do neither (added 2026-11-17).

Background: a live run got HTTP 404 "no longer available to new users" from the provider. It was filed under
kernel-crash, retried on the same model and never sent to the configured fallback. No model is called here.
"""

import json
import threading
import unittest
from pathlib import Path
from unittest import mock

from daale.client import CompletionRecord, DaaleModelError
from daale.execution_contract import (
    FAILURE_RULES,
    FailureMode,
    KernelRole,
    classify_failure,
    get_failure_rule,
)
from daale.pipeline import DaalePipeline

ROOT = Path(__file__).resolve().parents[1]
PRIMARY, BACKUP = "primary-model", "backup-model"


def load_json(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def failure(status, text="provider said no"):
    return DaaleModelError(f"OpenAI-compatible endpoint error {status} after 1 attempt(s): {text}", status_code=status)


class MatrixTests(unittest.TestCase):
    """The classification matrix, status by status."""

    def test_the_matrix(self):
        expected = {
            400: FailureMode.REQUEST_REJECTED,
            401: FailureMode.AUTHENTICATION_FAILED,
            403: FailureMode.AUTHENTICATION_FAILED,
            404: FailureMode.MODEL_NOT_AVAILABLE,
            408: FailureMode.MODEL_TIMEOUT,
            410: FailureMode.MODEL_NOT_AVAILABLE,
            413: FailureMode.REQUEST_REJECTED,
            422: FailureMode.REQUEST_REJECTED,
            429: FailureMode.PROVIDER_RATE_LIMIT,
            500: FailureMode.MODEL_UNAVAILABLE,
            501: FailureMode.MODEL_UNAVAILABLE,
            502: FailureMode.TRANSIENT_PROVIDER_ERROR,
            503: FailureMode.TRANSIENT_PROVIDER_ERROR,
            504: FailureMode.TRANSIENT_PROVIDER_ERROR,
        }
        for status, mode in expected.items():
            with self.subTest(status=status):
                self.assertIs(classify_failure(failure(status)), mode)

    def test_a_4xx_that_is_not_listed_keeps_its_old_classification(self):
        # "Do not classify every 4xx as a permanent model failure": 418 and 409 are not claimed.
        for status in (409, 418, 451):
            with self.subTest(status=status):
                self.assertIs(classify_failure(failure(status)), FailureMode.KERNEL_CRASH)

    def test_a_429_that_names_a_per_day_quota_is_not_retried_like_a_per_minute_one(self):
        daily = failure(429, 'quotaId: "GenerateRequestsPerDayPerProjectPerModel-FreeTier"')
        self.assertIs(classify_failure(daily), FailureMode.QUOTA_EXHAUSTED)
        per_minute = failure(429, 'quotaId: "GenerateRequestsPerMinutePerProjectPerModel-FreeTier"')
        self.assertIs(classify_failure(per_minute), FailureMode.PROVIDER_RATE_LIMIT)

    def test_failures_without_a_status_are_classified_as_before(self):
        self.assertIs(classify_failure(RuntimeError("boom")), FailureMode.KERNEL_CRASH)
        self.assertIs(classify_failure(DaaleModelError("Read timed out. (read timeout=500)")), FailureMode.MODEL_TIMEOUT)
        truncated = DaaleModelError("cut off")
        truncated.truncated = True
        self.assertIs(classify_failure(truncated), FailureMode.OUTPUT_TRUNCATED)

    def test_the_new_modes_are_single_attempt_and_tell_a_human(self):
        for mode in (FailureMode.MODEL_NOT_AVAILABLE, FailureMode.AUTHENTICATION_FAILED, FailureMode.REQUEST_REJECTED):
            for role in (KernelRole.BASE, KernelRole.ADVERSARY):
                with self.subTest(mode=mode, role=role):
                    rule = get_failure_rule(mode, role)
                    self.assertIsNotNone(rule)
                    self.assertIsNone(rule.retry_policy)
                    self.assertTrue(rule.requires_human_review)

    def test_every_failure_mode_a_status_can_produce_has_a_rule(self):
        ruled = {rule.failure_mode for rule in FAILURE_RULES}
        for status in (400, 401, 403, 404, 408, 410, 413, 422, 429, 500, 502, 503, 504):
            mode = classify_failure(failure(status))
            with self.subTest(status=status):
                self.assertIn(mode, ruled)


class ModelClient:
    """Serves the fixtures; ``behaviour[(purpose, model)](call_number)`` may return an exception to raise."""

    def __init__(self, behaviour=None):
        self.calls = []
        self.behaviour = behaviour or {}
        self._lock = threading.Lock()

    def complete_json(self, purpose, model, messages, schema):
        with self._lock:
            self.calls.append((purpose, model))
            number = sum(1 for p, m in self.calls if (p, m) == (purpose, model))
        action = self.behaviour.get((purpose, model))
        error = action(number) if action else None
        if error:
            raise error
        return CompletionRecord(
            purpose, load_json(f"fixtures/{purpose}_output.json"), model, f"served/{model}", f"req-{number}", {"total_tokens": 10}
        )

    def count(self, purpose, model):
        return sum(1 for p, m in self.calls if (p, m) == (purpose, model))


class PipelineBehaviourTests(unittest.TestCase):
    def setUp(self):
        self.case = load_json("cases/vendor_alpha.json")
        self.policy = load_json("policies/vendor_post_technical_dd_v0_1.json")
        patcher = mock.patch("daale.pipeline.time.sleep")
        patcher.start()
        self.addCleanup(patcher.stop)

    def run_pipeline(self, client, fallback=BACKUP):
        return DaalePipeline(
            client=client,
            model_by_kernel={"default": PRIMARY},
            fallback_by_kernel={"default": fallback} if fallback else None,
        ).run(self.case, self.policy)

    def integrity(self, result):
        return result.decision_packet["execution_integrity"]

    def events(self, result, kernel):
        return [e for e in result.trace["execution_state"]["audit_events"] if e["kernel_id"] == kernel]

    def test_a_missing_model_goes_straight_to_the_fallback_with_no_retry(self):
        client = ModelClient({("contrarian", PRIMARY): lambda n: failure(404, "no longer available to new users")})
        result = self.run_pipeline(client)
        self.assertEqual(client.count("contrarian", PRIMARY), 1)  # not retried on the dead model
        self.assertEqual(client.count("contrarian", BACKUP), 1)
        self.assertEqual(self.integrity(result)["base_kernels_failed"], [])
        self.assertEqual(
            self.integrity(result)["fallbacks_used"],
            [{"kernel": "CONTRARIAN", "from": PRIMARY, "to": BACKUP, "reason": "model-not-available"}],
        )

    def test_the_attempt_on_the_dead_model_is_recorded_with_its_model_and_mode(self):
        client = ModelClient({("contrarian", PRIMARY): lambda n: failure(404)})
        result = self.run_pipeline(client)
        failed = [e for e in self.events(result, "CONTRARIAN") if e["event_type"] == "kernel-failed"]
        self.assertEqual(len(failed), 1)
        self.assertEqual(failed[0]["metadata"]["failure_mode"], "model-not-available")
        self.assertEqual(failed[0]["metadata"]["model"], PRIMARY)

    def test_a_missing_fallback_too_fails_the_kernel_without_looping(self):
        client = ModelClient({("contrarian", PRIMARY): lambda n: failure(404), ("contrarian", BACKUP): lambda n: failure(404)})
        result = self.run_pipeline(client)
        self.assertEqual(client.count("contrarian", PRIMARY), 1)
        self.assertEqual(client.count("contrarian", BACKUP), 1)  # one try each, then it stops
        self.assertEqual(self.integrity(result)["base_kernels_failed"], ["CONTRARIAN"])
        self.assertTrue(self.integrity(result)["requires_human_review"])
        kinds = [e["event_type"] for e in self.events(result, "CONTRARIAN")]
        self.assertIn("kernel-fallback-failed", kinds)

    def test_an_authentication_failure_is_tried_once_and_never_sent_to_the_fallback(self):
        for status in (401, 403):
            with self.subTest(status=status):
                client = ModelClient({("contrarian", PRIMARY): lambda n, s=status: failure(s, "API key not valid")})
                result = self.run_pipeline(client)
                self.assertEqual(client.count("contrarian", PRIMARY), 1)
                self.assertEqual(client.count("contrarian", BACKUP), 0)  # same key: it would fail the same way
                self.assertEqual(self.integrity(result)["base_kernels_failed"], ["CONTRARIAN"])

    def test_a_rejected_request_is_not_retried_but_the_fallback_is_tried_once(self):
        client = ModelClient({("contrarian", PRIMARY): lambda n: failure(400, "max_tokens is too large")})
        result = self.run_pipeline(client)
        self.assertEqual(client.count("contrarian", PRIMARY), 1)
        self.assertEqual(client.count("contrarian", BACKUP), 1)
        self.assertEqual(self.integrity(result)["fallbacks_used"][0]["reason"], "request-rejected")

    def test_a_missing_model_with_no_fallback_is_one_attempt_not_two(self):
        client = ModelClient({("contrarian", PRIMARY): lambda n: failure(404)})
        result = self.run_pipeline(client, fallback=None)
        self.assertEqual(client.count("contrarian", PRIMARY), 1)  # was 2 when filed under kernel-crash
        self.assertEqual(self.integrity(result)["base_kernels_failed"], ["CONTRARIAN"])

    def test_a_503_still_retries_on_the_same_model_before_giving_up_to_the_fallback(self):
        client = ModelClient({("contrarian", PRIMARY): lambda n: failure(503, "high demand")})
        result = self.run_pipeline(client)
        self.assertEqual(client.count("contrarian", PRIMARY), 2)  # unchanged: a fallback is waiting, so two tries
        self.assertEqual(client.count("contrarian", BACKUP), 1)
        self.assertEqual(self.integrity(result)["base_kernels_failed"], [])

    def test_an_unlisted_4xx_keeps_its_old_behaviour_two_attempts_and_no_fallback(self):
        client = ModelClient({("contrarian", PRIMARY): lambda n: failure(418, "teapot")})
        self.run_pipeline(client)
        self.assertEqual(client.count("contrarian", PRIMARY), 2)
        self.assertEqual(client.count("contrarian", BACKUP), 0)

    def test_the_other_kernels_are_unaffected_when_one_model_is_missing(self):
        client = ModelClient({("analyst", PRIMARY): lambda n: failure(404)})
        result = self.run_pipeline(client)
        for kernel in ("contrarian", "first_principles", "expansionist", "outsider", "historian"):
            self.assertEqual(client.count(kernel, PRIMARY), 1)
            self.assertEqual(client.count(kernel, BACKUP), 0)
        self.assertEqual(self.integrity(result)["base_kernels_failed"], [])


if __name__ == "__main__":
    unittest.main()
