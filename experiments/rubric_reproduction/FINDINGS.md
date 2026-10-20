# Findings: L-lo run, gemini-2.5-flash (2026-09-11)

The first model run against the L-lo control. `rubric.md`, `compare.py`,
`build_prompt.py`, `ground_truth.py`, and the generated prompts were **not
modified** for this run — nothing about the experiment's own logic was touched
to produce or interpret these numbers.

## Setup

- **Model:** `gemini-2.5-flash`, called directly via Google's `generateContent`
  REST endpoint (not the Anthropic-gateway path `assistant.py` uses) —
  `experiments/rubric_reproduction/collect_responses.py`, a new file that
  implements the README's "after approval to call a model" step.
- **Protocol:** k = 5 samples per packet, both packets (`orbital-series-b`,
  `northwind-seed`) — 10 calls total, 10/10 succeeded, 0 parse failures.
- **Not recorded:** temperature. Gemini's default sampling was used; it was
  not pinned. Worth fixing before this is treated as a repeatable baseline —
  see Caveats.
- **The prompt was the entire message.** No system prompt beyond what the
  generated `.txt` file already contains; no schema-forced decoding beyond
  `responseMimeType: application/json` (format only, not content).

## Headline

Every one of the 10 raw comparisons returned **`Diverges`** from
`compare.py`. Read literally, that looks like a clear failure to reproduce.
It is not what the numbers mean once you look at *which* fields diverged.

**Reproduced exactly, in all 10 samples, both packets:**
recommendation · fired decision rule · every finding, stance and topic · every
claim/evidence citation (**zero X4 violations across all 10 runs** — the model
never cited an id absent from the IR) · kernel coverage · kernel
contradictions · kernel derivation steps and outcome · support/oppose/
conditional tally · usable kernels · agreements · disagreements.

**What actually diverged, and what it turned out to be:**

| Field | Raw verdict | Cause |
|---|---|---|
| `confidence` (tier 1) | divergence, 10/10 | **casing only** — `"LOW"` vs `"low"` |
| `kernel_bands` | divergence, 10/10 | **casing only** — `"MODERATE"`/`"REPORTED"` vs lowercase |
| `kernel_limiting_factors` | divergence, 10/10 | casing in 2/10 (northwind runs 2–3); **genuinely different sentence content in 8/10** |
| `confidence_limiting_factor` | divergence, 5/5 on orbital | casing does not explain it — **real** |
| `remaining_uncertainty` | divergence, 2/5 on orbital | casing does not explain it — real, but inconsistent across samples |

`experiments/rubric_reproduction/case_sensitivity_check.py` (new, also added
this run) re-scores every collected response with all strings case-folded,
reusing `compare.py`'s own `build_comparison_view` / `compare_views`
unmodified, and reports which fields were casing-only versus still divergent.
Full per-sample output: `results/case_sensitivity_check.json`.

| Sample | raw tier-2 match | case-folded tier-2 match | case-folded verdict |
|---|---|---|---|
| northwind run 1 | 0.778 | 0.889 | Substantially reproduces |
| northwind run 2 | 0.778 | **1.000** | **Reproduces** |
| northwind run 3 | 0.778 | **1.000** | **Reproduces** |
| northwind run 4 | 0.778 | 0.889 | Substantially reproduces |
| northwind run 5 | 0.778 | 0.889 | Substantially reproduces |
| orbital run 1–5 | 0.778 (all 5) | 0.889 (all 5) | Substantially reproduces (all 5) |

## Reading the real finding

Once casing is factored out, **no sample regresses to genuine `Diverges`.**
The floor is "Substantially reproduces," and the one thing consistently
keeping every sample off "Reproduces" is a **sentence-template fidelity gap**,
not a reasoning gap: the rubric specifies a literal string template for a
kernel's `limiting_factor` when the limiting factor is "weakest evidence is
`{quality}` (`{source}`)". The model gets the *content* right every time —
correct evidence quality, correct source label — but does not reliably
reproduce the *literal template*. Two concrete examples pulled from the raw
data:

- Ground truth: `weakest evidence is reported (SRC-DECK)`
  Response: `weakest evidence is SRC-DECK (REPORTED)` — same fact, slots
  swapped.
- This shows up on `orbital-series-b`'s `confidence_limiting_factor`
  **5 times out of 5** — the one field that never once matched, even after
  casefolding.

`northwind-seed`'s top-level `confidence_limiting_factor` is a **fixed**
string with no placeholders ("too few kernels reached a usable band"), and it
matched in all 5 samples — consistent with the template-fidelity
interpretation: fixed strings reproduce exactly; templated ones don't.

## Against the experiment's actual question

The question this experiment exists to answer is whether the deterministic
kernels + synthesizer are a reimplementation of something an LLM can do
directly from the rubric. On this run:

- **Decision logic** (which findings fire, evidence weighing, contradiction
  detection, which rule fires, the recommendation itself) reproduced
  perfectly, 10/10, with zero id fabrication. That is real evidence the
  qualitative reasoning is not load-bearing in the sense of "only the frozen
  code can do this."
- **Confidence-band derivation** (the numeric/ordinal part — evidence floor,
  coverage-based downgrade, weakest-wins aggregation) also reproduced
  correctly *in substance*, every time — the divergence there was entirely a
  formatting habit (uppercase enums), not a computation error.
- **Literal string-template reproduction** is where the model is genuinely
  unreliable. Whether that matters depends on what the deterministic
  machinery is actually being credited for: if part of YUKTI's claim is
  *exact, literal wording* in the institutional record (not just the correct
  conclusion), this run is evidence that claim still needs the frozen
  implementation. If the claim is only about the *conclusion and its
  grounding*, this run does not support the machinery being necessary.

That distinction was not resolved by this run and should not be read as
resolved.

## What this does not show

- **One model, one provider, no temperature pinned.** This is not the
  "recorded temperature and model version" protocol the README asks for —
  temperature was left at Gemini's default. A second run should pin it
  explicitly and note the value.
- **`compare.py`'s case-sensitivity is not a bug being reported here.** It is
  the correct default for the real experiment — the frozen engine's
  vocabulary is a fixed lowercase enum, and a response that drifts from it is
  worth flagging on its own terms. This document exists to separate that
  formatting signal from the reasoning signal, not to argue the scorer should
  change.
- **Both packets are the synthetic, rubric-shaped ones the README already
  names as a validity threat** — no noisy prose, no missing-but-inferable
  values, no `contested` or `decline` path exercised. This run does not
  speak to messier material.

## Files this run added

- `collect_responses.py` — makes the model call; the README's step 2.
- `case_sensitivity_check.py` — diagnostic-only, reuses `compare.py`
  unmodified.
- `responses/`, `results/` — gitignored already; not committed. This file is
  the durable record of what they showed.

## Suggested next step

Not yet done, and worth flagging as a real choice rather than folding it in
silently: rerun with a fixed, recorded temperature, and separately test
whether an explicit instruction to match the schema's lowercase convention
closes the casing gap without being asked to "get the right answer" — i.e.
whether the remaining gap is really about template literalism once casing is
controlled for by instruction rather than by post-hoc analysis.
