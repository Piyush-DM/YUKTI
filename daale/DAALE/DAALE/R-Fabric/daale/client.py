"""OpenRouter and offline fixture clients for bounded JSON completions."""

import json
import time
from copy import deepcopy
from dataclasses import dataclass

import requests

from .validation import DaaleValidationError, validate_schema


class DaaleModelError(RuntimeError):
    """Raised when a model call or model contract fails."""


@dataclass(frozen=True)
class CompletionRecord:
    purpose: str
    output: dict
    requested_model: str
    served_model: str
    request_id: str
    usage: dict


def _parse_json_content(content, purpose):
    if not isinstance(content, str) or not content.strip():
        raise DaaleModelError(
            f"{purpose} returned empty or non-text content"
        )

    raw = content.strip()

    if raw.startswith("```"):
        if "\n" not in raw:
            raise DaaleModelError(
                f"{purpose} returned an incomplete markdown fence"
            )

        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0].strip()

    try:
        parsed = json.loads(raw)

    except json.JSONDecodeError as error:
        preview = raw[:1200]

        raise DaaleModelError(
            f"{purpose} did not return valid JSON. "
            f"Output preview:\n{preview}"
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
    ):
        if not api_key:
            raise DaaleModelError(
                "OPENROUTER_API_KEY is required for live mode"
            )

        self.api_key = api_key
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
            "max_tokens": 4000,
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
            raise DaaleModelError(
                str(error)
            ) from error

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
            raise DaaleModelError(str(error)) from error

        return CompletionRecord(
            purpose=purpose,
            output=output,
            requested_model=model,
            served_model=body.get("model", "unknown"),
            request_id=body.get("id", "unknown"),
            usage=body.get("usage", {}),
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
            raise DaaleModelError(str(error)) from error

        return CompletionRecord(
            purpose=purpose,
            output=output,
            requested_model=model,
            served_model=body.get("model", "unknown"),
            request_id=body.get("id", "unknown"),
            usage=body.get("usage", {}),
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
        )
        return _post_json_with_retry(
            url=self.BASE_URL,
            headers=headers,
            payload=payload,
            timeout_seconds=self.timeout_seconds,
            max_attempts=self.max_attempts,
            service_name="NVIDIA",
        )


def _post_json_with_retry(
    url,
    headers,
    payload,
    timeout_seconds,
    max_attempts,
    service_name,
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
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=timeout_seconds,
            )
        except requests.RequestException as error:
            if attempt == max_attempts:
                raise DaaleModelError(
                    f"{service_name} request failed: {error}"
                ) from error
            time.sleep(min(2 ** attempt, 8))
            continue

        try:
            response_body = response.json()
        except ValueError:
            response_body = None

        embedded_error = None
        if isinstance(response_body, dict) and "error" in response_body:
            embedded_error = response_body["error"]

        if response.ok and embedded_error is None:
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
            retry_after = response.headers.get("Retry-After")
            try:
                delay = float(retry_after) if retry_after else 2 ** attempt
            except ValueError:
                delay = 2 ** attempt
            time.sleep(min(max(delay, 1), 10))
            continue

        raise DaaleModelError(
            f"{service_name} error {error_code} after {attempt} attempt(s): "
            f"{error_message}"
        )

    raise DaaleModelError(
        f"{service_name} request exhausted all retry attempts"
    )


class FixtureClient:
    """Deterministic client used by offline runs and tests."""

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