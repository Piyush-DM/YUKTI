# Judgment Supersession

| | |
|---|---|
| **Document ID** | YK-D-004 |
| **Source** | `docs/architecture/DECISION-004_judgment_supersession.md` (DECISION-004) |
| **Series** | Architecture Decisions |
| **Revision** | A |
| **Status** | Published |
| **Last Updated** | 2026-08-23 |

## Abstract

This document records an approved and implemented architecture ruling: institutional
history is append-only, and a committee decision remains permanently bound to the exact
judgment that existed when that decision was recorded (§ Ruling). It was ruled by the
architect in response to a verified defect in which re-running an analysis overwrote a
judgment record in place, leaving a ledger entry pointing at a digest nothing on disk
matched (§ Decision). The ruling selects supersession over the alternatives of archiving
and freezing, and the source records the resulting data model, invariants, tests, and
costs (§ Options put to the architect, § Implementation, § Invariants, and where they are
defended, § Consequences).

## Research Question

The source document does not pose a research question; it is an architecture decision
record. The question put to the architect was what a system should do when a case is
re-analysed after a committee decision has already been recorded against a prior judgment
— specifically, how to stop re-analysis from destroying the resolvability of decisions
already taken (§ Decision, § Options put to the architect). The source frames the stakes
in its own terms: the failure "does not produce a wrong answer — it destroys the ability
to defend a right one, which is the entire reason the product exists" (§ Decision).

## Finding

### The defect

A committee decision cites the record digest of the judgment it was taken against. Before
this change, re-running an analysis **overwrote that record in place**. The ledger entry
then pointed at a digest nothing on disk matched, and the decision silently became
undefendable (§ Decision).

The source states that this was verified rather than suspected, and records the verifying
output (§ Decision):

```text
decision cites digest : 1f8b7bfeed57e1b4
on disk after re-run  : 344d3b6d8840491d
DECISION VERIFIABLE   : False
```

The source classes this as "the most severe class of failure the product can have"
(§ Decision).

### The options and the ruling

Three options were put to the architect (§ Options put to the architect):

| Option | What it does |
|---|---|
| **Archive** | Copy the old record aside before overwriting, so decided judgments stay resolvable. |
| **Freeze** | Once a case is decided, refuse further analysis until the decision is explicitly reopened. |
| **Supersede** | A new analysis creates a *new* judgment. Previous decisions keep referencing the judgment they were made against. Nothing is overwritten and nothing is locked. |

The ruling was **Supersede**, stated by the architect (§ Ruling):

> A committee decision must always remain permanently bound to the exact
> judgment that existed when that decision was recorded. Re-analysis must never
> invalidate historical decisions. Do not freeze cases. Do not overwrite
> history. Institutional history is append-only.

The source records the reasoning for the two rejections. Freezing was rejected outright:
a case that cannot be re-analysed after a decision is a case an institution cannot keep
working on, and deferral is a first-class outcome in this product. Archiving was rejected
because it makes the *current* record primary and history a side effect; supersession
makes every judgment equally real and equally permanent (§ Ruling).

### What was implemented

The source records the following implementation (§ Implementation):

- `JudgmentRecord` on the case carries `judgment_id`, `record_digest`, `recorded_on`, and
  `superseded_by`. It is append-only; a new analysis marks the previous record superseded
  and appends its own.
- Artifacts moved from `reports/workspace/<case>/` to
  `reports/workspace/<case>/judgments/<judgment-id>/`, written once, never rewritten. Each
  judgment retains the exact document it saw.
- `LedgerEntry` gains `judgment_id`. The store rejects a decision citing a judgment the
  case never reached.
- Decisions can only be recorded against the judgment in force. The source's stated reason:
  recording one against a superseded judgment "would be minuting a meeting into the past".
- `analysis.verify_ledger` checks that every decision still resolves to artifacts on disk
  carrying the cited digest. The workspace shows the outcome beside each ledger entry,
  including a visible failure state. The source states plainly: "There is no quiet failure."
- An analysis reproducing the current judgment's digest returns that judgment rather than
  creating a duplicate. The source's stated justification is that the engine is
  deterministic, so an identical digest means the material reached the same conclusion, and
  recording it twice would put an event in institutional history that never happened.

Analysis runs in a scratch directory and the finished artifacts are moved into place in one
step, so a failed run cannot leave a half-written judgment behind (§ Implementation).

### Invariants and their defending tests

The source names seven invariants and the test defending each, in `TestSupersession` in
`applications/investment/workspace/tests/test_workspace.py`
(§ Invariants, and where they are defended):

| Invariant | Test |
|---|---|
| Historical decisions remain permanently verifiable | `test_a_decision_survives_re_analysis` |
| Historical record digests always resolve | `test_every_judgment_ever_reached_keeps_its_artifacts` |
| Re-analysis never invalidates prior decisions | `test_decisions_against_different_judgments_all_resolve` |
| Provenance remains complete | `test_the_material_that_produced_each_judgment_is_kept` |
| Append-only institutional history | `test_history_is_append_only` |
| A superseded judgment stays fully readable | `test_a_superseded_judgment_still_reads_in_full` |
| Determinism does not manufacture history | `test_re_running_unchanged_material_creates_no_new_judgment` |

### Costs the source accepts

The source records three consequences (§ Consequences):

- Storage grows with every distinct analysis. The source calls this deliberate and cheap —
  a judgment is roughly 70 KB — and states that retention "is an institutional policy
  question, not an engineering one, and is not answered here".
- The case store's on-disk layout changed, and there is **no migration path**. The source
  states the reason: the only data in the old layout was generated development data, and
  records the admission that "A deployed system would have needed one."
- `Case.status()` no longer takes an `analysed` argument, because judgment history lives on
  the case and status is derived entirely from the case record.

### Status of this ruling

The source records its own status as "Approved 2026-08-06. Implemented." (§ header) and
repeats "Approved and implemented 2026-08-06" (§ Approval Status). It is an approved and
implemented ruling. The source states it is recorded because the ruling "is
load-bearing for every future product decision about institutional history" (§ header).

## Architectural Implications

The source document does not name CHOIR or DAALE. The constraints below are the ones the
source itself draws, stated in its own terms — the case store, the ledger, the judgment
record, and the workspace.

**Append-only history is a binding constraint, not a preference.** The architect's ruling
forbids overwriting history and forbids freezing cases (§ Ruling). Any later design that
would mutate a judgment record in place, or block re-analysis of a decided case, is ruled
out by this decision. The source states the ruling is load-bearing for every future product
decision about institutional history (§ header).

**Decisions bind to a judgment identity, not to a case.** Because `LedgerEntry` carries
`judgment_id` and the store rejects a decision citing a judgment the case never reached
(§ Implementation), any component recording a decision must know which judgment is in force
and must record against that one. Decisions can only be recorded against the judgment in
force (§ Implementation).

**Artifacts are write-once and per-judgment.** The move to
`reports/workspace/<case>/judgments/<judgment-id>/`, written once and never rewritten,
means each judgment retains the exact document it saw (§ Implementation). Provenance
completeness is one of the seven defended invariants
(§ Invariants, and where they are defended).

**Verification is a first-class, visible operation.** `analysis.verify_ledger` checks that
every decision still resolves to artifacts carrying the cited digest, and the workspace
surfaces that outcome beside each ledger entry including a visible failure state
(§ Implementation). The source's stated commitment — "There is no quiet failure" — makes
silent unverifiability unacceptable rather than merely undesirable.

**Determinism is relied upon.** The de-duplication behaviour — an analysis reproducing the
current judgment's digest returns that judgment rather than creating a new one — rests on
the stated premise that the engine is deterministic (§ Implementation). That premise is
asserted in the source, not demonstrated in it.

**Deferral is preserved as an outcome.** Freezing was rejected in part because deferral is
a first-class outcome in the product and a decided case must remain workable (§ Ruling).

## Open Questions

- **Retention policy is unanswered.** Storage grows with every distinct analysis; the
  source states that retention "is an institutional policy question, not an engineering
  one, and is not answered here" (§ Consequences).
- **No migration path exists for the layout change.** The source records that none was
  written because the only data in the old layout was generated development data, and
  admits that "A deployed system would have needed one" (§ Consequences).
- **Determinism of the engine is asserted, not demonstrated here.** The de-duplication rule
  depends on it, and the source offers no measurement or proof of it within this document
  (§ Implementation).

## Related Documents

The source document itself cites no sibling publications; it cites only the test module
`applications/investment/workspace/tests/test_workspace.py`
(§ Invariants, and where they are defended). The relationships below are recorded in the
sibling documents named, not in this source.

- [YK-D-003 — Product Application Architecture](YK-D-003-product-application-architecture.md) — its source document, DECISION-003, points to DECISION-004 for the supersession ruling.
- [YK-D-006 — The Material Snapshot Layer](YK-D-006-the-material-snapshot-layer.md) — its source document, DECISION-006, records that supersession was subsequently re-keyed on material identity.
