"""The CHOIR Intermediate Representation.

This is the canonical representation used throughout the runtime. The domain
translator produces it; every downstream component consumes only it. Nothing in
this module reasons -- it only defines structure.

Design notes for V0:

- Everything is a frozen dataclass. No inheritance, no registries, no schemas
  beyond what is written here.
- Ordering is explicit everywhere so that two runs over the same packet produce
  byte-identical output.
- Uncertainty and evidence quality are *ordinal*, not numeric. Arithmetic on
  them is deliberately not provided.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum


class EvidenceQuality(Enum):
    """How the evidence was obtained.

    This is a structural property of the source, not a judgement about the
    claim. It is supplied by the packet, never invented by a kernel.
    """

    AUDITED = "audited"
    REPORTED = "reported"
    ESTIMATED = "estimated"
    ASSERTED = "asserted"

    @property
    def rank(self) -> int:
        """Ordinal rank. Higher is stronger. Used only for comparison."""
        return _EVIDENCE_RANK[self]


_EVIDENCE_RANK = {
    EvidenceQuality.AUDITED: 3,
    EvidenceQuality.REPORTED: 2,
    EvidenceQuality.ESTIMATED: 1,
    EvidenceQuality.ASSERTED: 0,
}


class Uncertainty(Enum):
    """How settled a claim is, as stated by the source packet."""

    SETTLED = "settled"
    LIKELY = "likely"
    DISPUTED = "disputed"
    UNKNOWN = "unknown"


class RelationshipKind(Enum):
    """The relationship families the prototype needs.

    SUPPORTS and CONTRADICTS are epistemic: they hold between evidence and
    claims. INFLUENCES is deliberately distinct from CAUSES -- an influence
    modulates an existing claim without asserting that it produced it.
    """

    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    INFLUENCES = "influences"
    DEPENDS_ON = "depends_on"


# A topic is an opaque label a kernel attaches to a finding so the synthesizer
# can group findings that are about the same thing. The core defines the
# *mechanism* -- findings carry a topic, topics group by equality. It does not
# define the *vocabulary*: which topics exist is supplied by each domain.
#
# This split was found by the portability experiment (see audit.py). The topic
# vocabulary originally lived here as an enum of investment terms, which meant
# no other domain could be added without editing the core IR.
Topic = str


@dataclass(frozen=True)
class Entity:
    """Something the packet reasons about."""

    id: str
    kind: str
    label: str
    attributes: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Evidence:
    """A source item that bears on one or more claims."""

    id: str
    source: str
    statement: str
    quality: EvidenceQuality


@dataclass(frozen=True)
class Claim:
    """A statement about an entity, backed by zero or more evidence items.

    A claim with no evidence is legal and meaningful: it records that the packet
    asserted something without support. Kernels must be able to see that.
    """

    id: str
    subject_id: str
    predicate: str
    value: str
    uncertainty: Uncertainty
    evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class Assumption:
    """Something taken as given by the packet rather than established by it."""

    id: str
    statement: str
    basis: str


@dataclass(frozen=True)
class Relationship:
    """A typed, directed link between two IR objects."""

    id: str
    kind: RelationshipKind
    source_id: str
    target_id: str
    note: str = ""


@dataclass(frozen=True)
class Metadata:
    """Provenance for the IR document itself."""

    packet_id: str
    packet_title: str
    domain: str
    translator: str
    ir_version: str


@dataclass(frozen=True)
class Reading:
    """What one kernel pulled out of the IR, ready for confidence derivation."""

    claims: dict[str, Claim]
    evidence: tuple[Evidence, ...]
    contradictions: int
    expected: int

    @property
    def found(self) -> int:
        """How many of the sought predicates were present."""
        return len(self.claims)

    def claim(self, predicate: str) -> Claim | None:
        """Return the claim for a predicate, or None if the packet omitted it."""
        return self.claims.get(predicate)

    def number(self, predicate: str) -> float | None:
        """Read a predicate's value as a number, or None if absent/non-numeric."""
        claim = self.claims.get(predicate)
        if claim is None:
            return None
        try:
            return float(claim.value)
        except ValueError:
            return None

    def text(self, predicate: str) -> str | None:
        """Read a predicate's value as text, or None if absent."""
        claim = self.claims.get(predicate)
        return claim.value if claim else None

    def contradicted(self, ir: ChoirIR) -> tuple[Claim, ...]:
        """Return the claims this reading used that something contradicts."""
        flagged = ir.contradicted_claim_ids()
        return tuple(
            claim
            for claim in sorted(self.claims.values(), key=lambda item: item.id)
            if claim.id in flagged
        )


@dataclass(frozen=True)
class ChoirIR:
    """The complete intermediate representation for one packet."""

    metadata: Metadata
    entities: tuple[Entity, ...]
    claims: tuple[Claim, ...]
    evidence: tuple[Evidence, ...]
    assumptions: tuple[Assumption, ...]
    relationships: tuple[Relationship, ...]

    def claim(self, claim_id: str) -> Claim | None:
        """Return the claim with this id, or None."""
        for item in self.claims:
            if item.id == claim_id:
                return item
        return None

    def evidence_item(self, evidence_id: str) -> Evidence | None:
        """Return the evidence with this id, or None."""
        for item in self.evidence:
            if item.id == evidence_id:
                return item
        return None

    def claims_with_predicate(self, predicate: str) -> tuple[Claim, ...]:
        """Return every claim using this predicate, in packet order."""
        return tuple(item for item in self.claims if item.predicate == predicate)

    def evidence_for_claim(self, claim: Claim) -> tuple[Evidence, ...]:
        """Return the evidence backing a claim, skipping dangling ids."""
        found = []
        for evidence_id in claim.evidence_ids:
            item = self.evidence_item(evidence_id)
            if item is not None:
                found.append(item)
        return tuple(found)

    def contradicted_claim_ids(self) -> frozenset[str]:
        """Return the ids of claims that some relationship contradicts."""
        return frozenset(
            relationship.target_id
            for relationship in self.relationships
            if relationship.kind is RelationshipKind.CONTRADICTS
        )

    def gather(self, predicates: Sequence[str]) -> Reading:
        """Collect the claims a kernel cares about, with their evidence.

        Domain-neutral mechanism: every kernel in every domain needs to pull a
        named set of predicates out of the IR, de-duplicate the evidence behind
        them, and count how many are contradicted. Predicates absent from the
        packet are simply missing from the result, which is what drives the
        coverage component of confidence.
        """
        found: dict[str, Claim] = {}
        evidence: dict[str, Evidence] = {}
        contradicted = self.contradicted_claim_ids()
        contradictions = 0

        for predicate in predicates:
            claims = self.claims_with_predicate(predicate)
            if not claims:
                continue
            claim = claims[0]
            found[predicate] = claim
            for item in self.evidence_for_claim(claim):
                evidence.setdefault(item.id, item)
            if claim.id in contradicted:
                contradictions += 1

        return Reading(
            claims=found,
            evidence=tuple(sorted(evidence.values(), key=lambda item: item.id)),
            contradictions=contradictions,
            expected=len(predicates),
        )

    def known_ids(self) -> frozenset[str]:
        """Return every addressable id in this IR. Used by artifact validation."""
        ids: set[str] = set()
        ids.update(item.id for item in self.entities)
        ids.update(item.id for item in self.claims)
        ids.update(item.id for item in self.evidence)
        ids.update(item.id for item in self.assumptions)
        ids.update(item.id for item in self.relationships)
        return frozenset(ids)
