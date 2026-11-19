"""Command-line entry point for the DAALE v0.1 reference pipeline."""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from daale.budget import BudgetExhausted
from daale.client import DaaleModelError, FixtureClient
from daale.intake import IntakeError, build_case_from_file, describe, verify_provenance
from daale.pipeline import DaalePipeline
from daale.providers import build_live_client, fallback_by_kernel_from_env, model_by_kernel_from_env
from daale.trace import write_trace
from daale.validation import DaaleValidationError


ROOT = Path(__file__).resolve().parent

KERNELS = [
    "analyst",
    "contrarian",
    "first_principles",
    "expansionist",
    "outsider",
    "historian",
    "adversary",
]


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def env_bool(name, default=False):
    raw = os.getenv(name)
    if raw is None:
        return default
    normalized = raw.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} must be true or false, received: {raw}")


def build_parser():
    parser = argparse.ArgumentParser(
        description="Run the DAALE v0.1 deterministic adversarial pipeline with R-Fabric."
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--offline", action="store_true", help="Use local fixtures")
    mode.add_argument("--live", action="store_true", help="Call OpenRouter")

    parser.add_argument(
        "--case",
        default=str(ROOT / "cases" / "vendor_alpha.json"),
        help="Path to the case JSON file",
    )
    parser.add_argument(
        "--material",
        help="Path to a material manifest; the case is built from the user's "
        "documents (see daale/intake.py) instead of read from --case",
    )
    parser.add_argument(
        "--resume",
        help="Path to a trace from an incomplete run. Kernels that succeeded are reused as recorded; "
        "failed kernels and the adversary run again. Case and policy come from the trace.",
    )
    parser.add_argument(
        "--policy",
        default=str(ROOT / "policies" / "vendor_post_technical_dd_v0_1.json"),
        help="Path to the policy JSON file",
    )
    for kernel in KERNELS:
        parser.add_argument(
            f"--{kernel}-fixture",
            default=str(ROOT / "fixtures" / f"{kernel}_output.json"),
            help=f"Offline {kernel} fixture",
        )
    parser.add_argument(
        "--runs-dir",
        default=str(ROOT / "runs"),
        help="Directory for audit traces",
    )
    return parser


def main():
    load_dotenv(ROOT / ".env")
    # Progress goes to stderr so stdout stays the decision packet alone.
    logging.basicConfig(
        level=os.getenv("DAALE_LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )
    args = build_parser().parse_args()

    try:
        prior_trace = None
        if args.resume:
            prior_trace = load_json(args.resume)
            case = policy = None
        elif args.material:
            if args.offline:
                raise ValueError(
                    "--material needs --live: the offline fixtures only match the "
                    "bundled cases, not your documents."
                )
            case = build_case_from_file(args.material)
            problems = verify_provenance(case)
            if problems:
                raise ValueError("provenance check failed: " + "; ".join(problems))
            print(describe(case), file=sys.stderr)
        else:
            case = load_json(args.case)
        if prior_trace is None:
            policy = load_json(args.policy)

        model_by_kernel = model_by_kernel_from_env(os.environ, live=args.live)

        if args.offline:
            fixtures = {}
            for kernel in KERNELS:
                fixture_path = getattr(args, f"{kernel}_fixture")
                if Path(fixture_path).exists():
                    fixtures[kernel] = load_json(fixture_path)
            client = FixtureClient(fixtures)
            native_json_schema = False
        else:
            client, native_json_schema = build_live_client(os.environ)

        pipeline = DaalePipeline(
            client=client,
            model_by_kernel=model_by_kernel,
            native_json_schema=native_json_schema,
            fallback_by_kernel=fallback_by_kernel_from_env(os.environ) if args.live else None,
            isolate_evidence=env_bool("DAALE_EVIDENCE_SEPARATION"),
        )
        result = pipeline.resume(prior_trace) if prior_trace is not None else pipeline.run(case, policy)
        trace_path = write_trace(result.trace, args.runs_dir)

        print(json.dumps(result.decision_packet, indent=2, ensure_ascii=False))
        print(f"\nTrace saved to: {trace_path}")
        return 0
    except (
        BudgetExhausted,
        IntakeError,
        DaaleValidationError,
        DaaleModelError,
        FileNotFoundError,
        json.JSONDecodeError,
        ValueError,
    ) as error:
        print(f"DAALE run failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
