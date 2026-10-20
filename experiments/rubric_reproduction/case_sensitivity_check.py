"""Isolate whether a "Diverges" verdict is real disagreement or a casing artifact.

`compare.py`'s classifiers do raw ``gt == resp`` string equality (see
`_classify_scalar`, `_classify_band_map`, `_classify_str_map`) -- deliberately:
the frozen engine's vocabulary is a fixed, lowercase enum, and a response that
drifts from it is worth flagging. That is the right default for the real
experiment. It also means a model that reasons correctly but answers in the
wrong case scores identically to one that reasons wrongly, and the two need to
be told apart before either is reported as a finding.

This script does **not** change how the experiment scores responses --
`compare.py` is untouched, and every number that script produces stands. It
answers a narrower, diagnostic question against already-collected responses:
*if every string is case-folded first, does the divergence survive?*
A field that matches only after folding was a casing artifact. A field that
still diverges after folding is a real disagreement, independent of casing.

Usage:
    python -m experiments.rubric_reproduction.case_sensitivity_check
    python -m experiments.rubric_reproduction.case_sensitivity_check --packet orbital-series-b
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any

REPOSITORY_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from experiments.rubric_reproduction import compare  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
GROUND_TRUTH_DIR = HERE / "ground_truth"
RESPONSES_DIR = HERE / "responses"
RESULTS_DIR = HERE / "results"


def _casefold(value: Any) -> Any:
    """Recursively lowercase every string leaf. Structure and non-strings untouched."""
    if isinstance(value, str):
        return value.casefold()
    if isinstance(value, dict):
        return {key: _casefold(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_casefold(item) for item in value]
    return value


def check_one(ground_truth_path: pathlib.Path, response_path: pathlib.Path) -> dict:
    ground_truth = json.loads(ground_truth_path.read_text(encoding="utf-8"))
    response = json.loads(response_path.read_text(encoding="utf-8"))

    gt_record = ground_truth["record"]
    resp_record = response.get("record", response)

    gt_view = compare.build_comparison_view(gt_record)
    resp_view = compare.build_comparison_view(resp_record)

    allowed = set(ground_truth.get("ir_known_ids", []))
    violations = sorted(
        id_ for id_ in compare.cited_ids(resp_record) if id_ not in allowed
    )

    raw = compare.compare_views(gt_view, resp_view, violations)
    folded = compare.compare_views(_casefold(gt_view), _casefold(resp_view), violations)

    fields_only_wrong_by_case: list[str] = []
    fields_genuinely_diverging: list[str] = []
    for tier in ("tier1", "tier2", "tier3"):
        for field, raw_verdict in raw["per_field"][tier].items():
            folded_verdict = folded["per_field"][tier][field]
            if raw_verdict == "divergence" and folded_verdict != "divergence":
                fields_only_wrong_by_case.append(f"{tier}.{field}")
            elif raw_verdict == "divergence" and folded_verdict == "divergence":
                fields_genuinely_diverging.append(f"{tier}.{field}")

    return {
        "ground_truth": str(ground_truth_path),
        "response": str(response_path),
        "packet_id": ground_truth.get("packet_id"),
        "raw_verdict": raw["verdict"],
        "raw_tier2_match_rate": raw["tier2_match_rate"],
        "case_folded_verdict": folded["verdict"],
        "case_folded_tier2_match_rate": folded["tier2_match_rate"],
        "fields_only_wrong_by_case": fields_only_wrong_by_case,
        "fields_genuinely_diverging_after_casefold": fields_genuinely_diverging,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="case-sensitivity-check")
    parser.add_argument("--packet", help="restrict to one packet's responses")
    args = parser.parse_args(argv)

    if not RESPONSES_DIR.is_dir():
        print(f"No responses collected yet at {RESPONSES_DIR}")
        return 1

    pattern = f"{args.packet}__L-lo__run*.json" if args.packet else "*__L-lo__run*.json"
    response_paths = sorted(
        p for p in RESPONSES_DIR.glob(pattern) if not p.name.endswith(".raw.txt")
    )
    if not response_paths:
        print(f"No response files matching {pattern!r} in {RESPONSES_DIR}")
        return 1

    results = []
    for response_path in response_paths:
        packet = response_path.name.split("__L-lo__run")[0]
        ground_truth_path = GROUND_TRUTH_DIR / f"{packet}.json"
        if not ground_truth_path.is_file():
            print(f"skip {response_path.name}: no ground truth for {packet!r}")
            continue

        result = check_one(ground_truth_path, response_path)
        results.append(result)
        print(
            f"{response_path.name:<40} "
            f"raw={result['raw_verdict']:<22} "
            f"case-folded={result['case_folded_verdict']:<12} "
            f"(tier2 {result['raw_tier2_match_rate']:.3f} -> "
            f"{result['case_folded_tier2_match_rate']:.3f})"
        )
        if result["fields_only_wrong_by_case"]:
            print(f"    casing-only: {result['fields_only_wrong_by_case']}")
        if result["fields_genuinely_diverging_after_casefold"]:
            print(
                "    STILL DIVERGES after casefold: "
                f"{result['fields_genuinely_diverging_after_casefold']}"
            )

    RESULTS_DIR.mkdir(exist_ok=True)
    out_path = RESULTS_DIR / "case_sensitivity_check.json"
    out_path.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"\nwritten: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
