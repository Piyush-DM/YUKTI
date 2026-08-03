"""The engineering domain -- the HOLD-OUT test.

This domain was written **after** the core was frozen and hashed for the
portability experiment. Nothing in ``choir_prototype/core/`` was consulted,
adjusted, or re-run while writing it.

That matters. Law and medicine were the development set: the core was decoupled
while they were being built, so any fix could have been tuned to them without
anyone noticing. Engineering is the control. If adding it requires zero core
changes, the decoupling generalises rather than fitting the two cases that
motivated it.

``audit.py`` records the core hashes taken before this file existed and compares
them afterwards. The comparison, not this docstring, is the evidence.

Subject: a structural member's fitness against a design code.
"""

from __future__ import annotations

from dataclasses import dataclass

from choir_prototype.core.contracts import Artifact, Finding, Stance, derive_confidence
from choir_prototype.core.domain import Domain, PacketSummary
from choir_prototype.core.ir import (
    Assumption,
    ChoirIR,
    Claim,
    Entity,
    Evidence,
    EvidenceQuality,
    Metadata,
    Relationship,
    RelationshipKind,
    Uncertainty,
)

TOPICS = (
    "load_capacity",
    "fatigue_margin",
    "material_assurance",
    "code_conformance",
    "design_compliance",
)

MINIMUM_SAFETY_FACTOR = 1.5
COMFORTABLE_SAFETY_FACTOR = 2.0
MINIMUM_FATIGUE_RATIO = 1.0
COMFORTABLE_FATIGUE_RATIO = 2.0
FULL_WELD_INSPECTION_PCT = 100.0
PARTIAL_WELD_INSPECTION_PCT = 25.0


@dataclass(frozen=True)
class Reference:
    """A standard, calculation or record relied on."""

    tag: str
    description: str
    kind: str


@dataclass(frozen=True)
class Parameter:
    """One design or as-built parameter."""

    name: str
    value: str
    reference_tags: tuple[str, ...]
    provenance: str


@dataclass(frozen=True)
class Discrepancy:
    """A parameter the record disputes."""

    name: str
    note: str


@dataclass(frozen=True)
class EngineeringPacket:
    """A structural fitness assessment."""

    id: str
    title: str
    asset: str
    component: str
    code_reference: str
    references: tuple[Reference, ...]
    parameters: tuple[Parameter, ...]
    stated_assumptions: tuple[str, ...]
    discrepancies: tuple[Discrepancy, ...]


TRANSLATOR_NAME = "engineering.v0"
IR_VERSION = "choir-ir/0.1"

_KIND_TO_QUALITY = {
    "test": EvidenceQuality.AUDITED,
    "survey": EvidenceQuality.AUDITED,
    "standard": EvidenceQuality.REPORTED,
    "calculation": EvidenceQuality.REPORTED,
    "model": EvidenceQuality.ESTIMATED,
    "assumption": EvidenceQuality.ASSERTED,
}

_PROVENANCE_TO_UNCERTAINTY = {
    "measured": Uncertainty.SETTLED,
    "certified": Uncertainty.SETTLED,
    "calculated": Uncertainty.LIKELY,
    "estimated": Uncertainty.LIKELY,
    "disputed": Uncertainty.DISPUTED,
    "unknown": Uncertainty.UNKNOWN,
}

_CODE_PARAMETERS = frozenset({"code_edition_current", "as_built_survey_available"})


def translate(packet: EngineeringPacket) -> ChoirIR:
    """Map an engineering assessment onto the CHOIR IR. No reasoning here."""
    component_id = "ent-component"
    code_id = "ent-code"

    entities = (
        Entity(
            id=component_id,
            kind="component",
            label=packet.component,
            attributes={"asset": packet.asset},
        ),
        Entity(
            id=code_id,
            kind="standard",
            label=packet.code_reference,
            attributes={"code": packet.code_reference},
        ),
    )

    evidence = tuple(
        Evidence(
            id=reference.tag,
            source=reference.description,
            statement=f"{reference.description} ({reference.kind})",
            quality=_KIND_TO_QUALITY.get(reference.kind, EvidenceQuality.ASSERTED),
        )
        for reference in packet.references
    )

    claims = tuple(
        Claim(
            id=f"clm-{index:03d}",
            subject_id=code_id if parameter.name in _CODE_PARAMETERS else component_id,
            predicate=parameter.name,
            value=parameter.value,
            uncertainty=_PROVENANCE_TO_UNCERTAINTY.get(
                parameter.provenance, Uncertainty.UNKNOWN
            ),
            evidence_ids=parameter.reference_tags,
        )
        for index, parameter in enumerate(packet.parameters, start=1)
    )

    assumptions = tuple(
        Assumption(
            id=f"asm-{index:03d}", statement=statement, basis="stated in assessment"
        )
        for index, statement in enumerate(packet.stated_assumptions, start=1)
    )

    relationships: list[Relationship] = []
    counter = 0
    for claim in claims:
        for tag in claim.evidence_ids:
            counter += 1
            relationships.append(
                Relationship(
                    id=f"rel-{counter:03d}",
                    kind=RelationshipKind.SUPPORTS,
                    source_id=tag,
                    target_id=claim.id,
                )
            )

    by_name = {claim.predicate: claim for claim in claims}
    for discrepancy in packet.discrepancies:
        claim = by_name.get(discrepancy.name)
        if claim is None:
            continue
        counter += 1
        relationships.append(
            Relationship(
                id=f"rel-{counter:03d}",
                kind=RelationshipKind.CONTRADICTS,
                source_id="record-review",
                target_id=claim.id,
                note=discrepancy.note,
            )
        )

    return ChoirIR(
        metadata=Metadata(
            packet_id=packet.id,
            packet_title=packet.title,
            domain="engineering",
            translator=TRANSLATOR_NAME,
            ir_version=IR_VERSION,
        ),
        entities=entities,
        claims=claims,
        evidence=evidence,
        assumptions=assumptions,
        relationships=tuple(relationships),
    )


class CapacityKernel:
    """Reads applied load against allowable capacity."""

    name = "structural_capacity"
    PREDICATES = ("applied_load_kn", "allowable_load_kn", "safety_factor")

    def run(self, ir: ChoirIR) -> Artifact:
        """Assess load capacity and return an artifact."""
        reading = ir.gather(self.PREDICATES)
        findings: list[Finding] = []
        unresolved: list[str] = []
        assumptions: list[str] = []

        applied = reading.number("applied_load_kn")
        allowable = reading.number("allowable_load_kn")

        if applied is None or allowable is None or applied <= 0:
            unresolved.append("Load capacity could not be assessed: loads missing.")
        else:
            ratio = allowable / applied
            assumptions.append(
                "Utilisation is derived as allowable / applied load at the "
                "governing load case only."
            )
            if ratio >= COMFORTABLE_SAFETY_FACTOR:
                stance = Stance.SUPPORTS
            elif ratio >= MINIMUM_SAFETY_FACTOR:
                stance = Stance.CONDITIONAL
            else:
                stance = Stance.OPPOSES
            claim_ids = (
                reading.claims["applied_load_kn"].id,
                reading.claims["allowable_load_kn"].id,
            )
            findings.append(
                Finding(
                    id="cap-utilisation",
                    topic="load_capacity",
                    stance=stance,
                    statement=(
                        f"Derived capacity ratio is {ratio:.2f} against a "
                        f"{MINIMUM_SAFETY_FACTOR:.1f} minimum / "
                        f"{COMFORTABLE_SAFETY_FACTOR:.1f} comfortable threshold."
                    ),
                    claim_ids=claim_ids,
                    evidence_ids=tuple(
                        sorted(
                            set(reading.claims["applied_load_kn"].evidence_ids)
                            | set(reading.claims["allowable_load_kn"].evidence_ids)
                        )
                    ),
                )
            )
            findings.append(
                Finding(
                    id="cap-compliance",
                    topic="design_compliance",
                    stance=stance,
                    statement=f"On capacity the member reads as {stance.value}.",
                    claim_ids=claim_ids,
                )
            )

        for claim in reading.contradicted(ir):
            unresolved.append(
                f"Parameter {claim.id} ({claim.predicate}) is disputed in the "
                "record; this finding is provisional."
            )

        return Artifact(
            kernel_name=self.name,
            findings=tuple(findings),
            evidence_references=tuple(item.id for item in reading.evidence),
            confidence=derive_confidence(
                evidence=reading.evidence,
                expected_inputs=reading.expected,
                found_inputs=reading.found,
                contradiction_count=reading.contradictions,
            ),
            assumptions=tuple(assumptions),
            unresolved_questions=tuple(unresolved),
        )


class FatigueKernel:
    """Reads design fatigue life against expected cycles."""

    name = "fatigue_life"
    PREDICATES = ("fatigue_cycles_design", "fatigue_cycles_expected")

    def run(self, ir: ChoirIR) -> Artifact:
        """Assess fatigue margin and return an artifact."""
        reading = ir.gather(self.PREDICATES)
        findings: list[Finding] = []
        unresolved: list[str] = []

        design = reading.number("fatigue_cycles_design")
        expected = reading.number("fatigue_cycles_expected")

        if design is None or expected is None or expected <= 0:
            unresolved.append("Fatigue margin could not be assessed: cycles missing.")
        else:
            ratio = design / expected
            if ratio >= COMFORTABLE_FATIGUE_RATIO:
                stance = Stance.SUPPORTS
            elif ratio >= MINIMUM_FATIGUE_RATIO:
                stance = Stance.CONDITIONAL
            else:
                stance = Stance.OPPOSES
            claim_ids = (
                reading.claims["fatigue_cycles_design"].id,
                reading.claims["fatigue_cycles_expected"].id,
            )
            findings.append(
                Finding(
                    id="fat-margin",
                    topic="fatigue_margin",
                    stance=stance,
                    statement=(
                        f"Design life covers {ratio:.2f}x expected cycles against a "
                        f"{MINIMUM_FATIGUE_RATIO:.1f}x minimum."
                    ),
                    claim_ids=claim_ids,
                    evidence_ids=tuple(
                        sorted(
                            set(reading.claims["fatigue_cycles_design"].evidence_ids)
                            | set(
                                reading.claims["fatigue_cycles_expected"].evidence_ids
                            )
                        )
                    ),
                )
            )
            findings.append(
                Finding(
                    id="fat-compliance",
                    topic="design_compliance",
                    stance=stance,
                    statement=f"On fatigue the member reads as {stance.value}.",
                    claim_ids=claim_ids,
                )
            )

        return Artifact(
            kernel_name=self.name,
            findings=tuple(findings),
            evidence_references=tuple(item.id for item in reading.evidence),
            confidence=derive_confidence(
                evidence=reading.evidence,
                expected_inputs=reading.expected,
                found_inputs=reading.found,
                contradiction_count=reading.contradictions,
            ),
            assumptions=(),
            unresolved_questions=tuple(unresolved),
        )


class MaterialKernel:
    """Reads material certification and weld inspection coverage."""

    name = "material_assurance"
    PREDICATES = ("material_grade_certified", "weld_inspection_pct")

    def run(self, ir: ChoirIR) -> Artifact:
        """Assess material assurance and return an artifact."""
        reading = ir.gather(self.PREDICATES)
        findings: list[Finding] = []
        unresolved: list[str] = []

        certified = (reading.text("material_grade_certified") or "").lower() == "yes"
        inspection = reading.number("weld_inspection_pct")

        if "material_grade_certified" not in reading.claims and inspection is None:
            unresolved.append("Neither material certification nor weld coverage given.")
        else:
            signals: list[str] = []
            claim_ids: list[str] = []
            evidence_ids: set[str] = set()
            stance = Stance.SUPPORTS

            claim = reading.claim("material_grade_certified")
            if claim is not None:
                claim_ids.append(claim.id)
                evidence_ids.update(claim.evidence_ids)
                signals.append(
                    "material grade certified"
                    if certified
                    else "material grade NOT certified"
                )
                if not certified:
                    stance = Stance.OPPOSES

            if inspection is not None:
                claim = reading.claims["weld_inspection_pct"]
                claim_ids.append(claim.id)
                evidence_ids.update(claim.evidence_ids)
                signals.append(f"{inspection:.0f}% weld inspection coverage")
                if inspection < PARTIAL_WELD_INSPECTION_PCT:
                    stance = Stance.OPPOSES
                elif (
                    inspection < FULL_WELD_INSPECTION_PCT and stance is Stance.SUPPORTS
                ):
                    stance = Stance.CONDITIONAL

            findings.append(
                Finding(
                    id="mat-assurance",
                    topic="material_assurance",
                    stance=stance,
                    statement=f"Material assurance: {'; '.join(signals)}.",
                    claim_ids=tuple(claim_ids),
                    evidence_ids=tuple(sorted(evidence_ids)),
                )
            )
            findings.append(
                Finding(
                    id="mat-compliance",
                    topic="design_compliance",
                    stance=stance,
                    statement=f"On material assurance the member reads as {stance.value}.",
                    claim_ids=tuple(claim_ids),
                )
            )

        return Artifact(
            kernel_name=self.name,
            findings=tuple(findings),
            evidence_references=tuple(item.id for item in reading.evidence),
            confidence=derive_confidence(
                evidence=reading.evidence,
                expected_inputs=reading.expected,
                found_inputs=reading.found,
                contradiction_count=reading.contradictions,
            ),
            assumptions=(),
            unresolved_questions=tuple(unresolved),
        )


class CodeConformanceKernel:
    """Reads whether the assessment is against a current code and as-built state."""

    name = "code_conformance"
    PREDICATES = (
        "code_edition_current",
        "as_built_survey_available",
        "corrosion_allowance_mm",
    )

    def run(self, ir: ChoirIR) -> Artifact:
        """Assess code conformance and return an artifact."""
        reading = ir.gather(self.PREDICATES)
        findings: list[Finding] = []
        unresolved: list[str] = []

        current = (reading.text("code_edition_current") or "").lower() == "yes"
        survey = (reading.text("as_built_survey_available") or "").lower() == "yes"

        if "code_edition_current" not in reading.claims:
            unresolved.append("The code edition used was not stated.")
        else:
            claim_ids = [reading.claims["code_edition_current"].id]
            evidence_ids = set(reading.claims["code_edition_current"].evidence_ids)
            survey_claim = reading.claim("as_built_survey_available")
            if survey_claim is not None:
                claim_ids.append(survey_claim.id)
                evidence_ids.update(survey_claim.evidence_ids)

            findings.append(
                Finding(
                    id="code-conformance",
                    topic="code_conformance",
                    stance=Stance.SUPPORTS
                    if current and survey
                    else Stance.CONDITIONAL,
                    statement=(
                        f"Code edition {'is' if current else 'is not'} current; "
                        f"as-built survey {'is' if survey else 'is not'} available."
                    ),
                    claim_ids=tuple(claim_ids),
                    evidence_ids=tuple(sorted(evidence_ids)),
                )
            )

        if "corrosion_allowance_mm" not in reading.claims:
            unresolved.append("Corrosion allowance was not stated.")

        return Artifact(
            kernel_name=self.name,
            findings=tuple(findings),
            evidence_references=tuple(item.id for item in reading.evidence),
            confidence=derive_confidence(
                evidence=reading.evidence,
                expected_inputs=reading.expected,
                found_inputs=reading.found,
                contradiction_count=reading.contradictions,
            ),
            assumptions=(),
            unresolved_questions=tuple(unresolved),
        )


def all_kernels() -> tuple[
    CapacityKernel, FatigueKernel, MaterialKernel, CodeConformanceKernel
]:
    """Return every kernel, in fixed dispatch order."""
    return (
        CapacityKernel(),
        FatigueKernel(),
        MaterialKernel(),
        CodeConformanceKernel(),
    )


_REFERENCES = (
    Reference("STD-CODE", "Design code, referenced edition", "standard"),
    Reference("CALC-PACK", "Structural calculation package", "calculation"),
    Reference("MTR-CERT", "Mill test report for the member", "test"),
    Reference("NDT-REPORT", "Non-destructive weld testing report", "test"),
    Reference("SURVEY-2025", "As-built dimensional survey", "survey"),
    Reference("LOAD-MODEL", "Traffic loading model", "model"),
)


BRIDGE_MEMBER = EngineeringPacket(
    id="bridge-hanger-assessment",
    title="Bridge hanger H-14 -- fitness assessment",
    asset="River crossing, span 3",
    component="Hanger H-14",
    code_reference="Design code, 2021 edition",
    references=_REFERENCES,
    parameters=(
        Parameter("applied_load_kn", "820", ("CALC-PACK", "LOAD-MODEL"), "calculated"),
        Parameter("allowable_load_kn", "1390", ("STD-CODE", "CALC-PACK"), "calculated"),
        Parameter("safety_factor", "1.5", ("STD-CODE",), "certified"),
        Parameter("fatigue_cycles_design", "2200000", ("CALC-PACK",), "calculated"),
        Parameter("fatigue_cycles_expected", "1800000", ("LOAD-MODEL",), "disputed"),
        Parameter("material_grade_certified", "yes", ("MTR-CERT",), "certified"),
        Parameter("weld_inspection_pct", "60", ("NDT-REPORT",), "measured"),
        Parameter("code_edition_current", "yes", ("STD-CODE",), "certified"),
        Parameter("as_built_survey_available", "yes", ("SURVEY-2025",), "measured"),
        Parameter("corrosion_allowance_mm", "2.0", ("SURVEY-2025",), "measured"),
    ),
    stated_assumptions=(
        "The governing load case is the one modelled; others were not checked.",
        "Corrosion is assumed uniform across the member.",
    ),
    discrepancies=(
        Discrepancy(
            name="fatigue_cycles_expected",
            note=(
                "The traffic model predates the 2024 route change; the operator's "
                "count suggests a materially higher cycle rate."
            ),
        ),
    ),
)


PACKETS = {BRIDGE_MEMBER.id: BRIDGE_MEMBER}


def describe(packet: EngineeringPacket) -> PacketSummary:
    """Tell the pipeline what it needs to know about an engineering assessment."""
    return PacketSummary(
        packet_id=packet.id,
        title=packet.title,
        record_count=len(packet.parameters),
        notes=(
            f"{len(packet.references)} reference(s)",
            f"{len(packet.parameters)} parameter(s)",
            f"{len(packet.stated_assumptions)} stated assumption(s)",
            f"{len(packet.discrepancies)} discrepancy/discrepancies",
        ),
    )


DOMAIN = Domain(
    name="engineering",
    description="Structural fitness assessment against a design code",
    translate=translate,
    describe=describe,
    kernels=all_kernels(),
    topics=TOPICS,
    packets=dict(PACKETS),
)
