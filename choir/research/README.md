# CHOIR Research Programme

Research cycle producing the computational framework for translating Vedic reasoning into
executable institutional reasoning.

**Status:** All 18 deliverables drafted. None accepted. Every document is a hypothesis, per
`MANIFESTO.md`.

---

## 1. What this cycle produced

| # | Deliverable | Phase | File |
|---|---|---|---|
| 001 | Computational Primitives | 1 | [computational_primitives.md](phase-1-foundations/computational_primitives.md) |
| 002 | Reasoning Ontology | 1 | [reasoning_ontology.md](phase-1-foundations/reasoning_ontology.md) |
| 003 | Knowledge Graph Specification | 1 | [knowledge_graph_spec.md](phase-1-foundations/knowledge_graph_spec.md) |
| 004 | Vedic Reasoning Methodology | 2 | [vedic_reasoning_methodology.md](phase-2-vedic/vedic_reasoning_methodology.md) |
| 005 | Sanskrit Analysis Pipeline | 2 | [sanskrit_analysis_pipeline.md](phase-2-vedic/sanskrit_analysis_pipeline.md) |
| 006 | Shloka Compiler | 2 | [shloka_compiler.md](phase-2-vedic/shloka_compiler.md) |
| 007 | Rule Extraction Framework | 2 | [rule_extraction_framework.md](phase-2-vedic/rule_extraction_framework.md) |
| 008 | Canonical Shloka Analysis **(benchmark)** | 2 | [canonical_shloka_analysis.md](phase-2-vedic/canonical_shloka_analysis.md) |
| 009 | Evidence Model | 3 | [evidence_model.md](phase-3-institutional/evidence_model.md) |
| 010 | Conflict Resolution | 3 | [conflict_resolution.md](phase-3-institutional/conflict_resolution.md) |
| 011 | Confidence Framework | 3 | [confidence_framework.md](phase-3-institutional/confidence_framework.md) |
| 012 | Explainability Framework | 3 | [explainability_framework.md](phase-3-institutional/explainability_framework.md) |
| 013 | CHOIR Intermediate Representation | 4 | [choir_intermediate_representation.md](phase-4-compiler/choir_intermediate_representation.md) |
| 014 | Reasoning Language (CRL) | 4 | [reasoning_language.md](phase-4-compiler/reasoning_language.md) |
| 015 | Execution Pipeline | 4 | [execution_pipeline.md](phase-4-compiler/execution_pipeline.md) |
| 016 | Domain Independence | 5 | [domain_independence.md](phase-5-generalization/domain_independence.md) |
| 017 | Computational Symbolism Review | 5 | [computational_symbolism_review.md](phase-5-generalization/computational_symbolism_review.md) |
| 018 | Related Work Survey | 5 | [related_work.md](phase-5-generalization/related_work.md) |

---

## 2. Reading order

**To understand the architecture:** 001 → 002 → 013 → 015.

**To understand the source-fidelity claim:** 004 → 005 → 006 → 008.

**To understand the epistemics:** 009 → 010 → 011 → 012.

**To assess the project's claims critically:** 016 → 017 → 018, then 008 §11.

**If you read only one document:** 008, the canonical shloka benchmark. It carries a single
verse through every stage and exhibits the whole system, including its failures.

---

## 3. The commitments everything else follows from

These recur across documents and are the load-bearing decisions.

| # | Commitment | Established in |
|---|---|---|
| 1 | **Fidelity, not truth.** CHOIR claims what a corpus says, never that it is correct. Jyotiṣa calibrates against textual fidelity; medicine against outcomes. | 001 §0.1, 004 §0.2, 011 §7 |
| 2 | **Confidence is derived, never authored.** No one may type a number. | 011 §1 |
| 3 | **Three confidence axes** — extraction, interpretive, inferential — never collapsed. | 011 §2 |
| 4 | **Undercutting ≠ rebutting.** Cancellation withdraws a rule; it does not assert the opposite. | 001 §3.12, 008 §9.2 |
| 5 | **Influence is second-order.** It modulates edges and cannot assert conclusions. | 001 §3.7, 013 §4.6 |
| 6 | **Ambiguity is a first-class IR citizen.** The compiler emits diagnostics rather than guessing. | 006 §7, 013 §3.1 |
| 7 | **Saturate, then adjudicate.** Fire every rule before resolving anything. | 015 §4.2 |
| 8 | ***Vikalpa*** — terminating in a legitimate disjunction is a valid output. | 010 §7.1, 016 §4 |
| 9 | **Explanations are projections of the trace**, never regenerated. | 012 §1 |
| 10 | **Neural retrieval, symbolic adjudication.** Embeddings propose; they never conclude. | 003 §2.5 |
| 11 | **Evidence independence is computed**, not assumed. Correlated evidence is discounted. | 009 §4 |
| 12 | **Nothing is deleted.** Defeated objects are marked and retained. | 003 I5 |
| 13 | **An unevaluated thing is never a false thing.** Coverage gaps are reported. | 015 §12 |

---

## 4. What the tradition supplied

A finding worth recording separately: several mechanisms were not designed but **adopted**,
because the classical apparatus was already more precise than standard rule-engine practice.

| Adopted | From | Used as |
|---|---|---|
| *pramāṇa* typology | Nyāya / Mīmāṃsā | Evidence types (009 §3) |
| *anupalabdhi* with its observability condition | Mīmāṃsā | Absence-reasoning, better-qualified than negation-as-failure (009 §3.3) |
| *upādhi* | Nyāya | Undercutting defeat — the same distinction as Pollock's (004 §2.1) |
| *hetvābhāsa* | Nyāya | Conflict taxonomy (010 §3.1) |
| *utsarga* / *apavāda* | Mīmāṃsā | *Lex specialis* (010 §5.1) |
| *vipratiṣedhe paraṃ kāryam* (A. 1.4.2) | Pāṇini | *Lex posterior* as a formal meta-rule |
| *pūrvatrāsiddham* (A. 8.2.1) | Pāṇini | Phase ordering |
| Six-fold interpretive priority | Mīmāṃsā | Precedence for textual conflict (010 §5.2) |
| *vidhi* / *arthavāda* distinction | Mīmāṃsā | The extraction gate (007 §4) |
| *vikalpa*, *samuccaya*, *bādha* | Mīmāṃsā | Resolution outcomes (010 §7) |
| *kāraka* roles | Pāṇini | Hyperedge participant roles (003 §7) |
| *pañcāvayava* | Nyāya | The explanation schema (012 §3) |

---

## 5. Relationship to the existing repository

`README.md` freezes repository organisation and requires that implementation be driven only
by approved specifications. Nothing here is approved. These documents are **research inputs
to specifications**, not specifications.

### 5.1 Mapping to the empty placeholders

The pre-existing empty files map as follows. **They have not been modified** — populating
them is a specification act requiring approval.

| Existing empty file | Populated by |
|---|---|
| `choir/ontology/computational_universe.md` | 001 §§1–3 |
| `choir/ontology/primitive_validation.md` | 001 §1 (admission test), 002 §8 (V1–V9) |
| `choir/ontology/relationship_validation.md` | 002 §4.1, 003 §6 (I1–I12) |
| `choir/research/R001_Institutional_Arbitration.md` | 010 |
| `choir/research/R002_Proposal_Structure.md` | 001 §4 (Proposal as composite) — **thinnest coverage** |
| `choir/research/R003_Evidence_Representation.md` | 009 |
| `choir/research/R004_Uncertainty_Representation.md` | 011 |
| `choir/research/R005_Contradiction_Lifecycle.md` | 010 §10 |
| `choir/research/R006_Traceability.md` | 012 |
| `choir/specifications/SPEC-001_Epistemic_Foundation.md` | 001 §0, 004 §0, 011 §7 |
| `choir/specifications/SPEC-002_Primitive_Objects.md` | 001 |
| `choir/specifications/SPEC-003_Reasoning_Model.md` | 013, 014, 015 |
| `choir/specifications/SPEC-004_Arbitration.md` | 010 |

**R002 (Proposal Structure) is the gap.** `Proposal` and `Decision` are treated as composites
in 001 §4 and are not developed further. Both are institutional-process notions rather than
reasoning notions, and 002 §10.5 questions whether `Decision` belongs at L1 at all. This is
the one brief-adjacent area this cycle did not cover.

### 5.2 DAALE module boundaries

The reserved scaffolds in `daale/ontology/` now have research backing:

| Module | Backed by | Note |
|---|---|---|
| `base.py` | 001, 002 | Primitive kinds and hierarchy |
| `evidence.py` | 009 | |
| `confidence.py` | 011 | |
| `contradiction.py` | 010 | |
| `relationships.py` | 002 §4, 003 §4.2 | |
| `proposal.py` | — | **Underspecified** — see R002 gap |
| `decision.py` | — | **Underspecified**; L1 membership questioned |

Per `IMPLEMENTATION_QUEUE.md`, these remain frozen until specifications are approved.

---

## 6. What is not done

Stated plainly, because the deliverable list being complete is not the same as the research
being finished.

| # | Gap | Where |
|---|---|---|
| G1 | **The domain-independence metric has never been run.** Only Jyotiṣa is worked through. | 016 §6 |
| G2 | **The benchmark verse is uncited.** `E-ATTEST` is unresolved; no critical edition checked. | 008 §1.2, §12 |
| G3 | **No gold set exists**, so no pipeline stage can be evaluated. | 005 §10, 007 §8 |
| G4 | **The Jyotiṣa technical lexicon does not exist**, and sandhi splitting depends on it. | 005 §10 |
| G5 | **The influence-vs-causation falsifier is untested** — the framework's own stated disconfirmation. | 001 §5, 017 §4.6 |
| G6 | **Literature verification queue is open**; no external novelty claim is currently supportable. | 018 §4 |
| G7 | **Proposal / Decision underspecified.** | §5.1 |
| G8 | **Saturation cost at corpus scale is unmeasured** and could be prohibitive. | 015 §13.1 |
| G9 | **Deontic depth is shallow** — modality tags, not a deontic logic. Likeliest source of a core-schema failure for law. | 014 §9.5, 016 §10.4 |

---

## 6.1 What the prototype has since settled

The executable prototype in [`choir_prototype/`](../../choir_prototype/) — **frozen at
V0.1** — closed one of the gaps above and sharpened another.

| Was | Now |
|---|---|
| **G1** the domain-independence metric had never been run | **Measured: portability 1.00** across four domains with a hold-out control. `domain_independence.md` §6.1 |
| **G5** the influence/causation falsifier untested | Still untested, but **F3 (graded defeat) is now the priority falsifier** — the prototype cannot test it, because it has no defeat typing |

G2, G3, G4, G6, G7, G8 and G9 are unchanged. The prototype is deliberately far narrower
than the research: no defeat typing, no context lattice, no precedence ordering, no
ambiguity representation, no provenance chain to source text.

---

## 7. Recommended next milestone

Not more documents. The cycle's own analysis points at one milestone that would test the
most assumptions per unit of effort:

> **Build the benchmark corpus: 20–30 rules around Gajakesarī, fully cited.**

This means resolving G2, extracting the three exception verses, extracting the *nīca-bhaṅga*
exception-to-exception, extracting the outcome verses separately, and adding one verse that
formulates the yoga differently.

That single corpus would exercise: citation discipline, multi-rule evidence accumulation
(009), correlation clustering (009 §4), well-founded defeater chains (010 §6), *vikalpa*
(010 §7), the three confidence axes (011), and coverage reporting (012) — all against real
text rather than a worked example.

It would also be small enough that dual extraction (007 §5.1) is affordable, which is what
makes the consistency metrics in 007 §8 computable for the first time.

Running the domain-independence metric (G1) on 20 legal rules in parallel would test the
other half of the architecture at comparable cost.
