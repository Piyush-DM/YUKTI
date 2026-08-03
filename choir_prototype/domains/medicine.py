"""The medicine domain.

A treatment-suitability assessment. One file: packet shape, translator, kernels,
topic vocabulary, and the ``Domain`` binding.

Nothing in ``choir_prototype/core/`` was changed to add this domain.

The packet shape differs again: this one has *observations* and *guidance*, not
data points and authorities. As with law, the translator absorbs the difference.
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
    "renal_safety",
    "interaction_risk",
    "evidence_quality",
    "monitoring_capacity",
    "treatment_suitability",
)

# --- Renal thresholds (mL/min/1.73m2) ---------------------------------------
NORMAL_EGFR = 60.0
IMPAIRED_EGFR = 30.0

# --- Interaction thresholds -------------------------------------------------
INTERACTION_CAUTION_COUNT = 3

# --- Evidence grading -------------------------------------------------------
STRONG_GUIDELINE_GRADES = frozenset({"a"})
ACCEPTABLE_GUIDELINE_GRADES = frozenset({"a", "b"})
STRONG_TRIAL_LEVEL = 2.0


# ---------------------------------------------------------------------------
# Packet shape
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Guidance:
    """A source of clinical evidence or record."""

    reference: str
    description: str
    basis: str


@dataclass(frozen=True)
class Observation:
    """One clinical observation, with its sources."""

    parameter: str
    value: str
    guidance_references: tuple[str, ...]
    reliability: str


@dataclass(frozen=True)
class ConflictingRecord:
    """An observation the record contradicts elsewhere."""

    parameter: str
    note: str


@dataclass(frozen=True)
class ClinicalPacket:
    """A treatment-suitability referral."""

    id: str
    title: str
    patient_ref: str
    proposed_treatment: str
    care_setting: str
    guidance: tuple[Guidance, ...]
    observations: tuple[Observation, ...]
    stated_assumptions: tuple[str, ...]
    conflicting_records: tuple[ConflictingRecord, ...]


# ---------------------------------------------------------------------------
# Translation
# ---------------------------------------------------------------------------

TRANSLATOR_NAME = "medicine.v0"
IR_VERSION = "choir-ir/0.1"

_BASIS_TO_QUALITY = {
    "trial": EvidenceQuality.AUDITED,
    "laboratory": EvidenceQuality.AUDITED,
    "guideline": EvidenceQuality.REPORTED,
    "chart": EvidenceQuality.REPORTED,
    "consensus": EvidenceQuality.ESTIMATED,
    "history": EvidenceQuality.ASSERTED,
}

_RELIABILITY_TO_UNCERTAINTY = {
    "measured": Uncertainty.SETTLED,
    "documented": Uncertainty.LIKELY,
    "reported": Uncertainty.LIKELY,
    "conflicting": Uncertainty.DISPUTED,
    "unknown": Uncertainty.UNKNOWN,
}

_TREATMENT_PARAMETERS = frozenset(
    {"guideline_grade", "trial_evidence_level", "interacting_drug_count"}
)


def translate(packet: ClinicalPacket) -> ChoirIR:
    """Map a clinical referral onto the CHOIR IR. No reasoning happens here."""
    patient_id = "ent-patient"
    treatment_id = "ent-treatment"

    entities = (
        Entity(
            id=patient_id,
            kind="patient",
            label=packet.patient_ref,
            attributes={"setting": packet.care_setting},
        ),
        Entity(
            id=treatment_id,
            kind="treatment",
            label=packet.proposed_treatment,
            attributes={"setting": packet.care_setting},
        ),
    )

    evidence = tuple(
        Evidence(
            id=item.reference,
            source=item.description,
            statement=f"{item.description} ({item.basis})",
            quality=_BASIS_TO_QUALITY.get(item.basis, EvidenceQuality.ASSERTED),
        )
        for item in packet.guidance
    )

    claims = tuple(
        Claim(
            id=f"clm-{index:03d}",
            subject_id=(
                treatment_id
                if observation.parameter in _TREATMENT_PARAMETERS
                else patient_id
            ),
            predicate=observation.parameter,
            value=observation.value,
            uncertainty=_RELIABILITY_TO_UNCERTAINTY.get(
                observation.reliability, Uncertainty.UNKNOWN
            ),
            evidence_ids=observation.guidance_references,
        )
        for index, observation in enumerate(packet.observations, start=1)
    )

    assumptions = tuple(
        Assumption(
            id=f"asm-{index:03d}", statement=statement, basis="stated in referral"
        )
        for index, statement in enumerate(packet.stated_assumptions, start=1)
    )

    relationships: list[Relationship] = []
    counter = 0
    for claim in claims:
        for reference in claim.evidence_ids:
            counter += 1
            relationships.append(
                Relationship(
                    id=f"rel-{counter:03d}",
                    kind=RelationshipKind.SUPPORTS,
                    source_id=reference,
                    target_id=claim.id,
                )
            )

    by_parameter = {claim.predicate: claim for claim in claims}
    for conflict in packet.conflicting_records:
        claim = by_parameter.get(conflict.parameter)
        if claim is None:
            continue
        counter += 1
        relationships.append(
            Relationship(
                id=f"rel-{counter:03d}",
                kind=RelationshipKind.CONTRADICTS,
                source_id="record-review",
                target_id=claim.id,
                note=conflict.note,
            )
        )

    return ChoirIR(
        metadata=Metadata(
            packet_id=packet.id,
            packet_title=packet.title,
            domain="medicine",
            translator=TRANSLATOR_NAME,
            ir_version=IR_VERSION,
        ),
        entities=entities,
        claims=claims,
        evidence=evidence,
        assumptions=assumptions,
        relationships=tuple(relationships),
    )


# ---------------------------------------------------------------------------
# Kernels
# ---------------------------------------------------------------------------


class RenalSafetyKernel:
    """Reads renal function against the proposed treatment."""

    name = "renal_safety"
    PREDICATES = ("egfr_ml_min", "on_dialysis", "age_years")

    def run(self, ir: ChoirIR) -> Artifact:
        """Assess renal safety and return an artifact."""
        reading = ir.gather(self.PREDICATES)
        findings: list[Finding] = []
        unresolved: list[str] = []

        egfr = reading.number("egfr_ml_min")
        dialysis = (reading.text("on_dialysis") or "").lower() == "yes"

        if egfr is None:
            unresolved.append("No eGFR was recorded, so renal safety is unassessed.")
        else:
            claim = reading.claims["egfr_ml_min"]
            if dialysis:
                stance = Stance.OPPOSES
                text = f"eGFR {egfr:.0f} with the patient on dialysis"
            elif egfr >= NORMAL_EGFR:
                stance = Stance.SUPPORTS
                text = f"eGFR {egfr:.0f} is within the normal range"
            elif egfr >= IMPAIRED_EGFR:
                stance = Stance.CONDITIONAL
                text = f"eGFR {egfr:.0f} indicates moderate impairment"
            else:
                stance = Stance.OPPOSES
                text = f"eGFR {egfr:.0f} indicates severe impairment"

            findings.append(
                Finding(
                    id="renal-function",
                    topic="renal_safety",
                    stance=stance,
                    statement=(
                        f"{text} against a {NORMAL_EGFR:.0f} normal / "
                        f"{IMPAIRED_EGFR:.0f} severe threshold."
                    ),
                    claim_ids=(claim.id,),
                    evidence_ids=claim.evidence_ids,
                )
            )
            findings.append(
                Finding(
                    id="renal-suitability",
                    topic="treatment_suitability",
                    stance=stance,
                    statement=f"On renal grounds the treatment reads as {stance.value}.",
                    claim_ids=(claim.id,),
                )
            )

        for claim in reading.contradicted(ir):
            unresolved.append(
                f"Observation {claim.id} ({claim.predicate}) conflicts with another "
                "record entry; this finding is provisional."
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


class InteractionSafetyKernel:
    """Reads allergy history and drug interactions."""

    name = "interaction_safety"
    PREDICATES = (
        "interacting_drug_count",
        "documented_allergy",
        "prior_adverse_reaction",
    )

    def run(self, ir: ChoirIR) -> Artifact:
        """Assess interaction and allergy risk and return an artifact."""
        reading = ir.gather(self.PREDICATES)
        findings: list[Finding] = []
        unresolved: list[str] = []

        interactions = reading.number("interacting_drug_count")
        allergy = (reading.text("documented_allergy") or "").lower() == "yes"
        prior = (reading.text("prior_adverse_reaction") or "").lower() == "yes"

        if interactions is None and "documented_allergy" not in reading.claims:
            unresolved.append(
                "Neither medication list nor allergy status was supplied."
            )
        else:
            signals: list[str] = []
            claim_ids: list[str] = []
            evidence_ids: set[str] = set()
            stance = Stance.SUPPORTS

            if allergy or prior:
                stance = Stance.OPPOSES
                if allergy:
                    signals.append("a documented allergy to this agent")
                if prior:
                    signals.append("a prior adverse reaction")
            if interactions is not None:
                claim = reading.claims["interacting_drug_count"]
                claim_ids.append(claim.id)
                evidence_ids.update(claim.evidence_ids)
                if interactions >= INTERACTION_CAUTION_COUNT:
                    signals.append(f"{interactions:.0f} interacting medications")
                    if stance is Stance.SUPPORTS:
                        stance = Stance.CONDITIONAL
                else:
                    signals.append(f"{interactions:.0f} interacting medications")

            for parameter in ("documented_allergy", "prior_adverse_reaction"):
                claim = reading.claim(parameter)
                if claim is not None:
                    claim_ids.append(claim.id)
                    evidence_ids.update(claim.evidence_ids)

            findings.append(
                Finding(
                    id="int-risk",
                    topic="interaction_risk",
                    stance=stance,
                    statement=f"Interaction and allergy profile: {'; '.join(signals)}.",
                    claim_ids=tuple(sorted(set(claim_ids))),
                    evidence_ids=tuple(sorted(evidence_ids)),
                )
            )
            findings.append(
                Finding(
                    id="int-suitability",
                    topic="treatment_suitability",
                    stance=stance,
                    statement=(
                        f"On interaction grounds the treatment reads as {stance.value}."
                    ),
                    claim_ids=tuple(sorted(set(claim_ids))),
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


class EvidenceStrengthKernel:
    """Reads how well the treatment is supported by published evidence."""

    name = "evidence_strength"
    PREDICATES = ("guideline_grade", "trial_evidence_level")

    def run(self, ir: ChoirIR) -> Artifact:
        """Assess evidence quality and return an artifact."""
        reading = ir.gather(self.PREDICATES)
        findings: list[Finding] = []
        unresolved: list[str] = []

        grade = (reading.text("guideline_grade") or "").lower()
        level = reading.number("trial_evidence_level")

        if not grade and level is None:
            unresolved.append("No guideline grade or trial evidence level was cited.")
        else:
            signals: list[str] = []
            claim_ids: list[str] = []
            evidence_ids: set[str] = set()

            strong = True
            if grade:
                claim = reading.claims["guideline_grade"]
                claim_ids.append(claim.id)
                evidence_ids.update(claim.evidence_ids)
                signals.append(f"guideline grade {grade.upper()}")
                if grade not in STRONG_GUIDELINE_GRADES:
                    strong = False
                if grade not in ACCEPTABLE_GUIDELINE_GRADES:
                    signals.append("below the acceptable grade band")

            if level is not None:
                claim = reading.claims["trial_evidence_level"]
                claim_ids.append(claim.id)
                evidence_ids.update(claim.evidence_ids)
                signals.append(f"trial evidence level {level:.0f}")
                if level > STRONG_TRIAL_LEVEL:
                    strong = False

            weak = grade not in ACCEPTABLE_GUIDELINE_GRADES if grade else False
            stance = (
                Stance.SUPPORTS
                if strong
                else (Stance.OPPOSES if weak else Stance.CONDITIONAL)
            )

            findings.append(
                Finding(
                    id="ev-quality",
                    topic="evidence_quality",
                    stance=stance,
                    statement=f"Published support: {'; '.join(signals)}.",
                    claim_ids=tuple(claim_ids),
                    evidence_ids=tuple(sorted(evidence_ids)),
                )
            )
            findings.append(
                Finding(
                    id="ev-suitability",
                    topic="treatment_suitability",
                    stance=stance,
                    statement=(
                        f"On published evidence the treatment reads as {stance.value}."
                    ),
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


class MonitoringKernel:
    """Reads whether the treatment can be safely monitored."""

    name = "monitoring_capacity"
    PREDICATES = ("monitoring_available", "baseline_lft_normal")

    def run(self, ir: ChoirIR) -> Artifact:
        """Assess monitoring capacity and return an artifact."""
        reading = ir.gather(self.PREDICATES)
        findings: list[Finding] = []
        unresolved: list[str] = []

        available = (reading.text("monitoring_available") or "").lower() == "yes"
        baseline = (reading.text("baseline_lft_normal") or "").lower() == "yes"

        if "monitoring_available" not in reading.claims:
            unresolved.append("Monitoring availability was not stated.")
        else:
            claim_ids = [reading.claims["monitoring_available"].id]
            evidence_ids = set(reading.claims["monitoring_available"].evidence_ids)
            baseline_claim = reading.claim("baseline_lft_normal")
            if baseline_claim is not None:
                claim_ids.append(baseline_claim.id)
                evidence_ids.update(baseline_claim.evidence_ids)

            findings.append(
                Finding(
                    id="mon-capacity",
                    topic="monitoring_capacity",
                    stance=(
                        Stance.SUPPORTS if available and baseline else Stance.OPPOSES
                    ),
                    statement=(
                        f"Monitoring {'is' if available else 'is not'} available; "
                        f"baseline liver function {'is' if baseline else 'is not'} "
                        "normal."
                    ),
                    claim_ids=tuple(claim_ids),
                    evidence_ids=tuple(sorted(evidence_ids)),
                )
            )

        if "baseline_lft_normal" not in reading.claims:
            unresolved.append("Baseline liver function was not recorded.")

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
    RenalSafetyKernel, InteractionSafetyKernel, EvidenceStrengthKernel, MonitoringKernel
]:
    """Return every kernel, in fixed dispatch order."""
    return (
        RenalSafetyKernel(),
        InteractionSafetyKernel(),
        EvidenceStrengthKernel(),
        MonitoringKernel(),
    )


# ---------------------------------------------------------------------------
# Packets
# ---------------------------------------------------------------------------

_STANDARD_GUIDANCE = (
    Guidance("GUIDE-RENAL", "Renal dosing guideline, current edition", "guideline"),
    Guidance("LAB-PANEL", "Laboratory panel, this admission", "laboratory"),
    Guidance("CHART-MEDS", "Medication reconciliation from the chart", "chart"),
    Guidance("TRIAL-META", "Pooled trial analysis for this indication", "trial"),
    Guidance("HX-PATIENT", "Patient-reported history", "history"),
)


RENAL_CAUTION = ClinicalPacket(
    id="renal-caution-referral",
    title="Referral A -- treatment suitability with renal impairment",
    patient_ref="Patient A",
    proposed_treatment="Agent X, standard dose",
    care_setting="inpatient",
    guidance=_STANDARD_GUIDANCE,
    observations=(
        Observation("egfr_ml_min", "22", ("LAB-PANEL",), "measured"),
        Observation("on_dialysis", "no", ("CHART-MEDS",), "documented"),
        Observation("age_years", "78", ("CHART-MEDS",), "documented"),
        Observation("interacting_drug_count", "4", ("CHART-MEDS",), "documented"),
        Observation("documented_allergy", "yes", ("HX-PATIENT",), "conflicting"),
        Observation("prior_adverse_reaction", "yes", ("HX-PATIENT",), "reported"),
        Observation("guideline_grade", "C", ("GUIDE-RENAL",), "documented"),
        Observation("trial_evidence_level", "4", ("TRIAL-META",), "documented"),
        Observation("monitoring_available", "no", ("CHART-MEDS",), "documented"),
        Observation("baseline_lft_normal", "no", ("LAB-PANEL",), "measured"),
    ),
    stated_assumptions=(
        "The eGFR is a single measurement, not a trend.",
        "The allergy history is patient-reported and not confirmed by challenge.",
    ),
    conflicting_records=(
        ConflictingRecord(
            parameter="documented_allergy",
            note=(
                "The allergy is recorded in the patient history but does not appear "
                "in the chart's structured allergy list."
            ),
        ),
    ),
)


ROUTINE_CASE = ClinicalPacket(
    id="routine-referral",
    title="Referral B -- routine treatment suitability",
    patient_ref="Patient B",
    proposed_treatment="Agent X, standard dose",
    care_setting="outpatient",
    guidance=_STANDARD_GUIDANCE,
    observations=(
        Observation("egfr_ml_min", "88", ("LAB-PANEL",), "measured"),
        Observation("on_dialysis", "no", ("CHART-MEDS",), "documented"),
        Observation("age_years", "41", ("CHART-MEDS",), "documented"),
        Observation("interacting_drug_count", "0", ("CHART-MEDS",), "documented"),
        Observation("documented_allergy", "no", ("CHART-MEDS",), "documented"),
        Observation("prior_adverse_reaction", "no", ("CHART-MEDS",), "documented"),
        Observation("guideline_grade", "A", ("GUIDE-RENAL",), "documented"),
        Observation("trial_evidence_level", "1", ("TRIAL-META",), "documented"),
        Observation("monitoring_available", "yes", ("CHART-MEDS",), "documented"),
        Observation("baseline_lft_normal", "yes", ("LAB-PANEL",), "measured"),
    ),
    stated_assumptions=("Renal function is stable over the last two measurements.",),
    conflicting_records=(),
)


PACKETS = {
    RENAL_CAUTION.id: RENAL_CAUTION,
    ROUTINE_CASE.id: ROUTINE_CASE,
}


def describe(packet: ClinicalPacket) -> PacketSummary:
    """Tell the pipeline what it needs to know about a clinical referral."""
    return PacketSummary(
        packet_id=packet.id,
        title=packet.title,
        record_count=len(packet.observations),
        notes=(
            f"{len(packet.guidance)} guidance/record source(s)",
            f"{len(packet.observations)} observation(s)",
            f"{len(packet.stated_assumptions)} stated assumption(s)",
            f"{len(packet.conflicting_records)} conflicting record(s)",
        ),
    )


DOMAIN = Domain(
    name="medicine",
    description="Treatment-suitability assessment from a clinical referral",
    translate=translate,
    describe=describe,
    kernels=all_kernels(),
    topics=TOPICS,
    packets=dict(PACKETS),
)
