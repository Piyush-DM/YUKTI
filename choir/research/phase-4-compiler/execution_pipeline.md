# 015 — Execution Pipeline

**Status:** Draft for review
**Phase:** 4 — Compiler Research
**Depends on:** `choir_intermediate_representation.md`, `reasoning_language.md`, Phase 3
**Feeds:** `domain_independence.md`

---

## 1. The pipeline

The brief specifies:

```
Input → Entity Detection → Rule Matching → Evidence → Conflict → Resolution → Explanation
```

Two stages must be inserted, both for correctness rather than convenience:

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

**S2** is required because almost no rule matches on raw input. "Jupiter in a kendra from the
Moon" requires computing house position from two raw positions. Without a distinct stage,
this computation gets buried inside matching, where it cannot be version-pinned, cached, or
traced.

**S4** is the architecturally significant one, and §4 explains why.

---

## 2. S1 — Entity detection and normalisation

**Input:** domain data — a chart, a case file, a patient record, a transaction set.

| Operation | Purpose |
|---|---|
| Entity recognition | Map input to ontology entities |
| Identity resolution | Same entity referred to twice → one node |
| Type assignment | Against L2 vocabulary |
| Attribute vs state separation | Definitional vs time-indexed (001 §3.2–3.3) |
| Temporal stamping | Valid time on every state |
| Completeness declaration | **Which domains are complete for absence-reasoning** |

The last row is the one usually forgotten. Absence-evidence is inadmissible without it
(`evidence_model.md` §3.3), so if S1 does not declare completeness, `ABSENT` conditions
cannot be evaluated at all. For a chart, positions are complete by construction; the yoga
corpus is not.

---

## 3. S2 — Derived-fact computation

Kernels (`reasoning_ontology.md` §6.2) compute facts that rules match on.

```
house_from(Guru, Candra) = 4       kernel: house_from v1
exalted(Guru, Karka)     = true    ontology lookup
combust(Guru)            = false   kernel: combustion v2 (orb parameter)
```

**Requirements:**

1. **Deterministic and pure.** No wall clock, no mutable external state. Required by the
   replay guarantee (`explainability_framework.md` §4.1).
2. **Version-pinned.** Every derived fact records the kernel version that produced it. A
   conclusion depending on an ephemeris must record *which* ephemeris.
3. **Computed in dependency order**, following the stratification (`reasoning_language.md`
   §7.3).
4. **Entered as ordinary facts** with provenance naming the kernel — not as a privileged
   fact class.

**Symbol resolution happens here, not at compile time.** Per
`shloka_compiler.md` §5.1: compile time fixes *which entity*; run time fixes *which
signification*. The query's `purpose` context selects the mapping, and the choice is
recorded so the explanation can state it.

---

## 4. S3–S4 — Matching and saturation

### 4.1 Matching

Rule conditions compiled to a discrimination network (RETE-family). The fit is good: many
rules, relatively slowly-changing facts, heavy condition sharing across rules — RETE's
design target. Sharing matters here because śāstric rules overlap heavily in their
conditions (dozens reference "in a kendra").

**Where RETE fits poorly**, and what is done instead:

| Issue | Handling |
|---|---|
| Contexts partition the fact base | Context as a discriminating node near the network root |
| `ANY n OF` is not a standard node | Dedicated threshold node; DNF expansion is rejected (`reasoning_language.md` §4.3) |
| Defeat is not a condition | **Not in the network** — S5, separately |
| Kernel-derived facts | Materialised in S2 before matching |

### 4.2 Saturation — the ordering commitment

> **Fire every applicable rule before adjudicating anything.**

Stated as a rule: **S4 completes before S5, S7 or S8 begins.**

**Why.** Precedence depends on the *full* set of fired rules. A rule may win by specificity
against one competitor and lose by source authority against another
(`conflict_resolution.md` §5). Neither judgement is available mid-match. A pipeline that
resolves during firing produces order-dependent results — the same inputs give different
answers depending on rule evaluation order, which destroys reproducibility.

**Cost.** Strictly more work than early filtering: rules fire that will later be defeated.

**Benefit.** Three things become possible that are otherwise not:

1. Deterministic results, independent of evaluation order.
2. The distinction between *not applicable* and *applied then defeated* — which have entirely
   different explanations (`canonical_shloka_analysis.md` §9.3).
3. Complete conflict detection, since all candidates are present simultaneously.

This is the pipeline's most consequential design decision and the one most likely to be
questioned on performance grounds. It should not be traded away.

---

## 5. S5 — Defeat evaluation

Structural, not graded (`evidence_model.md` §5.1).

```
for each fired inference, in decreasing stratum order:
    evaluate attached defeaters
    UNDERCUT fires  → withdraw the INFERENCE  (conclusion unasserted)
    REBUT   fires   → symmetric attack → S7
    DENY    fires   → remove premise support
    record: fired / not-fired / NOT EVALUATED
```

Three points that carry Phase 3 commitments into execution:

- **Undercutting withdraws; it does not negate.** Output is *no conclusion from this rule*,
  never the opposite conclusion.
- **Nothing is deleted.** Defeated inferences are marked and retained
  (`knowledge_graph_spec.md` I5).
- **`NOT EVALUATED` is recorded.** Truncated chains, unextracted exception rules, and
  unavailable defeaters are reported, not silently skipped
  (`explainability_framework.md` §2.2).

Strata guarantee termination (`conflict_resolution.md` §6); exceptions to exceptions resolve
naturally by processing in decreasing stratum order.

---

## 6. S6–S9 — Evidence, conflict, resolution, confidence

| Stage | Operation | Specified in |
|---|---|---|
| **S6** Evidence | Partition into independence clusters; reduce each cluster; aggregate with saturation | `evidence_model.md` §4.4 |
| **S7** Conflict | Detect over surviving inferences; **context-split first** | `conflict_resolution.md` §4 |
| **S8** Resolution | Apply precedence; record principles tried *and unavailable*; outcome may be *vikalpa* or escalation | `conflict_resolution.md` §5, §7 |
| **S9** Confidence | Three axes; summary is the **minimum**; name the limiting factor | `confidence_framework.md` §3 |

Two reminders that are easy to lose at implementation time:

- **S7 must attempt context splitting before reporting a conflict.** Most apparent conflicts
  are context collisions, and without the split the conflict queue becomes unusable.
- **S8 may terminate in a disjunction.** *Vikalpa* is a valid output, not a failure to
  resolve.

---

## 7. Determinism and reproducibility

> Same input + same corpus version + same kernel versions + same resolution policy →
> **byte-identical output**.

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

Requires: pure kernels (§3), saturation before adjudication (§4.2), and no wall-clock or
random dependence anywhere. `decision_time` is *recorded* input, never *read* from the clock
mid-execution.

This is what makes X1 (replay) in `explainability_framework.md` §9 testable, and it is the
property that lets an auditor ask "would we conclude this today?" and get a meaningful
answer by re-running under a current corpus version and diffing.

---

## 8. Incremental evaluation

Full re-execution on every corpus change does not scale. The `derives_from` closure —
maintained anyway for traceability — gives incrementality for free:

| Change | Invalidates |
|---|---|
| Input fact | Derived facts and inferences depending on it |
| Rule | Inferences from it; conflicts involving it |
| Exception added | Inferences it targets |
| Kernel version | Facts it produced; everything downstream |
| Authority ranking | **Every resolution that used P4** |
| Ambiguity re-resolution | Every rule compiled under it (`shloka_compiler.md` §7.1) |

The last two have large blast radii and are flagged as unresolved scale risks
(`conflict_resolution.md` §11.5).

Non-monotonicity means invalidation can *add* conclusions as well as remove them: retracting
a defeater restores what it withdrew.

---

## 9. Human-in-the-loop

Three entry points, all of which produce recorded, reusable artefacts rather than one-off
decisions:

| Point | Trigger | Recorded as |
|---|---|---|
| **Compile time** | Ambiguity diagnostics | Resolution cache entry (`shloka_compiler.md` §7.1) |
| **Extraction** | Dual-extraction disagreement | Adjudication with grounds |
| **Execution (S8)** | Escalated conflict | `Resolution` object with adjudicator and school |

Execution **blocks** on escalation for that conclusion but continues for independent ones. A
partial result with an explicit "one conclusion awaits adjudication" is correct; a complete
result obtained by guessing is not.

---

## 10. Worked trace

Chart B from `canonical_shloka_analysis.md` §9.2, stage by stage:

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

**Output:**

```
forms(Gajakesari): NOT INDICATED
  reason      : rule applied, then undercut by debilitation
  NOT         : ¬forms(Gajakesari)  — undercutting does not negate
  residue     : other chart evidence unaffected
  confidence  : moderate — limited by unverified citation
  coverage    : nīca-bhaṅga conditions not evaluated (rules not extracted)
                → this conclusion is PROVISIONAL
```

The two lines that most systems would omit — `NOT:` and `coverage:` — are the ones carrying
the most information.

---

## 11. Performance

| Stage | Cost driver | Mitigation |
|---|---|---|
| S2 | Kernel count × entities | Cache by (kernel, version, args) — pure, so safe |
| S3 | Rules × facts | RETE sharing; context discrimination at the root |
| S4 | **Saturation fires defeated rules** | Accepted cost; do not trade away |
| S5 | Defeaters × inferences | Defeater index (`knowledge_graph_spec.md` §5) |
| S6 | Independence partition | Union-find over independence keys |
| S7 | Pairwise over inferences | Context partition first — reduces the candidate set sharply |
| S10 | Trace materialisation | Open question (`explainability_framework.md` §10.1) |

S7's naive cost is quadratic in fired inferences. Context partitioning is what makes it
tractable, since conflicts can only occur within overlapping contexts — the same mechanism
that prevents the false-conflict flood also bounds the work.

---

## 12. Failure modes

The pipeline must degrade honestly, never silently.

| Failure | Correct behaviour |
|---|---|
| Kernel unavailable | Facts not derived; dependent rules **not evaluated** and reported as such |
| Rule has open ambiguities | Not executable; reported as excluded |
| Defeater chain truncated | Result marked provisional with the truncation stated |
| Escalation pending | That conclusion withheld; others returned |
| Completeness undeclared | `ABSENT` conditions **unevaluable**, not assumed false |
| Corpus version mismatch | Refuse to mix; do not silently reconcile |
| Incomparable contexts | Report separately; do not merge |

The unifying principle: **an unevaluated thing is never treated as a false thing.** The most
dangerous failure available to this system is quietly converting "we did not check" into
"it does not hold."

---

## 13. Open questions

1. **Saturation cost at corpus scale.** §4.2 is correct and expensive. With thousands of
   rules, firing everything before adjudicating may be prohibitive. Whether a
   *provably order-independent* pre-filter exists is the key optimisation question.
2. **Trace materialisation.** Always-on full traces may exceed conclusions in size;
   reconstruction from a compact log must be provably equivalent.
3. **Incremental invalidation blast radius.** §8's last two rows may be corpus-wide.
4. **Parallelism.** S2 and S4 are embarrassingly parallel; S5–S8 have ordering dependencies.
   How much of the pipeline parallelises without threatening determinism is unexamined.
5. **Query-directed evaluation.** The pipeline is forward-chaining and computes everything.
   For a specific question, backward chaining would be far cheaper — but saturation (§4.2)
   is what guarantees complete conflict detection, and a backward-chaining variant would
   need to preserve that property or explicitly report reduced coverage.
6. **Streaming inputs.** Everything here assumes a fixed input set. Domains where facts
   arrive over time (a case developing, a patient deteriorating) need re-execution semantics
   that are not specified.
