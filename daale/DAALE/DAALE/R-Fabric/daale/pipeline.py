"""DAALE v0.1 orchestration pipeline with R-Fabric."""

import concurrent.futures
import time
from dataclasses import dataclass
from typing import Any, Mapping, Optional

from . import CHOIR_CONTRACT_VERSION, DAALE_VERSION
from .policy_engine import apply_policy
from .prompts import build_adversary_messages, build_analyst_messages, build_kernel_messages
from .schemas import (
    ANALYST_OUTPUT_SCHEMA,
    KERNEL_IDS,
    KERNEL_OUTPUT_SCHEMA,
)
from .trace import hash_value, new_run_identity
from .validation import (
    validate_adversary_output,
    validate_analyst_output,
    validate_case_and_policy,
    validate_kernel_output,
)
from .execution_contract import (
    FailureMode,
    DegradationMode,
    KernelRole,
    KernelExecutionResult,
    PipelineExecutionState,
    classify_failure,
    get_failure_rule,
    calculate_retry_delay,
    can_continue_with_degraded_base,
    make_audit_event,
)


BASE_KERNELS = [
    "ANALYST",
    "CONTRARIAN",
    "FIRST_PRINCIPLES",
    "EXPANSIONIST",
    "OUTSIDER",
    "HISTORIAN",
]

ADVERSARIAL_KERNEL = "ADVERSARY"

ALL_KERNELS = BASE_KERNELS + [ADVERSARIAL_KERNEL]


@dataclass(frozen=True)
class PipelineResult:
    decision_packet: dict
    trace: dict


class DaalePipeline:
    def __init__(
        self,
        client,
        model_by_kernel=None,
        native_json_schema=False,
    ):
        self.client = client
        self.model_by_kernel = model_by_kernel or {}
        self.native_json_schema = native_json_schema

    def _get_model(self, kernel_id):
        return self.model_by_kernel.get(kernel_id, self.model_by_kernel.get("default", "nvidia/nemotron-3-ultra-550b-a55b:free"))

    def run(self, case, policy):
        validate_case_and_policy(case, policy)

        # Phase 1: Base kernels run in parallel (independent) with failure handling
        base_outputs, base_execution_state = self._run_base_kernels_with_recovery(case, policy)

        # Check if we can continue to adversary phase
        if not can_continue_with_degraded_base(base_execution_state):
            # Not enough base kernels succeeded - abort with degraded result
            decision_packet = self._make_degraded_decision_packet(
                case, policy, base_execution_state, "insufficient-base-kernels"
            )
            run = new_run_identity()
            trace = self._build_trace(case, policy, {}, decision_packet, run, base_execution_state)
            return PipelineResult(decision_packet=decision_packet, trace=trace)

        # Phase 2: Adversary runs after, seeing all base outputs
        adversary_output, adversary_execution_state = self._run_adversary_with_recovery(
            case, policy, base_outputs
        )

        # Combine all kernel outputs
        all_outputs = {**base_outputs, ADVERSARIAL_KERNEL: adversary_output}

        # Merge execution states
        combined_state = PipelineExecutionState(
            case_id=case["case_id"],
            base_results=base_execution_state.base_results,
            adversary_result=adversary_execution_state.adversary_result,
            degradation_mode=max(
                base_execution_state.degradation_mode,
                adversary_execution_state.degradation_mode,
                key=lambda m: m.value,
            ),
            failed_kernels=base_execution_state.failed_kernels + adversary_execution_state.failed_kernels,
            requires_human_review=base_execution_state.requires_human_review or adversary_execution_state.requires_human_review,
            audit_events=base_execution_state.audit_events + adversary_execution_state.audit_events,
        )

        # Policy evaluation uses all kernel outputs
        decision_packet = apply_policy(case, policy, all_outputs)
        run = new_run_identity()

        trace = self._build_trace(case, policy, all_outputs, decision_packet, run, combined_state)
        return PipelineResult(decision_packet=decision_packet, trace=trace)

    def _run_base_kernels_with_recovery(self, case, policy):
        """Run base kernels with retry/recovery per execution contract."""
        outputs = {}
        results: dict[str, KernelExecutionResult] = {}
        audit_events = []
        failed_kernels = []
        requires_human_review = False
        degradation_mode = DegradationMode.RETRY

        def run_kernel_with_recovery(kernel_id: str) -> KernelExecutionResult:
            nonlocal degradation_mode, requires_human_review
            role = KernelRole.BASE
            rule = None  # Will be set per failure
            max_attempts = 3
            base_delay = 2.0
            max_delay = 60.0

            for attempt in range(1, max_attempts + 1):
                try:
                    messages = build_kernel_messages(
                        kernel_id,
                        case,
                        policy,
                        prior_outputs=None,
                        native_schema=self.native_json_schema,
                    )
                    record = self.client.complete_json(
                        purpose=kernel_id.lower(),
                        model=self._get_model(kernel_id),
                        messages=messages,
                        schema=KERNEL_OUTPUT_SCHEMA,
                    )
                    output = record.output
                    validate_kernel_output(output, case, policy, kernel_id)

                    # Success
                    event = make_audit_event(
                        "kernel-succeeded", case["case_id"], kernel_id,
                        f"kernel {kernel_id} succeeded on attempt {attempt}",
                        {"attempt": attempt, "model": self._get_model(kernel_id)}
                    )
                    audit_events.append(event)

                    return KernelExecutionResult(
                        kernel_id=kernel_id,
                        role=role,
                        attempt=attempt,
                        success=True,
                        output=output,
                    )

                except Exception as e:
                    # Validation errors are data integrity issues - fail fast, no retry
                    from .validation import DaaleValidationError
                    if isinstance(e, DaaleValidationError):
                        event = make_audit_event(
                            "kernel-validation-failed", case["case_id"], kernel_id,
                            f"kernel {kernel_id} validation failed: {e}",
                            {"error": str(e)}
                        )
                        audit_events.append(event)
                        raise

                    failure_mode = classify_failure(e)
                    rule = get_failure_rule(failure_mode, role)

                    event = make_audit_event(
                        "kernel-failed", case["case_id"], kernel_id,
                        f"kernel {kernel_id} attempt {attempt} failed: {failure_mode.value}: {e}",
                        {"attempt": attempt, "failure_mode": failure_mode.value, "error": str(e)}
                    )
                    audit_events.append(event)

                    if rule is None or rule.retry_policy is None or attempt >= rule.retry_policy.max_attempts:
                        # No more retries
                        if rule and rule.degradation_mode == DegradationMode.ESCALATE:
                            requires_human_review = True
                        degradation_mode = max(degradation_mode, rule.degradation_mode if rule else DegradationMode.ABORT, key=lambda m: m.value)
                        return KernelExecutionResult(
                            kernel_id=kernel_id,
                            role=role,
                            attempt=attempt,
                            success=False,
                            failure_mode=failure_mode,
                            error_detail=str(e),
                        )

                    # Calculate delay and retry
                    retry_after = None
                    if hasattr(e, 'response') and e.response is not None:
                        retry_after_header = e.response.headers.get("Retry-After")
                        if retry_after_header:
                            try:
                                retry_after = float(retry_after_header)
                            except ValueError:
                                pass

                    delay = calculate_retry_delay(rule.retry_policy, attempt, retry_after)
                    time.sleep(delay)
                    continue

            # Should not reach here
            return KernelExecutionResult(
                kernel_id=kernel_id,
                role=role,
                attempt=max_attempts,
                success=False,
                failure_mode=FailureMode.KERNEL_CRASH,
                error_detail="exhausted all retry attempts",
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(BASE_KERNELS)) as executor:
            futures = {executor.submit(run_kernel_with_recovery, k): k for k in BASE_KERNELS}
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results[result.kernel_id] = result
                if result.success:
                    # Extract the output from the successful result
                    # We need to re-run the kernel to get the record/messages
                    # For now, store the output and re-fetch record/messages
                    messages = build_kernel_messages(
                        result.kernel_id,
                        case,
                        policy,
                        prior_outputs=None,
                        native_schema=self.native_json_schema,
                    )
                    record = self.client.complete_json(
                        purpose=result.kernel_id.lower(),
                        model=self._get_model(result.kernel_id),
                        messages=messages,
                        schema=KERNEL_OUTPUT_SCHEMA,
                    )
                    validate_kernel_output(record.output, case, policy, result.kernel_id)
                    outputs[result.kernel_id] = {
                        "output": record.output,
                        "record": record,
                        "messages": messages,
                    }
                else:
                    failed_kernels.append(result.kernel_id)

        state = PipelineExecutionState(
            case_id=case["case_id"],
            base_results=results,
            degradation_mode=degradation_mode,
            failed_kernels=tuple(failed_kernels),
            requires_human_review=requires_human_review,
            audit_events=tuple(audit_events),
        )
        return outputs, state

    def _run_adversary_with_recovery(self, case, policy, base_outputs):
        """Run adversary kernel with retry/recovery per execution contract."""
        role = KernelRole.ADVERSARY
        max_attempts = 3
        audit_events = []
        requires_human_review = False
        degradation_mode = DegradationMode.RETRY

        for attempt in range(1, max_attempts + 1):
            try:
                messages = build_adversary_messages(
                    case,
                    policy,
                    {k: v["output"] for k, v in base_outputs.items()},
                    native_schema=self.native_json_schema,
                )
                record = self.client.complete_json(
                    purpose=ADVERSARIAL_KERNEL.lower(),
                    model=self._get_model(ADVERSARIAL_KERNEL),
                    messages=messages,
                    schema=KERNEL_OUTPUT_SCHEMA,
                )
                output = record.output
                validate_adversary_output(output, case, policy)

                event = make_audit_event(
                    "kernel-succeeded", case["case_id"], ADVERSARIAL_KERNEL,
                    f"adversary succeeded on attempt {attempt}",
                    {"attempt": attempt, "model": self._get_model(ADVERSARIAL_KERNEL)}
                )
                audit_events.append(event)

                result = KernelExecutionResult(
                    kernel_id=ADVERSARIAL_KERNEL,
                    role=role,
                    attempt=attempt,
                    success=True,
                    output=output,
                )

                return (
                    {"output": output, "record": record, "messages": messages},
                    PipelineExecutionState(
                        case_id=case["case_id"],
                        base_results={},
                        adversary_result=result,
                        degradation_mode=degradation_mode,
                        failed_kernels=(),
                        requires_human_review=requires_human_review,
                        audit_events=tuple(audit_events),
                    )
                )

            except Exception as e:
                failure_mode = classify_failure(e)
                rule = get_failure_rule(failure_mode, role)

                event = make_audit_event(
                    "kernel-failed", case["case_id"], ADVERSARIAL_KERNEL,
                    f"adversary attempt {attempt} failed: {failure_mode.value}: {e}",
                    {"attempt": attempt, "failure_mode": failure_mode.value, "error": str(e)}
                )
                audit_events.append(event)

                if rule is None or rule.retry_policy is None or attempt >= rule.retry_policy.max_attempts:
                    if rule and rule.degradation_mode == DegradationMode.ESCALATE:
                        requires_human_review = True
                    degradation_mode = max(degradation_mode, rule.degradation_mode if rule else DegradationMode.ABORT, key=lambda m: m.value)
                    result = KernelExecutionResult(
                        kernel_id=ADVERSARIAL_KERNEL,
                        role=role,
                        attempt=attempt,
                        success=False,
                        failure_mode=failure_mode,
                        error_detail=str(e),
                    )
                    return (
                        None,
                        PipelineExecutionState(
                            case_id=case["case_id"],
                            base_results={},
                            adversary_result=result,
                            degradation_mode=degradation_mode,
                            failed_kernels=(ADVERSARIAL_KERNEL,),
                            requires_human_review=requires_human_review,
                            audit_events=tuple(audit_events),
                        )
                    )

                retry_after = None
                if hasattr(e, 'response') and e.response is not None:
                    retry_after_header = e.response.headers.get("Retry-After")
                    if retry_after_header:
                        try:
                            retry_after = float(retry_after_header)
                        except ValueError:
                            pass

                delay = calculate_retry_delay(rule.retry_policy, attempt, retry_after)
                time.sleep(delay)
                continue

        # Should not reach here
        result = KernelExecutionResult(
            kernel_id=ADVERSARIAL_KERNEL,
            role=role,
            attempt=max_attempts,
            success=False,
            failure_mode=FailureMode.KERNEL_CRASH,
            error_detail="exhausted all retry attempts",
        )
        return (
            None,
            PipelineExecutionState(
                case_id=case["case_id"],
                base_results={},
                adversary_result=result,
                degradation_mode=DegradationMode.ABORT,
                failed_kernels=(ADVERSARIAL_KERNEL,),
                requires_human_review=True,
                audit_events=tuple(audit_events),
            )
        )

    def _make_degraded_decision_packet(self, case, policy, state, reason):
        """Create a decision packet when pipeline is degraded."""
        return {
            "case_id": case["case_id"],
            "decision_stage": case["decision_stage"],
            "policy_id": policy["policy_id"],
            "policy_version": policy["policy_version"],
            "policy_state": "ESCALATE",
            "triggered_rule": {
                "rule_id": "DEGRADED-EXECUTION",
                "priority": -1,
                "description": f"Pipeline degraded: {reason}",
            },
            "other_matching_rule_ids": [],
            "metrics": {
                "high_adversarial_challenges": 0,
                "high_unresolved_contradictions": 0,
                "failed_critical_requirements": 0,
                "failed_mandatory_requirements": 0,
                "unknown_mandatory_requirements": len(policy["requirements"]),
                "all_mandatory_requirements_satisfied": False,
                "supporting_relations": 0,
                "weakening_relations": 0,
                "contradicting_relations": 0,
                "always": True,
                "details": {
                    "high_challenge_ids": [],
                    "high_contradiction_ids": [],
                    "failed_critical_requirement_ids": [],
                    "failed_mandatory_requirement_ids": [],
                    "unknown_mandatory_requirement_ids": [r["requirement_id"] for r in policy["requirements"]],
                    "degradation_reason": reason,
                    "failed_kernels": list(state.failed_kernels),
                    "degradation_mode": state.degradation_mode.value,
                    "requires_human_review": state.requires_human_review,
                },
            },
            "requirement_summary": {
                req["requirement_id"]: {
                    "status": "UNKNOWN",
                    "evidence_ids": [],
                    "rationale": f"Pipeline degraded: {reason}",
                }
                for req in policy["requirements"]
            },
            "provisional_claim_statuses": {
                claim["claim_id"]: "INSUFFICIENT_EVIDENCE"
                for claim in case["claims"]
            },
            "adversarial_summary": f"Pipeline execution degraded: {reason}. Human review required.",
            "authority_notice": (
                "This is a degraded DAALE policy state due to execution failure. "
                "Authorized human review is required."
            ),
        }

    def _build_trace(self, case, policy, all_outputs, decision_packet, run, state=None):
        hashes = {
            "case_sha256": hash_value(case),
            "policy_sha256": hash_value(policy),
            "decision_packet_sha256": hash_value(decision_packet),
        }
        model_calls = {}
        provisional_findings = {}

        for kernel_id, data in all_outputs.items():
            output = data["output"]
            record = data["record"]
            messages = data["messages"]
            key = kernel_id.lower()
            hashes[f"{key}_prompt_sha256"] = hash_value(messages)
            hashes[f"{key}_output_sha256"] = hash_value(output)
            model_calls[key] = _record_to_trace(record, messages)
            provisional_findings[key] = output

        trace = {
            "run": run,
            "choir_contract_version": CHOIR_CONTRACT_VERSION,
            "daale_version": DAALE_VERSION,
            "hashes": hashes,
            "pipeline_steps": [
                {"step": "validate_case_and_policy", "status": "completed"},
                {"step": "r_fabric_base_parallel", "status": "completed"},
                {"step": "r_fabric_adversarial", "status": "completed"},
                {"step": "validate_all_kernels", "status": "completed"},
                {"step": "deterministic_policy_evaluation", "status": "completed"},
            ],
            "case": case,
            "policy": policy,
            "model_calls": model_calls,
            "provisional_findings": provisional_findings,
            "decision_packet": decision_packet,
        }

        if state is not None:
            trace["execution_state"] = {
                "degradation_mode": state.degradation_mode.value,
                "failed_kernels": list(state.failed_kernels),
                "requires_human_review": state.requires_human_review,
                "audit_events": list(state.audit_events),
            }

        return trace


def _record_to_trace(record, messages):
    return {
        "purpose": record.purpose,
        "requested_model": record.requested_model,
        "served_model": record.served_model,
        "request_id": record.request_id,
        "usage": record.usage,
        "messages": messages,
    }