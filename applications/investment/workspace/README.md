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

## Storage

One directory per case under `reports/workspace/<case-id>/`:

```text
reports/workspace/orbital-logistics/
    case.json          the case, its material, and its decision ledger
    01-document.json   what the engine was given
    03-ir.json         · 04-artifacts.json · 05-record.json
    06-report.txt      the full reasoning record
    metadata.json      digests
```

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
  change it, change the material and re-run.
- **No cross-case memory.** Precedent and consistency-checking across decisions
  are explicitly out of scope for v0.1.

## Tests

```powershell
python -m unittest discover -s applications/investment/workspace -t .
```

26 tests. The two that matter most are the boundary tests named above; the rest
are workflow.
