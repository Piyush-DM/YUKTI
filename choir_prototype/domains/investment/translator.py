"""The domain translator.

Consumes a structured investment packet and produces the CHOIR Intermediate
Representation. Nothing else.

**No reasoning occurs here.** The translator does not weigh, score, filter, or
judge. It maps domain shapes onto IR shapes and preserves what the packet said,
including things the packet got wrong. If a data point cites a source that does
not exist, that dangling reference survives translation -- it is a fact about
the packet, and hiding it here would hide it from every kernel downstream.
"""

from __future__ import annotations

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
from choir_prototype.domains.investment.packets import InvestmentPacket

TRANSLATOR_NAME = "investment.v0"
IR_VERSION = "choir-ir/0.1"

# Source kind -> how the evidence was obtained. This is a vocabulary mapping,
# not a judgement: it records how the document came to exist.
_KIND_TO_QUALITY = {
    "audit": EvidenceQuality.AUDITED,
    "management": EvidenceQuality.REPORTED,
    "interview": EvidenceQuality.REPORTED,
    "third_party": EvidenceQuality.ESTIMATED,
    "assertion": EvidenceQuality.ASSERTED,
}

# Packet status -> how settled the claim is, as the packet itself described it.
_STATUS_TO_UNCERTAINTY = {
    "confirmed": Uncertainty.SETTLED,
    "reported": Uncertainty.LIKELY,
    "estimated": Uncertainty.LIKELY,
    "disputed": Uncertainty.DISPUTED,
    "unknown": Uncertainty.UNKNOWN,
}


def translate(packet: InvestmentPacket) -> ChoirIR:
    """Translate an investment packet into the CHOIR IR."""
    company_id = "ent-company"
    market_id = "ent-market"

    entities = (
        Entity(
            id=company_id,
            kind="company",
            label=packet.company_name,
            attributes={"sector": packet.sector, "stage": packet.stage},
        ),
        Entity(
            id=market_id,
            kind="market",
            label=f"{packet.sector} market",
            attributes={"sector": packet.sector},
        ),
    )

    evidence = tuple(
        Evidence(
            id=source.label,
            source=source.origin,
            statement=f"{source.origin} ({source.kind})",
            quality=_KIND_TO_QUALITY.get(source.kind, EvidenceQuality.ASSERTED),
        )
        for source in packet.sources
    )

    # Market-facing metrics attach to the market entity, everything else to the
    # company. This is a translation decision, not a reasoning one.
    market_metrics = frozenset({"tam_usd", "market_growth_pct", "competitor_count"})

    claims: list[Claim] = []
    for index, point in enumerate(packet.data_points, start=1):
        claims.append(
            Claim(
                id=f"clm-{index:03d}",
                subject_id=market_id if point.metric in market_metrics else company_id,
                predicate=point.metric,
                value=point.value,
                uncertainty=_STATUS_TO_UNCERTAINTY.get(
                    point.status, Uncertainty.UNKNOWN
                ),
                evidence_ids=point.source_labels,
            )
        )

    assumptions = tuple(
        Assumption(
            id=f"asm-{index:03d}",
            statement=statement,
            basis="stated in packet",
        )
        for index, statement in enumerate(packet.stated_assumptions, start=1)
    )

    relationships = _build_relationships(packet, tuple(claims))

    return ChoirIR(
        metadata=Metadata(
            packet_id=packet.id,
            packet_title=packet.title,
            domain="investment",
            translator=TRANSLATOR_NAME,
            ir_version=IR_VERSION,
        ),
        entities=entities,
        claims=tuple(claims),
        evidence=evidence,
        assumptions=assumptions,
        relationships=relationships,
    )


def _build_relationships(
    packet: InvestmentPacket, claims: tuple[Claim, ...]
) -> tuple[Relationship, ...]:
    """Link evidence to the claims it backs, and record flagged conflicts."""
    relationships: list[Relationship] = []
    counter = 0

    for claim in claims:
        for evidence_id in claim.evidence_ids:
            counter += 1
            relationships.append(
                Relationship(
                    id=f"rel-{counter:03d}",
                    kind=RelationshipKind.SUPPORTS,
                    source_id=evidence_id,
                    target_id=claim.id,
                )
            )

    by_predicate = {claim.predicate: claim for claim in claims}
    for conflict in packet.noted_conflicts:
        claim = by_predicate.get(conflict.metric)
        if claim is None:
            continue
        counter += 1
        relationships.append(
            Relationship(
                id=f"rel-{counter:03d}",
                kind=RelationshipKind.CONTRADICTS,
                source_id="packet-review",
                target_id=claim.id,
                note=conflict.note,
            )
        )

    return tuple(relationships)
