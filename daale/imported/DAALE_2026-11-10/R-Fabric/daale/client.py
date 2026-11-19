"""OpenRouter and offline fixture clients for bounded JSON completions."""

import json
import logging
import re
import threading
import time
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import requests

from .budget import DEFAULT_PATH, BudgetExhausted, RequestBudget
from .validation import DaaleValidationError, validate_schema


logger = logging.getLogger("daale.client")


class RequestPacer:
    """Keeps requests under per-minute caps on count and on tokens, across threads.

    Every HTTP attempt takes a slot before it is sent, retries included: a
    provider counts a retried request like any other, so a retry that skipped
    this would be exactly the request that tips a capped key over its limit.

    Tokens are reserved from an estimate before sending (the prompt, plus an
    allowance for the reply and any reasoning) and corrected to the provider's
    reported total afterwards. Waiting is logged, so a slow run is explained
    rather than mysterious.
    """

    def __init__(self, per_minute=None, budget=None, tokens_per_minute=None,
                 expected_output_tokens=4000, window_seconds=61.0,
                 clock=time.monotonic, sleep=time.sleep):
        if per_minute is not None and per_minute < 1:
            raise ValueError("requests per minute must be at least 1")
        if tokens_per_minute is not None and tokens_per_minute < 1:
            raise ValueError("tokens per minute must be at least 1")
        self.per_minute = per_minute
        self.tokens_per_minute = tokens_per_minute
        self.expected_output_tokens = expected_output_tokens
        self.budget = budget
        self.window = window_seconds
        self._clock = clock
        self._sleep = sleep
        self._entries = []  # [start time, tokens], oldest first
        self._lock = threading.Lock()

    def wait(self, estimated_tokens=0):
        """Block until a request of about ``estimated_tokens`` fits; return its handle."""
        # Refuse before waiting for a slot we would then be unable to use.
        if self.budget is not None:
            self.budget.check()
        if self.tokens_per_minute is not None and estimated_tokens > self.tokens_per_minute:
            raise BudgetExhausted(
                f"One request needs about {estimated_tokens} tokens (prompt plus the reply "
                f"allowance) but the per-minute token cap is {self.tokens_per_minute}, so it can "
                "never be sent. Use less material, a model with a higher cap, or lower "
                "LLM_EXPECTED_OUTPUT_TOKENS if the replies are short."
            )

        entry = None
        while self.per_minute is not None or self.tokens_per_minute is not None:
            with self._lock:
                now = self._clock()
                self._entries = [e for e in self._entries if now - e[0] < self.window]
                delay = 0.0
                reason = ""
                if self.per_minute is not None and len(self._entries) >= self.per_minute:
                    delay = self.window - (now - self._entries[0][0])
                    reason = f"request cap of {self.per_minute}/min"
                if self.tokens_per_minute is not None:
                    excess = sum(e[1] for e in self._entries) + estimated_tokens - self.tokens_per_minute
                    if excess > 0:
                        freed = 0
                        for earlier in self._entries:
                            freed += earlier[1]
                            if freed >= excess:
                                token_delay = self.window - (now - earlier[0])
                                if token_delay > delay:
                                    delay = token_delay
                                    reason = f"token cap of {self.tokens_per_minute}/min"
                                break
                if delay <= 0:
                    entry = [now, estimated_tokens]
                    self._entries.append(entry)
                    break
            logger.info("%s reached; waiting %.0fs for room", reason, delay)
            self._sleep(max(delay, 0.05))

        if self.budget is not None:
            self.budget.take()
        return entry

    def settle(self, entry, actual_tokens):
        """Replace a request's estimate with the tokens the provider reported."""
        if entry is not None and actual_tokens:
            with self._lock:
                entry[1] = int(actual_tokens)


class ModelPacers:
    """Request pacing and a daily budget, kept separately for each model.

    Providers meter each model on its own, so one shared counter would charge a
    Gemma request against a Gemini allowance. ``limits`` maps a model id to
    ``(requests_per_minute, requests_per_day, tokens_per_minute)``, any of which may
    be None; a model without an entry gets the defaults. No limit at all means no pacer.
    """

    def __init__(self, limits=None, default_per_minute=None, default_per_day=None,
                 default_tokens_per_minute=None, expected_output_tokens=4000, budget_dir=None):
        self.limits = limits or {}
        self.expected_output_tokens = expected_output_tokens
        self.default = (default_per_minute, default_per_day, default_tokens_per_minute)
        self.budget_dir = Path(budget_dir) if budget_dir else DEFAULT_PATH.parent
        self._pacers = {}
        self._lock = threading.Lock()

    def for_model(self, model):
        with self._lock:
            if model not in self._pacers:
                per_minute, per_day, tokens = (tuple(self.limits.get(model, self.default)) + (None,))[:3]
                if per_minute is None and per_day is None and tokens is None:
                    self._pacers[model] = None
                else:
                    safe = re.sub(r"[^A-Za-z0-9._-]", "_", model)
                    budget = (
                        RequestBudget(per_day, self.budget_dir / f"request_budget.{safe}.json")
                        if per_day else None
                    )
                    self._pacers[model] = RequestPacer(
                        per_minute, budget, tokens, self.expected_output_tokens
                    )
            return self._pacers[model]

    def remaining(self, model):
        pacer = self.for_model(model)
        return pacer.budget.remaining() if pacer is not None and pacer.budget else None

    def seconds_until_reset(self, model):
        pacer = self.for_model(model)
        return pacer.budget.seconds_until_reset() if pacer is not None and pacer.budget else 3600


class DaaleModelError(RuntimeError):
    """Raised when a model call or model contract fails.

    ``status_code`` is the provider's HTTP status when the failure came from
    one, so the pipeline can classify it without parsing message text.
    """

    def __init__(
        self, message, status_code=None, *, retry_after_seconds=None,
        request_id=None, usage=None, provider=None, attempts=None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.retry_after_seconds = retry_after_seconds
        self.request_id = request_id
        self.usage = usage or {}
        self.provider = provider
        self.attempts = attempts


def _schema_rejection(error, output):
    """The error for a reply that parsed as JSON but broke the schema, carrying that reply.

    The pipeline needs the rejected reply to show the model what was wrong with it. Without it a
    retry at temperature 0 repeats the same mistake: in the 2026-11-09 live run OUTSIDER failed
    twice with the same two findings missing ``target_id``.
    """
    rejection = DaaleModelError(str(error))
    rejection.output = output
    return rejection


@dataclass(frozen=True)
class CompletionRecord:
    purpose: str
    output: dict
    requested_model: str
    served_model: str
    request_id: str
    usage: dict
    attempts: int = 1


_REASONING_BLOCK = re.compile(r"<(thought|think)>.*?</\1>", re.DOTALL | re.IGNORECASE)
_REASONING_OPEN = re.compile(r"<(thought|think)>", re.IGNORECASE)


def _parse_json_content(content, purpose):
    if not isinstance(content, str) or not content.strip():
        raise DaaleModelError(
            f"{purpose} returned empty or non-text content"
        )

    # Some models (Gemma 4 on Google's endpoint, among others) put their
    # reasoning inline, ahead of the answer: "<thought>...</thought>{...}".
    # The reasoning is discarded; only what follows it is the answer.
    stripped = _REASONING_BLOCK.sub("", content)
    if _REASONING_OPEN.search(stripped):
        raise DaaleModelError(
            f"{purpose} reply was cut off while the model was still reasoning, "
            "before any answer. Raise the completion token limit "
            "(LLM_MAX_TOKENS / OPENROUTER_MAX_TOKENS)."
        )
    raw = stripped.strip()

    if raw.startswith("```"):
        if "\n" not in raw:
            raise DaaleModelError(
                f"{purpose} returned an incomplete markdown fence"
            )

        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0].strip()

    try:
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as error:
            # A complete object followed only by a stray closing code fence (the model
            # opened no fence but closed one) is the answer, not a malformed reply.
            # Anything else after the object still fails.
            if error.msg != "Extra data":
                raise
            parsed, end = json.JSONDecoder().raw_decode(raw)
            if raw[end:].strip(" \t\r\n`"):
                raise

    except json.JSONDecodeError as error:
        # Say where it broke. The first characters of a reply say nothing
        # about a failure in the middle or at the end of it.
        low = max(0, error.pos - 120)
        raise DaaleModelError(
            f"{purpose} did not return valid JSON ({error.msg} at line "
            f"{error.lineno} col {error.colno}, char {error.pos} of {len(raw)}). "
            f"Around the error: ...{raw[low:error.pos + 120]!r}..."
        ) from error

    if not isinstance(parsed, dict):
        raise DaaleModelError(
            f"{purpose} must return one JSON object"
        )

    return parsed


def _parse_tool_arguments(arguments, purpose):
    if isinstance(arguments, dict):
        parsed = arguments

    elif isinstance(arguments, str):
        try:
            parsed = json.loads(arguments)

        except json.JSONDecodeError as error:
            raise DaaleModelError(
                f"{purpose} returned invalid JSON inside "
                f"the forced tool arguments:\n"
                f"{arguments[:1200]}"
            ) from error

    else:
        raise DaaleModelError(
            f"{purpose} returned unsupported tool argument type: "
            f"{type(arguments).__name__}"
        )

    if not isinstance(parsed, dict):
        raise DaaleModelError(
            f"{purpose} tool arguments must be one JSON object"
        )

    return parsed


def _extract_forced_tool_output(
    message,
    purpose,
    expected_tool_name
):
    tool_calls = message.get("tool_calls") or []

    matching_calls = [
        tool_call
        for tool_call in tool_calls
        if (
            tool_call.get("function", {}).get("name")
            == expected_tool_name
        )
    ]

    if len(tool_calls) != 1 or len(matching_calls) != 1:
        text_preview = str(
            message.get("content") or ""
        )[:1200]

        raise DaaleModelError(
            f"{purpose} must call {expected_tool_name} "
            f"exactly once.\n"
            f"Received tool calls: {len(tool_calls)}\n"
            f"Text preview:\n{text_preview}"
        )

    function_call = matching_calls[0].get("function") or {}
    arguments = function_call.get("arguments")

    return _parse_tool_arguments(
        arguments,
        purpose
    )


class OpenRouterClient:
    def __init__(
        self,
        api_key,
        provider_by_purpose=None,
        native_json_schema=False,
        force_tool_output=True,
        timeout_seconds=180,
        max_attempts=3,
        max_tokens=4000,
    ):
        if not api_key:
            raise DaaleModelError(
                "OPENROUTER_API_KEY is required for live mode"
            )

        self.api_key = api_key
        self.max_tokens = max_tokens
        self.provider_by_purpose = (
            provider_by_purpose or {}
        )
        self.native_json_schema = native_json_schema
        self.force_tool_output = force_tool_output
        self.timeout_seconds = timeout_seconds
        self.max_attempts = max_attempts

    def complete_json(
        self,
        purpose,
        model,
        messages,
        schema
    ):
        payload = {
            "model": model,
            "temperature": 0,
            "max_tokens": self.max_tokens,
            "messages": messages,
        }

        provider = {
            "allow_fallbacks": False
        }

        provider_only = self.provider_by_purpose.get(
            purpose
        )

        if provider_only:
            provider["only"] = [
                provider_only
            ]

        tool_name = None

        if self.native_json_schema:
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": f"daale_{purpose}_output",
                    "strict": True,
                    "schema": schema,
                },
            }

            provider["require_parameters"] = True

        elif self.force_tool_output:
            tool_name = f"submit_daale_{purpose}"

            tool_schema = deepcopy(schema)

            # OpenRouter tool validation uses JSON Schema
            # Draft 7, so the Draft 2020 declaration is removed.
            tool_schema.pop("$schema", None)

            payload["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "description": (
                            "Submit the complete structured "
                            f"DAALE {purpose} output. "
                            "Call this function exactly once."
                        ),
                        "parameters": tool_schema,
                    },
                }
            ]

            payload["tool_choice"] = {
                "type": "function",
                "function": {
                    "name": tool_name
                },
            }

            provider["require_parameters"] = True

        payload["provider"] = provider

        response = self._post_with_retry(
            payload
        )

        try:
            body = response.json()

            message = body[
                "choices"
            ][0][
                "message"
            ]

        except (
            ValueError,
            KeyError,
            IndexError,
            TypeError
        ) as error:
            raise DaaleModelError(
                f"Malformed OpenRouter response "
                f"for {purpose}: "
                f"{response.text[:1200]}"
            ) from error

        if tool_name:
            output = _extract_forced_tool_output(
                message=message,
                purpose=purpose,
                expected_tool_name=tool_name,
            )

        else:
            output = _parse_json_content(
                message.get("content"),
                purpose,
            )

        try:
            validate_schema(
                output,
                schema,
                f"{purpose} model output",
            )

        except DaaleValidationError as error:
            raise _schema_rejection(error, output) from error

        return CompletionRecord(
            purpose=purpose,
            output=output,
            requested_model=model,
            served_model=body.get(
                "model",
                "unknown"
            ),
            request_id=body.get(
                "id",
                "unknown"
            ),
            usage=body.get(
                "usage",
                {}
            ),
            attempts=getattr(response, "_daale_attempts", 1),
        )

    def _post_with_retry(
        self,
        payload
    ):
        headers = {
            "Authorization": (
                f"Bearer {self.api_key}"
            ),
            "Content-Type": (
                "application/json"
            ),
            "X-OpenRouter-Title": (
                "YUKTI DAALE v0.1"
            ),
        }
        return _post_json_with_retry(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            payload=payload,
            timeout_seconds=self.timeout_seconds,
            max_attempts=self.max_attempts,
            service_name="OpenRouter",
            provider_id=getattr(self, "provider_id", "openrouter"),
        )


class NvidiaClient:
    """Direct NVIDIA NIM client (``integrate.api.nvidia.com``).

    Bypasses OpenRouter entirely -- no ``provider`` routing block, no
    OpenRouter-specific ``response_format`` structured-output mode, because
    neither concept exists on NVIDIA's own OpenAI-compatible endpoint.

    Deliberately does **not** use forced tool-calling. Measured directly
    against this endpoint (see the diagnostic session that added this
    client): any JSON Schema with a top-level array-of-plain-strings
    property -- which every DAALE output schema has (``uncertainties``,
    ``assumptions``) -- makes this model's constrained-decoding path for
    ``tool_choice`` return a bare 500, reproducibly, regardless of prompt.
    Arrays of objects and enums are unaffected; only bare string arrays are.
    Reshaping DAALE's actual output schemas to dodge one provider's decoding
    bug was rejected as the fix -- that changes the CHOIR-facing contract
    every other client (including the offline fixtures) is validated
    against, for a defect that belongs to this one backend.

    Instead this client uses the plain-prompted-JSON path ``prompts.py``
    already builds whenever ``native_schema=False``: the full JSON Schema is
    embedded as text instructions in the prompt, and the model's freeform
    reply is parsed and then validated locally with the same
    ``validate_schema`` call every other client uses. Confirmed working
    end-to-end against the real analyst prompt during diagnosis.
    """

    BASE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

    def __init__(
        self,
        api_key,
        timeout_seconds=180,
        max_attempts=3,
    ):
        if not api_key:
            raise DaaleModelError(
                "NVIDIA_API_KEY is required for --live with "
                "DAALE_LIVE_PROVIDER=nvidia"
            )

        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.max_attempts = max_attempts

    def complete_json(
        self,
        purpose,
        model,
        messages,
        schema
    ):
        payload = {
            "model": model,
            "temperature": 0,
            # Plain-prompted JSON (no forced tool-calling, see the class
            # docstring) means the model must write out the whole object as
            # text; a kernel generating many findings can run past 4000
            # tokens and get truncated mid-object. Observed directly:
            # EXPANSIONIST truncated at 4000 mid-response. This model
            # supports up to 65536 completion tokens; 8000 is headroom, not
            # an attempt to raise a ceiling that was actually load-bearing.
            "max_tokens": 8000,
            "messages": messages,
        }

        response = self._post_with_retry(payload)

        try:
            body = response.json()
            message = body["choices"][0]["message"]
        except (ValueError, KeyError, IndexError, TypeError) as error:
            raise DaaleModelError(
                f"Malformed NVIDIA response for {purpose}: "
                f"{response.text[:1200]}"
            ) from error

        output = _parse_json_content(message.get("content"), purpose)

        try:
            validate_schema(output, schema, f"{purpose} model output")
        except DaaleValidationError as error:
            raise _schema_rejection(error, output) from error

        return CompletionRecord(
            purpose=purpose,
            output=output,
            requested_model=model,
            served_model=body.get("model", "unknown"),
            request_id=body.get("id", "unknown"),
            usage=body.get("usage", {}),
            attempts=getattr(response, "_daale_attempts", 1),
        )

    def _post_with_retry(self, payload):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        return _post_json_with_retry(
            url=self.BASE_URL,
            headers=headers,
            payload=payload,
            timeout_seconds=self.timeout_seconds,
            max_attempts=self.max_attempts,
            service_name="NVIDIA",
            provider_id=getattr(self, "provider_id", "nvidia"),
        )


class AimlApiClient:
    """Direct AIML API client (``api.aimlapi.com``).

    Uses the OpenAI-compatible endpoint directly, bypassing OpenRouter.
    Supports native JSON schema via ``response_format`` if the model
    supports it, otherwise falls back to plain-prompted JSON.
    """

    BASE_URL = "https://api.aimlapi.com/v1/chat/completions"

    def __init__(
        self,
        api_key,
        native_json_schema=False,
        timeout_seconds=180,
        max_attempts=3,
    ):
        if not api_key:
            raise DaaleModelError(
                "AIMLAPI_API_KEY is required for --live with "
                "DAALE_LIVE_PROVIDER=aimlapi"
            )

        self.api_key = api_key
        self.native_json_schema = native_json_schema
        self.timeout_seconds = timeout_seconds
        self.max_attempts = max_attempts

    def complete_json(
        self,
        purpose,
        model,
        messages,
        schema
    ):
        payload = {
            "model": model,
            "temperature": 0,
            "max_tokens": 8000,
            "messages": messages,
        }

        if self.native_json_schema:
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": f"daale_{purpose}_output",
                    "strict": True,
                    "schema": schema,
                },
            }

        response = self._post_with_retry(payload)

        try:
            body = response.json()
            message = body["choices"][0]["message"]
        except (ValueError, KeyError, IndexError, TypeError) as error:
            raise DaaleModelError(
                f"Malformed AIML API response for {purpose}: "
                f"{response.text[:1200]}"
            ) from error

        if self.native_json_schema:
            # With native JSON schema, the content is the parsed JSON
            try:
                output = json.loads(message.get("content", "{}"))
            except json.JSONDecodeError:
                output = {}
        else:
            output = _parse_json_content(message.get("content"), purpose)

        try:
            validate_schema(output, schema, f"{purpose} model output")
        except DaaleValidationError as error:
            raise _schema_rejection(error, output) from error

        return CompletionRecord(
            purpose=purpose,
            output=output,
            requested_model=model,
            served_model=body.get("model", "unknown"),
            request_id=body.get("id", "unknown"),
            usage=body.get("usage", {}),
            attempts=getattr(response, "_daale_attempts", 1),
        )

    def _post_with_retry(self, payload):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        return _post_json_with_retry(
            url=self.BASE_URL,
            headers=headers,
            payload=payload,
            timeout_seconds=self.timeout_seconds,
            max_attempts=self.max_attempts,
            service_name="AIML API",
            provider_id=getattr(self, "provider_id", "aimlapi"),
        )
        return _post_json_with_retry(
            url=self.BASE_URL,
            headers=headers,
            payload=payload,
            timeout_seconds=self.timeout_seconds,
            max_attempts=self.max_attempts,
            service_name="NVIDIA",
            provider_id=getattr(self, "provider_id", "nvidia"),
        )


class GenericApiClient:
    """Any OpenAI-compatible ``/chat/completions`` endpoint, direct to the provider.

    This is the client for a Gemma key that is not an OpenRouter key: Google's
    Gemini API serves Gemma through an OpenAI-compatible endpoint, and vLLM,
    Ollama, Together and others do the same. Nothing here is specific to one
    vendor. The base URL and key come from the environment; the model id is
    whatever that provider calls the model.

    Like the NVIDIA client it asks for JSON in the prompt (``prompts.py`` embeds
    the schema when ``native_schema`` is false) and validates the reply locally
    with the same ``validate_schema`` every other client uses, because forced
    tool-calling and strict ``json_schema`` support differ by provider and
    model. Set ``native_json_schema`` only for an endpoint confirmed to honour
    it.

    The key is only ever sent over HTTPS, or to a loopback address.
    """

    _LOOPBACK = {"localhost", "127.0.0.1", "::1"}

    def __init__(
        self,
        api_key,
        base_url,
        native_json_schema=False,
        timeout_seconds=500,
        max_attempts=3,
        max_tokens=16000,
        pacers=None,
        max_tokens_by_purpose=None,
        max_tokens_limit=32000,
    ):
        parsed = urlparse(base_url or "")
        local = parsed.hostname in self._LOOPBACK
        if not parsed.scheme or not parsed.hostname:
            raise DaaleModelError(
                "LLM_BASE_URL is required, e.g. https://host/v1"
            )
        if parsed.scheme != "https" and not local:
            raise DaaleModelError(
                "Refusing to send an API key over plain http to a non-local host"
            )
        if not api_key and not local:
            raise DaaleModelError(
                "LLM_API_KEY is required for a non-local endpoint"
            )

        self.url = base_url.rstrip("/") + "/chat/completions"
        self.pacers = pacers
        self.api_key = api_key
        self.native_json_schema = native_json_schema
        self.timeout_seconds = timeout_seconds
        self.max_attempts = max_attempts
        self.max_tokens = max_tokens
        # A kernel whose reply is long can have a higher ceiling than the rest (keys are the
        # purpose, e.g. "analyst"). Added 2026-11-17: ANALYST was cut off at 16,000 on a case
        # with a 68-relation matrix while every other kernel finished well inside it.
        self.max_tokens_by_purpose = {k.lower(): int(v) for k, v in (max_tokens_by_purpose or {}).items()}
        self.max_tokens_limit = int(max_tokens_limit)

    def max_tokens_for(self, purpose):
        return self.max_tokens_by_purpose.get(purpose, self.max_tokens)

    def escalated_max_tokens(self, purpose):
        """The ceiling for a retry after a truncated reply: double the usual one, up to ``max_tokens_limit``.

        Added 2026-11-17. A reply cut off at the ceiling gets the same answer again from the same
        prompt, so a retry that changes nothing but a nudge fails the same way (ANALYST, then
        CONTRARIAN and FIRST_PRINCIPLES, on the stress case). The limit is a safety bound: a value
        above what the model accepts is refused by the provider, so keep it at or below the model's
        real maximum (``LLM_MAX_TOKENS_LIMIT``). Returns the usual ceiling when there is no headroom.
        """
        usual = self.max_tokens_for(purpose)
        return max(usual, min(usual * 2, self.max_tokens_limit))

    def requests_remaining(self, model=None):
        """Requests left in today's budget for ``model``, or None when it has no daily limit."""
        return self.pacers.remaining(model) if self.pacers is not None else None

    def budget_reset_seconds(self, model=None):
        return self.pacers.seconds_until_reset(model) if self.pacers is not None else 3600

    def complete_json(
        self,
        purpose,
        model,
        messages,
        schema,
        max_tokens=None,
    ):
        payload = {
            "model": model,
            "temperature": 0,
            "max_tokens": max_tokens or self.max_tokens_for(purpose),
            "messages": messages,
        }

        if self.native_json_schema:
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": f"daale_{purpose}_output",
                    "strict": True,
                    "schema": schema,
                },
            }

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        response = _post_json_with_retry(
            url=self.url,
            headers=headers,
            payload=payload,
            timeout_seconds=self.timeout_seconds,
            max_attempts=self.max_attempts,
            service_name="OpenAI-compatible endpoint",
            provider_id=getattr(self, "provider_id", "generic"),
            pacer=self.pacers.for_model(model) if self.pacers is not None else None,
        )

        try:
            body = response.json()
            message = body["choices"][0]["message"]
            if body["choices"][0].get("finish_reason") == "length":
                truncated = DaaleModelError(
                    f"{purpose} reply was cut off at the completion token limit "
                    f"({payload['max_tokens']}, which includes any reasoning). Raise LLM_MAX_TOKENS"
                    f" (or LLM_MAX_TOKENS_{purpose.upper()} for this kernel only)."
                )
                truncated.truncated = True
                raise truncated

            output = _parse_json_content(message.get("content"), purpose)
            try:
                validate_schema(output, schema, f"{purpose} model output")
            except DaaleValidationError as error:
                raise _schema_rejection(error, output) from error
        except Exception as error:  # provider reply exists; attach its provenance to every failure
            if not hasattr(error, "provider") or error.provider is None:
                error.provider = getattr(self, "provider_id", "generic")
            error.attempts = getattr(response, "_daale_attempts", 1)
            error.served_model = body.get("model", "unknown") if "body" in locals() else "unknown"
            error.request_id = body.get("id") if "body" in locals() else None
            error.usage = body.get("usage", {}) if "body" in locals() else {}
            error.max_tokens = payload["max_tokens"]
            if getattr(error, "retry_after_seconds", None) is None:
                error.retry_after_seconds = _server_retry_delay(response)
            if isinstance(error, (ValueError, KeyError, IndexError, TypeError)):
                wrapped = DaaleModelError(
                    f"Malformed response for {purpose}: {response.text[:1200]}"
                )
                for name in (
                    "provider", "attempts", "served_model", "request_id", "usage",
                    "max_tokens", "retry_after_seconds",
                ):
                    setattr(wrapped, name, getattr(error, name, None))
                raise wrapped from error
            raise

        return CompletionRecord(
            purpose=purpose,
            output=output,
            requested_model=model,
            served_model=body.get("model", "unknown"),
            request_id=body.get("id", "unknown"),
            usage=body.get("usage", {}),
            attempts=getattr(response, "_daale_attempts", 1),
        )


def _estimate_tokens(payload, expected_output):
    """Prompt tokens (about 3.5 characters each) plus an allowance for the reply."""
    characters = sum(len(message.get("content") or "") for message in payload.get("messages", []))
    return int(characters / 3.5) + expected_output


# The longest wait honoured when a provider says how long to hold off. A per-minute
# window is about 60 s, so waiting less than that only spends another request (and a
# slot of the daily budget) on a 429 that is certain to repeat.
MAX_SERVER_RETRY_WAIT_SECONDS = 65
# A reply may take the whole timeout; merely connecting should not.
CONNECT_TIMEOUT_SECONDS = 30


def _server_retry_delay(response):
    """Seconds the provider asks us to wait, or None when it does not say.

    Reads the ``Retry-After`` header, or the ``retryDelay`` that Google puts in a
    429's RetryInfo (``"retryDelay": "23s"``), which arrives in the body, not a header.
    """
    header = (getattr(response, "headers", None) or {}).get("Retry-After")
    if header:
        try:
            return float(header)
        except (TypeError, ValueError):
            pass
    body = str(getattr(response, "text", "") or "")
    match = re.search(r'"retryDelay"\s*:\s*"([0-9]+(?:\.[0-9]+)?)s"', body)
    return float(match.group(1)) if match else None


def _post_json_with_retry(
    url,
    headers,
    payload,
    timeout_seconds,
    max_attempts,
    service_name,
    pacer=None,
    provider_id=None,
):
    """Shared retry loop for any OpenAI-compatible chat-completions endpoint.

    Retries connection failures and 429/5xx responses with backoff that
    respects ``Retry-After`` when the server sends one. Also detects the
    OpenRouter quirk of an HTTP 200 whose JSON body embeds an upstream
    provider error -- harmless to check on a direct provider endpoint too,
    since a body without an ``"error"`` key never trips it.
    """
    retryable_codes = {429, 500, 502, 503, 504, 524, 529}

    for attempt in range(1, max_attempts + 1):
        handle = pacer.wait(_estimate_tokens(payload, pacer.expected_output_tokens)) if pacer else None
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=(min(CONNECT_TIMEOUT_SECONDS, timeout_seconds), timeout_seconds),
            )
        except requests.RequestException as error:
            # A reply that took the whole read timeout is not worth asking for again at this
            # layer. The kernel-level policy already retries a timeout, and three more waits of
            # the full timeout here made one stalled call cost three times as long (about 33
            # minutes at 500 s). Connecting errors are still retried.
            if isinstance(error, requests.exceptions.ReadTimeout):
                logger.warning(
                    "%s request timed out after %ss; not retrying at this layer",
                    service_name, timeout_seconds,
                )
                raise DaaleModelError(
                    f"{service_name} request failed: {error}",
                    provider=provider_id or service_name,
                    attempts=attempt,
                ) from error
            if attempt == max_attempts:
                logger.warning(
                    "%s request failed (%s), no attempts left", service_name, type(error).__name__
                )
                raise DaaleModelError(
                    f"{service_name} request failed: {error}",
                    provider=provider_id or service_name,
                    attempts=attempt,
                ) from error
            wait = min(2 ** attempt, 8)
            logger.warning(
                "%s request failed (%s); attempt %d/%d, retrying in %ds",
                service_name, type(error).__name__, attempt, max_attempts, wait,
            )
            time.sleep(wait)
            continue

        try:
            response_body = response.json()
        except ValueError:
            response_body = None

        embedded_error = None
        if isinstance(response_body, dict) and "error" in response_body:
            embedded_error = response_body["error"]

        if response.ok and embedded_error is None:
            if pacer is not None and isinstance(response_body, dict):
                pacer.settle(handle, (response_body.get("usage") or {}).get("total_tokens"))
            response._daale_attempts = attempt
            response._daale_provider = provider_id or service_name
            return response

        error_code = response.status_code
        error_message = response.text[:2000]

        if isinstance(embedded_error, dict):
            raw_code = embedded_error.get("code", error_code)
            try:
                error_code = int(raw_code)
            except (TypeError, ValueError):
                error_code = response.status_code
            error_message = str(
                embedded_error.get("message") or error_message
            )[:2000]
        elif embedded_error is not None:
            error_message = str(embedded_error)[:2000]

        retryable = error_code in retryable_codes or error_code >= 500

        if retryable and attempt < max_attempts:
            hint = _server_retry_delay(response)
            if hint is not None:
                wait = min(max(hint, 1), MAX_SERVER_RETRY_WAIT_SECONDS)
            else:
                wait = min(2 ** attempt, 10)
            logger.warning(
                "%s returned %s; attempt %d/%d, provider asked for %s, waiting %.0fs",
                service_name, error_code, attempt, max_attempts,
                f"{hint:.0f}s" if hint is not None else "no delay", wait,
            )
            time.sleep(wait)
            continue

        logger.warning(
            "%s error %s after %d attempt(s): %s",
            service_name, error_code, attempt, error_message[:300].replace("\n", " "),
        )
        headers = getattr(response, "headers", {}) or {}
        request_id = (
            headers.get("x-request-id")
            or headers.get("request-id")
            or headers.get("x-goog-request-id")
        )
        raise DaaleModelError(
            f"{service_name} error {error_code} after {attempt} attempt(s): "
            f"{error_message}",
            status_code=error_code,
            retry_after_seconds=_server_retry_delay(response),
            request_id=request_id,
            usage=(response_body.get("usage") if isinstance(response_body, dict) else None),
            provider=provider_id or service_name,
            attempts=attempt,
        )

    raise DaaleModelError(
        f"{service_name} request exhausted all retry attempts",
        provider=provider_id or service_name,
        attempts=max_attempts,
    )


class FixtureClient:
    """Deterministic client used by offline runs and tests."""

    # The pipeline asks this, rather than probing for ``outputs``, to decide
    # whether a missing adversary fixture means "skip" (fixture client only).
    is_fixture = True

    def __init__(
        self,
        outputs
    ):
        self.outputs = deepcopy(
            outputs
        )

    def complete_json(
        self,
        purpose,
        model,
        messages,
        schema
    ):
        if purpose not in self.outputs:
            raise DaaleModelError(
                "No offline fixture configured "
                f"for {purpose}"
            )

        output = deepcopy(
            self.outputs[purpose]
        )

        validate_schema(
            output,
            schema,
            f"{purpose} fixture",
        )

        return CompletionRecord(
            purpose=purpose,
            output=output,
            requested_model=model,
            served_model=(
                f"offline-fixture/{purpose}"
            ),
            request_id=(
                f"offline-{purpose}"
            ),
            usage={
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "cost": 0,
            },
        )
