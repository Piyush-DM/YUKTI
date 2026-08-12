# Decision: the Material Snapshot layer

**Status: Approved 2026-08-06 (Authorizations 1–4, 6, 7). Implemented.**

The first immutable institutional identity layer. Everything future provenance
work depends on sits on top of this.

## The defect that motivated it

The reasoning record carries a digest, and `choir_prototype/README.md` states
that two people running the same packet "can compare one hash and know they saw
the same reasoning."

That is true. The claim an institution actually needs — that they saw the same
**evidence** — is a different claim, and it was false. Measured against the
frozen translator on 2026-08-06:

```
STATUS reported vs estimated
  document differs : True
  digest A         : 580a5b279f18a7f13b71e5d3
  digest B         : 580a5b279f18a7f13b71e5d3
  COLLISION        : True
```

`_STATUS_TO_UNCERTAINTY` maps both `reported` and `estimated` to
`Uncertainty.LIKELY`, and a figure's status appears nowhere else in the
intermediate representation. Two materially different diligence packs, one hash.

This compounded with supersession, shipped the previous cycle, which keyed
institutional history on the record digest. An analyst restating a figure's
standing from *reported* to *estimated* — a real change to what the institution
claims about its own evidence — produced no new judgment. The material moved and
the record said nothing happened.

The defect was found by testing a claim in the independent architectural review
rather than by accepting or dismissing it.

## Decision

Introduce **Material Snapshot**: the immutable institutional material a judgment
was formed from, identified by a `material_digest` computed at full
institutional fidelity in the product layer.

`record_digest` is **not redefined**. It remains the digest of the reasoning
record. Reasoning identity and material identity are distinct architectural
concepts and are preserved independently.

## The invariant

**Material identity is finer-grained than reasoning identity.**

```
same material  =>  always the same reasoning record
same record    =>  not necessarily the same material
```

The direction matters. A material digest may safely be relied on where a record
digest cannot, and supersession therefore keys on material.

This is why the digest is computed over the material **in recorded order**
rather than over a normalised set. Claim identifiers in the engine are
positional, so re-ordering the diligence schedule changes the reasoning record.
An order-insensitive digest would be *coarser* than the record it must be finer
than, and the invariant would fail in precisely the case nobody would think to
check. `test_reordering_the_schedule_is_a_material_change` defends this.

## What was built

- `workspace/material.py` — `MaterialSnapshot`, `compute_material_digest`,
  `next_snapshot`, and the versioned hash scheme `yukti-material/1`.
- **Snapshot registry.** Every material save that moves the digest appends a
  snapshot, whether or not an analysis follows. The registry records what the
  institution assembled and when — deliberation over material, per
  Authorization 3, not only the states that happened to be analysed.
- **Supersession re-keyed on material.** A material change creates a new
  judgment even when the conclusion is unchanged.
- **Ledger verification against material identity.** `DigestCheck` now reports
  `record_resolves` and `material_resolves` as separate claims. A decision that
  cites no material reads as *unverified on that axis* rather than passing
  silently.
- **Product surfaces.** Material register on the case overview; snapshot and
  material digest on the judgment and audit views; per-decision verification
  shown on both axes; judgment history marks "same conclusion, different
  material".

## Boundaries observed

| Authorization | How it is honoured |
|---|---|
| 4 — product layer only | Nothing in `material.py` reaches the engine. `--frozen` INTACT, `--audit` 1.00. `test_material_identity_never_reaches_the_engine` asserts material fields never enter the composed document. |
| 6 — reference documents, do not store | Sources remain references — label, description, standing. No document is stored, hashed or ingested. No retention, tenancy or compliance surface is created. |
| 7 — status mapping unchanged | The lossy mapping inside the frozen engine is untouched. The product preserves the richer vocabulary and hashes it; CHOIR still flattens it. |
| 5 — no DAALE assumptions | This layer has no DAALE dependency of any kind, which is what let the cycle proceed while `DECISION-005` is open. |

## Consequences

- `Case` gains an append-only `snapshots` registry. `JudgmentRecord` and
  `LedgerEntry` gain `material_digest` and `snapshot_id`.
- Material digests may recur. Reverting material to an earlier state is a new
  institutional event with a new snapshot id and the earlier digest — the
  registry is a timeline, not a set.
- Case metadata still cannot change material identity. Re-assigning a case must
  not fabricate new material, and does not.
- Decisions recorded before this layer verify on reasoning but not on material.
  They are shown that way rather than being back-filled, because back-filling
  would assert something nobody attested.

## Approval Status

Approved and implemented 2026-08-06.
