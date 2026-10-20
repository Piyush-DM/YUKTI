# The Material Snapshot Layer

| | |
|---|---|
| **Document ID** | YK-D-006 |
| **Source** | `docs/architecture/DECISION-006_material_snapshot_layer.md` (DECISION-006) |
| **Series** | Architecture Decisions |
| **Revision** | A |
| **Status** | Published |
| **Last Updated** | 2026-08-23 |

## Abstract

This decision introduces **Material Snapshot**: "the immutable institutional material a judgment was formed from, identified by a `material_digest` computed at full institutional fidelity in the product layer" (§ "Decision"). It was motivated by a measured digest collision in which two materially different diligence packs produced one identical reasoning-record hash, so that a real change to what an institution claimed about its own evidence produced no new judgment (§ "The defect that motivated it"). The source records the layer as "the first immutable institutional identity layer" — "Everything future provenance work depends on sits on top of this" — and its status as **Approved 2026-08-06 (Authorizations 1–4, 6, 7). Implemented.**

## Research Question

The source does not pose an interrogative. Its framing is a distinction between two claims that had been treated as one (§ "The defect that motivated it"):

> The reasoning record carries a digest, and `choir_prototype/README.md` states that two people running the same packet "can compare one hash and know they saw the same reasoning."
>
> That is true. The claim an institution actually needs — that they saw the same **evidence** — is a different claim, and it was false.

The document therefore sets out to answer: what identity must an institution be able to compare so that a change in the material a judgment was formed from is recorded as a change — given that record identity alone demonstrably does not carry it?

## Finding

### The defect, as measured

The defect was not argued; it was measured against the frozen translator on 2026-08-06 (§ "The defect that motivated it"). The source reproduces the measurement verbatim:

```
STATUS reported vs estimated
  document differs : True
  digest A         : 580a5b279f18a7f13b71e5d3
  digest B         : 580a5b279f18a7f13b71e5d3
  COLLISION        : True
```

The mechanism is stated exactly: "`_STATUS_TO_UNCERTAINTY` maps both `reported` and `estimated` to `Uncertainty.LIKELY`, and a figure's status appears nowhere else in the intermediate representation. Two materially different diligence packs, one hash" (§ "The defect that motivated it").

The source records that this compounded with supersession, "shipped the previous cycle, which keyed institutional history on the record digest." The consequence is stated without softening: "An analyst restating a figure's standing from *reported* to *estimated* — a real change to what the institution claims about its own evidence — produced no new judgment. The material moved and the record said nothing happened."

The source also records how the defect surfaced: "The defect was found by testing a claim in the independent architectural review rather than by accepting or dismissing it" (§ "The defect that motivated it").

### The decision, and what it does not change

Material Snapshot is introduced as the immutable institutional material a judgment was formed from, identified by a `material_digest` computed at full institutional fidelity in the product layer (§ "Decision").

The source is explicit about the limit of the change: "`record_digest` is **not redefined**. It remains the digest of the reasoning record. Reasoning identity and material identity are distinct architectural concepts and are preserved independently" (§ "Decision").

### The invariant, and why order is part of it

The governing invariant is stated as: **"Material identity is finer-grained than reasoning identity."** (§ "The invariant")

```
same material  =>  always the same reasoning record
same record    =>  not necessarily the same material
```

The source stresses the asymmetry: "The direction matters. A material digest may safely be relied on where a record digest cannot, and supersession therefore keys on material."

It then gives the reason the digest is computed over the material **in recorded order** rather than over a normalised set: "Claim identifiers in the engine are positional, so re-ordering the diligence schedule changes the reasoning record. An order-insensitive digest would be *coarser* than the record it must be finer than, and the invariant would fail in precisely the case nobody would think to check." The test `test_reordering_the_schedule_is_a_material_change` is recorded as defending this (§ "The invariant").

### What was built

The source enumerates the implementation (§ "What was built"):

| Element | What the source records |
|---|---|
| `workspace/material.py` | `MaterialSnapshot`, `compute_material_digest`, `next_snapshot`, and the versioned hash scheme `yukti-material/1`. |
| **Snapshot registry** | "Every material save that moves the digest appends a snapshot, whether or not an analysis follows. The registry records what the institution assembled and when — deliberation over material, per Authorization 3, not only the states that happened to be analysed." |
| **Supersession re-keyed on material** | "A material change creates a new judgment even when the conclusion is unchanged." |
| **Ledger verification against material identity** | "`DigestCheck` now reports `record_resolves` and `material_resolves` as separate claims. A decision that cites no material reads as *unverified on that axis* rather than passing silently." |
| **Product surfaces** | "Material register on the case overview; snapshot and material digest on the judgment and audit views; per-decision verification shown on both axes; judgment history marks 'same conclusion, different material'." |

### Boundaries observed

The source records the authorization boundaries and how each is honoured (§ "Boundaries observed"):

| Authorization | How it is honoured |
|---|---|
| 4 — product layer only | Nothing in `material.py` reaches the engine. `--frozen` INTACT, `--audit` 1.00. `test_material_identity_never_reaches_the_engine` asserts material fields never enter the composed document. |
| 6 — reference documents, do not store | Sources remain references — label, description, standing. No document is stored, hashed or ingested. No retention, tenancy or compliance surface is created. |
| 7 — status mapping unchanged | The lossy mapping inside the frozen engine is untouched. The product preserves the richer vocabulary and hashes it; CHOIR still flattens it. |
| 5 — no DAALE assumptions | This layer has no DAALE dependency of any kind, which is what let the cycle proceed while `DECISION-005` is open. |

### Consequences recorded

The source records four consequences (§ "Consequences"):

- "`Case` gains an append-only `snapshots` registry. `JudgmentRecord` and `LedgerEntry` gain `material_digest` and `snapshot_id`."
- "Material digests may recur. Reverting material to an earlier state is a new institutional event with a new snapshot id and the earlier digest — the registry is a timeline, not a set."
- "Case metadata still cannot change material identity. Re-assigning a case must not fabricate new material, and does not."
- "Decisions recorded before this layer verify on reasoning but not on material. They are shown that way rather than being back-filled, because back-filling would assert something nobody attested."

The approval status is recorded as: "Approved and implemented 2026-08-06" (§ "Approval Status").

## Architectural Implications

Supersession no longer keys on the reasoning-record digest. Because material identity is finer-grained than reasoning identity, a material change creates a new judgment even when the conclusion is unchanged (§ "The invariant", § "What was built"). Institutional history is therefore keyed on the identity the source states "may safely be relied on" where a record digest cannot, rather than on the one that collided; the source asserts that property of the material digest rather than measuring it (§ "The invariant").

Verification is now two-axis. `DigestCheck` reports `record_resolves` and `material_resolves` as separate claims, and absence of cited material produces an explicit *unverified on that axis* reading rather than a silent pass (§ "What was built"). The same commitment governs the historical record: pre-layer decisions are displayed as verifying on reasoning but not on material, and are not back-filled, "because back-filling would assert something nobody attested" (§ "Consequences").

The material digest is order-sensitive by construction, which constrains any future normalisation work: an order-insensitive digest would be coarser than the reasoning record it is required to be finer than, breaking the invariant (§ "The invariant").

The layer is confined to the product layer. Nothing in `material.py` reaches the engine; `--frozen` is INTACT and `--audit` is 1.00; and the lossy `_STATUS_TO_UNCERTAINTY` mapping inside the frozen engine is untouched, so the product preserves the richer status vocabulary and hashes it while "CHOIR still flattens it" (§ "Boundaries observed"). Under Authorization 6, sources remain references — label, description, standing — with no document stored, hashed or ingested, and the source states that "No retention, tenancy or compliance surface is created."

The layer carries no DAALE dependency of any kind, which the source records as "what let the cycle proceed while `DECISION-005` is open" (§ "Boundaries observed"). Decoupling from DAALE is therefore load-bearing for sequencing, not incidental.

The data model changes are recorded as an append-only `snapshots` registry on `Case`, and `material_digest` and `snapshot_id` on `JudgmentRecord` and `LedgerEntry`; the registry is a timeline rather than a set, so a reverted material state recurs as a new institutional event with a new snapshot id and the earlier digest (§ "Consequences").

## Open Questions

The source contains no section headed as open questions. The unresolved and deliberately-unaddressed items it does record are:

- **`DECISION-005` is open.** The source states that this layer's lack of any DAALE dependency "is what let the cycle proceed while `DECISION-005` is open" (§ "Boundaries observed"). It does not record when or how that decision resolves.
- **The lossy status mapping inside the frozen engine remains in place.** Under Authorization 7 it is untouched: the product preserves the richer vocabulary and hashes it, but "CHOIR still flattens it" (§ "Boundaries observed"). The source records no plan to change this.
- **Pre-layer decisions are not verified on the material axis.** They verify on reasoning but not on material, and are shown that way rather than back-filled (§ "Consequences"). The source records no remedy, and states the reason back-filling is refused.
- **Authorization 5 is not listed in the approval line.** The status line records "Approved 2026-08-06 (Authorizations 1–4, 6, 7)" (§ header), while the boundaries table also carries a row for Authorization 5 — "no DAALE assumptions" (§ "Boundaries observed"). The source does not comment on the difference.

## Related Documents

- [YK-D-005 — Canonical Definition of DAALE](YK-D-005-canonical-definition-of-daale.md) — cited by name in the source as `DECISION-005`, recorded as open at the time of this decision (§ "Boundaries observed").
- [YK-D-004 — Judgment Supersession](YK-D-004-judgment-supersession.md) — the source refers to "supersession, shipped the previous cycle, which keyed institutional history on the record digest" (§ "The defect that motivated it") and re-keys it on material (§ "What was built"); it does not name the decision by its document identifier.

The source additionally cites `choir_prototype/README.md` and an "independent architectural review" (§ "The defect that motivated it"). Neither has a corresponding publication identifier in this index.
