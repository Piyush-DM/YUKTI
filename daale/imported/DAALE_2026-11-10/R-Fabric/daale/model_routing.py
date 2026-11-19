"""Deterministic configured model chains and per-run health state."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass

from .execution_contract import FailureMode


MAX_MODELS_PER_KERNEL = 4


def parse_model_chain(primary: str, fallback) -> tuple[str, ...]:
    """Validate one explicitly configured primary plus at most three fallbacks."""
    if not isinstance(primary, str) or not primary.strip():
        raise ValueError("a model chain requires a non-empty primary model")
    if fallback is None:
        alternatives = ()
    elif isinstance(fallback, str):
        raw_alternatives = fallback.split(",")
        if any(not part.strip() for part in raw_alternatives):
            raise ValueError("a model chain cannot contain an empty fallback model")
        alternatives = tuple(part.strip() for part in raw_alternatives)
    else:
        raw_alternatives = tuple(fallback)
        if any(not isinstance(part, str) or not part.strip() for part in raw_alternatives):
            raise ValueError("fallback models must be non-empty strings")
        alternatives = tuple(part.strip() for part in raw_alternatives)
    chain = (primary.strip(), *alternatives)
    if len(chain) > MAX_MODELS_PER_KERNEL:
        raise ValueError(
            f"a kernel model chain may contain at most {MAX_MODELS_PER_KERNEL} models"
        )
    if len(chain) != len(set(chain)):
        raise ValueError("a kernel model chain cannot repeat a model ID")
    return chain


@dataclass(frozen=True)
class ModelHealth:
    state: str
    reason: str
    until: float | None = None


class RunModelHealth:
    """Thread-safe health map shared by kernels within one pipeline execution.

    DEAD applies to one model for model-specific 404/410 failures. A provider
    authentication failure marks the endpoint dead for the run. COOLING is
    temporary and expires automatically, allowing a preferred model to return
    on a later kernel or run.
    """

    def __init__(self, clock=time.monotonic):
        self._clock = clock
        self._lock = threading.Lock()
        self._models: dict[str, ModelHealth] = {}
        self._dead_providers: dict[str, str] = {}

    def status(self, model: str, provider: str) -> ModelHealth:
        with self._lock:
            if provider in self._dead_providers:
                return ModelHealth("DEAD", self._dead_providers[provider])
            state = self._models.get(model)
            if state is None:
                return ModelHealth("HEALTHY", "")
            if state.state == "COOLING" and state.until is not None:
                remaining = state.until - self._clock()
                if remaining <= 0:
                    del self._models[model]
                    return ModelHealth("HEALTHY", "")
                return ModelHealth("COOLING", state.reason, state.until)
            return state

    def seconds_remaining(self, model: str, provider: str) -> float | None:
        health = self.status(model, provider)
        if health.state != "COOLING" or health.until is None:
            return None
        return max(0.0, health.until - self._clock())

    def mark_failure(
        self,
        model: str,
        provider: str,
        failure_mode: FailureMode | None,
        *,
        retry_after: float | None = None,
        daily_reset_seconds: float | None = None,
    ) -> ModelHealth:
        if failure_mode is FailureMode.AUTHENTICATION_FAILED:
            with self._lock:
                self._dead_providers[provider] = failure_mode.value
            return ModelHealth("DEAD", failure_mode.value)
        if failure_mode is FailureMode.MODEL_NOT_AVAILABLE:
            state = ModelHealth("DEAD", failure_mode.value)
        elif failure_mode is FailureMode.QUOTA_EXHAUSTED:
            delay = daily_reset_seconds if daily_reset_seconds is not None else 3600.0
            state = ModelHealth("COOLING", failure_mode.value, self._clock() + max(1.0, delay))
        elif failure_mode is FailureMode.PROVIDER_RATE_LIMIT:
            delay = retry_after if retry_after is not None else 60.0
            state = ModelHealth("COOLING", failure_mode.value, self._clock() + max(1.0, delay))
        else:
            return self.status(model, provider)
        with self._lock:
            self._models[model] = state
        return state

    def snapshot(self) -> dict:
        with self._lock:
            now = self._clock()
            models = {}
            for model, state in sorted(self._models.items()):
                if state.state == "COOLING" and state.until is not None:
                    remaining = max(0.0, state.until - now)
                    if remaining <= 0:
                        continue
                    models[model] = {
                        "state": "COOLING",
                        "reason": state.reason,
                        "seconds_remaining_at_snapshot": round(remaining, 3),
                    }
                else:
                    models[model] = {"state": state.state, "reason": state.reason}
            return {
                "models": models,
                "providers": {
                    provider: {"state": "DEAD", "reason": reason}
                    for provider, reason in sorted(self._dead_providers.items())
                },
            }


__all__ = ["MAX_MODELS_PER_KERNEL", "ModelHealth", "RunModelHealth", "parse_model_chain"]
