# DAALE

DAALE is the implementation scaffold for the architecture represented in this
repository.

The current codebase does not define execution logic. Existing packages and
modules preserve architectural names so future work can add interfaces and
behavior only after the corresponding CHOIR specifications or approved
architecture documents exist.

## Directory Intent

- `conformance/`: **Implemented.** Phase 0 of the DAALE execution plan — the
  frozen CHOIR v0.1 commitments as a machine-readable register, and the lock
  that resolves every piece of evidence they rest on. Reads the subject as
  source; imports nothing from it.
- `ontology/`: Python module boundaries for ontology-related primitives and
  relationships.
- `reasoning/`: Reserved for approved reasoning interfaces and behavior.
- `arbitration/`: Reserved for approved arbitration interfaces and behavior.
- `traceability/`: Reserved for approved traceability interfaces and behavior.
- `runtime/`: Reserved for approved runtime coordination behavior.
- `execution/`: Reserved for approved execution behavior.
- `tests/`: Standard-library tests that protect scaffold stability.

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

## Validation

Run these commands from the repository directory:

```powershell
ruff check .
ruff format --check .
python -m unittest
python -m compileall .
```
