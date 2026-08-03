"""Prototype-only structured contracts for the Risk RIK vertical slice.

These schemas are intentionally scoped to the investment prototype. They are
not canonical CHOIR or DAALE architecture contracts.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class QualitativeConfidence(StrEnum):
    """Allowed qualitative confidence values for prototype Risk RIK output."""

    HIGH = "High"
    MODERATE = "Moderate"
    LOW = "Low"
    CONTESTED = "Contested"


class EvidenceReference(BaseModel):
    """A reference to explicitly supplied source material."""

    model_config = ConfigDict(extra="forbid")

    source_label: str = Field(min_length=1)
    relevance: str = Field(min_length=1)
    support_status: Literal["supported", "unsupported", "unlinked"]


class IdentifiedRisk(BaseModel):
    """A risk identified by the prototype Risk RIK."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    severity: Literal["Low", "Medium", "High"]
    description: str = Field(min_length=1)
    mitigation_or_condition: str = Field(min_length=1)
    evidence_references: list[EvidenceReference] = Field(default_factory=list)


class RelevantProposition(BaseModel):
    """A proposition considered by the prototype Risk RIK."""

    model_config = ConfigDict(extra="forbid")

    proposition: str = Field(min_length=1)
    position: Literal["SUPPORTS", "OPPOSES", "CONDITIONAL", "UNRESOLVED"]
    reasoning_summary: str = Field(min_length=1)


class RiskRikArtifact(BaseModel):
    """Validated structured artifact returned by the prototype Risk RIK."""

    model_config = ConfigDict(extra="forbid")

    rik_identity: Literal["Risk RIK"]
    run_id: str = Field(min_length=1)
    primary_conclusion: str = Field(min_length=1)
    qualitative_confidence: QualitativeConfidence
    identified_risks: Annotated[list[IdentifiedRisk], Field(min_length=1)]
    relevant_propositions: Annotated[list[RelevantProposition], Field(min_length=1)]
    evidence_references: list[EvidenceReference] = Field(default_factory=list)
    key_assumptions: Annotated[list[str], Field(min_length=1)]
    strongest_objection: str = Field(min_length=1)
    information_that_would_change_position: Annotated[list[str], Field(min_length=1)]
    unresolved_questions: Annotated[list[str], Field(min_length=1)]
    generated_at: str = Field(min_length=1)
    prototype_contract: Literal["investment.prototype.risk_rik.v1"]

    @field_validator("generated_at")
    @classmethod
    def validate_generated_at(cls, value: str) -> str:
        """Require ISO-like timestamp strings."""
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return value


class SourceMaterial(BaseModel):
    """A user-supplied labeled source block for the prototype execution."""

    model_config = ConfigDict(extra="forbid")

    label: str = Field(min_length=1)
    text: str = Field(min_length=1)


class RiskRikExecutionRequest(BaseModel):
    """Input accepted by the prototype Risk RIK endpoint."""

    model_config = ConfigDict(extra="forbid")

    case_title: str = Field(min_length=1)
    case_material: str = Field(min_length=1)
    source_materials: list[SourceMaterial] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_material_or_sources(self) -> RiskRikExecutionRequest:
        """Ensure there is material for the model to evaluate."""
        if self.case_material.strip():
            return self
        if any(source.text.strip() for source in self.source_materials):
            return self
        msg = "case_material or source_materials must contain text"
        raise ValueError(msg)


class RiskRikExecutionError(Exception):
    """Raised when the prototype Risk RIK cannot return a valid artifact."""


def new_run_id() -> str:
    """Create a prototype run identifier."""
    return f"risk-rik-run-{uuid4()}"


def utc_now_iso() -> str:
    """Return a UTC timestamp for generated artifacts."""
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")
