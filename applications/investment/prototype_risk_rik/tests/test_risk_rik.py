"""Tests for prototype Risk RIK contracts and execution boundary."""

from __future__ import annotations

from http.server import ThreadingHTTPServer
from typing import Any, cast
import json
import os
import threading
import unittest
from unittest.mock import patch
from urllib.request import Request, urlopen

from applications.investment.prototype_risk_rik.contracts import (
    RiskRikArtifact,
    RiskRikExecutionError,
    RiskRikExecutionRequest,
    SourceMaterial,
)
from applications.investment.prototype_risk_rik.executor import execute_risk_rik
from applications.investment.prototype_risk_rik.provider import (
    DeterministicRiskRikAdapter,
    OpenAIResponsesAdapter,
    ProviderConfigurationError,
    configured_adapter_from_environment,
)
from applications.investment.prototype_risk_rik.server import PrototypeRiskRikHandler


class FakeAdapter:
    """Test adapter returning a supplied structured payload."""

    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload
        self.prompt = ""

    def generate_structured(
        self, prompt: str, schema: dict[str, Any]
    ) -> dict[str, Any]:
        self.prompt = prompt
        self.schema = schema
        return dict(self.payload)


def valid_payload() -> dict[str, Any]:
    """Return a minimal valid Risk RIK artifact payload."""
    return {
        "rik_identity": "Risk RIK",
        "run_id": "risk-rik-run-test",
        "primary_conclusion": "Concentration is the dominant risk.",
        "qualitative_confidence": "Moderate",
        "identified_risks": [
            {
                "name": "Customer concentration",
                "severity": "High",
                "description": "Revenue depends heavily on a small customer group.",
                "mitigation_or_condition": "Require concentration reporting.",
                "evidence_references": [
                    {
                        "source_label": "source-1",
                        "relevance": "Shows concentration.",
                        "support_status": "supported",
                    }
                ],
            }
        ],
        "relevant_propositions": [
            {
                "proposition": "Concentration is acceptable.",
                "position": "OPPOSES",
                "reasoning_summary": "Material concentration remains unresolved.",
            }
        ],
        "evidence_references": [
            {
                "source_label": "source-1",
                "relevance": "Used for concentration risk.",
                "support_status": "supported",
            }
        ],
        "key_assumptions": ["The source material is directionally accurate."],
        "strongest_objection": "The customer may diversify quickly.",
        "information_that_would_change_position": [
            "Signed contracts reducing top-three concentration."
        ],
        "unresolved_questions": ["Can new customers close before Series D?"],
        "generated_at": "2026-07-16T00:00:00Z",
        "prototype_contract": "investment.prototype.risk_rik.v1",
    }


class RiskRikContractTests(unittest.TestCase):
    """Structured artifact validation tests."""

    def test_valid_artifact_is_machine_readable(self) -> None:
        """A complete artifact payload should validate."""
        artifact = RiskRikArtifact.model_validate(valid_payload())

        self.assertEqual(artifact.rik_identity, "Risk RIK")
        self.assertEqual(artifact.identified_risks[0].severity, "High")

    def test_validation_rejects_malformed_output(self) -> None:
        """Malformed model output should fail validation."""
        payload = valid_payload()
        payload.pop("primary_conclusion")

        with self.assertRaises(Exception):
            RiskRikArtifact.model_validate(payload)


class RiskRikExecutionTests(unittest.TestCase):
    """Execution boundary behavior."""

    def test_execute_risk_rik_returns_validated_artifact(self) -> None:
        """The execution boundary should validate adapter output."""
        request = RiskRikExecutionRequest(
            case_title="Mock case",
            case_material="Customer concentration appears high.",
            source_materials=[
                SourceMaterial(
                    label="source-1",
                    text="Top three customers are a large share of revenue.",
                )
            ],
        )
        adapter = FakeAdapter(valid_payload())

        artifact = execute_risk_rik(request, adapter)

        self.assertEqual(artifact.rik_identity, "Risk RIK")
        self.assertIn("source-1", adapter.prompt)

    def test_execute_risk_rik_raises_on_invalid_adapter_output(self) -> None:
        """Malformed adapter output should become an explicit execution error."""
        request = RiskRikExecutionRequest(
            case_title="Mock case",
            case_material="Customer concentration appears high.",
        )
        adapter = FakeAdapter({"not": "valid"})

        with self.assertRaises(RiskRikExecutionError):
            execute_risk_rik(request, adapter)

    def test_provider_configuration_requires_explicit_environment(self) -> None:
        """The real provider should not run without explicit configuration."""
        with self.assertRaises(ProviderConfigurationError):
            configured_adapter_from_environment({})

    def test_openai_configuration_path_remains_intact(self) -> None:
        """OpenAI provider configuration should still build the OpenAI adapter."""
        adapter = configured_adapter_from_environment(
            {
                "YUKTI_PROTOTYPE_RISK_RIK_PROVIDER": "openai",
                "YUKTI_PROTOTYPE_RISK_RIK_MODEL": "test-model",
                "OPENAI_API_KEY": "test-key",
            }
        )

        self.assertIsInstance(adapter, OpenAIResponsesAdapter)


class DeterministicProviderTests(unittest.TestCase):
    """Deterministic provider behavior."""

    def test_identical_input_produces_identical_structured_output(self) -> None:
        """The deterministic provider should be stable for the same request."""
        request = deterministic_request(
            case_material="Top three customer concentration is 48% of ARR."
        )
        adapter = DeterministicRiskRikAdapter()

        first = execute_risk_rik(request, adapter)
        second = execute_risk_rik(request, adapter)

        self.assertEqual(
            first.model_dump(mode="json"),
            second.model_dump(mode="json"),
        )

    def test_different_input_changes_output(self) -> None:
        """Different risk signals should produce different artifacts."""
        adapter = DeterministicRiskRikAdapter()

        concentration = execute_risk_rik(
            deterministic_request(
                case_material="Top three customer concentration is 48% of ARR."
            ),
            adapter,
        )
        liquidity = execute_risk_rik(
            deterministic_request(case_material="Cash burn creates runway pressure."),
            adapter,
        )

        self.assertNotEqual(concentration.run_id, liquidity.run_id)
        self.assertNotEqual(
            concentration.identified_risks[0].name,
            liquidity.identified_risks[0].name,
        )

    def test_supplied_source_labels_are_preserved(self) -> None:
        """Evidence references should use supplied labels, not invented IDs."""
        artifact = execute_risk_rik(
            deterministic_request(
                case_material="Customer concentration and margin pressure.",
                source_label="MDR-19",
            ),
            DeterministicRiskRikAdapter(),
        )

        self.assertEqual(
            [reference.source_label for reference in artifact.evidence_references],
            ["MDR-19"],
        )

    def test_unsupported_provenance_is_not_invented(self) -> None:
        """No source labels should mean no fabricated evidence references."""
        artifact = execute_risk_rik(
            RiskRikExecutionRequest(
                case_title="No source labels",
                case_material="Customer concentration appears material.",
            ),
            DeterministicRiskRikAdapter(),
        )
        artifact_json = json.dumps(artifact.model_dump(mode="json"))

        self.assertEqual(artifact.evidence_references, [])
        self.assertNotIn("EV-", artifact_json)

    def test_deterministic_output_passes_schema(self) -> None:
        """Deterministic provider output should validate as a RiskRikArtifact."""
        artifact = execute_risk_rik(
            deterministic_request(case_material="Governance reporting is incomplete."),
            DeterministicRiskRikAdapter(),
        )

        self.assertIsInstance(artifact, RiskRikArtifact)
        self.assertIn("Deterministic development output", artifact.primary_conclusion)

    def test_deterministic_provider_requires_no_credentials(self) -> None:
        """Provider selection should allow deterministic execution without a key."""
        adapter = configured_adapter_from_environment(
            {"YUKTI_PROTOTYPE_RISK_RIK_PROVIDER": "deterministic"}
        )

        self.assertIsInstance(adapter, DeterministicRiskRikAdapter)


class RiskRikEndpointTests(unittest.TestCase):
    """HTTP endpoint execution tests."""

    def test_endpoint_runs_deterministic_provider_without_credentials(self) -> None:
        """The full endpoint should execute deterministic provider output."""
        server = ThreadingHTTPServer(("127.0.0.1", 0), PrototypeRiskRikHandler)
        host = cast(str, server.server_address[0])
        port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        payload = {
            "case_title": "Endpoint deterministic case",
            "case_material": "Customer concentration creates risk.",
            "source_materials": [
                {
                    "label": "source-A",
                    "text": "Top three customers account for 48% of ARR.",
                }
            ],
        }

        with patch.dict(
            os.environ,
            {"YUKTI_PROTOTYPE_RISK_RIK_PROVIDER": "deterministic"},
            clear=False,
        ):
            thread.start()
            try:
                request = Request(
                    f"http://{host}:{port}/prototype-risk-rik/execute",
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urlopen(request, timeout=5) as response:
                    response_payload = json.loads(response.read().decode("utf-8"))
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        self.assertTrue(response_payload["ok"])
        self.assertEqual(response_payload["provider"]["provider"], "deterministic")
        artifact = RiskRikArtifact.model_validate(response_payload["artifact"])
        self.assertEqual(artifact.evidence_references[0].source_label, "source-A")


def deterministic_request(
    case_material: str,
    source_label: str = "source-1",
) -> RiskRikExecutionRequest:
    """Create a deterministic-provider test request."""
    return RiskRikExecutionRequest(
        case_title="Deterministic case",
        case_material=case_material,
        source_materials=[
            SourceMaterial(
                label=source_label,
                text=case_material,
            )
        ],
    )


if __name__ == "__main__":
    unittest.main()
