# YUKTI

YUKTI is an early-stage repository for CHOIR research artifacts and the DAALE
implementation scaffold.

The repository is intentionally conservative. Existing files and directories
name architectural areas, but most runtime behavior has not been specified or
implemented yet. Implementation work should therefore preserve the current
architecture, document gaps clearly, and avoid filling those gaps with guessed
logic.

## Repository Map

- `MANIFESTO.md`: Current research prompt and constraints. This is the best
  available description of the repository posture.
- `choir/`: CHOIR research, ontology, proposal, and specification workspace.
- `daale/`: DAALE implementation scaffold aligned to the existing architecture
  names.
- `docs/`: Project documentation, architecture notes, diagrams, glossary, and
  meeting notes.
- `applications/`: Domain application placeholders.
- `tools/`: Developer and research tooling placeholders.

## Current Implementation Status

DAALE currently contains named Python ontology modules, but no execution logic.
The modules are documented scaffolds so future implementation can attach to
approved specifications without renaming architectural components.

CHOIR currently contains research and specification placeholders. Empty
research files should be filled with source material, criteria, or accepted
decisions before implementation depends on them.

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

The current repository has no runtime dependencies. Developer validation uses
Ruff plus standard-library Python checks. Install developer tooling with:

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
