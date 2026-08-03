"""Entry point: ``python -m choir_prototype``.

Runs the whole pipeline over a sample packet and prints the execution report.
The ``--inspect`` views open up each stage for someone reading the system for
the first time; ``--replay`` verifies that the run is reproducible; ``--audit``
measures the domain-independence claim.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from choir_prototype.audit import render_audit
from choir_prototype.core.inspection import (
    inspect_all,
    inspect_artifacts,
    inspect_ir,
    inspect_synthesis,
    inspect_trace,
)
from choir_prototype.core.pipeline import execute
from choir_prototype.core.replay import render_replay, verify
from choir_prototype.core.report import render
from choir_prototype.domains import REGISTRY, find_packet
from choir_prototype.freeze import VERSION, render_freeze, verify_freeze

DEFAULT_PACKET = "orbital-series-b"

EPILOG = """\
examples:
  python -m choir_prototype                        the execution report
  python -m choir_prototype --list                 every packet in every domain
  python -m choir_prototype --packet routine-referral
  python -m choir_prototype --inspect synthesis    how the decision was computed
  python -m choir_prototype --replay               verify reproducibility
  python -m choir_prototype --audit                measure domain independence
  python -m choir_prototype --frozen               verify the V0.1 freeze

reading order for a newcomer:
  1. --inspect ir          see the intermediate representation
  2. --inspect artifacts   see four kernels reason over it independently
  3. --inspect synthesis   see the recommendation computed, rule by rule
  4. --inspect trace       see the whole thing as a sequence of steps
  5. --audit               see the same core serve four unrelated domains
"""


def main(argv: Sequence[str] | None = None) -> int:
    """Run the prototype."""
    parser = argparse.ArgumentParser(
        prog="python -m choir_prototype",
        description=(
            f"CHOIR Prototype V{VERSION} (FROZEN) -- deterministic "
            "institutional reasoning."
        ),
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--packet",
        default=DEFAULT_PACKET,
        help=f"Which sample packet to run (default: {DEFAULT_PACKET})",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List every packet in every registered domain and exit.",
    )
    parser.add_argument(
        "--inspect",
        choices=("ir", "artifacts", "synthesis", "trace", "all"),
        help="Open up one stage of the pipeline instead of printing the report.",
    )
    parser.add_argument(
        "--replay",
        nargs="?",
        const=3,
        type=int,
        metavar="RUNS",
        help="Verify the run is reproducible (default: 3 runs).",
    )
    parser.add_argument(
        "--audit",
        action="store_true",
        help="Run the domain-independence audit and exit.",
    )
    parser.add_argument(
        "--frozen",
        action="store_true",
        help="Verify the V0.1 architecture freeze and exit.",
    )
    args = parser.parse_args(argv)

    if args.frozen:
        print(render_freeze())
        return 0 if verify_freeze().intact else 1

    if args.audit:
        print(render_audit())
        return 0

    if args.list:
        for name, domain in REGISTRY.items():
            print(f"{name}  --  {domain.description}")
            for packet_id, packet in domain.packets.items():
                title = getattr(packet, "title", packet_id)
                print(f"    {packet_id:<28} {title}")
        return 0

    located = find_packet(args.packet)
    if located is None:
        print(f"Unknown packet '{args.packet}'. Run --list to see what is available.")
        return 2
    domain, packet = located

    if args.replay is not None:
        report = verify(packet, domain, runs=max(2, args.replay))
        print(render_replay(report))
        return 0 if report.passed else 1

    result, synthesis = execute(packet, domain)

    if args.inspect == "ir":
        print(inspect_ir(result.ir))
    elif args.inspect == "artifacts":
        print(inspect_artifacts(result))
    elif args.inspect == "synthesis":
        print(inspect_synthesis(synthesis))
    elif args.inspect == "trace":
        print(inspect_trace(result))
    elif args.inspect == "all":
        print(inspect_all(result, synthesis))
    else:
        print(render(result, synthesis))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
