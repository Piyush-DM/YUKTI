# Computational Primitive Specification

| | |
|---|---|
| **Document ID** | YK-R-001 |
| **Source** | `choir/research/phase-1-foundations/computational_primitives.md` (001) |
| **Series** | CHOIR Research Programme |
| **Revision** | A |
| **Status** | Active |
| **Last Updated** | 2026-08-23 |

## Abstract

This document defines the universal vocabulary that every CHOIR reasoning system uses, regardless of domain (§0). It states a seven-condition admission test that a candidate primitive must pass, applies that test to the candidates named in the research brief, and records which pass, which are demoted to composites, and which remain contested (§0, §3, §4, §6). The source calls the Influence/Causation split — Influence being second-order modulation, Causation first-order production — "the primitive set's most consequential departure from standard rule engines," and the demotion of Rule to a composite "the least intuitive result of applying the admission test" (§7, §4).

**Status note.** This publication carries the status **Active**: the underlying document is drafted but has **not** been accepted as specification. The source itself is marked "Draft for review" in Phase 1 — Computational Foundations. `choir/research/README.md` records the programme-level position: "All 18 deliverables drafted. None accepted. Every document is a hypothesis, per `MANIFESTO.md`." `MANIFESTO.md` itself states the underlying formulation — "Treat every computational object as a hypothesis rather than an established truth." Nothing below should be read as an approved ruling.

## Research Question

The source states its own purpose in §0. It does two things:

> 1. States the **admission test** a candidate primitive must pass (the constitutional question posed in `MANIFESTO.md`).
> 2. Applies that test to the fifteen candidates named in the research brief, and records which pass, which are demoted to composites, and which remain contested.

The question, therefore, is: what conditions must a candidate concept satisfy to be admitted as a computational primitive of CHOIR rather than as a composite, a dimension, a system property, or a domain-specific term — and, under those conditions, what is the actual primitive set?

A prior question is answered in §0.1, and it constrains everything after it: what does CHOIR claim? The source's answer is that CHOIR "compiles a reasoning *tradition* into executable form. It claims fidelity to what a corpus says and how that corpus argues. It does **not** claim that the corpus is true."

## Finding

### 1. The scope of the claim, and what it excludes (§0.1)

The source treats the claim boundary as load-bearing rather than diplomatic, because it determines what the system can be validated against:

| Claim CHOIR makes | Validated against |
|---|---|
| This rule is what the text says | Critical editions, scholar agreement |
| This inference follows from that rule | Formal semantics, proof checking |
| This conclusion was reached this way | Execution trace replay |
| This conclusion is *true of the world* | **Not claimed** |

The last row is given as the reason the same machinery generalises to law and medicine: "A statute is not 'true'; it is *in force*. A clinical guideline is not 'true'; it is *recommended at grade B*." CHOIR is said to model normative and interpretive systems, where the object of study is the rule corpus itself. Where a domain does have outcome ground truth (medicine, finance), the source describes that as an additional validation layer bolted on top, cross-referring to `confidence_framework.md` §7. The operative consequence: "Any primitive whose definition presupposes that the corpus is factually correct is rejected by construction" (§0.1).

### 2. The admission test: seven necessary conditions (§1)

A candidate is admitted only if it passes all seven. Failing any one is disqualifying; passing all seven is explicitly *not* automatically sufficient (§1, §1.8).

| ID | Condition | Requirement as stated |
|---|---|---|
| C1 | Identity (§1.1) | Re-identifiable across time and across statements without appeal to storage location, list position, or any implementation artefact. Identity criteria must be stated positively and negatively. |
| C2 | Irreducibility (§1.2) | Not losslessly expressible as a configuration of other admitted primitives. Irreducibility is relative to the current set, so the test must be re-run whenever the set changes. "Demotion is not deletion: composites remain in the ontology as *defined terms*" (§4). |
| C3 | Domain independence (§1.3) | Instantiable in at least three of the five reference domains (Jyotiṣa, law, medicine, finance, engineering) with the *same* structure, differing only in vocabulary. "A candidate that needs a different arity, a different evaluation rule, or an extra field in a second domain is domain-specific and belongs in a domain namespace, not the core." |
| C4 | Necessity (§1.4) | Removing it must cause a demonstrable expressiveness loss — a specific attested corpus sentence that can no longer be represented faithfully. |
| C5 | Non-redundancy (§1.5) | Must not overlap an admitted primitive such that some instances could defensibly be classified as either. |
| C6 | Participation (§1.6) | Must be *capable of* standing in at least one relationship to another primitive. |
| C7 | Falsifiable membership (§1.7) | There must exist a statable observation that would disqualify the candidate. |

C5 comes with a stated inventory: the source records that "every primitive pair that was historically confusable is given an explicit discriminator in §3" — Entity/Object, State/Attribute, Event/Condition, Influence/Causation, Provenance/Traceability, and Constraint/Condition (§1.5).

Several of these conditions carry explicit disciplinary force. C4 is what "separates a primitive from a convenient abstraction. Convenience is a reason to define a composite, never a reason to admit a primitive" (§1.4). C7 "exists to prevent the ontology from accumulating unfalsifiable metaphysics"; if the sentence "This candidate does not belong in CHOIR if we discover that ______" cannot be completed, "the candidate is not a claim; it is a preference, and it is rejected" (§1.7). C6 is modal: an orphan instance is legal, but a primitive *kind* with no possible relation is not (§1.6).

**Sufficiency and tie-break (§1.8).** C1–C7 are jointly sufficient only when the candidate is also *minimal* with respect to the current set. Where two formulations both pass, the source prefers, in order: fewer evaluation rules in the execution pipeline; then more source distinctions kept visible (fidelity beats elegance); then localised change. The source flags criterion 2 as "the tie-break most likely to surprise," invoking the `MANIFESTO.md` instruction "do not optimize for elegance; optimize for rigor" — where a collapse would tidy the model but erase a distinction the corpus draws, the distinction wins.

**Failure modes (§1.9).** Rejection is typed: failing C1 → reject (metadata or a value); C2 → demote to composite; C3 → move to a domain namespace; C4 → reject as convenience; C5 → sharpen or merge; C6 → reject (a value or a unit); C7 → reject as unfalsifiable.

### 3. The two-tier answer to Entity vs Object, and the Entity primitive (§2, §3.1)

The source states that Entity and Object sit at different tiers, and that "conflating them is the single most common ontology error in rule systems."

**Object** is the universal supertype: anything CHOIR can name, address, version, and attach provenance to. Rules, evidence items, conflicts, resolutions, contexts and traces are objects. Objecthood is a computational property — "it means 'the system can refer to this.'"

**Entity** is a strict subtype: an object that models something in the domain being reasoned about, and which bears identity through change. "Every entity is an object. Most objects are not entities."

The discriminator is the reasoning-*about* / reasoning-*with* axis: a planet is an entity because the corpus makes claims about it; a rule is not, because the corpus makes claims *with* it. When a rule does become the object of reasoning — a commentary arguing how to read a sūtra — the rule is *mentioned* rather than *used*, and CHOIR represents this with an explicit `mentions` relation rather than by reclassifying the rule. The source states this use/mention discipline "is what keeps meta-reasoning from corrupting object reasoning."

Formally (§2):

```
Entity(x) ⟺ Object(x)
            ∧ ∃ identity_criterion(x)
            ∧ persists_through(x, some_change)
            ∧ referent_of(x, domain) ∧ ¬artefact_of(x, reasoning_process)
```

The falsifier for the split is stated: if a corpus is found in which reasoning artefacts and domain referents obey identical rules of identity, versioning and defeat, the two-tier split is unnecessary complexity and should collapse. The source records that no such corpus has been found among the five reference domains, and gives the supporting observation that "śāstric commentary, legal precedent and clinical guidelines all version rules differently from how they identify subjects" (§2).

**The Entity primitive itself (§3.1).** Entity is defined as "an identity-bearing referent of domain discourse that persists through change to its states." Its identity criterion is a *rigid designator* within a namespace — "a name that picks out the same thing in every context in which it appears at all." The worked case: `jyotisha:graha/Guru` designates Jupiter under every varga, every school, every epoch; contexts may disagree about Jupiter's *properties*, but "they may not disagree about which object is being discussed without a distinct designator."

Change tolerance follows the State/Attribute line: an entity survives any change to its states (§3.2), but does not survive a change to its identity-defining attributes (§3.3). The source states that this "is the entire State/Attribute distinction, and it is why that distinction is primitive rather than stylistic."

Four domain-independent sub-kinds are given: `Agent` (can act, can bear obligation), `PhysicalEntity`, `AbstractEntity`, and `SituationalEntity` — roles, positions and offices, "entities that exist only relative to a structure, e.g. a bhāva, a legal office, an anatomical site." `SituationalEntity` is the subject of open question 1 (§6).

§3.1 gives the Entity falsifier in fuller form than the §5 register does: if a domain is found in which the primary referents cannot be re-identified across statements — "where every mention is a fresh individual" — Entity is the wrong primitive for it, and that domain needs a mass/stuff ontology instead.

### 4. The verdicts (§3)

The source's verdict table records seventeen numbered rows:

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

Traceability and temporal reasoning were listed in the brief as topics; the source records that both fail C1 (no identity) and specifies them as system properties rather than primitives (§3).

**An unreconciled count in the source.** The prose introducing this table states: "Fifteen candidates were referred by the brief. Eleven are admitted as primitives, three are admitted as *dimensions* (they qualify other objects rather than standing alone), and one is demoted to a composite." The table as printed carries seventeen rows, of which thirteen are marked *Admitted*, two are marked *Dimension*, one is a *Property*, and one is a *régime*; the composite demotion discussed in the document is `Rule` (§4), which does not appear as a numbered candidate. The source does not reconcile these figures, and this publication does not resolve them.

### 5. State vs Attribute (§3.2, §3.3)

The source presents this pair as "a single decision presented as two primitives."

| | **Attribute** | **State** |
|---|---|---|
| Signature | `Entity → Value` | `(Entity, Interval) → Value` |
| Role | Definitional; part of what the thing *is* | Observational; part of how the thing *is now* |
| Change | Changing it yields a *different* entity | Changing it leaves the *same* entity |
| Validity | Whole lifetime of the entity | A bounded interval |
| Example (Jyotiṣa) | Mars is a natural malefic | Mars occupies Aries |
| Example (law) | This instrument is a lease | This lease is in default |
| Example (medicine) | This patient's blood type | This patient's blood pressure |

The discriminator is the **counterfactual identity question**: "If this value had always been different, would we be talking about a different thing?" Yes → attribute; no → state.

Hard cases are resolved explicitly (§3.2/§3.3): slowly-varying values (a credit rating, a planet's dignity in a given sign) are states with long intervals, since "Rate of change is irrelevant; only identity-dependence matters"; derived classifications (a "high-risk" patient) are states, inheriting temporal indexing from what they are computed from; and contested attributes — where schools disagree whether something is definitional — are represented as attributes *scoped to a context* (§3.10), not demoted to states, because "Disagreement about definition is a context problem, not a temporality problem."

The argument for keeping both is a C4 argument: collapsing attributes into states is technically possible "and is what most graph systems do," but a rule firing on "any natural malefic" ranges over an attribute-defined class while a rule firing on "any planet currently in Aries" ranges over a state extension. Erasing the distinction "makes the first kind of rule require a temporal qualifier it does not have in the source, which is a distortion."

### 6. Event vs Condition (§3.4, §3.5)

An Event is an occurrence located in time; it has no truth value, it *happens*, and it is countable. A Condition is a proposition evaluable over time; it has a truth value, it *holds*, and it is not countable in the same way. Events trigger state transitions; conditions gate rule applicability.

The bridge between them is deliberate and one-way:

```
occurred(e, window)  →  Condition
```

Rules match conditions. If a rule must fire on an event, the event is lifted into a condition with a stated window, "and that window becomes visible in the trace." The source's stated reason: "Systems that let rules match events directly hide the window, which then cannot be explained or contested." Neither reduces to the other — an event with no derived condition is still a fact of record, and definitional or computed conditions commonly have no generating event.

### 7. Influence vs Causation (§3.7, §3.8)

The source calls this "the distinction most rule engines lack, and the one that matters most for the corpora CHOIR targets."

**Causation** asserts a generative dependency: *C produces E*, and counterfactually, without C, E would not have arisen in the relevant context. It is first-order and licenses intervention reasoning.

**Influence** asserts "a *modulation of degree without a claim of production*." It does not say the effect would not have occurred; it says the effect's strength, likelihood, or polarity is altered. It is second-order — a function *on* another relation's weight:

```
Causation:  C ──produces──▶ E
Influence:  I ──modulates──▶ (C ──produces──▶ E)
                              └── the edge is the target
```

The justification is a corpus survey (§3.7):

| Domain | Predominant mode | Example |
|---|---|---|
| Jyotiṣa | **Influence** | A benefic aspect *strengthens* an indication; it does not produce an outcome |
| Law | **Influence** | A mitigating factor *reduces* a sentence; it does not cause the sentence |
| Medicine | Mixed | A pathogen *causes* infection; a comorbidity *worsens* prognosis |
| Finance | **Influence** | A covenant breach *increases* default risk |
| Engineering | Mixed | A load *produces* stress; a safety factor *modulates* the allowance |

Classical Jyotiṣa is described as "almost entirely influence-language: grahas *indicate*, *strengthen*, *afflict*, *cancel*." Rendering these as causal edges "would attribute to the corpus a claim it does not make — a fidelity failure, and precisely the kind of distortion C4 exists to catch," as well as generating false intervention semantics.

Two formal consequences are recorded: influence edges must be evaluated *after* the base graph is computed, fixing an ordering constraint in `execution_pipeline.md` §4; and influence composition "is not simple multiplication" — competing influences require an explicit combination policy, deferred to `confidence_framework.md` §5.

The falsifier is stated openly: if a faithful encoding of a substantial influence-heavy corpus can be produced using only causal edges plus weights, without loss of the modulation/production distinction in explanations, "Influence collapses into weighted Causation and should be demoted" (§3.7).

### 8. Relationship (§3.6)

A Relationship is "a named, typed, directed association among two or more objects, itself bearing identity." The identity-bearing clause is called critical and is said to drive the knowledge-graph decision in `knowledge_graph_spec.md`: every relationship instance is *reified by construction*, so it can carry confidence, provenance, context and temporal validity, and can itself be the target of another relationship (an exception attacking an inference link).

Seven domain-independent families are given: **Structural** (`instance-of`, `subclass-of`, `part-of`, `member-of`), **Positional** (`occupies`, `adjacent-to`, `aspects`, `contained-in`), **Temporal** (Allen's 13 interval relations), **Epistemic** (`supports`, `contradicts`, `cites`, `derives-from`, `attests`), **Normative** (`obliges`, `permits`, `forbids`, `empowers`), **Influence** (`strengthens`, `weakens`, `modulates`, `cancels`), and **Causal** (`produces`, `prevents`, `enables`).

Arity is not restricted to 2; the source defers to `knowledge_graph_spec.md` §3 for why n-ary is the storage default rather than an encoding over binary edges. Cardinality, transitivity, symmetry and inverses are declared per relationship type, not assumed; the source's worked declarations are that "`part-of` is transitive; `aspects` is not; `contradicts` is symmetric; `supports` is not."

### 9. Constraint (§3.9)

A Constraint is "a proposition that restricts the admissible configurations of the model, enforced rather than evaluated." Against Condition, the C5 discriminator is what happens on failure: a false condition means the rule does not fire (normal operation); a violated constraint means the state is inadmissible (something is wrong). "A planet occupies exactly one rāśi" is a constraint; "A planet occupies Aries" is a condition.

Three kinds are distinguished — **Integrity** (always enforced; violation means the model is malformed), **Applicability** (enforced at rule-match time; violation means the rule is out of scope), and **Normative** (evaluated, not enforced; violation means an obligation is unmet).

The source is emphatic that normative constraints "must **not** be enforced as integrity constraints — the entire point of a normative system is that it can be violated. A system that makes obligations unviolatable cannot represent breach, and therefore cannot represent law, ethics, or ritual injunction. This is a common and serious modelling error."

### 10. Context (§3.10)

Context is "a named set of assumptions under which propositions are evaluated; formally, a labelled scope that partitions the truth assignment." Its necessity argument: context is what allows two contradictory statements to both be admitted without the knowledge base exploding, since different schools, editions and epochs disagree and classical logic makes an inconsistent knowledge base worthless.

Six domain-independent, per-domain-extensible dimensions are given:

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

Contexts are partially ordered by specificity (`c₁ ⊑ c₂` iff every assumption in `c₂` holds in `c₁`). The source states this ordering "is not decoration — it is the machinery that powers conflict resolution (`conflict_resolution.md` §5)," and that most apparent contradictions in a śāstric or legal corpus are *context collisions*: rules never meant to co-apply whose scoping conditions were left implicit. "The first resolution move is always to look for the missing context discriminator."

On prior art, the source states this is "the same insight as Cyc's microtheories and RDF named graphs," and identifies CHOIR's addition as two things: the context lattice is derived from source structure (chapter, school, recension) rather than hand-declared, and context membership is itself evidence-bearing (`related_work.md` §2.1).

### 11. Evidence (§3.11)

Evidence is "an object that bears on the warrant of a proposition, with polarity, weight, and a derivation history." The source insists evidence is *not* data: "Data is raw; evidence is data *plus a bearing relation* to a specific claim."

```
Evidence ::= ⟨ source, claim, polarity, weight, derivation, context ⟩
```

Polarity is three-valued, and the third value is described as subtle: `supporting`, `contradicting`, and `neutral` — where neutral splits into *irrelevant* (no bearing; should not be stored against the claim) and *balanced* (bearing, but symmetric); only the latter is informative. Derivation distinguishes `direct`, `derived`, `inherited`, and `independent`. The source records that independence "is the hardest and most consequential to get right, because naive accumulation double-counts correlated evidence," and defers full specification to `evidence_model.md` §3 and §4.

A **non-destruction invariant** is stated: "Defeated evidence is *marked*, never deleted. The record of what was considered and rejected is part of the explanation."

### 12. Exception (§3.12)

An Exception is "an object that defeats an inference without necessarily denying its conclusion." Exceptions are typed using Pollock's defeater taxonomy, which the source says "maps with unusual precision onto the śāstric utsarga/apavāda apparatus" (`vedic_reasoning_methodology.md` §4):

| Type | Attacks | Effect | Śāstric analogue |
|---|---|---|---|
| **Rebutting** | The conclusion | Asserts the opposite conclusion | Conflicting vidhi |
| **Undercutting** | The inference link | Removes the warrant without asserting the opposite | *upādhi* (vitiating condition) |
| **Premise-denying** | An input condition | Denies a premise | Failure of a precondition |

The undercutting case is identified as the one systems usually get wrong: "'This rule does not apply here' is *not* 'the opposite conclusion holds.' A cancelled yoga does not produce the inverse result; it produces *no result from that rule*, leaving other evidence to decide. Conflating the two manufactures conclusions the corpus never asserted."

Exceptions are objects, not fields: an exception has its own source, its own confidence, and can itself be excepted — "exceptions to exceptions are common in law and in Pāṇinian grammar." Modelling exceptions as a boolean field on a rule makes this inexpressible and fails C4.

### 13. Inference (§3.13)

An Inference is "a licensed transition from a rule plus bindings plus inputs to a conclusion, recorded as an object."

```
Inference ::= ⟨ rule_id, bindings, inputs, conclusion, license, context, timestamp ⟩
```

License types determine defeasibility: **Deductive** (not defeasible), **Defeasible** (holds absent defeaters), **Abductive** (best explanation among considered alternatives; strongly defeasible), and **Analogical** (structural correspondence to a precedent; strongly defeasible). The source records that "Almost all śāstric and legal reasoning is *defeasible*, with significant analogical content," and that recording the license type "is what lets the explanation say honestly *how much* the conclusion is worth."

Inference is reified because the graph must reason about its own steps: conflict detection operates over inferences, and undercutting defeaters target inference objects directly.

### 14. Confidence as a dimension (§3.14)

**Verdict: admitted as a dimension, not a standalone primitive.** Confidence fails C1: "it has no identity independent of the thing it qualifies. There is no 'confidence #4172' floating free; there is *the confidence of this inference in this context*." It is defined as "a derived, graded epistemic attitude attached to a proposition-in-a-context."

The governing constraint is stated categorically: "confidence is computed, never authored." No rule author may type a number, because "if it can be set by hand it becomes an untraceable opinion wearing a number's clothing."

Three orthogonal axes are declared a core CHOIR commitment that "must not be collapsed for internal use":

| Axis | Question | Failure looks like |
|---|---|---|
| **Extraction** | Did we read the text correctly? | Mis-parsed compound; wrong sandhi split |
| **Interpretive** | Does the tradition agree what it means? | Schools differ on scope |
| **Inferential** | Given both, how strongly does evidence support the conclusion? | Weak or conflicting support |

A conclusion can be extracted with certainty from a text whose meaning is contested and whose evidential support is thin; one scalar cannot say that. A presented summary scalar is permitted, "but it must be decomposable back into the three axes on demand." Full specification is deferred to `confidence_framework.md`.

### 15. Provenance (dimension) vs Traceability (property) (§3.15, §3.16)

The source states these "are routinely conflated and are not the same thing."

**Provenance** answers *where did this come from* — origin — and is a dimension attached to every object:

```
Provenance ::= ⟨ source_text, locus, edition, translator, extractor,
                 extraction_method, timestamp, agent ⟩
```

It is "backward-looking and static: it does not change when the object is used."

**Traceability** answers *how did we get here* — path. It is not an object at all but a system property. It fails C1 (no identity) and C2 (it is the transitive closure of `derives-from` edges over reified inferences — fully reducible), and is specified as an invariant on the execution pipeline:

> **Traceability invariant.** For every conclusion *c*, the sub-graph of inferences, evidence and rules reachable from *c* by inverse `derives-from` edges is sufficient to re-derive *c* deterministically, given the same corpus version and resolution policy.

The source states this is testable and is the acceptance test for `execution_pipeline.md`. The *Trace* object — the materialised record — is admitted as an object; traceability, the property it guarantees, is not.

### 16. Temporal reasoning as a régime (§3.17)

Temporal reasoning is a cross-cutting régime, not a primitive; it is specified because every other primitive is time-indexed and the indexing must be uniform. Three independent axes (tri-temporal model) are given: **Valid time** (when the fact is true of the world), **Transaction time** (when the system recorded it), and **Decision time** (when the conclusion was drawn). Systems keeping only one axis "cannot answer 'what did we conclude then, and would we conclude it now?' — which is the core audit question in every institutional domain."

A fourth, domain-critical distinction is recorded: the time a rule is *about* versus the time a rule is *in force*. "A statute enacted in 2020 may govern conduct from 2018; a śāstric rule in a recension dated to one century may be about configurations of any epoch. These are different fields and conflating them produces retroactivity errors."

Allen's 13 interval relations are adopted wholesale; point events are modelled as degenerate intervals so one algebra covers both.

### 17. Composites, including Rule (§4)

The following are defined in terms of primitives so their structure stays inspectable, and are explicitly *not* primitives:

| Composite | Definition |
|---|---|
| **Rule** | `Context + Condition-structure + Conclusion(s) + Exception* + Provenance` |
| **Yoga / named combination** | A Rule whose conclusion asserts a named `SituationalEntity` |
| **Conflict** | A Relationship of family *epistemic* holding between two Inferences with incompatible conclusions in a shared Context |
| **Resolution** | An Inference whose inputs are a Conflict and a precedence policy |
| **Proposal** | A set of Inferences advanced together with their Evidence and open Conflicts |
| **Decision** | A Resolution promoted to authoritative status within a Context |
| **Trace** | The materialised transitive closure guaranteeing the traceability invariant |

The source calls Rule's demotion "the least intuitive result of applying the admission test": Rule fails C2, being losslessly expressible as a Context-scoped Condition→Conclusion structure with attached Exceptions and Provenance. Keeping it as a defined composite "forces its internal structure to remain visible to the conflict and explanation machinery, rather than becoming an opaque unit."

### 18. Falsifiers register (§5)

Per C7, each admitted primitive carries a statable disconfirmation:

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

The source states these are research tasks, not rhetorical flourishes, and singles one out: "The Influence falsifier in particular should be attempted seriously during Phase 2 corpus work: if it succeeds, the primitive set shrinks by one and the ontology improves."

### 19. The source's own summary (§7)

- **Object** is the universal supertype; **Entity** is the domain-referent subtype. Rules and evidence are objects, not entities.
- **Attribute** is definitional, **State** is time-indexed; the discriminator is the counterfactual identity question.
- **Event** happens, **Condition** holds; events are lifted to conditions through an explicit, visible window.
- **Influence** is second-order modulation; **Causation** is first-order production. Most of the target corpora are influence-dominant, and this is "the primitive set's most consequential departure from standard rule engines."
- **Confidence** and **Provenance** are dimensions, not free-standing objects. **Traceability** is a system invariant. **Temporal reasoning** is a tri-temporal régime.
- **Rule is a composite**, not a primitive — "the surprising but correct result of applying C2 honestly."

## Architectural Implications

These are the implications the source itself draws, except where marked as this publication's own observation.

**Reserved DAALE boundaries touched.** The source names `daale/ontology/base.py`, `relationships.py`, `evidence.py`, and `confidence.py` as the DAALE boundaries this specification touches (header). It further states that `proposal.py`, `decision.py` and `contradiction.py` name *composites*, and "should receive interfaces only after the primitives beneath them are approved" (§4). This publication observes — the source does not say it — that since this document is Active rather than accepted, that approval has not occurred.

**Relationship reification is a storage decision, not a modelling nicety.** Because every relationship instance bears identity by construction, it must be able to carry confidence, provenance, context and temporal validity, and be targetable by another relationship. The source states this "drives the knowledge-graph decision in `knowledge_graph_spec.md`," and that arity is not restricted to 2 — n-ary is the storage default rather than an encoding built on binary edges (§3.6).

**An ordering constraint on the execution pipeline.** Influence edges must be evaluated *after* the base graph is computed, because they need something to modulate. The source states this "fixes an ordering constraint in `execution_pipeline.md` §4" (§3.7).

**An explicit influence-combination policy is required.** Influence composition is not simple multiplication; competing influences require a stated combination policy, deferred to `confidence_framework.md` §5 (§3.7).

**The traceability invariant is an acceptance test, not an aspiration.** Traceability is specified as an invariant on the execution pipeline and is stated to be "the acceptance test for `execution_pipeline.md`" (§3.16).

**Confidence is computed, never authored.** "No rule author may type a number" (§3.14): confidence is a function of evidence structure, and a hand-set value "becomes an untraceable opinion wearing a number's clothing." The three axes (extraction, interpretive, inferential) are a stated CHOIR commitment and must remain decomposable even where a summary scalar is presented.

**Context lattice drives conflict resolution.** The specificity ordering over contexts "is the machinery that powers conflict resolution (`conflict_resolution.md` §5)," and the first resolution move is to search for a missing context discriminator (§3.10).

**Normative constraints must not be compiled to integrity constraints.** A system that makes obligations unviolatable "cannot represent breach, and therefore cannot represent law, ethics, or ritual injunction" (§3.9).

**The events-to-conditions lift must remain explicit and visible in the trace.** Rules match conditions only; any rule that fires on an event does so through `occurred(e, window)` with the window recorded, so it can be explained and contested (§3.4/§3.5).

**Defeated evidence is retained.** The non-destruction invariant (§3.11) constrains storage and deletion policy: marking, never deleting.

**Domain independence is measurable, not asserted.** C3 "is operationalised as a portability metric in `domain_independence.md` §6" (§1.3).

**The irreducibility test is not one-time.** Because C2 is relative to the current primitive set, the test "must be re-run whenever the set changes" (§1.2).

## Open Questions

The source records four open questions explicitly (§6):

1. **Is `SituationalEntity` a distinct sub-kind or a composite?** A bhāva and a legal office both exist only relative to a structure. They may reduce to `Entity + part-of + Context`. Recorded as unresolved and flagged for `reasoning_ontology.md`.
2. **Does Analogical inference need its own primitive machinery?** Śāstric reasoning uses *upamāna* substantively. Currently modelled as an inference license; may need a first-class correspondence structure.
3. **Granularity of Context.** Is granularity (varga level, court level) a context dimension or a separate abstraction/refinement relation? "Both readings are defensible; per `MANIFESTO.md` both are recorded rather than collapsed."
4. **Are normative constraints reducible to conditions plus a deontic modality?** If yes, Constraint loses one of its three kinds. Requires the deontic analysis in Phase 3.

Further unresolved and untested items, drawn from the source or observed against it:

- **Every falsifier in §5 is an open research task**, not a settled result. The Influence falsifier is explicitly scheduled for attempt during Phase 2 corpus work, with the stated consequence that if it succeeds "the primitive set shrinks by one and the ontology improves" (§5). Influence's status as a primitive is therefore provisional by the document's own terms.
- **The Entity/Object two-tier split rests on a negative finding.** The source states that no corpus collapsing reasoning artefacts and domain referents "has been found among the five reference domains" (§2), supported by the observation that śāstric commentary, legal precedent and clinical guidelines all version rules differently from how they identify subjects. What is recorded is the absence of a counterexample across those five domains; the source neither claims nor disclaims anything stronger.
- **The candidate counts in §3 do not reconcile.** The prose ("Fifteen candidates… Eleven… three… one") does not match the seventeen-row verdict table (thirteen *Admitted*, two *Dimension*, one *Property*, one *régime*), and the composite demotion discussed (`Rule`, §4) is not a numbered candidate. The source does not reconcile this.
- **Multiple central mechanisms are deferred rather than specified here**, and are therefore unspecified as of this document: independence of evidence (`evidence_model.md` §4), influence combination policy (`confidence_framework.md` §5), the full confidence specification (`confidence_framework.md`), outcome-ground-truth validation for domains that have it (`confidence_framework.md` §7), the portability metric (`domain_independence.md` §6), and n-ary storage (`knowledge_graph_spec.md` §3).
- **The document is a draft.** The source is marked "Draft for review"; this publication is Active, meaning drafted but not accepted as specification. `choir/research/README.md` records that all 18 deliverables are drafted, none accepted, and "Every document is a hypothesis, per `MANIFESTO.md`."

## Related Documents

Dependencies and downstream documents declared in the source header:

- Feeds [YK-R-002 — Reasoning Ontology](YK-R-002-reasoning-ontology.md) — also carries open question 1 (`SituationalEntity`)
- Feeds [YK-R-003 — Knowledge Graph Specification](YK-R-003-knowledge-graph-specification.md) — relationship reification and n-ary storage (§3, §3.6)
- Feeds [YK-R-013 — CHOIR Intermediate Representation](YK-R-013-choir-intermediate-representation.md)

Documents cited within the source:

- [YK-R-004 — Vedic Reasoning Methodology](YK-R-004-vedic-reasoning-methodology.md) — §4, utsarga/apavāda and the defeater taxonomy (§3.12)
- [YK-R-009 — Evidence Model](YK-R-009-evidence-model.md) — §3 polarity, §4 derivation and independence (§3.11)
- [YK-R-010 — Conflict Resolution](YK-R-010-conflict-resolution.md) — §5, context lattice as resolution machinery (§3.10)
- [YK-R-011 — Confidence Framework](YK-R-011-confidence-framework.md) — §5 influence combination policy (§3.7), §7 outcome ground truth (§0.1), full confidence specification (§3.14)
- [YK-R-015 — Execution Pipeline](YK-R-015-execution-pipeline.md) — §4 influence evaluation ordering (§3.7); traceability invariant as acceptance test (§3.16)
- [YK-R-016 — Domain Independence](YK-R-016-domain-independence.md) — §6, portability metric operationalising C3 (§1.3)
- [YK-R-018 — Related Work Survey](YK-R-018-related-work-survey.md) — §2.1, microtheories and named graphs (§3.10)

The source also declares a dependency on `MANIFESTO.md` (the admission criteria question), which is not a publication in this series.
