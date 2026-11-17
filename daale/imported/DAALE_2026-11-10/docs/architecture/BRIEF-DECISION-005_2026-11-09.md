# DECISION-005: decision brief for the owner

**Decided 2026-11-09: option 1 (ratify), recorded in `DECISION-005.md`.** This brief is kept as the
record of the options that were considered. It was prepared on 2026-11-09 from the code in this
snapshot. Its file name deliberately does not start with `DECISION-`: the conformance lock reads
every `DECISION-*.md` file's first status line, and a second file with the same number would
overwrite the ADR's status.

## The question

What is DAALE, and who evaluates? When D-Core commits a decision, who produced the reasoning
behind it?

The original ADR offered two answers: **A**, DAALE evaluates for itself; **B**, DAALE calls the
frozen `choir_prototype` kernels. A working-copy ruling dated 2026-08-29 (kept here as
`DECISION-005_RULING_rfabric_evaluates.md.bak`) gave a third: **R-Fabric evaluates, D-Core
commits.** It was accepted only for the old working copy and says it does not amend the ADR.

## What the code did before the ruling

- **R-Fabric.** Six LLM kernels and an adversary produce findings. A deterministic policy engine
  turns the validated findings into a policy state (ADVANCE, HOLD, REJECT or ESCALATE). Model
  output enters only as findings; the engine never reads a model's confidence.
- **D-Core.** It has no evaluator. `D-Core/rfabric.py` translates a finished trace into a package
  and one candidate. D-Core never imports R-Fabric.
- **The commit gate** (`D-Core/execution/commit.py`, `run_gate`) validated the candidate and sent
  it to `REVIEW_REQUIRED` only when its origin was not in `DETERMINISTIC_ORIGINS`. `rfabric` is in
  that list, so an R-Fabric packet was committed automatically, **even when the packet itself said
  `requires_human_review`** (a field added on 2026-11-09 for runs with failed kernels).
- **DECISION-001** (approved 2026-08-04): deterministic kernels are the architecture;
  model-backed execution is legacy and not canonical; model calls are advisory only; replay and
  determinism checks are mandatory.

## The tension

The live product path is model-backed, which DECISION-001 calls non-canonical, yet D-Core treated
its output as deterministic. The policy step is deterministic given the recorded findings; the
findings are not. No replay check existed, so "deterministic" was asserted, not enforced.

## Options

1. **Ratify "R-Fabric evaluates; D-Core commits", with conditions.** (a) Amend DECISION-001 so
   model-backed kernels are admissible as advisory findings, replayable from the recorded trace;
   (b) add a replay check; (c) make D-Core route any packet flagged `requires_human_review` to
   `REVIEW_REQUIRED` instead of committing it; (d) keep the human-authority notice. No refactor.
2. **D-Core evaluates (original A).** Move the deterministic policy engine under D-Core; R-Fabric
   only proposes findings. The most literal fit for "workers propose, D-Core commits", but it
   reverses D-Core's deliberate "no evaluator" boundary and is a sizeable refactor.
3. **Frozen kernels evaluate (original B).** `choir_prototype` decides; R-Fabric becomes advisory
   research. Honours DECISION-001 literally; the live Gemma and Gemini path stops being the source
   of decisions.
4. **Leave it open and label every R-Fabric packet provisional.** Resolves nothing.

## Recommendation, and what was chosen

Option 1 was recommended and chosen. It describes the system that exists, keeps D-Core's boundary,
needs no refactor, and turns the two soft spots (replay and the ignored review flag) into checked
behaviour.
