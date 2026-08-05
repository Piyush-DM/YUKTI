"""Entry point: ``python -m applications.investment.vertical_slice``.

Runs the fixed sample document through the whole pipeline, writes every stage
artifact, and prints where each one landed. The final report is printed too,
because a slice whose result you have to go and find has not demonstrated much.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from applications.investment.vertical_slice.parse import SAMPLE_DOCUMENT
from applications.investment.vertical_slice.run import (
    DEFAULT_OUTPUT_ROOT,
    REPORT_FILE,
    execute_slice,
)

EPILOG = """\
inspect the stages in pipeline order:

  01-document.json   the document, as supplied
  02-packet.json     what parsing produced
  03-ir.json         the CHOIR intermediate representation
  04-artifacts.json  what each kernel concluded, independently
  05-record.json     the canonical record: ir, artifacts, synthesis, trace
  06-report.txt      the rendered report, projected from that record
  metadata.json      digests for the record, the report and every file above
"""


def main(argv: Sequence[str] | None = None) -> int:
    """Run the vertical slice."""
    parser = argparse.ArgumentParser(
        prog="python -m applications.investment.vertical_slice",
        description=(
            "Carry one document through the full CHOIR pipeline and persist "
            "every stage."
        ),
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--document",
        type=Path,
        default=SAMPLE_DOCUMENT,
        help=f"Document to run (default: {SAMPLE_DOCUMENT.name})",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Directory to write stage artifacts into.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Write the artifacts and print the paths, but not the report.",
    )
    args = parser.parse_args(argv)

    try:
        run = execute_slice(args.document, args.output_root)
    except (OSError, ValueError) as exc:
        print(f"Vertical slice failed: {exc}")
        return 1

    if not args.quiet:
        print((run.output_directory / REPORT_FILE).read_text(encoding="utf-8"))

    print(f"packet          : {run.packet_id}")
    print(f"artifacts       : {run.output_directory}")
    for path in run.artifact_paths:
        print(f"                  {path.name}")
    print(f"record digest   : {run.record_digest}")
    print(f"report digest   : {run.report_digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
