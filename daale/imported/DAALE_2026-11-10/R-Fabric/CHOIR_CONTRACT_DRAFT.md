# CHOIR Contract Draft 0.1

This document is the minimal theory-facing contract required by the DAALE v0.1 reference implementation. It is deliberately marked **draft**. It does not claim to be the complete or canonical CHOIR specification.

## Layer boundary

- CHOIR defines the ontology, relations, invariants, and interpretation rules.
- DAALE executes a declared CHOIR contract and an application policy.
- YUKTI presents the resulting decision packet and workflow.
- The application supplies domain requirements and ordered decision rules.

DAALE must not silently introduce new CHOIR meanings. A contract change requires an explicit contract-version change.

## Core objects used by v0.1

- **Case**: the bounded institutional matter under analysis.
- **Decision stage**: the exact point in a workflow at which judgment is requested.
- **Claim**: a proposition evaluated against evidence.
- **Evidence item**: a source-bearing item with a stable identifier.
- **Policy requirement**: an application-defined condition relevant to the decision stage.
- **Evidence relation**: the relationship between one evidence item and one claim.
- **Requirement assessment**: whether a policy requirement is satisfied, not satisfied, or unknown.
- **Adversarial challenge**: an independent objection to a provisional analysis.
- **Unresolved contradiction**: evidence items that cannot presently be reconciled.
- **Decision packet**: a deterministic policy state plus traceable reasons and a human-authority notice.

## Evidence relations

Every evidence item must receive exactly one primary relation for every claim:

- `SUPPORTS`
- `WEAKENS`
- `CONTRADICTS`
- `CONTEXTUAL`
- `IRRELEVANT`

The complete relation matrix prevents a model from silently omitting inconvenient evidence.

## Requirement states

- `SATISFIED`: supplied evidence directly supports completion of the requirement.
- `NOT_SATISFIED`: supplied evidence directly establishes failure or non-completion.
- `UNKNOWN`: supplied evidence cannot establish either state.

An `UNKNOWN` state is not equivalent to failure.

## Invariants enforced by DAALE v0.1

1. Every claim, evidence item, requirement, and challenge has a unique stable identifier.
2. Model-generated references must resolve to identifiers present in the case or policy.
3. Every claim must classify every evidence item exactly once.
4. A satisfied or failed requirement must cite at least one supplied evidence item.
5. Missing evidence must be expressed through an explicit policy requirement, not a free-form invented checklist.
6. Adversarial disagreement is retained in the decision packet.
7. Model outputs are provisional findings and never the institutional decision.
8. The policy state is selected by an ordered deterministic rule set.
9. Identical validated findings and policy produce the same policy state.
10. The decision packet always states that human institutional authority is required.

## Confidence

DAALE v0.1 intentionally excludes model self-reported confidence from the policy engine. A model saying `0.8` is not evidence that a conclusion is 80% reliable. A future CHOIR specification may define calibrated uncertainty semantics; implementation must not invent them prematurely.

## Human authority

`ADVANCE`, `HOLD`, `REJECT`, and `ESCALATE` are deterministic policy states produced by DAALE. They are not autonomous institutional decisions. The authorized human or committee retains final authority.

