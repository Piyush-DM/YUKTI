"""Readiness check for the R-Fabric engine. Prints no secret values.

    python preflight.py

Exit code 0 means ready for a live run. Exit code 2 means the engine itself is
sound (dependencies, offline pipeline) but live inference is not configured yet,
which is the expected state before the API key is added. Exit code 1 means
something in the engine is broken.
"""

import importlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OK, WAIT, FAIL = "ok  ", "wait", "FAIL"


def line(status, text):
    print(f"[{status}] {text}")


def main():
    broken = False
    waiting = False

    line(OK if sys.version_info >= (3, 12) else FAIL, f"python {sys.version.split()[0]} (need 3.12+)")
    broken |= sys.version_info < (3, 12)

    for module in ("requests", "jsonschema", "dotenv"):
        try:
            importlib.import_module(module)
            line(OK, f"dependency: {module}")
        except ImportError:
            line(FAIL, f"dependency missing: {module} (pip install -r requirements.txt)")
            broken = True

    try:
        from dotenv import load_dotenv

        load_dotenv(ROOT / ".env")
    except ImportError:
        pass

    if not (ROOT / ".env").exists():
        line(WAIT, ".env not found (copy .env.example to .env)")
        waiting = True

    provider = os.getenv("DAALE_LIVE_PROVIDER", "openrouter").strip().lower()
    required_by_provider = {
        "openrouter": ["OPENROUTER_API_KEY"],
        "generic": ["LLM_BASE_URL", "LLM_API_KEY"],
        "nvidia": ["NVIDIA_API_KEY"],
        "aimlapi": ["AIMLAPI_API_KEY"],
    }
    if provider not in required_by_provider:
        line(FAIL, f"provider {provider!r} is not one of {sorted(required_by_provider)}")
        broken = True
    else:
        line(OK, f"provider: {provider}")
        for variable in required_by_provider[provider]:
            if os.getenv(variable, "").strip():
                line(OK, f"{variable} is set")
            else:
                line(WAIT, f"{variable} is empty (expected until it is added)")
                waiting = True

    model = os.getenv("DAALE_DEFAULT_MODEL")
    if model is None:
        line(WAIT, "DAALE_DEFAULT_MODEL unset: --live refuses to run; no model is assumed")
        waiting = True
    elif not model.strip():
        line(FAIL, "DAALE_DEFAULT_MODEL is set but empty: a live run would send an empty model ID")
        broken = True
    else:
        line(OK, f"default model: {model.strip()}")

    for path in ("run_daale.py", "daale/pipeline.py", "cases/vendor_alpha.json",
                 "policies/vendor_post_technical_dd_v0_1.json"):
        exists = (ROOT / path).exists()
        line(OK if exists else FAIL, f"file: {path}")
        broken |= not exists

    with tempfile.TemporaryDirectory() as runs_dir:
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        result = subprocess.run(
            [sys.executable, str(ROOT / "run_daale.py"), "--offline", "--runs-dir", runs_dir],
            capture_output=True, text=True, cwd=ROOT, env=env,
        )
        produced = any(Path(runs_dir).glob("*.json"))
    if result.returncode == 0 and produced:
        line(OK, "offline pipeline run produced a trace")
    else:
        line(FAIL, "offline pipeline run failed: " + (result.stderr.strip().splitlines() or ["no output"])[-1])
        broken = True

    print()
    if broken:
        print("NOT READY: fix the FAIL lines above.")
        return 1
    if waiting:
        print("ENGINE READY, LIVE INFERENCE NOT CONFIGURED (waiting on the WAIT lines).")
        return 2
    print("READY for a live run.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
