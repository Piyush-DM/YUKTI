# Decision: the candidate escalation rule

**Status: Approved 2026-08-14.** Codified by the architect's DAALE v0 closure
instruction, which directed that the escalation rule be made a rule rather than
left as an implementation assumption.

This supersedes assumption **G3** recorded in
`docs/development/IMPLEMENTATION_LOG.md` for the DAALE v0 Phases 1–2 cycle. G3
is closed by this note.

## Decision

The v0 execution plan states that `REVIEW_REQUIRED` is one of the terminal
states of the candidate-to-commit protocol, and states as a risk control that
model and human output "remain proposals until commit validation succeeds" and
"require validation/human review where appropriate".

It does not say **which origins escalate**. The commit gate cannot be written
without answering that, so it was answered provisionally as G3 and is answered
here properly.

## The rule

A candidate that fails any active gate check is `REJECTED`. A candidate that
passes every active check is then decided by its origin:

| Origin | Outcome |
|---|---|
| `dcore` | `VALIDATED` — may commit |
| `rfabric` | `VALIDATED` — may commit |
| `algorithm` | `VALIDATED` — may commit |
| **anything else** | `REVIEW_REQUIRED` — escalated, never committed |

The allow-list lives in `daale/execution/commit.py` as `DETERMINISTIC_ORIGINS`.

## The property that matters: default-deny

The rule is stated as an **allow-list, not a deny-list**, and that is the whole
substance of the decision rather than a stylistic choice.

Under a deny-list, an origin nobody thought to name — a new adapter, a new tool,
a coprocessor added in Phase 6 — would commit to canonical state silently, and
the failure would be invisible because the gate would report a pass. Under an
allow-list, the same unnamed origin escalates. Someone has to notice it and
decide.

That is the direction the project already treats as correct everywhere else: an
unevaluated thing is never a false thing (commitment E13), coverage gaps are
reported rather than assumed benign, and `INSUFFICIENT_BASIS` is a valid
result. An unrecognised origin is a coverage gap about *authority*, and the
conservative outcome is escalation.

## Options considered

**A — Escalate everything.** Every candidate goes to review. Maximally
conservative and makes the D-Core useless as an automated commit authority:
there would be no path by which anything becomes canonical without a human,
which is not what the plan describes.

**B — Allow-list of deterministic origins; everything else escalates.**
*Chosen.*

**C — Deny-list of known non-deterministic origins.** Rejected. An origin
nobody enumerated commits silently. This is the failure mode the whole
candidate protocol exists to prevent, reintroduced at the last step.

**D — No escalation; origin is recorded but not acted on.** Rejected. It
reduces `REVIEW_REQUIRED` to documentation, and it puts a model or a human on
exactly the same footing as a deterministic kernel, which is the "LLM authority
leakage" risk the plan names.

## Why these three origins

They are the ones whose output is reproducible, which is the property that makes
direct commit defensible:

- `dcore` — the commit authority itself.
- `rfabric` — parallel evaluation of deterministic kernels. Non-authoritative by
  design, but reproducible, and the plan's acceptance criterion requires that
  R-Fabric on or off does not change semantic results.
- `algorithm` — deterministic computation: parsing, traversal, matching,
  hashing, dependency analysis. The plan's own list for this coprocessor class.

Everything the plan lists as a coprocessor that can *disagree with itself* —
LLM, human reviewer, external tool — is deliberately absent.

This is consistent with `DECISION-001`, which made model-backed execution legacy
and non-canonical on the ground that a model emitting a value into a schema
*authors* it. Escalation is that finding applied at the commit gate: a model may
propose, and a person decides whether the proposal becomes institutional fact.

## Consequences

- **Adding an origin to `DETERMINISTIC_ORIGINS` requires an approved decision.**
  It grants canonical write authority to a new class of producer, which is not
  an implementation detail.
- Phase 6 coprocessor adapters do not need this revisited. LLM, human and
  external-tool adapters escalate under the rule as written, which is the
  intended behaviour.
- The rule decides *routing*, not correctness. An escalated candidate is not
  suspect; it is unreviewed. Nothing in the gate claims a `REVIEW_REQUIRED`
  candidate is wrong.
- **There is no review workflow.** Escalation marks a candidate and leaves it
  outside canonical state. Who reviews, how they record the outcome, and how a
  reviewed candidate re-enters the gate are not answered here and are not part
  of v0. Named so the gap is visible rather than discovered later.

## Defended by

`daale/tests/test_execution.py`:

| Property | Test |
|---|---|
| A non-deterministic origin escalates | `test_a_non_deterministic_origin_escalates_rather_than_commits` |
| A deterministic origin validates | `test_a_deterministic_origin_validates` |
| An escalated candidate never reaches canonical state | `test_an_escalated_candidate_leaves_canonical_state_untouched` |

## Approval Status

Approved 2026-08-14, by the DAALE v0 closure instruction.
