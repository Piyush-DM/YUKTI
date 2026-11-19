import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from daale.budget import BudgetExhausted, RequestBudget
from daale.client import (
    CompletionRecord,
    DaaleModelError,
    GenericApiClient,
    ModelPacers,
    RequestPacer,
)
from daale.providers import parse_limits
from daale.execution_contract import FailureMode, classify_failure
from daale.pipeline import ALL_KERNELS, DaalePipeline, budget_shortfall

ROOT = Path(__file__).resolve().parents[1]


def load_json(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class Clock:
    """A settable UTC clock."""

    def __init__(self, moment):
        self.moment = moment

    def __call__(self):
        return self.moment


NOON_PACIFIC = datetime(2026, 11, 8, 20, 0, tzinfo=timezone.utc)  # 12:00 PST


class RequestBudgetTests(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._dir.cleanup)
        self.path = Path(self._dir.name) / "budget.json"
        self.clock = Clock(NOON_PACIFIC)

    def budget(self, limit=3):
        return RequestBudget(limit, self.path, clock=self.clock)

    def test_counts_requests_until_the_limit_then_refuses(self):
        budget = self.budget(3)
        for _ in range(3):
            budget.take()
        self.assertEqual((budget.used(), budget.remaining()), (3, 0))
        with self.assertRaises(BudgetExhausted):
            budget.take()
        self.assertEqual(budget.used(), 3)

    def test_the_count_survives_a_restart(self):
        self.budget().take()
        self.assertEqual(self.budget().used(), 1)

    def test_a_new_pacific_day_starts_from_zero(self):
        budget = self.budget(2)
        budget.take()
        budget.take()
        self.clock.moment = NOON_PACIFIC + timedelta(hours=13)  # past midnight Pacific
        self.assertEqual(budget.remaining(), 2)

    def test_the_same_pacific_day_spans_utc_midnight(self):
        budget = self.budget(2)
        budget.take()
        self.clock.moment = datetime(2026, 11, 9, 3, 0, tzinfo=timezone.utc)  # 19:00 PST, still 8 Nov
        self.assertEqual(budget.used(), 1)

    def test_set_used_records_requests_made_elsewhere(self):
        budget = self.budget(20)
        budget.set_used(17)
        self.assertEqual(budget.remaining(), 3)

    def test_seconds_until_reset_is_positive_and_under_a_day(self):
        self.assertTrue(0 < self.budget().seconds_until_reset() <= 86400 + 1)

    def test_an_unreadable_file_counts_as_zero_rather_than_crashing(self):
        self.path.write_text("not json", encoding="utf-8")
        self.assertEqual(self.budget().used(), 0)


class PacerTests(unittest.TestCase):
    def test_third_request_in_a_window_waits_for_a_slot(self):
        now = [0.0]
        slept = []

        def sleep(seconds):
            slept.append(seconds)
            now[0] += seconds

        pacer = RequestPacer(2, clock=lambda: now[0], sleep=sleep)
        pacer.wait()
        pacer.wait()
        self.assertEqual(slept, [])
        pacer.wait()
        self.assertTrue(slept and sum(slept) >= 60)

    def test_budget_exhaustion_is_refused_without_waiting(self):
        budget = mock.Mock()
        budget.check.side_effect = BudgetExhausted("used up")
        sleep = mock.Mock()
        pacer = RequestPacer(1, budget=budget, sleep=sleep)
        with self.assertRaises(BudgetExhausted):
            pacer.wait()
        sleep.assert_not_called()

    def test_every_http_attempt_takes_a_slot_and_a_budget_unit(self):
        with tempfile.TemporaryDirectory() as directory:
            pacers = ModelPacers(limits={"m": (None, 2)}, budget_dir=directory)
            client = GenericApiClient(
                api_key="k", base_url="https://example.test/v1", pacers=pacers
            )
            self.assertEqual(client.requests_remaining("m"), 2)
            error_response = mock.Mock(ok=False, status_code=503, text="x", headers={})
            error_response.json.return_value = None
            with mock.patch("daale.client.requests.post", return_value=error_response), \
                    mock.patch("daale.client.time.sleep"):
                with self.assertRaises((DaaleModelError, BudgetExhausted)):
                    client.complete_json("analyst", "m", [{"role": "user", "content": "x"}], {"type": "object"})
            self.assertEqual(client.requests_remaining("m"), 0)


class PipelineBudgetTests(unittest.TestCase):
    def setUp(self):
        self.case = load_json("cases/vendor_alpha.json")
        self.policy = load_json("policies/vendor_post_technical_dd_v0_1.json")

    class Counting:
        def __init__(self, remaining, fail=None):
            self.remaining = remaining
            self.calls = 0
            self.purposes = []
            self.fail = fail

        def requests_remaining(self, model=None):
            return self.remaining

        def complete_json(self, purpose, model, messages, schema):
            self.calls += 1
            self.purposes.append(purpose)
            if self.fail:
                raise self.fail
            return CompletionRecord(purpose, load_json(f"fixtures/{purpose}_output.json"), model, model, "r", {})

    def test_a_judgment_the_budget_cannot_finish_is_refused_before_any_request(self):
        client = self.Counting(remaining=len(ALL_KERNELS) - 1)
        pipeline = DaalePipeline(client=client, model_by_kernel={"default": "m"})
        with self.assertRaisesRegex(BudgetExhausted, "Nothing was sent"):
            pipeline.run(self.case, self.policy)
        self.assertEqual(client.calls, 0)

    def test_enough_budget_lets_it_run(self):
        client = self.Counting(remaining=len(ALL_KERNELS))
        result = DaalePipeline(client=client, model_by_kernel={"default": "m"}).run(self.case, self.policy)
        self.assertEqual(client.calls, len(ALL_KERNELS))
        self.assertEqual(result.decision_packet["execution_integrity"]["adversary"], "ran")

    def test_a_budget_that_runs_out_mid_run_is_not_retried(self):
        error = BudgetExhausted("daily request budget used up")
        self.assertEqual(classify_failure(error), FailureMode.QUOTA_EXHAUSTED)
        client = self.Counting(remaining=None, fail=error)
        with mock.patch("daale.pipeline.time.sleep") as sleep:
            result = DaalePipeline(client=client, model_by_kernel={"default": "m"}).run(self.case, self.policy)
        sleep.assert_not_called()
        # The first daily-quota failure cools the model for this run; parallel
        # kernels already in flight may have called, but later phases skip it.
        self.assertGreaterEqual(client.calls, 1)
        self.assertLessEqual(client.calls, 6)
        self.assertNotIn("adversary", client.purposes)
        self.assertEqual(result.decision_packet["policy_state"], "ESCALATE")


class TokenPacingTests(unittest.TestCase):
    def make(self, tokens_per_minute, per_minute=None):
        self.now = [0.0]
        self.slept = []

        def sleep(seconds):
            self.slept.append(seconds)
            self.now[0] += seconds

        return RequestPacer(per_minute, tokens_per_minute=tokens_per_minute,
                            clock=lambda: self.now[0], sleep=sleep)

    def test_requests_that_do_not_fit_the_token_cap_wait_for_room(self):
        pacer = self.make(10000)
        pacer.wait(4000)
        pacer.wait(4000)
        self.assertEqual(self.slept, [])
        pacer.wait(4000)  # 12000 in the window
        self.assertTrue(self.slept and sum(self.slept) >= 60)

    def test_actual_usage_replaces_the_estimate(self):
        pacer = self.make(10000)
        handle = pacer.wait(9000)
        pacer.settle(handle, 2000)  # the reply was far smaller than reserved
        pacer.wait(7000)
        self.assertEqual(self.slept, [])

    def test_a_request_larger_than_the_cap_is_refused_not_waited_for(self):
        pacer = self.make(5000)
        with self.assertRaisesRegex(BudgetExhausted, "can never be sent"):
            pacer.wait(8000)
        self.assertEqual(self.slept, [])

    def test_request_and_token_caps_apply_together(self):
        pacer = self.make(100000, per_minute=1)
        pacer.wait(100)
        pacer.wait(100)
        self.assertTrue(sum(self.slept) >= 60)


class PerModelTests(unittest.TestCase):
    def test_limits_are_parsed_per_model(self):
        self.assertEqual(
            parse_limits("gemini-3.8-flash=5/20; gemma-4-31b-it=15/-"),
            {"gemini-3.8-flash": (5, 20, None), "gemma-4-31b-it": (15, None, None)},
        )
        self.assertEqual(parse_limits("m=5/20/250k"), {"m": (5, 20, 250000)})
        self.assertEqual(parse_limits("m=5/-/16000"), {"m": (5, None, 16000)})
        self.assertEqual(parse_limits(""), {})
        with self.assertRaises(ValueError):
            parse_limits("nonsense")

    def test_each_model_keeps_its_own_count(self):
        with tempfile.TemporaryDirectory() as directory:
            pacers = ModelPacers(limits={"a": (None, 2), "b": (None, 5)}, budget_dir=directory)
            pacers.for_model("a").budget.take()
            self.assertEqual((pacers.remaining("a"), pacers.remaining("b")), (1, 5))
            self.assertIsNone(pacers.remaining("unlisted"))

    def test_a_model_without_limits_is_never_short(self):
        with tempfile.TemporaryDirectory() as directory:
            pacers = ModelPacers(limits={"gemini": (5, 20)}, budget_dir=directory)
            pacers.for_model("gemini").budget.set_used(20)
            client = GenericApiClient(api_key="k", base_url="https://example.test/v1", pacers=pacers)
            models = {"default": "gemma", "ADVERSARY": "gemini"}
            self.assertEqual(budget_shortfall(client, models), ("gemini", 0, 1))
            pacers.for_model("gemini").budget.set_used(19)
            self.assertIsNone(budget_shortfall(client, models))

    def test_the_default_applies_to_models_without_an_entry(self):
        with tempfile.TemporaryDirectory() as directory:
            pacers = ModelPacers(default_per_day=3, budget_dir=directory)
            self.assertEqual((pacers.remaining("x"), pacers.remaining("y")), (3, 3))
            pacers.for_model("x").budget.take()
            self.assertEqual((pacers.remaining("x"), pacers.remaining("y")), (2, 3))


if __name__ == "__main__":
    unittest.main()
