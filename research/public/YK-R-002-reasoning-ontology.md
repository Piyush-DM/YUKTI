# Reasoning Ontology

| | |
|---|---|
| **Document ID** | YK-R-002 |
| **Source** | `choir/research/phase-1-foundations/reasoning_ontology.md` (002) |
| **Series** | CHOIR Research Programme |
| **Revision** | A |
| **Status** | Active |
| **Last Updated** | 2026-08-23 |

## Abstract

This document specifies how CHOIR's computational primitives are organised (§1): a three-layer
architecture (L0 Meta / L1 Core / L2 Domain) with dependencies pointing upward only, a
four-way entity hierarchy, seven relationship families with explicitly declared algebraic
properties, two separate inheritance systems, a namespace and versioning scheme, and nine
validation checks the ontology must pass against itself (§2–§8, summarised at §11). The
ontology being designed is an ontology of reasoning, not of any subject matter — it contains
no grahas, no statutes, no diagnoses; those live in domain layers that attach to it
(§1, §6). The source carries the status "Draft for review": it is drafted but
**not accepted as specification**,
and per `MANIFESTO.md` — as the source itself states at §8 — the ontology is a hypothesis
and needs its own acceptance tests.

## Research Question

The source states its own framing at §1: `computational_primitives.md` established *which*
primitives exist and why; this document specifies how they are **organised** — "the class
hierarchy, the relationship hierarchy, how properties and rules inherit, how domain layers
attach without contaminating the core, how names are scoped, and how the whole thing changes
over time without breaking anything that depends on it" (§1).

The document declares its dependency on `computational_primitives.md`, and declares that it
feeds `knowledge_graph_spec.md`, `choir_intermediate_representation.md`, and
`domain_independence.md`. It records the reserved DAALE boundaries it touches as
`daale/ontology/base.py` and `relationships.py` (front matter).

## Finding

### Three layers, dependencies upward only

The ontology is stratified into three layers with a strict dependency direction: nothing at a
lower number may reference anything at a higher number (§2).

| Layer | Contains | Change policy (as stated) |
|---|---|---|
| **L0 · META** | Primitive kinds, admission criteria, the type system — what kinds of thing can exist | "Changes: almost never. Requires constitutional review." |
| **L1 · CORE** | Domain-independent reasoning: Entity, Rule, Evidence, Exception, Conflict, Context… | "Changes: rarely, versioned, supersession only." |
| **L2 · DOMAIN** | Subject-matter vocabulary: `jyotisha:Graha` · `law:Statute` · `med:Diagnosis` | "Changes: freely, independently per domain." |

The source characterises this as "the domain-independence claim made structural" (§2): if a
Jyotiṣa requirement forces a change at L1, either the change is genuinely universal — and
must be justified in all five reference domains — or the design has leaked. It notes that
`domain_independence.md` §6 turns this into a measurable acceptance criterion, namely that
the number of L1 edits required to onboard a new domain should be zero (§2).

§2.1 tabulates what may live at each layer. Subject nouns (Graha, Statute, Drug) are
forbidden at L0 and L1 and defined only at L2. Precedence *orderings* and confidence *weights*
are marked forbidden at L1 and defined at L2; derived-fact computation (kernels) is marked
*interface only* at L1, with the implementation at L2. The precedence machinery and the
confidence structure are defined at L1. The source identifies the last four rows of that
table as "the ones that leak in practice" and states the governing pattern: **L1 owns the mechanism, L2 owns the parameters** (§2.1).
Its worked instances of the pattern: conflict resolution machinery is universal, but the fact
that a mūla text outranks a ṭīkā is a Jyotiṣa fact; confidence aggregation is universal, but
the weight assigned to scholarly consensus is domain-calibrated (§2.1).

### Entity hierarchy: a four-way split

The top-level split follows §2 of `computational_primitives.md` — the *reasoning-about /
reasoning-with* axis (§3). Under `CHOIRObject` (L0, everything addressable) sit four
branches:

- **Referent** — things reasoned ABOUT: `Entity` (identity-bearing, with `Agent`,
  `PhysicalEntity`, `AbstractEntity`, `SituationalEntity`), `Occurrent` (`Event`, `Process`,
  `Phase`), and `Quality` (`Attribute`, `State`, `Measure`).
- **Proposition** — things that can be true: `Condition` (evaluated to select), `Assertion`
  (claimed to hold), `Constraint` (enforced to reject), the last subdividing into
  `IntegrityConstraint`, `ApplicabilityConstraint`, and `NormativeConstraint` (violable by
  design).
- **ReasoningArtefact** — things reasoned WITH: `Rule`, `Exception` (with
  `RebuttingDefeater`, `UndercuttingDefeater`, `PremiseDefeater`), `Inference`, `Evidence`,
  `Conflict`, `Resolution`, `Proposal`, `Decision`.
- **MetaObject** — things ABOUT the reasoning: `Context`, `Provenance`, `ConfidenceRecord`,
  `Trace`, and `Source` (with `Text`, `Locus`, `Edition`, `Author`, `Tradition`).

§3.1 records three placements as contested rather than settled:

- **`Process` and `Phase`** are admitted at L1 but "were not in the 001 primitive set." They
  are admitted as *defined terms* (composites) because daśā systems, litigation stages,
  disease courses and project phases all instantiate them identically — the source calls this
  "a strong C3 signal even though they fail C2" (§3.1).
- **`Measure`** carries a `scale_type` field (nominal / ordinal / interval / ratio), because
  the scale type determines which operations are legal. Ṣaḍbala strength units, GRADE
  recommendation levels and credit ratings are ordinal, and the source states that averaging
  ordinals is a category error that "appears constantly in scoring systems"; the ontology's
  contribution is to make the error *detectable* (§3.1).
- **`SituationalEntity`** "remains the open question flagged in 001 §6.1." It is retained as
  a sub-kind rather than dissolved into `Entity + part-of + Context` on fidelity grounds — a
  bhāva, a legal office and an anatomical site are treated by their corpora as things with
  their own significations, not merely as positions. The source records this explicitly as
  "contested, not resolved" (§3.1).

### Relationships are first-class, and must declare their algebra

Because relationships are first-class objects (001 §3.6), they carry their own hierarchy and
metadata schema (§4). Seven families: `StructuralRelation`, `PositionalRelation`,
`TemporalRelation` (Allen's 13), `EpistemicRelation`, `NormativeRelation`,
`InfluenceRelation` (marked second-order), and `CausalRelation`.

Every relationship type must declare arity, transitivity, symmetry, reflexivity, and inverse;
the source states plainly that "None are assumed" (§4.1). The declared table covers
`subclass-of`, `part-of`, `instance-of`, `occupies`, `aspects`, `supports`, `contradicts`,
`derives-from`, `strengthens`, and `produces`. The table records `contradicts` as symmetric
with itself as inverse, `strengthens` with arity "2 (target may be an edge)", and `produces`
with arity *n*. The source notes that `instance-of` being non-transitive while
`subclass-of` is transitive "is the classic punning trap; it is declared explicitly to keep
reasoners from composing them" (§4.1).

§4.2 states a consequence for storage: `InfluenceRelation` and `UndercuttingDefeater` may
target a **relationship instance**, not just an object. This is given as "the structural
reason CHOIR cannot use plain RDF triples as its storage model without reification — see
`knowledge_graph_spec.md` §2" (§4.2). The illustration used is
`Exaltation(Guru, Karka)` strengthening the edge `Guru ──occupies──▶ Karka`.

### Two inheritance systems, kept separate

The source states that keeping property inheritance and rule inheritance separate "prevents
most of the pathologies that afflict large ontologies" (§5).

**Property inheritance (§5.1).** Identity-defining properties (identity criterion, primitive
kind) and structural properties (arity, algebraic properties of relations) use strict single
inheritance and override is **forbidden**. Defeasible properties (typical values, default
significations) inherit multiply via role mixins and may be overridden with a record.
Annotational properties (labels, comments) inherit multiply and override freely.

Strict single inheritance for identity is justified as eliminating the diamond problem "where
it would actually hurt." Role-like multiple membership is expressed with mixins carrying only
defeasible properties: a graha that is both a natural malefic and a functional benefic for a
given ascendant "is not a multiple-inheritance conflict; it is one entity with two
context-scoped defeasible property sets" (§5.1).

Every override is recorded as an object, not silently applied:

```
Override ::= ⟨ subject, property, inherited_value, override_value,
               context, justification, source ⟩
```

The source states that this "is what makes exceptional significations explainable rather than
mysterious. An un-recorded override is a specification bug" (§5.1).

**Rule inheritance (§5.2).** For a rule *R* scoped to class *C*, with *D* a subclass of *C*:

1. **Applicability inherits downward** — *R* applies to instances of *D*.
2. **Specificity inverts priority** — a rule scoped to *D* outranks a rule scoped to *C* on
   *lex specialis* grounds; the child wins. The source identifies this as *utsarga/apavāda*,
   "the same principle Pāṇini encodes in his paribhāṣā apparatus and that legal systems
   encode as *generalia specialibus non derogant*."
3. **Conclusions do not merge** — two applicable rules produce two Inference objects, both
   recorded; adjudication happens later in the conflict phase, "never during matching."
   `execution_pipeline.md` §4 is cited as making the *saturate-then-adjudicate* ordering
   mandatory.
4. **Exceptions inherit, and may be excepted** — an exception attached to *R* applies to *D*'s
   instances unless a *D*-scoped exception-to-the-exception overrides it.

The source volunteers that point 3 "is the design decision most likely to be questioned,
since it is more expensive than resolving during matching," and defends it on the ground that
precedence can depend on the full set of fired rules: a rule may win by *lex specialis*
against one competitor and lose by source authority against another, "and neither judgement
is available mid-match" (§5.2).

**Deliberate absence (§5.3).** There is no default-value inheritance for states. States are
time-indexed observations, and inheriting them from a class "would fabricate observations."
Only attributes and defeasible significations inherit.

### The extension contract for domain layers

§6.1 states the contract as two explicit lists. A domain layer **may** define new subject
classes under `Entity`, `Occurrent`, `Quality`; define new relationship subtypes under an
existing L1 family; supply precedence orderings, source-authority rankings, and confidence
weights; register derived-fact kernels against the L1 kernel interface; and declare context
dimensions beyond the six core ones.

A domain layer **may not** add a new top-level branch to the entity hierarchy; add a new
relationship *family*; change the arity, metadata schema, or algebraic declarations of an L1
relation; alter conflict, confidence, or explanation machinery; or introduce a new primitive
kind.

The escalation path is stated rather than left implicit: "If a domain cannot be expressed
within these bounds, that is a finding about the core ontology, and it is escalated as a
constitutional change under §7.3 — not patched locally" (§6.1).

**Derived-fact kernels (§6.2)** are the one place domains legitimately need arbitrary
computation — the source's examples are "which house is Jupiter in, counted from the Moon",
"is this filing within the limitation period", and "is this dose above the renal-adjusted
maximum". These are isolated behind a narrow L1 interface:

```
Kernel ::= ⟨ name, input_types, output_type, context_requirements,
             determinism_guarantee, provenance ⟩
```

Kernels must be deterministic and side-effect free, because the traceability invariant (001
§3.16) requires re-derivation to reproduce identical results; a kernel consulting the wall
clock or a mutable external source "breaks replay and is rejected." Kernel outputs enter the
graph as ordinary `State` objects with provenance naming the kernel and its version, so a
conclusion depending on an ephemeris computation can be traced to *which* ephemeris (§6.2).

### Namespaces, identity, and versioning

**Namespaces (§7.1).** `choir:meta/…` (L0), `choir:core/…` (L1), `choir:jyotisha/…`,
`choir:law/us-federal/…` (sub-scoped by jurisdiction), `choir:med/…` (L2). Identifiers are
stable and opaque; display labels are separate and may be multilingual —
`choir:jyotisha/graha/Guru` never changes even if the preferred English label does. A
Sanskrit term gets one canonical identifier in IAST transliteration, with Devanāgarī, SLP1
and vernacular labels attached as annotations. Homonyms are namespaced apart, never merged:
`choir:jyotisha/Guru` (the planet) and `choir:jyotisha/social/Guru` (the teacher) are
distinct identifiers, and symbol resolution between them "is a compiler task with recorded
justification, not an ontology shortcut" — see `shloka_compiler.md` §5.

**Two identity schemes (§7.2).** Nominal identifiers (`choir:core/Evidence`) apply to
ontology classes, relations, and contexts and are stable, human-readable, and curated.
Content addresses (`sha256:…` of canonical form) apply to rules, inferences, and evidence
instances and are immutable, deduplicating, and forgery-evident. The source draws out one
consequence: "two texts that state the same rule produce the same rule hash", so they unify
into one rule with two provenance records — "exactly the 'independent attestation' signal the
evidence model needs (`evidence_model.md` §4.3)". Obtaining this from the identity scheme
rather than from a matching heuristic is described as "a significant simplification" (§7.2).

**Versioning (§7.3).** Semantic versioning per namespace, with declared change classes:

| Change | Version bump | Allowed at |
|---|---|---|
| Add a class or relation subtype | MINOR | L1, L2 |
| Add an optional property | MINOR | L1, L2 |
| Deprecate (retain, mark) | MINOR | L1, L2 |
| Tighten a constraint | MAJOR | L1 with review, L2 free |
| Change an identity criterion | MAJOR | L0/L1 constitutional review only |
| Remove anything | MAJOR | Constitutional review only |

The governing rule is **supersession, never mutation**: an ontology object is immutable once
published, a change creates a new version and a `supersedes` edge, and "any conclusion ever
drawn under version *n* remains re-derivable under version *n* forever." The source states
the reason: "it is the only way to answer 'was this decision correct *at the time*', which is
the question every audit actually asks" (§7.3). The deprecation lifecycle is
`active → deprecated (with replacement) → retired (no new references)`; nothing is deleted.

**Compatibility contract (§7.4).** Because DAALE modules will attach to these definitions,
the source states the contract explicitly: a dependent pinned to `choir:core@1.x` will not
break on any MINOR release; MAJOR releases publish a migration note listing affected
identifiers and their replacements; content-addressed objects never break, because "the hash
*is* the version."

### The ontology's own acceptance tests

§8 opens by stating that "The ontology is a hypothesis (per `MANIFESTO.md`) and needs its own
acceptance tests," and records that the files these checks should populate —
`choir/ontology/primitive_validation.md` and `relationship_validation.md` — are **currently
empty**. Nine checks are specified:

| # | Check | Method | Fails if |
|---|---|---|---|
| V1 | Every class traces to an admitted primitive or a declared composite | Static walk of the hierarchy | An orphan class exists |
| V2 | No L1 object references an L2 identifier | Namespace dependency scan | Any upward reference |
| V3 | Every relation declares arity + algebraic properties | Schema completeness check | Any undeclared |
| V4 | Every override is recorded as an Override object | Diff inherited vs effective properties | A silent override |
| V5 | Identity criteria are stated positively and negatively | Manual review against C1 | Either half missing |
| V6 | Three-domain instantiation for every L1 class | Portability matrix (`domain_independence.md` §6) | Fewer than 3 |
| V7 | Every class has a stated falsifier | Register completeness | Any blank |
| V8 | Hierarchy is acyclic under `subclass-of` and `part-of` | Cycle detection | Any cycle |
| V9 | No inheritance of `State` defaults | Static rule check | Any state default |

The source singles out V6: "the expensive one and the one that matters most: it is the
ontology's own C3 test, run continuously rather than once" (§8). It does not report results
for any of V1–V9 — these are specified checks, not executed ones.

### Worked example: one configuration, three domains

§9 instantiates the same L1 structure in three L2 vocabularies with no L1 changes, described
as "the domain-independence claim in miniature", with the full treatment deferred to
`domain_independence.md`.

| L1 structure | Jyotiṣa | Law | Medicine |
|---|---|---|---|
| `Entity` | Guru (graha) | Lessee (party) | Patient |
| `Entity` | Karka (rāśi) | Leased premises | Renal system |
| `PositionalRelation: occupies` | Guru occupies Karka | Lessee occupies premises | — |
| `State` | Guru is exalted | Lease is in default | eGFR is 28 |
| `Attribute` | Guru is a natural benefic | Instrument is a lease | Patient's blood type |
| `Condition` | Guru in a kendra from Candra | Default continuing > 30 days | eGFR < 30 |
| `Rule` | Gajakesarī yoga arises | Right of re-entry accrues | Reduce dose |
| `Exception` (undercutting) | Nīca-bhaṅga cancels | Waiver by acceptance of rent | Dialysis in progress |
| `InfluenceRelation` | Aspect strengthens the yoga | Mitigation reduces relief | Comorbidity worsens prognosis |
| `Context` | Rāśi chart, natal, Parāśara school | Jurisdiction, court level | Guideline version, care setting |
| `Source` | BPHS, ch./v., edition | Statute § | Guideline §, grade |

The source draws attention to the Exception row: all three are *undercutting*, not rebutting.
"Waiver does not mean 'the opposite of re-entry'; nīca-bhaṅga does not mean 'the inverse of
the yoga's results'; dialysis does not mean 'increase the dose.'" The typology from 001 §3.12
"earns its place identically across all three" (§9). Note that the `occupies` row has no
Medicine instantiation — the cell is empty in the source.

### Status of this document

The source is headed **"Status: Draft for review"** and belongs to Phase 1 — Computational
Foundations. It is drafted but **not accepted as specification**. The document-level statement
is made by `choir/research/README.md`, which records that all 18 deliverables are drafted, none
accepted, and that "Every document is a hypothesis, per `MANIFESTO.md`"; `MANIFESTO.md` itself
states the underlying formulation as "Treat every computational object as a hypothesis rather
than an established truth." The source makes the same claim of the ontology at §8. The
acceptance tests V1–V9 that would test this one are specified but their target files are
recorded as empty.

## Architectural Implications

**For CHOIR's storage layer.** §4.2 states that because `InfluenceRelation` and
`UndercuttingDefeater` may target a relationship instance rather than an object, CHOIR
"cannot use plain RDF triples as its storage model without reification," and points at
`knowledge_graph_spec.md` §2. The summary (§11) restates this as the ontology forcing "the
storage decision in 003."

**For the execution pipeline.** Rule inheritance point 3 — conclusions never merge during
matching — is stated as requiring `execution_pipeline.md` §4 to make the
*saturate-then-adjudicate* ordering mandatory (§5.2). Adjudication cannot happen at match
time because precedence depends on the full set of fired rules.

**For the evidence model.** Content addressing of rule instances yields independent
attestation detection without a matching heuristic: two texts stating the same rule produce
the same hash and unify into one rule with two provenance records, which is the signal
`evidence_model.md` §4.3 needs (§7.2).

**For the compiler.** Homonym resolution (e.g. `choir:jyotisha/Guru` vs
`choir:jyotisha/social/Guru`) is assigned to the compiler as a task with recorded
justification rather than being handled by merging identifiers in the ontology — see
`shloka_compiler.md` §5 (§7.1).

**For domain independence as a measurable claim.** §2 states that the layer discipline is the
domain-independence claim made structural, and that `domain_independence.md` §6 converts it
into an acceptance criterion: zero L1 edits to onboard a new domain. V6 (three-domain
instantiation for every L1 class) is designated the ontology's own C3 test, "run continuously
rather than once" (§8).

**For DAALE.** The source records the reserved DAALE boundaries it touches as
`daale/ontology/base.py` and `relationships.py` (front matter), and §10 flags
`daale/ontology/decision.py` as the boundary affected by the unresolved question of whether
`Decision` belongs at L1 at all. §7.4 states the compatibility contract explicitly "Because
DAALE modules will attach to these definitions": MINOR releases are non-breaking for a
dependent pinned to `choir:core@1.x`, MAJOR releases must publish a migration note listing
affected identifiers and their replacements, and content-addressed objects never break.

**For audit.** Supersession-never-mutation is justified in the source not as storage
fastidiousness but as the only way to answer whether a decision was correct at the time
(§7.3).

## Open Questions

The source records five open questions at §10, verbatim in substance:

1. **`SituationalEntity`** — genuine sub-kind, or `Entity + part-of + Context`? Carried
   forward from 001 §6.1, "still unresolved."
2. **Are `Process` and `Phase` needed at L1**, or should daśā / litigation-stage structures be
   L2 patterns over `Event` + `part-of`? "Retained provisionally on C3 grounds."
3. **Context dimension extensibility.** Permitting L2 to add context dimensions (§6.1) risks
   domains inventing incomparable lattices, "which would break cross-domain conflict
   resolution. May need a registration discipline."
4. **Mixin conflict.** Two defeasible mixins supplying contradictory defaults currently
   resolve by context specificity. "Whether that is always right is untested."
5. **Should `Decision` be L1 at all?** It may be an institutional-process notion rather than a
   reasoning notion. Relevant to the reserved `daale/ontology/decision.py` boundary.

Further items the source records as unfinished or unverified elsewhere in the text:

- `choir/ontology/primitive_validation.md` and `relationship_validation.md` are stated to be
  **currently empty** (§8); the nine validation checks V1–V9 are specified but no results are
  reported for them.
- `Process` and `Phase` are admitted at L1 despite failing C2, on a C3 signal alone (§3.1).
- The rule-inheritance decision that conclusions do not merge during matching is
  self-identified as "the design decision most likely to be questioned" and as more expensive
  than the alternative (§5.2).

## Related Documents

- [YK-R-001 — Computational Primitive Specification](YK-R-001-computational-primitive-specification.md) — declared dependency; supplies the admitted primitive set, the reasoning-about / reasoning-with axis (§2 of 001), first-class relationships (001 §3.6), the defeater typology (001 §3.12), the traceability invariant (001 §3.16), and the carried-forward `SituationalEntity` question (001 §6.1).
- [YK-R-003 — Knowledge Graph Specification](YK-R-003-knowledge-graph-specification.md) — declared as fed by this document; §4.2 states the second-order targeting requirement that forces the storage decision (`knowledge_graph_spec.md` §2).
- [YK-R-006 — Shloka Compiler](YK-R-006-shloka-compiler.md) — cited at §7.1 as owning homonym symbol resolution with recorded justification (`shloka_compiler.md` §5).
- [YK-R-009 — Evidence Model](YK-R-009-evidence-model.md) — cited at §7.2 for the independent-attestation signal (`evidence_model.md` §4.3).
- [YK-R-013 — CHOIR Intermediate Representation](YK-R-013-choir-intermediate-representation.md) — declared as fed by this document (front matter).
- [YK-R-015 — Execution Pipeline](YK-R-015-execution-pipeline.md) — cited at §5.2 as making the *saturate-then-adjudicate* ordering mandatory (`execution_pipeline.md` §4).
- [YK-R-016 — Domain Independence](YK-R-016-domain-independence.md) — declared as fed by this document; cited at §2 and §8 for the zero-L1-edits acceptance criterion and the V6 portability matrix (`domain_independence.md` §6).
