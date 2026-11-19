"""Retrying a truncated reply, naming the target_type mistake, and fallback models."""

import json
import threading
import unittest
from collections import Counter
from pathlib import Path
from unittest import mock

from daale.budget import BudgetExhausted
from daale.client import CompletionRecord, DaaleModelError
from daale.execution_contract import FailureMode, classify_failure
from daale.pipeline import (
    BASE_KERNELS,
    TRUNCATION_NUDGE,
    DaalePipeline,
    _repair_instruction,
    budget_shortfall,
)
from daale.providers import fallback_by_kernel_from_env

ROOT = Path(__file__).resolve().parents[1]
PRIMARY, BACKUP = "primary-model", "backup-model"


def load_json(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def truncated():
    error = DaaleModelError("cut off at the completion token limit")
    error.truncated = True
    return error


def unavailable():
    return DaaleModelError("high demand", status_code=503)


class ModelClient:
    """Serves the fixtures. ``behaviour[(purpose, model)](call_number)`` may return an exception to raise."""

    def __init__(self, behaviour=None, remaining=None):
        self.calls = []
        self.behaviour = behaviour or {}
        self.remaining = remaining or {}
        self._lock = threading.Lock()

    def requests_remaining(self, model=None):
        return self.remaining.get(model)

    def complete_json(self, purpose, model, messages, schema):
        with self._lock:
            self.calls.append((purpose, model, messages))
            number = sum(1 for p, m, _ in self.calls if (p, m) == (purpose, model))
        if self.remaining.get(model) == 0:
            # What the real client does: the budget refuses before any request is sent.
            raise BudgetExhausted(f"daily request budget for {model} is used up")
        action = self.behaviour.get((purpose, model))
        error = action(number) if action else None
        if error:
            raise error
        return CompletionRecord(
            purpose, load_json(f"fixtures/{purpose}_output.json"), model, f"served/{model}", f"req-{number}", {"total_tokens": 10}
        )

    def count(self, purpose=None, model=None):
        return sum(1 for p, m, _ in self.calls if purpose in (None, p) and model in (None, m))


class ResilienceTests(unittest.TestCase):
    def setUp(self):
        self.case = load_json("cases/vendor_alpha.json")
        self.policy = load_json("policies/vendor_post_technical_dd_v0_1.json")
        patcher = mock.patch("daale.pipeline.time.sleep")
        self.sleep = patcher.start()
        self.addCleanup(patcher.stop)

    def run_pipeline(self, client, fallback=None):
        pipeline = DaalePipeline(
            client=client,
            model_by_kernel={"default": PRIMARY},
            fallback_by_kernel={"default": fallback} if fallback else None,
        )
        return pipeline.run(self.case, self.policy)

    # -- a truncated reply is retried once, with a nudge ---------------------------

    def test_a_truncated_reply_is_retried_once_with_a_nudge(self):
        client = ModelClient({("contrarian", PRIMARY): lambda n: truncated() if n == 1 else None})
        result = self.run_pipeline(client)
        self.assertEqual(client.count("contrarian"), 2)
        retry = [m for p, _, m in client.calls if p == "contrarian"][1]
        self.assertEqual(retry[-1], {"role": "user", "content": TRUNCATION_NUDGE})
        self.assertEqual(result.decision_packet["execution_integrity"]["base_kernels_failed"], [])

    def test_a_reply_truncated_twice_gives_up_after_two_attempts_not_more(self):
        client = ModelClient({("contrarian", PRIMARY): lambda n: truncated()})
        result = self.run_pipeline(client)
        self.assertEqual(client.count("contrarian"), 2)
        self.assertEqual(result.decision_packet["execution_integrity"]["base_kernels_failed"], ["CONTRARIAN"])

    def test_truncation_is_classified_as_its_own_failure(self):
        self.assertEqual(classify_failure(truncated()), FailureMode.OUTPUT_TRUNCATED)

    # -- the target_type mistake is named -------------------------------------------

    def test_the_repair_message_explains_the_target_type_rule(self):
        error = "FIRST_PRINCIPLES: EVIDENCE_RELATION finding F15 must have target_type 'CLAIM' -- it names a declared claim, never 'POLICY' 'C3'"
        text = _repair_instruction(error, {"findings": []})
        self.assertIn("How to fix", text)
        self.assertIn("target_type 'CLAIM'", text)
        self.assertIn("Never use 'POLICY' or 'GENERAL'", text)
        requirement = _repair_instruction("X: REQUIREMENT_ASSESSMENT finding F1 must have target_type 'REQUIREMENT' -- ...", {})
        self.assertIn("target_id that is a declared requirement id", requirement)

    # -- fallback models --------------------------------------------------------------

    def test_a_fallback_is_not_used_when_the_primary_works(self):
        client = ModelClient()
        result = self.run_pipeline(client, fallback=BACKUP)
        self.assertEqual(client.count(model=BACKUP), 0)
        self.assertEqual(result.decision_packet["execution_integrity"]["fallbacks_used"], [])

    def test_a_truncated_kernel_goes_straight_to_the_fallback(self):
        client = ModelClient({("contrarian", PRIMARY): lambda n: truncated()})
        result = self.run_pipeline(client, fallback=BACKUP)
        self.assertEqual(client.count("contrarian", PRIMARY), 1)  # no second attempt that would loop again
        self.assertEqual(client.count("contrarian", BACKUP), 1)
        integrity = result.decision_packet["execution_integrity"]
        self.assertEqual(integrity["base_kernels_failed"], [])
        fallback = integrity["fallbacks_used"][0]
        self.assertEqual(
            {key: fallback[key] for key in ("kernel", "from", "to", "reason")},
            {"kernel": "CONTRARIAN", "from": PRIMARY, "to": BACKUP, "reason": "output-truncated"},
        )
        self.assertEqual(fallback["models_attempted"], [PRIMARY, BACKUP])
        self.assertEqual(result.trace["model_calls"]["contrarian"]["requested_model"], BACKUP)
        self.assertEqual(result.trace["model_calls"]["analyst"]["requested_model"], PRIMARY)

    def test_provider_errors_get_two_attempts_then_the_fallback(self):
        client = ModelClient({("outsider", PRIMARY): lambda n: unavailable()})
        result = self.run_pipeline(client, fallback=BACKUP)
        self.assertEqual(client.count("outsider", PRIMARY), 2)
        self.assertEqual(client.count("outsider", BACKUP), 1)
        self.assertEqual(result.decision_packet["execution_integrity"]["base_kernels_failed"], [])

    def test_the_adversary_can_fall_back_too(self):
        client = ModelClient({("adversary", PRIMARY): lambda n: unavailable()})
        result = self.run_pipeline(client, fallback=BACKUP)
        integrity = result.decision_packet["execution_integrity"]
        self.assertEqual(integrity["adversary"], "ran")
        self.assertEqual([f["kernel"] for f in integrity["fallbacks_used"]], ["ADVERSARY"])
        self.assertNotEqual(result.decision_packet["triggered_rule"]["rule_id"], "DEGRADED-EXECUTION")

    def test_an_exhausted_daily_budget_falls_back_without_waiting(self):
        error = BudgetExhausted("daily request budget used up")
        client = ModelClient({("adversary", PRIMARY): lambda n: error})
        result = self.run_pipeline(client, fallback=BACKUP)
        self.assertEqual(result.decision_packet["execution_integrity"]["adversary"], "ran")
        self.sleep.assert_not_called()

    def test_both_models_failing_leaves_the_kernel_failed_and_the_record_complete(self):
        client = ModelClient({
            ("outsider", PRIMARY): lambda n: unavailable(),
            ("outsider", BACKUP): lambda n: unavailable(),
        })
        result = self.run_pipeline(client, fallback=BACKUP)
        self.assertEqual(result.decision_packet["execution_integrity"]["base_kernels_failed"], ["OUTSIDER"])
        events = [e["event_type"] for e in result.trace["execution_state"]["audit_events"]]
        self.assertIn("kernel-fallback-failed", events)
        self.assertTrue(result.decision_packet["execution_integrity"]["requires_human_review"])

    def test_a_failure_another_model_would_share_does_not_use_the_fallback(self):
        client = ModelClient({("analyst", PRIMARY): lambda n: DaaleModelError("contract violation in the case")})
        self.run_pipeline(client, fallback=BACKUP)
        self.assertEqual(client.count("analyst", BACKUP), 0)

    def test_a_fallback_equal_to_the_primary_is_ignored(self):
        client = ModelClient({("outsider", PRIMARY): lambda n: unavailable()})
        pipeline = DaalePipeline(client, {"default": PRIMARY}, fallback_by_kernel={"default": PRIMARY})
        with self.assertRaisesRegex(ValueError, "cannot repeat"):
            pipeline.run(self.case, self.policy)
        self.assertEqual(client.count("outsider", PRIMARY), 0)

    # -- the budget knows about fallbacks ----------------------------------------------

    def test_a_primary_with_no_budget_is_not_a_shortfall_if_the_fallback_has_room(self):
        client = ModelClient(remaining={PRIMARY: 0, BACKUP: 20})
        models = {"default": PRIMARY}
        self.assertEqual(budget_shortfall(client, models), (PRIMARY, 0, 7))
        self.assertIsNone(budget_shortfall(client, models, fallback_by_kernel={"default": BACKUP}))

    def test_it_is_a_shortfall_when_the_fallback_has_no_room_either(self):
        client = ModelClient(remaining={PRIMARY: 3, BACKUP: 2})
        shortfall = budget_shortfall(client, {"default": PRIMARY}, fallback_by_kernel={"default": BACKUP})
        self.assertEqual(shortfall, (BACKUP, 2, 4))

    def test_only_the_overflow_spills_to_the_fallback(self):
        client = ModelClient(remaining={PRIMARY: 5, BACKUP: 2})
        self.assertIsNone(budget_shortfall(client, {"default": PRIMARY}, fallback_by_kernel={"default": BACKUP}))

    def test_a_full_run_is_allowed_when_the_budget_only_works_with_the_fallback(self):
        client = ModelClient(remaining={PRIMARY: 0, BACKUP: 20})
        result = self.run_pipeline(client, fallback=BACKUP)
        self.assertNotEqual(result.decision_packet["triggered_rule"]["rule_id"], "DEGRADED-EXECUTION")
        served = {call["requested_model"] for call in result.trace["model_calls"].values()}
        self.assertEqual(served, {BACKUP})  # every kernel ran on the fallback; nothing was sent to the exhausted model
        self.assertEqual(len(result.decision_packet["execution_integrity"]["fallbacks_used"]), 7)
        self.sleep.assert_not_called()

    # -- configuration ----------------------------------------------------------------

    def test_fallbacks_come_from_the_environment(self):
        env = {
            "DAALE_FALLBACK_MODEL": "a,b",
            "DAALE_ADVERSARY_FALLBACK_MODEL": "c,d",
        }
        self.assertEqual(fallback_by_kernel_from_env(env), {"default": ["a", "b"], "ADVERSARY": ["c", "d"]})
        self.assertEqual(fallback_by_kernel_from_env({}), {})

    def test_fallback_chain_configuration_rejects_empty_and_overlong_lists(self):
        with self.assertRaisesRegex(ValueError, "empty model"):
            fallback_by_kernel_from_env({"DAALE_FALLBACK_MODEL": "backup,,last"})
        with self.assertRaisesRegex(ValueError, "at most three fallbacks"):
            fallback_by_kernel_from_env({"DAALE_FALLBACK_MODEL": "a,b,c,d"})


class EscalatingClient(ModelClient):
    """A client that offers the escalated ceiling, as the generic client does, and records what it was asked."""

    USUAL, ESCALATED = 16000, 32000

    def __init__(self, behaviour=None):
        super().__init__(behaviour)
        self.ceilings = []

    def max_tokens_for(self, purpose):
        return self.USUAL

    def escalated_max_tokens(self, purpose):
        return self.ESCALATED

    def complete_json(self, purpose, model, messages, schema, max_tokens=None):
        self.ceilings.append((purpose, model, max_tokens))
        return super().complete_json(purpose, model, messages, schema)

    def ceilings_for(self, purpose, model):
        return [c for p, m, c in self.ceilings if (p, m) == (purpose, model)]


class TruncationCeilingTests(unittest.TestCase):
    """A truncated reply is retried with a longer ceiling, not the same one (added 2026-11-17)."""

    def setUp(self):
        self.case = load_json("cases/vendor_alpha.json")
        self.policy = load_json("policies/vendor_post_technical_dd_v0_1.json")
        patcher = mock.patch("daale.pipeline.time.sleep")
        patcher.start()
        self.addCleanup(patcher.stop)

    def run_pipeline(self, client, fallback=None):
        return DaalePipeline(
            client=client,
            model_by_kernel={"default": PRIMARY},
            fallback_by_kernel={"default": fallback} if fallback else None,
        ).run(self.case, self.policy)

    def test_a_normal_call_does_not_ask_for_a_longer_ceiling(self):
        client = EscalatingClient()
        self.run_pipeline(client)
        self.assertTrue(all(c is None for _, _, c in client.ceilings))

    def test_the_fallback_after_a_truncation_gets_the_longer_ceiling(self):
        client = EscalatingClient({("contrarian", PRIMARY): lambda n: truncated()})
        self.run_pipeline(client, fallback=BACKUP)
        self.assertEqual(client.ceilings_for("contrarian", PRIMARY), [None])
        self.assertEqual(client.ceilings_for("contrarian", BACKUP), [EscalatingClient.ESCALATED])

    def test_the_retry_after_a_truncation_with_no_fallback_gets_the_longer_ceiling(self):
        client = EscalatingClient({("contrarian", PRIMARY): lambda n: truncated() if n == 1 else None})
        result = self.run_pipeline(client)
        self.assertEqual(client.ceilings_for("contrarian", PRIMARY), [None, EscalatingClient.ESCALATED])
        self.assertEqual(result.decision_packet["execution_integrity"]["base_kernels_failed"], [])

    def test_a_fallback_after_a_failure_that_is_not_truncation_keeps_the_usual_ceiling(self):
        client = EscalatingClient({("contrarian", PRIMARY): lambda n: unavailable()})
        self.run_pipeline(client, fallback=BACKUP)
        self.assertEqual(client.ceilings_for("contrarian", BACKUP), [None])

    def test_a_client_that_offers_no_escalation_is_called_exactly_as_before(self):
        client = ModelClient({("contrarian", PRIMARY): lambda n: truncated() if n == 1 else None})
        result = self.run_pipeline(client)  # ModelClient.complete_json takes no max_tokens: it would raise
        self.assertEqual(result.decision_packet["execution_integrity"]["base_kernels_failed"], [])



if __name__ == "__main__":
    unittest.main()
