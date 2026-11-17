"""GenericApiClient against a stubbed HTTP layer: no network, no key."""

import json
import unittest
from pathlib import Path
from unittest import mock

from daale.client import DaaleModelError, GenericApiClient
from daale.schemas import KERNEL_OUTPUT_SCHEMA

ROOT = Path(__file__).resolve().parents[1]
GOOD = json.loads((ROOT / "fixtures/analyst_output.json").read_text(encoding="utf-8"))


class FakeResponse:
    def __init__(self, body, status=200):
        self._body = body
        self.status_code = status
        self.ok = status < 400
        self.headers = {}
        self.text = json.dumps(body)

    def json(self):
        return self._body


def completion(content, model="gemma-served"):
    return FakeResponse(
        {
            "id": "req-1",
            "model": model,
            "choices": [{"message": {"content": content}}],
            "usage": {"total_tokens": 42},
        }
    )


def client(**kwargs):
    defaults = {"api_key": "test-key", "base_url": "https://example.test/v1"}
    return GenericApiClient(**{**defaults, **kwargs})


class GenericApiClientTests(unittest.TestCase):
    def call(self, response, **client_kwargs):
        with mock.patch("daale.client.requests.post", return_value=response) as post:
            record = client(**client_kwargs).complete_json(
                "analyst", "some-model", [{"role": "user", "content": "x"}], KERNEL_OUTPUT_SCHEMA
            )
        return record, post

    def test_sends_to_the_chat_completions_path_with_bearer_auth(self):
        _, post = self.call(completion(json.dumps(GOOD)))
        self.assertEqual(post.call_args.args[0], "https://example.test/v1/chat/completions")
        self.assertEqual(post.call_args.kwargs["headers"]["Authorization"], "Bearer test-key")
        payload = post.call_args.kwargs["json"]
        self.assertEqual(payload["model"], "some-model")
        self.assertNotIn("response_format", payload)
        self.assertNotIn("provider", payload)

    def test_returns_the_parsed_validated_output_and_provider_metadata(self):
        record, _ = self.call(completion(json.dumps(GOOD)))
        self.assertEqual(record.output, GOOD)
        self.assertEqual(record.requested_model, "some-model")
        self.assertEqual(record.served_model, "gemma-served")
        self.assertEqual(record.usage, {"total_tokens": 42})

    def test_a_markdown_fenced_reply_is_accepted(self):
        record, _ = self.call(completion("```json\n" + json.dumps(GOOD) + "\n```"))
        self.assertEqual(record.output, GOOD)

    def test_inline_reasoning_before_the_answer_is_discarded(self):
        reply = "<thought>The user wants JSON. {\"decoy\": 1}</thought>" + json.dumps(GOOD)
        record, _ = self.call(completion(reply))
        self.assertEqual(record.output, GOOD)

    def test_a_reply_cut_off_mid_reasoning_says_to_raise_the_token_limit(self):
        with self.assertRaisesRegex(DaaleModelError, "token limit"):
            self.call(completion("<thought>still thinking about the relation matr"))

    def test_a_stray_closing_fence_after_a_complete_object_is_accepted(self):
        # Seen live: the object, then "```" with no opening fence (OUTSIDER, 2026-11-10).
        record, _ = self.call(completion(json.dumps(GOOD, indent=2) + "\n```"))
        self.assertEqual(record.output, GOOD)

    def test_other_text_after_the_object_is_still_rejected(self):
        with self.assertRaisesRegex(DaaleModelError, "Extra data"):
            self.call(completion(json.dumps(GOOD) + "\nHope that helps!"))
        with self.assertRaisesRegex(DaaleModelError, "Extra data"):
            self.call(completion(json.dumps(GOOD) + '{"a": 1}'))

    def test_a_json_error_reports_where_it_broke(self):
        broken = json.dumps(GOOD)[:-40] + ' "unterminated'
        with self.assertRaisesRegex(DaaleModelError, r"char \d+ of \d+"):
            self.call(completion(broken))

    def test_a_reply_cut_off_at_the_token_limit_says_so(self):
        response = completion(json.dumps(GOOD)[:50])
        response._body["choices"][0]["finish_reason"] = "length"
        with self.assertRaisesRegex(DaaleModelError, "LLM_MAX_TOKENS"):
            self.call(response)

    def test_native_schema_is_opt_in(self):
        _, post = self.call(completion(json.dumps(GOOD)), native_json_schema=True)
        self.assertEqual(post.call_args.kwargs["json"]["response_format"]["type"], "json_schema")

    def test_non_json_reply_is_a_model_error(self):
        with self.assertRaises(DaaleModelError):
            self.call(completion("I think the answer is yes."))

    def test_schema_invalid_reply_is_a_model_error(self):
        with self.assertRaises(DaaleModelError):
            self.call(completion(json.dumps({"case_id": "only"})))

    def test_http_error_carries_its_status_code(self):
        with mock.patch("daale.client.time.sleep"):
            with self.assertRaises(DaaleModelError) as raised:
                self.call(FakeResponse({"error": {"message": "nope"}}, status=401))
        self.assertEqual(raised.exception.status_code, 401)

    # -- the key is protected ----------------------------------------------

    def test_plain_http_to_a_remote_host_is_refused(self):
        with self.assertRaisesRegex(DaaleModelError, "plain http"):
            client(base_url="http://example.test/v1")

    def test_plain_http_to_loopback_is_allowed_without_a_key(self):
        local = GenericApiClient(api_key=None, base_url="http://localhost:11434/v1")
        self.assertEqual(local.url, "http://localhost:11434/v1/chat/completions")

    def test_a_kernel_can_have_its_own_token_ceiling(self):
        _, post = self.call(completion(json.dumps(GOOD)), max_tokens=16000, max_tokens_by_purpose={"analyst": 32000})
        self.assertEqual(post.call_args.kwargs["json"]["max_tokens"], 32000)

    def test_other_kernels_keep_the_default_ceiling(self):
        with mock.patch("daale.client.requests.post", return_value=completion(json.dumps(GOOD))) as post:
            client(max_tokens=16000, max_tokens_by_purpose={"analyst": 32000}).complete_json(
                "contrarian", "some-model", [{"role": "user", "content": "x"}], KERNEL_OUTPUT_SCHEMA
            )
        self.assertEqual(post.call_args.kwargs["json"]["max_tokens"], 16000)

    def test_env_sets_a_per_kernel_ceiling(self):
        from daale.providers import build_live_client
        env = {"DAALE_LIVE_PROVIDER": "generic", "LLM_API_KEY": "k", "LLM_BASE_URL": "https://example.test/v1",
               "LLM_MAX_TOKENS": "16000", "LLM_MAX_TOKENS_ANALYST": "32000"}
        built, _ = build_live_client(env)
        self.assertEqual(built.max_tokens_for("analyst"), 32000)
        self.assertEqual(built.max_tokens_for("historian"), 16000)

    def test_an_explicit_ceiling_for_one_call_overrides_the_usual_one(self):
        with mock.patch("daale.client.requests.post", return_value=completion(json.dumps(GOOD))) as post:
            client(max_tokens=16000).complete_json(
                "analyst", "some-model", [{"role": "user", "content": "x"}], KERNEL_OUTPUT_SCHEMA, max_tokens=24000
            )
        self.assertEqual(post.call_args.kwargs["json"]["max_tokens"], 24000)

    def test_the_escalated_ceiling_doubles_up_to_the_limit(self):
        self.assertEqual(client(max_tokens=16000, max_tokens_limit=32000).escalated_max_tokens("contrarian"), 32000)
        self.assertEqual(client(max_tokens=16000, max_tokens_limit=20000).escalated_max_tokens("contrarian"), 20000)
        self.assertEqual(client(max_tokens=8000, max_tokens_limit=32000).escalated_max_tokens("contrarian"), 16000)

    def test_there_is_no_escalation_when_the_ceiling_is_already_at_the_limit(self):
        c = client(max_tokens=16000, max_tokens_by_purpose={"analyst": 32000}, max_tokens_limit=32000)
        self.assertEqual(c.escalated_max_tokens("analyst"), 32000)

    def test_env_sets_the_escalation_limit(self):
        from daale.providers import build_live_client
        env = {"DAALE_LIVE_PROVIDER": "generic", "LLM_API_KEY": "k", "LLM_BASE_URL": "https://example.test/v1",
               "LLM_MAX_TOKENS": "16000", "LLM_MAX_TOKENS_LIMIT": "48000"}
        built, _ = build_live_client(env)
        self.assertEqual(built.escalated_max_tokens("contrarian"), 32000)
        self.assertEqual(built.max_tokens_limit, 48000)

    def test_remote_endpoint_requires_a_key(self):
        with self.assertRaisesRegex(DaaleModelError, "API_KEY"):
            client(api_key="")

    def test_base_url_is_required(self):
        with self.assertRaisesRegex(DaaleModelError, "BASE_URL"):
            client(base_url="")


if __name__ == "__main__":
    unittest.main()