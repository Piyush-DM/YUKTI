import unittest

from daale.execution_contract import FailureMode
from daale.model_routing import RunModelHealth, parse_model_chain


class ModelChainTests(unittest.TestCase):
    def test_chain_is_primary_then_fallbacks_in_order(self):
        self.assertEqual(parse_model_chain(" primary ", ["backup-a", "backup-b"]),
                         ("primary", "backup-a", "backup-b"))

    def test_chain_rejects_duplicate_or_more_than_four_models(self):
        with self.assertRaisesRegex(ValueError, "cannot repeat"):
            parse_model_chain("primary", ["backup", "primary"])
        with self.assertRaisesRegex(ValueError, "at most 4"):
            parse_model_chain("primary", ["a", "b", "c", "d"])

    def test_chain_rejects_empty_or_non_string_entries(self):
        for fallback in ("backup,,last", ["backup", " "] , ["backup", None]):
            with self.subTest(fallback=fallback), self.assertRaises(ValueError):
                parse_model_chain("primary", fallback)


class RunModelHealthTests(unittest.TestCase):
    def setUp(self):
        self.now = 100.0
        self.health = RunModelHealth(clock=lambda: self.now)

    def test_unavailable_model_is_dead_for_the_run(self):
        state = self.health.mark_failure(
            "gone-model", "provider", FailureMode.MODEL_NOT_AVAILABLE
        )
        self.assertEqual(state.state, "DEAD")
        self.assertEqual(self.health.status("gone-model", "provider").state, "DEAD")
        self.assertEqual(self.health.status("other-model", "provider").state, "HEALTHY")

    def test_authentication_failure_marks_provider_dead_for_all_models(self):
        self.health.mark_failure("model-a", "provider", FailureMode.AUTHENTICATION_FAILED)
        self.assertEqual(self.health.status("model-a", "provider").state, "DEAD")
        self.assertEqual(self.health.status("model-b", "provider").state, "DEAD")
        self.assertEqual(self.health.status("model-b", "other-provider").state, "HEALTHY")

    def test_rate_limit_cools_until_retry_after_then_model_resumes(self):
        self.health.mark_failure(
            "model-a", "provider", FailureMode.PROVIDER_RATE_LIMIT, retry_after=30
        )
        self.assertEqual(self.health.status("model-a", "provider").state, "COOLING")
        self.assertEqual(self.health.seconds_remaining("model-a", "provider"), 30)
        self.now += 30
        self.assertEqual(self.health.status("model-a", "provider").state, "HEALTHY")

    def test_daily_quota_cools_until_budget_reset(self):
        self.health.mark_failure(
            "model-a", "provider", FailureMode.QUOTA_EXHAUSTED,
            daily_reset_seconds=120,
        )
        self.assertEqual(self.health.seconds_remaining("model-a", "provider"), 120)
        self.assertEqual(self.health.snapshot()["models"]["model-a"]["state"], "COOLING")

    def test_transient_failure_does_not_mark_model_unhealthy(self):
        self.health.mark_failure("model-a", "provider", FailureMode.TRANSIENT_PROVIDER_ERROR)
        self.assertEqual(self.health.status("model-a", "provider").state, "HEALTHY")


if __name__ == "__main__":
    unittest.main()
