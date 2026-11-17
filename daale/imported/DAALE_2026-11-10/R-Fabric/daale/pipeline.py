"""DAALE v0.1 orchestration pipeline with R-Fabric."""

import concurrent.futures
import json
import logging
import re
import time
from dataclasses import dataclass, field, replace
from typing import Any, Optional

from . import CHOIR_CONTRACT_VERSION, DAALE_VERSION
from .budget import BudgetExhausted
from .client import CompletionRecord
from .execution_contract import (
    DegradationMode,
    FailureMode,
    KernelExecutionResult,
    KernelRole,
    PipelineExecutionState,
    calculate_retry_delay,
    can_continue_with_degraded_base,
    classify_failure,
    get_failure_rule,
    make_audit_event,
    worse_degradation,
)
from .policy_engine import apply_policy
from .prompts import build_adversary_messages, build_kernel_messages
from .schemas import KERNEL_OUTPUT_SCHEMA
from .trace import hash_value, new_run_identity
from .validation import (
    DaaleValidationError,
    validate_adversary_output,
    validate_case_and_policy,
    validate_kernel_output,
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

logger = logging.getLogger("daale.pipeline")

# A hard stop on attempts for one kernel, whatever the failure rule asks for.
MAX_ATTEMPTS_CEILING = 6


class ResumeError(ValueError):
    """A run cannot be resumed from the trace given, and why."""


def budget_shortfall(client, model_by_kernel, kernels=None, fallback_by_kernel=None):
    """``(model, remaining, needed)`` for the first model whose daily budget cannot cover the
    kernels assigned to it (``kernels``, default all), or None. A model with no daily limit never
    falls short. Kernels a model cannot take may spill onto their fallback model, and only what
    the fallback models cannot take either is a shortfall."""
    remaining_for = getattr(client, "requests_remaining", None)
    if remaining_for is None:
        return None
    fallbacks = fallback_by_kernel or {}
    assigned = {}
    for kernel_id in (ALL_KERNELS if kernels is None else kernels):
        model = model_by_kernel.get(kernel_id) or model_by_kernel.get("default")
        assigned.setdefault(model, []).append(kernel_id)
    spill = {}
    for model, kernel_ids in assigned.items():
        remaining = remaining_for(model)
        if remaining is None or remaining >= len(kernel_ids):
            continue
        for kernel_id in kernel_ids[remaining:]:
            fallback = fallbacks.get(kernel_id) or fallbacks.get("default")
            if not fallback or fallback == model:
                return model, remaining, len(kernel_ids)
            spill[fallback] = spill.get(fallback, 0) + 1
    for model, count in spill.items():
        remaining = remaining_for(model)
        if remaining is not None and remaining < count:
            return model, remaining, count
    return None


_REPAIR_HINTS = (
    (
        ("'target_id' is a required property", "'target_type' is a required property"),
        "Every finding, of every type, needs both target_type and target_id. For a finding "
        "about the case as a whole use target_type 'GENERAL' and target_id 'GENERAL'.",
    ),
    (("is not one of",), "Use only the values the schema lists for that field."),
    (
        ("must have target_type 'CLAIM'",),
        "An EVIDENCE_RELATION or CLAIM_ASSESSMENT is about a claim: use target_type 'CLAIM' and a "
        "target_id that is a declared claim id such as 'C1'. Never use 'POLICY' or 'GENERAL' for those.",
    ),
    (
        ("must have target_type 'REQUIREMENT'",),
        "A REQUIREMENT_ASSESSMENT is about a requirement: use target_type 'REQUIREMENT' and a target_id "
        "that is a declared requirement id such as 'R1'.",
    ),
)

TRUNCATION_NUDGE = (
    "Your previous attempt used its whole reply budget reasoning and produced no answer. Do not re-list "
    "or re-derive anything. Reason briefly, then return the complete JSON object now."
)

# Failures another model might not share. Everything else (a bad case, a bad configuration) would
# fail the same way on any model.
_FALLBACK_MODES = {
    FailureMode.TRANSIENT_PROVIDER_ERROR,
    FailureMode.MODEL_UNAVAILABLE,
    FailureMode.MODEL_TIMEOUT,
    FailureMode.PROVIDER_RATE_LIMIT,
    FailureMode.NETWORK_FAILURE,
    FailureMode.QUOTA_EXHAUSTED,
    FailureMode.OUTPUT_TRUNCATED,
    FailureMode.MALFORMED_JSON,
    FailureMode.SCHEMA_VALIDATION_FAILED,
}


def _repair_instruction(error, rejected):
    """The validation error in words a model can act on.

    Array positions ("findings.13") become finding ids, which a model can find, and the common
    mistakes get a one-line fix. The error text itself is kept, so nothing is hidden.
    """
    text = str(error)
    findings = rejected.get("findings") if isinstance(rejected, dict) else None
    if isinstance(findings, list):

        def named(match):
            index = int(match.group(1))
            item = findings[index] if index < len(findings) else None
            finding_id = item.get("finding_id") if isinstance(item, dict) else None
            return f"findings.{index} (finding_id {finding_id})" if finding_id else match.group(0)

        text = re.sub(r"findings\.(\d+)", named, text)
    hints = [hint for needles, hint in _REPAIR_HINTS if any(needle in text for needle in needles)]
    return text + ("\n\nHow to fix: " + " ".join(hints) if hints else "")


@dataclass(frozen=True)
class PipelineResult:
    decision_packet: dict
    trace: dict


@dataclass
class _KernelRun:
    """Everything one kernel execution produced, kept together.

    The record and messages are kept from the call that was validated. The
    previous version threw them away and called the model a second time to get
    them back, which doubled live cost and could trace an output other than the
    one that had been validated.
    """

    result: KernelExecutionResult
    record: Any = None
    messages: Optional[list] = None
    events: list = field(default_factory=list)
    degradation: DegradationMode = DegradationMode.NONE
    requires_human_review: bool = False


class DaalePipeline:
    def __init__(
        self,
        client,
        model_by_kernel=None,
        native_json_schema=False,
        fallback_by_kernel=None,
    ):
        self.client = client
        self.model_by_kernel = model_by_kernel or {}
        self.native_json_schema = native_json_schema
        self.fallback_by_kernel = fallback_by_kernel or {}

    def _get_model(self, kernel_id):
        model = self.model_by_kernel.get(kernel_id) or self.model_by_kernel.get("default")
        if not model or not str(model).strip():
            raise DaaleValidationError(
                f"No model configured for {kernel_id}. Set a default model "
                "(DAALE_DEFAULT_MODEL) or a per-kernel model; none is assumed."
            )
        return model

    def _get_fallback(self, kernel_id):
        """The fallback model for a kernel, or None (none configured, or the same as the primary)."""
        fallback = self.fallback_by_kernel.get(kernel_id) or self.fallback_by_kernel.get("default")
        if not fallback or not str(fallback).strip() or fallback == self._get_model(kernel_id):
            return None
        return fallback

    def run(self, case, policy):
        validate_case_and_policy(case, policy)

        # Configuration is checked before any model call is spent.
        for kernel_id in ALL_KERNELS:
            self._get_model(kernel_id)

        # A judgment needs one request per kernel at the very least. Starting
        # one the daily budget cannot finish spends requests and yields nothing.
        shortfall = budget_shortfall(
            self.client, self.model_by_kernel, fallback_by_kernel=self.fallback_by_kernel
        )
        if shortfall is not None:
            model, remaining, needed = shortfall
            raise BudgetExhausted(
                f"A judgment needs at least {needed} request(s) to {model} and today's budget "
                f"for it has {remaining} left. Nothing was sent."
            )

        # Phase 1: base kernels in parallel, each independently recovered.
        logger.info("case %s: starting %d base kernels in parallel", case["case_id"], len(BASE_KERNELS))
        base_outputs, base_state = self._run_base_kernels(case, policy)
        logger.info(
            "base kernels done: %d succeeded, %d failed %s",
            len(base_outputs), len(base_state.failed_kernels), list(base_state.failed_kernels),
        )

        return self._finish_run(case, policy, base_outputs, base_state)

    def _finish_run(self, case, policy, base_outputs, base_state, resumed_from=None):
        """Everything after the base kernels: the adversary, the policy, the integrity rules, the trace."""
        if not can_continue_with_degraded_base(base_state):
            return self._finish_degraded(
                case, policy, base_outputs, base_state, "insufficient-base-kernels",
                adversary_status="not-run", resumed_from=resumed_from,
            )

        # Phase 2: the adversary sees every surviving base output.
        adversary_run = self._run_adversary(case, policy, base_outputs)

        if adversary_run is None:
            adversary_status = "skipped-no-fixture"
            adversary_events = ()
            adversary_result = None
            adversary_mode = DegradationMode.NONE
            adversary_human = False
        else:
            adversary_events = tuple(adversary_run.events)
            adversary_result = adversary_run.result
            adversary_mode = adversary_run.degradation
            adversary_human = adversary_run.requires_human_review
            adversary_status = "ran" if adversary_run.result.success else "failed"

        failed = base_state.failed_kernels
        if adversary_status == "failed":
            failed = failed + (ADVERSARIAL_KERNEL,)

        state = PipelineExecutionState(
            case_id=case["case_id"],
            base_results=base_state.base_results,
            adversary_result=adversary_result,
            degradation_mode=worse_degradation(base_state.degradation_mode, adversary_mode),
            failed_kernels=failed,
            # Decided 2026-11-09: any failed kernel makes the run incomplete, and an incomplete
            # run always requires human review, whatever the failure rule itself said.
            requires_human_review=bool(failed) or base_state.requires_human_review or adversary_human,
            audit_events=base_state.audit_events + adversary_events,
        )

        all_outputs = dict(base_outputs)
        if adversary_status == "ran":
            all_outputs[ADVERSARIAL_KERNEL] = {
                "output": adversary_run.record.output,
                "record": adversary_run.record,
                "messages": adversary_run.messages,
            }

        # A decision that went unchallenged because the adversary failed is
        # exactly what this architecture exists to prevent. It is not
        # presented as a clean pass; it is refused and sent to a human.
        if adversary_status == "failed":
            return self._finish_degraded(
                case, policy, all_outputs, state, "adversary-failed",
                adversary_status=adversary_status, resumed_from=resumed_from,
            )

        decision_packet = apply_policy(case, policy, all_outputs)
        decision_packet, state = self._apply_integrity_rules(
            policy, decision_packet, state, adversary_status
        )

        run = new_run_identity()
        trace = self._build_trace(
            case, policy, all_outputs, decision_packet, run, state, adversary_status,
            resumed_from=resumed_from,
        )
        return PipelineResult(decision_packet=decision_packet, trace=trace)

    def _reuse_from_trace(self, trace, kernel_id, case, policy):
        """A base kernel's recorded result, ready to reuse, or None if it must be run again.

        A recorded output whose hash no longer matches is refused outright (the trace was
        altered); one that merely fails today's validation is run again.
        """
        key = kernel_id.lower()
        output = trace.get("provisional_findings", {}).get(key)
        call = trace.get("model_calls", {}).get(key)
        if output is None or call is None:
            return None
        hashes = trace["hashes"]
        if (
            hashes.get(f"{key}_output_sha256") != hash_value(output)
            or hashes.get(f"{key}_prompt_sha256") != hash_value(call["messages"])
        ):
            raise ResumeError(
                f"{kernel_id}: its recorded output or prompt does not match the hash in the trace, "
                "so the trace was altered. Nothing was sent."
            )
        try:
            validate_kernel_output(output, case, policy, kernel_id)
        except DaaleValidationError:
            return None
        record = CompletionRecord(
            purpose=call["purpose"],
            output=output,
            requested_model=call["requested_model"],
            served_model=call["served_model"],
            request_id=call["request_id"],
            usage=call["usage"],
        )
        return {"output": output, "record": record, "messages": call["messages"]}

    def resume(self, prior_trace):
        """Finish a run that ended incomplete, running again only what it needs.

        Base kernels that succeeded are reused exactly as recorded (their hashes are checked and
        their outputs validated again). Base kernels that failed are run again. The adversary is
        always run again: it either failed, or it saw base outputs that are being replaced. The
        decision is then computed the ordinary way, from the complete set, and the new trace says
        what it reused and which run it continues, so the audit trail stays whole.

        Case and policy come from the trace itself, so a resume cannot be pointed at different
        material. A request budget too small for what remains is refused before anything is sent.
        """
        case, policy = prior_trace["case"], prior_trace["policy"]
        hashes = prior_trace["hashes"]
        if (
            hashes.get("case_sha256") != hash_value(case)
            or hashes.get("policy_sha256") != hash_value(policy)
            or hashes.get("decision_packet_sha256") != hash_value(prior_trace["decision_packet"])
        ):
            raise ResumeError(
                "The trace's case, policy or decision does not match its recorded hash, so it was "
                "altered. Nothing was sent."
            )
        validate_case_and_policy(case, policy)

        reused = {}
        for kernel_id in BASE_KERNELS:
            entry = self._reuse_from_trace(prior_trace, kernel_id, case, policy)
            if entry is not None:
                reused[kernel_id] = entry
        rerun_base = [k for k in BASE_KERNELS if k not in reused]
        adversary_ran = (
            "adversary" in prior_trace.get("provisional_findings", {})
            and prior_trace["execution_state"].get("adversary") == "ran"
        )
        if not rerun_base and adversary_ran:
            raise ResumeError("Nothing to resume: every kernel in that run succeeded.")

        to_run = rerun_base + [ADVERSARIAL_KERNEL]
        for kernel_id in to_run:
            self._get_model(kernel_id)
        shortfall = budget_shortfall(
            self.client, self.model_by_kernel, kernels=to_run, fallback_by_kernel=self.fallback_by_kernel
        )
        if shortfall is not None:
            model, remaining, needed = shortfall
            raise BudgetExhausted(
                f"Resuming needs at least {needed} request(s) to {model} and today's budget for it "
                f"has {remaining} left. Nothing was sent."
            )

        prior_id = prior_trace["run"]["run_id"]
        logger.info(
            "resuming %s: reusing %s, running again %s", prior_id, list(reused), to_run
        )
        resumed_from = {
            "run_id": prior_id,
            "prior_trace_sha256": hash_value(prior_trace),
            "prior_decision": {
                "policy_state": prior_trace["decision_packet"]["policy_state"],
                "rule_id": prior_trace["decision_packet"]["triggered_rule"]["rule_id"],
            },
            "reused_kernels": list(reused),
            "rerun_kernels": to_run,
        }
        base_outputs, base_state = self._run_base_kernels(
            case,
            policy,
            only=rerun_base,
            reused=reused,
            carried_events=tuple(prior_trace["execution_state"].get("audit_events", [])),
            prior_run_id=prior_id,
        )
        logger.info(
            "base kernels: %d succeeded, %d failed %s",
            len(base_outputs), len(base_state.failed_kernels), list(base_state.failed_kernels),
        )
        return self._finish_run(case, policy, base_outputs, base_state, resumed_from=resumed_from)

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def _execute_kernel(self, kernel_id, role, case, policy, base_outputs=None):
        """Run one kernel to a validated result or a classified failure, on its fallback model if needed.

        The primary model gets its own attempts. If it still fails in a way another model might not
        share, the fallback model (when configured) gets one series of attempts of its own. Both are
        recorded: the audit events keep every attempt, and the packet lists any fallback used.
        """
        primary = self._get_model(kernel_id)
        fallback = self._get_fallback(kernel_id)
        first = self._execute_on_model(kernel_id, role, case, policy, base_outputs, primary, bool(fallback))
        mode = first.result.failure_mode
        if first.result.success or fallback is None or mode not in _FALLBACK_MODES:
            return first

        logger.warning(
            "%s: %s failed on %s (%s); trying fallback model %s", kernel_id, role.value, primary, mode.value, fallback
        )
        # A kernel cut off at the usual ceiling has shown that this prompt needs a longer reply, so the
        # fallback model starts with the escalated ceiling instead of meeting the same wall.
        second = self._execute_on_model(
            kernel_id, role, case, policy, base_outputs, fallback, False,
            boost_tokens=mode is FailureMode.OUTPUT_TRUNCATED,
        )
        events = first.events + second.events
        note = {"from": primary, "to": fallback, "reason": mode.value}
        if second.result.success:
            events.append(make_audit_event(
                "kernel-fallback-used", case["case_id"], kernel_id,
                f"{kernel_id} ran on fallback model {fallback} after {primary} failed: {mode.value}", note,
            ))
        else:
            events.append(make_audit_event(
                "kernel-fallback-failed", case["case_id"], kernel_id,
                f"{kernel_id} also failed on fallback model {fallback}", note,
            ))
        second.events = events
        return second

    def _execute_on_model(self, kernel_id, role, case, policy, base_outputs, model, has_fallback, boost_tokens=False):
        """One model's series of attempts at a kernel."""
        events = []
        attempt = 0
        repair = None  # a rejected reply and why, sent back with the next attempt
        # Set once a reply was truncated: later attempts get the client's escalated ceiling. Only a
        # client that offers one (the generic client) takes part; the others keep their behaviour.
        escalate = getattr(self.client, "escalated_max_tokens", None)

        while True:
            attempt += 1
            started = time.monotonic()
            record = None
            logger.info("%s: calling %s (attempt %d)", kernel_id, model, attempt)
            try:
                if role is KernelRole.ADVERSARY:
                    messages = build_adversary_messages(
                        case,
                        policy,
                        {k: v["output"] for k, v in base_outputs.items()},
                        native_schema=self.native_json_schema,
                    )
                else:
                    messages = build_kernel_messages(
                        kernel_id,
                        case,
                        policy,
                        prior_outputs=None,
                        native_schema=self.native_json_schema,
                    )
                if repair:
                    messages = messages + repair
                extra = {}
                if boost_tokens and escalate is not None:
                    ceiling = escalate(kernel_id.lower())
                    if ceiling > self.client.max_tokens_for(kernel_id.lower()):
                        extra["max_tokens"] = ceiling
                        logger.info("%s: ceiling raised to %d tokens for this attempt", kernel_id, ceiling)
                record = self.client.complete_json(
                    purpose=kernel_id.lower(),
                    model=model,
                    messages=messages,
                    schema=KERNEL_OUTPUT_SCHEMA,
                    **extra,
                )
                if role is KernelRole.ADVERSARY:
                    validate_adversary_output(record.output, case, policy)
                else:
                    validate_kernel_output(record.output, case, policy, kernel_id)
            except Exception as error:  # noqa: BLE001 - classified below
                # The case and policy were validated before any model ran, so a
                # validation error here is the model's output being wrong. That
                # is the contract's SCHEMA_VALIDATION_FAILED: retry, then degrade.
                # The reply a model gets to correct comes from the record (our validators
                # rejected it) or from the error itself (the client's schema check rejected
                # it before a record existed). Missing this second source meant a schema
                # rejection was retried blind, so OUTSIDER repeated the same two mistakes.
                rejected = record.output if record is not None else getattr(error, "output", None)
                if isinstance(error, DaaleValidationError) or rejected is not None:
                    failure_mode = FailureMode.SCHEMA_VALIDATION_FAILED
                else:
                    failure_mode = classify_failure(error)
                if failure_mode is FailureMode.SCHEMA_VALIDATION_FAILED and rejected is not None:
                    # At temperature 0 the same prompt gets the same wrong answer, so a
                    # blind retry is a wasted request. Show the model what was wrong with
                    # its own reply instead.
                    repair = [
                        {"role": "assistant", "content": json.dumps(rejected, ensure_ascii=False)},
                        {
                            "role": "user",
                            "content": (
                                "Your previous reply was rejected by validation:\n"
                                f"{_repair_instruction(error, rejected)}\n\n"
                                "Return the complete corrected JSON object only, with no commentary."
                            ),
                        },
                    ]
                if failure_mode is FailureMode.OUTPUT_TRUNCATED:
                    # Nothing to correct: the model produced no answer. Ask it to answer directly.
                    repair = [{"role": "user", "content": TRUNCATION_NUDGE}]
                    boost_tokens = True  # the next attempt on this model gets a longer ceiling too
                rule = get_failure_rule(failure_mode, role)

                logger.warning(
                    "%s: attempt %d failed after %.1fs: %s (HTTP %s): %s",
                    kernel_id, attempt, time.monotonic() - started, failure_mode.value,
                    getattr(error, "status_code", None) or "-",
                    str(error)[:700].replace("\n", " "),
                )
                events.append(make_audit_event(
                    "kernel-failed", case["case_id"], kernel_id,
                    f"{kernel_id} attempt {attempt} failed: {failure_mode.value}: {error}",
                    {"attempt": attempt, "failure_mode": failure_mode.value,
                     "error": str(error), "model": model},
                ))

                allowed = rule.retry_policy.max_attempts if rule and rule.retry_policy else 1
                if has_fallback:
                    # Another model is waiting: do not spend minutes more on one that is failing. A
                    # truncated reply is not retried at all (it would loop again); the rest get two.
                    allowed = 1 if failure_mode is FailureMode.OUTPUT_TRUNCATED else min(allowed, 2)
                if attempt >= min(allowed, MAX_ATTEMPTS_CEILING):
                    mode = rule.degradation_mode if rule else DegradationMode.ABORT
                    human = bool(rule and rule.requires_human_review) or mode in (
                        DegradationMode.ESCALATE, DegradationMode.ABORT,
                    )
                    logger.error(
                        "%s: giving up after %d attempt(s) (%s); degradation=%s",
                        kernel_id, attempt, failure_mode.value, mode.value,
                    )
                    return _KernelRun(
                        result=KernelExecutionResult(
                            kernel_id=kernel_id,
                            role=role,
                            attempt=attempt,
                            success=False,
                            failure_mode=failure_mode,
                            error_detail=str(error),
                        ),
                        events=events,
                        degradation=mode,
                        requires_human_review=human,
                    )

                retry_after = None
                response = getattr(error, "response", None)
                if response is not None:
                    try:
                        retry_after = float(response.headers.get("Retry-After"))
                    except (TypeError, ValueError):
                        retry_after = None
                delay = calculate_retry_delay(rule.retry_policy, attempt, retry_after)
                logger.info(
                    "%s: waiting %.0fs before attempt %d of at most %d",
                    kernel_id, delay, attempt + 1, min(allowed, MAX_ATTEMPTS_CEILING),
                )
                time.sleep(delay)
                continue

            usage = getattr(record, "usage", None) or {}
            logger.info(
                "%s: ok in %.1fs (attempt %d, total_tokens=%s)",
                kernel_id, time.monotonic() - started, attempt, usage.get("total_tokens", "?"),
            )
            events.append(make_audit_event(
                "kernel-succeeded", case["case_id"], kernel_id,
                f"{kernel_id} succeeded on attempt {attempt}",
                {"attempt": attempt, "model": model},
            ))
            return _KernelRun(
                result=KernelExecutionResult(
                    kernel_id=kernel_id,
                    role=role,
                    attempt=attempt,
                    success=True,
                    output=record.output,
                ),
                record=record,
                messages=messages,
                events=events,
            )

    def _run_base_kernels(self, case, policy, only=None, reused=None, carried_events=(), prior_run_id=None):
        """Run the base kernels (all, or just ``only``) and merge any ``reused`` recorded results."""
        reused = reused or {}
        names = list(BASE_KERNELS if only is None else only)
        runs = {}
        if names:
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(names)) as pool:
                futures = {
                    kernel_id: pool.submit(
                        self._execute_kernel, kernel_id, KernelRole.BASE, case, policy
                    )
                    for kernel_id in names
                }
                runs = {kernel_id: future.result() for kernel_id, future in futures.items()}

        # Assembled in declared kernel order, never completion order, so the
        # same set of kernel outputs always yields the same decision.
        outputs = {}
        results = {}
        events = list(carried_events)
        failed = []
        mode = DegradationMode.NONE
        human = False
        for kernel_id in BASE_KERNELS:
            if kernel_id in reused:
                outputs[kernel_id] = reused[kernel_id]
                results[kernel_id] = KernelExecutionResult(
                    kernel_id=kernel_id,
                    role=KernelRole.BASE,
                    attempt=0,
                    success=True,
                    output=reused[kernel_id]["output"],
                )
                events.append(make_audit_event(
                    "kernel-reused", case["case_id"], kernel_id,
                    f"{kernel_id} reused from run {prior_run_id}",
                    {"from_run": prior_run_id},
                ))
                continue
            run = runs[kernel_id]
            results[kernel_id] = run.result
            events.extend(run.events)
            if run.result.success:
                outputs[kernel_id] = {
                    "output": run.record.output,
                    "record": run.record,
                    "messages": run.messages,
                }
            else:
                failed.append(kernel_id)
                mode = worse_degradation(mode, run.degradation)
                human = human or run.requires_human_review

        # Decided 2026-11-09: a run in which any kernel failed always requires human review.
        human = human or bool(failed)

        state = PipelineExecutionState(
            case_id=case["case_id"],
            base_results=results,
            degradation_mode=mode,
            failed_kernels=tuple(failed),
            requires_human_review=human,
            audit_events=tuple(events),
        )
        return outputs, state

    def _run_adversary(self, case, policy, base_outputs):
        """Run the adversary, or return None when an offline fixture set has none.

        Only a fixture client may lack an adversary. A live client always runs
        it: probing for an ``outputs`` attribute, as this used to, made every
        live run skip the adversary silently.
        """
        if getattr(self.client, "is_fixture", False) and "adversary" not in self.client.outputs:
            return None
        return self._execute_kernel(
            ADVERSARIAL_KERNEL, KernelRole.ADVERSARY, case, policy, base_outputs
        )

    # ------------------------------------------------------------------
    # Results
    # ------------------------------------------------------------------

    @staticmethod
    def _failure_reasons(state):
        if not state.failed_kernels:
            return []
        return [f"kernels failed: {', '.join(state.failed_kernels)}"]

    @staticmethod
    def _integrity(state, adversary_status, reasons=()):
        return {
            "base_kernels_succeeded": [
                k for k in BASE_KERNELS if state.base_results[k].success
            ],
            "base_kernels_failed": [
                k for k in BASE_KERNELS if not state.base_results[k].success
            ],
            "adversary": adversary_status,
            "degradation_mode": state.degradation_mode.value,
            "requires_human_review": state.requires_human_review,
            "human_review_reasons": list(reasons),
            "fallbacks_used": [
                {"kernel": event["kernel_id"], **event.get("metadata", {})}
                for event in state.audit_events
                if event["event_type"] == "kernel-fallback-used"
            ],
        }

    def _apply_integrity_rules(self, policy, decision_packet, state, adversary_status):
        """Rules about what an incomplete or contested run may conclude. Returns (packet, state).

        Decided 2026-11-09; this is the one place to change them:
          * a run in which any kernel failed is incomplete and always requires human review;
          * an incomplete run never emits ADVANCE: a favourable state needs every perspective, so
            it becomes ESCALATE, and the policy's own result stays in the packet;
          * a mandatory or critical requirement that the kernels disagree on requires human
            review (the aggregation has already made it UNKNOWN, so it cannot advance).
        REJECT and HOLD are conservative outcomes and are not blocked.
        """
        reasons = self._failure_reasons(state)

        flags = {item["requirement_id"]: item for item in policy["requirements"]}
        contested = sorted(
            requirement_id
            for requirement_id, summary in decision_packet.get("requirement_summary", {}).items()
            if summary.get("disagreement")
            and (flags[requirement_id]["mandatory"] or flags[requirement_id]["critical"])
        )
        if contested:
            reasons.append("kernels disagree on " + ", ".join(contested))

        if state.failed_kernels and decision_packet["policy_state"] == "ADVANCE":
            decision_packet = block_advance_if_incomplete(decision_packet, state.failed_kernels)
            reasons.append("ADVANCE blocked because the run is incomplete")

        if reasons and not state.requires_human_review:
            state = replace(state, requires_human_review=True)
        decision_packet["execution_integrity"] = self._integrity(state, adversary_status, reasons)
        return decision_packet, state

    def _finish_degraded(self, case, policy, outputs, state, reason, adversary_status, resumed_from=None):
        decision_packet = self._make_degraded_decision_packet(case, policy, state, reason)
        decision_packet["execution_integrity"] = self._integrity(
            state, adversary_status, [f"pipeline degraded: {reason}", *self._failure_reasons(state)]
        )
        run = new_run_identity()
        trace = self._build_trace(
            case, policy, outputs, decision_packet, run, state, adversary_status,
            resumed_from=resumed_from,
        )
        return PipelineResult(decision_packet=decision_packet, trace=trace)

    def _make_degraded_decision_packet(self, case, policy, state, reason):
        """Create a decision packet when the pipeline could not complete."""
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

    @staticmethod
    def _pipeline_steps(state, adversary_status, degraded):
        failed_base = [k for k in state.failed_kernels if k != ADVERSARIAL_KERNEL]
        if not failed_base:
            base_status = "completed"
        elif len(failed_base) <= len(BASE_KERNELS) - 4:
            base_status = "degraded"
        else:
            base_status = "failed"
        adversary_step = {
            "ran": "completed",
            "failed": "failed",
            "skipped-no-fixture": "skipped",
            "not-run": "not-run",
        }[adversary_status]
        return [
            {"step": "validate_case_and_policy", "status": "completed"},
            {"step": "r_fabric_base_parallel", "status": base_status, "failed_kernels": failed_base},
            {"step": "r_fabric_adversarial", "status": adversary_step},
            {
                "step": "deterministic_policy_evaluation",
                "status": "refused-degraded" if degraded else "completed",
            },
        ]

    def _build_trace(self, case, policy, all_outputs, decision_packet, run, state, adversary_status,
                     resumed_from=None):
        hashes = {
            "case_sha256": hash_value(case),
            "policy_sha256": hash_value(policy),
            "decision_packet_sha256": hash_value(decision_packet),
        }
        model_calls = {}
        provisional_findings = {}

        for kernel_id, data in all_outputs.items():
            output = data["output"]
            key = kernel_id.lower()
            hashes[f"{key}_prompt_sha256"] = hash_value(data["messages"])
            hashes[f"{key}_output_sha256"] = hash_value(output)
            model_calls[key] = _record_to_trace(data["record"], data["messages"])
            if resumed_from and kernel_id in resumed_from["reused_kernels"]:
                # Spent in an earlier run; marked so usage is not counted twice.
                model_calls[key]["reused_from_run"] = resumed_from["run_id"]
            provisional_findings[key] = output

        gap_report = _detect_gaps(case, policy, all_outputs, decision_packet)
        degraded = decision_packet["triggered_rule"]["rule_id"] == "DEGRADED-EXECUTION"

        trace = {
            "run": run,
            "choir_contract_version": CHOIR_CONTRACT_VERSION,
            "daale_version": DAALE_VERSION,
            "hashes": hashes,
            "pipeline_steps": self._pipeline_steps(state, adversary_status, degraded),
            "case": case,
            "policy": policy,
            "model_calls": model_calls,
            "provisional_findings": provisional_findings,
            "decision_packet": decision_packet,
            "gap_report": gap_report,
            "execution_state": {
                "degradation_mode": state.degradation_mode.value,
                "failed_kernels": list(state.failed_kernels),
                "requires_human_review": state.requires_human_review,
                "adversary": adversary_status,
                "audit_events": list(state.audit_events),
            },
        }
        if resumed_from is not None:
            trace["resumed_from"] = resumed_from
        return trace


def block_advance_if_incomplete(decision_packet, failed_kernels):
    """ESCALATE in place of an ADVANCE reached by an incomplete run, keeping the policy's own result.

    Shared with ``daale.replay``, so a recomputation applies the same rule the run applied.
    """
    if not failed_kernels or decision_packet["policy_state"] != "ADVANCE":
        return decision_packet
    original = decision_packet["triggered_rule"]
    blocked = dict(decision_packet)
    blocked["policy_state"] = "ESCALATE"
    blocked["triggered_rule"] = {
        "rule_id": "INCOMPLETE-RUN-ADVANCE-BLOCKED",
        "priority": -1,
        "description": (
            f"The policy reached ADVANCE ({original['rule_id']}), but "
            f"{', '.join(failed_kernels)} failed, so the run is incomplete and cannot approve."
        ),
    }
    blocked["other_matching_rule_ids"] = [original["rule_id"], *decision_packet["other_matching_rule_ids"]]
    blocked["policy_state_before_integrity_check"] = "ADVANCE"
    return blocked


def _detect_gaps(case, policy, all_outputs, decision_packet):
    """Detect gaps and issues in the pipeline execution."""
    gaps = {
        "low_confidence_findings": [],
        "missing_evidence_relations": [],
        "missing_evidence_citations": [],
        "low_confidence_requirements": [],
        "unresolved_claims": [],
        "validation_warnings": [],
        "requirement_disagreements": [],
        "unassessed_requirements": [],
        "summary": {}
    }

    claim_ids = {c["claim_id"] for c in case["claims"]}
    evidence_ids = {e["evidence_id"] for e in case["evidence"]}
    requirement_ids = {r["requirement_id"] for r in policy["requirements"]}

    # Analyze each kernel's findings
    for kernel_id, data in all_outputs.items():
        output = data["output"]
        findings = output.get("findings", [])

        for finding in findings:
            confidence = finding.get("confidence", 1.0)
            finding_id = finding.get("finding_id", "unknown")
            finding_type = finding.get("finding_type", "unknown")

            # Flag low confidence findings
            if confidence < 0.5:
                gaps["low_confidence_findings"].append({
                    "kernel": kernel_id,
                    "finding_id": finding_id,
                    "finding_type": finding_type,
                    "confidence": confidence,
                    "target": finding.get("target_id"),
                    "issue": f"Confidence {confidence:.2f} below threshold 0.5"
                })

            # Flag missing evidence citations for findings that should cite evidence
            if finding_type in ("CLAIM_ASSESSMENT", "REQUIREMENT_ASSESSMENT", "EVIDENCE_RELATION", "CHALLENGE", "CONTRADICTION"):
                evidence_ids_cited = finding.get("evidence_ids", [])
                if not evidence_ids_cited and finding_type != "UNCERTAINTY":
                    gaps["missing_evidence_citations"].append({
                        "kernel": kernel_id,
                        "finding_id": finding_id,
                        "finding_type": finding_type,
                        "issue": f"{finding_type} cites no evidence"
                    })

            # Flag low confidence requirement assessments
            if finding_type == "REQUIREMENT_ASSESSMENT" and confidence < 0.6:
                gaps["low_confidence_requirements"].append({
                    "kernel": kernel_id,
                    "requirement_id": finding.get("target_id"),
                    "confidence": confidence,
                    "status": finding.get("status"),
                    "issue": f"Requirement assessment confidence {confidence:.2f} below 0.6"
                })

        # Check evidence relation completeness per kernel (base kernels only)
        if kernel_id != "ADVERSARY":
            for claim_id in claim_ids:
                claim_relations = [
                    f for f in findings
                    if f["finding_type"] == "EVIDENCE_RELATION" and f["target_id"] == claim_id
                ]
                related_evidence = set()
                for rel in claim_relations:
                    if rel["evidence_ids"]:
                        related_evidence.add(rel["evidence_ids"][0])
                missing = evidence_ids - related_evidence
                if missing:
                    gaps["missing_evidence_relations"].append({
                        "kernel": kernel_id,
                        "claim_id": claim_id,
                        "missing_evidence": sorted(missing),
                        "issue": f"Claim {claim_id} missing evidence relations for {len(missing)} evidence item(s)"
                    })

    # Check decision packet for unresolved claims
    provisional_claims = decision_packet.get("provisional_claim_statuses", {})
    for claim_id, status in provisional_claims.items():
        if status == "INSUFFICIENT_EVIDENCE":
            gaps["unresolved_claims"].append({
                "claim_id": claim_id,
                "status": status,
                "issue": "Claim remains unresolved due to insufficient evidence"
            })

    # Check for unknown critical requirements
    req_summary = decision_packet.get("requirement_summary", {})
    for req_id, req_data in req_summary.items():
        if req_data.get("status") == "UNKNOWN":
            req_def = next((r for r in policy["requirements"] if r["requirement_id"] == req_id), None)
            if req_def and req_def.get("critical"):
                gaps["validation_warnings"].append({
                    "type": "critical_requirement_unknown",
                    "requirement_id": req_id,
                    "issue": f"Critical requirement {req_id} is UNKNOWN"
                })

    # Kernels that disagree on a requirement, and requirements no kernel assessed. Both come
    # from the aggregation; a degraded packet carries no "assessed_by", so it raises neither.
    requirement_flags = {r["requirement_id"]: r for r in policy["requirements"]}
    for req_id, req_data in req_summary.items():
        flags = requirement_flags.get(req_id, {})
        weighty = bool(flags.get("mandatory") or flags.get("critical"))
        if req_data.get("disagreement"):
            gaps["requirement_disagreements"].append({
                "requirement_id": req_id,
                "assessed_by": req_data.get("assessed_by", {}),
                "issue": f"Kernels disagree on {req_id}; it is treated as UNKNOWN",
            })
            if weighty:
                gaps["validation_warnings"].append({
                    "type": "requirement_kernels_disagree",
                    "requirement_id": req_id,
                    "issue": f"Kernels disagree on mandatory or critical requirement {req_id}",
                })
        if "assessed_by" in req_data and not req_data["assessed_by"]:
            gaps["unassessed_requirements"].append({
                "requirement_id": req_id,
                "issue": f"No kernel assessed {req_id}; it is treated as UNKNOWN",
            })
            if weighty:
                gaps["validation_warnings"].append({
                    "type": "requirement_not_assessed",
                    "requirement_id": req_id,
                    "issue": f"No kernel assessed mandatory or critical requirement {req_id}",
                })

    # Summary counts
    gaps["summary"] = {
        "total_low_confidence_findings": len(gaps["low_confidence_findings"]),
        "total_missing_evidence_relations": len(gaps["missing_evidence_relations"]),
        "total_missing_evidence_citations": len(gaps["missing_evidence_citations"]),
        "total_low_confidence_requirements": len(gaps["low_confidence_requirements"]),
        "total_unresolved_claims": len(gaps["unresolved_claims"]),
        "total_validation_warnings": len(gaps["validation_warnings"]),
        "total_requirement_disagreements": len(gaps["requirement_disagreements"]),
        "total_unassessed_requirements": len(gaps["unassessed_requirements"]),
        "has_critical_gaps": (
            len(gaps["low_confidence_findings"]) > 0 or
            len(gaps["missing_evidence_relations"]) > 0 or
            len(gaps["missing_evidence_citations"]) > 0 or
            len(gaps["validation_warnings"]) > 0
        )
    }

    return gaps


def _record_to_trace(record, messages):
    if record is None:
        return {
            "purpose": "adversary-skipped",
            "requested_model": "none",
            "served_model": "none",
            "request_id": "none",
            "usage": {},
            "messages": messages or [],
        }
    return {
        "purpose": record.purpose,
        "requested_model": record.requested_model,
        "served_model": record.served_model,
        "request_id": record.request_id,
        "usage": record.usage,
        "messages": messages,
    }