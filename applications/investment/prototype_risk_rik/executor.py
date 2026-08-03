"""Execution boundary for the prototype Risk RIK vertical slice."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from applications.investment.prototype_risk_rik.contracts import (
    RiskRikArtifact,
    RiskRikExecutionError,
    RiskRikExecutionRequest,
    SourceMaterial,
    new_run_id,
    utc_now_iso,
)
from applications.investment.prototype_risk_rik.provider import ModelAdapter


def execute_risk_rik(
    request: RiskRikExecutionRequest,
    adapter: ModelAdapter,
) -> RiskRikArtifact:
    """Run the prototype Risk RIK and validate the structured artifact."""
    run_id = new_run_id()
    prompt = build_risk_rik_prompt(request, run_id)
    raw_output = adapter.generate_structured(prompt, risk_rik_json_schema())
    raw_output.setdefault("run_id", run_id)
    raw_output.setdefault("rik_identity", "Risk RIK")
    raw_output.setdefault("generated_at", utc_now_iso())
    raw_output.setdefault("prototype_contract", "investment.prototype.risk_rik.v1")

    try:
        return RiskRikArtifact.model_validate(raw_output)
    except ValidationError as exc:
        raise RiskRikExecutionError(
            "Risk RIK returned malformed structured output."
        ) from exc


def build_risk_rik_prompt(request: RiskRikExecutionRequest, run_id: str) -> str:
    """Build the narrow prompt for the prototype Risk RIK."""
    source_labels = [source.label for source in request.source_materials]
    return "\n\n".join(
        (
            f"Prototype run id: {run_id}",
            f"Case title: {request.case_title}",
            "Task: Identify investment risks only. Do not produce a final "
            "investment recommendation, synthesis, debate, or institutional "
            "decision.",
            "Evidence rule: You may reference only explicitly supplied source "
            "labels. If a risk is not tied to a supplied source label, mark its "
            "evidence reference as unsupported or unlinked. Do not invent EV-* "
            "identifiers or provenance.",
            f"Available source labels: {', '.join(source_labels) or 'none'}",
            "Case material:",
            request.case_material,
            "Labeled source materials:",
            format_sources(request.source_materials),
        )
    )


def format_sources(sources: list[SourceMaterial]) -> str:
    """Format labeled source material for the model prompt."""
    if not sources:
        return "No labeled source material supplied."
    return "\n\n".join(f"[{source.label}]\n{source.text}" for source in sources)


def risk_rik_json_schema() -> dict[str, Any]:
    """Return the strict JSON schema used for model structured output."""
    schema = RiskRikArtifact.model_json_schema()
    _forbid_extra_properties(schema)
    return schema


def _forbid_extra_properties(value: Any) -> None:
    if isinstance(value, dict):
        if value.get("type") == "object":
            value.setdefault("additionalProperties", False)
        for child in value.values():
            _forbid_extra_properties(child)
    elif isinstance(value, list):
        for child in value:
            _forbid_extra_properties(child)
