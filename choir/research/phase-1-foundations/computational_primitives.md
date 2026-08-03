# 001 — Computational Primitive Specification

**Status:** Draft for review
**Phase:** 1 — Computational Foundations
**Depends on:** `MANIFESTO.md` (admission criteria question)
**Feeds:** `reasoning_ontology.md`, `knowledge_graph_spec.md`, `choir_intermediate_representation.md`
**Reserved DAALE boundaries touched:** `daale/ontology/base.py`, `relationships.py`, `evidence.py`, `confidence.py`

---

## 0. Purpose and epistemic status

This document defines the universal vocabulary that every CHOIR reasoning system uses,
regardless of domain. It does two things:

1. States the **admission test** a candidate primitive must pass (the constitutional
   question posed in `MANIFESTO.md`).
2. Applies that test to the fifteen candidates named in the research brief, and records
   which pass, which are demoted to composites, and which remain contested.

### 0.1 A note on what CHOIR claims

CHOIR compiles a reasoning *tradition* into executable form. It claims fidelity to what
a corpus says and how that corpus argues. It does **not** claim that the corpus is true.

This distinction is load-bearing, not diplomatic. It determines what the system can be
validated against:

| Claim CHOIR makes | Validated against |
|---|---|
| This rule is what the text says | Critical editions, scholar agreement |
| This inference follows from that rule | Formal semantics, proof checking |
| This conclusion was reached this way | Execution trace replay |
| This conclusion is *true of the world* | **Not claimed** |

The last row is why the same machinery generalises to law and medicine without
embarrassment. A statute is not "true"; it is *in force*. A clinical guideline is not
"true"; it is *recommended at grade B*. CHOIR models normative and interpretive systems,
where the object of study is the rule corpus itself. Where a domain *does* have outcome
ground truth (medicine, finance), that is an additional validation layer bolted on top —
see `confidence_framework.md` §7.

Any primitive whose definition presupposes that the corpus is factually correct is
rejected by construction.

---

## 1. The admission test

A candidate is admitted as a **primitive** only if it passes all seven necessary
conditions. Failing any one is disqualifying. Passing all seven is *not* automatically
sufficient — §1.8 gives the tie-break.

### 1.1 C1 — Identity

The candidate must be re-identifiable across time and across statements without appeal to
its storage location, its position in a list, or any implementation artefact.

> **Test:** Can two independent observers, given only the domain content, agree that
> occurrence *a* at t₁ and occurrence *b* at t₂ are the same thing?

Identity criteria must be stated positively (what makes two instances the same) *and*
negatively (what change makes them different). A candidate whose identity criterion is
"the same row in the same table" fails: that is an implementation detail.

### 1.2 C2 — Irreducibility

The candidate must not be losslessly expressible as a configuration of other admitted
primitives.

> **Test:** Attempt the reduction. If a faithful encoding exists using already-admitted
> primitives, and the encoding does not require a new edge type, new metadata slot, or new
> evaluation rule, the candidate is a **composite** and is demoted.

Irreducibility is relative to the current primitive set, so this test must be re-run
whenever the set changes. Demotion is not deletion: composites remain in the ontology as
*defined terms* (§4).

### 1.3 C3 — Domain independence

The candidate must be instantiable in at least three of the five reference domains
(Jyotiṣa, law, medicine, finance, engineering) with the *same* structure, differing only
in vocabulary.

> **Test:** Write the candidate's definition with every domain noun replaced by a
> variable. If the definition still reads coherently and the instantiations in three
> domains agree on structure, it passes.

A candidate that needs a different arity, a different evaluation rule, or an extra field
in a second domain is domain-specific and belongs in a domain namespace, not the core.
This test is operationalised as a portability metric in `domain_independence.md` §6.

### 1.4 C4 — Necessity

Removing the candidate must cause a demonstrable expressiveness loss: some statement the
corpus actually makes becomes inexpressible or requires a distortion to encode.

> **Test:** Delete it. Exhibit a specific attested sentence from a real corpus that can no
> longer be represented faithfully. "It would be inconvenient" is not a loss;
> "the conditional structure of *Bṛhat Jātaka* 12.3 collapses" is.

Necessity is what separates a primitive from a convenient abstraction. Convenience is a
reason to define a composite, never a reason to admit a primitive.

### 1.5 C5 — Non-redundancy

The candidate must not overlap an admitted primitive such that some instances could
defensibly be classified as either.

> **Test:** Construct the boundary case. If competent analysts disagree about which of two
> primitives a real instance belongs to, the pair is under-specified. Either sharpen the
> discriminator until the boundary case decides cleanly, or merge them.

Every primitive pair that was historically confusable is given an explicit discriminator
in §3 (Entity/Object, State/Attribute, Event/Condition, Influence/Causation,
Provenance/Traceability, Constraint/Condition).

### 1.6 C6 — Participation

The candidate must be capable of standing in at least one relationship to another
primitive. A thing that can neither bear a relation nor be borne by one cannot enter
reasoning and therefore cannot exist computationally in CHOIR.

Note the modality: *capable of*, not *currently does*. An orphan instance is legal (an
entity mentioned once and never used again is still an entity). A primitive *kind* with
no possible relation is not.

### 1.7 C7 — Falsifiable membership

There must exist a statable observation that would disqualify the candidate.

> **Test:** Complete the sentence "This candidate does not belong in CHOIR if we discover
> that ______." If the blank cannot be filled, the candidate is not a claim; it is a
> preference, and it is rejected.

This condition exists to prevent the ontology from accumulating unfalsifiable
metaphysics. §5 records the falsifier for each admitted primitive.

### 1.8 Sufficiency and the tie-break

C1–C7 are necessary. They are *jointly sufficient* only when the candidate is also
**minimal** with respect to the current set: no admitted primitive can be removed by
adding this one.

Where two candidate formulations both pass, prefer the one that:

1. requires fewer evaluation rules in the execution pipeline, then
2. keeps more source distinctions visible (fidelity beats elegance), then
3. localises change — a formulation that isolates domain variation into one slot beats one
   that spreads it across three.

Criterion 2 is the tie-break most likely to surprise. The `MANIFESTO.md` instruction
"do not optimize for elegance; optimize for rigor" is operative: where a collapse would
make the model tidier but would erase a distinction the corpus actually draws, the
distinction wins.

### 1.9 Failure modes (how a candidate is rejected)

| Failure | Diagnosis | Disposition |
|---|---|---|
| Fails C1 | Has no identity independent of storage | Reject; it is metadata or a value |
| Fails C2 | Reducible to admitted primitives | Demote to composite (§4) |
| Fails C3 | Structure changes across domains | Move to domain namespace |
| Fails C4 | Nothing becomes inexpressible | Reject as convenience |
| Fails C5 | Boundary cases undecidable | Sharpen or merge |
| Fails C6 | Cannot relate to anything | Reject; it is a value or a unit |
| Fails C7 | No possible disconfirmation | Reject as unfalsifiable |

---

## 2. The two-tier answer to "Entity vs Object"

The research brief asks what an Entity is, and what distinguishes Entity from Object.
The answer is that they sit at different tiers, and conflating them is the single most
common ontology error in rule systems.

**Object** is the universal supertype: anything CHOIR can name, address, version, and
attach provenance to. Rules are objects. Evidence items are objects. Conflicts,
resolutions, contexts and traces are objects. Objecthood is a *computational* property —
it means "the system can refer to this."

**Entity** is a strict subtype of Object: an object that models something *in the domain
being reasoned about*, and which bears identity through change.

> Every entity is an object. Most objects are not entities.

The discriminator is the **reasoning-about / reasoning-with** axis:

| | Reasoning *about* it | Reasoning *with* it |
|---|---|---|
| Jupiter, a patient, a contracting party | ✅ Entity | |
| A yoga rule, a statute, a guideline | | Reasoning artefact |
| A confidence score, a trace, a citation | | Meta-object |

A planet is an entity: the corpus makes claims about it. A rule is not an entity: the
corpus makes claims *with* it. When a rule *does* become the object of reasoning — a
commentary arguing about how to read a sūtra — the rule is *mentioned* rather than *used*,
and CHOIR represents that with an explicit `mentions` relation rather than by reclassifying
the rule. This use/mention discipline is what keeps meta-reasoning from corrupting object
reasoning.

**Formally:**

```
Entity(x) ⟺ Object(x)
            ∧ ∃ identity_criterion(x)
            ∧ persists_through(x, some_change)
            ∧ referent_of(x, domain) ∧ ¬artefact_of(x, reasoning_process)
```

**Falsifier for the split:** if a corpus is found in which the reasoning artefacts and the
domain referents obey identical rules of identity, versioning and defeat, the two-tier
split is unnecessary complexity and should collapse. No such corpus has been found among
the five reference domains; śāstric commentary, legal precedent and clinical guidelines
all version rules differently from how they identify subjects.

---

## 3. The primitives

Fifteen candidates were referred by the brief. Eleven are admitted as primitives, three
are admitted as *dimensions* (they qualify other objects rather than standing alone), and
one is demoted to a composite.

| # | Candidate | Verdict | Tier |
|---|---|---|---|
| 1 | Entity | Admitted | Referent |
| 2 | State | Admitted | Referent (time-indexed) |
| 3 | Attribute | Admitted | Referent (definitional) |
| 4 | Event | Admitted | Referent (occurrent) |
| 5 | Condition | Admitted | Proposition |
| 6 | Relationship | Admitted | Structural |
| 7 | Influence | Admitted | Structural (second-order) |
| 8 | Causation | Admitted | Structural |
| 9 | Constraint | Admitted | Proposition (enforced) |
| 10 | Context | Admitted | Meta (scope) |
| 11 | Evidence | Admitted | Reasoning artefact |
| 12 | Exception | Admitted | Reasoning artefact |
| 13 | Inference | Admitted | Reasoning artefact |
| 14 | Confidence | **Dimension** | Meta (derived) |
| 15 | Provenance | **Dimension** | Meta |
| 16 | Traceability | **Property**, not object | Meta (emergent) |
| 17 | Temporal reasoning | **Not an object** — a régime | Cross-cutting |

Traceability and temporal reasoning were listed in the brief as topics; both fail C1
(no identity) and are specified here as system properties rather than primitives.

---

### 3.1 Entity

**Definition.** An identity-bearing referent of domain discourse that persists through
change to its states.

**Identity criterion.** An entity is individuated by a *rigid designator* within a
namespace — a name that picks out the same thing in every context in which it appears at
all. `jyotisha:graha/Guru` designates Jupiter under every varga, every school, every
epoch. Contexts may disagree about Jupiter's *properties*; they may not disagree about
which object is being discussed without a distinct designator.

**Change tolerance.** An entity survives any change to its states (§3.2). It does not
survive a change to its identity-defining attributes (§3.3). This is the entire
State/Attribute distinction, and it is why that distinction is primitive rather than
stylistic.

**Sub-kinds** (domain-independent): `Agent` (can act, can bear obligation), `PhysicalEntity`,
`AbstractEntity`, `SituationalEntity` (roles, positions, offices — entities that exist only
relative to a structure, e.g. a bhāva, a legal office, an anatomical site).

**Falsifier.** If a domain is found in which the primary referents cannot be
re-identified across statements — where every mention is a fresh individual — Entity is
the wrong primitive for it and that domain needs a mass/stuff ontology instead.

---

### 3.2 State vs 3.3 Attribute

This pair is a single decision presented as two primitives, so they are specified together.

| | **Attribute** | **State** |
|---|---|---|
| Signature | `Entity → Value` | `(Entity, Interval) → Value` |
| Role | Definitional; part of what the thing *is* | Observational; part of how the thing *is now* |
| Change | Changing it yields a *different* entity | Changing it leaves the *same* entity |
| Validity | Whole lifetime of the entity | A bounded interval |
| Example (Jyotiṣa) | Mars is a natural malefic | Mars occupies Aries |
| Example (law) | This instrument is a lease | This lease is in default |
| Example (medicine) | This patient's blood type | This patient's blood pressure |

**The discriminator (C5 boundary test).** Ask the *counterfactual identity question*:

> If this value had always been different, would we be talking about a different thing?

If yes → attribute. If no → state.

Mars being a malefic is attributive: a benefic Mars is not Mars-with-a-different-property,
it is a different graha under the tradition's own classification. Mars being in Aries is a
state: the same Mars was elsewhere last month.

**The hard cases, resolved.**

- *Slowly-varying values* (a company's credit rating, a planet's dignity in a given sign)
  are **states with long intervals**, not attributes. Rate of change is irrelevant; only
  identity-dependence matters.
- *Derived classifications* (a "high-risk" patient) are **states**, because they are
  computed from other states and inherit their temporal indexing.
- *Contested attributes* — where schools disagree whether something is definitional —
  are represented as attributes **scoped to a context** (§3.10), not demoted to states.
  Disagreement about definition is a context problem, not a temporality problem.

**Why both are primitive.** Collapsing attributes into states (making everything
time-indexed) is technically possible and is what most graph systems do. It fails C4:
the corpus makes claims that are *definitional* and claims that are *observational*, and
rules quantify over them differently. A rule that fires on "any natural malefic" ranges
over an attribute-defined class; a rule that fires on "any planet currently in Aries"
ranges over a state extension. Erasing the distinction makes the first kind of rule
require a temporal qualifier it does not have in the source, which is a distortion.

---

### 3.4 Event vs 3.5 Condition

| | **Event** | **Condition** |
|---|---|---|
| Nature | An occurrence, located in time | A proposition, evaluable over time |
| Truth | Has no truth value; it *happens* | Has a truth value; it *holds* |
| Temporal shape | Point or bounded interval | Durative; may be open-ended |
| Countable | Yes — two transits are two events | No — "Jupiter is in Cancer" is one condition |
| Role in rules | Triggers state transitions | Gates rule applicability |
| Example (Jyotiṣa) | A daśā period beginning; an eclipse | Jupiter occupying a kendra |
| Example (law) | Filing; breach; service of notice | Being a resident; being over 18 |
| Example (medicine) | Onset; administration of a dose | Being hypertensive |

**Bridge.** Events become conditions through an explicit operator, never implicitly:

```
occurred(e, window)  →  Condition
```

This is a *deliberate* asymmetry. Rules match conditions. If a rule needs to fire on an
event, the event must be lifted into a condition with a stated window, and that window
becomes visible in the trace. Systems that let rules match events directly hide the
window, which then cannot be explained or contested.

**Why both are primitive.** Events are what make state change *auditable* — a state that
changed with no event is an unexplained mutation. Conditions are what make rules
*matchable*. Neither reduces to the other: an event with no condition derived from it is
still a fact of record (an audit trail item), and a condition with no generating event is
common (definitional and computed conditions).

---

### 3.6 Relationship

**Definition.** A named, typed, directed association among two or more objects, itself
bearing identity.

The "itself bearing identity" clause is critical and drives the knowledge-graph decision
in `knowledge_graph_spec.md`. In CHOIR every relationship instance is *reified by
construction* — it is an object, so it can carry confidence, provenance, context and
temporal validity, and can itself be the target of another relationship (an exception
attacking an inference link).

**Taxonomy.** Seven families, domain-independent:

| Family | Members | Semantics |
|---|---|---|
| **Structural** | `instance-of`, `subclass-of`, `part-of`, `member-of` | Ontological composition; drives inheritance |
| **Positional** | `occupies`, `adjacent-to`, `aspects`, `contained-in` | Spatial or configurational placement |
| **Temporal** | Allen's 13 interval relations (`before`, `meets`, `overlaps`, `during`, …) | Interval algebra over validity periods |
| **Epistemic** | `supports`, `contradicts`, `cites`, `derives-from`, `attests` | Bearing of one object on another's warrant |
| **Normative** | `obliges`, `permits`, `forbids`, `empowers` | Deontic force |
| **Influence** | `strengthens`, `weakens`, `modulates`, `cancels` | Degree modification (§3.7) |
| **Causal** | `produces`, `prevents`, `enables` | Generative dependency (§3.8) |

Arity is not restricted to 2. See `knowledge_graph_spec.md` §3 for why n-ary is the
storage default rather than an encoding built on binary edges.

**Cardinality, transitivity, symmetry and inverses** are declared per relationship type,
not assumed. `part-of` is transitive; `aspects` is not; `contradicts` is symmetric;
`supports` is not.

---

### 3.7 Influence vs 3.8 Causation

This is the distinction most rule engines lack, and the one that matters most for the
corpora CHOIR targets.

**Causation** asserts a generative dependency: *C produces E*, and counterfactually,
without C, E would not have arisen (in the relevant context). It is first-order — an edge
in the generative graph. It licenses intervention reasoning: change the cause, change
the effect.

**Influence** asserts a *modulation of degree without a claim of production*. It does not
say the effect would not have occurred; it says the effect's strength, likelihood, or
polarity is altered. It is **second-order** — it is a function *on* another relation's
weight, not a relation between the relata directly.

```
Causation:  C ──produces──▶ E
Influence:  I ──modulates──▶ (C ──produces──▶ E)
                              └── the edge is the target
```

**Why this is primitive, not stylistic.** Survey what the reference corpora actually
assert:

| Domain | Predominant mode | Example |
|---|---|---|
| Jyotiṣa | **Influence** | A benefic aspect *strengthens* an indication; it does not produce an outcome |
| Law | **Influence** | A mitigating factor *reduces* a sentence; it does not cause the sentence |
| Medicine | Mixed | A pathogen *causes* infection; a comorbidity *worsens* prognosis |
| Finance | **Influence** | A covenant breach *increases* default risk |
| Engineering | Mixed | A load *produces* stress; a safety factor *modulates* the allowance |

Classical Jyotiṣa is almost entirely influence-language: grahas *indicate*, *strengthen*,
*afflict*, *cancel*. Rendering these as causal edges would attribute to the corpus a claim
it does not make — a fidelity failure, and precisely the kind of distortion C4 exists to
catch. It would also generate false intervention semantics.

**Formal consequence.** Influence edges are evaluated *after* the base graph is computed
(they need something to modulate), which fixes an ordering constraint in
`execution_pipeline.md` §4. Influence composition is not simple multiplication:
competing influences require an explicit combination policy, specified in
`confidence_framework.md` §5.

**Falsifier.** If a faithful encoding of a substantial influence-heavy corpus can be
produced using only causal edges plus weights, without loss of the modulation/production
distinction in explanations, Influence collapses into weighted Causation and should be
demoted.

---

### 3.9 Constraint

**Definition.** A proposition that restricts the admissible configurations of the model,
enforced rather than evaluated.

**Constraint vs Condition (C5 boundary).** Both are propositions. The discriminator is
*what happens on failure*:

- A **condition** that is false → the rule does not fire. Normal operation.
- A **constraint** that is violated → the *state is inadmissible*. Something is wrong.

Same proposition, different role. "A planet occupies exactly one rāśi" is a constraint
(violation means bad input or a bug). "A planet occupies Aries" is a condition (falsity is
just information).

**Three kinds:**

| Kind | Enforced when | Violation means | Example |
|---|---|---|---|
| **Integrity** | Always | Model is malformed | Every graha has exactly one rāśi |
| **Applicability** | At rule-match time | Rule is out of scope | This rule applies only to natal charts |
| **Normative** | Evaluated, not enforced | An obligation is unmet | This filing *must* precede that one |

Normative constraints are the deontic case and must **not** be enforced as integrity
constraints — the entire point of a normative system is that it can be violated. A system
that makes obligations unviolatable cannot represent breach, and therefore cannot
represent law, ethics, or ritual injunction. This is a common and serious modelling error.

---

### 3.10 Context

**Definition.** A named set of assumptions under which propositions are evaluated;
formally, a labelled scope that partitions the truth assignment.

**Why primitive.** Context is what allows two contradictory statements to *both* be
admitted without the knowledge base exploding. Without it, the corpus is inconsistent on
its face — different schools, editions and epochs disagree — and classical logic makes an
inconsistent knowledge base worthless.

**Dimensions** (domain-independent, extensible per domain):

```
Context ::= {
  tradition   : which school / authority lineage
  source      : which text and edition
  temporal    : when the rule is in force (≠ when it is about)
  jurisdiction: where / to whom it applies
  granularity : at what resolution (varga; court level; care setting)
  purpose     : what question is being asked
}
```

**Lattice structure.** Contexts are partially ordered by specificity: `c₁ ⊑ c₂` iff every
assumption in `c₂` holds in `c₁`. This ordering is not decoration — it is the machinery
that powers conflict resolution (`conflict_resolution.md` §5). Most apparent
contradictions in a śāstric or legal corpus are *context collisions*: two rules that were
never meant to co-apply, whose scoping conditions were left implicit in the source. The
first resolution move is always to look for the missing context discriminator.

**Relation to prior art.** This is the same insight as Cyc's microtheories and RDF named
graphs. CHOIR's addition is that the context lattice is *derived from source structure*
(chapter, school, recension) rather than hand-declared, and that context membership is
itself evidence-bearing — see `related_work.md` §2.1.

---

### 3.11 Evidence

**Definition.** An object that bears on the warrant of a proposition, with polarity,
weight, and a derivation history.

Evidence is *not* data. Data is raw; evidence is data *plus a bearing relation* to a
specific claim. The same observation is evidence for one proposition and irrelevant to
another. Evidence is therefore always a triple-ish structure, never a standalone value:

```
Evidence ::= ⟨ source, claim, polarity, weight, derivation, context ⟩
```

**Polarity** is three-valued and the third value is subtle: `supporting`, `contradicting`,
and `neutral` — where neutral splits into *irrelevant* (no bearing; should not be stored
against this claim) and *balanced* (bearing, but symmetric). Only the second is
informative. See `evidence_model.md` §3.

**Derivation** distinguishes `direct` (observed), `derived` (inferred from other evidence),
`inherited` (holds by virtue of a structural relation), and `independent` (shares no
ancestry with other evidence for the same claim). Independence is the hardest and most
consequential to get right, because naive accumulation double-counts correlated evidence.
Fully specified in `evidence_model.md` §4.

**Non-destruction invariant.** Defeated evidence is *marked*, never deleted. The record of
what was considered and rejected is part of the explanation.

---

### 3.12 Exception

**Definition.** An object that defeats an inference without necessarily denying its
conclusion.

Exceptions are typed using Pollock's defeater taxonomy, which maps with unusual precision
onto the śāstric utsarga/apavāda apparatus (see `vedic_reasoning_methodology.md` §4):

| Type | Attacks | Effect | Śāstric analogue |
|---|---|---|---|
| **Rebutting** | The conclusion | Asserts the opposite conclusion | Conflicting vidhi |
| **Undercutting** | The inference link | Removes the warrant without asserting the opposite | *upādhi* (vitiating condition) |
| **Premise-denying** | An input condition | Denies a premise | Failure of a precondition |

The undercutting case is the one systems usually get wrong. "This rule does not apply
here" is *not* "the opposite conclusion holds." A cancelled yoga does not produce the
inverse result; it produces *no result from that rule*, leaving other evidence to decide.
Conflating the two manufactures conclusions the corpus never asserted.

**Exceptions are objects, not fields.** An exception has its own source, its own
confidence, and can itself be excepted (exceptions to exceptions are common in law and in
Pāṇinian grammar). Modelling exceptions as a boolean field on a rule makes this
inexpressible and fails C4.

---

### 3.13 Inference

**Definition.** A licensed transition from a rule plus bindings plus inputs to a
conclusion, recorded as an object.

```
Inference ::= ⟨ rule_id, bindings, inputs, conclusion, license, context, timestamp ⟩
```

**License types**, which determine defeasibility:

| License | Guarantee | Defeasible |
|---|---|---|
| Deductive | Conclusion cannot be false if premises are true | No |
| Defeasible | Conclusion holds absent defeaters | Yes |
| Abductive | Best explanation among considered alternatives | Yes, strongly |
| Analogical | Structural correspondence to a precedent | Yes, strongly |

Almost all śāstric and legal reasoning is *defeasible*, with significant analogical
content. Recording the license type is what lets the explanation say honestly *how much*
the conclusion is worth.

**Inference is reified because the graph must reason about its own steps** — conflict
detection operates over inferences, and undercutting defeaters target inference objects
directly.

---

### 3.14 Confidence (dimension)

**Verdict: admitted as a dimension, not a standalone primitive.** Confidence fails C1: it
has no identity independent of the thing it qualifies. There is no "confidence #4172"
floating free; there is *the confidence of this inference in this context*.

**Definition.** A derived, graded epistemic attitude attached to a proposition-in-a-context.

**The governing constraint: confidence is computed, never authored.** No rule author may
type a number. Confidence is a *function of evidence structure*, and if it can be set by
hand it becomes an untraceable opinion wearing a number's clothing.

**Three orthogonal axes** — this is a core CHOIR commitment and the axes must not be
collapsed for internal use:

| Axis | Question | Failure looks like |
|---|---|---|
| **Extraction** | Did we read the text correctly? | Mis-parsed compound; wrong sandhi split |
| **Interpretive** | Does the tradition agree what it means? | Schools differ on scope |
| **Inferential** | Given both, how strongly does evidence support the conclusion? | Weak or conflicting support |

A conclusion can be extracted with certainty from a text whose meaning is contested and
whose evidential support is thin. One scalar cannot say that. A presented summary scalar
is permitted, but it must be decomposable back into the three axes on demand.
Full specification in `confidence_framework.md`.

---

### 3.15 Provenance (dimension) vs 3.16 Traceability (property)

These are routinely conflated and are not the same thing.

**Provenance** answers *where did this come from* — origin. It is a dimension attached to
every object:

```
Provenance ::= ⟨ source_text, locus, edition, translator, extractor,
                 extraction_method, timestamp, agent ⟩
```

Provenance is **backward-looking and static**: it does not change when the object is used.

**Traceability** answers *how did we get here* — path. It is not an object at all; it is a
**system property**: the guarantee that any conclusion can be mechanically unwound to its
inputs.

Traceability fails C1 (no identity) and C2 (it is the transitive closure of `derives-from`
edges over reified inferences — fully reducible). It is therefore specified as an
invariant on the execution pipeline, not as a primitive:

> **Traceability invariant.** For every conclusion *c*, the sub-graph of inferences,
> evidence and rules reachable from *c* by inverse `derives-from` edges is sufficient to
> re-derive *c* deterministically, given the same corpus version and resolution policy.

This is testable, and it is the acceptance test for `execution_pipeline.md`. The
*Trace* object (the materialised record) is admitted as an object; traceability (the
property it guarantees) is not.

---

### 3.17 Temporal reasoning (régime, not object)

Temporal reasoning is a cross-cutting régime, not a primitive. It is specified here
because every other primitive is time-indexed and the indexing must be uniform.

**Three independent time axes** (tri-temporal model):

| Axis | Meaning | Example |
|---|---|---|
| **Valid time** | When the fact is true *of the world* | Jupiter was in Cancer during 2025 |
| **Transaction time** | When the system recorded it | Ingested 2026-03-04 |
| **Decision time** | When the conclusion was drawn | Reading produced 2026-03-05 |

Systems that keep only one axis cannot answer "what did we conclude then, and would we
conclude it now?" — which is the core audit question in every institutional domain.

**A fourth, domain-critical distinction:** the time a rule is *about* versus the time a
rule is *in force*. A statute enacted in 2020 may govern conduct from 2018; a śāstric rule
in a recension dated to one century may be about configurations of any epoch. These are
different fields and conflating them produces retroactivity errors.

**Interval algebra.** Allen's 13 relations are the standard vocabulary for temporal
relationships and are adopted wholesale. Point events are modelled as degenerate intervals
so one algebra covers both.

---

## 4. Composites (defined, not primitive)

These are important, frequently used, and explicitly *not* primitives. They are defined
in terms of primitives so that their structure stays inspectable.

| Composite | Definition |
|---|---|
| **Rule** | `Context + Condition-structure + Conclusion(s) + Exception* + Provenance` |
| **Yoga / named combination** | A Rule whose conclusion asserts a named `SituationalEntity` |
| **Conflict** | A Relationship of family *epistemic* holding between two Inferences with incompatible conclusions in a shared Context |
| **Resolution** | An Inference whose inputs are a Conflict and a precedence policy |
| **Proposal** | A set of Inferences advanced together with their Evidence and open Conflicts |
| **Decision** | A Resolution promoted to authoritative status within a Context |
| **Trace** | The materialised transitive closure guaranteeing the traceability invariant |

Note that `Rule` is **not** primitive. This is deliberate and is the least intuitive
result of applying the admission test: Rule fails C2, being losslessly expressible as a
Context-scoped Condition→Conclusion structure with attached Exceptions and Provenance.
Keeping it as a defined composite forces its internal structure to remain visible to the
conflict and explanation machinery, rather than becoming an opaque unit.

This directly informs the reserved DAALE boundaries: `proposal.py`, `decision.py` and
`contradiction.py` name *composites*, and should receive interfaces only after the
primitives beneath them are approved.

---

## 5. Falsifiers register

Per C7, each admitted primitive carries a statable disconfirmation.

| Primitive | Does not belong if we discover that… |
|---|---|
| Entity | Domain referents cannot be re-identified across statements |
| Attribute | No corpus rule quantifies over definitional classes |
| State | All values are lifetime-constant |
| Event | State changes never need occurrence-level attribution |
| Condition | Rules can match occurrences directly without a stated window |
| Relationship | All associations are binary and metadata-free |
| Influence | Influence-heavy corpora encode losslessly as weighted causation |
| Causation | No corpus supports intervention/counterfactual reasoning |
| Constraint | Violation and non-satisfaction never need different handling |
| Context | The corpus is globally consistent without scoping |
| Evidence | Support is always all-or-nothing and never accumulates |
| Exception | Undercutting and rebutting defeat behave identically |
| Inference | Nothing ever needs to attack a reasoning step itself |

Each falsifier is a research task, not a rhetorical flourish. The Influence falsifier in
particular should be attempted seriously during Phase 2 corpus work: if it succeeds, the
primitive set shrinks by one and the ontology improves.

---

## 6. Open questions

1. **Is `SituationalEntity` a distinct sub-kind or a composite?** A bhāva and a legal
   office both exist only relative to a structure. They may reduce to
   `Entity + part-of + Context`. Unresolved; flagged for `reasoning_ontology.md`.
2. **Does Analogical inference need its own primitive machinery?** Śāstric reasoning uses
   *upamāna* substantively. Currently modelled as an inference license; may need a
   first-class correspondence structure.
3. **Granularity of Context.** Is granularity (varga level, court level) a context
   dimension or a separate abstraction/refinement relation? Both readings are defensible;
   per `MANIFESTO.md` both are recorded rather than collapsed.
4. **Are normative constraints reducible to conditions plus a deontic modality?** If yes,
   Constraint loses one of its three kinds. Requires the deontic analysis in Phase 3.

---

## 7. Summary

- **Object** is the universal supertype; **Entity** is the domain-referent subtype. Rules
  and evidence are objects, not entities.
- **Attribute** is definitional, **State** is time-indexed; the discriminator is the
  counterfactual identity question.
- **Event** happens, **Condition** holds; events are lifted to conditions through an
  explicit, visible window.
- **Influence** is second-order modulation; **Causation** is first-order production. Most
  of the target corpora are influence-dominant, and this is the primitive set's most
  consequential departure from standard rule engines.
- **Confidence** and **Provenance** are dimensions, not free-standing objects.
  **Traceability** is a system invariant. **Temporal reasoning** is a tri-temporal régime.
- **Rule is a composite**, not a primitive — the surprising but correct result of applying
  C2 honestly.
