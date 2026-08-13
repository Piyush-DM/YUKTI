# YUKTI

YUKTI is an early-stage repository for CHOIR research artifacts and the DAALE
implementation scaffold.

The repository is intentionally conservative. Existing files and directories
name architectural areas, but most runtime behavior has not been specified or
implemented yet. Implementation work should therefore preserve the current
architecture, document gaps clearly, and avoid filling those gaps with guessed
logic.

## Repository Map

- `CHOIR_v0.1_RESEARCH_FREEZE.md`: **Canonical reference for CHOIR v0.1.** The
  engineering and research freeze — frozen commitments, open research
  questions, what is out of scope, and the falsification conditions. Read this
  before implementing anything.
- `MANIFESTO.md`: Current research prompt and constraints. This is the best
  available description of the repository posture.
- `choir/`: CHOIR research, ontology, proposal, and specification workspace.
  The research programme under `choir/research/phase-*/` is drafted; the
  `SPEC-*`, `R00*`, `ontology/` and `proposals/` files are empty placeholders.
- `choir_prototype/`: Executable CHOIR prototype, **frozen at V0.1**. The only
  running reasoning pipeline in the repository. Deterministic, no network, no
  model calls. See `choir_prototype/README.md` and `choir_prototype/FROZEN.md`.
- `DAALE_v0_CLOSURE.md`: **Canonical reference for DAALE v0.** The closure note
  and architectural freeze — what v0 contains, what is frozen, what it does not
  do, and what is carried out of it unresolved. Read this before changing
  anything under `daale/`.
- `daale/`: DAALE. `conformance/` and `execution/` are implemented and frozen
  at v0; the remaining areas are documented boundaries with no behavior.
- `docs/`: Architecture decision notes, development and validation procedure,
  repository-health process, and the traceability matrix.
- `applications/`: Domain applications. The investment committee workspace
  (the YUKTI application, V1), the vertical slice that is its reasoning
  reference implementation, and two superseded prototypes.
- `reports/`: Reserved for generated report output. Generated files are not
  committed.
- `website/`: YUKTI public website. Static HTML, CSS, and vanilla JavaScript,
  built with Vite as a dev-server and bundler only.

## Current Implementation Status

Three code areas exist, at very different stages. They are not yet reconciled
with one another, and the difference matters when reading the repository.
Reconciling DAALE against CHOIR is deliberately deferred: it is the first item
after a ruling on `DECISION-005`.

**`choir_prototype/` — executable, frozen at V0.1.** A deterministic pipeline
that carries a domain packet through translation, independent reasoning
kernels, structured artifacts, and synthesis to an institutional
recommendation. It measures domain independence rather than asserting it
(`--audit`, portability 1.00 across four domains with a hold-out control). Its
README states it is not DAALE architecture; where the prototype and DAALE
eventually meet is an open architectural question, not a settled one.

*Two corrections that cannot be made inside the package.* Every file in
`choir_prototype/` is hash-pinned, so editing one to fix its prose would trip
the freeze and destroy the archival record — the same tradeoff the project
already resolved in `FROZEN.md` §4, in favor of the evidence. Recorded here
instead:

1. **`FROZEN.md` §6 is out of date.** It states the work is not under version
   control and instructs the reader to run `git init`. That has been done: the
   prototype was committed in `2c7103b` and tagged `v0.1`.
2. **Freeze verification depends on `.gitattributes`.** `freeze.py` pins
   Markdown by content hash. With Git's Windows default (`core.autocrlf=true`)
   a checkout rewrites those files to CRLF, and `--frozen` reports the
   architecture as MODIFIED on a machine that changed nothing — verified by
   cloning this repository and running the check. The root `.gitattributes`
   normalises line endings to LF and is what keeps the freeze verifiable off
   the machine that produced it. Do not delete it.

**`daale/` — v0 closed and frozen, 2026-08-14.** A canonical control plane, and
the conformance machinery that keeps it honest.

`conformance/` holds the twenty-eight frozen CHOIR v0.1 §3 commitments as a
machine-readable register and a lock that resolves every piece of evidence they
rest on — 20 conforming, 8 unexercised and classified, 0 unresolved. It gave the
traceability chain its first real upstream end.

`execution/` holds the D-Core, the Reasoning State Store, the execution trace,
CHOIR contract validation and the candidate-to-commit gate. Anything may
propose; only the D-Core commits.

**DAALE still contains no reasoning logic, and that is v0's boundary rather than
a gap.** Emitting a judgment requires deciding whether DAALE calls the frozen
prototype's kernels or evaluates for itself — options B and A of
`DECISION-005`, which is open. There is no evaluator and no placeholder for one;
a stub would settle the ADR by implication. See `DAALE_v0_CLOSURE.md`.

The remaining areas — `ontology/`, `reasoning/`, `arbitration/`,
`traceability/`, `runtime/` — are docstrings naming planned boundaries. The rest
of the executable code in `daale/` is configuration, environment diagnostics,
logging, and report plumbing.

**`applications/investment/` — the application, the reference implementation,
and two superseded prototypes.**

`workspace/` is **Version 1 of the YUKTI application**: institutional software
for carrying an investment case from intake through an institutional judgment to
a recorded committee decision. It treats CHOIR as infrastructure — it calls the
vertical slice and reads back the record it wrote, and a user never sees a
kernel, a translator or an intermediate representation outside the audit view.
Run it with `python -m applications.investment.workspace`. Its architecture is
recorded in `docs/architecture/DECISION-003_product_application_architecture.md`
and is **pending approval**.

`vertical_slice/` is the repository's first complete end-to-end execution path
and the canonical reference implementation for how the engine is called:
one fixed sample document is parsed into a packet, carried through the frozen
prototype's translation, kernels and synthesis, and rendered as the canonical
execution report, with every intermediate stage persisted to `reports/` for
inspection. It adds a document intake layer and nothing else — `choir_prototype/`
is called as a library and is not modified, so `--frozen` still reports INTACT
and `--audit` still reports portability 1.00. The one architectural choice it
required, what a "document" is for v0.1, is recorded in
`docs/architecture/DECISION-002_document_intake_for_the_vertical_slice.md` and
is **pending approval**.

`prototype-ui/` and `prototype_risk_rik/` are a fixture-backed product prototype
and an executable Risk RIK path, isolated from DAALE engine architecture. Both
are superseded — the prototype UI by `workspace/`, the model-backed provider by
`docs/architecture/DECISION-001_reasoning_execution_substrate.md` — and neither
has been retired yet. Retirement is scheduled work, not a side effect of
building the replacement.

CHOIR research under `choir/research/phase-*/` is drafted but **not accepted**.
Every `SPEC-*` file is empty. Because `IMPLEMENTATION_QUEUE.md` forbids
implementing runtime behavior without an approved specification, the prototypes
above sit outside that gate — a known and unresolved governance gap recorded in
`docs/traceability/TRACEABILITY_MATRIX.md`.

## Engineering Rules

- Repository organization is frozen unless explicitly instructed otherwise.
- Treat CHOIR ontology content as provisional unless an approved specification
  states otherwise.
- Drive implementation work only from explicit specifications or direct
  architectural instructions.
- Do not invent execution behavior to satisfy tests.
- Do not rename architectural components without an approved decision.
- When no implementation work exists, perform repository maintenance only.
- When a decision is required, write the decision document first and wait for
  approval before changing behavior.

## Validation

`choir_prototype/` runs on the standard library alone, by design. The rest of
the repository does have runtime dependencies — `pyproject.toml` declares nine,
including `pydantic`, which the investment prototype requires. Install the
developer environment with:

```powershell
python -m pip install -r requirements-dev.txt
```

Run the full validation gate from the repository directory:

```powershell
ruff check .
ruff format --check .
python -m unittest
python -m compileall .
```

These checks confirm formatting, lint stability, unit-test stability, and
Python syntax validity across the scaffold.

See `docs/development/VALIDATION.md` for Windows PATH notes and the full
validation procedure.

## Website

The website has build-time Node dependencies, which are not committed. Install
them before running the site for the first time:

```powershell
npm install --prefix website
npm run dev --prefix website
```

See `website/node_modules/README.md` for details on why that directory is empty
in version control and how it is restored.
