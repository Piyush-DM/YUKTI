# Canonical Definition of DAALE

| | |
|---|---|
| **Document ID** | YK-D-005 |
| **Source** | `docs/architecture/DECISION-005_canonical_definition_of_daale.md` (DECISION-005) |
| **Series** | Architecture Decisions |
| **Revision** | A |
| **Status** | Superseded |
| **Last Updated** | 2026-08-23 |

## Abstract

This ADR records that the question *what DAALE is* was open and deliberately left unanswered, and that no implementation was permitted to depend on any assumption about DAALE until the ADR was accepted (stated in the unheaded status paragraph that opens the source). It records five accounts of DAALE — drawn from the repository, the research corpus and two independent architectural reviews — which the source states "do not agree, and each has been treated as authoritative by someone," and records that the modules named in the last of those accounts do not exist in this repository. The conclusion the source draws from that verification is hedged: the review is "a competent analysis of a **different or hypothetical** DAALE," and "that is not a criticism of it — its diagnosis of the missing canonical semantics converges with this repository's own recorded governance gap" (§ "Why it is open"). **This ADR no longer governs.** Per the governance block ruled 2026-08-22, `DECISION-005` is **INVALIDATED** — not approved and not rejected, because "the question was never answered, the decision was retired" — and its **replacement ruling is recorded as "not yet recorded"** (§ "Current governance", § "Governance record"). No replacement is on record; the evaluator boundary in `daale/` therefore stands unchanged until a superseding architectural artifact exists.

## Research Question

The source states its question explicitly under the heading "The question":

> "What is DAALE, and what is its relationship to CHOIR, to `choir_prototype/`, and to any future reference implementation?"

The document is explicit that it does not answer this question. Its stated purpose is procedural: "This record exists to stop a question being answered by accident. It is deliberately not answered here" (unheaded status paragraph, immediately preceding § "The question").

## Finding

### 1. Governance status: invalidated, not decided

The current governance block, ruled 2026-08-22, is preserved verbatim in the source:

```
DECISION-005
Historical status at closure: Open / Not accepted
Current governance status:    INVALIDATED
Reason:                       no longer governing
Replacement ruling:           not yet recorded
```

The source draws a distinction it treats as load-bearing: "Invalidation is not a verdict. This ADR is **not** marked `Approved` and **not** marked `Rejected`, because neither happened: the question was never answered, the decision was retired. Collapsing those two layers would destroy the record of what was actually true at closure" (§ "Current governance").

The ruling is scoped narrowly and negatively. In the source's own words: "**The ruling does not select option A or B, and introduces no replacement evaluator architecture.** The evaluator boundary in `daale/` therefore stands unchanged until the architectural artifact that supersedes this ADR is recorded" (§ "Current governance"). The governance block also states that everything below it "is preserved exactly as written and is *historical record* — the status line, the options, and the constraint section state what was the case at closure, not what is the case now."

The historical status at closure, stated in the body, was: "**Status: Open. Not accepted.** Raised under Authorization 5. **No implementation shall depend on assumptions regarding DAALE until this ADR is accepted.**"

### 2. Why the question was open: the recorded accounts do not agree

The source records that "The repository, the research corpus and two independent architectural reviews do not agree, and each has been treated as authoritative by someone" (§ "Why it is open"). The table it gives is reproduced here as recorded:

| Source | What it says DAALE is |
|---|---|
| `daale/` in this repository | A scaffold. Configuration, environment diagnostics, logging, report paths, and ontology modules that are docstrings with no behaviour. **No reasoning logic.** |
| `README.md` | "DAALE implementation scaffold… DAALE currently contains no reasoning logic." |
| `choir_prototype/README.md` | "**This is not YUKTI and not DAALE architecture.**" |
| `CHOIR_v0.1_RESEARCH_FREEZE.md` §4.4 | Records the relationship as **an open question**: whether the prototype graduates into DAALE, or DAALE is a separate target, is undecided. |
| Independent review, 2026-08-06 | "DAALE is its reference implementation" — describing an engine with `authority/lock.py`, `engine/core.py`, `evaluators.py`, a `BasisDemoEvaluator`, and five passing tests. |

### 3. The review describes a codebase that does not exist here

The source records a verification result, dated 2026-08-06: "**None of the modules in that last row exist in this repository.**" Specifically, `authority/lock.py`, `engine/core.py`, `experiments/runner.py`, `trace/events.py`, `provenance/model.py`, `judgment/basis.py`, `contract/` and `evaluators.py` "are all absent, `daale/` contains no `evaluate`, no `judgment` and no `INSUFFICIENT_BASIS`, and its suite is 12 tests rather than 5" (§ "Why it is open").

The conclusion drawn is deliberately hedged, and the hedge is preserved here: "The review is therefore a competent analysis of a **different or hypothetical** DAALE. That is not a criticism of it — its diagnosis of the missing canonical semantics converges with this repository's own recorded governance gap. But it cannot be read as a description of this codebase, and its prescriptions were written for the codebase it describes."

### 4. What was at stake: an unaccepted definition as a route to un-freezing the engine

The source states that "The prescriptions differ depending on the answer, and one of them is dangerous" (§ "What is at stake").

The review recommends "a **configurable hybrid evaluator** — forward chaining, backward chaining, certificate production and optionally Rete, behind one evaluator interface." The source concedes the conditional case for it: "If DAALE is the engine and DAALE is greenfield, that is reasonable advice."

The alternative reading is the one it flags as dangerous: "If DAALE is *this* repository, adopting it would replace CHOIR v0.1 outright: the engine here is four deterministic kernels and a synthesizer, hash-pinned, frozen, and carrying the project's only measured result." The same objection is applied to the review's Pydantic-strict recommendation, on the ground that "`choir_prototype/` is standard-library only *by design*, because that is what makes its determinism auditable."

The section closes with the framing that motivates the ADR's existence: "An unaccepted definition of DAALE is thus not a documentation gap. It is a live route to un-freezing the engine by implication."

### 5. Options recorded, explicitly unassessed

The source records four options "so the ADR has something to accept," and states plainly: "No recommendation is made" (§ "Options, unassessed").

| Option | Statement as recorded |
|---|---|
| **A** | **DAALE is the future reference implementation**, and `choir_prototype/` is the V0.1 evidence artefact it will supersede. |
| **B** | **DAALE is a separate architectural target**, and `choir_prototype/` is and remains the reference implementation of CHOIR. |
| **C** | **DAALE is retired as a name**, its scaffold folded into whichever component ends up owning execution. |
| **D** | **DAALE is the product-side engine boundary**, and the workspace's `analysis.py` is already an early form of it. |

None of A–D was assessed, and the 2026-08-22 ruling did not select among them.

### 6. The constraint that held while the ADR was open

The source records the following "as the operative rule, not as advice" (§ "Constraint while this is open"):

- No implementation may assume any of A–D.
- Nothing may be moved into or out of `daale/` on the basis of an assumed answer.
- The Material Snapshot layer (`DECISION-006`) is deliberately built with **no DAALE dependency of any kind**, which is what allowed this cycle to proceed while this ADR is open.

Under § "Approval Status" the source records only: "Open. Requires architect acceptance."

### 7. Governance record

The source states that this record is "Appended, never edited. Every section above is preserved as written," and carries two entries:

| Date | Event |
|---|---|
| 2026-08-06 | Raised under Authorization 5. Status at raising: open, not accepted. |
| 2026-08-22 | **INVALIDATED.** No longer governing. Not approved and not rejected — the question was never answered. No replacement ruling recorded, and evaluator option A or B is not selected. |

### Status statement required of a superseded ruling

This publication is issued at status **Superseded**: the ruling no longer governs. The source records **no replacement ruling** — the governance block gives "Replacement ruling: not yet recorded," and the 2026-08-22 governance entry repeats that "No replacement ruling recorded." Nothing in the source names a successor document.

## Architectural Implications

The implications below are those the source itself draws. They must be read against the source's own posture: its options are recorded under the heading "Options, unassessed," "No recommendation is made," and the ADR "is deliberately not answered here." Where the source argues conditionally — under the antecedent "If DAALE is *this* repository" — the condition is one of the four unassessed readings, and is carried through below rather than dropped.

**The evaluator boundary in `daale/` is unchanged by the invalidation.** The source states this directly: because the ruling "does not select option A or B, and introduces no replacement evaluator architecture," the boundary "stands unchanged until the architectural artifact that supersedes this ADR is recorded" (§ "Current governance").

**Replacement of CHOIR v0.1 by implication is recorded as a hazard, not forbidden by a rule.** The source characterises the engine as "four deterministic kernels and a synthesizer, hash-pinned, frozen, and carrying the project's only measured result," and states that *if* DAALE is this repository, adopting the review's hybrid-evaluator prescription "would replace CHOIR v0.1 outright." It issues no prohibition on that basis; what it states is that "an unaccepted definition of DAALE is thus not a documentation gap. It is a live route to un-freezing the engine by implication" (§ "What is at stake"). The source's operative rules are only the three bullets under § "Constraint while this is open," reproduced in §6 above.

**`choir_prototype/` is standard-library only by design.** The source gives the reason as auditable determinism. Its objection to the review's Pydantic-strict recommendation stands under the same antecedent — "If DAALE is *this* repository" — and the ADR declines nothing, since it makes no recommendation and answers no question (§ "What is at stake", § "Options, unassessed").

**The Material Snapshot layer was built with no DAALE dependency of any kind.** The source records this as the deliberate mechanism that allowed the development cycle to proceed while DECISION-005 was open (§ "Constraint while this is open"), and attributes it to `DECISION-006`.

**Governance status is recorded in two layers, not collapsed into one.** The source keeps historical status at closure ("Open / Not accepted") separate from current governance status ("INVALIDATED"), on the stated ground that collapsing them "would destroy the record of what was actually true at closure" (§ "Current governance").

**The review's inapplicability here is settled by module-level verification, not by argument.** The source lists eight absent modules and a test-count mismatch (12 tests rather than 5), and draws from that a claim scoped to this one review: it "cannot be read as a description of this codebase, and its prescriptions were written for the codebase it describes" (§ "Why it is open"). The source states no general principle about architectural reviews.

## Open Questions

- **The canonical question is unanswered.** "What is DAALE, and what is its relationship to CHOIR, to `choir_prototype/`, and to any future reference implementation?" was never answered; the decision was retired instead (§ "The question", § "Current governance").
- **Options A–D are unassessed.** The source records them explicitly as "Options, unassessed," makes no recommendation, and the 2026-08-22 ruling selects none of them.
- **No replacement ruling exists.** "Replacement ruling: not yet recorded" (§ "Current governance"); "No replacement ruling recorded" (§ "Governance record"). No superseding architectural artifact is named.
- **No replacement evaluator architecture is introduced.** The ruling introduces none, leaving the evaluator boundary undefined beyond its current state (§ "Current governance").
- **The recorded disagreement is not resolved.** The source records that the repository, the research corpus and two independent architectural reviews "do not agree, and each has been treated as authoritative by someone"; it documents the disagreement without adjudicating it (§ "Why it is open").
- **`CHOIR_v0.1_RESEARCH_FREEZE.md` §4.4 leaves the prototype/DAALE relationship undecided** — whether the prototype graduates into DAALE, or DAALE is a separate target (§ "Why it is open").
- **The verification of absent modules is dated 2026-08-06** and is stated as of that date; the source records no later re-verification.

## Related Documents

- [YK-D-006 — The Material Snapshot Layer](YK-D-006-the-material-snapshot-layer.md) — cited in § "Constraint while this is open" as `DECISION-006`, the layer deliberately built with no DAALE dependency of any kind.
