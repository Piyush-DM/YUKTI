#!/usr/bin/env python3
"""Start YUKTI.

    python yukti.py

That is the whole thing. No install, no configuration, no environment
variables, no arguments. It starts the investment committee workspace and opens
a browser at it.

Why this file exists at the repository root: the application was previously
reachable only as ``python -m applications.investment.workspace``, run from the
repository directory. That is a module path someone has to be told, from a
working directory someone has to be in — which is the difference between
handing over a running product and handing over a repository. This resolves
both from its own location, so it works from anywhere.

The workspace itself needs **no third-party packages**; it is standard library
only, as is the reasoning engine underneath it. A plain Python 3.12 or newer is
the entire requirement, and this file checks for it rather than failing on an
import three frames deep.

Arguments, if you need them, are passed straight through:

    python yukti.py --port 8771
    python yukti.py --no-browser
"""

from __future__ import annotations

import sys
from pathlib import Path

MINIMUM_PYTHON = (3, 12)

REPOSITORY_ROOT = Path(__file__).resolve().parent


def main(argv: list[str] | None = None) -> int:
    """Check the interpreter, put the repository on the path, and serve."""
    if sys.version_info < MINIMUM_PYTHON:
        running = ".".join(str(part) for part in sys.version_info[:3])
        wanted = ".".join(str(part) for part in MINIMUM_PYTHON)
        print(f"YUKTI needs Python {wanted} or newer. This is Python {running}.")
        print(f"Interpreter: {sys.executable}")
        return 1

    # Run from anywhere: the packages are found relative to this file, not to
    # whatever directory the shell happened to be in.
    root = str(REPOSITORY_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)

    # `.env` at the repository root, if one exists and python-dotenv is
    # installed. This is where the optional language model's key lives; the
    # file is gitignored and nothing here reads or logs its contents.
    try:
        from dotenv import load_dotenv

        load_dotenv(REPOSITORY_ROOT / ".env")
    except ImportError:
        pass

    try:
        from applications.investment.workspace.server import main as serve
    except ImportError as exc:
        print(f"YUKTI could not start: {exc}")
        print(f"Expected the application under: {REPOSITORY_ROOT}")
        print("This file must stay at the repository root to find it.")
        return 1

    return serve(sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    raise SystemExit(main())
