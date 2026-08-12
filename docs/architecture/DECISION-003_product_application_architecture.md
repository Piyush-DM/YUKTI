# Decision Required: product application architecture

**Status: Approved 2026-08-06.** All four choices approved, and the §5 scope
conflict ruled in favour of the reading taken here. See "Approval Status".

## Decision

The reasoning engine is stable and the vertical slice is the canonical reference
implementation. The product must be built *around* it. Four questions had to be
answered before a line of it could be written, and none is answered by an
existing specification.

1. **Where does the product live, and what is it called?**
2. **What vocabulary does it use** — the engine's, or something else?
3. **How does the product obtain a judgment**, given the engine is frozen?
4. **Where does institutional state live**, given `reports/` is for generated
   output and a database is out of scope?

## Context: two specifications disagree

`CHOIR_v0.1_RESEARCH_FREEZE.md` §5 lists **UI, APIs, databases and
authentication** as out of scope for v0.1, carried forward from the prototype's
own exclusions. The product instruction requires a UI and an application server.

Recorded rather than silently resolved, per the charter's rule on conflicting
specifications. The conservative reading, and the one taken here: §5's
exclusions are scoped to **the reasoning engine**, which must not grow a UI, an
API, or a database. A product layer built outside the engine, which leaves the
engine untouched and verifiably frozen, does not violate it. The most
conservative available reading of the database exclusion was taken literally —
there is no database.

**Ruled 2026-08-06: §5 applies to the reasoning engine, not to product layers.**
The reading taken here is the approved one. CHOIR, DAALE, kernel interfaces,
runtime behaviour, translator interfaces, repository governance and the
deterministic guarantees remain unmodifiable; product layers built outside them
are approved.

## Options and choices

### 1. Location and name

**Chosen: `applications/investment/workspace/`.**

Rejected: a new top-level `yukti/` package. The application serves one domain —
investment — because that is the only domain the engine's vertical slice
supports. Claiming a top-level namespace for something that serves one domain
over-states what was built, and repository organization is frozen. The existing
`applications/investment/` area is described as the domain-application area and
already holds both the reference implementation and the product prototype.

**Consequence:** if the product later serves a second domain, it will have to
move, and that move is a repository-organization change requiring its own
approval.

### 2. Vocabulary

**Chosen: the vocabulary the existing product prototype already established** —
Case, Evidence/Source, Positions, Conflicts, Decision Ledger, Institutional
Judgment (`applications/investment/prototype-ui/README.md`).

This was not a free choice. That prototype is the repository's existing product
design, and the charter requires preserving naming conventions rather than
inventing new ones. Two departures, both deliberate:

- **"RIK Positions" → "Review areas."** "RIK" belongs to the model-backed Risk
  RIK path, which `DECISION-001` made legacy. Keeping the prefix would attach
  the product to a retired path; keeping only the noun preserves the concept.
  *This is a rename of an existing product concept and needs explicit approval.*
- **"Propositions" is not used.** The engine has no decision-proposition object
  — that is an open question recorded in the research freeze §4.4. Rather than
  invent one, the product does not offer the concept. The prototype's
  Judgment → Proposition → Position → Evidence trace is therefore shortened to
  Judgment → Review area → Finding → Source.

### 3. Obtaining a judgment

**Chosen: compose a document, call the vertical slice, read the persisted
record back.**

Rejected: importing CHOIR core directly and holding the live objects. Reading
`05-record.json` back is slower and slightly awkward, and it buys the thing that
matters — the product view is a *projection of the record* and cannot display a
conclusion the record does not contain. That is commitment E9 extended into the
product rather than stopped at the engine boundary.

Rejected: extending the vertical slice to accept case material directly. It is
the canonical reference implementation and integrating with it means calling it,
not changing it.

**Consequence:** the product relabels engine prose into institutional language
through a whole-word substitution table, because some engine strings are
composed rather than looked up and the engine is frozen. This is the single
most reviewable thing in the application: it is the only place the product
touches the engine's own words. It is mechanical, total, and asserted by test to
leave prose containing no internal name byte-identical.

### 4. Institutional state

**Chosen: one JSON file per case under `reports/workspace/<case-id>/`, beside
that case's engine artifacts.**

Rejected: a database (out of scope, §5). Rejected: a new top-level data
directory (organization is frozen). `reports/` is already established as
generated output that is not committed, and putting the case file next to its
own audit trail means a judgment can be defended without leaving the directory.

**Consequence, and the weakest point in this decision:** `reports/README.md`
describes the directory as "reserved for Prototype-001 report output". A case
file is institutional state, not report output. The convention is being
stretched. The alternative was worse, but this is the choice most likely to want
revisiting once the product has real users and real retention requirements.

## Recommendation

Approve all four. Choice 4 is the one to revisit first; choice 2's "RIK
Positions" rename is the one that most needs an explicit yes or no, because it
changes an existing product name.

## Consequences

- `choir_prototype/` is untouched: `--frozen` reports INTACT and `--audit`
  reports portability 1.00 with the application in the tree.
- `applications/investment/vertical_slice/` is untouched and is called, not
  copied.
- The application makes no model calls and does not extend the legacy
  model-backed path, per `DECISION-001`.
- `applications/investment/prototype-ui/` is now superseded as the product
  direction but is **not removed**. Retiring it touches a passing test suite and
  is scheduled work, not a side effect of writing this note — the same treatment
  `DECISION-001` gave the Risk RIK provider.
- No authentication, no access control, no concurrency handling. Local
  development only, and stated as such in the application's own README.

## Approval Status

**Approved 2026-08-06.** All four choices approved.

- The section 5 conflict is ruled: the research freeze's engineering exclusions
  apply to the reasoning engine, not to product layers. The workspace and the
  product application are approved. CHOIR, DAALE, kernel interfaces, runtime
  behaviour, translator interfaces, repository governance and the deterministic
  guarantees remain unmodifiable.
- **"Review areas" is approved as canonical user-facing terminology.**
- Choice 4 (case state under `reports/workspace/`) is approved as it stands and
  remains the item most likely to want revisiting once the product has real
  users and real retention requirements.

A fifth decision followed from putting the application in front of a reviewer
and is now implemented: **supersession.** A committee decision is permanently
bound to the judgment it was recorded against; re-analysis creates a new
judgment and never invalidates a historical one. Institutional history is
append-only. See `DECISION-004`.
