# Related Work Survey

| | |
|---|---|
| **Document ID** | YK-R-018 |
| **Source** | `choir/research/phase-5-generalization/related_work.md` (018) |
| **Series** | CHOIR Research Programme |
| **Revision** | A |
| **Status** | Active |
| **Last Updated** | 2026-08-23 |

## Abstract

The source document assesses twelve families of existing system — Cyc, OpenCog, SOAR, ACT-R, Drools, Prolog, OWL/RDF/SPARQL, Neo4j, LegalRuleML, Catala, truth maintenance systems, and computational Sanskrit — against nine axes chosen because they are CHOIR's requirements (§1), and records, for most of them, where CHOIR differs and what CHOIR takes (§2). The treatment is not uniform: a "What CHOIR takes" block appears for six of the twelve sections, and §2.9 and §2.12 replace the standard "How CHOIR differs" heading with an "Honest assessment" and a "Limits for CHOIR" note respectively. It concludes with a conservatively stated positioning — CHOIR as "a **compiler architecture for interpretive normative corpora**" occupying the gap between computational linguistics and rule engines (§5) — and a six-item verification queue that must be discharged before any external novelty claim is made (§4). The document states its own limits plainly: it is "an analytical survey drawn from the established landscape of these systems, not a systematic literature review", version-level capabilities have not been verified against current documentation (§1), and the comparison is "comparison against a design" rather than against a running system (§3, §5).

This publication is **Active**: the source is a complete research document, drafted but not accepted as specification. Its own header records its status as "Draft for review". `choir/research/README.md` records the programme position: "All 18 deliverables drafted. None accepted. Every document is a hypothesis, per `MANIFESTO.md`." The formulation `MANIFESTO.md` itself gives is at the level of the computational object: "Treat every computational object as a hypothesis rather than an established truth."

## Research Question

The source does not state a single question in one sentence. Its framing is given by scope and purpose: it surveys "Systems the brief names, plus those the analysis in Phases 1–4 made unavoidable", each assessed "on the same axes, so comparison is like-for-like" (§1). Its stated downstream consumers are "the eventual paper; positioning for external review" (header).

The question the document sets out to answer is therefore one of positioning: against the systems that already exist, which of CHOIR's representational and execution commitments are already occupied, and which are not — and what may honestly be claimed on that basis. The document's own answer to the last part is the caution in §5: "The correct next step is not to publish a novelty claim but to run `domain_independence.md` §6 and build enough of the benchmark corpus (`canonical_shloka_analysis.md` §12) that the claims have something to be tested against."

The nine assessment axes are stated as CHOIR's requirements (§1):

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

## Finding

### The caveat the document places on itself (§1)

Before any system is discussed, the source restricts what the survey may be used for:

> **Caveat.** This is an analytical survey drawn from the established landscape of these systems, not a systematic literature review, and specific version-level capabilities have not been verified against current documentation. Before any external novelty claim, each row marked ⚠️ in §4 must be checked directly.

Two further cautions of the same kind are placed later in the document, each stated independently: §3 instructs the reader to "Read this table sceptically", and §5 closes under the heading "**And a caution.**"

### Cyc (§2.1)

Cyc is characterised as a decades-long commonsense encoding project with a higher-order logic (CycL) and **microtheories** — contexts partitioning assertions so that globally inconsistent knowledge stays locally consistent. Recorded strengths: microtheories as "the direct precedent for CHOIR contexts"; scale and commonsense coverage; inconsistency handled by contextual partitioning; support for non-monotonic default reasoning. Recorded limits: "Largely proprietary; hard to inspect or reproduce"; assertions encode curator judgement rather than sourced text; the knowledge-acquisition bottleneck as "the standing critique"; and no systematic source provenance to a locus.

The difference is stated as one of object: "Cyc encodes *what is true*; CHOIR encodes *what a source says, and how confident we are that we read it correctly*." CHOIR's contexts are "*derived from source structure* (recension, school, chapter) rather than hand-declared". What CHOIR takes: "Microtheories vindicate the context primitive. That Cyc found contextual partitioning necessary at scale is meaningful evidence for `computational_primitives.md` §3.10."

### OpenCog (§2.2)

An integrative AGI architecture on the AtomSpace — a weighted, labelled hypergraph — with Probabilistic Logic Networks for uncertain inference and attention allocation for resource control. Recorded strengths: "**Hypergraph as the core store** — the same conclusion as `knowledge_graph_spec.md` §3"; native uncertainty representation; handling of n-ary relations; and integration of learned and symbolic components. Limits recorded: AGI-oriented and "not designed for auditability"; truth values are "numeric pairs, not decomposable by axis"; no source provenance model; explanation is not a primary output.

The difference is stated as "Same storage decision, opposite motivation": OpenCog chose a hypergraph for representational generality, CHOIR for kāraka role-labelling and statement-level metadata. CHOIR's confidence is "a decomposable vector with a limiting factor, not a truth value", and "CHOIR's hard neural/symbolic boundary is the opposite of OpenCog's integration goal". What CHOIR takes: "Independent convergence on hypergraph storage is genuine support for that decision."

### SOAR and ACT-R (§2.3, §2.4 — presented together)

Cognitive architectures: SOAR with problem-space search, operator selection, impasse-driven subgoaling and chunking; ACT-R with a declarative/procedural memory split, subsymbolic activation, and validation against human behavioural data. Recorded strengths: both are "Mature, long-validated"; "SOAR's impasse mechanism resembles escalation"; "ACT-R's activation gives principled retrieval"; and "Both explain their processing". The limits are recorded specifically for CHOIR's purposes, the decisive one in emphasis: they are "**Modelling *how humans think*, not *what a corpus says***". Further limits: no source provenance or textual fidelity notion; "Subsymbolic activation is not auditable"; and "Explanation is of *cognition*, not of *warrant*".

"Different objects entirely. A cognitive architecture asks how a mind reaches a conclusion; CHOIR asks what a corpus licenses and how that can be audited. ACT-R's activation is exactly the kind of unauditable numeric influence `knowledge_graph_spec.md` §2.5 excludes." What CHOIR takes: "SOAR's impasse-and-subgoal pattern is a useful precedent for escalation as a first-class state rather than an error."

### Drools and production rule engines (§2.5)

A mature business rule management system: RETE-based matching, a rule language, agenda control, decision tables. Recorded strengths: an "Excellent RETE implementation; production-proven"; "Good tooling; decision tables are business-readable"; scaling "to large rule sets"; and handling of rule modularity. The recorded limits are that "**Conflict resolution is agenda strategy** (salience, recency) — not principled precedence"; that there is no defeat typing, "exceptions are just conditions"; no statement-level provenance or confidence; and that it "Cannot represent unresolved conflict — always fires something".

The source calls this "the sharpest contrast on conflict handling". Drools resolves conflict "by **agenda ordering** — salience numbers assigned by the rule author"; CHOIR resolves "by **principled precedence** (specificity, phase, recency, authority) with the grounds recorded, and can decline to resolve. A salience number is exactly the authored, untraceable value `confidence_framework.md` §1 forbids."

A second structural point is recorded: "Drools also cannot distinguish *not applicable* from *applied then defeated*, because resolution happens during matching rather than after saturation (`execution_pipeline.md` §4.2)."

What CHOIR takes: "RETE, and the evidence that it scales."

### Prolog (§2.6)

Horn clauses, SLD resolution, backward chaining, negation as failure. Strengths recorded include clean declarative semantics, efficient backward chaining, maturity, and that "Negation as failure ≈ *anupalabdhi*". Limits recorded: "**Cut is procedural** and breaks declarative reading"; "Clause order matters — results depend on it"; NAF "has **no observability condition** (009 §3.3)"; no native metadata, provenance, or graded support; and it cannot represent unresolved conflict.

The stated difference: "Prolog's negation as failure is closed-world *unconditionally*. CHOIR's `Absent` requires an explicit completeness declaration and is unevaluable without it — which is the classical *anupalabdhi* restriction that modern NAF dropped. This is a case where the older formulation is more careful than the newer."

And on ordering: "Prolog's clause-order sensitivity is precisely what saturation-before-adjudication (`execution_pipeline.md` §4.2) exists to eliminate." What CHOIR takes: "The stratification discipline, and the negation-as-failure idea in its qualified form."

### OWL / RDF / SPARQL (§2.7)

Recorded as already covered in `computational_symbolism_review.md` §2.2 and `knowledge_graph_spec.md` §2.1. Strengths: formal semantics where "entailment is a defined question"; decidable fragments with known complexity; genuine standards and vocabulary reuse; SHACL validation. Limits: "**Monotonic** — incompatible with a defeat-centred system"; open-world throughout with no scoped closure; "Inconsistency is fatal, not localised"; statement metadata requires reification or RDF-star; n-ary requires the intermediate-node pattern.

"The monotonicity mismatch is fundamental. CHOIR retains RDF-star as an **export target** rather than rejecting the family (`knowledge_graph_spec.md` §3)."

The section singles out one deployed system: "**Wikidata** deserves separate mention: its qualifier-and-reference model is the closest widely-deployed precedent for statement-level provenance, and it demonstrates the pattern works at scale."

### Neo4j and property-graph reasoning (§2.8)

Labelled property graph database, Cypher/GQL, graph algorithms. Strengths: native edge properties, so "statement metadata is free"; traversal performance; mature operations; a pleasant path query language. Limits: "**No formal semantics** — entailment is application code"; "Edges cannot be edge endpoints (`knowledge_graph_spec.md` §2.2)"; n-ary needs intermediate nodes; "Property values flat; nested metadata becomes opaque strings".

"CHOIR uses an LPG *projection* for traversal while keeping the hypergraph authoritative. The disqualifier for LPG-as-record is second-order targeting: undercutting defeaters and influences must target edges."

### LegalRuleML — "the closest comparator" (§2.9)

An OASIS standard extending RuleML for legal norms: defeasibility, deontic operators, temporal management, isomorphism between rules and source provisions, and metadata for authorship and jurisdiction. The source states: "**This is the system CHOIR must be most careful to distinguish itself from** (threat T6 in `computational_symbolism_review.md` §6)."

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

The section's assessment is explicitly hedged: "LegalRuleML is a *markup standard* for representing legal rules; CHOIR is a *compiler and execution architecture*. They are not the same kind of artefact, which makes direct comparison awkward — but the overlap in representational commitments is real and substantial."

And: "The four differences that appear genuine: ambiguity representation, interpretive confidence, derived-not-authored confidence, and disjunctive termination. Whether those constitute a different system or an extension is a fair question, and it should be settled by detailed comparison against the current specification rather than by assertion. ⚠️ **Flagged for verification.**"

### Catala (§2.10)

A domain-specific language for statutory and regulatory law, "designed around the observation that legal text is *default logic with exceptions*", pairing code with the legal text it implements through literate programming. Strengths recorded: "**Default-with-exceptions matches legal structure**, as it matches *utsarga/apavāda*"; literate programming keeping text and code adjacent; verified executable code; formal semantics. Limits recorded: it targets "computable law (tax, benefits) — deterministic calculation"; "No graded confidence; law is treated as determinate"; "No ambiguity representation"; "No disjunctive output — a computation returns a value".

"Catala's domain is statutes that *compute* (a tax owed). CHOIR's domains *interpret* — the answer is contested, graded, and sometimes plural. Where Catala can assume determinacy, CHOIR cannot."

The convergence is recorded as evidence: "Catala arrived at default-logic-with-exceptions from French tax law; CHOIR arrived at the same structure from Mīmāṃsā and Pāṇini. Two unrelated legal-textual traditions producing the same computational structure is meaningful support for `computational_primitives.md` §3.12."

### Truth maintenance systems, JTMS / ATMS (§2.11)

Dependency-tracking systems maintaining justifications for beliefs and retracting dependents when a premise is withdrawn; ATMS maintains multiple contexts simultaneously. Strengths: "**Dependency tracking is exactly CHOIR's `derives_from` closure**"; "ATMS multi-context ≈ CHOIR contexts"; efficient retraction; justifications supporting explanation. Limits: no graded support; no source provenance; "Assumption sets can grow exponentially"; "Justification ≠ warrant with a citation".

"CHOIR's traceability invariant is a TMS justification structure with provenance, confidence and defeat typing layered on. The retraction machinery in `execution_pipeline.md` §8 is TMS-derived." What CHOIR takes: "The whole incremental invalidation model."

### Computational Sanskrit (§2.12)

Recorded as distinct from the reasoning systems above but essential to Phase 2, and as already covered in `sanskrit_analysis_pipeline.md` §10: morphological analysers and readers (the Sanskrit Heritage platform named as best-known), annotated corpora (the Digital Corpus of Sanskrit), dependency and kāraka treebanks from Indian NLP groups, digitised classical lexica, and neural work on sandhi splitting and compound analysis.

Strengths: "the segmentation and morphology problems are seriously attacked, with real resources."

Limits, stated as a gap rather than a result: "these tools produce *linguistic analysis*, not *executable rules*. Nothing in this literature, as surveyed, carries the analysis through to a reasoning representation. The gap between a kāraka-labelled parse and an executable defeasible rule is where CHOIR's Phase 2 sits, and it appears genuinely unoccupied."

The section then records the survey's single largest exposure:

> ⚠️ **This is the most important verification item in the document.** A prior system that compiles śāstric text to executable rules would substantially change CHOIR's positioning, and this survey has not searched exhaustively for one.

### Comparison matrix (§3)

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

The source instructs the reader how to discount it:

> **Read this table sceptically.** The final row describes a *design*, not a running system; every other row describes something that exists and has been used. A design scoring well against implemented systems has proved nothing. The table's honest use is to show which columns are unoccupied — **ambiguity** most conspicuously, and **unresolved output** nearly so.

### Verification queue (§4)

Six items are recorded as requiring direct checking before external claims; five carry the ⚠️ marker.

| # | Item | Why it matters |
|---|---|---|
| V1 | ⚠️ Current LegalRuleML specification, in detail | Closest comparator; threat T6 |
| V2 | ⚠️ Prior work compiling śāstric text to executable rules | Would change positioning fundamentally (§2.12) |
| V3 | ⚠️ Interpretive-uncertainty models in semantic-web trust literature | Threat T2 in `computational_symbolism_review.md` |
| V4 | ⚠️ Current capabilities of named Sanskrit NLP resources | Dependency decisions rest on this |
| V5 | ⚠️ Structured argumentation systems reporting unresolved conflict as primary output | *Vikalpa* novelty claim |
| V6 | Catala's current handling of legal ambiguity | May have advanced |

### Positioning (§5)

The document's conclusion is a single conservatively stated claim:

> CHOIR is a **compiler architecture for interpretive normative corpora**. It occupies the gap between computational linguistics (which analyses text but does not produce executable reasoning) and rule engines (which execute rules but assume an authoritative formalisation already exists).
>
> Its distinguishing requirements come from a source type the rule-engine literature has not centred: **a canonical corpus in a dead literary register, with a live interpretive tradition, no outcome ground truth, and centuries of recorded disagreement.**

Four commitments are recorded as forced by that source type and not made by the surveyed systems:

1. Ambiguity survives into the IR.
2. Interpretive uncertainty is a distinct confidence axis.
3. Confidence is derived, never authored.
4. Unresolved conflict is a reportable outcome.

The section closes with a caution rather than a claim: "Everything in this survey is comparison against a design. The correct next step is not to publish a novelty claim but to run `domain_independence.md` §6 and build enough of the benchmark corpus (`canonical_shloka_analysis.md` §12) that the claims have something to be tested against."

## Architectural Implications

The implications the source itself draws:

**External support for three existing decisions.** Three of the surveyed systems are recorded as supporting a CHOIR decision rather than competing with it; the source frames two of the three explicitly as convergence. Cyc's microtheories "vindicate the context primitive", and that Cyc "found contextual partitioning necessary at scale is meaningful evidence for `computational_primitives.md` §3.10" (§2.1). OpenCog's AtomSpace reaches "the same conclusion as `knowledge_graph_spec.md` §3", and the source records that "Independent convergence on hypergraph storage is genuine support for that decision" (§2.2). Catala reaching default-logic-with-exceptions from French tax law, where CHOIR reached it from Mīmāṃsā and Pāṇini, is recorded as "**Independent convergence worth noting**" and as "meaningful support for `computational_primitives.md` §3.12" (§2.10).

**Components adopted rather than reinvented.** The survey records specific inheritance: RETE and the evidence that it scales, from Drools (§2.5); the stratification discipline and negation as failure in qualified form, from Prolog (§2.6); SOAR's impasse-and-subgoal pattern as precedent for escalation as a first-class state rather than an error (§2.3/§2.4); and "the whole incremental invalidation model" from truth maintenance systems, with `execution_pipeline.md` §8 recorded as TMS-derived (§2.11).

**Constraints on the record layer.** Two disqualifications are recorded against candidate substrates. RDF/OWL is monotonic, which is "incompatible with a defeat-centred system"; CHOIR keeps RDF-star as an export target rather than as the record (§2.7). LPG is disqualified as the record layer by second-order targeting — "undercutting defeaters and influences must target edges" — so CHOIR keeps the hypergraph authoritative and uses an LPG projection for traversal (§2.8).

**Two pipeline decisions are given comparative justification.** Saturation-before-adjudication (`execution_pipeline.md` §4.2) is recorded twice: as what eliminates Prolog's clause-order sensitivity (§2.6), and as what allows CHOIR to distinguish *not applicable* from *applied then defeated*, which Drools cannot because resolution happens during matching (§2.5). The prohibition on authored confidence in `confidence_framework.md` §1 is given a concrete referent: "A salience number is exactly the authored, untraceable value `confidence_framework.md` §1 forbids" (§2.5).

**A restriction on what may be published.** The survey does not license a novelty claim. Section 5 states the next step is to run `domain_independence.md` §6 and build enough of the benchmark corpus (`canonical_shloka_analysis.md` §12) "that the claims have something to be tested against", and §4 requires the verification queue be discharged first.

**A live risk to positioning.** Section 2.12 records that a prior system compiling śāstric text to executable rules "would substantially change CHOIR's positioning", and that the survey has not searched exhaustively for one. Section 2.9 records LegalRuleML as threat T6 and flags the four claimed differences as unverified against the current specification.

## Open Questions

Items 1–5 are the five the source records in §6. Items 6 and 7 are the uncertainties it flags in §2.9 and §2.12; item 8 is the caveat it states in §1.

1. **Complete the verification queue (§4) before any external claim.** Six items, five marked ⚠️: the current LegalRuleML specification (V1); prior work compiling śāstric text to executable rules (V2); interpretive-uncertainty models in semantic-web trust literature (V3, threat T2); current capabilities of the named Sanskrit NLP resources, on which dependency decisions rest (V4); structured argumentation systems reporting unresolved conflict as primary output, bearing on the *vikalpa* novelty claim (V5); and Catala's current handling of legal ambiguity, which "May have advanced" (V6).

2. **Is the composition claim testable?** "`computational_symbolism_review.md` §5 argues the mechanisms interlock. Demonstrating that requires showing a system missing one commitment fails in a specific way — an ablation study, which is possible but not designed." (§6)

3. **Should CHOIR target LegalRuleML as an export format?** "If the overlap is as substantial as §2.9 suggests, interoperability may be more valuable than differentiation." (§6)

4. **Catala collaboration.** "The convergence in §2.10 suggests the two projects have a shared problem; the default-logic core may be directly comparable." (§6)

5. **Is "interpretive normative corpora" a recognised category?** "If the literature has a name for this class of system, CHOIR should use it rather than coin one." (§6)

6. **Whether the four LegalRuleML differences constitute a different system or an extension.** Recorded in §2.9 as "a fair question", to "be settled by detailed comparison against the current specification rather than by assertion", and flagged for verification.

7. **Whether the Phase 2 gap is genuinely unoccupied.** Section 2.12 states the gap between a kāraka-labelled parse and an executable defeasible rule "appears genuinely unoccupied", qualified immediately by the admission that the survey "has not searched exhaustively" for a counterexample.

8. **Version-level capability of the systems surveyed.** The §1 caveat records that "specific version-level capabilities have not been verified against current documentation", and requires that "each row marked ⚠️ in §4 must be checked directly" before any external novelty claim.

## Related Documents

Documents this source depends on, feeds, or cites:

- [YK-R-017 — Computational Symbolism Review](YK-R-017-computational-symbolism-review.md) — stated dependency (header); source of threat T6 (§2.9), threat T2 (§4), the OWL/RDF treatment (§2.7), and the composition argument at §5 (§6).
- [YK-R-001 — Computational Primitive Specification](YK-R-001-computational-primitive-specification.md) — §3.10 (contexts) and §3.12 (default-with-exceptions), both cited as receiving external support.
- [YK-R-003 — Knowledge Graph Specification](YK-R-003-knowledge-graph-specification.md) — §3 (hypergraph store, RDF-star as export), §2.5 (exclusion of unauditable numeric influence), §2.2 (edges as edge endpoints), §2.1 (RDF/OWL).
- [YK-R-005 — Sanskrit Analysis Pipeline](YK-R-005-sanskrit-analysis-pipeline.md) — §10, where the computational Sanskrit landscape of §2.12 is covered.
- [YK-R-008 — Canonical Shloka Analysis (Benchmark)](YK-R-008-canonical-shloka-analysis-benchmark.md) — §12, the benchmark corpus §5 names as prerequisite to any claim.
- [YK-R-009 — Evidence Model](YK-R-009-evidence-model.md) — §3.3, the observability condition negation as failure lacks (§2.6).
- [YK-R-011 — Confidence Framework](YK-R-011-confidence-framework.md) — §1, the prohibition on authored confidence contrasted with Drools salience (§2.5).
- [YK-R-015 — Execution Pipeline](YK-R-015-execution-pipeline.md) — §4.2 (saturation before adjudication) and §8 (TMS-derived retraction).
- [YK-R-016 — Domain Independence](YK-R-016-domain-independence.md) — §6, the measurement §5 names as the next step before publishing a novelty claim.
