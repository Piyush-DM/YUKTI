# DAALE v0 — Closure and Freeze

**Status:** CLOSED — 2026-08-14.
**Type:** Engineering closure and freeze. Not a specification.
**Supersedes:** nothing. It sits above the DAALE v0 record and indexes it.
**Governs:** what DAALE v0 may be assumed to provide, and what changing it costs.

---

## 1. What this closes

DAALE v0 was authorized to proceed toward completion under the existing
execution plan, with a finite definition of done. That definition is met, and
this note records the result.

| Area | State at closure |
|---|---|
| Phase 0 — conformance lock | Complete. Accepted as the v0 execution baseline. |
| Phase 1 — single-threaded D-Core | Complete to the `DECISION-005` boundary. |
| Phase 2 — commit protocol | Complete. |
| Eight unexercised commitments | Classified, five categories, each citing its source. |
| `E12` | Preserved as an evidence discrepancy. Not closed. |
| Escalation rule | Codified as `DECISION-007`. Assumption G3 closed. |
| §14 top-level `yukti/` | Not adopted. `DECISION-003` stands. |
| CHOIR v1 | Not present in this repository. Nothing backported. |

v0 is closed. Phases 3–8 are not in it.

---

## 2. What DAALE v0 is

A **canonical control plane** and the conformance machinery that keeps it honest.
It validates, names, orders, versions, commits, traces and terminates. It does
not reason.

That is the whole of it, and it is deliberate: the plan's design rule for this
component is "the D-Core owns authority, not necessarily compute volume."

```
daale/
  conformance/   the frozen CHOIR v0.1 commitments, made checkable
  execution/     the D-Core, its state store, its trace, and the commit gate
```

Neither package imports `choir_prototype` or `applications`. Both assert that
mechanically, in a subprocess, rather than claiming it.

---

## 3. What was built

### 3.1 Conformance (Phase 0)

The twenty-eight frozen `CHOIR_v0.1_RESEARCH_FREEZE.md` §3 commitments
(E1–E13, A1–A11, X1–X4) as a machine-readable register, and a lock that resolves
every piece of evidence they rest on.

```
28 commitments -- 20 conforming, 8 unexercised, 0 unresolved
```

It is a **tripwire, not a second opinion.** It does not re-run the reasoning:
`--replay` and the prototype suite already do, and a second answer to the same
question is worse than none. It catches what those cannot see — a frozen
commitment whose evidence has quietly stopped existing.

This gave the traceability chain its first real upstream end. Every
`choir/specifications/SPEC-*.md` file is still empty; §3 is not, and it is
accepted frozen content.

### 3.2 Execution (Phases 1–2)

| Module | What it holds |
|---|---|
| `identity.py` | Execution identity, computed over the **input** at full fidelity. |
| `contract.py` | CHOIR contract validation: A2 shape, uniqueness, referential integrity. |
| `state.py` | The Reasoning State Store. Six areas, versioned, lease-guarded. |
| `trace.py` | Append-only ordered events. No clock. |
| `commit.py` | The candidate lifecycle and the seven-check gate. |
| `dcore.py` | The D-Core. |

The invariant the whole package serves: **anything may propose; only the D-Core
commits.** A rejected or escalated candidate leaves canonical state untouched.

### 3.3 Classification

The eight unexercised commitments, each carrying the source that says why it is
unimplemented.

| Category | Commitments |
|---|---|
| `research-open` | E4, E5, E7 |
| `prototype-limit` | E6 |
| `specified-not-implemented` | E3, E11 |
| `decision-required` | E10 |
| `evidence-discrepancy` | E12 |

Classified, **not queued.** Four are §4 research programmes, and research freeze
§9 forbids partially implementing one to make a current problem easier.

---

## 4. The defining limit: the `DECISION-005` boundary

The D-Core implements eight of the plan's nine listed responsibilities. The
ninth — emitting a judgment — is absent, and its absence is the shape of v0.

A judgment requires evaluated results. Evaluation requires deciding **who
evaluates**: whether DAALE calls the frozen prototype's kernels, or evaluates
for itself. Those are options **B** and **A** of `DECISION-005` verbatim, and
there is no neutral third answer, because "who evaluates" is precisely what that
ADR asks.

**There is no evaluator and no placeholder for one.** A stub raising
`NotImplementedError` would still assert that the evaluator belongs inside
DAALE, which is itself one of the answers.

This is not a gap in v0. It is v0's boundary, and the candidate-to-commit
protocol is what makes the component coherent without crossing it: a commit
authority never needs to evaluate anything. It takes candidates from whoever
produced them and decides admissibility.

Every `ExecutionSummary` reports `emits_judgment=False` and carries the reason,
so a completed execution cannot be mistaken for an adjudicated one.

---

## 5. What is frozen

Frozen at the **architecture** level, in the sense `choir_prototype/FROZEN.md`
uses the word — not the code as text.

| Frozen | Why |
|---|---|
| Execution identity is derived from inputs, never from output | The `DECISION-006` collision. An identifier derived from what a computation emitted collides when the computation does not observe part of its input. |
| Execution identity is order-sensitive | Downstream identifiers are positional. An order-insensitive digest would be coarser than the thing it must be finer than. |
| Canonical writes require a lease; executions are serialised | "R-Fabric can propose; D-Core alone can commit." Two writers is nondeterminism. |
| Stale reads are refused, never applied | The silent overwrite is the failure the protocol exists to prevent. |
| The seven gate checks, and their names | "Rejected" is not an audit record; "rejected by `required-provenance-present`" is. |
| A check that cannot run reports `INACTIVE`, never `PASSED` | A gate that passes vacuously looks stronger than it is. |
| The escalation rule is an allow-list | `DECISION-007`. An unnamed origin must escalate, not commit. |
| The trace is append-only and carries no clock | Two runs of the same package must be comparable event for event. |
| Neither package imports the engine | What lets v0 exist while `DECISION-005` is open. |
| Unexercised commitments are never reported as conforming | An unchecked commitment must not read as a passing one. |

**The freeze is a tripwire, not a prohibition.** Reconciliation against CHOIR v1
is expected to change things here. It exists so that changing them is a
deliberate act with a version attached, rather than something that happens by
accident.

### 5.1 How the freeze is enforced

No new machinery was built for it. Three mechanisms already in the repository
carry it:

| Mechanism | Command | Catches |
|---|---|---|
| Conformance lock | `python -m daale conformance` | A frozen commitment whose evidence has gone missing. Exits non-zero. |
| Test suite | `python -m unittest` | Every property in the table above. 77 tests for `daale/`, 237 for the repository. |
| Boundary guard | `test_the_d_core_has_no_evaluator` | The `DECISION-005` boundary eroding one convenient method at a time. |

Gate at closure: `ruff check`, `ruff format --check`, 237 unittest, `compileall`,
`mypy --strict` across 44 files. `--frozen` INTACT, `--audit` portability 1.00.

---

## 6. What v0 deliberately does not do

Named so it is clear these were considered and excluded, not forgotten.

- **Reason.** No evaluator, no kernels, no synthesis, no judgment.
- **Plan.** No execution planner. Gate check 4 is `INACTIVE` and says so.
- **Parallelise.** No R-Fabric. There is nothing to parallelise without an
  evaluator.
- **Fork.** No shadow or replay lanes. The snapshot and lease machinery they
  will need is in place; the lanes are not.
- **Adapt.** No coprocessor adapters. The gate already routes by origin.
- **Review.** Escalation marks a candidate and stops. Who reviews it, how the
  outcome is recorded, and how it re-enters the gate are unanswered.
- **Persist.** The state store is in-memory. Durability is not a v0 concern.

---

## 7. Carried out of v0, unresolved

These leave v0 open, and none is closed by this note.

1. **`DECISION-005` is open.** The evaluator choice. Everything in Phases 3–5
   waits on it, and the exact dependency is recorded in §4 above.
2. **`E12` is an evidence discrepancy.** `CHOIR_v0.1_RESEARCH_FREEZE.md` §3.1
   marks "Nothing is deleted" as demonstrated; this repository cites nothing for
   it. Either the evidence exists and was never recorded, or the status is
   optimistic. Both are adjudications about the freeze. It was not closed by
   finding something plausible to cite, because that would manufacture the
   traceability the lock exists to measure.
3. **Seven commitments remain unexercised** beyond `E12`, classified in §3.3.
   Four are research programmes.
4. **No review workflow** behind the escalation rule. See `DECISION-007`.
5. **The v0 plan itself is recorded nowhere in this repository.** It exists as
   an external document whose own status line reads "DAALE implementation
   proposal". Every phase was implemented under direct architectural
   instruction, which the rules permit. Its disposition is still unrecorded.

---

## 8. Reconciliation against CHOIR v1

Out of scope for v0 and deliberately not begun.

**No CHOIR v1 exists in this repository.** Verified at closure: the only `v1`
matches in the tree are website, film and motion-system assets. Nothing was
backported, and the instruction not to backport was satisfied by absence rather
than by restraint.

When reconciliation happens, the parts of §5 most likely to move are the
conformance register — which transcribes v0.1 §3 and would need a v1 counterpart
rather than an edit — and the contract in `contract.py`, which transcribes
commitment A2. Both are transcriptions of a frozen source, so both change by
version bump, not by amendment.

---

## 9. Closing statement

DAALE v0 is a control plane that cannot reason, and that is the point. It was
built to the edge of an open architectural question and stopped there with the
question intact.

The next act is not Phase 3. It is a ruling on `DECISION-005`.
