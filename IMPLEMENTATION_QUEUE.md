# DAALE Implementation Queue

This file is the working backlog for implementation engineering. It records
repository-health work that can be done without inventing architecture or
execution logic.

Inspect this file after each completed task. From the repository organization
freeze onward, only maintenance work is permitted unless an explicit
specification or direct architectural instruction authorizes implementation
work.

Last updated: 2026-08-13

Current validation gate status: Passed on 2026-08-13.

Narrative record of implementation work, including assumptions and open review
points, is kept in `docs/development/IMPLEMENTATION_LOG.md`. This file remains
the backlog.

**Known governance gap.** `choir_prototype/`,
`applications/investment/prototype_risk_rik/` and
`applications/investment/vertical_slice/` contain runtime behavior that was
implemented while every `choir/specifications/SPEC-*.md` file is empty. Under
the rules below, that work was not authorized by an approved specification.
Recorded here rather than resolved: the rule and the repository disagree, and
which one gives way is an architectural decision, not a maintenance task.

The vertical slice was authorized by direct architectural instruction, which the
rules below permit as an alternative to a specification. It widens the gap
rather than creating a new kind of one.

## Operating Rules

- Repository organization is frozen unless explicitly instructed otherwise.
- Preserve existing architecture names.
- Do not implement runtime behavior without an approved specification.
- Do not rename architectural components without an approved decision.
- Do not introduce new documentation systems, dashboards, reporting systems,
  architectural components, runtime logic, execution logic, schedulers, kernels,
  providers, or cognitive behavior.
- Drive all implementation work from explicit specifications or direct
  architectural instructions.
- If no implementation work exists, perform repository maintenance only.
- If a task requires an architectural choice, stop and write a decision note in
  `docs/architecture/`.
- Every generated file must contain meaningful documentation.
- Every iteration must end with the validation gate below.

## Validation Gate

Run these commands from the repository directory every iteration:

```powershell
ruff check .
ruff format --check .
python -m unittest
python -m compileall .
```

If any command fails, stop the queue work, fix the failure if it is within the
implementation-engineering boundary, then run the full gate again.

See `docs/development/VALIDATION.md` for developer-tool installation and
Windows PATH notes.

## Continuous Tracks

### Track A: Repository Engineering

Continuous work that protects repository stability and developer experience.

- [x] Add root repository README with current scaffold boundaries.
- [x] Add Python cache and local environment hygiene to `.gitignore`.
- [x] Add architecture decision-note guidance.
- [x] Add explicit developer tooling dependency record.
- [ ] Maintain existing README quality when files are changed.
- [ ] Check existing documentation for broken links and stale references.
- [ ] Add CI only if explicitly instructed.

### Track B: Skeleton Engineering

Document architectural objects before implementation.

- [x] Add docstrings to existing DAALE ontology modules.
- [x] Add ontology skeleton documentation for current module boundaries.
- [ ] Frozen until explicit specifications or direct architectural instructions
  require additional skeleton documentation.

### Track C: Traceability

Build the chain from specifications to implementation artifacts.

- [x] Add traceability documentation scaffold.
- [x] Add traceability matrix scaffold.
- [ ] Populate traceability rows only after source specifications contain
  accepted content.
- [ ] Maintain existing traceability files when referenced artifacts change.
- [ ] Add benchmark-column conventions only after benchmark architecture is
  approved and implementation is explicitly instructed.

## Priority Queue

### Priority 1: Repository Stability

- [x] Establish standard validation gate.
- [x] Make Ruff an explicit developer tooling dependency.
- [ ] Keep validation gate passing.
- [ ] Keep repository organization frozen unless explicitly instructed.

### Priority 2: Documentation

- [x] Document repository purpose and constraints.
- [x] Document architecture decision process.
- [x] Document repository health dashboard process.
- [ ] Maintain existing documentation quality when files are touched.

### Priority 3: Architecture Traceability

- [x] Define canonical traceability chain.
- [x] Create traceability matrix file.
- [ ] Link approved SPEC content to DAALE skeletons when SPEC files are filled.

### Priority 4: Testing Framework

- [x] Add standard-library smoke tests for ontology module importability.
- [ ] Maintain existing scaffold tests when Python files change.

### Priority 5: Kernel Interfaces

- [ ] Blocked until approved architecture identifies kernel interface names and
  responsibilities.

### Priority 6: Runtime Interfaces

- [ ] Blocked until approved architecture identifies runtime interface names and
  responsibilities.

### Priority 7: Execution Engine

- [x] First complete vertical slice: one document to a rendered report, every
  stage persisted (`applications/investment/vertical_slice/`). Built by direct
  architectural instruction; composes frozen V0.1 components and adds document
  intake only.
- [x] `DECISION-002` approved and broadened 2026-08-06. Product-generated
  serialised packet documents are authorised. Documents may represent packets;
  they may not interpret them. Prose plus extraction remains unapproved.
- [x] **DAALE v0 Phase 0 — conformance lock** (`daale/conformance/`). The 28
  frozen §3 commitments as a machine-readable register, every citation resolved
  mechanically. 28 commitments: 20 conforming, 8 unexercised, 0 unresolved.
  Built under direct architectural instruction, with no `DECISION-005`
  dependency: the commitments are CHOIR's and identical under all four options
  that ADR leaves open.
- [ ] **DAALE v0 Phase 1 — single-threaded D-Core. Blocked on `DECISION-005`.**
  The dependency is exact: a deterministic executor must either call the frozen
  prototype's kernels or evaluate for itself, and those are options B and A of
  that ADR verbatim. Nothing else in the plan is blocked by it.
- [ ] Blocked until approved execution behavior exists for anything beyond the
  above.

### Priority 8: Product Application

Added when the engine was declared stable and the product instruction was
issued. Product work is governed by
`docs/architecture/DECISION-003_product_application_architecture.md`.

- [x] YUKTI application V1: case register, intake, diligence schedule,
  institutional judgment, audit trail, decision ledger
  (`applications/investment/workspace/`).
- [x] `DECISION-003` approved 2026-08-06, including "Review areas" as canonical
  product terminology. Research freeze section 5 applies to the engine, not to
  product layers.
- [x] Judgment supersession (`DECISION-004`). Decisions bind permanently to the
  judgment they were recorded against; institutional history is append-only.
- [x] Material Snapshot layer (`DECISION-006`). Institutional material has an
  immutable identity; supersession keys on material; ledger verification
  covers reasoning and material as separate claims.
- [ ] **Blocked on `DECISION-005`** (open ADR): anything that assumes a
  definition of DAALE, or moves code into or out of `daale/`.
- [ ] Retire `applications/investment/prototype-ui/`. Now unblocked: the rename
  it was waiting on is approved. Superseded by the workspace; removal touches a
  passing test suite, so it is scheduled work.
- [ ] Authentication and access control. Required before the workspace records
  real institutional decisions attributed to named people.
- [ ] Concurrent-edit handling. Material is replaced wholesale, so two analysts
  editing one case overwrite each other silently.
