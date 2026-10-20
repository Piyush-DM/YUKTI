"""Entry point: ``python -m applications.investment.workspace``.

Starts the workspace on http://127.0.0.1:8770/, opens a browser, and leaves it
running. ``yukti.py`` at the repository root is the same thing without needing
to know the module path.
"""

from __future__ import annotations

import sys

from applications.investment.workspace.server import main

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
