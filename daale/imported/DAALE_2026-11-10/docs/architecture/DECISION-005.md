# DECISION-005: Canonical Definition of DAALE

**Status: Approved 2026-11-09.** Decided by the repository owner from the options in
`BRIEF-DECISION-005_2026-11-09.md`. Recorded in this working copy; the canonical repository needs
the same edit set (listed under Consequences).

## The question

What is DAALE, and who evaluates? When the D-Core commits a decision, who produced the reasoning
behind it?

The ADR originally listed two answers: **A**, DAALE evaluates for itself; **B**, DAALE calls the
frozen `choir_prototype` kernels. A working-copy ruling of 2026-08-29 gave a third, **R-Fabric
evaluates, D-Core commits**, for the old working copy only
(`DECISION-005_RULING_rfabric_evaluates.md.bak`).

## Decision

**R-Fabric evaluates. The D-Core commits.** This ratifies the 2026-08-29 ruling for the whole
repository, with the four conditions below.

- **R-Fabric** is the evaluator. Its model-backed kernels produce *advisory findings*; its
  deterministic policy engine turns validated findings into a policy state (ADVANCE, HOLD, REJECT
  or ESCALATE). Model output enters only as recorded findings. No model selects a policy state or
  is read for its own confidence.
- **The D-Core** validates, orders, arbitrates, versions, commits and traces. It has no evaluator
  and no stub for one, never imports R-Fabric, and emits no judgment. A committed policy state is
  not an institutional decision.
- **A human** retains final authority. Every packet carries the authority notice.

## Conditions (part of the decision)

1. **DECISION-001 is narrowed.** Model-backed kernels are admissible as advisory findings feeding a
   deterministic policy engine (see the amendment in `DECISION-001.md`).
2. **Replay.** The policy state of a completed run can be recomputed from the findings its trace
   recorded. `python -m daale.replay <trace>` (in R-Fabric) does it and reports any difference.
3. **The review flag has teeth.** A packet carrying `execution_integrity.requires_human_review`
   becomes a candidate with `needs_review=True`; the D-Core gate escalates it to `REVIEW_REQUIRED`
   instead of committing it. This adds a second reason to escalate to DECISION-007's rule. It does
   not widen `DETERMINISTIC_ORIGINS`. DECISION-007 is not in this working copy and should record
   the addition.
4. **The authority notice stays** in every decision packet.

## Consequences

- Unchanged on purpose: the D-Core has no evaluator; `emits_judgment` stays false;
  `test_the_d_core_has_no_evaluator` still guards the boundary.
- Changed deliberately, because they pinned this ADR as open: `test_conformance.py` (the open-ADR
  example now uses a synthetic open decision, and the status pin reads "Approved 2026-11-09."),
  the docstrings of `execution/dcore.py` and `rfabric.py`, the D-Core README, and the reason every
  execution summary carries when it explains why it emits no judgment.
- Added: `Candidate.needs_review` and its gate branch (`execution/commit.py`), the bridge setting
  it (`rfabric.py`), and R-Fabric's `daale/replay.py`.
- Not decided here: how a human review is recorded and closed; persistence of canonical state
  (still in memory per admission); whether the policy engine will later need calibrated
  uncertainty.
