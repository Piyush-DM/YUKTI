# Prepare R-Fabric on Windows: venv, dependencies, empty .env, readiness check.
# Safe to re-run. Never overwrites an existing .env and never writes a key.
Set-Location $PSScriptRoot

if (-not (Test-Path .venv)) { py -3.12 -m venv .venv }
.\.venv\Scripts\python.exe -m pip install -q -r requirements.txt

if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "Created .env from .env.example (API key left empty)."
}

.\.venv\Scripts\python.exe preflight.py
