# DAALE run dataset, 2026-11-17

Built by `../build_dataset.py` from the 16 saved traces in `R-Fabric/runs/` (Nov 10-12, 2026) and the registered
expectations in `R-Fabric/cases/`. Re-running the script regenerates every file. Nothing here was produced by a new
model call. A scan of the traces found no API keys or tokens.

## Read this before training on it

1. **There is very little ground truth.** The only human-written labels are the registered case-level expectations
   (the expected decision, plus the failing requirement for REJECT cases) for 8 cases. Everything else is output from
   Gemini and Gemma models acting as a *teacher*. It is useful, but it is unverified, not gold.
2. **Check the model terms first.** Records carry `served_model` so you can filter by source. I have **not** verified
   whether Google's Gemini API terms or the Gemma terms allow using their outputs to train another model. Do that
   before using any of `sft_pairs.jsonl` or `kernel_outputs.jsonl` for training. Output from a model whose terms forbid it
   should be dropped by filtering on `served_model`.
3. **The cases are few, small and related.** 8 cases, 3 of them synthetic vendor cases, 3 synthetic-reversed, 2 paraphrased from
   published fund-manager case studies. `INV-BANK-B2` is `INV-BANK-A` with one requirement's evidence replaced, and
   `INV-LOGISTICS-B` is the same for `INV-LOGISTICS-A`. **Split by `family`** (vendor, bank, logistics), never by run or
   case, or a near-duplicate leaks across train and test.
4. **I wrote the registered expectations** and know how each case was built. The 4 Aberdeen-derived cases have been
   used for tuning discussions, so do not treat them as a clean held-out set.
5. **The adversary's severity labels are known to be inconsistent** (see the tuning report). Rows carry empty
   `human_severity` and `human_note` fields for you to fill in.

## Files

| File | Rows | One row is |
|---|---|---|
| `cases.jsonl` | 8 | A case: evidence, claims, policy, family, kind, provenance, and the registered label (`label_source` is `registered_before_run` or `design`) |
| `runs.jsonl` | 16 | One engine run: decision, rule, metrics, per-requirement summary, fallbacks, `complete_run`, `matches_expected` |
| `kernel_outputs.jsonl` | 84 | One kernel's validated output for one run: findings, summary, uncertainties, served model, tokens |
| `requirement_verdicts.jsonl` | 174 | One kernel's verdict on one requirement, with the aggregate and the registered expectation where one exists |
| `adversary_findings.jsonl` | 27 | One adversary challenge or contradiction, with severity, target, and whether a base kernel corroborated it |
| `failures.jsonl` | 146 | One failed attempt or fallback event: failure mode, model, attempt, detail |
| `sft_pairs.jsonl` | 84 | Full prompt messages plus the model's validated JSON reply, for supervised fine-tuning |

## Which rows to trust, by purpose

| Purpose | Use | Count |
|---|---|---|
| Teach the decision (case to ADVANCE/REJECT) | `runs.jsonl` with `complete_run` and a registered label | 8 complete runs over 7 cases |
| Teach per-requirement judgment | `requirement_verdicts.jsonl`, `kernel_matches_expected` not null, complete runs | 85 verdicts, 83 match the registered expectation |
| Teach kernel output format | `sft_pairs.jsonl` with `complete_run` true | 56 pairs (84 total) |
| Teach the adversary | `adversary_findings.jsonl` after you add `human_severity` | 27 findings, 14 HIGH, 0 LOW |
| Learn failure handling and routing | `failures.jsonl` | 146 events |

Registered requirement labels cover R1 to R3 on the ADVANCE cases and the single failing requirement on REJECT cases; R4
and the non-failing requirements of REJECT cases are unlabelled, so `expected` is null there.

## Fields worth knowing

- `complete_run`: all six base kernels and the adversary succeeded. Incomplete runs were refused by the engine's integrity rules and carry no usable judgment, but they remain useful for `failures.jsonl`.
- `matches_expected`: null when the run is incomplete or the case has no registered label.
- `corroborated_by_a_base_kernel` (adversary rows): true if any base kernel scored the target requirement non-SATISFIED
  (UNKNOWN counts) or recorded a WEAKENS/CONTRADICTS relation against the target claim. A loose definition.
- `label_quality` in `sft_pairs.jsonl` is always `teacher_output_unverified`.
- `served_model` values present: `gemma-4-31b-it` 38, `gemini-2.5-flash` 22, `gemini-3-flash-preview` 13,
  `gemini-3.8-flash` 11 (kernel outputs).

## What would make this a real training set

- 30 to 50 more cases with expectations registered before any model sees them, split across several families.
- A human pass over `adversary_findings.jsonl` setting the severity you would defend.
- A human pass over a sample of `kernel_outputs.jsonl` findings, to measure how often the teacher is wrong.
- Cases that include a deliberate trap only an adversary should catch.
