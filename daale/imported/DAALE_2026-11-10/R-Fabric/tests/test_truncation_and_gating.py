"""Truncation retries and fallbacks, and the opt-in gating of the quotes field (added 2026-11-17).

Offline only: no model is called. These tests show how the code behaves; they cannot show that live models
no longer truncate (see the live-validation protocol in ENGINEERING_REVIEW_2026-11-17.md).
"""

import copy
import json
import threading
import unittest
from pathlib import Path
from unittest import mock

from daale.client import CompletionRecord, DaaleModelError, GenericApiClient
from daale.pipeline import BASE_KERNELS, DaalePipeline
from daale.prompts import build_adversary_messages, build_kernel_messages
from daale.schemas import KERNEL_OUTPUT_SCHEMA, kernel_output_schema

ROOT = Path(__file__).resolve().parents[1]
PRIMARY, BACKUP = "primary-model", "backup-model"
USUAL, ESCALATED = 16000, 32000


def load_json(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def truncated():
    error = DaaleModelError("cut off at the completion token limit")
    error.truncated = True
    return error


class RecordingClient:
    """Serves the fixtures; records the schema and ceiling of every call; offers an escalated ceiling."""

    def __init__(self, behaviour=None, usual=USUAL, escalated=ESCALATED):
        self.calls = []  # (purpose, model, max_tokens or None)
        self.schemas = []
        self.behaviour = behaviour or {}
        self._usual, self._escalated = usual, escalated
        self._lock = threading.Lock()

    def max_tokens_for(self, purpose):
        return self._usual

    def escalated_max_tokens(self, purpose):
        return self._escalated

    def complete_json(self, purpose, model, messages, schema, max_tokens=None):
        with self._lock:
            self.calls.append((purpose, model, max_tokens))
            self.schemas.append(schema)
            number = sum(1 for p, m, _ in self.calls if (p, m) == (purpose, model))
        action = self.behaviour.get((purpose, model))
        error = action(number) if action else None
        if error:
            raise error
        return CompletionRecord(
            purpose, load_json(f"fixtures/{purpose}_output.json"), model, f"served/{model}", f"req-{number}", {"total_tokens": 10}
        )

    def ceilings(self, purpose, model):
        return [c for p, m, c in self.calls if (p, m) == (purpose, model)]


class PipelineCase(unittest.TestCase):
    def setUp(self):
        self.case = load_json("cases/vendor_alpha.json")
        self.policy = load_json("policies/vendor_post_technical_dd_v0_1.json")
        patcher = mock.patch("daale.pipeline.time.sleep")
        patcher.start()
        self.addCleanup(patcher.stop)

    def run_pipeline(self, client, fallback=BACKUP, policy=None):
        return DaalePipeline(
            client=client,
            model_by_kernel={"default": PRIMARY},
            fallback_by_kernel={"default": fallback} if fallback else None,
        ).run(self.case, policy or self.policy)

    def events(self, result, kernel, kind=None):
        found = [e for e in result.trace["execution_state"]["audit_events"] if e["kernel_id"] == kernel]
        return [e for e in found if kind is None or e["event_type"] == kind]


class TruncationTests(PipelineCase):
    def test_a_kernel_that_always_truncates_is_bounded_and_fails_once(self):
        client = RecordingClient({
            ("contrarian", PRIMARY): lambda n: truncated(),
            ("contrarian", BACKUP): lambda n: truncated(),
        })
        result = self.run_pipeline(client)
        self.assertEqual(client.ceilings("contrarian", PRIMARY), [None])            # one try, then the fallback
        self.assertEqual(client.ceilings("contrarian", BACKUP), [ESCALATED, ESCALATED])  # two tries, both longer
        self.assertEqual(len([c for c in client.calls if c[0] == "contrarian"]), 3)  # no loop
        self.assertEqual(result.decision_packet["execution_integrity"]["base_kernels_failed"], ["CONTRARIAN"])

    def test_no_partial_output_from_a_truncated_kernel_reaches_the_decision(self):
        client = RecordingClient({
            ("contrarian", PRIMARY): lambda n: truncated(),
            ("contrarian", BACKUP): lambda n: truncated(),
        })
        result = self.run_pipeline(client)
        self.assertNotIn("contrarian", result.trace["provisional_findings"])
        self.assertNotIn("contrarian", result.trace["model_calls"])
        self.assertTrue(result.decision_packet["execution_integrity"]["requires_human_review"])

    def test_each_attempt_records_the_ceiling_it_ran_under(self):
        client = RecordingClient({("contrarian", PRIMARY): lambda n: truncated()})
        result = self.run_pipeline(client)
        failed = self.events(result, "CONTRARIAN", "kernel-failed")
        succeeded = self.events(result, "CONTRARIAN", "kernel-succeeded")
        self.assertEqual([e["metadata"]["max_tokens"] for e in failed], [USUAL])
        self.assertEqual([e["metadata"]["max_tokens"] for e in succeeded], [ESCALATED])
        self.assertEqual(self.events(result, "CONTRARIAN", "kernel-fallback-used")[0]["metadata"]["reason"], "output-truncated")

    def test_an_ordinary_call_records_the_usual_ceiling(self):
        result = self.run_pipeline(RecordingClient())
        for event in self.events(result, "ANALYST", "kernel-succeeded"):
            self.assertEqual(event["metadata"]["max_tokens"], USUAL)

    def test_no_boost_is_asked_for_when_the_limit_leaves_no_headroom(self):
        client = RecordingClient({("contrarian", PRIMARY): lambda n: truncated()}, usual=16000, escalated=16000)
        self.run_pipeline(client)
        self.assertEqual(client.ceilings("contrarian", BACKUP), [None])

    def test_a_kernel_already_at_the_limit_is_not_boosted(self):
        client = RecordingClient({("analyst", PRIMARY): lambda n: truncated()}, usual=32000, escalated=32000)
        self.run_pipeline(client)
        self.assertEqual(client.ceilings("analyst", BACKUP), [None])


class EscalationArithmeticTests(unittest.TestCase):
    def client(self, **kwargs):
        return GenericApiClient(api_key="k", base_url="https://example.test/v1", **kwargs)

    def test_the_escalated_ceiling_never_exceeds_the_limit_unless_the_usual_one_already_does(self):
        cases = [
            (16000, 32000, 32000),  # doubles
            (16000, 20000, 20000),  # capped by the limit
            (16000, 16000, 16000),  # no headroom
            (16000, 8000, 16000),   # limit below the usual ceiling: never lowers it
            (4000, 32000, 8000),
        ]
        for usual, limit, expected in cases:
            with self.subTest(usual=usual, limit=limit):
                self.assertEqual(self.client(max_tokens=usual, max_tokens_limit=limit).escalated_max_tokens("x"), expected)

    def test_a_per_kernel_ceiling_is_escalated_from_its_own_value(self):
        c = self.client(max_tokens=16000, max_tokens_by_purpose={"analyst": 24000}, max_tokens_limit=40000)
        self.assertEqual(c.escalated_max_tokens("analyst"), 40000)   # 48000 capped at the limit
        self.assertEqual(c.escalated_max_tokens("contrarian"), 32000)


class QuotesGatingTests(PipelineCase):
    """The quotes schema property and instruction are sent only under a policy that asks for them."""

    def grounded_policy(self):
        policy = copy.deepcopy(self.policy)
        policy["contradiction_grounding"] = "quoted"
        return policy

    def findings_properties(self, schema):
        return schema["properties"]["findings"]["items"]["properties"]

    def test_the_model_facing_schema_has_no_quotes_unless_asked(self):
        self.assertNotIn("quotes", self.findings_properties(kernel_output_schema(False)))
        self.assertIn("quotes", self.findings_properties(kernel_output_schema(True)))

    def test_building_the_stripped_schema_does_not_change_the_validating_schema(self):
        before = json.dumps(KERNEL_OUTPUT_SCHEMA, sort_keys=True)
        kernel_output_schema(False)
        self.assertEqual(json.dumps(KERNEL_OUTPUT_SCHEMA, sort_keys=True), before)
        self.assertIn("quotes", self.findings_properties(KERNEL_OUTPUT_SCHEMA))

    def test_a_policy_without_grounding_sends_no_mention_of_quotes_to_any_kernel(self):
        for native in (False, True):
            for kernel in BASE_KERNELS:
                with self.subTest(kernel=kernel, native=native):
                    text = json.dumps(build_kernel_messages(kernel, self.case, self.policy, None, native))
                    self.assertNotIn("quotes", text)
            with self.subTest(kernel="ADVERSARY", native=native):
                text = json.dumps(build_adversary_messages(self.case, self.policy, {}, native))
                self.assertNotIn("quotes", text)

    def test_a_grounding_policy_asks_only_the_kernels_that_can_raise_contradictions(self):
        policy = self.grounded_policy()
        for kernel in BASE_KERNELS:
            system = build_kernel_messages(kernel, self.case, policy, None, True)[0]["content"]
            with self.subTest(kernel=kernel):
                self.assertEqual("'quotes'" in system, kernel in ("CONTRARIAN", "OUTSIDER"))
        self.assertIn("'quotes'", build_adversary_messages(self.case, policy, {}, True)[0]["content"])

    def test_the_prompted_schema_carries_quotes_only_for_a_grounding_policy(self):
        plain = build_kernel_messages("ANALYST", self.case, self.policy, None, False)[1]["content"]
        grounded = build_kernel_messages("ANALYST", self.case, self.grounded_policy(), None, False)[1]["content"]
        self.assertNotIn('"quotes"', plain)
        self.assertIn('"quotes"', grounded)

    def test_the_pipeline_hands_the_client_the_matching_schema(self):
        plain_client = RecordingClient()
        self.run_pipeline(plain_client)
        self.assertTrue(all("quotes" not in self.findings_properties(s) for s in plain_client.schemas))
        grounded_client = RecordingClient()
        self.run_pipeline(grounded_client, policy=self.grounded_policy())
        self.assertTrue(all("quotes" in self.findings_properties(s) for s in grounded_client.schemas))


if __name__ == "__main__":
    unittest.main()
