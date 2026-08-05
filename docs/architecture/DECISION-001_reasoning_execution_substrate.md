# Decision Required: reasoning execution substrate

**Status: Approved 2026-08-04.** Recorded retrospectively — the repository
already contained two contradictory answers to this question before the
decision was written down.

## Decision

What executes a reasoning kernel: deterministic code, or a language model
constrained by an output schema?

The repository currently answers both ways, in two places that do not reference
each other:

| Path | Substrate | Self-description |
|---|---|---|
| `choir_prototype/` | Deterministic Python, standard library only | "No LLM call anywhere" |
| `applications/investment/prototype_risk_rik/` | OpenAI Responses API, Pydantic-validated output | "It does not represent live model reasoning" (of its *deterministic* provider only) |

Both are described as prototypes. Neither is described as superseding the
other, so a reader cannot tell which represents the intended architecture.

## Options

**Option A — deterministic kernels are the architecture.** Model-backed
execution is exploratory work, retained as legacy and wound down. Kernels are
code that reads an intermediate representation and emits a structured artifact.

**Option B — model-backed kernels are the architecture.** Kernels are model
calls whose outputs are schema-validated. Determinism is abandoned or relocated
to a caching or seeding layer.

**Option C — both, at different tiers.** Deterministic kernels for adjudication,
model-backed extraction upstream of the IR.

## Tradeoffs

Three CHOIR commitments are load-bearing here, and Option B breaks all three at
once:

- **Confidence is derived, never authored** (`confidence_framework.md` §1). A
  model emitting a confidence field into a schema *authors* it. Schema
  validation checks the shape of the value, not its provenance. `contracts.py`
  currently defines `QualitativeConfidence` as an enum the provider fills in —
  which is authorship with a type check on it.
- **Independent agreement is evidence, not echo.** Two kernels backed by the
  same model are not independent in the sense that makes agreement meaningful.
  Shared training data is a common cause; the prototype's whole argument for
  why agreement counts collapses.
- **Replay and projection integrity** (`explainability_framework.md` §1). A
  non-deterministic step means a record cannot be re-derived, so the
  `execution-determinism` and `projection-integrity` checks cannot hold.

Option C is coherent in principle and is close to commitment #10 — *neural
retrieval, symbolic adjudication: embeddings propose, they never conclude*
(`knowledge_graph_spec.md` §2.5). It is not what the investment prototype does
today: its model call produces the conclusion, not a retrieval candidate.

Option A costs the least. The model-backed path is one isolated vertical slice
under `applications/`, and the deterministic path already carries the
project's only measured result.

## Recommendation

**Option A.** It is the only option consistent with the project's stated thesis
and with the three commitments above. Option C remains available later for
extraction upstream of the IR, where a proposing model concludes nothing — but
that is a different decision, and adopting it should not be confused with
keeping the current provider.

## Consequences

- `applications/investment/prototype_risk_rik/` is **legacy**. Its OpenAI
  provider is retained for reference and is not canonical architecture.
- No new work should extend the model-backed path.
- Retirement is not performed by this note. Removing it touches a passing test
  suite and a running UI, so it is scheduled work, not a side effect of writing
  a decision down.
- `requirements-dev.txt` and `pyproject.toml` keep `httpx` while the legacy path
  exists. Both can be reviewed at retirement.

## Approval Status

Approved by Piyush, 2026-08-04.
