# Reasoning Execution Substrate

| | |
|---|---|
| **Document ID** | YK-D-001 |
| **Source** | `docs/architecture/DECISION-001_reasoning_execution_substrate.md` (DECISION-001) |
| **Series** | Architecture Decisions |
| **Revision** | A |
| **Status** | Published |
| **Last Updated** | 2026-08-23 |

## Abstract

This document records the approved ruling on what executes a reasoning
kernel: deterministic code, or a language model constrained by an output schema.
The ruling adopts Option A — deterministic kernels are the architecture, and the
model-backed path under `applications/investment/prototype_risk_rik/` is legacy,
retained for reference and not canonical architecture (§ Recommendation,
§ Consequences). The source records that the decision was written down
retrospectively, after the repository already contained two contradictory
answers to the question (status note).

This is a Published ruling: approved by Piyush on 2026-08-04 (§ Approval
Status).

## Research Question

The source states the question explicitly (§ Decision):

> What executes a reasoning kernel: deterministic code, or a language model
> constrained by an output schema?

The source records that the question was live because the repository answered it
both ways at once, in two places that do not reference each other, and that both
are described as prototypes with neither described as superseding
the other — "so a reader cannot tell which represents the intended
architecture" (§ Decision).

## Finding

### The contradiction on record

The source tabulates the two contradictory answers found in the repository
(§ Decision):

| Path | Substrate | Self-description |
|---|---|---|
| `choir_prototype/` | Deterministic Python, standard library only | "No LLM call anywhere" |
| `applications/investment/prototype_risk_rik/` | OpenAI Responses API, Pydantic-validated output | "It does not represent live model reasoning" (of its *deterministic* provider only) |

### The options considered

The source sets out three options (§ Options), stated here in its own terms:

- **Option A — deterministic kernels are the architecture.** Model-backed
  execution is exploratory work, retained as legacy and wound down. Kernels are
  code that reads an intermediate representation and emits a structured
  artifact.
- **Option B — model-backed kernels are the architecture.** Kernels are model
  calls whose outputs are schema-validated. Determinism is abandoned or
  relocated to a caching or seeding layer.
- **Option C — both, at different tiers.** Deterministic kernels for
  adjudication, model-backed extraction upstream of the IR.

### Why Option B is rejected

The source identifies three CHOIR commitments as load-bearing here, and states
that Option B "breaks all three at once" (§ Tradeoffs):

1. **Confidence is derived, never authored** (`confidence_framework.md` §1). A
   model emitting a confidence field into a schema *authors* it. Schema
   validation checks the shape of the value, not its provenance. The source
   records that `contracts.py` currently defines `QualitativeConfidence` as an
   enum the provider fills in — "which is authorship with a type check on it."
2. **Independent agreement is evidence, not echo.** Two kernels backed by the
   same model are not independent in the sense that makes agreement meaningful.
   The source names shared training data as a common cause, and states that
   "the prototype's whole argument for why agreement counts collapses."
3. **Replay and projection integrity** (`explainability_framework.md` §1). A
   non-deterministic step means a record cannot be re-derived, so the
   `execution-determinism` and `projection-integrity` checks cannot hold.

### Why Option C is not adopted now

The source describes Option C as "coherent in principle" and close to
commitment #10 — *neural retrieval, symbolic adjudication: embeddings propose,
they never conclude* (`knowledge_graph_spec.md` §2.5). It rules Option C out as
a description of present practice on a factual ground, not a principled one:
"It is not what the investment prototype does today: its model call produces the
conclusion, not a retrieval candidate" (§ Tradeoffs).

### Cost, and the ruling

The source records that Option A costs the least, on two stated grounds: the
model-backed path is one isolated vertical slice under `applications/`, and the
deterministic path "already carries the project's only measured result"
(§ Tradeoffs).

The recommendation adopted is **Option A** — "the only option consistent with
the project's stated thesis and with the three commitments above." The source
qualifies this: Option C "remains available later for extraction upstream of the
IR, where a proposing model concludes nothing — but that is a different
decision, and adopting it should not be confused with keeping the current
provider" (§ Recommendation).

### What the ruling does and does not do

The consequences recorded (§ Consequences):

- `applications/investment/prototype_risk_rik/` is **legacy**. Its OpenAI
  provider is retained for reference and is not canonical architecture.
- No new work should extend the model-backed path.
- Retirement is not performed by this note. The source states that removing the
  legacy path "touches a passing test suite and a running UI, so it is scheduled
  work, not a side effect of writing a decision down."
- `requirements-dev.txt` and `pyproject.toml` keep `httpx` while the legacy path
  exists. Both can be reviewed at retirement.

The source also records the provenance of the ruling itself: it was "recorded
retrospectively — the repository already contained two contradictory answers to
this question before the decision was written down" (status note).

## Architectural Implications

The implications below are drawn from the source's own statements. The source
has no section of this kind and does not itself present them as implications.

A reasoning kernel is deterministic code that reads an intermediate
representation and emits a structured artifact (§ Options, Option A). The
operative rule the source states is narrower than a general prohibition: "No new
work should extend the model-backed path" (§ Consequences).

Three commitments constrain any future substrate proposal, because the source
treats them as the test Option B failed: confidence must be derived rather than
authored (`confidence_framework.md` §1); agreement between kernels counts as
evidence only where the kernels are independent, which two kernels backed by the
same model are not; and records must be re-derivable, or the
`execution-determinism` and `projection-integrity` checks cannot hold
(`explainability_framework.md` §1) (§ Tradeoffs).

Model-backed components are not excluded from the architecture in general, but
their admissible position is bounded: upstream of the IR, as extraction where "a
proposing model concludes nothing," consistent with *neural retrieval, symbolic
adjudication: embeddings propose, they never conclude*
(`knowledge_graph_spec.md` §2.5). Admitting such a component is a separate
decision that this ruling does not make (§ Recommendation).

The legacy path continues to exist; the source records that removing it "touches
a passing test suite and a running UI," so the ruling constrains new work rather
than immediately removing the old (§ Consequences).

## Open Questions

The source records the following unresolved or deferred items:

- **Option C is deferred, not decided.** Adopting model-backed extraction
  upstream of the IR "remains available later" but is "a different decision"
  that this note does not make (§ Recommendation).
- **Retirement of the legacy path is scheduled work, not done.** The source
  states that retirement "is not performed by this note" and is "scheduled work"
  because it touches a passing test suite and a running UI (§ Consequences). The
  source does not record when that work is to be carried out.
- **Dependency cleanup is deferred.** `requirements-dev.txt` and `pyproject.toml`
  keep `httpx` while the legacy path exists; "both can be reviewed at
  retirement" (§ Consequences).
- **`QualitativeConfidence` in `contracts.py` is recorded as non-conforming** —
  an enum the provider fills in, described as "authorship with a type check on
  it" (§ Tradeoffs). The source records the defect; it does not record a
  remediation.
- **The decision is retrospective.** The source notes the repository held two
  contradictory answers before the decision was written down (status note); it
  does not record what else was built against the unresolved contradiction.

## Related Documents

- [YK-R-011 — Confidence Framework](YK-R-011-confidence-framework.md) — cited as
  `confidence_framework.md` §1 for the commitment that confidence is derived,
  never authored (§ Tradeoffs).
- [YK-R-012 — Explainability Framework](YK-R-012-explainability-framework.md) —
  cited as `explainability_framework.md` §1 for replay and projection integrity,
  and the `execution-determinism` and `projection-integrity` checks
  (§ Tradeoffs).
- [YK-R-003 — Knowledge Graph Specification](YK-R-003-knowledge-graph-specification.md)
  — cited as `knowledge_graph_spec.md` §2.5 for commitment #10, *neural
  retrieval, symbolic adjudication: embeddings propose, they never conclude*
  (§ Tradeoffs).
- [YK-R-013 — CHOIR Intermediate Representation](YK-R-013-choir-intermediate-representation.md)
  — the source depends on "an intermediate representation" / "the IR" as the
  input a kernel reads and as the boundary above which a proposing model may sit
  (§ Options, § Recommendation). The source refers to the IR without naming a
  document.
