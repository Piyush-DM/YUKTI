"""Deterministic, network-free comparison of a control response against ground truth.

Given:

* a ground-truth file written by ``ground_truth.py`` (the frozen pipeline's record
  plus a ``comparison_view`` and the IR's addressable ids), and
* a response file (same record shape, as produced by the frozen pipeline or by an
  external model),

this module builds a ``comparison_view`` for the response and diffs it field by
field against ground truth, using the tiered match / partial / divergence rules
from the experiment design. It performs no I/O beyond reading the two input files
and writing one JSON report, does no network access, and imports nothing from
``choir_prototype`` -- the record shape is all it needs.

``build_comparison_view`` is imported by ``ground_truth.py`` so that both sides of
the comparison are extracted by exactly the same code.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
RESULTS_DIR = HERE / "results"

# Confidence bands, strongest to weakest, in their canonical lowercase form.
BAND_ORDER = ["high", "moderate", "low", "insufficient"]

MATCH = "match"
PARTIAL = "partial"
DIVERGENCE = "divergence"

TIER1_FIELDS = ["recommendation", "confidence", "fired_rule"]
TIER2_FIELDS = [
    "kernel_bands",
    "kernel_limiting_factors",
    "kernel_coverage",
    "kernel_contradictions",
    "kernel_derivation_outcome",
    "kernel_derivation_steps",
    "findings",
    "finding_citations",
    "tally",
    "usable_kernels",
]
TIER3_FIELDS = [
    "agreements",
    "disagreements",
    "remaining_uncertainty",
    "kernel_unresolved",
    "confidence_limiting_factor",
]

# Fields whose divergence forces the whole-case verdict to "Diverges" (they would
# have changed the fired rule or the recommendation had the tally propagated).
HARD_TIER2_FIELDS = {"fired_rule", "findings", "tally", "kernel_bands"}

# Advisory fields: recorded and diffed, but a mismatch never counts as a
# divergence -- only match or partial. The derivation strings are a projection of
# band + inputs, not an independent verdict.
ADVISORY_FIELDS = {"kernel_derivation_steps"}


# --------------------------------------------------------------------------
# comparison-view extraction
# --------------------------------------------------------------------------


def _norm(text: str) -> str:
    """Strip a leading ``[kernel]`` attribution prefix and collapse whitespace."""
    without_prefix = re.sub(r"^\s*\[[^\]]+\]\s*", "", text)
    return re.sub(r"\s+", " ", without_prefix).strip()


def _derivation_outcome(derivation: list[str]) -> str | None:
    """The band a confidence derivation terminates on, or ``INSUFFICIENT``.

    ``None`` when no derivation was supplied.
    """
    if not derivation:
        return None
    for line in derivation:
        if "INSUFFICIENT (stop)" in line:
            return "insufficient"
    for line in reversed(derivation):
        stripped = line.strip()
        if stripped.startswith("result:"):
            after = stripped[len("result:") :].strip()
            return after.split(" (")[0].strip().lower()
    return None


def _derivation_steps(derivation: list[str]) -> list[str]:
    """The set of ``rule N`` tokens present in a derivation, sorted."""
    steps = set()
    for line in derivation or ():
        match = re.match(r"\s*(rule \d+)", line)
        if match:
            steps.add(match.group(1))
    return sorted(steps)


def build_comparison_view(record: dict[str, Any]) -> dict[str, Any]:
    """Extract the scored fields from a pipeline-shaped record.

    ``record`` must carry ``artifacts`` (a list of kernel artifacts) and
    ``synthesis`` (the institutional result), in the shape
    ``choir_prototype.core.replay._canonical`` produces. Missing optional keys are
    tolerated so an external response that omits, say, ``tally_detail`` still
    compares on the fields it does supply.
    """
    artifacts = record.get("artifacts", []) or []
    synthesis = record.get("synthesis", {}) or {}

    kernel_bands: dict[str, Any] = {}
    kernel_limiting: dict[str, Any] = {}
    kernel_coverage: dict[str, Any] = {}
    kernel_contradictions: dict[str, Any] = {}
    kernel_deriv_outcome: dict[str, Any] = {}
    kernel_deriv_steps: dict[str, Any] = {}
    kernel_unresolved: dict[str, Any] = {}
    findings: list[list[str]] = []
    finding_citations: dict[str, dict[str, list[str]]] = {}

    for artifact in artifacts:
        name = artifact.get("kernel_name", "?")
        confidence = artifact.get("confidence", {}) or {}
        derivation = confidence.get("derivation", []) or []
        kernel_bands[name] = confidence.get("band")
        kernel_limiting[name] = confidence.get("limiting_factor")
        kernel_coverage[name] = confidence.get("coverage")
        kernel_contradictions[name] = confidence.get("contradictions")
        kernel_deriv_outcome[name] = _derivation_outcome(derivation)
        kernel_deriv_steps[name] = _derivation_steps(derivation)
        kernel_unresolved[name] = sorted(
            {_norm(q) for q in artifact.get("unresolved_questions", []) or []}
        )
        for finding in artifact.get("findings", []) or []:
            key = f"{name}:{finding.get('id')}"
            findings.append(
                [name, finding.get("id"), finding.get("topic"), finding.get("stance")]
            )
            finding_citations[key] = {
                "claim_ids": sorted(set(finding.get("claim_ids", []) or [])),
                "evidence_ids": sorted(set(finding.get("evidence_ids", []) or [])),
            }

    fired_rule = None
    for rule in synthesis.get("rules_evaluated", []) or []:
        if rule.get("fired"):
            fired_rule = rule.get("name")
            break

    remaining = sorted(
        {_norm(item) for item in synthesis.get("remaining_uncertainty", []) or []}
    )

    return {
        "recommendation": synthesis.get("recommendation"),
        "confidence": synthesis.get("confidence"),
        "fired_rule": fired_rule,
        "confidence_limiting_factor": synthesis.get("confidence_limiting_factor"),
        "kernel_bands": kernel_bands,
        "kernel_limiting_factors": kernel_limiting,
        "kernel_coverage": kernel_coverage,
        "kernel_contradictions": kernel_contradictions,
        "kernel_derivation_outcome": kernel_deriv_outcome,
        "kernel_derivation_steps": kernel_deriv_steps,
        "kernel_unresolved": kernel_unresolved,
        "findings": sorted(findings, key=lambda row: (row[0] or "", row[1] or "")),
        "finding_citations": finding_citations,
        "tally": {
            "support": synthesis.get("support_weight"),
            "oppose": synthesis.get("oppose_weight"),
            "conditional": synthesis.get("conditional_count"),
        },
        "usable_kernels": sorted(set(synthesis.get("usable_kernels", []) or [])),
        "agreements": sorted(
            {view.get("topic") for view in synthesis.get("agreements", []) or []}
        ),
        "disagreements": sorted(
            {view.get("topic") for view in synthesis.get("disagreements", []) or []}
        ),
        "remaining_uncertainty": remaining,
    }


def cited_ids(record: dict[str, Any]) -> list[str]:
    """Every id a record's findings and evidence references cite, sorted."""
    ids: set[str] = set()
    for artifact in record.get("artifacts", []) or []:
        ids.update(artifact.get("evidence_references", []) or [])
        for finding in artifact.get("findings", []) or []:
            ids.update(finding.get("claim_ids", []) or [])
            ids.update(finding.get("evidence_ids", []) or [])
    return sorted(ids)


# --------------------------------------------------------------------------
# per-field classification
# --------------------------------------------------------------------------


def _classify_scalar(field: str, gt: Any, resp: Any) -> str:
    if gt == resp:
        return MATCH
    if field == "confidence" and gt in BAND_ORDER and resp in BAND_ORDER:
        if abs(BAND_ORDER.index(gt) - BAND_ORDER.index(resp)) == 1:
            return PARTIAL
    return DIVERGENCE


def _classify_band_map(gt: dict[str, Any], resp: dict[str, Any]) -> str:
    worst = MATCH
    for name in sorted(set(gt) | set(resp)):
        a, b = gt.get(name), resp.get(name)
        if a == b:
            continue
        if (
            a in BAND_ORDER
            and b in BAND_ORDER
            and (abs(BAND_ORDER.index(a) - BAND_ORDER.index(b)) == 1)
        ):
            worst = PARTIAL if worst == MATCH else worst
        else:
            return DIVERGENCE
    return worst


def _classify_str_map(gt: dict[str, Any], resp: dict[str, Any]) -> str:
    return MATCH if gt == resp else DIVERGENCE


def _classify_int_map(gt: dict[str, Any], resp: dict[str, Any]) -> str:
    worst = MATCH
    for name in sorted(set(gt) | set(resp)):
        a, b = gt.get(name), resp.get(name)
        if a == b:
            continue
        if isinstance(a, int) and isinstance(b, int) and abs(a - b) == 1:
            worst = PARTIAL if worst == MATCH else worst
        else:
            return DIVERGENCE
    return worst


def _classify_set(gt: list[Any], resp: list[Any], advisory: bool = False) -> str:
    a, b = set(map(_hashable, gt)), set(map(_hashable, resp))
    if a == b:
        return MATCH
    if len(a ^ b) == 1:
        return PARTIAL
    return PARTIAL if advisory else DIVERGENCE


def _classify_set_map(
    gt: dict[str, list[Any]], resp: dict[str, list[Any]], advisory: bool = False
) -> str:
    worst = MATCH
    for name in sorted(set(gt) | set(resp)):
        verdict = _classify_set(gt.get(name, []), resp.get(name, []), advisory=advisory)
        worst = _worse(worst, verdict)
    return worst


def _classify_tally(gt: dict[str, Any], resp: dict[str, Any]) -> str:
    worst = MATCH
    for key in ("support", "oppose", "conditional"):
        a, b = gt.get(key), resp.get(key)
        if a == b:
            continue
        if isinstance(a, int) and isinstance(b, int) and abs(a - b) == 1:
            worst = _worse(worst, PARTIAL)
        else:
            return DIVERGENCE
    return worst


def _classify_findings(gt: list[list[str]], resp: list[list[str]]) -> str:
    gt_keys = {(row[0], row[1], row[2]) for row in gt}
    resp_keys = {(row[0], row[1], row[2]) for row in resp}
    gt_stance = {(row[0], row[1], row[2]): row[3] for row in gt}
    resp_stance = {(row[0], row[1], row[2]): row[3] for row in resp}

    if gt_keys - resp_keys or resp_keys - gt_keys:
        return DIVERGENCE

    worst = MATCH
    for key in gt_keys:
        a, b = gt_stance[key], resp_stance[key]
        if a == b:
            continue
        if {a, b} == {"supports", "opposes"}:
            return DIVERGENCE
        worst = _worse(worst, PARTIAL)
    return worst


def _classify_citations(
    gt: dict[str, dict[str, list[str]]], resp: dict[str, dict[str, list[str]]]
) -> str:
    worst = MATCH
    for key in sorted(set(gt) | set(resp)):
        if key not in gt or key not in resp:
            return DIVERGENCE
        for slot in ("claim_ids", "evidence_ids"):
            a, b = set(gt[key].get(slot, [])), set(resp[key].get(slot, []))
            if a == b:
                continue
            worst = _worse(worst, PARTIAL if len(a ^ b) == 1 else DIVERGENCE)
    return worst


_SEVERITY = {MATCH: 0, PARTIAL: 1, DIVERGENCE: 2}


def _worse(a: str, b: str) -> str:
    return a if _SEVERITY[a] >= _SEVERITY[b] else b


def _hashable(value: Any) -> Any:
    return tuple(value) if isinstance(value, list) else value


def _classify_field(field: str, gt: Any, resp: Any) -> str:
    if field in ("recommendation", "fired_rule", "confidence_limiting_factor"):
        return _classify_scalar(field, gt, resp)
    if field == "confidence":
        return _classify_scalar(field, gt, resp)
    if field == "kernel_bands":
        return _classify_band_map(gt, resp)
    if field in (
        "kernel_limiting_factors",
        "kernel_coverage",
        "kernel_derivation_outcome",
    ):
        return _classify_str_map(gt, resp)
    if field == "kernel_contradictions":
        return _classify_int_map(gt, resp)
    if field in ("kernel_derivation_steps", "kernel_unresolved"):
        return _classify_set_map(gt, resp, advisory=field in ADVISORY_FIELDS)
    if field == "findings":
        return _classify_findings(gt, resp)
    if field == "finding_citations":
        return _classify_citations(gt, resp)
    if field == "tally":
        return _classify_tally(gt, resp)
    if field in (
        "usable_kernels",
        "agreements",
        "disagreements",
        "remaining_uncertainty",
    ):
        return _classify_set(gt, resp)
    raise KeyError(field)


# --------------------------------------------------------------------------
# whole-case roll-up
# --------------------------------------------------------------------------


def compare_views(
    gt_view: dict[str, Any],
    resp_view: dict[str, Any],
    x4_violations: list[str],
) -> dict[str, Any]:
    """Diff two comparison views and roll up to a whole-case verdict."""
    per_field: dict[str, dict[str, str]] = {}
    for tier, fields in (
        ("tier1", TIER1_FIELDS),
        ("tier2", TIER2_FIELDS),
        ("tier3", TIER3_FIELDS),
    ):
        per_field[tier] = {
            field: _classify_field(field, gt_view.get(field), resp_view.get(field))
            for field in fields
        }

    tier1 = per_field["tier1"]
    tier2 = per_field["tier2"]
    tier3 = per_field["tier3"]

    tier1_divergence = any(v == DIVERGENCE for v in tier1.values())
    hard_tier2_divergence = any(
        tier2.get(field) == DIVERGENCE for field in HARD_TIER2_FIELDS if field in tier2
    )
    findings_stance_flip = tier2.get("findings") == DIVERGENCE
    honesty_divergence = (
        tier3["agreements"] == DIVERGENCE or tier3["disagreements"] == DIVERGENCE
    )

    countable = [v for field, v in tier2.items() if field not in ADVISORY_FIELDS]
    tier2_match_rate = (
        sum(1 for v in countable if v == MATCH) / len(countable) if countable else 1.0
    )

    any_divergence = any(
        v == DIVERGENCE for tier in (tier1, tier2, tier3) for v in tier.values()
    )

    if (
        tier1_divergence
        or bool(x4_violations)
        or hard_tier2_divergence
        or findings_stance_flip
    ):
        verdict = "Diverges"
    elif any_divergence or tier2_match_rate < 0.90 or honesty_divergence:
        verdict = "Substantially reproduces"
    else:
        verdict = "Reproduces"

    return {
        "verdict": verdict,
        "tier2_match_rate": round(tier2_match_rate, 3),
        "x4_violations": x4_violations,
        "per_field": per_field,
    }


def compare_files(ground_truth_path: Path, response_path: Path) -> dict[str, Any]:
    """Load a ground-truth file and a response file and return the comparison."""
    ground_truth = json.loads(ground_truth_path.read_text(encoding="utf-8"))
    response = json.loads(response_path.read_text(encoding="utf-8"))

    gt_view = ground_truth.get("comparison_view") or build_comparison_view(
        ground_truth["record"]
    )
    resp_record = response.get("record", response)
    resp_view = build_comparison_view(resp_record)

    allowed = set(ground_truth.get("ir_known_ids", []))
    violations = sorted(id_ for id_ in cited_ids(resp_record) if id_ not in allowed)

    result = compare_views(gt_view, resp_view, violations)
    result["ground_truth"] = str(ground_truth_path)
    result["response"] = str(response_path)
    result["packet_id"] = ground_truth.get("packet_id")
    return result


def render_table(result: dict[str, Any]) -> str:
    """A plain-text summary of one comparison."""
    lines = [
        "=" * 78,
        f"RUBRIC-REPRODUCTION COMPARISON -- {result.get('packet_id')}",
        "=" * 78,
        f"ground truth : {result['ground_truth']}",
        f"response     : {result['response']}",
        "",
        f"VERDICT: {result['verdict']}   "
        f"(tier-2 match rate {result['tier2_match_rate']})",
        "",
    ]
    for tier in ("tier1", "tier2", "tier3"):
        lines.append(f"-- {tier} --")
        for field, verdict in result["per_field"][tier].items():
            lines.append(f"  {verdict:<11} {field}")
        lines.append("")
    if result["x4_violations"]:
        lines.append("X4 VIOLATIONS (cited ids absent from the IR):")
        for violation in result["x4_violations"]:
            lines.append(f"  - {violation}")
    else:
        lines.append("X4: no cited id is absent from the IR.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """Compare one response file against one ground-truth file."""
    parser = argparse.ArgumentParser(
        prog="python -m experiments.rubric_reproduction.compare",
        description="Deterministic diff of a control response against ground truth.",
    )
    parser.add_argument("--ground-truth", required=True, type=Path)
    parser.add_argument("--response", required=True, type=Path)
    parser.add_argument("--out", type=Path, default=RESULTS_DIR)
    args = parser.parse_args(argv)

    if not args.ground_truth.is_file():
        print(f"ground-truth file not found: {args.ground_truth}", file=sys.stderr)
        return 2
    if not args.response.is_file():
        print(f"response file not found: {args.response}", file=sys.stderr)
        return 2

    result = compare_files(args.ground_truth, args.response)
    print(render_table(result))

    args.out.mkdir(parents=True, exist_ok=True)
    stem = f"{result.get('packet_id')}__{args.response.stem}"
    out_path = args.out / f"comparison__{stem}.json"
    out_path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"\nwritten: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
