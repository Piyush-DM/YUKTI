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
