# 018 — Related Work Survey

**Status:** Draft for review
**Phase:** 5 — Generalization Research
**Depends on:** `computational_symbolism_review.md`
**Feeds:** the eventual paper; positioning for external review

---

## 1. Scope and caveat

Systems the brief names, plus those the analysis in Phases 1–4 made unavoidable. Each is
assessed on the same axes, so comparison is like-for-like.

**Caveat.** This is an analytical survey drawn from the established landscape of these
systems, not a systematic literature review, and specific version-level capabilities have not
been verified against current documentation. Before any external novelty claim, each row
marked ⚠️ in §4 must be checked directly.

**Assessment axes** (chosen because they are CHOIR's requirements):

| Axis | Question |
|---|---|
| **Defeasibility** | Can adding knowledge retract a conclusion? |
| **Defeat typing** | Undercutting distinguished from rebutting? |
| **Statement metadata** | Confidence/provenance per statement instance? |
| **Contexts** | Locally consistent partitions? |
| **Source fidelity** | Does a rule trace to a text locus with its derivation? |
| **Ambiguity** | Can unresolved readings be represented? |
| **Graded support** | Does evidence accumulate? |
| **Unresolved output** | Can it terminate in a legitimate disjunction? |
| **Explanation** | Trace-projected, or generated? |

---

## 2. Systems

### 2.1 Cyc

**What it is.** A decades-long project to encode commonsense knowledge, with a very large
assertion base, a higher-order logic (CycL), and **microtheories** — contexts partitioning
assertions so globally inconsistent knowledge stays locally consistent.

| Strengths | Weaknesses / limits |
|---|---|
| Microtheories are the direct precedent for CHOIR contexts | Largely proprietary; hard to inspect or reproduce |
| Enormous scale; genuine commonsense coverage | Assertions encode curator judgement, not sourced text |
| Handles inconsistency by contextual partitioning | Knowledge-acquisition bottleneck is the standing critique |
| Supports non-monotonic default reasoning | No systematic source provenance to a locus |

**How CHOIR differs.** Contexts are *derived from source structure* (recension, school,
chapter) rather than hand-declared; every assertion traces to a text locus in a stated
edition; interpretive uncertainty is represented. Cyc encodes *what is true*; CHOIR encodes
*what a source says, and how confident we are that we read it correctly*.

**What CHOIR takes.** Microtheories vindicate the context primitive. That Cyc found
contextual partitioning necessary at scale is meaningful evidence for
`computational_primitives.md` §3.10.

---

### 2.2 OpenCog

**What it is.** An integrative AGI architecture built on the AtomSpace — a weighted,
labelled hypergraph — with Probabilistic Logic Networks for uncertain inference and
attention allocation for resource control.

| Strengths | Weaknesses / limits |
|---|---|
| **Hypergraph as the core store** — the same conclusion as `knowledge_graph_spec.md` §3 | AGI-oriented; not designed for auditability |
| Native uncertainty representation | Truth values are numeric pairs, not decomposable by axis |
| Handles n-ary relations | No source provenance model |
| Integrates learned and symbolic components | Explanation is not a primary output |

**How CHOIR differs.** Same storage decision, opposite motivation: OpenCog chose a hypergraph
for representational generality, CHOIR for kāraka role-labelling and statement-level
metadata. CHOIR's confidence is a decomposable vector with a limiting factor, not a truth
value; and CHOIR's hard neural/symbolic boundary is the opposite of OpenCog's integration
goal.

**What CHOIR takes.** Independent convergence on hypergraph storage is genuine support for
that decision.

---

### 2.3 SOAR and 2.4 ACT-R

**What they are.** Cognitive architectures. SOAR: problem-space search, operator selection,
impasse-driven subgoaling, chunking. ACT-R: declarative/procedural memory split with
subsymbolic activation, validated against human behavioural data.

| Strengths | Weaknesses / limits (for CHOIR's purposes) |
|---|---|
| Mature, long-validated | **Modelling *how humans think*, not *what a corpus says*** |
| SOAR's impasse mechanism resembles escalation | No source provenance; no textual fidelity notion |
| ACT-R's activation gives principled retrieval | Subsymbolic activation is not auditable |
| Both explain their processing | Explanation is of *cognition*, not of *warrant* |

**How CHOIR differs.** Different objects entirely. A cognitive architecture asks how a mind
reaches a conclusion; CHOIR asks what a corpus licenses and how that can be audited. ACT-R's
activation is exactly the kind of unauditable numeric influence `knowledge_graph_spec.md`
§2.5 excludes.

**What CHOIR takes.** SOAR's impasse-and-subgoal pattern is a useful precedent for
escalation as a first-class state rather than an error.

---

### 2.5 Drools (and production rule engines generally)

**What it is.** A mature business rule management system: RETE-based matching, a rule
language, agenda control, decision tables.

| Strengths | Weaknesses / limits |
|---|---|
| Excellent RETE implementation; production-proven | **Conflict resolution is agenda strategy** (salience, recency) — not principled precedence |
| Good tooling; decision tables are business-readable | No defeat typing; exceptions are just conditions |
| Scales to large rule sets | No statement-level provenance or confidence |
| Handles rule modularity | Cannot represent unresolved conflict — always fires something |

**How CHOIR differs.** This is the sharpest contrast on conflict handling. Drools resolves
conflict by **agenda ordering** — salience numbers assigned by the rule author. CHOIR
resolves by **principled precedence** (specificity, phase, recency, authority) with the
grounds recorded, and can decline to resolve. A salience number is exactly the authored,
untraceable value `confidence_framework.md` §1 forbids.

Drools also cannot distinguish *not applicable* from *applied then defeated*, because
resolution happens during matching rather than after saturation
(`execution_pipeline.md` §4.2).

**What CHOIR takes.** RETE, and the evidence that it scales.

---

### 2.6 Prolog

**What it is.** Logic programming: Horn clauses, SLD resolution, backward chaining,
negation as failure.

| Strengths | Weaknesses / limits |
|---|---|
| Clean declarative semantics | **Cut is procedural** and breaks declarative reading |
| Backward chaining is efficient for specific queries | Clause order matters — results depend on it |
| Negation as failure ≈ *anupalabdhi* | NAF has **no observability condition** (009 §3.3) |
| Excellent for prototyping rule logic | No native metadata, provenance, or graded support |
| Well-understood, mature | Cannot represent unresolved conflict |

**How CHOIR differs.** Prolog's negation as failure is closed-world *unconditionally*.
CHOIR's `Absent` requires an explicit completeness declaration and is unevaluable without it
— which is the classical *anupalabdhi* restriction that modern NAF dropped. This is a case
where the older formulation is more careful than the newer.

Prolog's clause-order sensitivity is precisely what saturation-before-adjudication
(`execution_pipeline.md` §4.2) exists to eliminate.

**What CHOIR takes.** The stratification discipline, and the negation-as-failure idea in its
qualified form.

---

### 2.7 OWL / RDF / SPARQL

Covered in `computational_symbolism_review.md` §2.2 and `knowledge_graph_spec.md` §2.1.

| Strengths | Weaknesses / limits |
|---|---|
| **Formal semantics** — entailment is a defined question | **Monotonic** — incompatible with a defeat-centred system |
| Decidable fragments with known complexity | Open-world throughout; no scoped closure |
| Genuine standards and interoperability | Inconsistency is fatal, not localised |
| Vast tooling and vocabulary reuse | Statement metadata needs reification / RDF-star |
| SHACL adds validation | n-ary needs the intermediate-node pattern |

**How CHOIR differs.** The monotonicity mismatch is fundamental. CHOIR retains RDF-star as an
**export target** rather than rejecting the family
(`knowledge_graph_spec.md` §3).

**Wikidata** deserves separate mention: its qualifier-and-reference model is the closest
widely-deployed precedent for statement-level provenance, and it demonstrates the pattern
works at scale.

---

### 2.8 Neo4j and property-graph reasoning

**What it is.** LPG database; Cypher/GQL; graph algorithms.

| Strengths | Weaknesses / limits |
|---|---|
| Edge properties native — statement metadata is free | **No formal semantics** — entailment is application code |
| Excellent traversal performance | Edges cannot be edge endpoints (`knowledge_graph_spec.md` §2.2) |
| Mature operations | n-ary needs intermediate nodes |
| Pleasant path query language | Property values flat; nested metadata becomes opaque strings |

**How CHOIR differs.** CHOIR uses an LPG *projection* for traversal while keeping the
hypergraph authoritative. The disqualifier for LPG-as-record is second-order targeting:
undercutting defeaters and influences must target edges.

---

### 2.9 LegalRuleML — the closest comparator

**What it is.** An OASIS standard extending RuleML for legal norms: defeasibility, deontic
operators, temporal management, isomorphism between rules and source provisions, and
metadata for authorship and jurisdiction.

**This is the system CHOIR must be most careful to distinguish itself from** (threat T6 in
`computational_symbolism_review.md` §6).

| Shared with CHOIR | Where CHOIR goes further |
|---|---|
| Defeasible rules with exceptions | **Defeat typed** rebutting / undercutting / premise, enforced in the type system |
| Deontic operators | Comparable |
| **Isomorphism to source provisions** | Extends to *grammatical derivation*, not just provision-level linkage |
| Rich provenance and jurisdiction metadata | Adds the **interpretive confidence axis** |
| Temporal management of norms | Comparable; tri-temporal |
| Conflict via defeasibility and precedence | Adds ***vikalpa*** as a reportable outcome |
| — | **Ambiguity as a first-class IR construct** |
| — | **Confidence derived, never authored** |
| — | Explanation as trace projection with a fixed schema |

**Honest assessment.** LegalRuleML is a *markup standard* for representing legal rules;
CHOIR is a *compiler and execution architecture*. They are not the same kind of artefact,
which makes direct comparison awkward — but the overlap in representational commitments is
real and substantial.

The four differences that appear genuine: ambiguity representation, interpretive confidence,
derived-not-authored confidence, and disjunctive termination. Whether those constitute a
different system or an extension is a fair question, and it should be settled by detailed
comparison against the current specification rather than by assertion. ⚠️ **Flagged for
verification.**

---

### 2.10 Catala

**What it is.** A domain-specific language for encoding statutory and regulatory law,
designed around the observation that legal text is *default logic with exceptions* — literate
programming pairs code with the legal text it implements.

| Strengths | Weaknesses / limits |
|---|---|
| **Default-with-exceptions matches legal structure**, as it matches *utsarga/apavāda* | Targets computable law (tax, benefits) — deterministic calculation |
| Literate programming keeps text and code adjacent | No graded confidence; law is treated as determinate |
| Produces verified executable code | No ambiguity representation |
| Formal semantics | No disjunctive output — a computation returns a value |

**How CHOIR differs.** Catala's domain is statutes that *compute* (a tax owed). CHOIR's
domains *interpret* — the answer is contested, graded, and sometimes plural. Where Catala can
assume determinacy, CHOIR cannot.

**Independent convergence worth noting:** Catala arrived at default-logic-with-exceptions
from French tax law; CHOIR arrived at the same structure from Mīmāṃsā and Pāṇini. Two
unrelated legal-textual traditions producing the same computational structure is meaningful
support for `computational_primitives.md` §3.12.

---

### 2.11 Truth maintenance systems (JTMS / ATMS)

**What they are.** Dependency-tracking systems that maintain justifications for beliefs and
retract dependents when a premise is withdrawn. ATMS maintains multiple contexts
simultaneously.

| Strengths | Weaknesses / limits |
|---|---|
| **Dependency tracking is exactly CHOIR's `derives_from` closure** | No graded support |
| ATMS multi-context ≈ CHOIR contexts | No source provenance |
| Efficient retraction | Assumption sets can grow exponentially |
| Justifications support explanation | Justification ≠ warrant with a citation |

**How CHOIR differs.** CHOIR's traceability invariant is a TMS justification structure with
provenance, confidence and defeat typing layered on. The retraction machinery in
`execution_pipeline.md` §8 is TMS-derived.

**What CHOIR takes.** The whole incremental invalidation model.

---

### 2.12 Computational Sanskrit

Distinct from the reasoning systems above but essential to Phase 2. Covered in
`sanskrit_analysis_pipeline.md` §10: morphological analysers and readers (the Sanskrit
Heritage platform being the best-known), annotated corpora (the Digital Corpus of Sanskrit),
dependency and kāraka treebanks from Indian NLP groups, digitised classical lexica, and
neural work on sandhi splitting and compound analysis.

**Strengths:** the segmentation and morphology problems are seriously attacked, with real
resources.

**Limits for CHOIR:** these tools produce *linguistic analysis*, not *executable rules*.
Nothing in this literature, as surveyed, carries the analysis through to a reasoning
representation. The gap between a kāraka-labelled parse and an executable defeasible rule is
where CHOIR's Phase 2 sits, and it appears genuinely unoccupied.

⚠️ **This is the most important verification item in the document.** A prior system that
compiles śāstric text to executable rules would substantially change CHOIR's positioning, and
this survey has not searched exhaustively for one.

---

## 3. Comparison matrix

| System | Defeasible | Defeat typed | Stmt metadata | Contexts | Source fidelity | Ambiguity | Graded | Unresolved output | Explanation |
|---|---|---|---|---|---|---|---|---|---|
| **Cyc** | ✅ | ~ | ~ | ✅ | ✗ | ✗ | ~ | ✗ | ~ |
| **OpenCog** | ✅ | ✗ | ✅ | ~ | ✗ | ✗ | ✅ | ✗ | ✗ |
| **SOAR** | ~ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ~ | ~ |
| **ACT-R** | ~ | ✗ | ✗ | ✗ | ✗ | ✗ | ✅ | ✗ | ~ |
| **Drools** | ✗ | ✗ | ✗ | ~ | ✗ | ✗ | ✗ | ✗ | ~ |
| **Prolog** | ~ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ~ |
| **OWL/RDF** | ✗ | ✗ | ~ | ✅ | ~ | ✗ | ✗ | ✗ | ~ |
| **Neo4j** | ✗ | ✗ | ✅ | ~ | ✗ | ✗ | ~ | ✗ | ✗ |
| **LegalRuleML** | ✅ | ~ | ✅ | ✅ | ✅ | ✗ | ~ | ~ | ~ |
| **Catala** | ✅ | ~ | ~ | ~ | ✅ | ✗ | ✗ | ✗ | ✅ |
| **ATMS** | ✅ | ✗ | ✗ | ✅ | ✗ | ✗ | ✗ | ~ | ✅ |
| **CHOIR** (design) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

✅ native · ~ partial or achievable with effort · ✗ absent

**Read this table sceptically.** The final row describes a *design*, not a running system;
every other row describes something that exists and has been used. A design scoring well
against implemented systems has proved nothing. The table's honest use is to show which
columns are unoccupied — **ambiguity** most conspicuously, and **unresolved output** nearly
so.

---

## 4. Verification queue

Items requiring direct checking before external claims:

| # | Item | Why it matters |
|---|---|---|
| V1 | ⚠️ Current LegalRuleML specification, in detail | Closest comparator; threat T6 |
| V2 | ⚠️ Prior work compiling śāstric text to executable rules | Would change positioning fundamentally (§2.12) |
| V3 | ⚠️ Interpretive-uncertainty models in semantic-web trust literature | Threat T2 in `computational_symbolism_review.md` |
| V4 | ⚠️ Current capabilities of named Sanskrit NLP resources | Dependency decisions rest on this |
| V5 | ⚠️ Structured argumentation systems reporting unresolved conflict as primary output | *Vikalpa* novelty claim |
| V6 | Catala's current handling of legal ambiguity | May have advanced |

---

## 5. Positioning

The defensible statement, stated conservatively:

> CHOIR is a **compiler architecture for interpretive normative corpora**. It occupies the
> gap between computational linguistics (which analyses text but does not produce executable
> reasoning) and rule engines (which execute rules but assume an authoritative formalisation
> already exists).
>
> Its distinguishing requirements come from a source type the rule-engine literature has not
> centred: **a canonical corpus in a dead literary register, with a live interpretive
> tradition, no outcome ground truth, and centuries of recorded disagreement.**

That source type forces four commitments the surveyed systems do not make:

1. Ambiguity survives into the IR.
2. Interpretive uncertainty is a distinct confidence axis.
3. Confidence is derived, never authored.
4. Unresolved conflict is a reportable outcome.

**And a caution.** Everything in this survey is comparison against a design. The correct
next step is not to publish a novelty claim but to run
`domain_independence.md` §6 and build enough of the benchmark corpus
(`canonical_shloka_analysis.md` §12) that the claims have something to be tested against.

---

## 6. Open questions

1. **Complete the verification queue** (§4) before any external claim.
2. **Is the composition claim testable?** `computational_symbolism_review.md` §5 argues the
   mechanisms interlock. Demonstrating that requires showing a system missing one commitment
   fails in a specific way — an ablation study, which is possible but not designed.
3. **Should CHOIR target LegalRuleML as an export format?** If the overlap is as substantial
   as §2.9 suggests, interoperability may be more valuable than differentiation.
4. **Catala collaboration.** The convergence in §2.10 suggests the two projects have a shared
   problem; the default-logic core may be directly comparable.
5. **Is "interpretive normative corpora" a recognised category?** If the literature has a
   name for this class of system, CHOIR should use it rather than coin one.
