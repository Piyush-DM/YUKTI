"""Build the training/analysis dataset from the saved run traces. Reads only; calls no model.

    python build_dataset.py            (from the DAALE_2026-11-10 folder)

Writes dataset_2026-11-17/*.jsonl. Re-running overwrites them. The R-Fabric/runs traces are the source of truth.
"""

import collections
import glob
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RF = ROOT / "R-Fabric"
OUT = ROOT / "dataset_2026-11-17"
OUT.mkdir(exist_ok=True)

# case_id -> (case file, expectation file or None, family, kind, provenance)
CASES = {
    "DD-001": ("cases/vendor_alpha.json", None, "vendor", "synthetic",
               "Synthetic vendor due-diligence case, built so two critical requirements fail (no SOC 2, incomplete questionnaire)."),
    "DD-002": ("cases/vendor_beta.json", "cases/expected/vendor_beta.expected.json", "vendor", "synthetic",
               "Synthetic vendor case, expectation registered before the run."),
    "DD-003": ("cases/vendor_gamma.json", "cases/expected/vendor_gamma.expected.json", "vendor", "synthetic",
               "Synthetic vendor case written after seeing DD-002, so not a blind first sample."),
    "INV-BANK-A": ("cases/inv_bank_a.json", "cases/expected/inv_bank_a.expected.json", "bank", "as_published",
                   "Paraphrased from a fund manager's published case study of a holding; company and country not named."),
    "INV-BANK-B": ("cases/_superseded_bank_b_v1/inv_bank_b.json", "cases/_superseded_bank_b_v1/inv_bank_b.expected.json",
                   "bank", "synthetic_reversed", "First version of the reversed bank case; superseded by INV-BANK-B2."),
    "INV-BANK-B2": ("cases/inv_bank_b2.json", "cases/expected/inv_bank_b2.expected.json", "bank", "synthetic_reversed",
                    "Derived from INV-BANK-A with the financial-strength evidence replaced by invented adverse facts."),
    "INV-LOGISTICS-A": ("cases/inv_logistics_a.json", "cases/expected/inv_logistics_a.expected.json", "logistics",
                        "as_published", "Paraphrased from a fund manager's published case study; company not named."),
    "INV-LOGISTICS-B": ("cases/inv_logistics_b.json", "cases/expected/inv_logistics_b.expected.json", "logistics",
                        "synthetic_reversed", "Derived from INV-LOGISTICS-A with the management evidence replaced by invented adverse facts."),
    "INV-STRESS-1": ("cases/inv_stress_1.json", "cases/expected/inv_stress_1.expected.json", "stress", "stress_synthetic",
                     "Synthetic stress case built to break the engine: 17 evidence items, a buried multi-item failure, a prompt injection."),
}
DESIGN_EXPECTATION = {"DD-001": {"expected_policy_state": "REJECT", "expected_failed_requirement": None,
                                 "label_source": "design"}}


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def expectation(case_id):
    _, exp_path, *_ = CASES[case_id]
    if exp_path is None:
        return DESIGN_EXPECTATION[case_id]
    p = RF / exp_path
    if not p.exists():
        return None
    e = load(p)
    return {
        "expected_policy_state": e.get("expected_policy_state"),
        "expected_rule": e.get("expected_rule"),
        "expected_requirements": e.get("expected_requirements"),
        "expected_failed_requirement": e.get("expected_failed_requirement"),
        "registered_at": e.get("registered_at"),
        "label_source": "registered_before_run",
    }


def write(name, rows):
    with open(OUT / name, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{name}: {len(rows)} rows")


def main():
    cases, runs, kernels, reqs, advs, fails, sft = [], [], [], [], [], [], []
    for case_id, (case_file, _, family, kind, prov) in CASES.items():
        case = load(RF / case_file)
        cases.append({
            "case_id": case_id, "family": family, "kind": kind, "provenance": prov,
            "case": case, "case_sha256": hashlib.sha256(json.dumps(case, sort_keys=True).encode()).hexdigest(),
            "label": expectation(case_id),
        })

    for f in sorted(glob.glob(str(RF / "runs" / "*.json"))):
        t = load(f)
        dp = t["decision_packet"]
        case_id = dp["case_id"]
        if case_id not in CASES:
            continue
        run_id = t["run"]["run_id"]
        es = t["execution_state"]
        ei = dp["execution_integrity"]
        lab = expectation(case_id)
        complete = not es["failed_kernels"] and es["adversary"] == "ran"
        match = None
        if complete and lab:
            match = dp["policy_state"] == lab["expected_policy_state"]
        runs.append({
            "run_id": run_id, "timestamp": t["run"]["timestamp"], "case_id": case_id, "family": CASES[case_id][2],
            "policy_id": dp["policy_id"], "policy_version": dp["policy_version"],
            "policy_state": dp["policy_state"], "rule_id": dp["triggered_rule"]["rule_id"],
            "other_matching_rules": dp.get("other_matching_rule_ids", []),
            "complete_run": complete, "failed_kernels": es["failed_kernels"], "adversary": es["adversary"],
            "fallbacks_used": ei.get("fallbacks_used", []), "metrics": {k: v for k, v in dp["metrics"].items() if k != "details"},
            "metric_details": dp["metrics"].get("details"), "requirement_summary": dp["requirement_summary"],
            "claim_statuses": dp["provisional_claim_statuses"], "adversarial_summary": dp.get("adversarial_summary"),
            "label": lab, "matches_expected": match,
            "usable_as_judgment_example": complete,
        })

        base = {k: v for k, v in t["provisional_findings"].items() if k != "adversary"}
        for kernel, out in t["provisional_findings"].items():
            call = t["model_calls"].get(kernel, {})
            kernels.append({
                "run_id": run_id, "case_id": case_id, "kernel": kernel.upper(), "served_model": call.get("served_model"),
                "requested_model": call.get("requested_model"), "usage": call.get("usage"),
                "passed_validation": True, "summary": out.get("summary"), "uncertainties": out.get("uncertainties"),
                "findings": out["findings"],
            })
            if call.get("messages"):
                sft.append({
                    "run_id": run_id, "case_id": case_id, "family": CASES[case_id][2], "kernel": kernel.upper(),
                    "served_model": call.get("served_model"), "complete_run": complete,
                    "messages": call["messages"] + [{"role": "assistant", "content": json.dumps(out, ensure_ascii=False)}],
                    "label_quality": "teacher_output_unverified",
                })

        # per-requirement verdicts, one row per kernel, with the registered label where one exists
        for rid, v in dp["requirement_summary"].items():
            exp = (lab or {}).get("expected_requirements") or {}
            expected_status = exp.get(rid)
            if (lab or {}).get("expected_failed_requirement") == rid:
                expected_status = "NOT_SATISFIED"
            for kernel, status in (v.get("assessed_by") or {}).items():
                reqs.append({
                    "run_id": run_id, "case_id": case_id, "requirement_id": rid, "kernel": kernel, "verdict": status,
                    "aggregate": v.get("status"), "disagreement": v.get("disagreement"), "expected": expected_status,
                    "kernel_matches_expected": (status == expected_status) if expected_status else None,
                    "complete_run": complete,
                })

        # adversary findings, with whether any base kernel agreed with the target being weak
        for a in t["provisional_findings"].get("adversary", {}).get("findings", []):
            corroborated = False
            for out in base.values():
                for x in out["findings"]:
                    if a["target_type"] == "REQUIREMENT" and x["finding_type"] == "REQUIREMENT_ASSESSMENT" \
                            and x["target_id"] == a["target_id"] and x["status"] != "SATISFIED":
                        corroborated = True
                    if a["target_type"] == "CLAIM" and x["target_id"] == a["target_id"] and (
                            (x["finding_type"] == "CLAIM_ASSESSMENT" and x["status"] != "SUPPORTED")
                            or (x["finding_type"] == "EVIDENCE_RELATION" and x.get("relation") in ("WEAKENS", "CONTRADICTS"))):
                        corroborated = True
            advs.append({
                "run_id": run_id, "case_id": case_id, "served_model": t["model_calls"].get("adversary", {}).get("served_model"),
                "finding_id": a["finding_id"], "finding_type": a["finding_type"], "target_type": a["target_type"],
                "target_id": a["target_id"], "status": a.get("status"), "severity": a["severity"],
                "confidence": a.get("confidence"), "evidence_ids": a["evidence_ids"], "content": a["content"],
                "corroborated_by_a_base_kernel": corroborated, "run_policy_state": dp["policy_state"],
                "human_severity": None, "human_note": None,
            })

        for e in es["audit_events"]:
            if e["event_type"] in ("kernel-failed", "kernel-fallback-used", "kernel-fallback-failed"):
                m = e.get("metadata", {})
                fails.append({
                    "run_id": run_id, "case_id": case_id, "kernel": e["kernel_id"], "event": e["event_type"],
                    "failure_mode": m.get("failure_mode"), "model": m.get("model"), "attempt": m.get("attempt"),
                    "detail": e["detail"][:400],
                })

    write("cases.jsonl", cases)
    write("runs.jsonl", runs)
    write("kernel_outputs.jsonl", kernels)
    write("requirement_verdicts.jsonl", reqs)
    write("adversary_findings.jsonl", advs)
    write("failures.jsonl", fails)
    write("sft_pairs.jsonl", sft)

    # a tiny summary for the dataset card
    c = collections.Counter((r["case_id"], r["complete_run"]) for r in runs)
    print(dict(c))


if __name__ == "__main__":
    main()
