"""The law domain.

A contract-claim viability assessment. One file: packet shape, translator,
kernels, topic vocabulary, and the ``Domain`` binding.

Nothing in ``choir_prototype/core/`` was changed to add this domain. That is the
claim, and ``audit.py`` measures it.

Note how different the packet shape is from the investment domain's: this one
has *authorities* and *case facts*, not source documents and data points. The
translator absorbs that difference; everything downstream sees only the IR.
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
    "limitation",
    "claim_viability",
    "evidentiary_strength",
    "jurisdictional_certainty",
    "procedural_compliance",
)

# --- Limitation thresholds --------------------------------------------------
LIMITATION_WARNING_RATIO = 0.85

# --- Evidentiary thresholds -------------------------------------------------
STRONG_DOCUMENTARY_PCT = 80.0
WEAK_DOCUMENTARY_PCT = 50.0
SUFFICIENT_WITNESS_COUNT = 3

# --- Precedent thresholds ---------------------------------------------------
SETTLED_PRECEDENT_COUNT = 5
CONTESTED_PRECEDENT_COUNT = 2


# ---------------------------------------------------------------------------
# Packet shape
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Authority:
    """A source of law or evidence relied on."""

    citation: str
    description: str
    weight: str


@dataclass(frozen=True)
class CaseFact:
    """One fact about the case, with the authorities behind it."""

    element: str
    value: str
    authority_citations: tuple[str, ...]
    standing: str


@dataclass(frozen=True)
class DisputedFact:
    """A fact the other side contests."""

    element: str
    note: str


@dataclass(frozen=True)
class LegalPacket:
    """A contract-claim assessment brief."""

    id: str
    title: str
    claimant: str
    respondent: str
    forum: str
    authorities: tuple[Authority, ...]
    case_facts: tuple[CaseFact, ...]
    stated_assumptions: tuple[str, ...]
    disputed_facts: tuple[DisputedFact, ...]


# ---------------------------------------------------------------------------
# Translation
# ---------------------------------------------------------------------------

TRANSLATOR_NAME = "law.v0"
IR_VERSION = "choir-ir/0.1"

_WEIGHT_TO_QUALITY = {
    "binding": EvidenceQuality.AUDITED,
    "statutory": EvidenceQuality.AUDITED,
    "persuasive": EvidenceQuality.REPORTED,
    "documentary": EvidenceQuality.REPORTED,
    "submission": EvidenceQuality.ESTIMATED,
    "assertion": EvidenceQuality.ASSERTED,
}

_STANDING_TO_UNCERTAINTY = {
    "admitted": Uncertainty.SETTLED,
    "evidenced": Uncertainty.LIKELY,
    "pleaded": Uncertainty.LIKELY,
    "contested": Uncertainty.DISPUTED,
    "unknown": Uncertainty.UNKNOWN,
}

_FORUM_ELEMENTS = frozenset(
    {"governing_law_stated", "forum_clause_exclusive", "notice_served"}
)


def translate(packet: LegalPacket) -> ChoirIR:
    """Map a legal brief onto the CHOIR IR. No reasoning happens here."""
    claimant_id = "ent-claimant"
    forum_id = "ent-forum"

    entities = (
        Entity(
            id=claimant_id,
            kind="party",
            label=packet.claimant,
            attributes={"role": "claimant", "respondent": packet.respondent},
        ),
        Entity(
            id=forum_id,
            kind="forum",
            label=packet.forum,
            attributes={"forum": packet.forum},
        ),
    )

    evidence = tuple(
        Evidence(
            id=authority.citation,
            source=authority.description,
            statement=f"{authority.description} ({authority.weight})",
            quality=_WEIGHT_TO_QUALITY.get(authority.weight, EvidenceQuality.ASSERTED),
        )
        for authority in packet.authorities
    )

    claims = tuple(
        Claim(
            id=f"clm-{index:03d}",
            subject_id=forum_id if fact.element in _FORUM_ELEMENTS else claimant_id,
            predicate=fact.element,
            value=fact.value,
            uncertainty=_STANDING_TO_UNCERTAINTY.get(
                fact.standing, Uncertainty.UNKNOWN
            ),
            evidence_ids=fact.authority_citations,
        )
        for index, fact in enumerate(packet.case_facts, start=1)
    )

    assumptions = tuple(
        Assumption(id=f"asm-{index:03d}", statement=statement, basis="stated in brief")
        for index, statement in enumerate(packet.stated_assumptions, start=1)
    )

    relationships: list[Relationship] = []
    counter = 0
    for claim in claims:
        for citation in claim.evidence_ids:
            counter += 1
            relationships.append(
                Relationship(
                    id=f"rel-{counter:03d}",
                    kind=RelationshipKind.SUPPORTS,
                    source_id=citation,
                    target_id=claim.id,
                )
            )

    by_element = {claim.predicate: claim for claim in claims}
    for disputed in packet.disputed_facts:
        claim = by_element.get(disputed.element)
        if claim is None:
            continue
        counter += 1
        relationships.append(
            Relationship(
                id=f"rel-{counter:03d}",
                kind=RelationshipKind.CONTRADICTS,
                source_id="respondent-defence",
                target_id=claim.id,
                note=disputed.note,
            )
        )

    return ChoirIR(
        metadata=Metadata(
            packet_id=packet.id,
            packet_title=packet.title,
            domain="law",
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


class LimitationKernel:
    """Reads whether the claim is brought in time."""

    name = "limitation"
    PREDICATES = (
        "days_since_accrual",
        "limitation_period_days",
        "written_acknowledgement",
        "claimant_under_disability",
    )

    def run(self, ir: ChoirIR) -> Artifact:
        """Assess limitation and return an artifact."""
        reading = ir.gather(self.PREDICATES)
        findings: list[Finding] = []
        unresolved: list[str] = []

        elapsed = reading.number("days_since_accrual")
        period = reading.number("limitation_period_days")
        acknowledged = (reading.text("written_acknowledgement") or "").lower() == "yes"
        disability = (reading.text("claimant_under_disability") or "").lower() == "yes"

        if elapsed is None or period is None or period <= 0:
            unresolved.append(
                "Limitation could not be assessed: accrual date or period missing."
            )
        else:
            ratio = elapsed / period
            claim_ids = (
                reading.claims["days_since_accrual"].id,
                reading.claims["limitation_period_days"].id,
            )
            if ratio >= 1.0 and not (acknowledged or disability):
                stance = Stance.OPPOSES
                text = (
                    f"{elapsed:.0f} days elapsed against a {period:.0f}-day period: "
                    "the claim is prima facie time-barred"
                )
            elif ratio >= 1.0:
                stance = Stance.CONDITIONAL
                extender = (
                    "written acknowledgement" if acknowledged else "claimant disability"
                )
                text = (
                    f"{elapsed:.0f} days elapsed against a {period:.0f}-day period, "
                    f"but {extender} may restart or suspend time"
                )
            elif ratio >= LIMITATION_WARNING_RATIO:
                stance = Stance.CONDITIONAL
                text = (
                    f"{elapsed:.0f} of {period:.0f} days used "
                    f"({ratio:.0%}); the period expires shortly"
                )
            else:
                stance = Stance.SUPPORTS
                text = f"{elapsed:.0f} of {period:.0f} days used ({ratio:.0%}); in time"

            findings.append(
                Finding(
                    id="lim-period",
                    topic="limitation",
                    stance=stance,
                    statement=f"{text}.",
                    claim_ids=claim_ids,
                    evidence_ids=tuple(
                        sorted(
                            set(reading.claims["days_since_accrual"].evidence_ids)
                            | set(reading.claims["limitation_period_days"].evidence_ids)
                        )
                    ),
                )
            )
            findings.append(
                Finding(
                    id="lim-viability",
                    topic="claim_viability",
                    stance=stance,
                    statement=(
                        "Limitation is a complete answer to the claim if it runs, "
                        f"and it currently reads as {stance.value}."
                    ),
                    claim_ids=claim_ids,
                )
            )

        for claim in reading.contradicted(ir):
            unresolved.append(
                f"Claim {claim.id} ({claim.predicate}) is contested by the "
                "respondent; this finding is provisional."
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


class EvidentiaryKernel:
    """Reads the strength of the evidential record."""

    name = "evidentiary_record"
    PREDICATES = (
        "documentary_completeness_pct",
        "witness_count",
        "expert_evidence_available",
    )

    def run(self, ir: ChoirIR) -> Artifact:
        """Assess the evidential record and return an artifact."""
        reading = ir.gather(self.PREDICATES)
        findings: list[Finding] = []
        unresolved: list[str] = []

        documents = reading.number("documentary_completeness_pct")
        witnesses = reading.number("witness_count")
        expert = (reading.text("expert_evidence_available") or "").lower() == "yes"

        if documents is None and witnesses is None:
            unresolved.append("Neither documentary nor witness evidence was described.")
        else:
            signals: list[str] = []
            strong = True
            claim_ids: list[str] = []
            evidence_ids: set[str] = set()

            if documents is not None:
                claim = reading.claims["documentary_completeness_pct"]
                claim_ids.append(claim.id)
                evidence_ids.update(claim.evidence_ids)
                if documents >= STRONG_DOCUMENTARY_PCT:
                    signals.append(f"documentary record {documents:.0f}% complete")
                elif documents >= WEAK_DOCUMENTARY_PCT:
                    signals.append(f"documentary record only {documents:.0f}% complete")
                    strong = False
                else:
                    signals.append(
                        f"documentary record {documents:.0f}%: substantial gaps"
                    )
                    strong = False

            if witnesses is not None:
                claim = reading.claims["witness_count"]
                claim_ids.append(claim.id)
                evidence_ids.update(claim.evidence_ids)
                if witnesses >= SUFFICIENT_WITNESS_COUNT:
                    signals.append(f"{witnesses:.0f} witnesses available")
                else:
                    signals.append(f"only {witnesses:.0f} witness(es)")
                    strong = False

            signals.append(
                "expert evidence available" if expert else "no expert evidence"
            )
            if not expert:
                strong = False

            findings.append(
                Finding(
                    id="ev-record",
                    topic="evidentiary_strength",
                    stance=Stance.SUPPORTS if strong else Stance.CONDITIONAL,
                    statement=f"Evidential record: {'; '.join(signals)}.",
                    claim_ids=tuple(claim_ids),
                    evidence_ids=tuple(sorted(evidence_ids)),
                )
            )
            findings.append(
                Finding(
                    id="ev-viability",
                    topic="claim_viability",
                    stance=Stance.SUPPORTS if strong else Stance.CONDITIONAL,
                    statement=(
                        "On the evidential record alone the claim is "
                        f"{'well supported' if strong else 'arguable but incomplete'}."
                    ),
                    claim_ids=tuple(claim_ids),
                )
            )

        if "expert_evidence_available" not in reading.claims:
            unresolved.append("Expert evidence availability was not stated.")

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


class ForumKernel:
    """Reads jurisdiction, governing law and pre-action compliance."""

    name = "forum_and_procedure"
    PREDICATES = ("governing_law_stated", "forum_clause_exclusive", "notice_served")

    def run(self, ir: ChoirIR) -> Artifact:
        """Assess forum and procedure and return an artifact."""
        reading = ir.gather(self.PREDICATES)
        findings: list[Finding] = []
        unresolved: list[str] = []

        governing = (reading.text("governing_law_stated") or "").lower() == "yes"
        exclusive = (reading.text("forum_clause_exclusive") or "").lower() == "yes"
        notice = (reading.text("notice_served") or "").lower() == "yes"

        if "governing_law_stated" in reading.claims:
            certain = governing and exclusive
            findings.append(
                Finding(
                    id="forum-certainty",
                    topic="jurisdictional_certainty",
                    stance=Stance.SUPPORTS if certain else Stance.CONDITIONAL,
                    statement=(
                        f"Governing law {'is' if governing else 'is not'} stated; "
                        f"forum clause {'is' if exclusive else 'is not'} exclusive."
                    ),
                    claim_ids=(reading.claims["governing_law_stated"].id,),
                    evidence_ids=reading.claims["governing_law_stated"].evidence_ids,
                )
            )
        else:
            unresolved.append("Governing law was not addressed in the brief.")

        if "notice_served" in reading.claims:
            findings.append(
                Finding(
                    id="forum-notice",
                    topic="procedural_compliance",
                    stance=Stance.SUPPORTS if notice else Stance.OPPOSES,
                    statement=(
                        "Pre-action notice has been served."
                        if notice
                        else "Pre-action notice has not been served."
                    ),
                    claim_ids=(reading.claims["notice_served"].id,),
                    evidence_ids=reading.claims["notice_served"].evidence_ids,
                )
            )
        else:
            unresolved.append("Service of pre-action notice was not confirmed.")

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


class PrecedentKernel:
    """Reads how settled the point of law is."""

    name = "precedent"
    PREDICATES = (
        "prior_similar_rulings",
        "rulings_favourable_pct",
        "contract_value_usd",
    )

    def run(self, ir: ChoirIR) -> Artifact:
        """Assess precedent and return an artifact."""
        reading = ir.gather(self.PREDICATES)
        findings: list[Finding] = []
        unresolved: list[str] = []
        assumptions: list[str] = []

        rulings = reading.number("prior_similar_rulings")
        favourable = reading.number("rulings_favourable_pct")

        if rulings is None:
            unresolved.append("No survey of comparable rulings was supplied.")
        else:
            claim = reading.claims["prior_similar_rulings"]
            if rulings >= SETTLED_PRECEDENT_COUNT:
                settled = "the point is well covered by authority"
                stance = Stance.SUPPORTS
            elif rulings >= CONTESTED_PRECEDENT_COUNT:
                settled = "authority exists but is thin"
                stance = Stance.CONDITIONAL
            else:
                settled = "the point is close to untested"
                stance = Stance.CONDITIONAL

            if favourable is not None and favourable < 50.0:
                stance = Stance.OPPOSES
                settled += f", and only {favourable:.0f}% of it favours the claimant"
                assumptions.append(
                    "Favourability is taken from the brief's own characterisation "
                    "of the prior rulings."
                )

            findings.append(
                Finding(
                    id="prec-coverage",
                    topic="evidentiary_strength",
                    stance=stance,
                    statement=f"{rulings:.0f} comparable rulings: {settled}.",
                    claim_ids=(claim.id,),
                    evidence_ids=claim.evidence_ids,
                )
            )
            findings.append(
                Finding(
                    id="prec-viability",
                    topic="claim_viability",
                    stance=stance,
                    statement=(
                        f"On precedent the claim reads as {stance.value} at this stage."
                    ),
                    claim_ids=(claim.id,),
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
            assumptions=tuple(assumptions),
            unresolved_questions=tuple(unresolved),
        )


def all_kernels() -> tuple[
    LimitationKernel, EvidentiaryKernel, ForumKernel, PrecedentKernel
]:
    """Return every kernel, in fixed dispatch order."""
    return (LimitationKernel(), EvidentiaryKernel(), ForumKernel(), PrecedentKernel())


# ---------------------------------------------------------------------------
# Packets
# ---------------------------------------------------------------------------

MERIDIAN_SUPPLY = LegalPacket(
    id="meridian-supply-claim",
    title="Meridian Foods v. Calder Logistics -- supply contract claim",
    claimant="Meridian Foods Ltd.",
    respondent="Calder Logistics plc",
    forum="Commercial Court",
    authorities=(
        Authority(
            "AUTH-LIMITATION-ACT", "Limitation statute, s.5 and s.29", "statutory"
        ),
        Authority("AUTH-CONTRACT", "Executed supply agreement", "documentary"),
        Authority(
            "AUTH-CORRESPONDENCE", "Inter-party correspondence bundle", "documentary"
        ),
        Authority(
            "AUTH-CASE-SURVEY", "Counsel's survey of comparable rulings", "persuasive"
        ),
        Authority("AUTH-CLIENT", "Client instructions", "assertion"),
    ),
    case_facts=(
        CaseFact("days_since_accrual", "2380", ("AUTH-CORRESPONDENCE",), "evidenced"),
        CaseFact(
            "limitation_period_days", "2190", ("AUTH-LIMITATION-ACT",), "admitted"
        ),
        CaseFact(
            "written_acknowledgement", "yes", ("AUTH-CORRESPONDENCE",), "contested"
        ),
        CaseFact("claimant_under_disability", "no", ("AUTH-CLIENT",), "admitted"),
        CaseFact("documentary_completeness_pct", "88", ("AUTH-CONTRACT",), "evidenced"),
        CaseFact("witness_count", "4", ("AUTH-CLIENT",), "pleaded"),
        CaseFact("expert_evidence_available", "yes", ("AUTH-CLIENT",), "pleaded"),
        CaseFact("governing_law_stated", "yes", ("AUTH-CONTRACT",), "admitted"),
        CaseFact("forum_clause_exclusive", "yes", ("AUTH-CONTRACT",), "admitted"),
        CaseFact("notice_served", "yes", ("AUTH-CORRESPONDENCE",), "evidenced"),
        CaseFact("prior_similar_rulings", "7", ("AUTH-CASE-SURVEY",), "pleaded"),
        CaseFact("rulings_favourable_pct", "38", ("AUTH-CASE-SURVEY",), "pleaded"),
        CaseFact("contract_value_usd", "4200000", ("AUTH-CONTRACT",), "admitted"),
    ),
    stated_assumptions=(
        "The correspondence bundle is complete for the acknowledgement issue.",
        "Counsel's ruling survey covers the relevant jurisdiction only.",
    ),
    disputed_facts=(
        DisputedFact(
            element="written_acknowledgement",
            note=(
                "The respondent denies the 2021 letter amounts to an acknowledgement "
                "of the debt, which is the only thing preventing limitation running."
            ),
        ),
    ),
)


HARBOUR_NOTE = LegalPacket(
    id="harbour-note-claim",
    title="Harbour Devices -- preliminary claim note",
    claimant="Harbour Devices Inc.",
    respondent="unidentified counterparty",
    forum="not yet selected",
    authorities=(
        Authority(
            "AUTH-NOTE", "One-page instruction note from the client", "assertion"
        ),
    ),
    case_facts=(
        CaseFact("days_since_accrual", "300", ("AUTH-NOTE",), "pleaded"),
        CaseFact("contract_value_usd", "150000", ("AUTH-NOTE",), "pleaded"),
    ),
    stated_assumptions=("The client's account of the timeline is untested.",),
    disputed_facts=(),
)


PACKETS = {
    MERIDIAN_SUPPLY.id: MERIDIAN_SUPPLY,
    HARBOUR_NOTE.id: HARBOUR_NOTE,
}


def describe(packet: LegalPacket) -> PacketSummary:
    """Tell the pipeline what it needs to know about a legal brief."""
    return PacketSummary(
        packet_id=packet.id,
        title=packet.title,
        record_count=len(packet.case_facts),
        notes=(
            f"{len(packet.authorities)} authority/authorities cited",
            f"{len(packet.case_facts)} case fact(s)",
            f"{len(packet.stated_assumptions)} stated assumption(s)",
            f"{len(packet.disputed_facts)} disputed fact(s)",
        ),
    )


DOMAIN = Domain(
    name="law",
    description="Contract-claim viability assessment from a brief",
    translate=translate,
    describe=describe,
    kernels=all_kernels(),
    topics=TOPICS,
    packets=dict(PACKETS),
)
