# 002 — Reasoning Ontology

**Status:** Draft for review
**Phase:** 1 — Computational Foundations
**Depends on:** `computational_primitives.md`
**Feeds:** `knowledge_graph_spec.md`, `choir_intermediate_representation.md`, `domain_independence.md`
**Reserved DAALE boundaries touched:** `daale/ontology/base.py`, `relationships.py`

---

## 1. What this document specifies

`computational_primitives.md` established *which* primitives exist and why. This document
specifies how they are **organised**: the class hierarchy, the relationship hierarchy, how
properties and rules inherit, how domain layers attach without contaminating the core, how
names are scoped, and how the whole thing changes over time without breaking anything that
depends on it.

The ontology being designed here is an ontology **of reasoning**, not of any subject
matter. It contains no grahas, no statutes, no diagnoses. Those live in domain layers that
attach to it (§6).

---

## 2. Layer architecture

Three layers, with a strict dependency direction. Nothing at a lower number may reference
anything at a higher number.

```
┌─────────────────────────────────────────────────────────┐
│  L0 · META          What kinds of thing can exist       │
│  Primitive kinds, admission criteria, the type system   │
│  Changes: almost never. Requires constitutional review. │
├─────────────────────────────────────────────────────────┤
│  L1 · CORE          Domain-independent reasoning        │
│  Entity, Rule, Evidence, Exception, Conflict, Context…  │
│  Changes: rarely, versioned, supersession only.         │
├─────────────────────────────────────────────────────────┤
│  L2 · DOMAIN        Subject-matter vocabulary           │
│  jyotisha:Graha  ·  law:Statute  ·  med:Diagnosis       │
│  Changes: freely, independently per domain.             │
└─────────────────────────────────────────────────────────┘
              dependency points upward only
```

**The layer discipline is the domain-independence claim made structural.** If a Jyotiṣa
requirement forces a change at L1, either the change is genuinely universal (and must be
justified in all five reference domains) or the design has leaked. `domain_independence.md`
§6 turns this into a measurable acceptance criterion: the number of L1 edits required to
onboard a new domain should be zero.

### 2.1 What may live at each layer

| | L0 Meta | L1 Core | L2 Domain |
|---|---|---|---|
| Primitive kinds | ✅ defined | referenced | referenced |
| Reasoning artefacts (Rule, Evidence, Conflict) | — | ✅ defined | specialised |
| Subject nouns (Graha, Statute, Drug) | ✗ forbidden | ✗ forbidden | ✅ defined |
| Precedence *machinery* | — | ✅ defined | — |
| Precedence *orderings* (which source outranks which) | — | ✗ forbidden | ✅ defined |
| Derived-fact computation (kernels) | — | interface only | ✅ implementation |
| Confidence *structure* | — | ✅ defined | — |
| Confidence *weights* | — | ✗ forbidden | ✅ defined |

The last four rows are the ones that leak in practice. The pattern is consistent:
**L1 owns the mechanism, L2 owns the parameters.** Conflict resolution machinery is
universal; the fact that a mūla text outranks a ṭīkā is a Jyotiṣa fact. Confidence
aggregation is universal; the weight assigned to scholarly consensus is domain-calibrated.

---

## 3. Entity hierarchy

The top-level split follows directly from §2 of `computational_primitives.md`: the
*reasoning-about / reasoning-with* axis.

```
CHOIRObject                            (L0 — everything addressable)
│
├── Referent                           things reasoned ABOUT
│   ├── Entity                         identity-bearing (§3.1 of 001)
│   │   ├── Agent                      can act; can bear obligation
│   │   ├── PhysicalEntity
│   │   ├── AbstractEntity
│   │   └── SituationalEntity          exists relative to a structure
│   ├── Occurrent                      happens rather than holds
│   │   ├── Event                      point or bounded
│   │   ├── Process                    extended, internally structured
│   │   └── Phase                      a bounded stage of a Process
│   └── Quality                        how something is
│       ├── Attribute                  definitional
│       ├── State                      time-indexed
│       └── Measure                    quantity + unit + scale type
│
├── Proposition                        things that can be true
│   ├── Condition                      evaluated to select
│   ├── Assertion                      claimed to hold
│   └── Constraint                     enforced to reject
│       ├── IntegrityConstraint
│       ├── ApplicabilityConstraint
│       └── NormativeConstraint        violable by design
│
├── ReasoningArtefact                  things reasoned WITH
│   ├── Rule                           composite (§4 of 001)
│   ├── Exception
│   │   ├── RebuttingDefeater
│   │   ├── UndercuttingDefeater
│   │   └── PremiseDefeater
│   ├── Inference
│   ├── Evidence
│   ├── Conflict
│   ├── Resolution
│   ├── Proposal
│   └── Decision
│
└── MetaObject                         things ABOUT the reasoning
    ├── Context
    ├── Provenance
    ├── ConfidenceRecord
    ├── Trace
    └── Source
        ├── Text
        ├── Locus                      chapter/verse/section address
        ├── Edition
        ├── Author
        └── Tradition
```

### 3.1 Notes on contested placements

**`Process` and `Phase`** are admitted at L1 but were not in the 001 primitive set. They
are composites (`Process` = an Occurrent with internal `part-of` structure and a temporal
extent; `Phase` = a `part-of` a Process). They earn a place in the hierarchy as *defined
terms* because daśā systems, litigation stages, disease courses and project phases all
instantiate them identically — a strong C3 signal even though they fail C2.

**`Measure`** carries a `scale_type` field (nominal / ordinal / interval / ratio). This is
not pedantry: it determines which operations are legal. Ṣaḍbala strength units, GRADE
recommendation levels and credit ratings are **ordinal**, and averaging ordinals is a
category error that appears constantly in scoring systems. The ontology makes the error
detectable.

**`SituationalEntity`** remains the open question flagged in 001 §6.1. It is retained as a
sub-kind rather than dissolved into `Entity + part-of + Context`, on fidelity grounds: a
bhāva, a legal office and an anatomical site are all treated by their corpora as things
with their own significations, not merely as positions. Recorded as contested, not
resolved.

---

## 4. Relationship hierarchy

Relationships are first-class objects (001 §3.6), so they have their own hierarchy and
their own metadata schema.

```
Relationship
├── StructuralRelation      instance-of, subclass-of, part-of, member-of
├── PositionalRelation      occupies, contained-in, adjacent-to, aspects
├── TemporalRelation        Allen's 13
├── EpistemicRelation       supports, contradicts, cites, derives-from, attests, mentions
├── NormativeRelation       obliges, permits, forbids, empowers
├── InfluenceRelation       strengthens, weakens, modulates, cancels    ← second-order
└── CausalRelation          produces, prevents, enables
```

### 4.1 Declared algebraic properties

Every relationship type must declare these. None are assumed.

| Type | Arity | Transitive | Symmetric | Reflexive | Inverse |
|---|---|---|---|---|---|
| `subclass-of` | 2 | ✅ | ✗ | ✅ | `superclass-of` |
| `part-of` | 2 | ✅ | ✗ | ✗ | `has-part` |
| `instance-of` | 2 | ✗ | ✗ | ✗ | `has-instance` |
| `occupies` | 2 | ✗ | ✗ | ✗ | `occupied-by` |
| `aspects` | 2 | ✗ | ✗ | ✗ | `aspected-by` |
| `supports` | 2 | ✗ | ✗ | ✗ | `supported-by` |
| `contradicts` | 2 | ✗ | ✅ | ✗ | self |
| `derives-from` | 2 | ✅ | ✗ | ✗ | `derived-into` |
| `strengthens` | 2 (target may be an edge) | ✗ | ✗ | ✗ | `strengthened-by` |
| `produces` | n | ✗ | ✗ | ✗ | `produced-by` |

`instance-of` being non-transitive while `subclass-of` is transitive is the classic
punning trap; it is declared explicitly to keep reasoners from composing them.

### 4.2 Second-order targeting

`InfluenceRelation` and `UndercuttingDefeater` may target a **relationship instance**, not
just an object. This is the structural reason CHOIR cannot use plain RDF triples as its
storage model without reification — see `knowledge_graph_spec.md` §2.

```
    Guru ──occupies──▶ Karka
                │
                └──◀── strengthens ── Exaltation(Guru, Karka)
```

---

## 5. Inheritance

Two distinct inheritance systems operate, and keeping them separate prevents most of the
pathologies that afflict large ontologies.

### 5.1 Property inheritance

| Property class | Inheritance | Override |
|---|---|---|
| **Identity-defining** (identity criterion, primitive kind) | Strict single inheritance | ✗ Forbidden |
| **Structural** (arity, algebraic properties of relations) | Strict single inheritance | ✗ Forbidden |
| **Defeasible** (typical values, default significations) | Multiple, via role mixins | ✅ Permitted, with a record |
| **Annotational** (labels, comments) | Multiple | ✅ Free |

**Strict single inheritance for identity** eliminates the diamond problem where it would
actually hurt. Role-like multiple membership is expressed with **mixins** that carry only
defeasible properties. A graha that is both a natural malefic and a functional benefic for
a given ascendant is not a multiple-inheritance conflict; it is one entity with two
context-scoped defeasible property sets.

**Every override is recorded as an object**, not silently applied:

```
Override ::= ⟨ subject, property, inherited_value, override_value,
               context, justification, source ⟩
```

This is what makes exceptional significations explainable rather than mysterious. An
un-recorded override is a specification bug.

### 5.2 Rule inheritance

Rules inherit differently from properties, and the difference matters.

When rule *R* is scoped to class *C*, and *D* is a subclass of *C*:

1. **Applicability inherits downward.** *R* applies to instances of *D*.
2. **Specificity inverts priority.** A rule scoped to *D* outranks a rule scoped to *C* on
   *lex specialis* grounds — the child wins. This is *utsarga/apavāda*, and it is the same
   principle Pāṇini encodes in his paribhāṣā apparatus and that legal systems encode as
   *generalia specialibus non derogant*.
3. **Conclusions do not merge.** Two applicable rules produce two Inference objects, both
   recorded. Adjudication happens later, in the conflict phase — never during matching.
   (`execution_pipeline.md` §4 makes the *saturate-then-adjudicate* ordering mandatory.)
4. **Exceptions inherit, and may be excepted.** An exception attached to *R* applies to
   *D*'s instances unless a *D*-scoped exception-to-the-exception overrides it.

Point 3 is the design decision most likely to be questioned, since it is more expensive
than resolving during matching. It is required because precedence can depend on the *full
set* of fired rules — a rule may win by *lex specialis* against one competitor and lose by
source authority against another, and neither judgement is available mid-match.

### 5.3 What is deliberately absent

There is no **default-value inheritance for states**. States are time-indexed
observations; inheriting them from a class would fabricate observations. Only attributes
and defeasible significations inherit. This closes a common source of phantom facts.

---

## 6. Domain independence, structurally

### 6.1 The extension contract

A domain layer (L2) may:

- ✅ Define new subject classes under `Entity`, `Occurrent`, `Quality`
- ✅ Define new relationship subtypes under an existing L1 family
- ✅ Supply precedence orderings, source-authority rankings, confidence weights
- ✅ Register derived-fact kernels against the L1 kernel interface
- ✅ Declare context dimensions beyond the six core ones

A domain layer may **not**:

- ✗ Add a new top-level branch to the entity hierarchy
- ✗ Add a new relationship *family*
- ✗ Change the arity, metadata schema, or algebraic declarations of an L1 relation
- ✗ Alter conflict, confidence, or explanation machinery
- ✗ Introduce a new primitive kind

If a domain cannot be expressed within these bounds, that is a finding about the core
ontology, and it is escalated as a constitutional change under §7.3 — not patched locally.

### 6.2 Derived-fact kernels

The one place domains legitimately need arbitrary computation is derived facts: "which
house is Jupiter in, counted from the Moon"; "is this filing within the limitation
period"; "is this dose above the renal-adjusted maximum".

These are isolated behind a narrow L1 interface:

```
Kernel ::= ⟨ name, input_types, output_type, context_requirements,
             determinism_guarantee, provenance ⟩
```

**Kernels must be deterministic and side-effect free**, because the traceability
invariant (001 §3.16) requires re-derivation to reproduce identical results. A kernel that
consults the wall clock or a mutable external source breaks replay and is rejected.

Kernel outputs enter the graph as ordinary `State` objects with provenance naming the
kernel and its version — so a conclusion that depended on an ephemeris computation can be
traced to *which* ephemeris.

---

## 7. Namespaces and versioning

### 7.1 Namespace scheme

```
choir:meta/…            L0
choir:core/…            L1
choir:jyotisha/…        L2
choir:law/us-federal/…  L2, sub-scoped by jurisdiction
choir:med/…             L2
```

Identifiers are **stable and opaque**; display labels are separate and may be multilingual.
`choir:jyotisha/graha/Guru` never changes even if the preferred English label does. A
Sanskrit term gets one canonical identifier in IAST transliteration, with Devanāgarī,
SLP1 and vernacular labels attached as annotations.

**Homonyms are namespaced apart, never merged.** `choir:jyotisha/Guru` (the planet) and
`choir:jyotisha/social/Guru` (the teacher) are distinct identifiers. Symbol resolution
between them is a compiler task with recorded justification, not an ontology shortcut —
see `shloka_compiler.md` §5.

### 7.2 Two identity schemes, used for different things

| Scheme | Applies to | Form | Property |
|---|---|---|---|
| **Nominal** | Ontology classes, relations, contexts | `choir:core/Evidence` | Stable, human-readable, curated |
| **Content-addressed** | Rules, inferences, evidence instances | `sha256:…` of canonical form | Immutable, deduplicating, forgery-evident |

Content addressing gives an important property for free: **two texts that state the same
rule produce the same rule hash**, so they unify into one rule with two provenance records
— which is exactly the "independent attestation" signal the evidence model needs
(`evidence_model.md` §4.3). Getting this from the identity scheme rather than from a
matching heuristic is a significant simplification.

### 7.3 Versioning policy

Semantic versioning per namespace, with change classes:

| Change | Version bump | Allowed at |
|---|---|---|
| Add a class or relation subtype | MINOR | L1, L2 |
| Add an optional property | MINOR | L1, L2 |
| Deprecate (retain, mark) | MINOR | L1, L2 |
| Tighten a constraint | MAJOR | L1 with review, L2 free |
| Change an identity criterion | MAJOR | L0/L1 constitutional review only |
| Remove anything | MAJOR | Constitutional review only |

**Supersession, never mutation.** An ontology object is immutable once published. A change
creates a new version and a `supersedes` edge. Any conclusion ever drawn under version *n*
remains re-derivable under version *n* forever. This is not storage fastidiousness — it is
the only way to answer "was this decision correct *at the time*", which is the question
every audit actually asks.

**Deprecation lifecycle:** `active → deprecated (with replacement) → retired (no new
references) `. Nothing is deleted.

### 7.4 Compatibility contract for dependents

Because DAALE modules will attach to these definitions, the contract must be explicit:

- A dependent pinned to `choir:core@1.x` will not break on any MINOR release.
- MAJOR releases publish a migration note listing affected identifiers and their
  replacements.
- Content-addressed objects never break: the hash *is* the version.

---

## 8. Validation of the ontology itself

The ontology is a hypothesis (per `MANIFESTO.md`) and needs its own acceptance tests.
These are the checks that should populate `choir/ontology/primitive_validation.md` and
`relationship_validation.md`, currently empty.

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

V6 is the expensive one and the one that matters most: it is the ontology's own C3 test,
run continuously rather than once.

---

## 9. Worked example — one configuration, three domains

The same L1 structure, instantiated in three L2 vocabularies, with no L1 changes. This is
the domain-independence claim in miniature; the full treatment is `domain_independence.md`.

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

Note the Exception row: all three are *undercutting*, not rebutting. Waiver does not mean
"the opposite of re-entry"; nīca-bhaṅga does not mean "the inverse of the yoga's results";
dialysis does not mean "increase the dose." The typology from 001 §3.12 earns its place
identically across all three.

---

## 10. Open questions

1. **`SituationalEntity`** — genuine sub-kind or `Entity + part-of + Context`? Carried
   forward from 001 §6.1, still unresolved.
2. **Are `Process` and `Phase` needed at L1** or should daśā/litigation-stage structures be
   L2 patterns over `Event` + `part-of`? Retained provisionally on C3 grounds.
3. **Context dimension extensibility.** Permitting L2 to add context dimensions (§6.1)
   risks domains inventing incomparable lattices, which would break cross-domain conflict
   resolution. May need a registration discipline.
4. **Mixin conflict.** Two defeasible mixins supplying contradictory defaults currently
   resolve by context specificity. Whether that is always right is untested.
5. **Should `Decision` be L1 at all?** It may be an institutional-process notion rather
   than a reasoning notion. Relevant to the reserved `daale/ontology/decision.py`
   boundary.

---

## 11. Summary

- Three layers: **L0 Meta / L1 Core / L2 Domain**, dependencies upward only. L1 owns
  mechanisms, L2 owns parameters.
- Entity hierarchy splits four ways: **Referent / Proposition / ReasoningArtefact /
  MetaObject** — the reasoning-about vs reasoning-with axis made structural.
- Seven relationship families, each declaring arity and algebraic properties explicitly;
  influence and undercutting defeaters may target **edges**, which forces the storage
  decision in 003.
- **Strict single inheritance** for identity, **mixins with recorded overrides** for
  defeasible properties, **no inheritance of state defaults**.
- Rules inherit applicability downward but priority inverts (*lex specialis* /
  *apavāda*); conclusions never merge during matching.
- **Nominal identifiers** for ontology objects, **content addresses** for instances — which
  makes independent attestation of the same rule detectable for free.
- **Supersession, never mutation**, so historical conclusions stay re-derivable.
- Nine validation checks (V1–V9) give the ontology its own acceptance criteria, populating
  the currently-empty `choir/ontology/*_validation.md` placeholders.
