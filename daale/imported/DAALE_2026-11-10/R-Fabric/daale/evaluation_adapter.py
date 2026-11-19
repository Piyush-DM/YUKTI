"""Provider-neutral contract for isolated model evaluations.

This module is deliberately not imported by the live pipeline and contains no
provider implementation. It gives a future evaluation adapter one typed
request/response boundary without changing DAALE execution semantics.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol

from .execution_contract import FailureMode


@dataclass(frozen=True)
class AdapterRequest:
    provider_id: str
    requested_model: str
    purpose: str
    messages: tuple[Mapping[str, str], ...]
    json_schema: Mapping[str, Any]
    reasoning_effort: str | None
    max_output_tokens: int
    timeout_seconds: float

    def __post_init__(self):
        for field_name in ("provider_id", "requested_model", "purpose"):
            if not getattr(self, field_name).strip():
                raise ValueError(f"{field_name} must be non-empty")
        if self.max_output_tokens < 1:
            raise ValueError("max_output_tokens must be positive")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if not self.messages:
            raise ValueError("messages must not be empty")


@dataclass(frozen=True)
class AdapterUsage:
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    provider_fields: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class AdapterResponse:
    provider_id: str
    requested_model: str
    served_model: str
    output: Mapping[str, Any]
    request_id: str | None
    usage: AdapterUsage
    attempts: int
    output_token_ceiling: int
    structured_output_mode: str
    reasoning_effort_requested: str | None
    reasoning_effort_served: str | None = None

    def __post_init__(self):
        for field_name in ("provider_id", "requested_model", "served_model"):
            if not getattr(self, field_name).strip():
                raise ValueError(f"{field_name} must be non-empty")
        if self.attempts < 1:
            raise ValueError("attempts must be at least one")
        if self.output_token_ceiling < 1:
            raise ValueError("output_token_ceiling must be positive")
        if self.structured_output_mode not in {
            "json-schema", "json-object", "validated-json-text"
        }:
            raise ValueError("unsupported structured_output_mode")


@dataclass(frozen=True)
class AdapterFailure(Exception):
    provider_id: str
    requested_model: str
    failure_mode: FailureMode
    message: str
    attempts: int
    status_code: int | None = None
    retry_after_seconds: float | None = None
    request_id: str | None = None
    usage: AdapterUsage | None = None

    def __str__(self):
        return self.message


class EvaluationAdapter(Protocol):
    """One-model adapter contract; routing and policy remain outside the adapter."""

    def complete_json(self, request: AdapterRequest) -> AdapterResponse:
        """Return schema-constrained output or raise a classified AdapterFailure."""
        ...


__all__ = [
    "AdapterFailure",
    "AdapterRequest",
    "AdapterResponse",
    "AdapterUsage",
    "EvaluationAdapter",
]
