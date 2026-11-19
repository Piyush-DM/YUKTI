"""DAALE Execution Contract: failure modes, retries, and recovery semantics.

This module defines the formal contract for pipeline execution, specifying
what happens when things go wrong. It is the "what happens if" layer that
makes the system production-ready.

Failure modes covered:
- Model timeout / unavailable
- Malformed JSON output
- Partial kernel output
- Kernel crash / exception
- Evidence parser failure
- Adversary failure
- Provider rate limit (429)
- Network failure
- Duplicate run detection

Each failure mode has a defined:
- Detection mechanism
- Retry policy (attempts, backoff, max delay)
- Degradation mode (RETRY, DEGRADE, HOLD, ESCALATE, ABORT)
- Audit trace emission
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Optional


class FailureMode(Enum):
    """Classified failure modes for kernel execution."""

    # Transient failures (retryable)
    MODEL_TIMEOUT = "model-timeout"
    MODEL_UNAVAILABLE = "model-unavailable"  # 5xx from provider
    PROVIDER_RATE_LIMIT = "provider-rate-limit"  # 429
    NETWORK_FAILURE = "network-failure"
    TRANSIENT_PROVIDER_ERROR = "transient-provider-error"  # 502, 503, 504

    # Permanent failures (non-retryable)
    MALFORMED_JSON = "malformed-json"
    SCHEMA_VALIDATION_FAILED = "schema-validation-failed"
    EVIDENCE_PARSER_FAILED = "evidence-parser-failed"
    CONTRACT_VIOLATION = "contract-violation"
    KERNEL_CRASH = "kernel-crash"
    ADVERSARY_FAILURE = "adversary-failure"

    # The request budget for the day is spent; nothing retried now can succeed.
    QUOTA_EXHAUSTED = "quota-exhausted"

    # The reply hit the completion token limit. Retrying the same prompt at the
    # same limit would be cut off at the same place.
    OUTPUT_TRUNCATED = "output-truncated"

    # The provider answered, and said this request cannot succeed as sent. Added 2026-11-17 after a
    # live run in which an HTTP 404 ("no longer available to new users") was filed under
    # KERNEL_CRASH: retried on the same dead model, and the configured fallback was never tried.
    # None of these is retried on the same model (it would fail identically).
    MODEL_NOT_AVAILABLE = "model-not-available"        # 404, 410: this model is gone or not open to this key
    AUTHENTICATION_FAILED = "authentication-failed"    # 401, 403: the key or its permissions, not the model
    REQUEST_REJECTED = "request-rejected"              # 400, 413, 422: the model refused this request as written

    # Structural failures
    DUPLICATE_RUN_DETECTED = "duplicate-run-detected"
    INVALID_CONFIGURATION = "invalid-configuration"


class DegradationMode(Enum):
    """How the pipeline responds to a failure."""

    NONE = "none"             # Nothing failed: the run is complete
    RETRY = "retry"           # Retry the same kernel with backoff
    DEGRADE = "degrade"       # Continue with reduced kernel set
    HOLD = "hold"             # Pause execution, require human intervention
    ESCALATE = "escalate"     # Escalate to review (D-Core REVIEW_REQUIRED)
    ABORT = "abort"           # Terminate entire pipeline run


class KernelRole(Enum):
    """Kernel roles for failure policy differentiation."""

    BASE = "base"              # Analyst, Contrarian, First_Principles, Expansionist, Outsider, Historian
    ADVERSARY = "adversary"    # Adversary (runs after base kernels)
    ALL = "all"


@dataclass(frozen=True)
class RetryPolicy:
    """Retry configuration for a failure mode."""

    max_attempts: int
    base_delay_seconds: float
    max_delay_seconds: float
    exponential_base: float = 2.0
    jitter: bool = True


@dataclass(frozen=True)
class FailureRule:
    """Complete failure handling rule."""

    failure_mode: FailureMode
    applicable_roles: tuple[KernelRole, ...]
    retry_policy: Optional[RetryPolicy]
    degradation_mode: DegradationMode
    requires_human_review: bool = False
    audit_detail_template: str = "{failure_mode} in {kernel_id}: {detail}"


# Default retry policies by failure mode
_DEFAULT_RETRY_POLICIES: dict[FailureMode, RetryPolicy] = {
    FailureMode.MODEL_TIMEOUT: RetryPolicy(
        max_attempts=3, base_delay_seconds=5.0, max_delay_seconds=60.0
    ),
    FailureMode.MODEL_UNAVAILABLE: RetryPolicy(
        max_attempts=4, base_delay_seconds=10.0, max_delay_seconds=120.0
    ),
    FailureMode.PROVIDER_RATE_LIMIT: RetryPolicy(
        max_attempts=6, base_delay_seconds=30.0, max_delay_seconds=300.0
    ),
    FailureMode.NETWORK_FAILURE: RetryPolicy(
        max_attempts=3, base_delay_seconds=2.0, max_delay_seconds=30.0
    ),
    FailureMode.TRANSIENT_PROVIDER_ERROR: RetryPolicy(
        max_attempts=4, base_delay_seconds=5.0, max_delay_seconds=60.0
    ),
}


# Failure handling rules (the execution contract)
FAILURE_RULES: tuple[FailureRule, ...] = (
    # Transient model failures - retry with backoff
    FailureRule(
        failure_mode=FailureMode.MODEL_TIMEOUT,
        applicable_roles=(KernelRole.BASE, KernelRole.ADVERSARY),
        retry_policy=_DEFAULT_RETRY_POLICIES[FailureMode.MODEL_TIMEOUT],
        degradation_mode=DegradationMode.RETRY,
    ),
    FailureRule(
        failure_mode=FailureMode.MODEL_UNAVAILABLE,
        applicable_roles=(KernelRole.BASE, KernelRole.ADVERSARY),
        retry_policy=_DEFAULT_RETRY_POLICIES[FailureMode.MODEL_UNAVAILABLE],
        degradation_mode=DegradationMode.RETRY,
    ),
    FailureRule(
        failure_mode=FailureMode.PROVIDER_RATE_LIMIT,
        applicable_roles=(KernelRole.BASE, KernelRole.ADVERSARY),
        retry_policy=_DEFAULT_RETRY_POLICIES[FailureMode.PROVIDER_RATE_LIMIT],
        degradation_mode=DegradationMode.RETRY,
    ),
    FailureRule(
        failure_mode=FailureMode.NETWORK_FAILURE,
        applicable_roles=(KernelRole.BASE, KernelRole.ADVERSARY),
        retry_policy=_DEFAULT_RETRY_POLICIES[FailureMode.NETWORK_FAILURE],
        degradation_mode=DegradationMode.RETRY,
    ),
    FailureRule(
        failure_mode=FailureMode.TRANSIENT_PROVIDER_ERROR,
        applicable_roles=(KernelRole.BASE, KernelRole.ADVERSARY),
        retry_policy=_DEFAULT_RETRY_POLICIES[FailureMode.TRANSIENT_PROVIDER_ERROR],
        degradation_mode=DegradationMode.RETRY,
    ),

    # Malformed output - retry once (model may self-correct), then degrade
    FailureRule(
        failure_mode=FailureMode.MALFORMED_JSON,
        applicable_roles=(KernelRole.BASE, KernelRole.ADVERSARY),
        # Live models were observed returning unparseable JSON on roughly one
        # call in three, intermittently; one retry was not enough.
        retry_policy=RetryPolicy(max_attempts=3, base_delay_seconds=1.0, max_delay_seconds=5.0),
        degradation_mode=DegradationMode.DEGRADE,
    ),

    # Schema validation failure - retry once, then degrade
    FailureRule(
        failure_mode=FailureMode.SCHEMA_VALIDATION_FAILED,
        applicable_roles=(KernelRole.BASE, KernelRole.ADVERSARY),
        retry_policy=RetryPolicy(max_attempts=2, base_delay_seconds=1.0, max_delay_seconds=5.0),
        degradation_mode=DegradationMode.DEGRADE,
    ),

    # Evidence parser failure - degrade (can't fix by retrying)
    FailureRule(
        failure_mode=FailureMode.EVIDENCE_PARSER_FAILED,
        applicable_roles=(KernelRole.ALL,),
        retry_policy=None,
        degradation_mode=DegradationMode.DEGRADE,
        requires_human_review=True,
    ),

    # Contract violation - escalate (data integrity issue)
    FailureRule(
        failure_mode=FailureMode.CONTRACT_VIOLATION,
        applicable_roles=(KernelRole.ALL,),
        retry_policy=None,
        degradation_mode=DegradationMode.ESCALATE,
        requires_human_review=True,
    ),

    # Kernel crash - retry once, then degrade
    FailureRule(
        failure_mode=FailureMode.KERNEL_CRASH,
        applicable_roles=(KernelRole.BASE, KernelRole.ADVERSARY),
        retry_policy=RetryPolicy(max_attempts=2, base_delay_seconds=2.0, max_delay_seconds=10.0),
        degradation_mode=DegradationMode.DEGRADE,
    ),

    # Adversary failure - degrade (base kernels already ran)
    FailureRule(
        failure_mode=FailureMode.ADVERSARY_FAILURE,
        applicable_roles=(KernelRole.ADVERSARY,),
        retry_policy=RetryPolicy(max_attempts=2, base_delay_seconds=2.0, max_delay_seconds=10.0),
        degradation_mode=DegradationMode.DEGRADE,
    ),

    # Reply cut off at the token limit. The same prompt at temperature 0 tends to loop again, so
    # this is retried once, with a nudge to answer directly (see the pipeline); where a fallback
    # model is configured the pipeline goes straight to it instead.
    FailureRule(
        failure_mode=FailureMode.OUTPUT_TRUNCATED,
        applicable_roles=(KernelRole.BASE, KernelRole.ADVERSARY),
        retry_policy=RetryPolicy(max_attempts=2, base_delay_seconds=1.0, max_delay_seconds=5.0),
        degradation_mode=DegradationMode.DEGRADE,
    ),

    # Permanent for this model: one attempt, then the pipeline decides whether a fallback is tried.
    # They need an operator (a model to replace, a key to fix, a request to shrink), so a human is told.
    FailureRule(
        failure_mode=FailureMode.MODEL_NOT_AVAILABLE,
        applicable_roles=(KernelRole.BASE, KernelRole.ADVERSARY),
        retry_policy=None,
        degradation_mode=DegradationMode.DEGRADE,
        requires_human_review=True,
    ),
    FailureRule(
        failure_mode=FailureMode.AUTHENTICATION_FAILED,
        applicable_roles=(KernelRole.BASE, KernelRole.ADVERSARY),
        retry_policy=None,
        degradation_mode=DegradationMode.DEGRADE,
        requires_human_review=True,
    ),
    FailureRule(
        failure_mode=FailureMode.REQUEST_REJECTED,
        applicable_roles=(KernelRole.BASE, KernelRole.ADVERSARY),
        retry_policy=None,
        degradation_mode=DegradationMode.DEGRADE,
        requires_human_review=True,
    ),

    # Daily request budget spent - no retry (it would only wait for midnight)
    FailureRule(
        failure_mode=FailureMode.QUOTA_EXHAUSTED,
        applicable_roles=(KernelRole.BASE, KernelRole.ADVERSARY),
        retry_policy=None,
        degradation_mode=DegradationMode.DEGRADE,
        requires_human_review=True,
    ),

    # Duplicate run - abort (idempotency violation)
    FailureRule(
        failure_mode=FailureMode.DUPLICATE_RUN_DETECTED,
        applicable_roles=(KernelRole.ALL,),
        retry_policy=None,
        degradation_mode=DegradationMode.ABORT,
        requires_human_review=True,
    ),

    # Invalid configuration - abort (can't proceed)
    FailureRule(
        failure_mode=FailureMode.INVALID_CONFIGURATION,
        applicable_roles=(KernelRole.ALL,),
        retry_policy=None,
        degradation_mode=DegradationMode.ABORT,
        requires_human_review=True,
    ),
)


@dataclass(frozen=True)
class KernelExecutionResult:
    """Result of a single kernel execution attempt."""

    kernel_id: str
    role: KernelRole
    attempt: int
    success: bool
    output: Optional[Mapping[str, Any]] = None
    failure_mode: Optional[FailureMode] = None
    error_detail: str = ""
    retry_after_seconds: Optional[float] = None


@dataclass(frozen=True)
class PipelineExecutionState:
    """Tracks the execution state across all kernels."""

    case_id: str
    base_results: Mapping[str, KernelExecutionResult]  # kernel_id -> result
    adversary_result: Optional[KernelExecutionResult] = None
    degradation_mode: DegradationMode = DegradationMode.NONE
    failed_kernels: tuple[str, ...] = ()
    requires_human_review: bool = False
    audit_events: tuple[Mapping[str, Any], ...] = ()

    def all_base_kernels_succeeded(self) -> bool:
        return all(r.success for r in self.base_results.values())

    def any_base_kernel_failed(self) -> bool:
        return any(not r.success for r in self.base_results.values())

    def adversary_succeeded(self) -> bool:
        return self.adversary_result is not None and self.adversary_result.success


# Enum values are strings, so max() over them orders alphabetically and
# "retry" outranks "abort". Severity has to be stated explicitly.
_DEGRADATION_SEVERITY: dict[DegradationMode, int] = {
    DegradationMode.NONE: -1,
    DegradationMode.RETRY: 0,
    DegradationMode.DEGRADE: 1,
    DegradationMode.HOLD: 2,
    DegradationMode.ESCALATE: 3,
    DegradationMode.ABORT: 4,
}


def worse_degradation(*modes: DegradationMode) -> DegradationMode:
    """The most severe of the given degradation modes."""
    return max(modes, key=_DEGRADATION_SEVERITY.__getitem__)


def classify_failure(exception: Exception, http_status: Optional[int] = None) -> FailureMode:
    """Classify an exception into a FailureMode.

    A provider error carries its HTTP status on ``status_code`` (set by the
    client); message text is only the fallback, because "error 429" in a
    message contains none of the keywords below and used to fall through to
    KERNEL_CRASH, so rate limits never got their rate-limit backoff.
    """
    error_msg = str(exception).lower()

    if getattr(exception, "quota_exhausted", False):
        return FailureMode.QUOTA_EXHAUSTED
    if getattr(exception, "truncated", False):
        return FailureMode.OUTPUT_TRUNCATED

    if http_status is None:
        http_status = getattr(exception, "status_code", None)

    # HTTP status based classification
    if http_status is not None:
        if http_status == 429:
            # A per-day limit will not lift in a retry window. The wording is checked, not assumed:
            # no 429 body has been captured in the saved traces, so this match is unverified against
            # Google's real payload (it is believed to name a "...PerDay..." quota).
            if "perday" in error_msg.replace("_", "").replace(" ", "").replace("-", ""):
                return FailureMode.QUOTA_EXHAUSTED
            return FailureMode.PROVIDER_RATE_LIMIT
        if http_status == 408:
            return FailureMode.MODEL_TIMEOUT
        if http_status in (404, 410):
            return FailureMode.MODEL_NOT_AVAILABLE
        if http_status in (401, 403):
            return FailureMode.AUTHENTICATION_FAILED
        if http_status in (400, 413, 422):
            return FailureMode.REQUEST_REJECTED
        if http_status >= 500:
            if http_status in (502, 503, 504):
                return FailureMode.TRANSIENT_PROVIDER_ERROR
            return FailureMode.MODEL_UNAVAILABLE

    # Exception message based classification
    if "timeout" in error_msg:
        return FailureMode.MODEL_TIMEOUT
    if "connection" in error_msg or "network" in error_msg or "dns" in error_msg:
        return FailureMode.NETWORK_FAILURE
    if "json" in error_msg or "decode" in error_msg or "parse" in error_msg:
        return FailureMode.MALFORMED_JSON
    if "schema" in error_msg or "validation" in error_msg:
        return FailureMode.SCHEMA_VALIDATION_FAILED
    if "evidence" in error_msg and "pars" in error_msg:
        return FailureMode.EVIDENCE_PARSER_FAILED
    if "contract" in error_msg:
        return FailureMode.CONTRACT_VIOLATION

    # Default to kernel crash for unclassified exceptions
    return FailureMode.KERNEL_CRASH


def get_failure_rule(failure_mode: FailureMode, role: KernelRole) -> Optional[FailureRule]:
    """Get the applicable failure rule for a failure mode and kernel role."""
    for rule in FAILURE_RULES:
        if rule.failure_mode == failure_mode:
            if KernelRole.ALL in rule.applicable_roles or role in rule.applicable_roles:
                return rule
    return None


def calculate_retry_delay(policy: RetryPolicy, attempt: int, retry_after: Optional[float] = None) -> float:
    """Calculate the delay before the next retry attempt."""
    if retry_after is not None:
        return min(max(retry_after, policy.base_delay_seconds), policy.max_delay_seconds)

    delay = policy.base_delay_seconds * (policy.exponential_base ** (attempt - 1))
    if policy.jitter:
        import random
        delay *= (0.5 + random.random())  # 50-150% of calculated delay
    return min(delay, policy.max_delay_seconds)


def should_degrade(state: PipelineExecutionState) -> bool:
    """Determine if pipeline should enter degradation mode."""
    return state.degradation_mode in (DegradationMode.DEGRADE, DegradationMode.HOLD, DegradationMode.ESCALATE)


def can_continue_with_degraded_base(state: PipelineExecutionState) -> bool:
    """Check if enough base kernels succeeded to continue to adversary phase.

    Requires at least 4 of 6 base kernels to have succeeded.
    """
    succeeded = sum(1 for r in state.base_results.values() if r.success)
    return succeeded >= 4


# Audit event helpers
def make_audit_event(
    event_type: str,
    case_id: str,
    kernel_id: str,
    detail: str,
    metadata: Optional[Mapping[str, Any]] = None,
) -> Mapping[str, Any]:
    """Create a standardized audit event."""
    import time
    event = {
        "timestamp": time.time(),
        "event_type": event_type,
        "case_id": case_id,
        "kernel_id": kernel_id,
        "detail": detail,
    }
    if metadata:
        event["metadata"] = dict(metadata)
    return event


__all__ = [
    "FailureMode",
    "DegradationMode",
    "KernelRole",
    "RetryPolicy",
    "FailureRule",
    "KernelExecutionResult",
    "PipelineExecutionState",
    "FAILURE_RULES",
    "classify_failure",
    "get_failure_rule",
    "calculate_retry_delay",
    "worse_degradation",
    "should_degrade",
    "can_continue_with_degraded_base",
    "make_audit_event",
]