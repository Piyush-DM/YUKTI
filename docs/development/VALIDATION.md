# Validation

This document records the repository validation gate used by implementation
engineering. It exists so validation failures can be reproduced and fixed
without changing architecture or runtime behavior.

## Developer Tooling

Install developer tooling from the repository directory:

```powershell
uv venv .venv
uv pip install -r requirements-dev.txt
```

If validating outside the virtual environment on Windows, a user-level Python
install may place command-line tools in a versioned Python user Scripts
directory before that directory is available on `PATH`. Opening a new terminal
often resolves this. For the current PowerShell session, the directory can be
prepended with:

```powershell
$userSite = python -m site --user-site
$userScripts = Join-Path (Split-Path $userSite -Parent) "Scripts"
$env:Path = "$userScripts;$env:Path"
```

## Validation Gate

Run the full gate from the repository directory:

```powershell
ruff check .
ruff format --check .
python -m unittest
python -m compileall .
```

If any command fails, stop implementation-queue work, fix the failure if it is
inside the implementation-engineering boundary, and rerun the full gate.

The approved toolchain is recorded in
`docs/development/DEVELOPMENT_ENVIRONMENT.md`.

## Environment Doctor

After installing the package into the virtual environment, run:

```powershell
daale doctor
```

The doctor command verifies the Python version, virtual environment state,
configured dependencies, configured API key names, required repository paths,
and reports-directory writability. It does not validate API key values or run
DAALE reasoning logic.
