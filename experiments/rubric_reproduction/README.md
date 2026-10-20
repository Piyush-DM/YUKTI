# Experiment: rubric reproduction

**Question.** Can a single LLM, given the *same* investment reasoning rubric that
YUKTI's deterministic kernels encode, reproduce the frozen `choir_prototype`
pipeline's output on a synthetic packet?

This is the L-lo ("rubric-executor") control from the experiment design. It is
the tightest test of whether YUKTI's deterministic machinery is *necessary to
produce the answer*: if an LLM can execute the rubric faithfully, the kernels and
synthesizer are a reimplementation of something a model does from the rubric
alone. If it cannot, the deterministic implementation is doing real work.

This scaffold builds ground truth and the control prompts. **It makes no model
call.** Running an LLM against these prompts is a separate, explicitly-approved
step.

> Not built to make YUKTI win. The rubric is a literal transcription of the
> frozen source. If that makes the control unusually strong, that is the finding.

## What is here

| File | Role |
|---|---|
| `rubric.md` | Literal transcription of `kernels.py`, `contracts.py`, `synthesizer.py`, and the citation rule. Carries a machine-readable constants block that a test checks against live source. |
| `ground_truth.py` | Runs `choir_prototype`'s own pipeline for each packet and writes the record, a `comparison_view`, the IR's addressable ids, and the packet document. No expected value is hand-written. |
| `build_prompt.py` | Assembles the L-lo prompt: preamble + `rubric.md` + deterministic id map + packet + output schema. No model client. |
| `compare.py` | Deterministic, network-free diff of a response against ground truth, using the tiered match / partial / divergence rules. Reused by `ground_truth.py` so both sides are extracted by identical code. |
| `run.py` | Regenerates ground truth and prompts, then stops at `prompts generated; awaiting external model responses.` |
| `tests/` | Drift detection, ground-truth fidelity, prompt content + offline guarantees, comparison-engine behaviour. |
| `ground_truth/` | Generated: `<packet>.json` and `<packet>__document.json`. |
| `prompts/` | Generated: `<packet>__L-lo.txt` and `OUTPUT_SCHEMA.json`. |
| `responses/`, `results/` | Not committed (`.gitignore`). Future model responses and comparison output. |

## Boundaries

Nothing here modifies `choir_prototype/`, `daale/`, `applications/`, or any
decision record. It imports the frozen package read-only. `_canonical`,
`record_digest` and `text_digest` are imported from `choir_prototype.core.replay`
for the same reason `applications/investment/vertical_slice/run.py` imports them:
a second copy of that reduction would be a second answer to the same question.

## The two cases

| Packet | Frozen pipeline result | Why it is in the set |
|---|---|---|
| `orbital-series-b` | `proceed with conditions` / `low` confidence; R3 fires; one agreement, one disagreement, one contradiction-driven downgrade | Exercises the most machinery in one run. |
| `northwind-seed` | `insufficient basis` / `insufficient`; R1 fires (only 1 of 4 kernels usable) | Exercises the decline path, which is half of the thesis. |

Both are synthetic packets that ship in the frozen prototype. There is no real
user or company data anywhere in this experiment.

## Run the offline half

```powershell
python -m experiments.rubric_reproduction.run
```

Writes `ground_truth/` and `prompts/`, then prints
`prompts generated; awaiting external model responses.` and stops.

## Run the tests

```powershell
python -m unittest discover -s experiments/rubric_reproduction/tests -t .
```

## After approval to call a model

1. A reviewer diffs `rubric.md` Sections A–G against the four source files (the
   drift test covers the constants in Section H; it cannot see operator direction
   or string wording — Section I lists exactly what it misses).
2. Collect one model response per prompt into `responses/`, each a JSON object
   `{"record": {"artifacts": [...], "synthesis": {...}}}` matching
   `prompts/OUTPUT_SCHEMA.json`. Run `k >= 5` samples per prompt at a recorded
   temperature and model version.
3. For each response:
   ```powershell
   python -m experiments.rubric_reproduction.compare `
     --ground-truth experiments/rubric_reproduction/ground_truth/orbital-series-b.json `
     --response experiments/rubric_reproduction/responses/<file>.json
   ```
4. Read the verdicts. **Reproduces on 5/5** for L-lo is evidence the deterministic
   machinery is not load-bearing for the answer (it may still be load-bearing for
   replay / projection integrity / auditability -- separate claims). **Diverges**
   -- stance flips, wrong fired rule, X4 violations, or a recommendation that
   varies across samples -- is evidence the deterministic implementation is doing
   real work.

## Known validity threats (see the experiment design for the full list)

- **Transcription error** in `rubric.md` turns a real match into a fake one, or
  vice versa. Mitigated by the drift test + the pre-run human diff.
- **The packet is rubric-shaped.** `orbital-series-b` was authored alongside the
  kernels; its metrics are exactly the kernels' predicates, with no noise, no
  prose, and no missing-but-inferable values. A reproduction here does **not**
  generalise to real material.
- **One domain, two cases.** No investment packet reaches `contested` or
  `decline`; those paths are untested by this experiment.
- **The id map is pre-computed.** `build_prompt.py` hands the model the claim /
  evidence / entity ids the translator would assign. This removes a numbering
  confound and is defensible because `translator.py` states it does "no
  reasoning" -- but it is a deliberate choice. The alternative (make the model
  number claims itself) is a knob to turn in a follow-up.
- **"Reproduces the output" is not "the machinery is unnecessary."** This tests
  one YUKTI claim. A pass narrows which claim carries the weight; it is not a
  verdict on YUKTI.
