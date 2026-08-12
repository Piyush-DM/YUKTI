# Decision: judgment supersession

**Status: Approved 2026-08-06. Implemented.** Ruled by the architect in response
to a verified defect; recorded here because the ruling is load-bearing for every
future product decision about institutional history.

## Decision

A committee decision cites the record digest of the judgment it was taken
against. Before this change, re-running an analysis **overwrote that record in
place**. The ledger entry then pointed at a digest nothing on disk matched, and
the decision silently became undefendable.

Verified rather than suspected:

```text
decision cites digest : 1f8b7bfeed57e1b4
on disk after re-run  : 344d3b6d8840491d
DECISION VERIFIABLE   : False
```

This is the most severe class of failure the product can have. It does not
produce a wrong answer — it destroys the ability to defend a right one, which is
the entire reason the product exists.

## Options put to the architect

**Archive.** Copy the old record aside before overwriting, so decided judgments
stay resolvable.

**Freeze.** Once a case is decided, refuse further analysis until the decision is
explicitly reopened.

**Supersede.** A new analysis creates a *new* judgment. Previous decisions keep
referencing the judgment they were made against. Nothing is overwritten and
nothing is locked.

## Ruling

**Supersede.** Stated by the architect:

> A committee decision must always remain permanently bound to the exact
> judgment that existed when that decision was recorded. Re-analysis must never
> invalidate historical decisions. Do not freeze cases. Do not overwrite
> history. Institutional history is append-only.

Freezing was rejected outright: a case that cannot be re-analysed after a
decision is a case an institution cannot keep working on, and deferral is a
first-class outcome in this product. Archiving was rejected because it makes the
*current* record primary and history a side effect; supersession makes every
judgment equally real and equally permanent.

## Implementation

- `JudgmentRecord` on the case: `judgment_id`, `record_digest`, `recorded_on`,
  `superseded_by`. Append-only; a new analysis marks the previous record
  superseded and appends its own.
- Artifacts move from `reports/workspace/<case>/` to
  `reports/workspace/<case>/judgments/<judgment-id>/`, written once, never
  rewritten. Each judgment retains the exact document it saw.
- `LedgerEntry` gains `judgment_id`. The store rejects a decision citing a
  judgment the case never reached.
- Decisions can only be recorded against the judgment in force. Recording one
  against a superseded judgment would be minuting a meeting into the past.
- `analysis.verify_ledger` checks every decision still resolves to artifacts on
  disk carrying the cited digest. The workspace shows the outcome beside each
  ledger entry, including a visible failure state. There is no quiet failure.
- An analysis reproducing the current judgment's digest returns that judgment
  rather than creating a duplicate. The engine is deterministic, so an identical
  digest means the material reached the same conclusion; recording it twice
  would put an event in institutional history that never happened.

Analysis runs in a scratch directory and the finished artifacts are moved into
place in one step, so a failed run cannot leave a half-written judgment behind.

## Invariants, and where they are defended

`TestSupersession` in `applications/investment/workspace/tests/test_workspace.py`.

| Invariant | Test |
|---|---|
| Historical decisions remain permanently verifiable | `test_a_decision_survives_re_analysis` |
| Historical record digests always resolve | `test_every_judgment_ever_reached_keeps_its_artifacts` |
| Re-analysis never invalidates prior decisions | `test_decisions_against_different_judgments_all_resolve` |
| Provenance remains complete | `test_the_material_that_produced_each_judgment_is_kept` |
| Append-only institutional history | `test_history_is_append_only` |
| A superseded judgment stays fully readable | `test_a_superseded_judgment_still_reads_in_full` |
| Determinism does not manufacture history | `test_re_running_unchanged_material_creates_no_new_judgment` |

## Consequences

- Storage grows with every distinct analysis. Deliberate, and cheap: a judgment
  is roughly 70 KB. Retention is an institutional policy question, not an
  engineering one, and is not answered here.
- The case store's on-disk layout changed. There is no migration path, because
  the only data in the old layout was generated development data. A deployed
  system would have needed one.
- `Case.status()` no longer takes an `analysed` argument. Judgment history lives
  on the case, so status is derived entirely from the case record.

## Approval Status

Approved and implemented 2026-08-06.
