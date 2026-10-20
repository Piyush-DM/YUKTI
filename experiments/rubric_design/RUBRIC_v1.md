# RUBRIC_v1 — operational specification (experiment)

**Status: draft, first pass. Not yet tested against outputs.** Built from
`CANDIDATE_SET_v1.md` (frozen 2026-09-14). This is step 4 of the stated
pipeline:

```
candidate selection → operational dimensions → observable evidence
→ scoring rules → reproduction/testing → eventual canonicalization
        (done)          (this document)              (§7, next)      (not yet)
```

It lives under `experiments/rubric_design/` for the same reason
`CANDIDATE_SET_v1.md` does — provisional, versioned, not yet promoted to
`docs/architecture/`.

**What this rubric scores.** Every dimension below is written against a
*specific output* — one judgment, one response, one decision — not against a
system's architecture in the abstract. `CANDIDATE_SET_v1.md` asked "does
YUKTI have a mechanism for X." This document asks "does *this judgment*
exhibit X, observably, mechanically." That shift is deliberate: a rubric that
can only be applied to a system's design, never to one of its outputs, cannot
be tested, and an untestable rubric is exactly what the meta-rubric sieve
exists to catch.

---

## 1. Scoring vocabulary

Three tiers, reused from `experiments/rubric_reproduction/compare.py`'s own
`MATCH` / `PARTIAL` / `DIVERGENCE` vocabulary rather than inventing a
competing one — this project already has one tested, working tiering scheme,
and a rubric that can't agree with its own codebase's precedent on what
"partial" means is not reproducible.

| Tier | Meaning |
|---|---|
| **PASS** | The observable evidence positively demonstrates the criterion. |
| **PARTIAL** | The criterion is not violated, but the evidence is incomplete, unverifiable, or holds only in a weakened form named explicitly per-dimension below. |
| **FAIL** | The observable evidence demonstrates the criterion does not hold, or no evidence exists to check it. |

No dimension is scored by a rater's holistic impression. Every PASS/PARTIAL/
FAIL boundary below is defined as a mechanical check against the record —
find the field, apply the rule, read the answer. Where a check genuinely
requires semantic judgment (Evidence Fitness's relevance test, mainly), that
is flagged explicitly rather than pretended away.

---

## 2. Operational dimensions

The seven validity-weighted dimensions from `CANDIDATE_SET_v1.md` (§3, items
1, 2, 3, 5, 8, 9, 10). Reproducibility (item 7) is handled separately in §3 —
it is a gate, not a graded dimension, per that record's own framing.

For each: what capability it actually tests, what kind of failure it's a
detector for, what distinguishes genuinely-good from superficially-plausible,
and what it measures (reasoning / knowledge-grounding / instruction-following
/ calibration / process — classified honestly, not defaulted to "reasoning").

### D1 — Decision Framing & Scope

- **Capability tested:** whether an explicit decision statement and scope
  existed *before* evidence was applied, as opposed to one reconstructed
  after the fact to match whatever conclusion was reached.
- **Failure mode exposed:** scope creep — the question silently changes
  between framing and conclusion (e.g. asked to evaluate a $12M allocation,
  the output evaluates a different facility size without saying so).
- **Genuine vs. superficial:** superficially-plausible output states a
  decision *somewhere*; genuinely-good output states it **before** the
  evidence section and never contradicts it.
- **Measures:** process discipline / instruction-following. Not reasoning
  quality — this is a compliance check on whether a step happened, not a
  judgment of content.
- **Criterion:** the judgment's material carries an explicit, unchanged
  decision statement and scope.
- **Observable evidence:** `Case.requested_decision` (or equivalent) is set
  prior to `record_material`/analysis, and the synthesis's recommendation
  addresses that exact decision, not a substituted one.
- **Failure condition:** no recoverable decision statement; or the
  recommendation answers a different question than the one framed.
- **Scoring boundary:** PASS = statement present, prior, and unchanged.
  PARTIAL = statement present but recoverable only by inference from the
  conclusion (framing was implicit, not stated). FAIL = no statement
  recoverable, or the conclusion visibly answers something else.

### D2 — Evidence Provenance & Integrity

- **Capability tested:** every cited figure traces to a literal, locatable
  span in the supplied material.
- **Failure mode exposed:** fabricated or misattributed evidence — a figure
  that looks sourced but isn't.
- **Genuine vs. superficial:** superficially-plausible output cites a source
  label that *sounds* right; genuinely-good output's quote is a literal
  substring of the actual text, checkable without trusting the claim.
- **Measures:** knowledge-grounding / faithfulness. Is the output anchored to
  the given material, not to the model's own memory — a different capability
  from whether the anchored claim is itself sound (that's D5).
- **Criterion:** every cited figure resolves to a real span and a registered
  source.
- **Observable evidence:** exactly the guard already implemented in
  `assistant.py::propose` — `text.find(quote) != -1` for every cited quote,
  and `source_label` resolves to a registered `Source`.
- **Failure condition:** any figure driving the stated recommendation whose
  quote does not resolve, or whose source is unregistered/invented.
- **Scoring boundary:** PASS = 100% of cited figures resolve. PARTIAL =
  a non-decisive figure fails to resolve (recommendation unaffected if it's
  dropped). FAIL = a figure that determines the stated recommendation fails
  to resolve.

### D3 — Evidence Fitness (relevance, reliability, sufficiency)

- **Capability tested:** cited evidence is not just real (D2) but actually
  responsive to the claim it's attached to, and present in enough
  independent quantity for the stakes involved.
- **Failure mode exposed:** correctly-sourced but off-topic or
  single-sourced-where-corroboration-matters evidence driving a conclusion.
- **Genuine vs. superficial:** superficially-plausible output cites *a*
  source for every claim; genuinely-good output's sources actually bear on
  the specific claim, and claims the domain would expect corroboration for
  (e.g. a contested figure) aren't resting on one document repeated as if it
  were two.
- **Measures:** reasoning (relevance is a semantic-fit judgment, not a
  mechanical lookup) combined with a mechanical sufficiency count. This is
  the one dimension in this rubric that cannot be fully automated — flagged
  here rather than pretending a keyword match settles relevance.
- **Criterion:** cited evidence is on-topic for its claim and sufficiently
  corroborated for the claim's materiality.
- **Observable evidence:** reliability — `Source.kind` → evidence-quality
  rank (already implemented, `_KIND_TO_QUALITY` in `translator.py`).
  Relevance — does the source's content actually address the metric it's
  cited for (requires review, not a regex). Sufficiency — for a claim the
  domain treats as needing corroboration, are ≥2 *independent* sources cited
  (not the same document under two labels).
- **Failure condition:** a claim's cited source doesn't address the claim;
  or a claim expected to need corroboration rests on one source.
- **Scoring boundary:** PASS = on-topic and, where expected, corroborated.
  PARTIAL = on-topic but single-sourced where corroboration would normally
  be expected. FAIL = the cited evidence is not actually responsive to the
  claim.

### D5 — Inference Soundness / Warrant

- **Capability tested:** the stated conclusion actually follows from the
  stated evidence under the stated rule, when the rule is independently
  re-applied.
- **Failure mode exposed:** valid citations, invalid inferential leap — the
  classic warrant failure. A correct-looking derivation that doesn't
  actually derive.
- **Genuine vs. superficial:** superficially-plausible output narrates a
  derivation that *sounds* rule-governed; genuinely-good output's narrated
  rule, re-applied mechanically to the same cited numbers, reproduces the
  same result.
- **Measures:** reasoning, directly — the most classically "reasoning" of
  every dimension here.
- **Criterion:** independently re-deriving the stated rule over the stated
  evidence reproduces the stated recommendation.
- **Observable evidence:** this is precisely what
  `experiments/rubric_reproduction/compare.py` already does for YUKTI's own
  engine — `fired_rule`, `recommendation`, and the per-kernel
  `kernel_derivation_outcome`/`kernel_derivation_steps` fields, tier-1 and
  hard-tier-2 in that module's own vocabulary.
- **Failure condition:** re-derivation yields a different recommendation
  (hard failure) or a different fired rule at the same recommendation
  (softer failure — the stated *reason* is wrong even though the answer
  isn't).
- **Scoring boundary:** PASS = re-derivation matches exactly (recommendation
  and fired rule). PARTIAL = recommendation matches, fired rule/derivation
  steps differ. FAIL = re-derivation produces a different recommendation.
- **Note:** of every dimension in this rubric, this is the only one with an
  existing, tested, working implementation — `compare.py` already scores
  D5 for the gemini-2.5-flash run (`FINDINGS.md`, 2026-09-11: D5-equivalent
  fields matched 10/10, zero X4 violations).

### D8 — Independent Challenge & Review

- **Capability tested:** whether this specific output was subjected to
  critique by an agent that did not produce it, with the critique's outcome
  recorded.
- **Failure mode exposed:** automation bias / rubber-stamping — errors an
  outside perspective would catch, uncaught because no outside perspective
  was applied.
- **Genuine vs. superficial:** a review artifact that says "reviewed: OK" is
  indistinguishable from one that never happened; a genuine review artifact
  names at least one thing it checked and what it would have flagged.
- **Measures:** process, not the output's own content — this dimension can
  be PASS even for a flawed judgment (the flaw just needs to have been
  caught and disposed of) and FAIL even for a correct one (no one checked).
- **Criterion:** a distinct reviewer examined this specific output and its
  findings, if any, were disposed of on the record.
- **Observable evidence:** a review artifact tied to this `judgment_id`,
  authored by an identity distinct from whoever produced the judgment,
  containing ≥1 substantive check (not a bare approval) and, if a finding
  was raised, its disposition (accepted / overridden-with-reason).
- **Failure condition:** no review artifact exists for this output.
- **Scoring boundary:** PASS = distinct reviewer, ≥1 substantive finding,
  disposition recorded. PARTIAL = review occurred, zero findings recorded
  (cannot distinguish "genuinely clean" from "rubber-stamped" from the
  artifact alone — deliberately not PASS). FAIL = no independent review
  exists.
- **Where YUKTI stands today:** FAIL, for every output the system has ever
  produced. `DECISION-008` governs the model-proposes/human-confirms intake
  path, and that path is single-pass confirmation, not independent
  challenge — this was named explicitly in the architecture critique this
  rubric traces back to.

### D9 — Decision Criteria & Thresholds

- **Capability tested:** the specific numeric or qualitative cutoff that
  was decisive for this output's recommendation has a documented rationale,
  not just a value.
- **Failure mode exposed:** an arbitrary threshold presented as if it were
  self-evidently correct, or an aggregation rule that lets a strong area's
  score mask a weak one.
- **Genuine vs. superficial:** a threshold that is merely *consistent*
  (same value every time) is not the same as one that is *justified*
  (someone can say why that value and not another).
- **Measures:** documentation/governance, with one reasoning-adjacent
  sub-check — does the aggregation rule actually avoid masking (i.e. is it
  min-based/weakest-wins rather than an average that could hide a failing
  area).
- **Criterion:** the decisive threshold(s) for this output have a traceable
  rationale, and the aggregation does not average away a weak area.
- **Observable evidence:** for the rule that fired (from D5), is its
  threshold constant (e.g. `DOMINANCE_MARGIN = 3`) attached to a documented
  "why this value" note anywhere in the codebase or its research record; and
  does `institutional confidence = min(area bands)` hold rather than a mean.
- **Failure condition:** the decisive threshold is undocumented and
  undiscoverable; or the aggregation is average-based and a weak area's
  score was masked.
- **Scoring boundary:** PASS = threshold has a documented rationale and
  aggregation is weakest-wins. PARTIAL = threshold is consistent and
  auditable (drift-tested, as `rubric.md`'s own constants block is) but its
  *rationale* is undocumented. FAIL = inconsistent, undiscoverable, or
  masking.
- **Where YUKTI stands today:** PARTIAL, honestly. The kernel thresholds are
  consistent and drift-tested (`rubric.md` §H, checked against live source),
  and the aggregation is correctly weakest-wins — but *why*
  `top_customer_revenue_pct > 35%` and not 30% or 40% is not documented
  anywhere as a policy rationale, only as a literal transcription of
  existing code. This is the same gap named as "the kernels may be proving
  the wrong thing" in `context_yukti.md` §8.

### D10 — Auditability & Reconstruction

- **Capability tested:** a third party, given only the persisted record —
  no live access to whoever produced it — can reconstruct the full decision.
- **Failure mode exposed:** a log that exists but can't actually be replayed
  because some intermediate step was never stored.
- **Genuine vs. superficial:** a record that reproduces the *what* (the
  recommendation) but not the *why* (which evidence, which rule, in what
  order) looks complete and isn't.
- **Measures:** engineering completeness — similar in kind to Reproducibility
  (§3) but about *stored* completeness rather than *re-run* consistency.
  They are correlated but independently failable: a system can store
  everything needed to reconstruct a past run without being able to re-run
  it live (external dependency changed), or be perfectly re-runnable while
  storing nothing (no audit trail if the source material moves on).
- **Criterion:** the persisted record alone is sufficient to answer "what
  was decided and why," with nothing supplied from outside it.
- **Observable evidence:** a cold-audit test — hand only
  `05-record.json` + the material snapshot to a fresh reader and check that
  recommendation, rationale, evidence trail, and cited ids are all present
  and resolve within the record.
- **Failure condition:** any step in the chain is unrecoverable from the
  stored record alone.
- **Scoring boundary:** PASS = fully reconstructable from stored artifacts.
  PARTIAL = the *what* is recoverable but one *why* step is not (e.g. a
  figure's original source quote wasn't retained). FAIL = the recommendation
  itself can't be reproduced from the stored record.
- **Where YUKTI stands today:** the strongest dimension in the whole set —
  `verify_ledger`'s dual-digest check (`material_digest` + `record_digest`)
  is close to a PASS by construction for anything that went through
  `record_material` → `request_judgment`.

---

## 3. Foundational control: Reproducibility (not graded)

Per `CANDIDATE_SET_v1.md` §4: tested and enforced, but not weighted as a
validity dimension alongside D1–D10. Binary, not tiered — a system is either
reproducible on a given input or it isn't; there is no meaningful "partial"
reproducibility.

- **Criterion:** N independent replays of the identical input produce a
  byte-identical output.
- **Observable evidence:** already implemented twice in this repo —
  `experiments/messy_intake/evidence.py::EvidenceRecord.replay_is_stable`
  (engine-side, N=8–10 replays, `record_digest` comparison) and
  `applications/investment/workspace/cases.py`'s judgment supersession
  logic, which keys on material digest for the same reason.
- **Failure condition:** any variance in `record_digest` or the reported
  verdict across replays of one frozen input.
- **Scoring boundary:** PASS / FAIL only.
- **What a PASS does and doesn't mean, stated because it's the whole reason
  this is a gate and not a peer dimension:** PASS means the process is
  consistent. It does not mean the process is correct. This is not
  theoretical — `experiments/rubric_reproduction/FINDINGS.md` (2026-09-11)
  measured exactly this: reasoning variance 0 across replays, while the
  underlying rubric's correctness remained, and remains, an open question.
  A dimension that can be satisfied by a system that is confidently and
  consistently wrong cannot be treated as evidence the system is right.
  This gate exists to catch drift, tampering, and implementation bugs —
  nothing more, nothing less — and D5/D8/D9 exist precisely because this
  gate cannot do their job too.

---

## 4. Provisional dimensions — #4 and #6, worked forward

`CANDIDATE_SET_v1.md` refused to force these into the clean set. Per its own
§5 next steps, they're reworked here against what YUKTI actually is (fixed
kernels, ordinal bands) rather than what a general-purpose reasoning system
might be. Both are marked **PROVISIONAL** — included because the rework
produced something that looks testable, not because they've cleared step 7
yet. If §7's testing shows either doesn't discriminate, it comes back out.

### D4′ — Kernel/Area Independence *(reworked from "Hypotheses & Alternatives Management")*

The original candidate's test — count the hypotheses generated — assumes
open-ended generation. YUKTI's four review areas are fixed, not generated.
The failure mode the original candidate is actually trying to catch,
restated for a fixed-decomposition architecture: **is the decomposition into
separate areas doing real work, or is it decorative** — four kernels that
always agree are one kernel wearing four labels, and confirmation bias at
the *architecture* level looks exactly like that.

- **Capability tested:** independent review areas produce genuinely
  independent signal — they can and do disagree when the evidence actually
  conflicts, rather than always converging regardless of input.
- **Failure mode exposed:** a decomposition that never diverges, meaning
  disagreement/`CONTESTED` exists in the rule set but never fires in
  practice — the architecture's independence claim is nominal.
- **Genuine vs. superficial:** superficially-independent kernels are four
  code paths that happen to be organized separately; genuinely-independent
  kernels demonstrably reach opposite conclusions given evidence engineered
  to conflict, and don't when it doesn't.
- **Measures:** reasoning (does the synthesis correctly detect and preserve
  a real disagreement) combined with an empirical, corpus-level property —
  this can't be checked on one output; it needs a set of outputs with known
  ground truth about whether they *should* produce disagreement.
- **Criterion:** across a benchmark corpus including cases engineered to
  contain genuinely conflicting evidence, disagreement/CONTESTED fires on
  those cases and areas are not perfectly correlated across the corpus.
- **Observable evidence:** rate of `disagreements`/CONTESTED outcomes on a
  corpus that includes both agreement-expected and conflict-expected cases;
  pairwise correlation of kernel stance across the corpus.
- **Failure condition:** CONTESTED never fires even on cases deliberately
  engineered to produce it, or two kernels are empirically perfectly
  correlated.
- **Scoring boundary:** PASS = disagreement fires reliably on
  conflict-engineered cases and kernels are not perfectly correlated.
  PARTIAL = disagreement fires only on extreme/engineered cases, not on
  organically conflicting real material. FAIL = disagreement never fires.
- **Existing data point (not yet a corpus):** `experiments/messy_intake`'s
  `5-contested` scenario was deliberately engineered to produce exactly this
  and does — `Contested / Moderate`, one disagreement on `revenue_quality`,
  reproduced by both the keyword and model readers. One case is not a rate.
  This is the natural seed for the §7 test corpus, not a completed test.

### D6′ — Ordinal Uncertainty Fidelity *(reworked from "Uncertainty Management")*

The original candidate assumes probabilistic output (ranges, confidence
intervals). CHOIR's confidence is ordinal — HIGH/MODERATE/LOW/INSUFFICIENT,
weakest-area-wins. Importing probabilistic machinery to satisfy this
candidate would be architecture creep disguised as a rubric requirement,
exactly what `CANDIDATE_SET_v1.md` §4 warned against. Reworked to the intent
behind the candidate — no false precision, no hidden uncertainty — using
only the vocabulary CHOIR already has.

- **Capability tested:** three things, not one, and they were conflated in
  the original candidate: (a) the reported confidence band never overstates
  what the weakest cited evidence would justify; (b) "evidence present but
  weak" is reported distinctly from "evidence absent," never collapsed into
  one undifferentiated low-confidence signal; (c) every band carries a
  specific, named limiting factor, not a bare label.
- **Failure mode exposed:** false precision (a model or process stating more
  confidence than its weakest input supports) and silent uncertainty (a
  "low confidence" that doesn't say *why*, or that doesn't distinguish
  "we have weak data" from "we have no data").
- **Genuine vs. superficial:** a band with a generic limiting factor
  ("insufficient data") is superficial; one that names the specific weak
  area and the specific weak source is genuine — exactly the distinction
  `explain.py`'s existing `_confidence`/`_gaps` handlers already draw.
- **Measures:** calibration — is the stated confidence level actually
  tracking the true strength of the underlying evidence, not a reasoning or
  knowledge property.
- **Criterion:** (a), (b), and (c) above all hold for this output.
- **Observable evidence:** (a) compare stated overall band against the
  evidence-quality rank of the weakest cited source — flag if the stated
  band exceeds what that rank would justify; (b) check whether "no evidence
  for metric X" (INSUFFICIENT / on `outstanding_schedule_items`) and "weak
  evidence for metric X" (LOW, cited) are ever reported identically; (c)
  every band has a non-generic `limiting_factor` string naming a specific
  area or source.
- **Failure condition:** (a) failing — an overstated band — is the serious
  failure and gates straight to FAIL regardless of (b)/(c), because it's the
  one that actively misleads rather than merely under-informs.
- **Scoring boundary:** PASS = all three hold. PARTIAL = (a) and (c) hold,
  (b) is blurred (absent and weak evidence reported the same way). FAIL =
  (a) fails.
- **Structural note:** (a) is close to a guaranteed PASS for YUKTI's own
  engine by construction — `institutional confidence = min(area bands)`
  cannot mathematically exceed the weakest area. It is a genuinely
  discriminating test for an *external* model's output, where nothing
  enforces it. This connects directly to the gemini-2.5-flash run: that
  run's confidence-band divergence (`FINDINGS.md`) was a casing artifact,
  not an overstatement — worth explicitly re-checking under D6′ in §7,
  since it's a ready-made first test rather than a hypothetical one.
- **Explicitly out of scope, not forced into a fake test:** whether a system
  can flag "there may be a relevant consideration outside our fixed
  15-metric schedule" — a true unknown-unknown beyond the schedule's own
  boundary. The fixed schedule makes anything outside it structurally
  invisible; that is a scope/architecture question, not a per-output rubric
  criterion, and no criterion above pretends to test it.

---

## 5. Where #11 (Transparency & Explainability) landed

Not a standalone dimension, per `CANDIDATE_SET_v1.md`'s merge decision. Its
content is covered here:

- "Intelligible derivation" → **D5** (Warrant): a re-derivable rule is, by
  construction, a stated one.
- "Legible record" → **D10** (Auditability): a record that fails a cold-read
  test is not legible regardless of completeness.

If §7 testing finds a real gap neither D5 nor D10 catches — e.g. a
derivation that is re-derivable but incomprehensible to a lay reader even
though every step is technically present — that is evidence the merge was
wrong and #11 should be reinstated. Not assumed here either way.

---

## 6. Full dimension index

| ID | Dimension | Status | Measures |
|---|---|---|---|
| D1 | Decision Framing & Scope | Operational | Process / instruction-following |
| D2 | Evidence Provenance & Integrity | Operational | Knowledge-grounding / faithfulness |
| D3 | Evidence Fitness | Operational | Reasoning (relevance) + mechanical (sufficiency) |
| D5 | Inference Soundness / Warrant | Operational | Reasoning |
| Repro | Reproducibility & Determinism | **Gate, not scored** | Engineering (consistency only) |
| D8 | Independent Challenge & Review | Operational | Process |
| D9 | Decision Criteria & Thresholds | Operational | Documentation/governance + reasoning (aggregation) |
| D10 | Auditability & Reconstruction | Operational | Engineering completeness |
| D4′ | Kernel/Area Independence | **Provisional** | Reasoning + corpus-level empirical |
| D6′ | Ordinal Uncertainty Fidelity | **Provisional** | Calibration |
| — | Transparency & Explainability | Merged into D5 + D10 | — |

Seven operational, one gate, two provisional, one merged. 8/2/1, carried
forward exactly as frozen.

---

## 7. Next: test against actual outputs

Not done in this document. What exists in the repo right now that this
rubric could be run against immediately, without producing anything new:

- **`experiments/rubric_reproduction/responses/`** — 10 gemini-2.5-flash
  responses (2 packets × 5 samples), each with known ground truth. Already
  scored on a D5-equivalent basis by `compare.py`. Not yet scored on D1–D3,
  D8–D10, or D6′.
- **`experiments/messy_intake/`** — 5 engineered scenarios including the one
  designed to produce CONTESTED (D4′'s seed case) and the memo-4 negation
  case (a D2/D3 provenance edge case by construction).
- **The `orbital-series-b` / `northwind-seed` worked examples** — YUKTI's
  own engine output, which should score near-ceiling on D2, D5, D10 (all
  three are close to structurally guaranteed by the architecture) and at
  D8 = FAIL, D9 = PARTIAL (both stated as YUKTI's honest current standing
  above, not aspirational).

The test that actually matters most: does scoring the same corpus surface
*different* PASS/PARTIAL/FAIL patterns across D1–D10, or do they all move
together (in which case several "distinct" dimensions are one dimension
wearing ten labels, and this document has the same disease
`CANDIDATE_SET_v1.md`'s meta-rubric was built to catch — just one level
down). That correlation check, not any single dimension's score, is the
real output of §7.
