import unittest

from daale.evaluation_adapter import (
    AdapterFailure,
    AdapterRequest,
    AdapterResponse,
    AdapterUsage,
)
from daale.execution_contract import FailureMode


class EvaluationAdapterContractTests(unittest.TestCase):
    def request(self, **changes):
        values = {
            "provider_id": "evaluation-provider",
            "requested_model": "nemotron-explicit-id",
            "purpose": "analyst",
            "messages": ({"role": "user", "content": "case material"},),
            "json_schema": {"type": "object"},
            "reasoning_effort": "high",
            "max_output_tokens": 12000,
            "timeout_seconds": 600,
        }
        values.update(changes)
        return AdapterRequest(**values)

    def test_request_makes_model_effort_schema_and_limits_explicit(self):
        request = self.request()
        self.assertEqual(request.requested_model, "nemotron-explicit-id")
        self.assertEqual(request.reasoning_effort, "high")
        self.assertEqual(request.max_output_tokens, 12000)
        self.assertEqual(request.timeout_seconds, 600)
        self.assertEqual(request.json_schema, {"type": "object"})

    def test_request_rejects_missing_identity_and_nonpositive_limits(self):
        for changes in ({"requested_model": " "}, {"max_output_tokens": 0},
                        {"timeout_seconds": 0}, {"messages": ()}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.request(**changes)

    def test_response_preserves_usage_and_route_provenance(self):
        response = AdapterResponse(
            provider_id="evaluation-provider",
            requested_model="nemotron-explicit-id",
            served_model="nemotron-served-id",
            output={"findings": []},
            request_id="req-123",
            usage=AdapterUsage(input_tokens=100, output_tokens=20, total_tokens=120),
            attempts=2,
            output_token_ceiling=12000,
            structured_output_mode="json-schema",
            reasoning_effort_requested="high",
            reasoning_effort_served="high",
        )
        self.assertEqual(response.served_model, "nemotron-served-id")
        self.assertEqual(response.usage.total_tokens, 120)
        self.assertEqual(response.attempts, 2)

    def test_failure_has_classification_attempts_and_retry_metadata(self):
        error = AdapterFailure(
            provider_id="evaluation-provider",
            requested_model="nemotron-explicit-id",
            failure_mode=FailureMode.PROVIDER_RATE_LIMIT,
            message="rate limited",
            attempts=1,
            status_code=429,
            retry_after_seconds=30,
        )
        self.assertEqual(str(error), "rate limited")
        self.assertIs(error.failure_mode, FailureMode.PROVIDER_RATE_LIMIT)
        self.assertEqual(error.retry_after_seconds, 30)


if __name__ == "__main__":
    unittest.main()
