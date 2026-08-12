# YUKTI Investment Committee Workspace

Version 1 of the YUKTI application. Institutional software for carrying an
investment case from intake to a recorded committee decision.

```powershell
python -m applications.investment.workspace
```

Then open `http://127.0.0.1:8770/`.

The reasoning engine is infrastructure here. A user never sees a kernel, a
translator, an intermediate representation, or a runtime artifact — except in
the Audit view, which exists so a decision can be defended.

---

## What the institution is trying to do

Everything in this product answers one question: **can a committee reach a
defensible decision, and show its work afterwards?**

That decomposes into five things a person actually does.

| The task | Where it happens |
|---|---|
| Decide what we are being asked to approve | Open case |
| Assemble what we know, and record where each figure came from | Material |
| See what the material supports | Judgment |
| Understand where the analysis is divided against itself | Judgment → disagreements |
| Record what we decided, and against what | Judgment → decision ledger |

## The journey

```text
Case register                 every open case and its standing
      |
      v  Open case            what is the committee being asked to approve
Draft
      |
      v  Material             source register + diligence schedule
Material assembled
      |
      v  Request judgment     the reasoning engine runs on the material
Analysed                      recommendation, confidence, conditions,
      |                       disagreements, what was not established
      v  Record decision      what the committee chose, and why
Decided
```

Status is **derived from the record**, never set by hand. A case cannot be shown
as Analysed unless a reasoning record exists on disk for it.

## Entities

The vocabulary is the one the existing investment product prototype already
established (`../prototype-ui/README.md`), now backed by real analysis rather
than fixtures.

| Entity | What it is |
|---|---|
| **Case** | One decision the institution has to make |
| **Source** | One document in the case's register, with how it came to exist |
| **Figure** | One entry on the diligence schedule, its value, its standing, and the sources behind it |
| **Flagged conflict** | A figure the team already believes its own sources disagree about |
| **Judgment** | What the material supports — produced by the engine, never edited |
| **Review area** | One independent line of analysis over the material |
| **Condition** | A finding that supports proceeding only if something is resolved first |
| **Decision ledger** | What the committee chose, recorded against the judgment |

### Diligence schedule

The committee's standing checklist: fifteen figures, grouped into four review
areas. Every entry is a figure the engine reads, and that correspondence is
enforced by a test — a figure nobody reads would be busywork asked of a
diligence team.

The schedule is what lets the workspace say *which* figures are outstanding
**before** anything is run, while an analyst can still go and find them.

### Why the source register matters

Every figure must cite a source in the register, and a figure citing a source
that is not registered is rejected at save time. This is the one rule in the
product that exists purely for the audit trail: an uncitable figure is exactly
what an audit trail exists to prevent.

How a source came to exist — audited, management-provided, interview,
third-party, unsupported — sets the ceiling on how confident any conclusion
resting on it can be. The institution records that at intake rather than
arguing about it later.

## Judgment, and what the product is not allowed to do

The workspace **computes no judgment of its own.** It composes the case material
into the document format the reference implementation accepts, hands it to
`applications.investment.vertical_slice`, and then reads the persisted record
back to build the screen.

Reading the record back rather than holding the live objects is deliberate. The
engine's central guarantee is that a view is a projection of the record and can
never disagree with the reasoning. Building the judgment view from
`05-record.json` extends that guarantee into the product: **the workspace cannot
display a conclusion the record does not contain, because the record is the only
thing it has.**

Two tests hold that boundary:

- `test_judgment_matches_the_engine_directly` runs the engine independently over
  the same material and compares. If the product ever starts computing
  something, it fails.
- `test_workspace_does_not_call_the_synthesizer` reads the product's own source
  and fails if it ever calls `synthesize` or `derive_confidence`.

### Institutional relabelling

Engine output is relabelled into institutional language on the way to the
screen. Review areas, topics, stances and confidence bands are looked up in a
table; some engine prose is *composed* rather than looked up, and is passed
through a whole-word substitution instead.

That substitution is a relabelling, never a rewrite. Text containing no internal
name passes through byte for byte — asserted by
`test_relabelling_leaves_ordinary_prose_untouched`. The engine is frozen and
cannot be changed to phrase things differently, so this is the only place the
product can say "review area" where the engine wrote "kernel".

It matters more than it sounds. Without it a committee reads:

> Claim clm-007 (net_revenue_retention_pct) is contradicted elsewhere in the
> packet; this finding is provisional.

With it:

> Net revenue retention is contradicted elsewhere in the case material; this
> finding is provisional.

`clm-007` is still in the audit view, verbatim, which is the one place a reader
who needs it is looking.

## Material identity — what a judgment was formed from

**Two digests, two different claims.**

| | Proves |
|---|---|
| `record_digest` | the *reasoning* was identical |
| `material_digest` | the *material* was identical |

The second does not follow from the first. The frozen engine flattens
distinctions the institution records — a figure marked `reported` and the same
figure marked `estimated` both become `LIKELY`, and status appears nowhere else
in the intermediate representation. Two materially different diligence packs
therefore produce one reasoning record, verified:

```
digest A : 580a5b279f18a7f13b71e5d3
digest B : 580a5b279f18a7f13b71e5d3
COLLISION: True
```

A **Material Snapshot** closes it. Every state of a case's material is hashed at
full institutional fidelity, given an identity and a version, and appended to the
case's material register. A judgment binds to the snapshot in force when it ran,
and says so.

The invariant that makes this safe:

```
same material  =>  always the same reasoning record
same record    =>  not necessarily the same material
```

Material identity is deliberately *finer-grained* than reasoning identity, which
is why the digest covers the material in recorded order — claim identifiers in
the engine are positional, so an order-insensitive digest would be coarser than
the record it must be finer than.

Consequences a committee sees:

- **A material change creates a new judgment even when the conclusion is
  unchanged.** History records deliberation over material, not only changes of
  mind. The judgment list marks these "same conclusion, different material".
- **Decisions verify on both axes independently.** A decision can be *reasoning
  verified* but *material not identified*; the workspace says exactly that
  rather than reporting it as verified.
- **Reverting material is a new state**, with a new snapshot id and a recurring
  digest. The register is a timeline, not a set.

Sources remain **references** to documents the institution holds elsewhere.
Nothing is uploaded, stored or ingested — this layer is identity, not document
management (`DECISION-006`).

## Supersession — how history stays honest

**A decision is permanently bound to the judgment it was taken against.**

Re-analysing a case creates a *new* judgment. The previous one is marked
superseded and otherwise left completely alone: same id, same digest, same
artifacts on disk. Any decision citing it keeps resolving, forever.

```text
JUDGMENT-001  ──superseded by──▶  JUDGMENT-002 (in force)
     ▲
     └── LEDGER-001 "Approved with conditions"  ← still verifies
```

This replaced the product's worst defect. Previously a re-run overwrote the
record in place, so a recorded decision silently stopped resolving — the exact
opposite of what the audit trail exists for.

Three rules make it work:

- **Append-only.** No judgment is deleted or rewritten. A case accumulates
  `JUDGMENT-001`, `-002`, `-003` and keeps all of them.
- **Identical records do not create a judgment.** The engine is deterministic,
  so a re-run over unchanged material produces the same digest, which means the
  same conclusion. Recording it twice would put an event in the institutional
  history that never happened.
- **Decisions bind forward only.** A decision can only be recorded against the
  judgment in force. Recording one against a superseded judgment would be
  minuting a meeting into the past, and the store rejects a decision citing a
  judgment the case never reached.

`analysis.verify_ledger` makes the invariant checkable rather than asserted: for
every decision it confirms the cited judgment is on disk and carries the cited
digest. The workspace shows the result beside each ledger entry — "verified
against its record", or a black **RECORD DOES NOT RESOLVE** flag. There is no
quiet failure mode.

## Storage

One directory per case, with each judgment written once into its own directory:

```text
reports/workspace/orbital-logistics/
    case.json                    material, material register, judgments, ledger
    judgments/
        JUDGMENT-001/            superseded — kept, still resolvable
            01-document.json     what the engine was given
            02-packet.json · 03-ir.json · 04-artifacts.json
            05-record.json       the canonical record
            06-report.txt        the full reasoning record
            metadata.json        digests
        JUDGMENT-002/            in force
            ...
```

Each judgment keeps the exact document it saw, so provenance runs from a
decision back through its judgment to the material that produced it — even after
the case material has moved on.

No database. The material is small, a JSON file is readable by a human without
tooling, and `reports/` is already established as generated output that is not
committed. Case identifiers are slugs of the company name, so a directory
listing is legible and a URL says what it points at.

The audit trail sits **beside** the case file rather than somewhere else, so a
judgment can be defended without leaving the case directory.

## What this version does not do

Named rather than implied, following the reference implementation's practice:

- **No authentication and no access control.** Local development only. A real
  deployment needs both; pretending otherwise here would be worse than saying so.
- **No concurrency handling** beyond what `ThreadingHTTPServer` gives by default.
  Two people editing one case will overwrite each other.
- **One domain.** The workspace is bound directly to the investment domain.
  There is no domain dispatch, because there is one domain.
- **No document upload.** Sources are registered by reference and description;
  the file itself lives wherever the institution already keeps it. Uploading
  documents implies extraction, which is an open architectural question, not a
  product feature.
- **No editing of a judgment.** A judgment is what the material supported. To
  change it, change the material and re-run — which supersedes rather than
  overwrites.
- **No deletion of anything.** Cases, judgments and ledger entries only
  accumulate. There is no path in the product that removes institutional
  history.
- **No cross-case memory.** Precedent and consistency-checking across decisions
  are explicitly out of scope for v0.1.

## Tests

```powershell
python -m unittest discover -s applications/investment/workspace -t .
```

46 tests. `TestMaterialIdentity` defends the material layer, and its first test reproduces the digest collision that motivated it. `TestSupersession` is the supersession ruling made checkable — each of
its seven tests defends one named invariant, and the first reproduces the defect
that prompted the ruling. `TestJudgment`'s two boundary tests defend the engine
boundary. The rest are workflow.
