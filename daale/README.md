# DAALE

DAALE is the implementation scaffold for the architecture represented in this
repository.

The current codebase does not define execution logic. Existing packages and
modules preserve architectural names so future work can add interfaces and
behavior only after the corresponding CHOIR specifications or approved
architecture documents exist.

## Directory Intent

- `conformance/`: **Implemented (v0 Phase 0).** The frozen CHOIR v0.1
  commitments as a machine-readable register, the lock that resolves every
  piece of evidence they rest on, and the classification of every gap the lock
  finds. Reads the subject as source; imports nothing from it.
- `execution/`: **Implemented (v0 Phases 1–2).** The D-Core, the Reasoning
  State Store, the execution trace, CHOIR contract validation, and the
  candidate-to-commit gate. No evaluator — see below.
- `ontology/`: Python module boundaries for ontology-related primitives and
  relationships.
- `reasoning/`: Reserved for approved reasoning interfaces and behavior.
- `arbitration/`: Reserved for approved arbitration interfaces and behavior.
- `traceability/`: Reserved for approved traceability interfaces and behavior.
- `runtime/`: Reserved for approved runtime coordination behavior.
- `tests/`: Standard-library tests that protect scaffold stability.

## The DECISION-005 boundary

DAALE v0 stops at one specific point, and it is worth stating plainly because
everything else in `execution/` is complete without it.

The D-Core validates, orders, versions, commits, traces and terminates. It does
not evaluate. Evaluating requires deciding *who evaluates* — whether DAALE
calls the frozen prototype's kernels or evaluates for itself — and those are
options **B** and **A** of `DECISION-005` verbatim. There is no neutral third
answer, because "who evaluates" is exactly what that ADR asks.

There is therefore **no evaluator and no placeholder for one**. A stub raising
`NotImplementedError` would still assert that the evaluator belongs inside
DAALE, which is itself one of the answers. `test_the_d_core_has_no_evaluator`
guards the boundary mechanically so it cannot erode one convenient method at a
time.

Every `ExecutionSummary` reports `emits_judgment=False` and carries the reason,
so a completed execution cannot be mistaken for an adjudicated one.

## Implementation Boundary

Until a specification is approved, DAALE modules should contain documentation,
typing scaffolds, and tests that verify stability rather than behavior. Do not
introduce new runtime dependencies or frameworks without explicit approval.

**One exception, and its limits.** `conformance/` contains behavior. It was
built under direct architectural instruction to implement the DAALE v0
execution plan, which the rules permit as an alternative to a specification. It
carries no dependency on `DECISION-005`: the commitments it locks are CHOIR's
and are identical under every option that ADR leaves open, and the package
imports nothing from `choir_prototype` or `applications`. Nothing else in
`daale/` has been unblocked by it.

## Conformance

Run the lock from the repository directory:

```powershell
python -m daale conformance
```

It exits non-zero when a frozen commitment cites evidence that no longer
exists, and writes `reports/daale/conformance/`. Current result: 28
commitments, 20 conforming, 8 unexercised, 0 unresolved.

The eight unexercised commitments are **classified, not queued**. Each carries
the source that says why it is unimplemented — a research question, a recorded
prototype limit, an unmade decision, or an evidence discrepancy. Four are §4
research programmes, and research freeze §9 forbids partially implementing one
to make a current problem easier. `E12` is the single evidence discrepancy: the
freeze marks it demonstrated while the repository cites nothing, and it stays
surfaced until an architect adjudicates it.

## Validation

Run these commands from the repository directory:

```powershell
ruff check .
ruff format --check .
python -m unittest
python -m compileall .
```
