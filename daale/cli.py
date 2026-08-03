"""Command-line interface for DAALE infrastructure checks."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from daale.doctor import all_checks_passed, run_doctor
from daale.logging import initialize_logging


def main(argv: Sequence[str] | None = None) -> int:
    """Run the DAALE command-line interface."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "doctor":
        initialize_logging()
        results = run_doctor(Path.cwd())
        for result in results:
            status = "PASS" if result.passed else "FAIL"
            print(f"{status}: {result.name} - {result.detail}")
        return 0 if all_checks_passed(results) else 1

    parser.print_help()
    return 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="daale")
    subcommands = parser.add_subparsers(dest="command")
    subcommands.add_parser("doctor", help="Verify the local DAALE environment")
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
