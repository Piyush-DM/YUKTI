# Vedic Reasoning Methodology

| | |
|---|---|
| **Document ID** | YK-R-004 |
| **Source** | `choir/research/phase-2-vedic/vedic_reasoning_methodology.md` (004) |
| **Series** | CHOIR Research Programme |
| **Revision** | A |
| **Status** | Active |
| **Last Updated** | 2026-08-23 |

## Abstract

This document studies the inferential machinery of classical Jyotiṣa texts — what counts as a reason, how rules compose, what defeats what, and how conflict is settled (§0.1). Its central finding is that the tradition supplies its own conflict-resolution and explanation machinery, drawn from Nyāya, Mīmāṃsā and Vyākaraṇa, and that this machinery is more precisely specified than what most modern rule engines ship with; CHOIR does not need to invent these mechanisms, it needs to formalise them (§1). The analysis closes by deriving thirteen numbered computational requirements (R1–R13) that the corpus imposes on the rest of the system (§7).

This document carries the status **Active**: it is a research document, drafted but **not accepted as specification**. The source itself is marked "Draft for review". Per `choir/research/README.md`, all 18 research deliverables are drafted, none accepted, and every document is a hypothesis.

## Research Question

The source states its question explicitly in §0.1:

> *How do classical Jyotiṣa texts actually reason?* Not: are their conclusions correct. The object of study is the **inferential machinery** — what counts as a reason, how rules compose, what defeats what, how conflict is settled.

§0.2 restricts the claim being made, restating the commitment from `computational_primitives.md` §0.1 "because this document is where it is most likely to be misread":

- **Claimed:** that a given rule is what a given text says; that a conclusion follows from that rule under stated semantics; that the derivation is reconstructible.
- **Not claimed:** that the rule is true of the world, or that the predictions it licenses are borne out.

The source states plainly that "Jyotiṣa's predictive claims are not empirically supported, and CHOIR is not evidence for them" (§0.2). What the corpus offers instead is one of the most highly developed **defeasible rule corpora** in existence: thousands of interacting conditional rules with explicit cancellation conditions, strength gradations, reference-frame parameterisation, contextual scoping, and centuries of commentarial conflict resolution — a stress test for a reasoning compiler harder than most legal corpora. **The validation target is therefore textual fidelity, not predictive accuracy** (§0.2).

## Finding

### The tradition supplies its own reasoning apparatus (§1)

Jyotiṣa is a *śāstra*, and śāstric argument inherits a shared toolkit from three neighbouring disciplines:

| Discipline | Contributes | CHOIR relevance |
|---|---|---|
| **Nyāya** | Theory of inference and of evidence-kinds; fallacy taxonomy | Evidence typing; conflict classification |
| **Mīmāṃsā** | Rule interpretation, injunction theory, precedence ordering | Conflict resolution; extraction gating |
| **Vyākaraṇa** (Pāṇinian grammar) | Meta-rules governing rule application | Rule ordering; blocking; exception handling |

The source names this as its central finding: the tradition supplies its own conflict-resolution and explanation machinery, more precisely specified than what most modern rule engines ship with (§1).

### Evidence typing: the *pramāṇa* framework (§2)

Classical Indian epistemology types knowledge by its means of acquisition (*pramāṇa*). The source maps the Nyāya set of four and the Mīmāṃsā extension to six onto CHOIR evidence types:

| *Pramāṇa* | Gloss | Modern analogue | CHOIR evidence type |
|---|---|---|---|
| *pratyakṣa* | Perception | Direct observation | `direct` |
| *anumāna* | Inference | Rule-based derivation | `derived` |
| *upamāna* | Comparison / analogy | Case-based, analogical reasoning | `analogical` |
| *śabda* | Reliable testimony | Authority; cited source | `attested` |
| *arthāpatti* | Postulation | Abduction; inference to best explanation | `abductive` |
| *anupalabdhi* | Non-apprehension | **Negation as failure** | `absence` |

Two are emphasised. **`anupalabdhi`** — reasoning from absence — is the Mīmāṃsā (and Advaita) recognition of non-apprehension as an independent means of knowledge, and is identified as a direct precursor of negation as failure, with the qualification that the classical formulation includes an **observability condition**: non-apprehension licenses denial only where apprehension *would have occurred*. The source states that this condition "is exactly what modern closed-world reasoning gets wrong when it is applied naively to incomplete data," and that CHOIR adopts the qualified form — absence-evidence admissible only where the context declares the relevant domain complete (§2, referring to `evidence_model.md` §3.4). **`śabda`** — testimony — is a first-class means of knowledge in this tradition rather than a fallback, which is what makes the corpus a normative rather than an empirical system and makes source-authority ranking (`conflict_resolution.md` §5) central rather than peripheral (§2).

### *Vyāpti* and *upādhi*: an exact correspondence with undercutting defeat (§2.1)

An inference (*anumāna*) is licensed by *vyāpti*, invariable concomitance between the reason (*hetu*) and what is inferred (*sādhya*), established by *anvaya* (positive co-presence) and *vyatireka* (negative co-absence), and threatened by *upādhi* — a conditioning factor that vitiates the pervasion: an unstated additional condition on which the concomitance actually depends.

The source states that *upādhi* **is an undercutting defeater**: it does not assert the opposite conclusion, it shows the inferential link was never warranted. It records the correspondence with Pollock's undercutting defeater (`computational_primitives.md` §3.12) as "exact," and describes it as "a striking convergence between two traditions separated by a millennium." The consequence drawn is that CHOIR's exception typology is a formalisation of a distinction the corpus already draws, not an imposition on it (§2.1).

### *Hetvābhāsa*: a native conflict taxonomy (§2.2)

Nyāya's classification of defective reasons maps onto CHOIR's conflict classes:

| *Hetvābhāsa* | Defect | CHOIR conflict class |
|---|---|---|
| *savyabhicāra* / *anaikāntika* | Inconclusive — the reason strays; occurs with and without the *sādhya* | Non-discriminating condition |
| *viruddha* | Contradictory — the reason proves the opposite | Rebutting defeat |
| *satpratipakṣa* | Counterbalanced — an equally strong reason for the opposite | **Genuine tie → *vikalpa* or escalation** |
| *asiddha* | Unestablished — a premise fails | Premise defeat |
| *bādhita* | Contradicted — a stronger means of knowledge overrides | Precedence loss (*bādha*) |

The source records that this maps "almost one-to-one" onto the conflict typology derived independently in `conflict_resolution.md` §3, and singles out *satpratipakṣa*: the tradition has a name for a conflict that is genuinely balanced and treats it as a terminal state of analysis rather than something to be broken arbitrarily. Most rule engines cannot represent this; CHOIR must (§2.2, §5.3).

### Symbol resolution is deferred to query time (§3)

Jyotiṣa's vocabulary is systematically polysemous by design — a single significator maps to a field of referents across domains (the source tabulates Sūrya as father/authority/king, bone/right eye/vitality, the east, soul/self, gold/copper). The source states this is not vagueness but a **structured mapping**, with the structure supplied by *kāraka* (significator) assignments, *bhāva* (house) significations, and elemental/qualitative correspondences (§3.1).

The computational problem is identified as **sense selection**: when a rule concludes "Sūrya is afflicted," the referent is fixed by the question being asked, not by the rule. This is what `Context.purpose` is for (`computational_primitives.md` §3.10) — the source states that without it "the rule is genuinely under-determined," and that a system resolving symbols at extraction time rather than query time "will produce a corpus that answers only one kind of question." The stated **design rule** is that symbol → referent mappings are stored as context-scoped relations, not resolved during compilation: the compiler preserves the symbol, the executor resolves it against the query context and records which mapping it used (§3.1).

Analogical transfer (*upamāna*) is modelled as an `analogical` inference license (001 §3.13) that is **strongly defeasible** and must record its correspondence explicitly — source structure, target structure, mapped relations, and critically the relations *not* mapped. The source's reason: "An analogy that does not state its limits cannot be defeated, and an undefeatable inference is not a reasoning step" (§3.2).

### Exception structure: *utsarga*/*apavāda* and layered *bhaṅga* (§4)

The general rule (*utsarga*) / exception (*apavāda*) pair is the fundamental structure of śāstric rule systems. The source is explicit that the relationship is **not** contradiction: the exception restricts the domain of the general rule, and where the exception applies the general rule was never applicable. Computationally, a defeated general rule "does not produce a negated conclusion, it produces *no* conclusion from that source, leaving the field to other evidence" — the undercutting pattern again, and the tradition's default (§4.1).

Cancellation (*bhaṅga*) is layered — the best-known family being *nīca-bhaṅga* (cancellation of debilitation), where a graha in its sign of debilitation has that weakness annulled *under specified conditions*:

```
base configuration       →  yields result R
  + cancellation cond.   →  R suppressed
    + counter-condition  →  cancellation itself annulled → R restored (sometimes modified)
```

Exceptions to exceptions are described as *normal*, not edge cases — decisive for treating `Exception` as a first-class object rather than a boolean field (`computational_primitives.md` §3.12) and for the well-foundedness requirement on defeater chains (`conflict_resolution.md` §6). The source further records that the commentarial literature **disagrees substantially** about the precise conditions for *nīca-bhaṅga*, and rules that this disagreement is **interpretive confidence** (011 §3), not extraction error, and must be recorded as such rather than resolved by picking a favourite (§4.2).

### The *vidhi* apparatus as an extraction gate (§4.3)

Mīmāṃsā's classification of statement types is used directly as an extraction gate:

| Type | Nature | Extract as a rule? |
|---|---|---|
| *vidhi* | Injunction — enjoins an action or asserts a relation | Yes |
| *niṣedha* | Prohibition | Yes, with negative modality |
| *arthavāda* | Commendatory or explanatory passage; praise, blame, narrative | **No** |
| *nāmadheya* | Naming — assigns a designation | As a definition, not a rule |
| *mantra* | Liturgical formula | No |

The source calls the *arthavāda* exclusion "the single most valuable extraction heuristic available": a large fraction of śāstric verse is laudatory or illustrative, and naively extracting such lines as rules "produces a corpus full of unfalsifiable superlatives." It notes a grammatical signal — injunctions characteristically appear in the optative (*vidhi-liṅ*) or use gerundive/necessitative forms — making the gate **partly** automatable via the Sanskrit pipeline (`sanskrit_analysis_pipeline.md` §7, `canonical_shloka_analysis.md` §4).

### Rule composition, stratification, and strength (§5.1–§5.2)

The corpus composes rules in a consistent pipeline shape: static configuration → combination detection (yoga) → strength modulation (*bala*) → cancellation/affliction (*bhaṅga*) → temporal activation (*daśā* / *gochara*) → aggregate judgement. Three observations carry design consequences (§5.1):

1. **Detection and strength are separate stages.** A yoga either forms or does not (boolean), and separately has a strength (graded). Collapsing these into one weighted score loses the corpus's own distinction and makes cancellation — which operates on formation, not on strength — inexpressible.
2. ***Bala* is an explicit quantitative apparatus.** *Ṣaḍbala* sums positional, directional, temporal, motional, natural and aspectual components, and maps onto CHOIR's confidence decomposition requirement "rather well." **Caveat, stated in the source:** the components are ordinal-to-interval at best, and the received computations vary between authorities — so "the *structure* is adoptable, the *numbers* are not authoritative" (cf. the `Measure.scale_type` warning in `reasoning_ontology.md` §3.1).
3. **Temporal activation is a separate gate**, a clean instance of the valid time vs decision time separation (001 §3.17).

Judgements are built at multiple levels — graha → bhāva → yoga → daśā → overall — with higher-level rules able to override lower-level indications. The source identifies this as a **stratified rule system**, and stratification as what makes termination provable (`reasoning_language.md` §7.3) and what lets `execution_pipeline.md` §4 compute derived facts in dependency order rather than needing a general fixpoint (§5.2).

### Conflict resolution: what the tradition supplies (§5.3)

The source states this is where the classical apparatus most exceeds standard rule-engine practice.

**Mīmāṃsā's interpretive priority ordering**, quoted from the source:

> *śruti* (direct statement) > *liṅga* (indicatory power of a word) > *vākya* (syntactic connection) > *prakaraṇa* (contextual setting) > *sthāna* (position) > *samākhyā* (name)

This is described as "a **ready-made precedence lattice for interpretive conflict**," adopted directly in `conflict_resolution.md` §5.2.

**Pāṇinian meta-rules (*paribhāṣā*).** Two from the *Aṣṭādhyāyī* are held directly reusable:

- ***vipratiṣedhe paraṃ kāryam*** (A. 1.4.2) — where two rules of equal scope conflict, the later prevails: *lex posterior*, "stated as a formal meta-rule roughly two and a half millennia before its Latin restatement."
- ***pūrvatrāsiddham*** (A. 8.2.1) — rules in a designated section are treated as "not having taken effect" with respect to earlier rules, imposing a **phase ordering** on rule application.

Together with *utsarga*/*apavāda* (*lex specialis*), the tradition supplies specificity, recency, and phase-ordering meta-rules — "the three axes any serious rule-conflict system needs."

**Resolution outcomes.** Mīmāṃsā names outcomes most engines lack:

| Outcome | Meaning | Engine support elsewhere |
|---|---|---|
| *bādha* | Sublation — the stronger rule cancels the weaker | Common |
| *samuccaya* | Conjunction — both apply together | Common |
| ***vikalpa*** | **Optionality — both are admissible; either may be followed** | **Rare** |

*vikalpa* is singled out as the important one: a legitimate terminal state in which two rules conflict, neither defeats the other, and the correct output is *both alternatives with their support*, not a forced choice. Combined with *satpratipakṣa* (§2.2), the tradition both recognises balanced conflict and prescribes what to do about it. The conclusion drawn: **CHOIR must be able to terminate in a disjunction**; a system that always returns one answer cannot be faithful to this corpus, and per `domain_independence.md` §4 cannot be faithful to law or medicine either, where genuine unresolved splits are routine (§5.3).

### Context dependence (§6)

Conclusions in this corpus are systematically parameterised by context. The source tabulates six dimensions: *varga* (divisional chart — Rāśi (D-1), Navāṃśa (D-9), and others), reference frame (from Lagna, from Candra, from a graha), birth condition (*divā* / *rātri*), application (*jātaka*, *praśna*, *muhūrta*), school (Parāśara, Jaimini, Tājika, and others), and query purpose (medical, relational, vocational — selecting the symbol mapping per §3.1).

**Reference frame is called the most computationally consequential.** Counting "from the Moon" rather than "from the Ascendant" is a parameter of the rule, expressed grammatically by the ablative case; this is why role-labelled n-ary storage matters (`knowledge_graph_spec.md` §7), since flattening the reference frame into a binary edge loses it.

**School incompatibility is not conflict.** Parāśara and Jaimini rules "are not competitors to be adjudicated; they are *different systems*," and mixing them produces incoherence. The context lattice must keep them separated and the conflict detector must not report cross-school differences as contradictions. The source states the primary practical use of the context lattice this way: **most apparent contradictions are context collisions** (`conflict_resolution.md` §4).

### Source-critical constraints carried into every extraction (§0.3)

The source records two facts that must be carried into every extraction:

- **Textual instability.** *Bṛhat Parāśara Horā Śāstra*, the most-cited Jyotiṣa source, "has a contested transmission history: it circulates in multiple recensions of differing length, and its received form is generally regarded by scholars as considerably later than its attributed authorship. Verse numbering differs between editions."
- **Translation drift.** Most working practitioners use translations, and translations differ substantially — "particularly on quantifiers, conditionals, and the scope of exception clauses, which is exactly what a rule compiler depends on."

**Operational consequence (§0.3):** every extracted rule must record its *edition* and *translator*, not merely "BPHS ch. X"; citations that cannot be checked against a stated edition are marked `citation_unverified` and carry reduced extraction confidence, enforced in `rule_extraction_framework.md` §5. Transliteration throughout is IAST, with technical terms glossed on first use and thereafter used untranslated "because the English glosses are lossy in precisely the ways that matter" (§0.4).

## Architectural Implications

§7 states the requirements this analysis imposes on the rest of the system, each traced to its source in the tradition and to the document that specifies it:

| # | Requirement | Source in the tradition | Specified in |
|---|---|---|---|
| R1 | Six evidence types, including absence-evidence with an observability condition | *pramāṇa*, *anupalabdhi* | `evidence_model.md` §3 |
| R2 | Undercutting defeat distinct from rebutting defeat | *upādhi*, *apavāda* | `computational_primitives.md` §3.12 |
| R3 | Exceptions to exceptions, arbitrarily nested, well-founded | *bhaṅga* layering | `conflict_resolution.md` §6 |
| R4 | Precedence by specificity, recency, and phase | *utsarga/apavāda*, A. 1.4.2, A. 8.2.1 | `conflict_resolution.md` §5 |
| R5 | Interpretive precedence ordering for textual conflict | Mīmāṃsā six-fold ordering | `conflict_resolution.md` §5.2 |
| R6 | **Termination in a disjunction** (`vikalpa`) as a first-class outcome | *vikalpa*, *satpratipakṣa* | `conflict_resolution.md` §7 |
| R7 | Extraction gate excluding non-injunctive passages | *arthavāda* / *vidhi* distinction | `rule_extraction_framework.md` §4 |
| R8 | Symbol resolution deferred to query context | *kāraka* polysemy | `execution_pipeline.md` §3 |
| R9 | Separation of formation (boolean) from strength (graded) | yoga vs *bala* | `confidence_framework.md` §4 |
| R10 | Reference frame as an explicit rule parameter | ablative reckoning | `knowledge_graph_spec.md` §7 |
| R11 | Explanation structured as claim/reason/rule/application/conclusion | *pañcāvayava* | `explainability_framework.md` §3 |
| R12 | Conflict taxonomy including "genuinely balanced" | *hetvābhāsa* | `conflict_resolution.md` §3 |
| R13 | Cross-school difference is not contradiction | school contexts | `conflict_resolution.md` §4 |

R11 refers to the Nyāya five-membered demonstration (*pañcāvayava*): *pratijñā* (thesis), *hetu* (reason), *udāharaṇa* (general rule with example), *upanaya* (application to the case), *nigamana* (conclusion). The source describes it as "a fully-formed explanation schema" and records that it is adopted as CHOIR's explanation template (§7, `explainability_framework.md` §3).

Two further points are recorded by the source rather than derived here. First, the source sets the validation target as textual fidelity rather than predictive accuracy, and says it states this "plainly here so that no downstream document has to hedge" (§0.2) — the disclaimer is made once, in this document, rather than repeated downstream. Second, on *ṣaḍbala* the source records that "the *structure* is adoptable, the *numbers* are not authoritative" (§5.1); whether CHOIR should ship any default weights or force the user to select an authority it leaves unresolved (§8, question 1).

## Open Questions

The source records five open questions in §8:

1. **How much *bala* arithmetic is authoritative?** The component structure is well-attested; the numeric weights vary by authority and edition. Whether CHOIR should ship any default weights, or force the user to select an authority, is unresolved.
2. **Is *arthāpatti* distinct from abduction in a way that matters computationally?** The classical formulation is narrower than modern inference-to-best-explanation; treating them as identical may be a fidelity loss.
3. **Should school contexts be siblings or incomparable?** If Parāśara and Jaimini are incomparable in the lattice, no cross-school conflict can ever be adjudicated — "probably correct, but it forecloses synthesis that practitioners do perform."
4. **Where does *anupalabdhi*'s observability condition come from computationally?** It requires declaring a domain complete. Who declares it, and on what authority, is unresolved and matters for R1.
5. **The extent of the *arthavāda* boundary.** Some passages are simultaneously commendatory and injunctive. Mīmāṃsā has extensive machinery for this; how much of it CHOIR needs "is unknown until extraction is attempted at scale."

Additional unresolved or unverified items recorded elsewhere in the source:

- The commentarial literature disagrees substantially about the precise conditions for *nīca-bhaṅga*; the disagreement is to be recorded as interpretive confidence rather than resolved (§4.2).
- Citations that cannot be checked against a stated edition are marked `citation_unverified` and carry reduced extraction confidence (§0.3).
- The *arthavāda* extraction gate is only **partly** automatable from morphological signals (§4.3).

The source document is itself marked "Draft for review" and, at the status assigned to this publication (Active), is drafted but not accepted as specification. Per `choir/research/README.md`, every document in this series is a hypothesis; `MANIFESTO.md` states the underlying commitment as "Treat every computational object as a hypothesis rather than an established truth."

## Related Documents

Depends on:

- [YK-R-001 — Computational Primitive Specification](YK-R-001-computational-primitive-specification.md) (`computational_primitives.md`; §0.2, §2.1, §3.1, §3.2, §4.2, §5.1)
- [YK-R-002 — Reasoning Ontology](YK-R-002-reasoning-ontology.md) (`reasoning_ontology.md`; §5.1)

Feeds:

- [YK-R-007 — Rule Extraction Framework](YK-R-007-rule-extraction-framework.md) (`rule_extraction_framework.md`; §0.3, §7)
- [YK-R-010 — Conflict Resolution](YK-R-010-conflict-resolution.md) (`conflict_resolution.md`; §2, §2.2, §4.2, §5.3, §6, §7)
- [YK-R-012 — Explainability Framework](YK-R-012-explainability-framework.md) (`explainability_framework.md`; §7)

Also cited:

- [YK-R-003 — Knowledge Graph Specification](YK-R-003-knowledge-graph-specification.md) (`knowledge_graph_spec.md`; §6, §7)
- [YK-R-005 — Sanskrit Analysis Pipeline](YK-R-005-sanskrit-analysis-pipeline.md) (`sanskrit_analysis_pipeline.md`; §4.3)
- [YK-R-008 — Canonical Shloka Analysis (Benchmark)](YK-R-008-canonical-shloka-analysis-benchmark.md) (`canonical_shloka_analysis.md`; §4.3)
- [YK-R-009 — Evidence Model](YK-R-009-evidence-model.md) (`evidence_model.md`; §2, §7)
- [YK-R-011 — Confidence Framework](YK-R-011-confidence-framework.md) (`confidence_framework.md`; §4.2, §7)
- [YK-R-014 — Reasoning Language (CRL)](YK-R-014-reasoning-language-crl.md) (`reasoning_language.md`; §5.2)
- [YK-R-015 — Execution Pipeline](YK-R-015-execution-pipeline.md) (`execution_pipeline.md`; §5.2, §7)
- [YK-R-016 — Domain Independence](YK-R-016-domain-independence.md) (`domain_independence.md`; §5.3)
