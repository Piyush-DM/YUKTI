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