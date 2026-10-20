"""Answering questions about a case **from the record**, never by generating one.

This is the conversational half of the workspace, and it contains no model and
no prose generation. Every answer below is assembled out of values the pipeline
already recorded: the derived confidence and its limiting factor, the conditions,
the review areas and their coverage, the contested topics, the outstanding
schedule items, the ledger.

Why it works this way
---------------------

The engine's central guarantee is commitment E9 — *explanations are projections
of the trace, never regenerated* — enforced by the ``projection-integrity``
check, which renders one record twice and requires identical text. ``report.py``
and ``inspection.py`` are that guarantee for the terminal; this module is the
same guarantee for a chat.

A generated answer would break it. Asked "why is confidence low", a model would
produce a plausible sentence; this returns the *limiting factor the pipeline
computed*, which is the actual reason and is checkable against the artifact on
disk. If the two ever disagreed the record would be right and the chat wrong,
which is why the chat is not permitted to have an opinion.

The consequence is deliberate and visible: this answers a bounded set of
questions and says plainly when a question is outside it, rather than
improvising. A chat that declines is the same discipline as a judgment that
declines.
"""

from __future__ import annotations

from dataclasses import dataclass

from applications.investment.workspace.analysis import Judgment
from applications.investment.workspace.cases import Case

# Recognised intents, each a set of phrasings. Matched by longest hit so
# "what is missing from the schedule" reaches coverage rather than conditions.
_INTENTS: dict[str, tuple[str, ...]] = {
    "recommendation": (
        "what did it conclude",
        "what is the recommendation",
        "what's the recommendation",
        "what did it decide",
        "what is the judgment",
        "recommendation",
        "conclusion",
        "verdict",
        "summary",
        "summarise",
        "summarize",
    ),
    "why": (
        "why this recommendation",
        "why proceed",
        "why not decline",
        "why not proceed",
        "why did it",
        "how did it reach",
        "reasoning",
        "why",
    ),
    "confidence": (
        "why is confidence low",
        "why low confidence",
        "what is limiting confidence",
        "limiting factor",
        "how confident",
        "confidence",
    ),
    "conditions": ("what are the conditions", "conditions", "caveats", "provisos"),
    "gaps": (
        "what is missing",
        "what's missing",
        "what is outstanding",
        "what wasn't established",
        "what was not established",
        "gaps",
        "missing",
        "outstanding",
        "unresolved",
    ),
    "contested": (
        "what is contested",
        "what do they disagree",
        "disagreement",
        "disagree",
        "contested",
        "conflict",
    ),
    "evidence": (
        "what sources",
        "which sources",
        "what evidence",
        "which evidence",
        "sources",
        "evidence",
    ),
    "improve": (
        "what would change",
        "what would improve",
        "how do i get to proceed",
        "what would make it stronger",
        "strengthen",
        "improve",
    ),
    "status": ("where are we", "what happens next", "next step", "status", "progress"),
    "decision": (
        "what did the committee decide",
        "what was decided",
        "decision",
        "ledger",
    ),
    "provenance": (
        "where did that come from",
        "where did this come from",
        "where did these figures come from",
        "where did the figures come from",
        "come from",
        "what did you read",
        "how do you know",
        "provenance",
        "came from",
    ),
}


@dataclass(frozen=True)
class Answer:
    """One reply, and the record fields it was assembled from.

    ``sources`` names where in the record each part came from, so an answer can
    be checked against the artifact rather than believed.
    """

    text: str
    sources: tuple[str, ...] = ()
    understood: bool = True


def classify(question: str) -> str | None:
    """Which intent a question matches, or ``None``. Longest phrasing wins."""
    lowered = question.lower().strip()
    best: tuple[int, str] | None = None
    for intent, phrasings in _INTENTS.items():
        for phrasing in phrasings:
            if phrasing in lowered and (best is None or len(phrasing) > best[0]):
                best = (len(phrasing), intent)
    return best[1] if best else None


def _bullets(items: tuple[str, ...] | list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def _no_judgment(case: Case) -> Answer:
    outstanding = ""
    return Answer(
        text=(
            f"No judgment on file for {case.title} yet. "
            f"{len(case.figures)} of 15 figures are recorded. "
            "Ask me to run it once the material is in place." + outstanding
        ),
        sources=("case.figures",),
    )


def answer(question: str, case: Case, judgment: Judgment | None) -> Answer:
    """Answer one question about a case, entirely from its record."""
    intent = classify(question)
    if intent is None:
        return Answer(
            text=(
                "I answer from this case's record rather than by writing prose, "
                "so I only handle what the record actually holds. Try: what did "
                "it conclude, why, what is limiting confidence, what are the "
                "conditions, what is missing, what is contested, what sources "
                "were used, what would change it, what was decided, or where did "
                "a figure come from."
            ),
            understood=False,
        )

    if intent == "status":
        return _status(case, judgment)
    if intent == "decision":
        return _decision(case)
    if intent == "provenance":
        return _provenance(case)
    if judgment is None:
        return _no_judgment(case)

    handlers = {
        "recommendation": _recommendation,
        "why": _why,
        "confidence": _confidence,
        "conditions": _conditions,
        "gaps": _gaps,
        "contested": _contested,
        "evidence": _evidence,
        "improve": _improve,
    }
    return handlers[intent](judgment)


def _status(case: Case, judgment: Judgment | None) -> Answer:
    status = case.status()
    nxt = {
        "Draft": "Paste what you know, or record figures on the Material screen.",
        "Material assembled": "Ask me to request the judgment.",
        "Analysed": "Record the committee's decision when you are ready.",
        "Decided": "Nothing outstanding. Re-analysing would create a new judgment.",
    }.get(status, "")
    lines = [
        f"{case.title} is at **{status}**.",
        f"{len(case.figures)} of 15 figures recorded, "
        f"{len(case.sources)} source(s) in the register, "
        f"{len(case.judgments)} judgment(s), {len(case.ledger)} decision(s).",
    ]
    if judgment is not None:
        lines.append(
            f"The judgment in force is {judgment.judgment_id}: "
            f"{judgment.recommendation} at {judgment.confidence} confidence."
        )
    if nxt:
        lines.append(f"Next: {nxt}")
    return Answer("\n\n".join(lines), ("case.status()", "case.judgments"))


def _decision(case: Case) -> Answer:
    if not case.ledger:
        return Answer(
            "No decision is recorded yet. The ledger is what the committee "
            "chose, held separately from what the analysis recommended.",
            ("case.ledger",),
        )
    lines = []
    for entry in case.ledger:
        lines.append(
            f"**{entry.decision}** — {entry.decided_by}, {entry.recorded_on}. "
            f"Recorded against {entry.judgment_id} "
            f"({entry.judgment_recommendation} at {entry.judgment_confidence}). "
            f"{entry.rationale}".strip()
        )
    return Answer("\n\n".join(lines), ("case.ledger",))


def _provenance(case: Case) -> Answer:
    if not case.intake_records:
        return Answer(
            "Nothing on this case was read from prose — the figures were "
            "recorded directly, so there is no passage to point at. Figures "
            "read from pasted material keep the sentence they came from.",
            ("case.intake_records",),
        )
    lines = [
        f"{len(case.intake_records)} figure(s) on this case were read from "
        "pasted material and confirmed. Each kept the passage it came from:"
    ]
    for record in case.intake_records[-8:]:
        mark = " (corrected on accept)" if record.edited else ""
        lines.append(
            f"- **{record.metric}** = {record.value} "
            f"[{record.status}]{mark}\n  from: “{record.quote}”"
        )
    return Answer("\n".join(lines), ("case.intake_records",))


def _recommendation(judgment: Judgment) -> Answer:
    return Answer(
        f"**{judgment.recommendation}** at {judgment.confidence} confidence "
        f"({judgment.judgment_id}, {judgment.recorded_on}).\n\n"
        f"{judgment.outcome_guidance}",
        ("judgment.recommendation", "judgment.confidence"),
    )


def _why(judgment: Judgment) -> Answer:
    text = (
        f"**{judgment.recommendation}** was reached this way — these are the "
        "steps the pipeline recorded, in order:\n\n"
        f"{_bullets(judgment.rationale)}"
    )
    if judgment.disagreements:
        topics = ", ".join(view.topic for view in judgment.disagreements)
        text += f"\n\nOne thing to note: the review areas are split on {topics}."
    return Answer(text, ("judgment.rationale", "judgment.disagreements"))


def _confidence(judgment: Judgment) -> Answer:
    weakest = max(
        judgment.review_areas,
        key=lambda area: _BAND_ORDER.get(area.confidence, -1),
        default=None,
    )
    lines = [
        f"Institutional confidence is **{judgment.confidence}**.",
        f"Limited by: {judgment.confidence_note}",
        "",
        "Confidence is the *weakest* contributing review area, not the average "
        "— a conclusion is no more reliable than the thinnest thing under it. "
        "By review area:",
        _bullets(
            tuple(
                f"{area.review_area}: {area.confidence} "
                f"({area.coverage}) — {area.confidence_note}"
                for area in judgment.review_areas
            )
        ),
    ]
    if weakest is not None:
        lines.append(
            f"\nSo the binding constraint is **{weakest.review_area}**. "
            "Improving anything else will not move the headline number."
        )
    return Answer(
        "\n".join(lines),
        ("judgment.confidence", "judgment.confidence_note", "judgment.review_areas"),
    )


# Weakest last, for picking the binding review area.
_BAND_ORDER = {"High": 0, "Moderate": 1, "Low": 2, "Insufficient": 3}


def _conditions(judgment: Judgment) -> Answer:
    if not judgment.conditions:
        return Answer(
            "No conditions. Nothing in this judgment supports proceeding only "
            "if something is resolved first.",
            ("judgment.conditions",),
        )
    lines = [
        f"{len(judgment.conditions)} condition(s) — findings that support "
        "proceeding only if something is resolved first:"
    ]
    for finding in judgment.conditions:
        cites = ", ".join(finding.evidence_labels) or "no source cited"
        lines.append(f"- {finding.statement}\n  ({finding.topic}; cites {cites})")
    return Answer("\n".join(lines), ("judgment.conditions",))


def _gaps(judgment: Judgment) -> Answer:
    parts = []
    if judgment.outstanding_schedule_items:
        parts.append(
            "Not recorded on the diligence schedule:\n"
            + _bullets(judgment.outstanding_schedule_items)
        )
    if judgment.unresolved_questions:
        parts.append(
            "The analysis could not establish:\n"
            + _bullets(judgment.unresolved_questions)
        )
    if judgment.remaining_uncertainty:
        parts.append(
            "Carried forward unresolved:\n" + _bullets(judgment.remaining_uncertainty)
        )
    if not parts:
        return Answer(
            "Nothing outstanding: the schedule is complete and no review area "
            "reported a question it could not answer.",
            ("judgment.outstanding_schedule_items",),
        )
    parts.append(
        "A blank is recorded as a gap and reported. It is never treated as a "
        "zero, and never quietly absorbed into the conclusion."
    )
    return Answer(
        "\n\n".join(parts),
        (
            "judgment.outstanding_schedule_items",
            "judgment.unresolved_questions",
            "judgment.remaining_uncertainty",
        ),
    )


def _contested(judgment: Judgment) -> Answer:
    if not judgment.disagreements:
        note = "No review areas reached directly opposing conclusions on any topic."
        if judgment.agreements:
            topics = ", ".join(view.topic for view in judgment.agreements)
            note += (
                f" They independently agreed on: {topics}. That agreement means "
                "something because no review area can see another's work."
            )
        return Answer(note, ("judgment.disagreements", "judgment.agreements"))

    lines = ["The review areas are split on:"]
    for view in judgment.disagreements:
        lines.append(f"\n**{view.topic}**")
        for area, stance, statement in view.positions:
            lines.append(f"- {area} ({stance}): {statement}")
    lines.append(
        "\nBoth positions are reported rather than averaged. A live "
        "disagreement is a result, not a failure to decide."
    )
    return Answer("\n".join(lines), ("judgment.disagreements",))


def _evidence(judgment: Judgment) -> Answer:
    labels: list[str] = []
    for area in judgment.review_areas:
        for finding in area.findings:
            for label in finding.evidence_labels:
                if label not in labels:
                    labels.append(label)
    if not labels:
        return Answer("No finding cited a source.", ("judgment.review_areas",))
    lines = ["Sources cited by at least one finding:", _bullets(tuple(labels)), ""]
    lines.append("By review area:")
    for area in judgment.review_areas:
        cited = sorted(
            {label for finding in area.findings for label in finding.evidence_labels}
        )
        lines.append(f"- {area.review_area}: {', '.join(cited) or 'none'}")
    return Answer("\n".join(lines), ("judgment.review_areas",))


def _improve(judgment: Judgment) -> Answer:
    moves: list[str] = []
    weakest = max(
        judgment.review_areas,
        key=lambda area: _BAND_ORDER.get(area.confidence, -1),
        default=None,
    )
    if weakest is not None:
        moves.append(
            f"Confidence is held down by **{weakest.review_area}** "
            f"({weakest.confidence}) — {weakest.confidence_note}. "
            "Confidence takes the weakest review area, so this is the only one "
            "that moves the headline."
        )
    if judgment.outstanding_schedule_items:
        moves.append(
            "Record the outstanding figures — coverage is part of how "
            "confidence is derived:\n" + _bullets(judgment.outstanding_schedule_items)
        )
    if judgment.conditions:
        moves.append(
            f"Resolve the {len(judgment.conditions)} condition(s); each is a "
            "finding that supports proceeding only once something is settled."
        )
    if judgment.disagreements:
        moves.append(
            "Settle the contested topic(s) with better material: "
            + ", ".join(view.topic for view in judgment.disagreements)
        )
    moves.append(
        "Note what will *not* move it: nothing you say to me. Confidence is "
        "derived from evidence quality, coverage and contradictions. There is "
        "no path in this product that lets anyone type a confidence in."
    )
    return Answer(
        "\n\n".join(moves),
        ("judgment.review_areas", "judgment.conditions", "judgment.disagreements"),
    )


def suggestions(case: Case, judgment: Judgment | None) -> tuple[str, ...]:
    """Questions worth asking about this case right now, given its state."""
    if judgment is None:
        if not case.figures:
            return ("What happens next?",)
        return ("What is missing?", "What happens next?")
    prompts = ["Why this recommendation?", "What is limiting confidence?"]
    if judgment.conditions:
        prompts.append("What are the conditions?")
    if judgment.disagreements:
        prompts.append("What is contested?")
    prompts.append("What would change it?")
    if case.intake_records:
        prompts.append("Where did these figures come from?")
    return tuple(prompts)


__all__ = ["Answer", "answer", "classify", "suggestions"]
