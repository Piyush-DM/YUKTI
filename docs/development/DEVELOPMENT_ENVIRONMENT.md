# Development Environment

This document defines the approved DAALE developer toolchain. Do not add,
install, or rely on new development dependencies without updating this file as
an explicit engineering decision.

The repository organization is frozen. The tools below prepare the workstation
and validation environment only; they do not define DAALE architecture, runtime
logic, execution logic, kernels, schedulers, or providers.

## Python

- Python: 3.12 or newer.
- Virtual environment: `.venv` in the repository root.
- Package installer/environment tool: `uv`.
- Dependency file: `requirements-dev.txt`.
- Project/tool configuration: `pyproject.toml`.

Approved Python validation tools:

- `ruff`
- `mypy`
- `pytest`

Approved Python libraries for the developer environment:

- `aiofiles`
- `aiosqlite`
- `httpx`
- `jinja2`
- `orjson`
- `pydantic`
- `python-dotenv`
- `rich`
- `typer`

Formatting policy:

- Ruff is the project formatter and linter.
- Black is not installed because the project formatting policy does not require
  it.
- isort is not installed because the project formatting policy does not require
  it separately from Ruff.

## Rust

- Rust installer/toolchain manager: `rustup`.
- Toolchain: latest stable.
- Build tool: `cargo`.
- Components:
  - `clippy`
  - `rustfmt`

Rust is installed for future development readiness only. No Rust architecture
or runtime behavior is implied by this bootstrap.

## Git

- Git must be available on `PATH`.
- Repository status must be checked before and after bootstrap work.

## SQLite

- SQLite CLI must be available on `PATH`.
- Python's standard-library `sqlite3` module should also be available.

## VS Code

Approved extension recommendations:

- Python: `ms-python.python`
- Pylance: `ms-python.vscode-pylance`
- MyPy Type Checker: `ms-python.mypy-type-checker`
- Ruff: `charliermarsh.ruff`
- Even Better TOML: `tamasfe.even-better-toml`
- Rust Analyzer: `rust-lang.rust-analyzer`
- Error Lens: `usernamehw.errorlens`
- GitLens: `eamodio.gitlens`
- Markdown All in One: `yzhang.markdown-all-in-one`

Workspace settings should enable Python formatting through Ruff, type checking
through MyPy, test discovery through pytest and unittest-compatible tests, and
Rust support through Rust Analyzer.

## Validation Gate

Run this gate from the repository root:

```powershell
ruff check .
ruff format --check .
python -m unittest
python -m compileall .
```

If any command fails, stop, fix the failure within the Build Engineer boundary,
and rerun the full gate.

## Bootstrap Verification

Verified on 2026-07-10:

- Python: 3.14.0
- Repository virtual environment: `.venv` using Python 3.14.0
- uv: 0.11.26
- rustup: 1.29.0
- rustc: 1.97.0 stable
- cargo: 1.97.0
- rustfmt: 1.9.0 stable
- clippy: 0.1.97
- Git: 2.44.0.windows.1
- SQLite CLI: 3.53.3
- Python `sqlite3` module: 3.50.4
- Ruff: 0.15.20
- MyPy: 2.2.0
- Pytest: 9.1.1

The validation gate passed after this bootstrap.

## Prototype Infrastructure

The development environment includes a minimal CLI entry point:

```powershell
daale doctor
```

The command performs environment checks only. It does not run Prototype-001,
reasoning, planning, provider, scheduler, kernel, or execution logic.
