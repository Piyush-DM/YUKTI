"""Recompute a finished run's policy decision from the findings its trace recorded.

DECISION-001 makes replay mandatory and DECISION-005 (condition 2) applies it to the policy step: the
policy state of a completed run must be a deterministic function of the findings the trace recorded.
Model calls are not replayed. They are what was recorded.

    python -m daale.replay runs/<trace>.json

Exit status 0: the recomputed decision matches the recorded one. 1: it differs (the differing
fields are listed). 2: the run was refused, so there was no decision to recompute.
"""

import json
import sys
from pathlib import Path

from .pipeline import block_advance_if_incomplete
from .policy_engine import apply_policy

# The parts of a decision packet that are a pure function of the case, the policy, the recorded
# findings and which kernels failed. ``execution_integrity`` is run state, not decision, so it is
# not compared.
COMPARED = (
    "policy_state",
    "triggered_rule",
    "other_matching_rule_ids",
    "metrics",
    "requirement_summary",
    "provisional_claim_statuses",
    "claim_summary",
    "adversarial_summary",
    "policy_state_before_integrity_check",
)


def replay_decision(trace):
    """The decision packet recomputed from the trace's recorded inputs."""
    outputs = {
        kernel.upper(): {"output": findings}
        for kernel, findings in trace["provisional_findings"].items()
    }
    # A trace recorded before 2026-11-17 has no claim_summary and used last-kernel-wins claim statuses.
    legacy = "claim_summary" not in trace["decision_packet"]
    has_alleged_metric = "alleged_critical_failures" in trace["decision_packet"].get("metrics", {})
    packet = apply_policy(
        trace["case"],
        trace["policy"],
        outputs,
        legacy_claim_statuses=legacy,
        include_alleged_critical_failures=has_alleged_metric,
    )
    return block_advance_if_incomplete(packet, tuple(trace["execution_state"]["failed_kernels"]))


def compare(trace):
    """``(replayable, differences)``. A refused run has no decision to recompute."""
    recorded = trace["decision_packet"]
    if recorded["triggered_rule"]["rule_id"] == "DEGRADED-EXECUTION":
        return False, []
    recomputed = replay_decision(trace)
    differences = [field for field in COMPARED if recorded.get(field) != recomputed.get(field)]
    return True, differences


def main(argv=None):
    arguments = sys.argv[1:] if argv is None else argv
    if len(arguments) != 1:
        print("usage: python -m daale.replay runs/<trace>.json")
        return 2
    trace = json.loads(Path(arguments[0]).read_text(encoding="utf-8"))
    replayable, differences = compare(trace)
    if not replayable:
        print("not replayable: the run was refused (DEGRADED-EXECUTION), so there is no decision to recompute")
        return 2
    if differences:
        print("REPLAY DIFFERS in: " + ", ".join(differences))
        return 1
    state = trace["decision_packet"]["policy_state"]
    print(f"REPLAY OK: policy state {state} recomputed identically from the recorded findings "
          f"({len(COMPARED)} fields compared)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
