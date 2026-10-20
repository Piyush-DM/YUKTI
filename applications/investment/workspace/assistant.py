"""The optional language model. It proposes and it phrases. It never decides.

This is the seam `DECISION-008` describes and `intake.propose_from_assistant`
declares. It is **off unless a key is configured**, and everything in the
workspace works without it — the deterministic reader in `intake.py` and the
record projection in `explain.py` are the product, not the fallback.

What the model is allowed to do
-------------------------------

1. **Read prose into proposals.** Better than the keyword reader at messy
   sentences. Its output is still a `Proposal`: a suggestion carrying the span
   it came from, which a person must accept, edit or reject before it is
   material. Identical governance to the deterministic path.

2. **Phrase an answer that `explain.py` already computed.** The deterministic
   answer is produced *first* and handed to the model as the thing to convey.
   The model rewrites it conversationally. It is not asked what the judgment
   means, because the record already says.

What it is not allowed to do, and how that is enforced rather than requested
---------------------------------------------------------------------------

- **It cannot invent a passage.** Every proposed quote must be a literal
  substring of the text that was pasted. One that is not is dropped, not
  trusted — so a fabricated citation cannot reach the confirm step.
- **It cannot invent a figure.** Every number in a phrased answer must already
  appear in the record or in the deterministic answer. If any does not, the
  deterministic answer is returned instead and the substitution is reported.
- **It cannot commit anything.** No function here writes to the case store.
  Accepting a proposal and recording a decision stay human actions, and the
  routes that perform them are not reachable from this module.

That ordering — compute, then phrase, then verify — is what keeps commitment E9
true with a model in the loop. The explanation is still a projection of the
record; the model only changes its wording, and is checked afterwards.

Configuration (yours to set; this module never asks for a key)
--------------------------------------------------------------

    ANTHROPIC_API_KEY=...            required to turn any of this on
    ANTHROPIC_BASE_URL=...           optional, for a compatible endpoint
    YUKTI_ASSIST_MODEL=...           optional, default claude-fable-5-1
    YUKTI_ASSIST=off                 optional kill switch

Put them in `.env` at the repository root. It is gitignored. Check the wiring
with `python yukti.py --check-assist`, which makes one small call and reports
what happened.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any

from applications.investment.workspace.cases import Case, Source
from applications.investment.workspace.diligence import FIGURE_STATUSES, SCHEDULE
from applications.investment.workspace.intake import Proposal, Span

# Claude Fable 5.1. Named because the operator asked for it; overridable.
DEFAULT_MODEL = "claude-fable-5-1"

# Fable 5.1 can decline a request outright (`stop_reason: "refusal"`). Server
# side fallback re-runs the same request on this model inside the same call, so
# a refusal on a diligence memo degrades to a working answer rather than an
# error. Opted into by default, per Anthropic's guidance for this model.
FALLBACK_MODEL = "claude-opus-4-8"
FALLBACK_BETA = "server-side-fallback-2026-06-01"

_STATUS_KEYS = tuple(entry.key for entry in FIGURE_STATUSES)
_METRICS = {item.metric: item for item in SCHEDULE}

_NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")


class AssistantUnavailable(RuntimeError):
    """No model is configured, reachable, or willing. Callers fall back."""


@dataclass(frozen=True)
class PhrasedAnswer:
    """A conversational answer, and whether the model actually produced it."""

    text: str
    model_used: bool
    note: str = ""


def enabled() -> bool:
    """True when a key is configured and the kill switch is not set."""
    if os.environ.get("YUKTI_ASSIST", "").strip().lower() in {"off", "0", "false"}:
        return False
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def status() -> dict[str, Any]:
    """What is configured, for the UI and the doctor. Never returns a secret."""
    try:
        import anthropic  # noqa: F401

        sdk = True
    except ImportError:
        sdk = False
    return {
        "enabled": enabled() and sdk,
        "sdk_installed": sdk,
        "key_configured": bool(os.environ.get("ANTHROPIC_API_KEY")),
        "model": os.environ.get("YUKTI_ASSIST_MODEL", DEFAULT_MODEL),
        "base_url": _base_url() or "(Anthropic default)",
    }


def _client() -> Any:
    """Build the SDK client, or explain precisely what is missing."""
    if os.environ.get("YUKTI_ASSIST", "").strip().lower() in {"off", "0", "false"}:
        raise AssistantUnavailable("YUKTI_ASSIST is off.")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise AssistantUnavailable(
            "No ANTHROPIC_API_KEY. Put one in .env at the repository root."
        )
    try:
        import anthropic
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise AssistantUnavailable(
            "The anthropic SDK is not installed. `pip install anthropic`."
        ) from exc

    # Passed explicitly rather than left to the SDK's own ANTHROPIC_BASE_URL
    # lookup. `.env` does not override a variable already set in the shell, so a
    # workspace pointed at a gateway would silently keep calling whatever
    # ANTHROPIC_BASE_URL some other tool had exported. The YUKTI-namespaced name
    # wins, and nothing else in an environment sets it.
    base_url = _base_url()
    if base_url:
        return anthropic.Anthropic(base_url=base_url)
    return anthropic.Anthropic()


def _base_url() -> str:
    """Where the Messages API lives. Empty means Anthropic's own endpoint."""
    return (
        os.environ.get("YUKTI_ASSIST_BASE_URL", "")
        or os.environ.get("ANTHROPIC_BASE_URL", "")
    ).strip()


def _model() -> str:
    return os.environ.get("YUKTI_ASSIST_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL


def _call(system: str, user: str, schema: dict[str, Any] | None, effort: str) -> str:
    """One request. Returns the response text, or raises AssistantUnavailable.

    Fable 5.1 specifics, which are not the same as the Opus family:
    thinking is always on so the parameter is omitted entirely; sampling
    parameters are rejected; and forced tool choice is rejected, so structured
    output is requested through ``output_config.format`` rather than by forcing
    a tool call.
    """
    client = _client()
    output_config: dict[str, Any] = {"effort": effort}
    if schema is not None:
        output_config["format"] = {
            "type": "json_schema",
            "schema": schema,
        }

    request: dict[str, Any] = {
        "model": _model(),
        "max_tokens": 16000,
        "system": system,
        "messages": [{"role": "user", "content": user}],
        "output_config": output_config,
    }

    try:
        import anthropic
    except ImportError as exc:  # pragma: no cover
        raise AssistantUnavailable("The anthropic SDK is not installed.") from exc

    try:
        try:
            response = client.beta.messages.create(
                betas=[FALLBACK_BETA],
                fallbacks=[{"model": FALLBACK_MODEL}],
                **request,
            )
        except (TypeError, anthropic.BadRequestError, anthropic.NotFoundError):
            # An SDK or an endpoint that does not know the refusal-fallback
            # parameter. A gateway proxying the Messages API typically does not,
            # and rejects the request rather than ignoring the field. Losing the
            # safety net is acceptable; losing the feature over it is not.
            response = client.messages.create(**request)
    except anthropic.AuthenticationError as exc:
        raise AssistantUnavailable(f"The key was rejected: {exc}") from exc
    except anthropic.NotFoundError as exc:
        raise AssistantUnavailable(
            f"Model {_model()!r} is not available: {exc}"
        ) from exc
    except anthropic.BadRequestError as exc:
        raise AssistantUnavailable(f"The request was rejected: {exc}") from exc
    except anthropic.RateLimitError as exc:
        raise AssistantUnavailable(f"Rate limited: {exc}") from exc
    except anthropic.APIConnectionError as exc:
        raise AssistantUnavailable(f"Could not reach the API: {exc}") from exc
    except anthropic.APIStatusError as exc:
        raise AssistantUnavailable(f"API error {exc.status_code}: {exc}") from exc

    if getattr(response, "stop_reason", None) == "refusal":
        details = getattr(response, "stop_details", None)
        category = getattr(details, "category", None) or "unspecified"
        raise AssistantUnavailable(f"The model declined ({category}).")

    parts = [block.text for block in response.content if block.type == "text"]
    text = "".join(parts).strip()
    if not text:
        raise AssistantUnavailable("The model returned nothing.")
    return text


# --------------------------------------------------------------- proposals


_PROPOSAL_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["figures"],
    "properties": {
        "figures": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["metric", "value", "status", "source_label", "quote"],
                "properties": {
                    "metric": {"type": "string", "enum": sorted(_METRICS)},
                    "value": {"type": "string"},
                    "status": {"type": "string", "enum": list(_STATUS_KEYS)},
                    "source_label": {"type": "string"},
                    "quote": {"type": "string"},
                },
            },
        }
    },
}

_PROPOSE_SYSTEM = """\
You read investment diligence prose and propose figures for a fixed schedule. \
You are a reading aid, not an analyst.

Rules, all of which are checked after you answer:

- Propose a metric only if the text states it. Never infer, estimate, convert \
between different things, or fill a gap. A metric the text does not establish \
must be absent from your output; a blank is recorded as a gap and reported, and \
that is the correct outcome.
- `quote` must be copied verbatim from the text, character for character. Any \
quote that is not a literal substring of the text is discarded and your \
proposal with it.
- `value` is digits only for USD and count metrics, with no currency symbol, \
separators, or scale suffix: write 18000000, not $18M. For percentages write \
the number alone: 62, not 62%. For text metrics write the single word the text \
uses.
- `source_label` must be one of the registered labels given to you, or an empty \
string if the sentence does not attribute the figure to one. Do not invent a \
label.
- `status` reflects how the text presents the figure, not how good it sounds.

You propose. A person confirms every figure before any of it is recorded."""


def propose(text: str, sources: tuple[Source, ...] = ()) -> tuple[Proposal, ...]:
    """Ask the model to read prose into proposals. Raises if unavailable.

    Every proposal that survives is one whose quote was found verbatim in the
    supplied text, whose metric is on the schedule, and whose source is either
    registered or blank. The rest are dropped without comment: a reading that
    cannot be located in the text is not a reading.
    """
    register = (
        "\n".join(
            f"- {source.label}: {source.origin} ({source.kind})" for source in sources
        )
        or "(the register is empty; leave source_label empty)"
    )
    schedule = "\n".join(
        f"- {item.metric} ({item.unit}) — {item.label}: {item.guidance}"
        for item in SCHEDULE
    )
    user = (
        f"SCHEDULE (the only metrics you may propose):\n{schedule}\n\n"
        f"REGISTERED SOURCES:\n{register}\n\n"
        f"TEXT:\n{text}"
    )

    raw = _call(_PROPOSE_SYSTEM, user, _PROPOSAL_SCHEMA, effort="medium")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AssistantUnavailable(f"The model returned malformed JSON: {exc}") from exc

    known = {source.label for source in sources}
    proposals: list[Proposal] = []
    seen: set[str] = set()

    for entry in payload.get("figures", []):
        metric = str(entry.get("metric", ""))
        quote = str(entry.get("quote", ""))
        item = _METRICS.get(metric)
        if item is None or metric in seen:
            continue

        # The anti-fabrication check. A quote the model composed rather than
        # copied cannot be located, and is therefore not evidence of anything.
        start = text.find(quote)
        if not quote or start == -1:
            continue

        label = str(entry.get("source_label", ""))
        if label and label not in known:
            label = ""
        status = str(entry.get("status", ""))
        if status not in _STATUS_KEYS:
            status = "unknown"

        proposals.append(
            Proposal(
                metric=metric,
                label=item.label,
                unit=item.unit,
                value=str(entry.get("value", "")).strip(),
                status=status,
                source_label=label,
                span=Span(start=start, end=start + len(quote), quote=quote),
                basis=f"read by {_model()}; quote located in the text",
            )
        )
        seen.add(metric)

    order = {item.metric: index for index, item in enumerate(SCHEDULE)}
    return tuple(sorted(proposals, key=lambda item: order.get(item.metric, 99)))


# ----------------------------------------------------------------- phrasing


_PHRASE_SYSTEM = """\
You are the voice of YUKTI, an institutional reasoning system for investment \
committees. You are answering a question about one case.

You are given the answer already, computed from the case's reasoning record. \
Your job is to say it well — conversationally, in continuous prose, at most a \
short paragraph or a tight list.

Hard constraints, checked after you answer:

- Every figure, band, count, and name you write must already appear in the \
computed answer or the record extract. Introduce no number of your own.
- Do not soften, hedge, upgrade or reinterpret the finding. If the computed \
answer says confidence is Low and the binding constraint is Market, so does \
yours.
- Do not offer investment advice, a view on the company, or a recommendation \
the record did not reach. You are explaining a record, not forming a judgment.
- If the computed answer says the question is outside what the record holds, \
say that plainly and stop.

No preamble. No "great question". Answer."""


def _numbers(text: str) -> set[str]:
    return {match.group(0).replace(",", "") for match in _NUMBER.finditer(text)}


def phrase(
    question: str,
    case: Case,
    grounded_text: str,
    record_extract: str,
) -> PhrasedAnswer:
    """Rephrase a computed answer conversationally, then verify it invented nothing.

    Returns the deterministic answer unchanged if the model is unavailable, or
    if it introduced a figure that is in neither the computed answer nor the
    record. Silence about a substitution would make the guard pointless, so the
    reason is carried back on ``note``.
    """
    user = (
        f"CASE: {case.title}\n\n"
        f"QUESTION: {question}\n\n"
        f"COMPUTED ANSWER (from the reasoning record — say this):\n{grounded_text}\n\n"
        f"RECORD EXTRACT (context only; do not introduce anything new):\n"
        f"{record_extract}"
    )
    try:
        reply = _call(_PHRASE_SYSTEM, user, None, effort="low")
    except AssistantUnavailable as exc:
        return PhrasedAnswer(text=grounded_text, model_used=False, note=str(exc))

    allowed = _numbers(grounded_text) | _numbers(record_extract)
    invented = sorted(_numbers(reply) - allowed)
    if invented:
        return PhrasedAnswer(
            text=grounded_text,
            model_used=False,
            note=(
                "the model introduced figures that are not in the record "
                f"({', '.join(invented[:5])}), so the computed answer is shown instead"
            ),
        )
    return PhrasedAnswer(text=reply, model_used=True)


_CONVERSE_SYSTEM = """\
You are YUKTI, an institutional reasoning system for investment committees. You \
are talking to the analyst working one case. Talk normally — this is a \
conversation, not a form.

What you know, and its limits:

- YUKTI carries a case from messy material to a defensible decision. A person \
assembles material against a fifteen-figure diligence schedule; a frozen, \
deterministic engine reads only that material and produces a judgment; the \
committee records a decision against that judgment. Confidence is derived from \
evidence quality, coverage and contradictions — nobody can type one in. It \
takes the weakest review area, not the average. CONTESTED and INSUFFICIENT \
BASIS are real outcomes, not failures.
- You may explain any of that, discuss what the analyst should chase next, and \
answer questions about this case using the record extract below.

Two things you must not do, both checked after you answer:

- Do not state any figure, band, count or name that is not in the record \
extract. If you want to cite a number, it must be there. Say you do not have it \
rather than producing one.
- Do not give investment advice, a view on the company, or a recommendation. \
The engine reached a judgment; you report and explain it, you do not form your \
own or argue with it. If asked what you think of the deal, say that the record \
holds the judgment and the committee holds the decision, and point at what the \
record actually says.

If the record cannot answer something, say so plainly and say what would. Be \
brief — a short paragraph unless more is genuinely needed."""


def converse(
    question: str,
    case: Case,
    record_extract: str,
) -> PhrasedAnswer:
    """Answer an open question conversationally, grounded in the record.

    Used for anything ``explain.classify`` does not recognise, so the chat holds
    an ordinary conversation instead of refusing everything outside a fixed
    intent list. The record is the only source of case facts, and the same
    numeric check that guards ``phrase`` guards this: a reply carrying a figure
    the record does not contain is discarded rather than shown.
    """
    user = (
        f"CASE: {case.title} — {case.status()}\n"
        f"The committee is being asked to: {case.requested_decision}\n\n"
        f"ANALYST SAID: {question}\n\n"
        f"RECORD EXTRACT (the only source of facts about this case):\n"
        f"{record_extract}"
    )
    try:
        reply = _call(_CONVERSE_SYSTEM, user, None, effort="low")
    except AssistantUnavailable as exc:
        raise exc

    invented = sorted(_numbers(reply) - _numbers(record_extract) - _numbers(question))
    if invented:
        return PhrasedAnswer(
            text=(
                "I started to answer that, but the reply carried figures the "
                f"record does not contain ({', '.join(invented[:5])}), so I have "
                "held it back. Ask me about the recommendation, the confidence "
                "and what limits it, the conditions, what is missing, what is "
                "contested, the sources, or what would change the result — those "
                "I answer straight from the record."
            ),
            model_used=False,
            note="a drafted reply was discarded for citing figures absent from the record",
        )
    return PhrasedAnswer(text=reply, model_used=True)


def check() -> str:
    """One small call, so a person can verify their key without reading code."""
    report = status()
    lines = [
        f"model:        {report['model']}",
        f"base_url:     {report['base_url']}",
        f"key present:  {report['key_configured']}",
        f"sdk present:  {report['sdk_installed']}",
        "",
    ]
    try:
        reply = _call(
            "Reply with exactly: ready",
            "Say ready.",
            None,
            effort="low",
        )
    except AssistantUnavailable as exc:
        lines.append(f"RESULT: not available — {exc}")
        return "\n".join(lines)
    lines.append(f"RESULT: reachable. The model said: {reply[:80]!r}")
    return "\n".join(lines)


__all__ = [
    "AssistantUnavailable",
    "PhrasedAnswer",
    "check",
    "enabled",
    "phrase",
    "propose",
    "status",
]
