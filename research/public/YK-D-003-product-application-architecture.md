# Product Application Architecture

| | |
|---|---|
| **Document ID** | YK-D-003 |
| **Source** | `docs/architecture/DECISION-003_product_application_architecture.md` (DECISION-003) |
| **Series** | Architecture Decisions |
| **Revision** | A |
| **Status** | Published |
| **Last Updated** | 2026-08-23 |

## Abstract

This document records the approved architecture for the product application built
around the CHOIR reasoning engine. It answers four questions — where the product
lives and what it is called (§1), what vocabulary it uses (§2), how it obtains a
judgment given the engine is frozen (§3), and where institutional state lives (§4)
— and rules the scope conflict between `CHOIR_v0.1_RESEARCH_FREEZE.md` §5 and the
product instruction. All four choices were approved on 2026-08-06, together with
the ruling that §5's engineering exclusions apply to the reasoning engine and not
to product layers.

## Research Question

The source frames the question directly: "The reasoning engine is stable and the
vertical slice is the canonical reference implementation. The product must be
built *around* it. Four questions had to be answered before a line of it could be
written, and none is answered by an existing specification."

The four questions, as the source numbers them:

1. **Where does the product live, and what is it called?**
2. **What vocabulary does it use** — the engine's, or something else?
3. **How does the product obtain a judgment**, given the engine is frozen?
4. **Where does institutional state live**, given `reports/` is for generated
   output and a database is out of scope?

## Finding

### The scope conflict, and how it was ruled

Two specifications disagreed. `CHOIR_v0.1_RESEARCH_FREEZE.md` §5 lists **UI, APIs,
databases and authentication** as out of scope for v0.1, carried forward from the
prototype's own exclusions. The product instruction requires a UI and an
application server.

The conflict was recorded rather than silently resolved, per the charter's rule on
conflicting specifications. The reading taken was the conservative one: §5's
exclusions are scoped to the reasoning engine, which must not grow a UI, an API,
or a database. A product layer built outside the engine — one that leaves the
engine untouched and verifiably frozen — does not violate it. The source states
that the most conservative available reading of the database exclusion was taken
literally: there is no database.

The ruling is recorded verbatim in the source:

> **Ruled 2026-08-06: §5 applies to the reasoning engine, not to product layers.**
> The reading taken here is the approved one. CHOIR, DAALE, kernel interfaces,
> runtime behaviour, translator interfaces, repository governance and the
> deterministic guarantees remain unmodifiable; product layers built outside them
> are approved.

### 1. Location and name (§1)

**Chosen: `applications/investment/workspace/`.**

Rejected: a new top-level `yukti/` package. The reasoning given is that the
application serves one domain — investment — because that is the only domain the
engine's vertical slice supports. Claiming a top-level namespace for something
that serves one domain over-states what was built, and repository organization is
frozen. The existing `applications/investment/` area is described as the
domain-application area and already holds both the reference implementation and
the product prototype.

**Consequence recorded:** if the product later serves a second domain, it will
have to move, and that move is a repository-organization change requiring its own
approval.

### 2. Vocabulary (§2)

**Chosen: the vocabulary the existing product prototype already established** —
Case, Evidence/Source, Positions, Conflicts, Decision Ledger, Institutional
Judgment (`applications/investment/prototype-ui/README.md`).

The source states this was not a free choice: that prototype is the repository's
existing product design, and the charter requires preserving naming conventions
rather than inventing new ones. Two departures are recorded, both deliberate:

| Departure | Reason given in the source |
|---|---|
| **"RIK Positions" → "Review areas."** | "RIK" belongs to the model-backed Risk RIK path, which `DECISION-001` made legacy. Keeping the prefix would attach the product to a retired path; keeping only the noun preserves the concept. The source flags this as "a rename of an existing product concept" that "needs explicit approval." |
| **"Propositions" is not used.** | The engine has no decision-proposition object — the source records this as an open question in the research freeze §4.4. Rather than invent one, the product does not offer the concept. |

Because "Propositions" is dropped, the prototype's Judgment → Proposition →
Position → Evidence trace is shortened to **Judgment → Review area → Finding →
Source**.

### 3. Obtaining a judgment (§3)

**Chosen: compose a document, call the vertical slice, read the persisted record
back.**

Rejected: importing CHOIR core directly and holding the live objects. The source
concedes the cost plainly — reading `05-record.json` back "is slower and slightly
awkward" — and states what it buys: the product view is a *projection of the
record* and cannot display a conclusion the record does not contain. The source
describes this as commitment E9 extended into the product rather than stopped at
the engine boundary.

Rejected: extending the vertical slice to accept case material directly. It is the
canonical reference implementation, and integrating with it means calling it, not
changing it.

**Consequence recorded:** the product relabels engine prose into institutional
language through a whole-word substitution table, because some engine strings are
composed rather than looked up and the engine is frozen. The source identifies
this as "the single most reviewable thing in the application: it is the only place
the product touches the engine's own words." It is described as mechanical, total,
and asserted by test to leave prose containing no internal name byte-identical.

### 4. Institutional state (§4)

**Chosen: one JSON file per case under `reports/workspace/<case-id>/`, beside that
case's engine artifacts.**

Rejected: a database (out of scope, §5). Rejected: a new top-level data directory
(organization is frozen). The reasoning given is that `reports/` is already
established as generated output that is not committed, and putting the case file
next to its own audit trail means a judgment can be defended without leaving the
directory.

The source records this as the weakest point in the decision, in its own words:
`reports/README.md` describes the directory as "reserved for Prototype-001 report
output". A case file is institutional state, not report output. "The convention is
being stretched. The alternative was worse, but this is the choice most likely to
want revisiting once the product has real users and real retention requirements."

### Consequences recorded

- `choir_prototype/` is untouched: `--frozen` reports INTACT and `--audit` reports
  portability 1.00 with the application in the tree.
- `applications/investment/vertical_slice/` is untouched and is called, not
  copied.
- The application makes no model calls and does not extend the legacy model-backed
  path, per `DECISION-001`.
- `applications/investment/prototype-ui/` is now superseded as the product
  direction but is **not removed**. Retiring it touches a passing test suite and is
  scheduled work, not a side effect of writing this note — the same treatment
  `DECISION-001` gave the Risk RIK provider.
- No authentication, no access control, no concurrency handling. Local development
  only, and stated as such in the application's own README.

### Approval status

Approved 2026-08-06. All four choices approved.

- The section 5 conflict is ruled: the research freeze's engineering exclusions
  apply to the reasoning engine, not to product layers. The workspace and the
  product application are approved. CHOIR, DAALE, kernel interfaces, runtime
  behaviour, translator interfaces, repository governance and the deterministic
  guarantees remain unmodifiable.
- **"Review areas" is approved as canonical user-facing terminology.**
- Choice 4 (case state under `reports/workspace/`) is approved as it stands and
  remains the item most likely to want revisiting once the product has real users
  and real retention requirements.

The source's own recommendation, prior to approval, was to approve all four, with
choice 4 named as the one to revisit first and choice 2's "RIK Positions" rename
named as the one that most needed an explicit yes or no, because it changes an
existing product name.

The source further records that a fifth decision followed from putting the
application in front of a reviewer and is now implemented: **supersession.** A
committee decision is permanently bound to the judgment it was recorded against;
re-analysis creates a new judgment and never invalidates a historical one.
Institutional history is append-only. The source points to `DECISION-004`.

## Architectural Implications

- CHOIR, DAALE, kernel interfaces, runtime behaviour, translator interfaces,
  repository governance and the deterministic guarantees remain unmodifiable. The
  ruling on §5 permits product layers only where they are built outside these and
  leave the engine untouched and verifiably frozen.
- The reasoning engine must not grow a UI, an API, or a database. Under the most
  conservative reading of the database exclusion, taken literally, there is no
  database anywhere in this architecture.
- Integration with the vertical slice is by call, not by modification and not by
  copy: `applications/investment/vertical_slice/` is untouched, and
  `choir_prototype/` remains INTACT under `--frozen` with portability 1.00 under
  `--audit`.
- Commitment E9 is extended past the engine boundary into the product: because the
  product view is a projection of the persisted record (`05-record.json`), it
  cannot display a conclusion the record does not contain.
- The product exposes no decision-proposition object, because the engine has none;
  the user-facing trace is Judgment → Review area → Finding → Source.
- "Review areas" is canonical user-facing terminology. The product does not carry
  the "RIK" prefix, which belongs to the model-backed Risk RIK path made legacy by
  `DECISION-001`.
- The application makes no model calls and does not extend the legacy model-backed
  path, per `DECISION-001`.
- The whole-word substitution table is the only place the product touches the
  engine's own words, which is why the source calls it the single most reviewable
  thing in the application. It is mechanical, total, and asserted by test to leave
  prose containing no internal name byte-identical.
- A second domain would force the application to move out of
  `applications/investment/workspace/`, and that move is a repository-organization
  change requiring its own approval.
- Institutional history is append-only: a committee decision is permanently bound
  to the judgment it was recorded against, and re-analysis creates a new judgment
  rather than invalidating a historical one (`DECISION-004`).

## Open Questions

- **Choice 4 (§4) — case state under `reports/workspace/`.** Approved as it
  stands, but recorded by the source as the weakest point in the decision and the
  item most likely to want revisiting once the product has real users and real
  retention requirements. `reports/README.md` describes the directory as "reserved
  for Prototype-001 report output"; a case file is institutional state, not report
  output, and the convention is being stretched.
- **No decision-proposition object in the engine (§2).** The source records this
  as an open question in the research freeze §4.4. The product does not offer the
  concept rather than inventing one.
- **Retirement of `applications/investment/prototype-ui/` (Consequences).** It is
  superseded as the product direction but not removed. Retiring it touches a
  passing test suite and is recorded as scheduled work, not yet done.
- **Second-domain relocation (§1).** If the product later serves a second domain
  it will have to move, and that move is a repository-organization change requiring
  its own approval. No such approval is recorded here.
- **Authentication, access control, and concurrency (Consequences).** None of the
  three is handled. The application is local development only, and stated as such
  in its own README.

## Related Documents

- [YK-D-001 — Reasoning Execution Substrate](YK-D-001-reasoning-execution-substrate.md) — made the model-backed Risk RIK path legacy, which drives the "RIK Positions" → "Review areas" rename (§2) and the constraint that the application makes no model calls; also the precedent for not removing a superseded component with a passing test suite.
- [YK-D-004 — Judgment Supersession](YK-D-004-judgment-supersession.md) — the fifth decision that followed from this one: a committee decision is permanently bound to the judgment it was recorded against, and institutional history is append-only.
