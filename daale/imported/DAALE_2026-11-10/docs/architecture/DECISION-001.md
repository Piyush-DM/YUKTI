# DECISION-001: Deterministic kernels are the architecture

**Status: Approved 2026-08-04.** Recorded retrospectively -- the repository architecture was established by this decision before the working copy was created.

## Context

The DAALE v0.1 architecture establishes deterministic kernels as the canonical reasoning mechanism. Model-backed execution is legacy and not canonical.

## Decision

Approved.

## Consequences

- All reasoning must be expressible as deterministic kernel operations
- Model calls are advisory only, never authoritative
- Replay and determinism checks are mandatory

## Amendment, 2026-11-09 (by DECISION-005)

"Model-backed execution is legacy and not canonical" is narrowed. Model-backed kernels are
admissible as **advisory findings** that feed a deterministic policy engine, provided that:

- every finding is recorded and validated before it is used;
- the policy state is a deterministic function of those recorded findings, so it can be
  recomputed from the trace (replay);
- a model never selects a policy state, never commits anything, and is never read for its own
  confidence.

Model calls remain advisory only, never authoritative. Replay and determinism checks remain
mandatory, and they now apply to the policy step.