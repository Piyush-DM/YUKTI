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
- `daale/`: DAALE implementation scaffold. Ontology modules are documented
  boundaries with no behavior; the working code is environment and reporting
  tooling.
- `docs/`: Architecture decision notes, development and validation procedure,
  repository-health process, and the traceability matrix.
- `applications/`: Domain applications. Currently the investment prototype
  vertical slice.
- `reports/`: Reserved for generated report output. Generated files are not
  committed.
- `website/`: YUKTI public website. Static HTML, CSS, and vanilla JavaScript,
  built with Vite as a dev-server and bundler only.

## Current Implementation Status

Three code areas exist, at very different stages. They are not yet reconciled
with one another, and the difference matters when reading the repository.

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

**`daale/` — scaffold only.** The ontology modules under `daale/ontology/` are
docstrings that name planned boundaries and define no behavior. The executable
code in `daale/` is configuration, environment diagnostics, logging, and report
plumbing. DAALE currently contains no reasoning logic.

**`applications/investment/` — prototype vertical slice.** A UI and an
executable Risk RIK path, isolated from DAALE engine architecture. Its
model-backed provider is retained only as legacy; see
`docs/architecture/DECISION-001_reasoning_execution_substrate.md`.

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
