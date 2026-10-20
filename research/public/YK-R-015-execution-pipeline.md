# Execution Pipeline

| | |
|---|---|
| **Document ID** | YK-R-015 |
| **Source** | `choir/research/phase-4-compiler/execution_pipeline.md` (015) |
| **Series** | CHOIR Research Programme |
| **Revision** | A |
| **Status** | Active |
| **Last Updated** | 2026-08-23 |

## Abstract

This document specifies the ten-stage execution pipeline that runs compiled CHOIR rules against domain data, expanding the pipeline given in the brief by two inserted stages — derived-fact computation and saturation — both inserted "for correctness rather than convenience" (§1). Its central commitment is that every applicable rule fires before any adjudication begins (§4.2), which the document identifies as "the pipeline's most consequential design decision and the one most likely to be questioned on performance grounds" (§4.2). It further specifies the determinism contract and execution record (§7), incremental invalidation (§8), human-in-the-loop entry points (§9), performance cost drivers (§11), and a failure-mode table whose unifying principle is that "an unevaluated thing is never treated as a false thing" (§12).

The source document carries the status "Draft for review". This publication is **Active**: the source is a complete research document, drafted but **not accepted as specification**. Per `choir/research/README.md`, all 18 research deliverables in this programme are drafted and none accepted — "Every document is a hypothesis, per `MANIFESTO.md`." The manifesto's own formulation is narrower: "Treat every computational object as a hypothesis rather than an established truth."

## Research Question

The source does not state a research question under that heading. It opens (§1) from the brief's specified pipeline —

```
Input → Entity Detection → Rule Matching → Evidence → Conflict → Resolution → Explanation
```

— and sets out to determine what stages that pipeline actually requires, in what order, and which orderings are forced by correctness rather than chosen for convenience. The document's own framing is that "[t]wo stages must be inserted, both for correctness rather than convenience" (§1), and the remainder works out the consequences of those insertions for determinism, incrementality, performance, and failure behaviour.

## Finding

### The ten-stage pipeline

The document inserts two stages into the brief's pipeline, giving ten stages in all (§1):

```
Input
  ↓
S1  Entity detection & normalisation
  ↓
S2  Derived-fact computation              ← INSERTED: rules match on computed facts
  ↓
S3  Rule matching
  ↓
S4  Saturation (fire all applicable rules)  ← INSERTED: no adjudication yet
  ↓
S5  Defeat evaluation
  ↓
S6  Evidence accumulation
  ↓
S7  Conflict detection
  ↓
S8  Resolution
  ↓
S9  Confidence computation
  ↓
S10 Explanation generation
  ↓
Output
```

**S2** is required "because almost no rule matches on raw input" (§1). The example given is "Jupiter in a kendra from the Moon", which requires computing house position from two raw positions. Without a distinct stage, the document states, this computation "gets buried inside matching, where it cannot be version-pinned, cached, or traced" (§1).

**S4** is identified in §1 as "the architecturally significant one", with the argument deferred to §4.

### S1 — entity detection and normalisation

S1 takes domain data — "a chart, a case file, a patient record, a transaction set" (§2) — and performs entity recognition against the ontology, identity resolution (the same entity referred to twice becomes one node), type assignment against the L2 vocabulary, separation of attributes from states (definitional versus time-indexed, per 001 §3.2–3.3), temporal stamping of every state with valid time, and completeness declaration.

The document flags the last of these as "the one usually forgotten" (§2). Absence-evidence is inadmissible without it (`evidence_model.md` §3.3), so "if S1 does not declare completeness, `ABSENT` conditions cannot be evaluated at all" (§2). For a chart, positions are complete by construction; the yoga corpus is not.

### S2 — derived-fact computation

Kernels (`reasoning_ontology.md` §6.2) compute the facts that rules match on, for example (§3):

```
house_from(Guru, Candra) = 4       kernel: house_from v1
exalted(Guru, Karka)     = true    ontology lookup
combust(Guru)            = false   kernel: combustion v2 (orb parameter)
```

Four requirements are stated (§3): kernels must be **deterministic and pure** — no wall clock, no mutable external state — as required by the replay guarantee (`explainability_framework.md` §4.1); every derived fact must be **version-pinned**, so that "[a] conclusion depending on an ephemeris must record *which* ephemeris"; facts must be **computed in dependency order**, following the stratification (`reasoning_language.md` §7.3); and they must be **entered as ordinary facts** with provenance naming the kernel, "not as a privileged fact class".

The document places symbol resolution at run time, not compile time: per `shloka_compiler.md` §5.1, "compile time fixes *which entity*; run time fixes *which signification*" (§3). The query's `purpose` context selects the mapping, and the choice is recorded so the explanation can state it.

### S3–S4 — matching and saturation

Rule conditions are compiled to a discrimination network of the RETE family (§4.1). The document argues the fit is good — many rules, relatively slowly-changing facts, heavy condition sharing across rules — and notes that sharing matters "because śāstric rules overlap heavily in their conditions (dozens reference 'in a kendra')" (§4.1). It also records where RETE fits poorly and what is done instead:

| Issue | Handling |
|---|---|
| Contexts partition the fact base | Context as a discriminating node near the network root |
| `ANY n OF` is not a standard node | Dedicated threshold node; DNF expansion is rejected (`reasoning_language.md` §4.3) |
| Defeat is not a condition | **Not in the network** — S5, separately |
| Kernel-derived facts | Materialised in S2 before matching |

The saturation commitment is stated as: "**Fire every applicable rule before adjudicating anything.**" As a rule: "**S4 completes before S5, S7 or S8 begins.**" (§4.2)

The justification given is that precedence depends on the *full* set of fired rules: "A rule may win by specificity against one competitor and lose by source authority against another (`conflict_resolution.md` §5). Neither judgement is available mid-match." A pipeline that resolves during firing "produces order-dependent results — the same inputs give different answers depending on rule evaluation order, which destroys reproducibility" (§4.2).

The document states the cost plainly: saturation is "[s]trictly more work than early filtering: rules fire that will later be defeated" (§4.2). Against that it lists three benefits that are otherwise unobtainable — deterministic results independent of evaluation order; the distinction between *not applicable* and *applied then defeated*, "which have entirely different explanations" (`canonical_shloka_analysis.md` §9.3); and complete conflict detection, "since all candidates are present simultaneously" (§4.2). It closes: "This is the pipeline's most consequential design decision and the one most likely to be questioned on performance grounds. It should not be traded away."

### S5 — defeat evaluation

Defeat is structural, not graded (`evidence_model.md` §5.1). The procedure (§5):

```
for each fired inference, in decreasing stratum order:
    evaluate attached defeaters
    UNDERCUT fires  → withdraw the INFERENCE  (conclusion unasserted)
    REBUT   fires   → symmetric attack → S7
    DENY    fires   → remove premise support
    record: fired / not-fired / NOT EVALUATED
```

Three Phase 3 commitments are carried into execution here (§5). **Undercutting withdraws; it does not negate** — the output is "*no conclusion from this rule*, never the opposite conclusion". **Nothing is deleted** — defeated inferences are marked and retained (`knowledge_graph_spec.md` I5). **`NOT EVALUATED` is recorded** — truncated chains, unextracted exception rules, and unavailable defeaters "are reported, not silently skipped" (`explainability_framework.md` §2.2). Strata guarantee termination (`conflict_resolution.md` §6), and exceptions to exceptions resolve naturally by processing in decreasing stratum order.

### S6–S9 — evidence, conflict, resolution, confidence

| Stage | Operation | Specified in |
|---|---|---|
| **S6** Evidence | Partition into independence clusters; reduce each cluster; aggregate with saturation | `evidence_model.md` §4.4 |
| **S7** Conflict | Detect over surviving inferences; **context-split first** | `conflict_resolution.md` §4 |
| **S8** Resolution | Apply precedence; record principles tried *and unavailable*; outcome may be *vikalpa* or escalation | `conflict_resolution.md` §5, §7 |
| **S9** Confidence | Three axes; summary is the **minimum**; name the limiting factor | `confidence_framework.md` §3 |

Two points are called out as "easy to lose at implementation time" (§6): S7 must attempt context splitting before reporting a conflict, because "[m]ost apparent conflicts are context collisions, and without the split the conflict queue becomes unusable"; and S8 may terminate in a disjunction — "*Vikalpa* is a valid output, not a failure to resolve."

### Determinism and reproducibility

The contract (§7): "Same input + same corpus version + same kernel versions + same resolution policy → **byte-identical output**."

Everything that could vary is pinned into the execution record:

```
ExecutionRecord ::= {
  input_hash
  corpus_version, ontology_version
  kernel_versions   : [ { kernel, version } ]
  resolution_policy : PolicyVersion
  context           : ContextRef
  completeness_declarations : [ … ]
  decision_time     : Instant
  engine_version
}
```

This requires pure kernels (§3), saturation before adjudication (§4.2), and no wall-clock or random dependence anywhere; `decision_time` is "*recorded* input, never *read* from the clock mid-execution" (§7). The document states that this is what makes X1 (replay) in `explainability_framework.md` §9 testable, and "the property that lets an auditor ask 'would we conclude this today?' and get a meaningful answer by re-running under a current corpus version and diffing" (§7).

### Incremental evaluation

"Full re-execution on every corpus change does not scale" (§8). The `derives_from` closure, maintained anyway for traceability, "gives incrementality for free":

| Change | Invalidates |
|---|---|
| Input fact | Derived facts and inferences depending on it |
| Rule | Inferences from it; conflicts involving it |
| Exception added | Inferences it targets |
| Kernel version | Facts it produced; everything downstream |
| Authority ranking | **Every resolution that used P4** |
| Ambiguity re-resolution | Every rule compiled under it (`shloka_compiler.md` §7.1) |

The last two rows "have large blast radii and are flagged as unresolved scale risks" (`conflict_resolution.md` §11.5) (§8). The document also notes that non-monotonicity means invalidation can *add* conclusions as well as remove them: "retracting a defeater restores what it withdrew" (§8).

### Human-in-the-loop

Three entry points, "all of which produce recorded, reusable artefacts rather than one-off decisions" (§9):

| Point | Trigger | Recorded as |
|---|---|---|
| **Compile time** | Ambiguity diagnostics | Resolution cache entry (`shloka_compiler.md` §7.1) |
| **Extraction** | Dual-extraction disagreement | Adjudication with grounds |
| **Execution (S8)** | Escalated conflict | `Resolution` object with adjudicator and school |

Execution **blocks** on escalation for that conclusion but continues for independent ones: "A partial result with an explicit 'one conclusion awaits adjudication' is correct; a complete result obtained by guessing is not." (§9)

### Worked trace

§10 traces Chart B from `canonical_shloka_analysis.md` §9.2 stage by stage:

| Stage | Action |
|---|---|
| S1 | Entities: Guru, Candra, Sūrya, rāśis. Completeness declared: **positions** ✓, **yoga corpus** ✗ |
| S2 | `house_from(Guru, Candra) = 10` (kernel v1, pinned); `debilitated(Guru) = true` (ontology) |
| S3 | `gajakesari_formation` matches — `10 ∈ kendra` ✓ |
| S4 | **Rule fires.** No adjudication yet. Inference created |
| S5 | `ex_debilitated` **UNDERCUT fires** → inference withdrawn. `ex_combust` not fired. `ex_afflicted` not fired. **`nīca_bhaṅga` NOT EVALUATED — rules not extracted** |
| S6 | No surviving support for `forms(Gajakesari)` from this rule. Other evidence untouched |
| S7 | No conflict — undercutting is not a conflict; it is defeat |
| S8 | No resolution required |
| S9 | Confidence for the *negative* result: limited by (a) unverified citation, (b) undeclared completeness of the cancellation corpus |
| S10 | *Pañcāvayava* explanation including the coverage gap |

The output:

```
forms(Gajakesari): NOT INDICATED
  reason      : rule applied, then undercut by debilitation
  NOT         : ¬forms(Gajakesari)  — undercutting does not negate
  residue     : other chart evidence unaffected
  confidence  : moderate — limited by unverified citation
  coverage    : nīca-bhaṅga conditions not evaluated (rules not extracted)
                → this conclusion is PROVISIONAL
```

The document's comment on this output: "The two lines that most systems would omit — `NOT:` and `coverage:` — are the ones carrying the most information." (§10)

### Performance

| Stage | Cost driver | Mitigation |
|---|---|---|
| S2 | Kernel count × entities | Cache by (kernel, version, args) — pure, so safe |
| S3 | Rules × facts | RETE sharing; context discrimination at the root |
| S4 | **Saturation fires defeated rules** | Accepted cost; do not trade away |
| S5 | Defeaters × inferences | Defeater index (`knowledge_graph_spec.md` §5) |
| S6 | Independence partition | Union-find over independence keys |
| S7 | Pairwise over inferences | Context partition first — reduces the candidate set sharply |
| S10 | Trace materialisation | Open question (`explainability_framework.md` §10.1) |

S7's naive cost is quadratic in fired inferences; context partitioning is what makes it tractable, "since conflicts can only occur within overlapping contexts — the same mechanism that prevents the false-conflict flood also bounds the work" (§11). S10's mitigation is recorded not as a solution but as an open question.

### Failure modes

"The pipeline must degrade honestly, never silently." (§12)

| Failure | Correct behaviour |
|---|---|
| Kernel unavailable | Facts not derived; dependent rules **not evaluated** and reported as such |
| Rule has open ambiguities | Not executable; reported as excluded |
| Defeater chain truncated | Result marked provisional with the truncation stated |
| Escalation pending | That conclusion withheld; others returned |
| Completeness undeclared | `ABSENT` conditions **unevaluable**, not assumed false |
| Corpus version mismatch | Refuse to mix; do not silently reconcile |
| Incomparable contexts | Report separately; do not merge |

The unifying principle: "**an unevaluated thing is never treated as a false thing.** The most dangerous failure available to this system is quietly converting 'we did not check' into 'it does not hold.'" (§12)

## Architectural Implications

**Saturation before adjudication is a hard ordering constraint on any CHOIR execution engine.** Because "S4 completes before S5, S7 or S8 begins" (§4.2), no implementation may filter or resolve during rule firing. The document treats this as non-negotiable — "It should not be traded away" (§4.2) — and makes the accepted extra work explicit in the performance table (§11), where the mitigation column for S4 reads "Accepted cost; do not trade away."

**Kernel purity and version pinning become engine-level requirements, not kernel-author conventions.** The byte-identical-output contract (§7) is stated to require pure kernels (§3), saturation before adjudication (§4.2), and no wall-clock or random dependence anywhere. This constrains the `ExecutionRecord` shape given in §7 and makes replay (X1 in `explainability_framework.md` §9) testable.

**Completeness declaration is load-bearing at intake, not at reasoning time.** Since `ABSENT` conditions "cannot be evaluated at all" without an S1 declaration (§2), any intake path that omits the declaration removes absence-reasoning from the system's reach for that domain. The source requires the omission to be visible rather than silent: §12 lists undeclared completeness as a failure mode whose correct behaviour is that `ABSENT` conditions are "**unevaluable**, not assumed false", under the stated principle that "[t]he pipeline must degrade honestly, never silently" (§12).

**Defeat must live outside the discrimination network.** §4.1 records that defeat is "**Not in the network** — S5, separately", which fixes the boundary between matching and adjudication in the engine's structure rather than leaving it to implementation preference.

**Traceability infrastructure doubles as the incrementality mechanism.** The `derives_from` closure is "maintained anyway for traceability" and "gives incrementality for free" (§8) — so the cost of the explainability commitment is partly repaid in execution economics. The same section, however, records two invalidation rows with large blast radii as unresolved scale risks.

**Escalation is a first-class execution outcome, not an error path.** Because execution blocks per-conclusion and continues for independent ones (§9), and because *vikalpa* is "a valid output, not a failure to resolve" (§6), the engine's result type must admit partial, disjunctive, and awaiting-adjudication outcomes.

This document depends on `choir_intermediate_representation.md`, `reasoning_language.md`, and Phase 3, and feeds `domain_independence.md` (source header).

## Open Questions

The source records six open questions (§13), reproduced here with its own framing:

1. **Saturation cost at corpus scale.** "§4.2 is correct and expensive. With thousands of rules, firing everything before adjudicating may be prohibitive. Whether a *provably order-independent* pre-filter exists is the key optimisation question."
2. **Trace materialisation.** "Always-on full traces may exceed conclusions in size; reconstruction from a compact log must be provably equivalent." (Also flagged as the open-question mitigation for S10 in §11, referencing `explainability_framework.md` §10.1.)
3. **Incremental invalidation blast radius.** "§8's last two rows may be corpus-wide" — the authority-ranking and ambiguity-re-resolution rows, flagged as unresolved scale risks against `conflict_resolution.md` §11.5.
4. **Parallelism.** "S2 and S4 are embarrassingly parallel; S5–S8 have ordering dependencies. How much of the pipeline parallelises without threatening determinism is unexamined."
5. **Query-directed evaluation.** "The pipeline is forward-chaining and computes everything. For a specific question, backward chaining would be far cheaper — but saturation (§4.2) is what guarantees complete conflict detection, and a backward-chaining variant would need to preserve that property or explicitly report reduced coverage."
6. **Streaming inputs.** "Everything here assumes a fixed input set. Domains where facts arrive over time (a case developing, a patient deteriorating) need re-execution semantics that are not specified."

Two further gaps are recorded in the body rather than in §13. The worked trace in §10 terminates with `nīca_bhaṅga` marked **NOT EVALUATED — rules not extracted**, and its output is labelled PROVISIONAL on that ground, with confidence limited by an unverified citation and the undeclared completeness of the cancellation corpus (§10). No performance figures, benchmarks, or measured costs appear anywhere in the source; §11 states cost drivers and mitigations only.

## Related Documents

Depends on:

- [YK-R-013 — CHOIR Intermediate Representation](YK-R-013-choir-intermediate-representation.md)
- [YK-R-014 — Reasoning Language (CRL)](YK-R-014-reasoning-language-crl.md) — §4.3 (`ANY n OF` / DNF expansion rejected), §7.3 (stratification)
- [YK-R-009 — Evidence Model](YK-R-009-evidence-model.md) — §3.3 (absence-evidence admissibility), §4.4 (independence clusters), §5.1 (structural defeat)
- [YK-R-010 — Conflict Resolution](YK-R-010-conflict-resolution.md) — §4, §5, §6, §7, §11.5
- [YK-R-011 — Confidence Framework](YK-R-011-confidence-framework.md) — §3
- [YK-R-012 — Explainability Framework](YK-R-012-explainability-framework.md) — §2.2, §4.1, §9 (X1 replay), §10.1

Cites:

- [YK-R-001 — Computational Primitive Specification](YK-R-001-computational-primitive-specification.md) — §3.2–3.3 (attribute vs state)
- [YK-R-002 — Reasoning Ontology](YK-R-002-reasoning-ontology.md) — §6.2 (kernels)
- [YK-R-003 — Knowledge Graph Specification](YK-R-003-knowledge-graph-specification.md) — I5 (retention of defeated inferences), §5 (defeater index)
- [YK-R-006 — Shloka Compiler](YK-R-006-shloka-compiler.md) — §5.1 (compile-time vs run-time resolution), §7.1 (resolution cache)
- [YK-R-008 — Canonical Shloka Analysis (Benchmark)](YK-R-008-canonical-shloka-analysis-benchmark.md) — §9.2 (Chart B), §9.3

Feeds:

- [YK-R-016 — Domain Independence](YK-R-016-domain-independence.md)
