"""Minimal model adapter boundary for the prototype Risk RIK.

This is not a generalized provider framework. It exists only to keep the Risk
RIK execution boundary from being coupled throughout the prototype code to one
model API.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
import re
from typing import Any, Protocol

import httpx


class ProviderConfigurationError(Exception):
    """Raised when the prototype model provider is not configured."""


class ModelAdapter(Protocol):
    """Minimal adapter contract required by the prototype Risk RIK."""

    def generate_structured(
        self, prompt: str, schema: dict[str, Any]
    ) -> dict[str, Any]:
        """Return model output as a JSON-compatible dictionary."""


@dataclass(frozen=True)
class ProviderStatus:
    """Configuration status exposed by the prototype development server."""

    provider: str
    mode: str
    configured: bool
    requires_credentials: bool
    description: str


@dataclass(frozen=True)
class DeterministicRiskRikAdapter:
    """Rule-based development provider for exercising the execution path.

    This adapter is intentionally simple. It is deterministic test machinery,
    not model reasoning and not a DAALE reasoning engine.
    """

    def generate_structured(
        self, prompt: str, schema: dict[str, Any]
    ) -> dict[str, Any]:
        """Return a valid structured artifact derived from the prompt."""
        del schema
        normalized_prompt = _normalize_prompt_for_determinism(prompt)
        digest = hashlib.sha256(normalized_prompt.encode("utf-8")).hexdigest()
        source_labels = _extract_source_labels(prompt)
        material = _extract_case_material(prompt)
        matched_risks = _match_risk_signals(material)
        evidence_references = _build_evidence_references(source_labels, matched_risks)
        leading_risk = matched_risks[0]

        return {
            "rik_identity": "Risk RIK",
            "run_id": f"risk-rik-deterministic-{digest[:16]}",
            "primary_conclusion": (
                "Deterministic development output: "
                f"{leading_risk.name.lower()} is the leading risk signal in "
                "the supplied prototype material."
            ),
            "qualitative_confidence": _confidence_for(matched_risks),
            "identified_risks": [
                {
                    "name": risk.name,
                    "severity": risk.severity,
                    "description": risk.description,
                    "mitigation_or_condition": risk.condition,
                    "evidence_references": evidence_references,
                }
                for risk in matched_risks
            ],
            "relevant_propositions": [
                {
                    "proposition": risk.proposition,
                    "position": risk.position,
                    "reasoning_summary": (
                        "Deterministic development rule matched prototype "
                        f"input terms for {risk.name.lower()}."
                    ),
                }
                for risk in matched_risks
            ],
            "evidence_references": evidence_references,
            "key_assumptions": [
                "This is deterministic development output, not live model reasoning.",
                "No source provenance was verified beyond supplied prototype labels.",
                "Keyword matches are only used to exercise the execution boundary.",
            ],
            "strongest_objection": (
                "The deterministic provider may overstate or miss risks because "
                "it uses simple keyword rules rather than model analysis."
            ),
            "information_that_would_change_position": [
                f"Labeled source material resolving {leading_risk.name.lower()}.",
                "A live model provider or approved analysis layer replacing the "
                "development provider.",
            ],
            "unresolved_questions": [
                f"What diligence evidence confirms or reduces {risk.name.lower()}?"
                for risk in matched_risks[:3]
            ],
            "generated_at": "2000-01-01T00:00:00Z",
            "prototype_contract": "investment.prototype.risk_rik.v1",
        }


@dataclass(frozen=True)
class OpenAIResponsesAdapter:
    """OpenAI Responses API adapter for prototype structured output."""

    api_key: str
    model: str
    endpoint: str = "https://api.openai.com/v1/responses"
    timeout_seconds: float = 60.0

    def generate_structured(
        self, prompt: str, schema: dict[str, Any]
    ) -> dict[str, Any]:
        """Request strict JSON-schema output from the configured model."""
        payload = {
            "model": self.model,
            "input": [
                {
                    "role": "system",
                    "content": (
                        "You are the Risk RIK for a prototype investment workflow. "
                        "Return only the requested structured artifact. Do not invent "
                        "evidence provenance. Evidence references must use only source "
                        "labels supplied by the user or be marked unsupported/unlinked."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "risk_rik_artifact",
                    "schema": schema,
                    "strict": True,
                }
            },
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(self.endpoint, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        return _extract_json_object(data)


def configured_adapter_from_environment(
    environ: dict[str, str] | None = None,
) -> ModelAdapter:
    """Build the configured prototype model adapter from environment variables."""
    environment = environ or os.environ
    provider = environment.get("YUKTI_PROTOTYPE_RISK_RIK_PROVIDER", "").strip().lower()
    if not provider:
        raise ProviderConfigurationError(
            "Set YUKTI_PROTOTYPE_RISK_RIK_PROVIDER to deterministic or openai."
        )
    if provider == "deterministic":
        return DeterministicRiskRikAdapter()
    if provider != "openai":
        raise ProviderConfigurationError(
            "Unsupported prototype provider. Supported values: deterministic, openai."
        )

    api_key = environment.get("OPENAI_API_KEY", "").strip()
    model = environment.get("YUKTI_PROTOTYPE_RISK_RIK_MODEL", "").strip()
    endpoint = environment.get(
        "YUKTI_PROTOTYPE_RISK_RIK_ENDPOINT",
        "https://api.openai.com/v1/responses",
    ).strip()

    missing = [
        name
        for name, value in (
            ("OPENAI_API_KEY", api_key),
            ("YUKTI_PROTOTYPE_RISK_RIK_MODEL", model),
        )
        if not value
    ]
    if missing:
        raise ProviderConfigurationError(
            f"Missing required prototype model configuration: {', '.join(missing)}"
        )

    return OpenAIResponsesAdapter(api_key=api_key, model=model, endpoint=endpoint)


def provider_status_from_environment(
    environ: dict[str, str] | None = None,
) -> ProviderStatus:
    """Return prototype provider status without exposing secrets."""
    environment = environ or os.environ
    provider = environment.get("YUKTI_PROTOTYPE_RISK_RIK_PROVIDER", "").strip().lower()
    if not provider:
        return ProviderStatus(
            provider="unconfigured",
            mode="not configured",
            configured=False,
            requires_credentials=False,
            description=(
                "Set YUKTI_PROTOTYPE_RISK_RIK_PROVIDER to deterministic or openai."
            ),
        )

    if provider == "deterministic":
        return ProviderStatus(
            provider="deterministic",
            mode="deterministic development execution",
            configured=True,
            requires_credentials=False,
            description=(
                "Rule-based provider for exercising the prototype execution path; "
                "not live model reasoning."
            ),
        )

    if provider == "openai":
        model_present = bool(
            environment.get("YUKTI_PROTOTYPE_RISK_RIK_MODEL", "").strip()
        )
        key_present = bool(environment.get("OPENAI_API_KEY", "").strip())
        return ProviderStatus(
            provider="openai",
            mode="live model execution",
            configured=model_present and key_present,
            requires_credentials=True,
            description=(
                "OpenAI Responses API provider using structured output validation."
            ),
        )

    return ProviderStatus(
        provider=provider,
        mode="unsupported",
        configured=False,
        requires_credentials=False,
        description="Unsupported prototype provider.",
    )


def _extract_json_object(response_data: dict[str, Any]) -> dict[str, Any]:
    if "output_parsed" in response_data and isinstance(
        response_data["output_parsed"], dict
    ):
        return response_data["output_parsed"]

    output_text = response_data.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return _loads_object(output_text)

    for output_item in response_data.get("output", []):
        if not isinstance(output_item, dict):
            continue
        for content in output_item.get("content", []):
            if not isinstance(content, dict):
                continue
            text = content.get("text")
            if isinstance(text, str) and text.strip():
                return _loads_object(text)

    raise ValueError("Model response did not contain structured JSON output.")


def _loads_object(text: str) -> dict[str, Any]:
    loaded = json.loads(text)
    if not isinstance(loaded, dict):
        raise TypeError("Structured model output must be a JSON object.")
    return loaded


@dataclass(frozen=True)
class _RiskSignal:
    name: str
    severity: str
    description: str
    condition: str
    proposition: str
    position: str
    keywords: tuple[str, ...]


_RISK_SIGNALS = (
    _RiskSignal(
        name="Customer concentration",
        severity="High",
        description=(
            "The supplied material indicates possible dependence on a limited "
            "customer or revenue base."
        ),
        condition="Require concentration reporting and signed diversification evidence.",
        proposition="Customer concentration is acceptable without further conditions.",
        position="OPPOSES",
        keywords=("concentration", "top three", "top 3", "single customer"),
    ),
    _RiskSignal(
        name="Implementation margin pressure",
        severity="Medium",
        description=(
            "The supplied material indicates services, deployment, or margin "
            "execution pressure."
        ),
        condition="Require cohort margin reporting and evidence of stabilized delivery.",
        proposition="Implementation economics are already sufficiently de-risked.",
        position="CONDITIONAL",
        keywords=("margin", "implementation", "deployment", "services"),
    ),
    _RiskSignal(
        name="Regulatory or procurement timing",
        severity="Medium",
        description=(
            "The supplied material indicates timing exposure tied to regulation, "
            "budgets, or procurement."
        ),
        condition="Require a downside case for delayed approvals or procurement slippage.",
        proposition="Regulatory and procurement timing fully support the plan.",
        position="CONDITIONAL",
        keywords=("regulatory", "procurement", "budget", "approval", "state"),
    ),
    _RiskSignal(
        name="Valuation sensitivity",
        severity="Medium",
        description=(
            "The supplied material indicates valuation may depend on unresolved "
            "growth, ARR, or multiple assumptions."
        ),
        condition="Require valuation cases tied to verified operating evidence.",
        proposition="The valuation is justified without additional downside cases.",
        position="CONDITIONAL",
        keywords=("valuation", "multiple", "arr", "growth"),
    ),
    _RiskSignal(
        name="Governance and reporting readiness",
        severity="Medium",
        description=(
            "The supplied material indicates governance, board, cyber, or reporting "
            "controls may be incomplete."
        ),
        condition="Require board-ready reporting rights and risk-monitoring cadence.",
        proposition="Governance controls are institutional-grade as supplied.",
        position="CONDITIONAL",
        keywords=("governance", "board", "reporting", "cyber", "controls"),
    ),
    _RiskSignal(
        name="Revenue retention durability",
        severity="Low",
        description=(
            "The supplied material references retention, churn, renewal, or revenue "
            "durability signals requiring confirmation."
        ),
        condition="Require verified retention and renewal evidence.",
        proposition="Revenue durability is fully proven by the supplied material.",
        position="UNRESOLVED",
        keywords=("retention", "churn", "renewal", "revenue"),
    ),
    _RiskSignal(
        name="Liquidity or runway pressure",
        severity="Medium",
        description=(
            "The supplied material indicates cash, burn, liquidity, or runway may "
            "need explicit diligence."
        ),
        condition="Require runway and cash-burn reporting before relying on the plan.",
        proposition="Liquidity risk is immaterial to the case.",
        position="CONDITIONAL",
        keywords=("cash", "burn", "liquidity", "runway"),
    ),
)

_DEFAULT_RISK_SIGNAL = _RiskSignal(
    name="Diligence completeness",
    severity="Low",
    description=(
        "The deterministic provider did not match a specific risk keyword, so it "
        "flags diligence completeness as the development output."
    ),
    condition="Supply labeled case evidence covering the key investment risks.",
    proposition="The supplied material is sufficient for risk evaluation.",
    position="UNRESOLVED",
    keywords=(),
)


def _normalize_prompt_for_determinism(prompt: str) -> str:
    lines = [
        line for line in prompt.splitlines() if not line.startswith("Prototype run id:")
    ]
    return "\n".join(lines).strip()


def _extract_source_labels(prompt: str) -> list[str]:
    match = re.search(r"^Available source labels:\s*(.*)$", prompt, re.MULTILINE)
    if not match:
        return []
    raw_labels = match.group(1).strip()
    if not raw_labels or raw_labels == "none":
        return []
    return [label.strip() for label in raw_labels.split(",") if label.strip()]


def _extract_case_material(prompt: str) -> str:
    marker = "Case material:\n"
    source_marker = "\n\nLabeled source materials:\n"
    if marker not in prompt:
        return prompt
    after_marker = prompt.split(marker, maxsplit=1)[1]
    if source_marker not in after_marker:
        return after_marker
    case_material, source_materials = after_marker.split(source_marker, maxsplit=1)
    return f"{case_material}\n\n{source_materials}"


def _match_risk_signals(material: str) -> list[_RiskSignal]:
    material_lower = material.lower()
    matched = [
        signal
        for signal in _RISK_SIGNALS
        if any(keyword in material_lower for keyword in signal.keywords)
    ]
    return matched or [_DEFAULT_RISK_SIGNAL]


def _build_evidence_references(
    source_labels: list[str],
    risks: list[_RiskSignal],
) -> list[dict[str, str]]:
    if not source_labels:
        return []

    return [
        {
            "source_label": label,
            "relevance": (
                "Supplied prototype source label referenced by deterministic "
                f"development output for {risks[0].name.lower()}."
            ),
            "support_status": "supported",
        }
        for label in source_labels
    ]


def _confidence_for(risks: list[_RiskSignal]) -> str:
    high_count = sum(1 for risk in risks if risk.severity == "High")
    if high_count:
        return "Moderate"
    if len(risks) >= 3:
        return "Moderate"
    return "Low"
