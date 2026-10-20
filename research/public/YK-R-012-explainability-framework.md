# Explainability Framework

| | |
|---|---|
| **Document ID** | YK-R-012 |
| **Source** | `choir/research/phase-3-institutional/explainability_framework.md` (012) |
| **Series** | CHOIR Research Programme |
| **Revision** | A |
| **Status** | Active |
| **Last Updated** | 2026-08-23 |

## Abstract

This document establishes that CHOIR explanations are projections of the execution record — never regenerated, paraphrased, or reconstructed by a separate process — and that faithfulness therefore holds by construction rather than by evaluation (§1). It specifies the seven mandatory components of an explanation (§2), adopts the Nyāya *pañcāvayava* as the explanation schema (§3), defines the trace as a DAG with a replay guarantee (§4), fixes four audience renderings as views over one trace (§6), and lists eight verification tests (§9). The source carries the status "Draft for review" and records six open questions, including one it states outright is "not solved here" (§10.6).

**Status note.** This publication has status **Active**: the research document is complete and drafted, but it has *not* been accepted as specification. Per `MANIFESTO.md`, every research document is a hypothesis. Nothing below should be read as a governing ruling.

## Research Question

The source does not state a research question in those words. Its governing framing is the constraint it opens with (§1): explanations must be projections of the execution record rather than narratives produced by a second process. The operative question it sets out to answer is stated in §2 as a requirement inherited from the brief — that every inference must answer "Why?" — and the document proceeds by asking what components that answer must contain (§2), what schema it should take (§3), what structure the record must have to support it (§4), how it should differ by audience without diverging (§6), and how the property can be tested (§9).

## Finding

### 1. The governing constraint (§1)

The source states the constraint verbatim as:

> **Explanations are *projections of the execution record*. They are never regenerated, paraphrased, or reconstructed by a separate process.**

It calls this "the single most important design decision in this document," and identifies it as what distinguishes a CHOIR explanation from a plausible-sounding narrative (§1). The stated reasoning: if an explanation is produced by asking a second system why a conclusion might have been reached, the result is a *rationalisation* — "fluent, convincing, and unconnected to what actually happened" — and it will remain fluent and convincing when the reasoning was wrong, which makes it worse than no explanation (§1).

The consequence the source draws is that **faithfulness is guaranteed by construction**: there is no separate model that could disagree with the reasoning, because there is no separate model (§1). Architecturally, this means the trace is not a debugging artefact produced on request but a primary output, produced always; the traceability invariant (`computational_primitives.md` §3.16) is what makes explanation possible at all, and it is the reason `knowledge_graph_spec.md` reifies every inference (§1).

### 2. The seven mandatory components (§2)

The source requires five components from the brief, plus two additions that it says fall out of Phase 3. All seven are mandatory.

| # | Component | Question answered |
|---|---|---|
| E1 | Rule chain | Which rules fired, in what order, with what bindings? |
| E2 | Evidence | What supported this, what opposed it, how was it weighted? |
| E3 | Exceptions | Which defeaters were checked? Which fired? Which did not? |
| E4 | Alternative conclusions | What else was live, and why did it lose? |
| E5 | Supporting texts | What sources, at what loci, in what editions? |
| E6 | Confidence decomposition | How confident, on which axis, limited by what? |
| E7 | Coverage | What was **not** evaluated? |

Two of these carry explicit argument in the source.

**E3 must include negative results (§2.1).** A statement that three cancellation conditions were checked and none applied is part of the explanation, not housekeeping. The source's claim is epistemic: "A conclusion reached after checking for defeaters differs epistemically from one reached without looking — even when the conclusion is identical."

**E7 is the component systems usually omit (§2.2).** A system that reports only what it did is "overstating its coverage by omission." Truncated defeater chains, incomplete exception corpora, and unavailable precedence principles must be reported. The source cites `canonical_shloka_analysis.md` §9.2 as the demonstration: the trace reports `incomplete_defeater_analysis` for the unevaluated *nīca-bhaṅga* conditions rather than presenting a clean result, and the source judges that "report is more valuable than the conclusion it qualifies" (§2.2).

### 3. The explanation schema: *pañcāvayava* (§3)

CHOIR adopts the Nyāya five-membered demonstration as its explanation template. The source describes it as "not an ornament" but a fully-formed schema that maps onto the execution record.

| Member | Content | Drawn from |
|---|---|---|
| ***pratijñā*** — thesis | The claim | `Inference.conclusion` |
| ***hetu*** — reason | Why, in this case | Matched `conditions` |
| ***udāharaṇa*** — general rule + example | The warrant, with its source | `Rule` + `Provenance` |
| ***upanaya*** — application | How the general rule applies here | `bindings` + derived facts |
| ***nigamana*** — conclusion | Therefore, with qualification | Conclusion + confidence + coverage |

The source gives four properties as its reason for adopting rather than inventing a format (§3.1): the schema separates the rule from its application (*udāharaṇa* states the general warrant, *upanaya* the instantiation), where most generated explanations blur the two and become uninspectable; it requires the warrant to be *exhibited* rather than merely relied upon, which forces source citation into the structure; it handles negative and defeated conclusions without modification, as `canonical_shloka_analysis.md` §10 shows in the same template for both cases; and it is the corpus's own explanatory form, so explanations of śāstric reasoning are legible to people trained in that tradition — described as "a genuine and rare fidelity property."

The source singles out the third property as the one hardest to retrofit: ad-hoc explanation formats "are almost always designed around successful firing and become awkward when the answer is 'nothing follows from this rule'" (§3.1).

On generality (§3.2), the source states the schema is not Jyotiṣa-specific, noting that legal reasoning already uses something close to it — issue, rule, application, conclusion — and clinical reasoning follows finding → guideline → applicability → recommendation, referring to `domain_independence.md` §5.

### 4. Trace structure and the replay guarantee (§4)

The trace is a DAG, not a list; explanations are *walks* over it at chosen depths (§4). The source's structure retains, as first-class nodes: unsatisfied conditions; derived facts pinned to a versioned kernel and its inputs; defeaters split into `fired`, `not fired` (with why not, marked E3) and `not evaluated` (with why not, marked E7); second-order influences that modulate rather than produce; evidence clusters with an independence key plus contradicting evidence (E2); conflict resolution recording both the principles applied and the principles unavailable with reasons (E4); a three-axis confidence tuple ⟨extraction, interpretive, inferential⟩ with a limiting factor (E6); and a coverage node (E7).

Every node carries back-pointers to source spans, "reaching all the way to character offsets in the attested text" (`shloka_compiler.md` §4), so that a user can go from a conclusion to the exact substring of the verse that licensed it (§4).

The replay guarantee is stated as:

> Given the same inputs, the same corpus version, the same kernel versions, and the same resolution policy, replaying a trace reproduces the identical conclusion.

The source calls this the traceability invariant made operational, and says it is what makes E1–E7 verifiable rather than merely asserted. It depends on the determinism constraints in `reasoning_ontology.md` §6.2 (kernels are pure) and the version pinning in `execution_pipeline.md` §7 (§4.1).

### 5. Alternatives and counterfactuals (§5)

The argument for E4 is that a conclusion reached where nothing else was live differs from one that narrowly beat a competitor, and "suppressing the competitor makes the first look like the second" (§5.1). For every live alternative the record carries the alternative itself, its support (rules and evidence), why it lost (defeated / preempted / lower confidence / out of context), and the margin.

Where an alternative was **not** defeated but merely unpreferred, the outcome is *vikalpa* (`conflict_resolution.md` §7.1) and both are presented; the explanation "must not narrate a forced choice as though it were a determination" (§5.1).

The rule graph also supports counterfactual explanation — what minimal change would flip this conclusion — computable by walking conditions and defeaters for minimal sets whose alteration changes the outcome (§5.2). The source's example is a defeated Chart B reading: the indication would have held had Jupiter not been debilitated, the positional condition having been satisfied because the 10th from the Moon is a kendra. The source claims this is often the most informative thing the system can say, "because it identifies the *load-bearing* fact rather than reciting all of them" (§5.2).

### 6. Audiences: four renderings, one trace (§6)

Because all renderings are projections, the source states they cannot disagree with each other or with the reasoning (§6).

| Audience | Depth | Emphasis | Omits |
|---|---|---|---|
| Practitioner | Shallow | Conclusion, main reason, confidence band, limiting factor | Full evidence graph; resolution internals |
| Scholar | Deep | Source loci, grammatical derivation, commentarial disputes, interpretive confidence | Kernel internals |
| Auditor | Complete | Every input, version pin, replay instructions | Nothing |
| Subject | Shallow, plain language | What was concluded, what it rests on, **what is uncertain** | Technical vocabulary |

Four rendering constraints are stated (§6.1): never render a conclusion without its confidence band and limiting factor (`confidence_framework.md` §6), since "moderate confidence — limited by an unverified citation" tells the reader what would change the answer and "moderate confidence" does not; never render a *vikalpa* as a single answer at any depth, and where the practitioner view cannot fit two alternatives it must show that there are two and link to them; never omit coverage gaps from any view, a truncated defeater chain appearing in the practitioner view too, in one sentence; and the scholar view must expose the grammatical derivation, because the kāraka analysis that fixed the reference frame is the answer to "why the Moon and not the Ascendant" (`canonical_shloka_analysis.md` §4.3).

### 7. Anti-patterns (§7)

| Anti-pattern | Why it is prohibited |
|---|---|
| Post-hoc generation | Produces plausible narratives disconnected from the reasoning; stays plausible when the reasoning is wrong |
| Selective tracing | Showing only supporting evidence; the omission is the distortion |
| Confidence without a limiting factor | Unactionable |
| Silent coverage gaps | Overstates completeness by omission |
| Collapsed *vikalpa* | Presents a genuine split as a determination |
| Untraceable derived facts | A kernel output with no version pin cannot be replayed |
| Explaining a conclusion the system did not reach | Any divergence between explanation and record is a defect, not a presentation choice |

The source names the first as the important one, "because it is what almost every contemporary system does, and because the output is *more* convincing than a faithful explanation would be" (§7).

### 8. Worked example (§8)

The worked example is drawn from `canonical_shloka_analysis.md` §9.2 — Chart B, where the rule fired and was undercut. The practitioner view states that Gajakesarī yoga is **not indicated**: Jupiter is in the 10th house from the Moon, which is a kendra, so the positional condition is met, but Jupiter is in Capricorn, its sign of debilitation, and debilitation withdraws the indication. It states explicitly that this is not a contrary indication — the rule contributes nothing here and other factors in the chart are unaffected. It closes with confidence "moderate — limited by an unverified citation for the source verse," and a coverage line stating that conditions which can annul debilitation were not evaluated because those rules have not been extracted, and that the conclusion is provisional. The source observes that every mandatory component is present in six sentences (§8).

The scholar expansion answers "why is the Moon the reference frame?" from the verse *candrāt kendragate jīve*: *candrāt* is the ablative singular of *candra*, and in the *a*-stem paradigm the ablative singular is formally distinct from the genitive singular (*candrasya*), so the case is unambiguous. The ablative marks the kāraka *apādāna* — the point from which something is reckoned — fixing the Moon as the reference frame rather than as the subject of the condition; the subject is *jīve* (Jupiter), in the locative, forming a locative absolute with *kendragate*. The construction carries conditional force with no conditional particle present, the reading depending on case morphology rather than any lexical marker. The expansion itself carries two qualifications: the source verse is not yet verified against a critical edition (`E-ATTEST`), and a metrical anomaly in the first pāda is flagged for review (`W-VARIANT`) (§8).

The source states that this is the property that most justifies the architecture, "because kāraka roles became hyperedge participant roles instead of being translated away" (§8).

### 9. Verification (§9)

The source holds that explainability is a testable property and gives eight tests.

| # | Test | Method | Fails if |
|---|---|---|---|
| X1 | Replay | Re-execute from the trace | Any divergence in the conclusion |
| X2 | Completeness | Check E1–E7 present on every conclusion | Any missing |
| X3 | Faithfulness | Diff the explanation against the record | Any claim not in the record |
| X4 | Source reachability | Follow every citation to a locus and span | Any dangling citation |
| X5 | Negative coverage | Confirm unfired defeaters are reported | Any silent omission |
| X6 | Counterfactual soundness | Apply the stated minimal change; re-run | The outcome does not flip |
| X7 | Cross-view consistency | Compare the four audience renderings | Any contradiction |
| X8 | Coverage honesty | Confirm every truncation is reported | Any silent truncation |

Two notes are attached. X3 is trivially satisfiable given §1 — a projection cannot contain what the record does not — and is retained as a regression test "precisely because the temptation to 'improve' an explanation with generated prose will recur." X6 is described as the strongest test of whether the rule graph is correct, because it checks the system's causal model of its own reasoning against its actual behaviour (§9).

### Caveats recorded by the source

- The source is marked "Draft for review" and is Phase 3 work; it fills `choir/research/R006_Traceability.md`, which the source records as "currently empty."
- The counterfactual and replay guarantees are stated as design commitments; the source does not report having executed X1–X8 against an implementation.
- Trace size is unresolved and may substantially exceed the conclusion (§10.1).
- The natural-language generation question is explicitly unproven, "and the failure mode is severe" (§10.4).
- The subject-facing problem for a domain lacking predictive validity is stated to be "a real design problem and it is not solved here" (§10.6).

## Architectural Implications

The following are implications the source itself draws.

- **The trace is a primary output, not a debugging artefact.** It is produced always, and the traceability invariant of `computational_primitives.md` §3.16 is what makes explanation possible at all; `knowledge_graph_spec.md` reifies every inference for this reason (§1).
- **No second model may sit between the record and the explanation.** Post-hoc generation is prohibited (§7), and X3 exists as a standing regression test against its reintroduction (§9).
- **Negative and unevaluated results must be materialised in the record**, not merely computed and discarded: unsatisfied conditions, unfired defeaters with reasons, unevaluated defeaters with reasons, and unavailable resolution principles with reasons are all retained nodes (§4).
- **Determinism and version pinning are load-bearing.** The replay guarantee depends on pure kernels (`reasoning_ontology.md` §6.2) and on version pinning in `execution_pipeline.md` §7 (§4.1); a kernel output with no version pin is an anti-pattern because it cannot be replayed (§7).
- **Provenance must reach character offsets** in the attested text (`shloka_compiler.md` §4), so that a conclusion resolves to the exact licensing substring (§4).
- **Grammatical structure must survive into the graph.** The scholar view's obligation to expose the kāraka analysis (§6.1) is satisfiable only because kāraka roles became hyperedge participant roles rather than being translated away (§8).
- **Confidence and coverage are rendering obligations, not options.** No view may show a conclusion without its confidence band and limiting factor, collapse a *vikalpa*, or omit a coverage gap (§6.1).
- **The schema is claimed to generalise beyond Jyotiṣa**, aligning with legal and clinical reasoning forms per `domain_independence.md` §5 (§3.2).

## Open Questions

The source records six (§10).

1. **Trace size (§10.1).** A full trace carrying every unfired defeater and every unsatisfied condition may substantially exceed the conclusion in size. Whether to materialise it always or reconstruct it on demand from a compact log is an engineering question with a correctness constraint: reconstruction must be provably equivalent.
2. **Explaining *absence* (§10.2).** "No evidence was found" requires the observability condition (`evidence_model.md` §3.3) rendered comprehensibly, and the source states there is no obvious plain-language form for "this absence is informative because the domain is complete."
3. **Explaining aggregation (§10.3).** Cluster-based correlation discounting (`evidence_model.md` §4.4) is correct but unintuitive; a reader shown five citations and told they count as one needs that explained without a lecture on independence.
4. **Natural-language generation (§10.4).** Templated text is faithful but stilted; generated text is fluent but reintroduces the §1 hazard. A constrained middle — generation restricted to surface realisation of record-derived content, with X3 enforced automatically — is described as "plausible but unproven, and the failure mode is severe."
5. **Explaining *vikalpa* without implying a preference (§10.5).** Presentation order alone suggests ranking; whether ordering can be made genuinely neutral is unresolved (`conflict_resolution.md` §11.2).
6. **Subject-facing explanation of a system whose domain lacks predictive validity (§10.6).** For Jyotiṣa, the subject view must convey that the system reports *what the tradition says*, not *what will happen*, without either editorialising or misleading. The source states: "This is a real design problem and it is not solved here."

Beyond these, the source's own header records that it is a "Draft for review" and that it fills `choir/research/R006_Traceability.md`, described as currently empty.

## Related Documents

Declared dependencies:

- [YK-R-004 — Vedic Reasoning Methodology](YK-R-004-vedic-reasoning-methodology.md)
- [YK-R-009 — Evidence Model](YK-R-009-evidence-model.md) — cited at §10.2 (§3.3, observability) and §10.3 (§4.4, cluster-based correlation discounting)
- [YK-R-010 — Conflict Resolution](YK-R-010-conflict-resolution.md) — cited at §5.1 (§7.1, *vikalpa*) and §10.5 (§11.2)
- [YK-R-011 — Confidence Framework](YK-R-011-confidence-framework.md) — cited at §6.1 (§6)

Declared downstream:

- [YK-R-015 — Execution Pipeline](YK-R-015-execution-pipeline.md) — also cited at §4.1 for version pinning (§7)

Also cited within the source:

- [YK-R-001 — Computational Primitive Specification](YK-R-001-computational-primitive-specification.md) — §1 (traceability invariant, §3.16)
- [YK-R-002 — Reasoning Ontology](YK-R-002-reasoning-ontology.md) — §4.1 (determinism constraints, §6.2)
- [YK-R-003 — Knowledge Graph Specification](YK-R-003-knowledge-graph-specification.md) — §1 (reification of every inference)
- [YK-R-006 — Shloka Compiler](YK-R-006-shloka-compiler.md) — §4 (character-offset provenance, §4)
- [YK-R-008 — Canonical Shloka Analysis (Benchmark)](YK-R-008-canonical-shloka-analysis-benchmark.md) — §2.2 (§9.2), §3.1 (§10), §6.1 (§4.3), §8 (§9.2)
- [YK-R-016 — Domain Independence](YK-R-016-domain-independence.md) — §3.2 (§5)
