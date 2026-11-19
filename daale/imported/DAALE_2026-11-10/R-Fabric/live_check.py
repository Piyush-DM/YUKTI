"""Live check: do all six base kernels, and the adversary, succeed against the real model?

    python live_check.py              # one full judgment on the sample case
    python live_check.py --base-only  # only the six base kernels: no adversary call, a few minutes faster

Needs the key in .env. Exit status 0 only when every base kernel succeeded and, in a full run, the
adversary ran, no kernel failed and the policy decision replays identically from the trace. It prints
a table and never a key. A full run also writes its trace under runs/.

This is a diagnostic, not a unit test: it makes real model calls (up to seven requests, one of them
against the adversary's daily budget) and takes several minutes. tests/test_live_six_kernels.py wraps
it behind DAALE_LIVE=1. The logic that decides pass or fail is covered offline by test_live_check.py.
"""

import json
import logging
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

from daale.budget import BudgetExhausted
from daale.client import DaaleModelError
from daale.pipeline import ADVERSARIAL_KERNEL, BASE_KERNELS, DaalePipeline
from daale.network import force_ipv4, ipv6_is_broken
from daale.providers import build_live_client, env_bool, fallback_by_kernel_from_env, model_by_kernel_from_env
from daale.replay import compare
from daale.trace import write_trace
from daale.validation import DaaleValidationError

ROOT = Path(__file__).resolve().parent


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


@dataclass
class Row:
    kernel: str
    ok: bool
    attempts: int
    tokens: object = None
    note: str = ""


@dataclass
class Report:
    rows: list
    adversary: str = "not-run"
    decision: str = ""
    review: str = ""
    replay: str = ""
    trace_path: str = ""
    problems: list = field(default_factory=list)

    @property
    def ok(self):
        return not self.problems

    @property
    def succeeded(self):
        return sum(1 for row in self.rows if row.ok)

    def render(self):
        lines = [f"{'kernel':<18}{'result':<8}{'attempts':<10}{'tokens':<8}note"]
        for row in self.rows:
            lines.append(
                f"{row.kernel:<18}{'ok' if row.ok else 'FAILED':<8}{row.attempts:<10}"
                f"{'' if row.tokens is None else row.tokens!s:<8}{row.note}"
            )
        lines.append(f"\n{self.succeeded}/{len(BASE_KERNELS)} base kernels succeeded")
        if self.decision:
            lines.append(f"adversary: {self.adversary}")
            lines.append(f"decision:  {self.decision}")
            lines.append(f"review:    {self.review}")
            lines.append(f"replay:    {self.replay}")
        if self.trace_path:
            lines.append(f"trace:     {self.trace_path}")
        lines.append("\nRESULT: " + ("PASS" if self.ok else "FAIL"))
        lines.extend(f"  - {problem}" for problem in self.problems)
        return "\n".join(lines)


def _one_line(text, limit=160):
    return " ".join(str(text).split())[:limit]


def _attempts(events, kernel):
    """Calls made for one kernel: the failed attempts plus the one that succeeded, if any."""
    mine = [e for e in events if e.get("kernel_id") == kernel]
    failed = sum(1 for e in mine if e["event_type"] == "kernel-failed")
    return failed + (1 if any(e["event_type"] == "kernel-succeeded" for e in mine) else 0)


def _failure_notes(events):
    """The last recorded failure for each kernel, in one line."""
    notes = {}
    for event in events:
        if event["event_type"] == "kernel-failed":
            notes[event["kernel_id"]] = _one_line(event["detail"])
    return notes


def _problems_for_kernels(failed, notes):
    if not failed:
        return []
    detail = "; ".join(f"{kernel}: {notes.get(kernel, 'no detail recorded')}" for kernel in failed)
    return [f"{len(failed)} of {len(BASE_KERNELS)} base kernels failed. {detail}"]


def base_report(outputs, state):
    """Report for a run of the base kernels alone (``DaalePipeline._run_base_kernels``)."""
    notes = _failure_notes(state.audit_events)
    rows = []
    for kernel in BASE_KERNELS:
        result = state.base_results[kernel]
        usage = getattr(outputs.get(kernel, {}).get("record"), "usage", None) or {}
        rows.append(
            Row(kernel, result.success, result.attempt, usage.get("total_tokens"),
                "" if result.success else notes.get(kernel, _one_line(result.error_detail)))
        )
    failed = [row.kernel for row in rows if not row.ok]
    return Report(rows=rows, problems=_problems_for_kernels(failed, notes))


def full_report(result, runs_dir=None):
    """Report for a complete judgment: the six base kernels, the adversary, the decision and its replay."""
    trace = result.trace
    state = trace["execution_state"]
    events = state["audit_events"]
    notes = _failure_notes(events)
    failed = [kernel for kernel in BASE_KERNELS if kernel in state["failed_kernels"]]
    rows = []
    for kernel in BASE_KERNELS:
        usage = trace["model_calls"].get(kernel.lower(), {}).get("usage") or {}
        ok = kernel not in failed
        rows.append(Row(kernel, ok, _attempts(events, kernel), usage.get("total_tokens"),
                        "" if ok else notes.get(kernel, "")))

    packet = result.decision_packet
    integrity = packet.get("execution_integrity", {})
    problems = _problems_for_kernels(failed, notes)
    adversary = state.get("adversary", "unknown")
    if adversary != "ran":
        problems.append(f"the adversary did not run (status: {adversary})")
        if ADVERSARIAL_KERNEL in notes:
            problems.append(f"{ADVERSARIAL_KERNEL}: {notes[ADVERSARIAL_KERNEL]}")
    if packet["triggered_rule"]["rule_id"] == "DEGRADED-EXECUTION":
        problems.append("the run was refused: " + packet["triggered_rule"]["description"])

    replayable, differences = compare(trace)
    if not replayable:
        replay = "not replayable (the run was refused)"
    elif differences:
        replay = "DIFFERS in " + ", ".join(differences)
        problems.append("the decision does not replay from the recorded findings: " + replay)
    else:
        replay = "ok, recomputed identically from the recorded findings"

    review = "required" if integrity.get("requires_human_review") else "not required"
    if integrity.get("human_review_reasons"):
        review += " (" + "; ".join(integrity["human_review_reasons"]) + ")"
    rule = packet["triggered_rule"]
    return Report(
        rows=rows,
        adversary=adversary,
        decision=f"{packet['policy_state']} ({rule['rule_id']})",
        review=review,
        replay=replay,
        trace_path=str(write_trace(trace, runs_dir or ROOT / "runs")),
        problems=problems,
    )


def check(base_only=False, client=None, native_json_schema=None, model_by_kernel=None,
          case=None, policy=None, runs_dir=None):
    """Run the live judgment (or just its base kernels) and judge the outcome."""
    case = case or load_json(ROOT / "cases" / "vendor_alpha.json")
    policy = policy or load_json(ROOT / "policies" / "vendor_post_technical_dd_v0_1.json")
    if client is None:
        client, native_json_schema = build_live_client(os.environ)
    if model_by_kernel is None:
        model_by_kernel = model_by_kernel_from_env(os.environ, live=True)
    pipeline = DaalePipeline(
        client=client, model_by_kernel=model_by_kernel, native_json_schema=bool(native_json_schema),
        fallback_by_kernel=fallback_by_kernel_from_env(os.environ),
        isolate_evidence=env_bool(os.environ, "DAALE_EVIDENCE_SEPARATION"),
    )
    if base_only:
        outputs, state = pipeline._run_base_kernels(case, policy)
        return base_report(outputs, state)
    return full_report(pipeline.run(case, policy), runs_dir)


def use_ipv4_if_needed(env=None, out=None):
    """Switch this run to IPv4 when IPv6 to the provider is dead, and say so. True when it switched.

    On such a network every new connection waits about three minutes (eight IPv6 addresses at roughly
    21 s each) before falling back to IPv4, which once made each model call minutes slower than it needed
    to be and looked like the provider queueing the request. ``DAALE_FORCE_IPV4=true`` in .env does this
    for every run; this only protects a check that was started without it.
    """
    env = os.environ if env is None else env
    out = sys.stderr if out is None else out
    if env_bool(env, "DAALE_FORCE_IPV4") or not ipv6_is_broken(env.get("LLM_BASE_URL")):
        return False
    force_ipv4()
    print(
        "This computer cannot reach the provider over IPv6, so each new connection would wait about "
        "three minutes before falling back to IPv4. Using IPv4 only for this run. To make that permanent, "
        "add DAALE_FORCE_IPV4=true to .env.",
        file=out,
    )
    return True


def main(argv=None):
    arguments = sys.argv[1:] if argv is None else argv
    load_dotenv(ROOT / ".env")
    logging.basicConfig(
        level=os.getenv("DAALE_LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,
    )
    use_ipv4_if_needed()
    try:
        report = check(base_only="--base-only" in arguments)
    except (BudgetExhausted, DaaleModelError, DaaleValidationError, ValueError) as error:
        print(f"Live check could not run: {error}")
        return 2
    print(report.render())
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
