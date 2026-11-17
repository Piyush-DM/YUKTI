"""Run one case through R-Fabric, then offer the result to the D-Core.

This is the two-process shape the integration actually has, made runnable in
one command. R-Fabric and D-Core are not merged into one Python package --
each still defines its own top-level ``daale`` package (R-Fabric's own, and
D-Core's reached here through the ``daale`` junction beside this file), and
that collision is exactly why this script runs them as two subprocesses
instead of importing both into one interpreter. It also matches the actual
authority boundary: R-Fabric evaluates and writes its own audit trace under
``R-Fabric/runs/`` regardless of what happens next; D-Core decides admissibility
afterward, as a separate step, from that trace alone.

See ``docs/architecture/DECISION-005_RULING_rfabric_evaluates.md`` for what
this integration is ruling on and why, and ``D-Core/rfabric.py`` for the
translation this script's second step relies on.

Usage
-----

    python run_pipeline.py --offline
    python run_pipeline.py --live

Any extra arguments are forwarded to R-Fabric's own ``run_daale.py`` unchanged
(``--case``, ``--policy``, and so on) -- this script does not duplicate that
argument surface.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
R_FABRIC = ROOT / "R-Fabric"
R_FABRIC_PYTHON = R_FABRIC / ".venv" / "Scripts" / "python.exe"


def run_rfabric(argv: list[str]) -> Path:
    """Run R-Fabric's pipeline and return the trace file it wrote.

    Runs are told apart by the newest file in ``R-Fabric/runs/`` after the
    subprocess exits, rather than by parsing stdout, because the trace path
    R-Fabric prints and the trace path it writes are the same fact recorded
    twice -- reading the directory is reading the fact itself.
    """
    runs_directory = R_FABRIC / "runs"
    before = set(runs_directory.glob("*.json")) if runs_directory.exists() else set()

    python = R_FABRIC_PYTHON if R_FABRIC_PYTHON.exists() else sys.executable
    result = subprocess.run(
        [str(python), "run_daale.py", *argv], cwd=R_FABRIC, check=False
    )
    if result.returncode != 0:
        raise SystemExit(f"R-Fabric run failed with exit code {result.returncode}")

    after = set(runs_directory.glob("*.json"))
    written = after - before
    if len(written) != 1:
        raise SystemExit(
            f"expected exactly one new trace file in {runs_directory}, "
            f"found {len(written)}: {sorted(p.name for p in written)}"
        )
    return written.pop()


def run_dcore(trace_path: Path) -> int:
    """Offer the trace to the D-Core commit gate, from the repository directory.

    Run with this script's own directory as ``cwd`` so the ``daale`` junction
    beside it resolves to D-Core, matching how D-Core's README already
    documents running ``python -m daale`` "from the repository directory."
    """
    result = subprocess.run(
        [sys.executable, "-m", "daale", "admit-rfabric", str(trace_path)],
        cwd=ROOT,
        check=False,
    )
    return result.returncode


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in ("--offline", "--live"):
        print("usage: run_pipeline.py --offline|--live [R-Fabric args...]", file=sys.stderr)
        return 2

    trace_path = run_rfabric(argv)
    print(f"\nR-Fabric trace: {trace_path.relative_to(ROOT)}\n", flush=True)
    print("Offering the run's decision packet to the D-Core:\n", flush=True)
    return run_dcore(trace_path)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
