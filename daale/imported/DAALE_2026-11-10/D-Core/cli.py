"""Command-line interface for DAALE infrastructure checks.

``doctor`` verifies the local environment. ``conformance`` runs the Phase 0
conformance lock: it resolves every piece of evidence the frozen CHOIR v0.1
commitments rely on and fails if any of it has gone missing.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from daale import rfabric
from daale.conformance import COMMITMENTS, ConformanceReport, as_json, lock, render
from daale.doctor import all_checks_passed, run_doctor
from daale.execution import ContractRejected
from daale.logging_config import initialize_logging

# Artifacts land beside the other generated output, namespaced by producer.
# No date in the path: a clock would break the determinism the lock checks for.
CONFORMANCE_ARTIFACT_DIRECTORY = Path("reports") / "daale" / "conformance"
RFABRIC_ARTIFACT_DIRECTORY = Path("reports") / "daale" / "rfabric_admission"


def write_conformance_artifacts(
    root: Path, report: ConformanceReport
) -> tuple[Path, ...]:
    """Persist the lock as inspectable evidence, and return what was written."""
    directory = root / CONFORMANCE_ARTIFACT_DIRECTORY
    directory.mkdir(parents=True, exist_ok=True)

    rendered = directory / "conformance.txt"
    machine = directory / "conformance.json"
    rendered.write_text(render(report), encoding="utf-8")
    machine.write_text(as_json(report), encoding="utf-8")

    return (rendered, machine)


def write_rfabric_artifacts(
    root: Path, admission: rfabric.Admission
) -> tuple[Path, ...]:
    """Persist one R-Fabric admission as inspectable evidence.

    Namespaced by execution id rather than overwritten in place, for the same
    reason R-Fabric's own ``runs/`` directory never overwrites: two admissions
    are two audit records, not one record with the earlier draft discarded.
    """
    directory = root / RFABRIC_ARTIFACT_DIRECTORY
    directory.mkdir(parents=True, exist_ok=True)

    execution_id = admission.summary.identity.execution_id
    rendered = directory / f"{execution_id}.txt"
    machine = directory / f"{execution_id}.json"
    rendered.write_text(rfabric.render(admission), encoding="utf-8")
    machine.write_text(
        json.dumps(rfabric.as_json(admission), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return (rendered, machine)


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

    if args.command == "conformance":
        root = Path.cwd()
        report = lock(root, COMMITMENTS)
        print(render(report))
        for path in write_conformance_artifacts(root, report):
            print(f"Written: {path.relative_to(root)}")
        return 0 if report.holds else 1

    if args.command == "admit-rfabric":
        root = Path.cwd()
        trace = json.loads(Path(args.trace).read_text(encoding="utf-8"))
        try:
            admission = rfabric.admit(trace)
        except ContractRejected as rejected:
            print(f"package rejected: execution {rejected.identity.execution_id}")
            for violation in rejected.result.violations:
                print(f"  {violation.code}: {violation.subject} -- {violation.detail}")
            return 1

        print(rfabric.render(admission))
        for path in write_rfabric_artifacts(root, admission):
            print(f"Written: {path.relative_to(root)}")
        return 0 if admission.outcome.state.value == "committed" else 1

    parser.print_help()
    return 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="daale")
    subcommands = parser.add_subparsers(dest="command")
    subcommands.add_parser("doctor", help="Verify the local DAALE environment")
    subcommands.add_parser(
        "conformance",
        help="Lock the frozen CHOIR v0.1 commitments against their evidence",
    )
    admit_rfabric = subcommands.add_parser(
        "admit-rfabric",
        help="Offer one finished R-Fabric trace to the D-Core commit gate",
    )
    admit_rfabric.add_argument(
        "trace", help="Path to an R-Fabric trace JSON file (written under runs/)"
    )
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
