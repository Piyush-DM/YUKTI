"""Build the live model client and model selection from the environment.

Shared by the command line (run_daale.py) and the HTTP service, so both read
the same variables the same way. Nothing here is OpenRouter-specific except the
``openrouter`` branch.
"""

import os

from .client import (
    AimlApiClient,
    GenericApiClient,
    ModelPacers,
    NvidiaClient,
    OpenRouterClient,
)
from .network import force_ipv4
from .pipeline import ALL_KERNELS

PROVIDERS = ("openrouter", "generic", "nvidia", "aimlapi")


def env_bool(env, name, default=False):
    raw = env.get(name)
    if raw is None:
        return default
    normalized = raw.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} must be true or false, received: {raw}")


def parse_limits(spec):
    """``"a=5/20/250k;b=15/-"`` -> ``{"a": (5, 20, 250000), "b": (15, None, None)}``."""
    limits = {}
    for entry in filter(None, (part.strip() for part in (spec or "").replace(",", ";").split(";"))):
        model, _, rates = entry.partition("=")
        parts = rates.split("/")
        if not model.strip() or not parts[0] or len(parts) > 3:
            raise ValueError(
                f"LLM_LIMITS entry must look like model=5/20/250k (per minute / per day / "
                f"tokens per minute; - for none): {entry!r}"
            )

        def number(text):
            text = text.strip().lower()
            if text in ("", "-"):
                return None
            return int(float(text[:-1]) * 1000) if text.endswith("k") else int(text)

        values = [number(part) for part in parts] + [None] * (3 - len(parts))
        limits[model.strip()] = tuple(values)
    return limits


def pacers_from_env(env=None):
    """Per-model pacing and daily budgets from LLM_LIMITS and the defaults."""
    env = os.environ if env is None else env

    def optional(name):
        return int(env[name]) if env.get(name) else None

    return ModelPacers(
        limits=parse_limits(env.get("LLM_LIMITS")),
        default_per_minute=optional("LLM_MAX_REQUESTS_PER_MINUTE"),
        default_per_day=optional("LLM_MAX_REQUESTS_PER_DAY"),
        default_tokens_per_minute=optional("LLM_MAX_TOKENS_PER_MINUTE"),
        expected_output_tokens=int(env.get("LLM_EXPECTED_OUTPUT_TOKENS") or 4000),
        budget_dir=env.get("LLM_BUDGET_DIR") or None,
    )


def provider_name(env=None):
    env = os.environ if env is None else env
    return env.get("DAALE_LIVE_PROVIDER", "openrouter").strip().lower()


def model_by_kernel_from_env(env=None, live=True):
    """Default model plus any per-kernel overrides. Live runs require a default."""
    env = os.environ if env is None else env
    default_model = env.get("DAALE_DEFAULT_MODEL", "").strip()
    if live and not default_model:
        raise ValueError("DAALE_DEFAULT_MODEL must be set for live runs; no model is assumed.")
    models = {"default": default_model or "offline-fixture"}
    for kernel in ALL_KERNELS:
        override = env.get(f"DAALE_{kernel}_MODEL")
        if override:
            models[kernel] = override
    return models


def fallback_by_kernel_from_env(env=None):
    """Fallback model per kernel: DAALE_FALLBACK_MODEL for all, DAALE_<KERNEL>_FALLBACK_MODEL to override.

    A fallback is tried once, only after the primary model has failed in a way another model might not
    (provider errors, timeouts, an exhausted quota, truncation, unusable output).
    """
    env = os.environ if env is None else env
    fallbacks = {}
    default = env.get("DAALE_FALLBACK_MODEL", "").strip()
    if default:
        fallbacks["default"] = default
    for kernel in ALL_KERNELS:
        override = env.get(f"DAALE_{kernel}_FALLBACK_MODEL", "").strip()
        if override:
            fallbacks[kernel] = override
    return fallbacks


def build_live_client(env=None):
    """Return ``(client, native_json_schema)`` for the configured provider."""
    env = os.environ if env is None else env
    if env_bool(env, "DAALE_FORCE_IPV4"):
        # For a network whose IPv6 does not work: without this every new connection waits about
        # three minutes before falling back to IPv4 (see network.py).
        force_ipv4()
    provider = provider_name(env)

    if provider == "nvidia":
        # Direct NVIDIA NIM endpoint. No OpenRouter routing concepts apply: no
        # provider pinning, no native-json-schema response_format mode. The
        # endpoint was measured returning a bare 500 on ~40% of requests, hence
        # the higher default attempt count.
        client = NvidiaClient(
            api_key=env.get("NVIDIA_API_KEY"),
            timeout_seconds=int(env.get("NVIDIA_TIMEOUT_SECONDS", "180")),
            max_attempts=int(env.get("NVIDIA_MAX_ATTEMPTS", "6")),
        )
        return client, False

    if provider == "openrouter":
        native = env_bool(env, "OPENROUTER_NATIVE_JSON_SCHEMA")
        provider_by_purpose = {
            kernel.lower(): env[f"DAALE_{kernel}_PROVIDER"]
            for kernel in ALL_KERNELS
            if env.get(f"DAALE_{kernel}_PROVIDER")
        }
        client = OpenRouterClient(
            api_key=env.get("OPENROUTER_API_KEY"),
            provider_by_purpose=provider_by_purpose or None,
            native_json_schema=native,
            timeout_seconds=int(env.get("OPENROUTER_TIMEOUT_SECONDS", "180")),
            max_tokens=int(env.get("OPENROUTER_MAX_TOKENS", "4000")),
        )
        return client, native

    if provider == "generic":
        # Any chat-completions endpoint called directly (a Gemma key issued by
        # Google's Gemini API, vLLM, Ollama, Together, ...).
        native = env_bool(env, "LLM_NATIVE_JSON_SCHEMA")
        client = GenericApiClient(
            api_key=env.get("LLM_API_KEY"),
            base_url=env.get("LLM_BASE_URL"),
            native_json_schema=native,
            timeout_seconds=int(env.get("LLM_TIMEOUT_SECONDS", "500")),
            max_tokens=int(env.get("LLM_MAX_TOKENS", "16000")),
            max_tokens_by_purpose={
                kernel.lower(): env[f"LLM_MAX_TOKENS_{kernel}"]
                for kernel in ALL_KERNELS
                if env.get(f"LLM_MAX_TOKENS_{kernel}")
            } or None,
            max_tokens_limit=int(env.get("LLM_MAX_TOKENS_LIMIT", "32000")),
            pacers=pacers_from_env(env),
        )
        return client, native

    if provider == "aimlapi":
        native = env_bool(env, "AIMLAPI_NATIVE_JSON_SCHEMA")
        client = AimlApiClient(
            api_key=env.get("AIMLAPI_API_KEY"),
            native_json_schema=native,
            timeout_seconds=int(env.get("AIMLAPI_TIMEOUT_SECONDS", "180")),
            max_attempts=int(env.get("AIMLAPI_MAX_ATTEMPTS", "6")),
        )
        return client, native

    raise ValueError(
        f"DAALE_LIVE_PROVIDER must be one of {list(PROVIDERS)}, received: {provider!r}"
    )
