"""How long a model may take, and how HTTP retries are paced. Stubbed HTTP: no network, no key."""

import json
import unittest
from pathlib import Path
from unittest import mock

import requests

from daale.client import DaaleModelError, GenericApiClient
from daale.execution_contract import FailureMode, classify_failure
from daale.providers import build_live_client
from daale.schemas import KERNEL_OUTPUT_SCHEMA

ROOT = Path(__file__).resolve().parents[1]
GOOD = json.loads((ROOT / "fixtures/analyst_output.json").read_text(encoding="utf-8"))
LOCAL = {"DAALE_LIVE_PROVIDER": "generic", "LLM_BASE_URL": "http://127.0.0.1:1/v1"}


class FakeResponse:
    def __init__(self, body, status=200, headers=None):
        self._body = body
        self.status_code = status
        self.ok = status < 400
        self.headers = headers or {}
        self.text = json.dumps(body)

    def json(self):
        return self._body


def completion():
    return FakeResponse(
        {
            "id": "r",
            "model": "m",
            "choices": [{"message": {"content": json.dumps(GOOD)}}],
            "usage": {"total_tokens": 1},
        }
    )


def google_429(delay):
    """A 429 shaped like Google's: a list body whose RetryInfo carries the delay."""
    body = [{"error": {"code": 429, "status": "RESOURCE_EXHAUSTED", "details": [
        {"@type": "type.googleapis.com/google.rpc.RetryInfo", "retryDelay": delay}]}}]
    return FakeResponse(body, status=429)


class TimeoutTests(unittest.TestCase):
    def test_the_generic_provider_waits_up_to_500_seconds_for_a_reply(self):
        client, _ = build_live_client(dict(LOCAL))
        self.assertEqual(client.timeout_seconds, 500)

    def test_the_wait_can_still_be_set_in_the_environment(self):
        client, _ = build_live_client({**LOCAL, "LLM_TIMEOUT_SECONDS": "300"})
        self.assertEqual(client.timeout_seconds, 300)

    def test_a_reply_may_take_the_whole_timeout_but_connecting_fails_after_30_seconds(self):
        client = GenericApiClient(api_key="k", base_url="https://example.test/v1")
        with mock.patch("daale.client.requests.post", return_value=completion()) as post:
            client.complete_json("analyst", "m", [{"role": "user", "content": "x"}], KERNEL_OUTPUT_SCHEMA)
        self.assertEqual(post.call_args.kwargs["timeout"], (30, 500))


class RetryPacingTests(unittest.TestCase):
    def run_with(self, *responses):
        client = GenericApiClient(api_key="k", base_url="https://example.test/v1")
        with mock.patch("daale.client.requests.post", side_effect=list(responses)), \
                mock.patch("daale.client.time.sleep") as sleep:
            client.complete_json("analyst", "m", [{"role": "user", "content": "x"}], KERNEL_OUTPUT_SCHEMA)
        return sleep

    def test_a_429_waits_for_the_delay_google_asks_for(self):
        sleep = self.run_with(google_429("23s"), completion())
        sleep.assert_called_once_with(23.0)

    def test_a_fractional_delay_is_understood(self):
        sleep = self.run_with(google_429("7.5s"), completion())
        sleep.assert_called_once_with(7.5)

    def test_a_retry_after_header_is_honoured_too(self):
        throttled = FakeResponse({"error": {"message": "slow down"}}, status=429, headers={"Retry-After": "12"})
        sleep = self.run_with(throttled, completion())
        sleep.assert_called_once_with(12.0)

    def test_a_very_long_delay_is_capped_so_a_run_cannot_hang_on_it(self):
        sleep = self.run_with(google_429("3600s"), completion())
        sleep.assert_called_once_with(65)

    def test_without_a_hint_the_short_backoff_is_unchanged(self):
        sleep = self.run_with(FakeResponse({"error": {"message": "overloaded"}}, status=503), completion())
        sleep.assert_called_once_with(2)


class TimeoutRetryTests(unittest.TestCase):
    """A full read timeout is not repeated at the HTTP layer; the kernel-level policy owns that."""

    def call(self, side_effect):
        client = GenericApiClient(api_key="k", base_url="https://example.test/v1")
        with mock.patch("daale.client.requests.post", side_effect=side_effect) as post, \
                mock.patch("daale.client.time.sleep") as sleep:
            try:
                client.complete_json("analyst", "m", [{"role": "user", "content": "x"}], KERNEL_OUTPUT_SCHEMA)
                raised = None
            except DaaleModelError as error:
                raised = error
        return post, sleep, raised

    def test_a_read_timeout_is_not_retried_at_the_http_layer(self):
        timeout = requests.exceptions.ReadTimeout(
            "HTTPSConnectionPool(host='x', port=443): Read timed out. (read timeout=500)"
        )
        post, sleep, raised = self.call(timeout)
        self.assertEqual(post.call_count, 1)
        sleep.assert_not_called()
        self.assertIs(classify_failure(raised), FailureMode.MODEL_TIMEOUT)

    def test_a_connection_error_is_still_retried(self):
        post, sleep, raised = self.call([requests.exceptions.ConnectionError("reset"), completion()])
        self.assertIsNone(raised)
        self.assertEqual(post.call_count, 2)
        sleep.assert_called_once()


if __name__ == "__main__":
    unittest.main()
