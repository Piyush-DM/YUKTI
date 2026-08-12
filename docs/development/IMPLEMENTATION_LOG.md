# Implementation Log

A running record of implementation work: what was built, what remains, what was
assumed, and what needs an architect.

This is the *narrative* companion to `IMPLEMENTATION_QUEUE.md`, which stays the
backlog. Entries are append-only and newest last. Every assumption recorded here
should be reviewable on its own, without reading the code that rests on it.

---

## 2026-08-05 — Vertical slice: document to rendered report

**Instruction.** Implement the first complete vertical slice of the YUKTI
reasoning pipeline: one fixed sample document traversing parsing, an
intermediate representation, reasoning, a canonical report, and a rendered
report, with every intermediate artifact persisted and inspectable.

### Completed

- `applications/investment/vertical_slice/` — the slice, runnable with
  `python -m applications.investment.vertical_slice`.
  - `documents/orbital-series-b.json` — the fixed sample document.
  - `parse.py` — document → `InvestmentPacket`. Structural validation only.
  - `run.py` — executes the pipeline and persists all six stage artifacts plus
    `metadata.json`.
  - `__main__.py` — CLI.
  - `tests/test_vertical_slice.py` — 17 tests.
  - `README.md`.
- `docs/architecture/DECISION-002_document_intake_for_the_vertical_slice.md` —
  the one architectural choice the instruction did not settle. **Pending
  approval.**
- Supporting updates: root `README.md` repository map and implementation status;
  `TRACEABILITY_MATRIX.md` (two rows, both marked outside the approved chain);
  `pyproject.toml` pytest testpaths; `.gitignore` for generated `reports/`
  output; this log.

**Validation gate:** `ruff check`, `ruff format --check`, `python -m unittest`
(126 tests), `python -m compileall` all pass. `python -m choir_prototype
--frozen` reports INTACT and `--audit` reports portability 1.00 with the slice
in the tree.

### What was built on, and what was not touched

Everything downstream of parsing is `choir_prototype/` called as a library:
`domains.investment.translate`, `core.pipeline.execute`, `core.report.render`.
No file in that package was modified — it is frozen and hash-pinned, and the
freeze check is what verifies the claim rather than this paragraph.

The slice therefore adds exactly one new stage, document intake, and composes
existing components for the rest. That was the conservative reading of the
instruction and is what makes the change reversible.

### Assumptions

Each is the smallest assumption that let the work proceed, and each is stated so
it can be rejected independently.

**A1 — A "document" for v0.1 is the deal packet serialised, not prose.**
`choir_prototype/` starts at a packet and has no document concept, so the
instruction's first stage did not exist. Prose would have required an extraction
layer, which is interpretation — an unaudited reasoning step in front of the
audited ones — and would begin paying down the provenance gap recorded in
`CHOIR_v0.1_RESEARCH_FREEZE.md` §4.3, a research programme rather than a task.
*Full reasoning and rejected options: `DECISION-002`. Pending approval.*

**A2 — The sample document is `ORBITAL_SERIES_B` serialised, not new material.**
This makes the slice's central claim checkable: the parsed packet is asserted
*equal* to the packet frozen inside the prototype, so intake provably added no
semantics. A freshly written sample would have made "the pipeline works" and
"intake guessed well" indistinguishable. Cost: the slice demonstrates the
machinery for experimental objective O1, not O1 itself, which requires real
material. No O1 claim is made anywhere in this work.

**A3 — Artifacts are written to `reports/vertical-slice/<packet-id>/`, not to a
dated directory.** `reports/README.md` describes `reports/YYYY-MM-DD/report.md`
for *infrastructure utility* output, and `daale/reports.py` builds those paths
from `date.today()`. A clock in the path would break the success criterion that
repeated runs behave deterministically. The directory is named by packet id
instead; `metadata.json` is kept, matching the convention's second file. Flagged
as a mild divergence from a convention that was written for a different
producer.

**A4 — The rendered report is written as `06-report.txt`, not `report.md`.** It
is the byte-exact output of `core.report.render`. Reformatting it as Markdown
would make the renderer stop being a pure projection of the record, which is
commitment A8 / E9 and the `projection-integrity` check. Verbatim was judged to
outrank the filename convention.

**A5 — Serialisation reuses `choir_prototype.core.replay._canonical`, a private
function.** It is the exact reduction `record_digest` is computed over. A local
copy would be a second answer to the same question, and the first time the two
disagreed the persisted artifacts would silently stop matching the hash that
vouches for them. The import is deliberate and is documented at the import site.

**A6 — Intake validates structure but not vocabulary.** An unrecognised source
`kind` or data-point `status` is not rejected; it falls through to the
translator's existing conservative defaults (`ASSERTED`, `UNKNOWN`). Duplicating
that mapping at intake would create a second place to change it.

### Specification ambiguities surfaced

- **`reports/` conventions are scoped to one producer.** `reports/README.md`
  describes the shape `daale/reports.py` builds and says utilities "may" create
  it. It does not say whether a non-`daale` producer must follow it. Resolved
  conservatively for now — see A3 and A4 — and worth settling if a third
  producer appears.
- **The instruction's stage list and the frozen stage counts do not line up.**
  The instruction names six stages; `FROZEN.md` §1 says seven and
  `choir_prototype/README.md` says five. This is the known discrepancy already
  recorded in `CHOIR_v0.1_RESEARCH_FREEZE.md` §3.4, which resolves it: stage
  *ordering* is the frozen commitment, stage *count* is not load-bearing. The
  slice follows the ordering and does not adopt any count.

### Questions requiring human review

1. **`DECISION-002` needs approval or rejection.** Everything in the slice rests
   on it. Rejection is contained: delete the directory and its two matrix rows.
2. **The governance gap is now wider.** `IMPLEMENTATION_QUEUE.md` forbids
   implementing runtime behavior without an approved specification, and every
   `SPEC-*.md` is still empty. This work was authorized by direct architectural
   instruction, which the queue's own rules permit as an alternative to a
   specification — but it is the third code area now sitting outside the
   traceability chain. The rule and the repository continue to disagree, and
   which gives way remains an architectural decision rather than a maintenance
   task.
3. **Whether the slice belongs under `applications/investment/`.** It was placed
   there because that directory is described as the domain-application area and
   the slice is bound to one domain. If the intent is that a vertical slice is
   *pipeline* infrastructure rather than a domain application, it is in the
   wrong place — but moving it is a repository-organization change, which is
   frozen, so it was not made.

### Remaining work

Not started, and deliberately out of scope for this slice:

- A second document, or any document that is not the frozen sample. Needs A1
  settled first.
- Real case material, which is what experimental objective O1 actually requires.
- Provenance to source loci (`CHOIR_v0.1_RESEARCH_FREEZE.md` §4.3). This is the
  natural successor to A1 and should be taken deliberately, with a locus model,
  not folded into a plumbing change.
- `mypy` coverage. The slice is not in `[tool.mypy] packages`, because that
  section is `strict = true` and the slice imports `choir_prototype`, which is
  not type-checked and is frozen against being made so. `mypy` is not part of
  the validation gate, so nothing currently regresses; recorded rather than
  worked around.

---

## 2026-08-06 — YUKTI application V1: the investment committee workspace

**Instruction.** The engine is stable and the vertical slice is the canonical
reference implementation. Build the YUKTI product around it: professional
institutional software, not a chatbot, exposing institutional concepts rather
than computational ones.

### Completed

- `applications/investment/workspace/` — Version 1 of the application, runnable
  with `python -m applications.investment.workspace` on port 8770.
  - `cases.py` — Case, Source, Figure, FlaggedConflict, LedgerEntry, and a
    JSON-file case store.
  - `diligence.py` — the standard diligence schedule (15 figures, 4 review
    areas), the intake vocabularies, and the institutional relabelling of engine
    output.
  - `analysis.py` — the only door to the engine. Composes the document, calls
    the vertical slice, projects the persisted record.
  - `server.py`, `__main__.py` — the application server, standard library only.
  - `ui/` — the workspace: case register, intake, material, judgment, audit.
  - `tests/test_workspace.py` — 26 tests.
  - `README.md` — the product architecture, journeys, and stated non-goals.
- `docs/architecture/DECISION-003_product_application_architecture.md` — the four
  architectural choices the instruction did not settle. **Pending approval.**

**Verified by use, not only by test.** The full journey was walked in a browser:
open case → load material → request judgment → record decision. The reference
case reaches `Proceed With Conditions` at `Low` confidence, with 5 conditions,
1 disagreement and 1 independent agreement, and the ledger entry pins the
committee's decision to record digest `9ba1d434…`.

**Validation gate:** `ruff check`, `ruff format --check`, `python -m unittest`,
`python -m compileall` all pass. `--frozen` reports INTACT and `--audit` reports
portability 1.00 with the application in the tree.

### A defect that only using the product found

The vocabulary test passed while the screen read:

> Claim clm-007 (net_revenue_retention_pct) is contradicted elsewhere in the
> packet; this finding is provisional.

The test had checked the headline fields — recommendation, confidence, review
area and topic names — and not the unresolved questions. Walking the workflow in
a browser surfaced it immediately.

Two things were fixed, and the second matters more: the relabelling was extended
to cover identifiers and the word "packet", and the test was rewritten to
collect *every* string a judgment can render rather than a sample. Recorded here
because the lesson generalises — a leak test that enumerates surfaces will
always trail the surfaces that exist.

### Assumptions

**B1 — §5's engineering exclusions are scoped to the engine, not the
repository.** `CHOIR_v0.1_RESEARCH_FREEZE.md` §5 excludes UI, APIs, databases
and authentication from v0.1. The product instruction requires the first two.
Read conservatively: the *engine* must not grow them, and a product layer
outside it does not violate the exclusion. The database exclusion was taken
literally — there is no database. *This is the conflict most worth an explicit
ruling; see `DECISION-003`.*

**B2 — The product uses the existing prototype's vocabulary, with two
departures.** "RIK Positions" became "Review areas" because RIK belongs to the
legacy path retired by `DECISION-001`. "Propositions" is not offered at all,
because the engine has no decision-proposition object (research freeze §4.4) and
inventing one would be product architecture answering an open research question.

**B3 — Engine prose is relabelled by whole-word substitution.** Some engine
strings are composed, not looked up, and the engine is frozen. The substitution
is mechanical and total; prose containing no internal name passes through byte
for byte, which is asserted by test. It is the only place the product touches the
engine's own words and should be reviewed as such.

**B4 — The judgment view is built by reading `05-record.json` back**, not from
live objects. Slower, and it buys the guarantee that the product cannot display
a conclusion the record does not contain.

**B5 — Case metadata never reaches the engine.** Owner, opened-on date,
requested decision and thesis are institutional metadata. Passing them through
would change the document and therefore the record digest without changing a
single conclusion. Asserted by test.

**B6 — Case state lives in `reports/workspace/`.** `reports/README.md` reserves
that tree for "Prototype-001 report output", and a case file is institutional
state rather than report output. The convention is stretched knowingly; the
alternatives were a database (excluded) or a new top-level directory
(organization frozen).

**B7 — Design tokens are restated in the workspace stylesheet** rather than
imported, because the application server serves its own UI root and cannot reach
`website/`. The website file remains the source of truth and wins on any
divergence. This is a real duplication and the website architecture doc calls a
literal value outside the token file a defect — recorded as a question below.

**B8 — A "Use reference material" action loads the worked example** into a case
so a first-time user can walk the workflow without typing fifteen figures. It is
read from the reference implementation's own document rather than copied, and is
labelled as reference material wherever it appears.

### Specification ambiguities surfaced

- **Whether §5 governs the repository or the engine.** See B1. This is the one
  that should be ruled on before more product work.
- **Whether product UIs may consume the website design tokens.** The website
  architecture treats a literal token value outside `tokens.design.css` as a
  defect, but provides no mechanism for a separately-served application to
  consume it. See B7.
- **`reports/` has no stated owner beyond `daale`.** Now stretched twice: by the
  vertical slice (A3, previous entry) and by case storage (B6). A third producer
  should prompt a convention rather than a third stretch.

### Questions requiring human review

1. **`DECISION-003` needs approval**, particularly the "RIK Positions" → "Review
   areas" rename, which changes an existing product name.
2. **`prototype-ui/` is now superseded as the product direction but not
   removed.** It has a passing test suite and its own fixture workspace.
   Retiring it is scheduled work, not a side effect of building its replacement
   — the same treatment `DECISION-001` gave the Risk RIK provider. Two product
   UIs in one directory is a state that should not persist.
3. **The decision-proposition object is now a product-visible gap.** The
   research freeze (§4.4) records it as open and notes it may be a prerequisite
   rather than an enhancement for objective O5. Building the ledger made that
   concrete: the product records a decision *about a case*, not a motion a body
   votes on. A committee that wants to vote on a specific proposition cannot.
4. **No authentication or access control.** A tool that records institutional
   decisions and attributes them to named people needs both. Out of scope for
   this slice and stated in the application's README, but it is the first thing
   standing between this and real use.
5. **Concurrent edits overwrite.** Whole-record material replacement means two
   analysts editing one case lose each other's work silently. Acceptable for a
   local single-user tool; not acceptable for a committee.

### Remaining work

Not started, and deliberately out of scope for this slice:

- Retiring `prototype-ui/`, once question 2 is settled.
- Any second domain. The workspace is bound to the investment domain because
  that is what the engine's reference implementation supports.
- Document upload. Sources are registered by reference and description; the file
  stays where the institution already keeps it. Upload implies extraction, which
  is the open question `DECISION-002` deliberately did not answer.
- Anything from the research freeze §5 institutional layer list: cross-case
  memory, precedent, calibration, committee workflow optimisation, human roles
  and accountability. Named here only so it is clear they were considered and
  excluded rather than forgotten.

---

## 2026-08-06 — Supersession, and the close of the product cycle

**Instruction.** The architect ruled on every open question from the previous
entry. Implement the supersession model and verify its invariants before
continuing.

### Rulings received, and what they closed

| Ruling | Closed |
|---|---|
| Implement supersession; history is append-only; do not freeze cases | The audit-trail defect. `DECISION-004`. |
| Research freeze §5 applies to the engine, not to product layers | Assumption B1 and the specification conflict. `DECISION-003` approved. |
| `DECISION-002` broadened: product-generated packet documents approved | The boundary overrun recorded in the previous entry. |
| "Review areas" approved as canonical product terminology | Assumption B2. |

Every assumption carried by the previous two entries is now either approved or
superseded by a ruling. Nothing from those entries remains open.

### Completed

- **Supersession implemented.** Judgments are append-only, identified,
  dated, and marked superseded rather than replaced. Artifacts moved to
  `reports/workspace/<case>/judgments/<judgment-id>/`, written once. Decisions
  bind to a `judgment_id` permanently. Full rationale and the invariant-to-test
  map are in `DECISION-004`.
- `analysis.verify_ledger` — the invariant made checkable, surfaced in the
  workspace beside every ledger entry with a visible failure state.
- UI: judgment history with supersession chain, a banner on superseded
  judgments, per-decision verification status, and navigation from a decision to
  the exact judgment it was taken against.
- `TestSupersession` — 7 tests, one per named invariant. Suite is 34 tests for
  the workspace, 160 for the repository.
- `DECISION-002`, `DECISION-003` marked approved; `DECISION-004` written.

**Validation gate:** ruff check, ruff format --check, 160 unittest, compileall
all pass. `--frozen` INTACT, `--audit` portability 1.00.

**Verified by use.** In the running application: open case → material → analyse
→ decide → edit a figure → re-analyse. `JUDGMENT-001` is superseded by
`JUDGMENT-002`, digests differ, and `LEDGER-001` still binds to `JUDGMENT-001`
and still verifies. The superseded judgment reads in full, report included.

### Assumptions

**C1 — An analysis reproducing the current digest returns the existing judgment
rather than creating a duplicate.** The engine is deterministic, so an identical
digest means the material reached the same conclusion. The alternative records
an event in institutional history that never happened. Reviewable: an
institution that wants "we re-checked on the 12th and it still held" as a
first-class event would need a re-affirmation record, which this is not.

**C2 — Decisions bind forward only.** A decision can only be recorded against
the judgment in force. Recording one against a superseded judgment would be
minuting a meeting into the past.

**C3 — No migration path was written for the storage layout change.** The only
data in the old layout was generated development data, which was deleted. A
deployed system would have required one; this is the first change that would
have.

**C4 — Retention is unbounded.** Every distinct analysis is kept forever, at
roughly 70 KB per judgment. Retention is institutional policy, not an
engineering decision, and is deliberately unanswered.

### Questions requiring human review

Carried forward, unchanged and still open:

1. **Authentication and access control.** Still the first thing standing between
   this and real use, now more so: the product records attributed, permanent,
   append-only institutional history with no identity layer beneath it.
2. **Concurrent edits overwrite silently.** Material is replaced wholesale.
3. **`prototype-ui/` retirement**, now unblocked — the "Review areas" rename it
   was waiting on has been approved.
4. **The decision-proposition object.** Unchanged by this cycle and still the
   most product-visible gap.

### Remaining work

The product cycle is closed. No further feature work was started, per
instruction. The next entry should be the outcome of the architectural proposal
requested at the close of this cycle.

---

## 2026-08-06 — The Material Snapshot layer

**Instruction.** Authorizations 1–8. Implement the first immutable institutional
identity layer: material identity, `material_digest`, snapshot registry,
supersession re-keying, ledger verification against material identity.

### The defect this cycle closed

An independent architectural review claimed an execution ID derived from emitted
output can collide when input fields go unobserved. Rather than accepting or
dismissing it, the claim was tested against the actual translator:

```
STATUS reported vs estimated
  document differs : True
  digest A         : 580a5b279f18a7f13b71e5d3
  digest B         : 580a5b279f18a7f13b71e5d3
  COLLISION        : True
```

`_STATUS_TO_UNCERTAINTY` maps both `reported` and `estimated` to
`Uncertainty.LIKELY`, and a figure's status appears nowhere else in the IR. Two
materially different diligence packs, one hash.

Compounding: supersession, shipped the previous cycle, keyed history on the
record digest. Restating a figure's standing — a real change to what the
institution claims about its own evidence — produced **no new judgment**. The
material moved and the record said nothing happened. The comment in that code
claimed "an identical digest means the material reached the same conclusion";
true, but it was written as though it meant identical *material*.

### Completed

- `workspace/material.py` — `MaterialSnapshot`, `compute_material_digest`,
  `next_snapshot`, hash scheme `yukti-material/1`.
- Append-only snapshot registry on `Case`; `JudgmentRecord` and `LedgerEntry`
  gain `material_digest` and `snapshot_id`.
- Supersession re-keyed on material identity.
- `DigestCheck` reports `record_resolves` and `material_resolves` as
  independent claims.
- Product surfaces: material register on the overview, snapshot and both digests
  on judgment and audit views, per-decision verification on both axes, judgment
  history marking "same conclusion, different material".
- `DECISION-006` (this layer) and `DECISION-005` (open ADR on DAALE).
- `TestMaterialIdentity` — 12 tests. Suite: 46 workspace, **172 repository**.

**Validation gate:** ruff check, ruff format --check, 172 unittest, compileall
all pass. `--frozen` INTACT, `--audit` portability 1.00.

**Verified live**, not only by test. In the running application: material stated
as `reported`, analysed, decided; the same figure restated as `estimated` and
re-analysed. Result — `reasoning_identical: true`, `material_differs: true`,
`JUDGMENT-001 -> JUDGMENT-002`, register `MATERIAL-001`/`MATERIAL-002`, and the
decision still bound to `JUDGMENT-001`/`MATERIAL-001` verifying on both axes.
Under the previous behaviour no second judgment would have existed.

### On the independent review

Its diagnosis converged with ours; its prescription would have broken the
freeze. Recorded because the distinction is the reusable lesson.

**It does not describe this repository.** Verified: `authority/lock.py`,
`engine/core.py`, `experiments/runner.py`, `trace/events.py`,
`provenance/model.py`, `judgment/basis.py`, `contract/` and `evaluators.py` are
all absent; `daale/` contains no `evaluate`, no `judgment`, no
`INSUFFICIENT_BASIS`; its suite is 12 tests, not the 5 the review cites.

Its **configurable hybrid evaluator** (forward / backward / certificate / Rete)
would replace CHOIR v0.1 outright, and its Pydantic-strict recommendation would
break the engine's deliberate standard-library-only constraint. Adopted where it
was right — input-bound identity — and declined where it assumed a different
codebase. `DECISION-005` exists so that distinction cannot be lost.

### Assumptions

**D1 — Material identity is finer-grained than reasoning identity, and the
digest is order-sensitive.** Claim ids in the engine are positional, so an
order-insensitive digest would be *coarser* than the record it must be finer
than, and supersession would suppress genuinely different judgments. Defended by
`test_reordering_the_schedule_is_a_material_change`.

**D2 — Snapshots are appended on material save, not on analysis.** The registry
records what the institution assembled and when, per Authorization 3, including
states never analysed.

**D3 — Material digests may recur.** Reverting material is a new institutional
event with a new snapshot id and the earlier digest. The register is a timeline,
not a set.

**D4 — Case metadata is excluded from material identity.** Re-assigning a case
must not fabricate new material. Asserted by test.

**D5 — Pre-existing decisions are not back-filled.** They verify on reasoning
and read as *material not identified*, because back-filling would assert
something nobody attested.

**D6 — Sources remain references.** Per Authorization 6, no document is stored,
hashed or ingested. Material identity covers the assembled material, not
per-document identity.

### Numbering (Authorization 8)

**No renumbering was required.** Verified: `DECISION-001`, `-002`, `-003` are in
git history with no duplicates; `-004` was uncommitted and is the correct next
number. The "DECISION-003 — Supersession" reference in the authorization was
prose; renumbering supersession to 003 would have collided with the committed
product-architecture note. `-005` and `-006` continue the sequence.

### Remaining unresolved uncertainties

1. **`DECISION-005` is open.** No implementation may assume a definition of
   DAALE. This cycle was deliberately built with no DAALE dependency.
2. **Per-document identity does not exist.** A source is a reference; nothing
   binds it to a specific version of a specific file. This is the next layer of
   the provenance floor and needs Authorization 6 revisited.
3. **Evidence formation is still unrecorded.** A human typing `status:
   estimated` performs an unaudited judgement. Material identity now records
   *that they did it and when*, but not *why* or *from what*.
4. **Authentication is still absent** beneath an append-only attributed record.
5. **Concurrent edits still overwrite silently.**

---

## 2026-08-13 — DAALE v0, Phase 0: the conformance lock

**Instruction.** Implement the established DAALE v0 execution plan while
remaining compliant with `DECISION-005`. Treat that ADR as an implementation
constraint rather than a blanket prohibition: proceed unless the specific step
requires an assumption it prohibits, and if one does, stop at that dependency
rather than halting the programme.

### The boundary, located before any code was written

The v0 plan's Phase 0 is "map each frozen CHOIR commitment to executable
contract + test." That step needs no answer to *what DAALE is*: the commitments
are CHOIR's, they are frozen, and they are identical under all four options
`DECISION-005` leaves open. It is also the route the research freeze §9 already
prescribed — "until it is resolved, DAALE implementation should attach to §3
commitments rather than to prototype internals."

**Phase 1 is where the boundary actually falls, and it falls at one point.** A
D-Core is a deterministic executor, and to execute it must either call the
frozen prototype's kernels or evaluate for itself. Those are options B and A of
`DECISION-005` verbatim. There is no neutral third choice, because *who
evaluates* is precisely the question the ADR asks. Phase 1 is therefore blocked
on that ADR and nothing else; Phases 0 is not.

### Completed

- `daale/conformance/` — Phase 0.
  - `commitments.py` — all 28 frozen §3 commitments (E1–E13, A1–A11, X1–X4) as
    a machine-readable register: identifier, statement, support status, and the
    evidence that exercises it. A transcription, not an interpretation.
  - `lock.py` — resolves every citation against the repository by parsing source
    into syntax trees. Three evidence kinds: `test`, `check` (a CLI flag or one
    of the four replay checks), `decision` (an ADR, which must be *approved* to
    resolve).
  - `report.py` — a pure projection. Deterministic text and JSON.
  - `daale conformance` CLI subcommand; artifacts to
    `reports/daale/conformance/`.
- `daale/tests/test_conformance.py` — 21 tests. Suite: 33 for `daale/`,
  **193 for the repository** (was 172).

**Result:** 28 commitments — 20 conforming, 8 unexercised, **0 unresolved.**

**Validation gate:** ruff check, ruff format --check, 193 unittest, compileall
all pass. `mypy --strict` clean across 36 files. `--frozen` INTACT (tree digest
unchanged), `--audit` portability 1.00.

### What the lock is for, and what it deliberately is not

It is a tripwire in the sense `FROZEN.md` uses the word. It does **not** re-run
the reasoning — `--replay` and the prototype suite already do, and a second
answer to the same question is worse than none. It catches the failure those
cannot see: a frozen commitment whose evidence has quietly stopped existing.
Rename `TestKernelIndependence` today and every test passes, `--frozen` still
reports INTACT, and commitment A3 silently loses the only thing demonstrating
it. The lock fails.

### Two defects found while building it

Both found the same way the Material Snapshot cycle found its collision — by
testing a claim rather than asserting it.

1. **A negative result from a broken instrument.** The first repository-wide
   search for the v0 plan's vocabulary returned zero hits for *everything*,
   including `INSUFFICIENT_BASIS`, which §3 A11 demonstrably contains. The
   search tool was failing silently. Re-run through a different one:
   `INSUFFICIENT_BASIS` 27 hits, `D-Core`/`R-Fabric` 0. Only then was the zero
   worth anything. `test_a_fabricated_citation_does_not_resolve` and its two
   siblings institutionalise that lesson — a resolver that always answers
   "found" is indistinguishable from a working one until it is handed something
   that does not exist.
2. **Decision-status parsing swallowed the following sentence.** Reading to end
   of line reported `DECISION-001`'s status as "Approved 2026-08-04.** Recorded
   retrospectively — the repository", which both misquoted the note and dragged
   non-ASCII prose into an artifact that must print on any console. Truncated at
   the bold run, and typographic characters are now normalised. Research freeze
   §9 names locale as one of the ways an integrity mechanism ends up working
   only on the machine that produced it; this was that failure mode, caught
   early.

### Assumptions

**F1 — `daale/conformance/` is a new package inside `daale/`, not a move.**
`DECISION-005` forbids moving anything *into or out of* `daale/` on an assumed
answer. Nothing was moved. `daale/README.md` already declares named subpackages
reserved for approved work, so adding one follows the existing declared pattern
rather than changing repository organization. Reviewable: someone reading the
ADR strictly may still consider any new code in `daale/` to presume the name
survives, which is option C's concern.

**F2 — Evidence is resolved by reading source, never by importing it.** This is
the mechanical form of the no-engine-dependency claim and is asserted in a
subprocess by `test_conformance_never_imports_the_engine`. It is also how
`freeze.py` already works, so the mechanism is idiomatic here.

**F3 — An unexercised commitment is never reported as conforming.** The three
outcomes partition the register and `UNEXERCISED` is not a softer pass.

**F4 — A commitment marked demonstrated that cites nothing is reported, not
failed.** It is a hole in the chain rather than a broken link, and failing on it
would assert the commitment is *not* demonstrated, which the lock does not know.

**F5 — The unexercised set is pinned by test.** Closing one of those holes, or
opening a new one, is now a deliberate act that changes a test rather than a
drift nobody notices.

### Questions requiring human review

1. **`DECISION-005` still needs acceptance before Phase 1.** The exact
   dependency is named above: a D-Core cannot be written without ruling whether
   DAALE calls the frozen kernels or evaluates for itself.
2. **E12 is marked demonstrated and cites nothing.** Either evidence exists and
   was never recorded, or §3's status for it is optimistic. This is a question
   about the freeze, not about the lock, and the lock should not answer it.
3. **The v0 plan's §14 repository structure conflicts with an approved
   decision.** It proposes a top-level `yukti/`; `DECISION-003` explicitly
   rejected one and approved `applications/investment/workspace/`. Adopting §14
   as written would reverse an approved choice. Flagged, not acted on.
4. **The v0 plan itself is recorded nowhere in this repository.** It exists as
   an external document whose own status line reads "DAALE implementation
   proposal". Phase 0 was implemented under direct architectural instruction,
   which the rules permit; the plan's disposition is still unrecorded.

### Remaining work

- Phases 1–8. Phase 1 is blocked on `DECISION-005` at the point named above.
- Carried forward unchanged: authentication, concurrent-edit handling,
  `prototype-ui/` retirement, per-document identity, the decision-proposition
  object.

---

## 2026-08-13 — DAALE v0 Phases 1–2, and the classification of the eight

**Instruction.** DAALE v0 execution authorization. Phase 0 accepted as the v0
baseline. Implement all subsequent v0 work not requiring the evaluator choice in
`DECISION-005`; stop at that boundary and present it rather than choosing A or B
implicitly. Classify the eight unexercised commitments rather than implementing
them. Preserve `E12` as an evidence discrepancy. `DECISION-003` remains
authoritative for repository organization; the proposal's §14 top-level `yukti/`
is not authorized. Do not backport CHOIR v1.

### Completed

**Phases 1–2 — `daale/execution/`.**

- `identity.py` — execution identity computed over the **input** package at full
  fidelity, never over a result.
- `contract.py` — CHOIR contract validation. Required sections transcribed from
  commitment A2; identifier uniqueness; referential integrity, which is X4
  applied one step earlier, at the input boundary.
- `state.py` — the Reasoning State Store. Six areas per plan §6, versioned
  canonical objects, provenance and dependents, append-only snapshots.
  Canonical writes require an `ExecutionLease`; executions are serialised;
  stale reads are refused.
- `trace.py` — append-only ordered events, no clock.
- `commit.py` — the candidate lifecycle and the seven-check gate.
- `dcore.py` — the D-Core.
- `tests/test_execution.py` — 37 tests.

**Classification — `daale/conformance/classification.py`.** The eight
unexercised commitments, each with the source that says why it is unimplemented,
across five categories: `research-open` (E4, E5, E7), `prototype-limit` (E6),
`specified-not-implemented` (E3, E11), `decision-required` (E10),
`evidence-discrepancy` (E12). Surfaced in the conformance artifact. 7 tests.

Suite: **77 for `daale/`, 237 for the repository** (was 193).

**Validation gate:** ruff check, ruff format --check, 237 unittest, compileall
all pass. `mypy --strict` clean across 44 files. `--frozen` INTACT, `--audit`
portability 1.00.

**Verified live**, not only by test. Three candidates through one execution:
`rfabric` committed, `llm` escalated to review, one without provenance rejected.
Ten trace events, `emits_judgment: False` with its reason attached.

### The boundary, and why nothing was stubbed

The D-Core implements eight of the plan's nine listed responsibilities. The
ninth, emitting a judgment, requires evaluated results, and evaluation requires
deciding whether DAALE calls the frozen kernels or evaluates for itself —
options B and A of `DECISION-005` verbatim.

**No evaluator was written and no placeholder was left in its place.** A stub
raising `NotImplementedError` would still assert that the evaluator belongs
inside DAALE, which is one of the answers. The candidate-to-commit protocol
means the commit authority never needs to evaluate: it takes candidates from
whoever produced them and decides admissibility. `test_the_d_core_has_no_
evaluator` guards the boundary mechanically, because a boundary defended only
by a docstring erodes one convenient method at a time.

### Assumptions

**G1 — Execution identity is input-bound and order-sensitive.** Directly
inherited from the `DECISION-006` collision: an identifier derived from what a
computation emitted collides when the computation does not observe part of its
input. `test_inputs_the_engine_would_flatten_are_still_distinct` is the
regression, using the same `reported`/`estimated` pair that collided before.

**G2 — Contract validation is structural only.** It transcribes A2 and checks
referential integrity. It makes no semantic judgement, because that is CHOIR's
and reaching it needs the evaluator.

**G3 — A non-deterministic origin escalates rather than commits.** The plan
states `REVIEW_REQUIRED` exists and that model output requires review, but does
not enumerate which origins escalate. The conservative reading is taken:
`dcore`, `rfabric` and `algorithm` may commit; anything else escalates. This is
the plan's LLM-authority-leakage control made mechanical, and it is the
assumption in this cycle most worth an explicit ruling.

**G4 — Check 4 is `INACTIVE`, not passing.** Plan conformance needs the Phase 3
planner. A check that returns `True` because it has nothing to check makes a
gate look stronger than it is, so it is reported as not-run in every record.

**G5 — `INSUFFICIENT_BASIS` here is the floor case, not CHOIR's basis rule.**
Emitted when nothing was committed. CHOIR's full rule lives in the frozen
synthesizer and needs the evaluator. Stated on the summary rather than left for
a reader to infer.

**G6 — Classification is not a work list.** Recorded because the failure mode is
obvious in hindsight: "unexercised" reads like a to-do, and closing a §4
research programme to tidy a report is precisely what research freeze §1 exists
to prevent. `test_research_open_items_are_not_treated_as_tasks` pins it.

### Findings

- **No CHOIR v1 exists in this repository.** Verified: the only `v1` matches are
  website, film and motion-system assets. "Do not backport CHOIR v1" is
  satisfied by absence, and reconciliation remains a post-v0 act against
  something not present here.
- **`E12` remains an evidence discrepancy** and was not closed. Finding
  something plausible to cite would have manufactured the traceability the lock
  exists to measure.

### Remaining v0 work

- **Phase 3 — planner and dependency index.** The dependency index over IR
  objects is structural and unblocked. The *planner* is not: an execution plan
  is a plan over units of evaluation, which is the `DECISION-005` choice.
- **Phase 4 — R-Fabric parallelism.** Blocked: there are no kernels to
  parallelise without the evaluator.
- **Phase 5 — shadow/replay lanes.** Blocked for the same reason. The snapshot
  and lease machinery they need is already in place.
- **Phase 6 — coprocessor adapters.** Partially unblocked: the gate already
  distinguishes origins and escalates non-deterministic ones. Actual adapters
  are proposal *producers*, which is where the boundary bites.
- **Phase 7 — YUKTI debugger integration.** Product layer, governed by
  `DECISION-003`. Not started.
- **Phase 8 — institutional pilot.** Not code.
