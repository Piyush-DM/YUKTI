"""Collect L-lo control responses from a configured model, then compare them.

This is the "after approval to call a model" step the README describes and
`run.py` deliberately stops short of. It is a separate file for exactly that
reason: `run.py` and everything it calls make no model call and must stay that
way; this one exists only to make one.

The prompt file is the entire message. No system prompt is added beyond a
one-line role framing -- the prompt itself already carries every rule,
including the output contract -- because adding workspace-style scaffolding
here would be assisting the model at the one task this experiment exists to
test unassisted. This is deliberately NOT `assistant.py`: that module is wired
for the workspace's own proposal/phrase contracts (JSON-schema-constrained
output, workspace system prompts) and reusing it would contaminate the control.

Two providers are wired, dispatched by `--provider` (default: inferred from
the model name):

- **anthropic-gateway** -- the Experiential Labs gateway already used by
  `assistant.py`, speaking the Anthropic Messages API. Needs `ANTHROPIC_API_KEY`
  (+ `YUKTI_ASSIST_BASE_URL`) in `.env`.
- **gemini** -- Google's `generateContent` REST endpoint, called directly with
  no SDK dependency. Needs `GEMINI_API_KEY` in `.env`.

Both paths make one bare call per sample: the prompt file is the entire
message, no system prompt beyond what the prompt itself already specifies.

Usage:
    python -m experiments.rubric_reproduction.collect_responses --model gpt-5.6-luna
    python -m experiments.rubric_reproduction.collect_responses --model gemini-2.5-pro
    python -m experiments.rubric_reproduction.collect_responses --model gemini-2.5-pro --samples 5
    python -m experiments.rubric_reproduction.collect_responses --model gemini-2.5-pro --packet orbital-series-b
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

REPOSITORY_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

try:
    from dotenv import load_dotenv

    load_dotenv(REPOSITORY_ROOT / ".env")
except ImportError:
    pass

import os  # noqa: E402

from experiments.rubric_reproduction import compare  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
PROMPTS_DIR = HERE / "prompts"
GROUND_TRUTH_DIR = HERE / "ground_truth"
RESPONSES_DIR = HERE / "responses"
RESULTS_DIR = HERE / "results"

PACKETS = ("orbital-series-b", "northwind-seed")

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

Caller = Callable[[str, str], tuple[str, float]]

_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


@dataclass(frozen=True)
class Sample:
    packet: str
    index: int
    model: str
    raw_text: str
    parsed: dict | None
    parse_error: str
    latency_s: float


def _base_url() -> str:
    return (
        os.environ.get("YUKTI_ASSIST_BASE_URL", "")
        or os.environ.get("ANTHROPIC_BASE_URL", "")
    ).strip()


def _infer_provider(model: str) -> str:
    return "gemini" if model.startswith("gemini") else "anthropic-gateway"


def make_caller(provider: str) -> Caller:
    """Build the one-call-per-sample function for the chosen provider.

    Kept as a single closure returned up front, rather than re-branching per
    call, so `collect()` never needs to know which provider it is talking to.
    """
    if provider == "gemini":
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise SystemExit("No GEMINI_API_KEY in .env.")

        def call_gemini(model: str, prompt_text: str) -> tuple[str, float]:
            url = GEMINI_ENDPOINT.format(model=model)
            body = json.dumps(
                {
                    "contents": [{"parts": [{"text": prompt_text}]}],
                    # The rubric prompt is ~900 lines and this model reports a
                    # "thoughtSignature" (internal reasoning), which spends
                    # output-token budget before the final JSON -- 8000 was
                    # observed truncating silently. 32000 gives the reasoning
                    # room without touching the prompt or the output contract.
                    "generationConfig": {
                        "maxOutputTokens": 32000,
                        "responseMimeType": "application/json",
                    },
                }
            ).encode("utf-8")
            request = urllib.request.Request(
                url,
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": api_key,
                },
                method="POST",
            )

            # UNAVAILABLE (503, "high demand") observed on this prompt's length
            # even though a one-line prompt succeeded immediately -- transient
            # capacity, not an auth or request problem. Retried with backoff;
            # anything else surfaces on the first try.
            attempts = 3
            last_error: Exception | None = None
            start = time.monotonic()
            for attempt in range(1, attempts + 1):
                try:
                    with urllib.request.urlopen(request, timeout=180) as resp:
                        payload = json.loads(resp.read())
                    break
                except urllib.error.HTTPError as exc:
                    detail = exc.read().decode("utf-8", errors="replace")
                    last_error = RuntimeError(f"Gemini HTTP {exc.code}: {detail}")
                    if exc.code == 503 and attempt < attempts:
                        time.sleep(10 * attempt)
                        continue
                    raise last_error from exc
            else:  # pragma: no cover - loop exits via break or raise above
                raise last_error  # type: ignore[misc]
            latency = time.monotonic() - start

            candidates = payload.get("candidates") or []
            if not candidates:
                feedback = payload.get("promptFeedback", {})
                raise RuntimeError(f"Gemini returned no candidates: {feedback}")
            finish_reason = candidates[0].get("finishReason", "")
            if finish_reason not in ("STOP", ""):
                raise RuntimeError(
                    f"Gemini finishReason={finish_reason!r} (likely truncated); "
                    "raise maxOutputTokens or inspect the partial response"
                )
            parts = candidates[0].get("content", {}).get("parts", [])
            text = "".join(part.get("text", "") for part in parts).strip()
            return text, latency

        return call_gemini

    # anthropic-gateway
    import anthropic

    base_url = _base_url()
    client = anthropic.Anthropic(base_url=base_url) if base_url else anthropic.Anthropic()

    def call_anthropic(model: str, prompt_text: str) -> tuple[str, float]:
        start = time.monotonic()
        response = client.messages.create(
            model=model,
            max_tokens=8000,
            messages=[{"role": "user", "content": prompt_text}],
        )
        latency = time.monotonic() - start
        parts = [block.text for block in response.content if block.type == "text"]
        return "".join(parts).strip(), latency

    return call_anthropic


def _strip_fences(text: str) -> str:
    return _FENCE.sub("", text.strip()).strip()


def collect(model: str, packet: str, index: int, caller: Caller) -> Sample:
    prompt_path = PROMPTS_DIR / f"{packet}__L-lo.txt"
    prompt_text = prompt_path.read_text(encoding="utf-8")

    raw_text, latency = caller(model, prompt_text)

    parsed: dict | None = None
    parse_error = ""
    candidate = _strip_fences(raw_text)
    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError as exc:
        parse_error = str(exc)

    return Sample(
        packet=packet,
        index=index,
        model=model,
        raw_text=raw_text,
        parsed=parsed,
        parse_error=parse_error,
        latency_s=round(latency, 2),
    )


def _write_sample(sample: Sample) -> tuple[pathlib.Path, pathlib.Path | None]:
    RESPONSES_DIR.mkdir(exist_ok=True)
    stem = f"{sample.packet}__L-lo__run{sample.index}"
    raw_path = RESPONSES_DIR / f"{stem}.raw.txt"
    raw_path.write_text(sample.raw_text, encoding="utf-8")

    json_path = None
    if sample.parsed is not None:
        json_path = RESPONSES_DIR / f"{stem}.json"
        json_path.write_text(
            json.dumps(sample.parsed, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return raw_path, json_path


def run(model: str, packets: tuple[str, ...], samples: int, provider: str) -> int:
    caller = make_caller(provider)
    recorded_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    print(f"provider:   {provider}")
    print(f"model:      {model}")
    if provider == "anthropic-gateway":
        print(f"base_url:   {_base_url() or '(Anthropic default)'}")
    print(f"samples:    {samples} per packet")
    print(
        "temperature: not set (this provider's sampling controls are "
        "unverified; recorded as default -- see the summary file)"
    )
    print()

    RESULTS_DIR.mkdir(exist_ok=True)
    overall_summary: dict[str, object] = {
        "model": model,
        "recorded_at": recorded_at,
        "samples_per_packet": samples,
        "packets": {},
    }

    for packet in packets:
        ground_truth_path = GROUND_TRUTH_DIR / f"{packet}.json"
        if not ground_truth_path.is_file():
            print(f"{packet}: no ground truth at {ground_truth_path}; skipping")
            continue

        print(f"=== {packet} ===")
        verdicts: list[str] = []
        tier2_rates: list[float] = []
        x4_violation_total = 0
        parse_failures = 0

        for i in range(1, samples + 1):
            try:
                sample = collect(model, packet, i, caller)
            except (RuntimeError, urllib.error.URLError) as exc:
                print(f"  run {i}: CALL_FAILED ({exc})")
                verdicts.append("CALL_FAILED")
                continue
            raw_path, json_path = _write_sample(sample)

            if json_path is None:
                parse_failures += 1
                print(
                    f"  run {i}: PARSE_FAILURE ({sample.parse_error[:80]}) "
                    f"-> {raw_path.name}"
                )
                verdicts.append("PARSE_FAILURE")
                continue

            result = compare.compare_files(ground_truth_path, json_path)
            verdicts.append(result["verdict"])
            tier2_rates.append(result["tier2_match_rate"])
            x4_violation_total += len(result["x4_violations"])
            print(
                f"  run {i}: {result['verdict']:<10} "
                f"tier2={result['tier2_match_rate']:.3f} "
                f"x4_violations={len(result['x4_violations'])} "
                f"({sample.latency_s}s) -> {json_path.name}"
            )

        overall_summary["packets"][packet] = {
            "verdicts": verdicts,
            "reproduces_all": bool(verdicts)
            and all(v == "MATCH" for v in verdicts),
            "tier2_match_rate_range": (
                [min(tier2_rates), max(tier2_rates)] if tier2_rates else None
            ),
            "x4_violations_total": x4_violation_total,
            "parse_failures": parse_failures,
        }
        print()

    summary_path = RESULTS_DIR / f"{model}__summary.json"
    summary_path.write_text(
        json.dumps(overall_summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"summary written to {summary_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="collect-responses")
    parser.add_argument("--model", required=True, help="model id, e.g. gemini-2.5-pro")
    parser.add_argument(
        "--provider",
        choices=["auto", "anthropic-gateway", "gemini"],
        default="auto",
        help="which API to call (default: inferred from --model)",
    )
    parser.add_argument(
        "--samples", type=int, default=5, help="samples per packet (default 5)"
    )
    parser.add_argument(
        "--packet",
        choices=PACKETS,
        help="restrict to one packet (default: both)",
    )
    args = parser.parse_args(argv)

    provider = (
        _infer_provider(args.model) if args.provider == "auto" else args.provider
    )
    packets = (args.packet,) if args.packet else PACKETS
    return run(args.model, packets, args.samples, provider)


if __name__ == "__main__":
    raise SystemExit(main())
