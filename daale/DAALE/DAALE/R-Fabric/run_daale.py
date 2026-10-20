"""Command-line entry point for the DAALE v0.1 reference pipeline."""

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from daale.client import DaaleModelError, FixtureClient, NvidiaClient, OpenRouterClient, AimlApiClient
from daale.pipeline import DaalePipeline
from daale.trace import write_trace
from daale.validation import DaaleValidationError


ROOT = Path(__file__).resolve().parent
DEFAULT_MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"

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
    args = build_parser().parse_args()

    try:
        case = load_json(args.case)
        policy = load_json(args.policy)

        model_by_kernel = {
            "default": os.getenv("DAALE_DEFAULT_MODEL", DEFAULT_MODEL),
        }
        for kernel in KERNELS:
            env_var = f"DAALE_{kernel.upper()}_MODEL"
            if os.getenv(env_var):
                model_by_kernel[kernel.upper()] = os.getenv(env_var)

        if args.offline:
            fixtures = {}
            for kernel in KERNELS:
                fixture_path = getattr(args, f"{kernel}_fixture")
                if Path(fixture_path).exists():
                    fixtures[kernel] = load_json(fixture_path)
            client = FixtureClient(fixtures)
            native_json_schema = False
        else:
            live_provider = os.getenv("DAALE_LIVE_PROVIDER", "openrouter").strip().lower()
            native_json_schema = False

            if live_provider == "nvidia":
                # Direct NVIDIA NIM endpoint (integrate.api.nvidia.com).
                # No OpenRouter routing concepts apply here: no provider
                # pinning, no native-json-schema response_format mode.
                client = NvidiaClient(
                    api_key=os.getenv("NVIDIA_API_KEY"),
                    timeout_seconds=int(os.getenv("NVIDIA_TIMEOUT_SECONDS", "180")),
                    # Measured directly against this endpoint: ~40% of
                    # identical requests return a bare 500 regardless of
                    # payload (see the diagnostic session that added this
                    # client). 3 attempts alone leaves each of the 7 kernel
                    # calls a non-trivial chance of exhausting its retries;
                    # 6 pushes that down to roughly 1 in 10,000 per call.
                    max_attempts=int(os.getenv("NVIDIA_MAX_ATTEMPTS", "6")),
                )
            elif live_provider == "openrouter":
                native_json_schema = env_bool(
                    "OPENROUTER_NATIVE_JSON_SCHEMA",
                    default=False,
                )
                provider_by_purpose = {}
                for kernel in KERNELS:
                    env_var = f"DAALE_{kernel.upper()}_PROVIDER"
                    if os.getenv(env_var):
                        provider_by_purpose[kernel] = os.getenv(env_var)
                client = OpenRouterClient(
                    api_key=os.getenv("OPENROUTER_API_KEY"),
                    provider_by_purpose=provider_by_purpose or None,
                    native_json_schema=native_json_schema,
                    timeout_seconds=int(os.getenv("OPENROUTER_TIMEOUT_SECONDS", "180")),
                )
            elif live_provider == "aimlapi":
                native_json_schema = env_bool(
                    "AIMLAPI_NATIVE_JSON_SCHEMA",
                    default=False,
                )
                client = AimlApiClient(
                    api_key=os.getenv("AIMLAPI_API_KEY"),
                    native_json_schema=native_json_schema,
                    timeout_seconds=int(os.getenv("AIMLAPI_TIMEOUT_SECONDS", "180")),
                    max_attempts=int(os.getenv("AIMLAPI_MAX_ATTEMPTS", "6")),
                )
            else:
                raise ValueError(
                    "DAALE_LIVE_PROVIDER must be 'openrouter', 'nvidia', or 'aimlapi', "
                    f"received: {live_provider!r}"
                )

        pipeline = DaalePipeline(
            client=client,
            model_by_kernel=model_by_kernel,
            native_json_schema=native_json_schema,
        )
        result = pipeline.run(case, policy)
        trace_path = write_trace(result.trace, args.runs_dir)

        print(json.dumps(result.decision_packet, indent=2, ensure_ascii=False))
        print(f"\nTrace saved to: {trace_path}")
        return 0
    except (
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