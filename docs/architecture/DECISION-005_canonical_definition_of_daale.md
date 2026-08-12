# ADR — Canonical Definition of DAALE

**Status: Open. Not accepted.** Raised under Authorization 5. **No
implementation shall depend on assumptions regarding DAALE until this ADR is
accepted.**

This record exists to stop a question being answered by accident. It is
deliberately not answered here.

## The question

What is DAALE, and what is its relationship to CHOIR, to `choir_prototype/`, and
to any future reference implementation?

## Why it is open

The repository, the research corpus and two independent architectural reviews do
not agree, and each has been treated as authoritative by someone.

| Source | What it says DAALE is |
|---|---|
| `daale/` in this repository | A scaffold. Configuration, environment diagnostics, logging, report paths, and ontology modules that are docstrings with no behaviour. **No reasoning logic.** |
| `README.md` | "DAALE implementation scaffold… DAALE currently contains no reasoning logic." |
| `choir_prototype/README.md` | "**This is not YUKTI and not DAALE architecture.**" |
| `CHOIR_v0.1_RESEARCH_FREEZE.md` §4.4 | Records the relationship as **an open question**: whether the prototype graduates into DAALE, or DAALE is a separate target, is undecided. |
| Independent review, 2026-08-06 | "DAALE is its reference implementation" — describing an engine with `authority/lock.py`, `engine/core.py`, `evaluators.py`, a `BasisDemoEvaluator`, and five passing tests. |

**None of the modules in that last row exist in this repository.** Verified
2026-08-06: `authority/lock.py`, `engine/core.py`, `experiments/runner.py`,
`trace/events.py`, `provenance/model.py`, `judgment/basis.py`, `contract/` and
`evaluators.py` are all absent, `daale/` contains no `evaluate`, no `judgment`
and no `INSUFFICIENT_BASIS`, and its suite is 12 tests rather than 5.

The review is therefore a competent analysis of a **different or hypothetical**
DAALE. That is not a criticism of it — its diagnosis of the missing canonical
semantics converges with this repository's own recorded governance gap. But it
cannot be read as a description of this codebase, and its prescriptions were
written for the codebase it describes.

## What is at stake

The prescriptions differ depending on the answer, and one of them is dangerous.

The review recommends a **configurable hybrid evaluator** — forward chaining,
backward chaining, certificate production and optionally Rete, behind one
evaluator interface. If DAALE is the engine and DAALE is greenfield, that is
reasonable advice.

If DAALE is *this* repository, adopting it would replace CHOIR v0.1 outright:
the engine here is four deterministic kernels and a synthesizer, hash-pinned,
frozen, and carrying the project's only measured result. The same applies to the
review's Pydantic-strict recommendation — `choir_prototype/` is standard-library
only *by design*, because that is what makes its determinism auditable.

An unaccepted definition of DAALE is thus not a documentation gap. It is a live
route to un-freezing the engine by implication.

## Options, unassessed

Recorded so the ADR has something to accept. No recommendation is made.

- **A — DAALE is the future reference implementation**, and `choir_prototype/`
  is the V0.1 evidence artefact it will supersede.
- **B — DAALE is a separate architectural target**, and `choir_prototype/` is
  and remains the reference implementation of CHOIR.
- **C — DAALE is retired as a name**, its scaffold folded into whichever
  component ends up owning execution.
- **D — DAALE is the product-side engine boundary**, and the workspace's
  `analysis.py` is already an early form of it.

## Constraint while this is open

Recorded as the operative rule, not as advice:

- No implementation may assume any of A–D.
- Nothing may be moved into or out of `daale/` on the basis of an assumed
  answer.
- The Material Snapshot layer (`DECISION-006`) is deliberately built with **no
  DAALE dependency of any kind**, which is what allowed this cycle to proceed
  while this ADR is open.

## Approval Status

Open. Requires architect acceptance.
