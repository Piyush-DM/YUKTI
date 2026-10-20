# The Candidate Escalation Rule

| | |
|---|---|
| **Document ID** | YK-D-007 |
| **Source** | `docs/architecture/DECISION-007_candidate_escalation_rule.md` (DECISION-007) |
| **Series** | Architecture Decisions |
| **Revision** | A |
| **Status** | Published |
| **Last Updated** | 2026-08-23 |

*The source document numbers no sections. Citations below therefore name the source's headings — for example (§ "The rule") — so any claim can be checked against the original.*

## Abstract

This decision fixes which candidate origins may commit directly to canonical state and which are escalated to `REVIEW_REQUIRED`. The rule is stated as an allow-list of three deterministic origins — `dcore`, `rfabric`, `algorithm` — with everything else escalating; the source states that the allow-list form "is the whole substance of the decision rather than a stylistic choice" (§ "The property that matters: default-deny"). The document carries **Status: Approved 2026-08-14**, codified by the architect's DAALE v0 closure instruction, and supersedes assumption **G3** in `docs/development/IMPLEMENTATION_LOG.md` for the DAALE v0 Phases 1–2 cycle (§ preamble, § "Approval Status").

## Research Question

The source frames the question in its Decision section. The v0 execution plan already states that `REVIEW_REQUIRED` is one of the terminal states of the candidate-to-commit protocol, and states as a risk control that model and human output "remain proposals until commit validation succeeds" and "require validation/human review where appropriate" (§ "Decision").

What the plan does not say is **which origins escalate**. The source states: "The commit gate cannot be written without answering that, so it was answered provisionally as G3 and is answered here properly" (§ "Decision"). The question this document sets out to answer is therefore: which candidate origins are permitted to commit to canonical state without human review, and by what rule form is that set expressed.

## Finding

### The rule as codified

A candidate that fails any active gate check is `REJECTED`. A candidate that passes every active check is then decided by its origin (§ "The rule"):

| Origin | Outcome |
|---|---|
| `dcore` | `VALIDATED` — may commit |
| `rfabric` | `VALIDATED` — may commit |
| `algorithm` | `VALIDATED` — may commit |
| **anything else** | `REVIEW_REQUIRED` — escalated, never committed |

The allow-list lives in `daale/execution/commit.py` as `DETERMINISTIC_ORIGINS` (§ "The rule").

### Default-deny is the substance of the decision

The source states that the rule is expressed as "an **allow-list, not a deny-list**, and that is the whole substance of the decision rather than a stylistic choice" (§ "The property that matters: default-deny").

The reasoning given is a comparison of failure modes. Under a deny-list, "an origin nobody thought to name — a new adapter, a new tool, a coprocessor added in Phase 6 — would commit to canonical state silently, and the failure would be invisible because the gate would report a pass." Under an allow-list, that same unnamed origin escalates: "Someone has to notice it and decide" (§ "The property that matters: default-deny").

The source places this in continuity with commitments the project already holds: "an unevaluated thing is never a false thing (commitment E13), coverage gaps are reported rather than assumed benign, and `INSUFFICIENT_BASIS` is a valid result. An unrecognised origin is a coverage gap about *authority*, and the conservative outcome is escalation" (§ "The property that matters: default-deny").

### Options considered

The source records four options and the grounds for each disposition (§ "Options considered"):

| Option | Disposition | Stated grounds |
|---|---|---|
| **A — Escalate everything.** Every candidate goes to review. | Not chosen | "Maximally conservative and makes the D-Core useless as an automated commit authority: there would be no path by which anything becomes canonical without a human, which is not what the plan describes." |
| **B — Allow-list of deterministic origins; everything else escalates.** | ***Chosen.*** | — |
| **C — Deny-list of known non-deterministic origins.** | Rejected | "An origin nobody enumerated commits silently. This is the failure mode the whole candidate protocol exists to prevent, reintroduced at the last step." |
| **D — No escalation; origin is recorded but not acted on.** | Rejected | "It reduces `REVIEW_REQUIRED` to documentation, and it puts a model or a human on exactly the same footing as a deterministic kernel, which is the 'LLM authority leakage' risk the plan names." |

### Why these three origins

The stated selection criterion is reproducibility — "which is the property that makes direct commit defensible" (§ "Why these three origins"):

- `dcore` — "the commit authority itself."
- `rfabric` — "parallel evaluation of deterministic kernels. Non-authoritative by design, but reproducible, and the plan's acceptance criterion requires that R-Fabric on or off does not change semantic results."
- `algorithm` — "deterministic computation: parsing, traversal, matching, hashing, dependency analysis. The plan's own list for this coprocessor class."

The exclusions are recorded as deliberate: "Everything the plan lists as a coprocessor that can *disagree with itself* — LLM, human reviewer, external tool — is deliberately absent" (§ "Why these three origins").

The source ties this to `DECISION-001`, "which made model-backed execution legacy and non-canonical on the ground that a model emitting a value into a schema *authors* it. Escalation is that finding applied at the commit gate: a model may propose, and a person decides whether the proposal becomes institutional fact" (§ "Why these three origins").

### What the rule does not claim

The source is explicit that the rule "decides *routing*, not correctness. An escalated candidate is not suspect; it is unreviewed. Nothing in the gate claims a `REVIEW_REQUIRED` candidate is wrong" (§ "Consequences").

### Test coverage claimed

The source names the tests it is defended by, in `daale/tests/test_execution.py` (§ "Defended by"):

| Property | Test |
|---|---|
| A non-deterministic origin escalates | `test_a_non_deterministic_origin_escalates_rather_than_commits` |
| A deterministic origin validates | `test_a_deterministic_origin_validates` |
| An escalated candidate never reaches canonical state | `test_an_escalated_candidate_leaves_canonical_state_untouched` |

## Architectural Implications

The source draws the following consequences directly (§ "Consequences"):

- **Adding an origin to `DETERMINISTIC_ORIGINS` requires an approved decision.** The stated reason: "It grants canonical write authority to a new class of producer, which is not an implementation detail."
- **Phase 6 coprocessor adapters do not need this revisited.** "LLM, human and external-tool adapters escalate under the rule as written, which is the intended behaviour."
- **Escalation is routing, not a correctness verdict.** The source confines the claim to the gate itself: "Nothing in the gate claims a `REVIEW_REQUIRED` candidate is wrong" (§ "Consequences").
- **Escalation leaves a candidate outside canonical state.** "Escalation marks a candidate and leaves it outside canonical state" (§ "Consequences"). The source leaves the review and re-entry path unanswered and outside v0.

The decision also closes an open assumption in the implementation record: it supersedes assumption **G3** recorded in `docs/development/IMPLEMENTATION_LOG.md` for the DAALE v0 Phases 1–2 cycle, and the source states "G3 is closed by this note" (status block).

## Open Questions

The source records one gap, and records it deliberately (§ "Consequences"):

- **There is no review workflow.** In the source's words: "Who reviews, how they record the outcome, and how a reviewed candidate re-enters the gate are not answered here and are not part of v0. Named so the gap is visible rather than discovered later."

## Related Documents

- [YK-D-001 — Reasoning Execution Substrate](YK-D-001-reasoning-execution-substrate.md) — cited by the source as the finding this rule applies at the commit gate: `DECISION-001` "made model-backed execution legacy and non-canonical on the ground that a model emitting a value into a schema *authors* it" (§ "Why these three origins").
