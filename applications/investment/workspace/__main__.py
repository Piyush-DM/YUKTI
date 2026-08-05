"""Entry point: ``python -m applications.investment.workspace``.

Starts the workspace on http://127.0.0.1:8770/ and leaves it running.
"""

from __future__ import annotations

from applications.investment.workspace.server import main

if __name__ == "__main__":
    raise SystemExit(main())
