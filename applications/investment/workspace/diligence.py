"""The standard diligence schedule.

An institution does not ask an analyst for ``net_revenue_retention_pct``. It
asks for net revenue retention, and it knows in advance which figures a
committee requires before it will look at a case. This module is that list.

Every entry corresponds to a figure the reasoning engine looks for. That
correspondence is the point: a case with gaps in this schedule is a case the
committee cannot fully assess, and the schedule is what lets the product say
*which* figures are outstanding before anyone runs anything.

Review areas group the schedule the way a diligence team divides work. They are
presented to the user as review areas and nothing else -- how the engine
allocates work internally is not the institution's concern.

The metric keys, source kinds and figure statuses here are the engine's
vocabulary and must match it exactly. They are the product's contract with
infrastructure and are never shown to a user; the ``label`` is what is shown.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ScheduleItem:
    """One figure the committee requires, in institutional language."""

    metric: str
    label: str
    unit: str
    review_area: str
    guidance: str


@dataclass(frozen=True)
class Vocabulary:
    """One selectable value, with the plain-language meaning shown beside it."""

    key: str
    label: str
    meaning: str


# Review areas, in the order a diligence pack is normally assembled.
FINANCIAL_POSITION = "Financial position"
REVENUE_QUALITY = "Revenue quality and risk"
MARKET = "Market"
GOVERNANCE = "Governance"

REVIEW_AREAS = (FINANCIAL_POSITION, REVENUE_QUALITY, MARKET, GOVERNANCE)

SCHEDULE: tuple[ScheduleItem, ...] = (
    ScheduleItem(
        metric="arr_usd",
        label="Annual recurring revenue",
        unit="USD",
        review_area=FINANCIAL_POSITION,
        guidance="Contracted recurring revenue at the most recent period end.",
    ),
    ScheduleItem(
        metric="yoy_growth_pct",
        label="Year-over-year growth",
        unit="%",
        review_area=FINANCIAL_POSITION,
        guidance="Growth in recurring revenue against the prior comparable period.",
    ),
    ScheduleItem(
        metric="gross_margin_pct",
        label="Gross margin",
        unit="%",
        review_area=FINANCIAL_POSITION,
        guidance="Gross margin on recurring revenue, net of delivery cost.",
    ),
    ScheduleItem(
        metric="net_burn_monthly_usd",
        label="Net monthly burn",
        unit="USD",
        review_area=FINANCIAL_POSITION,
        guidance="Average net cash consumed per month over the trailing period.",
    ),
    ScheduleItem(
        metric="cash_usd",
        label="Cash on hand",
        unit="USD",
        review_area=FINANCIAL_POSITION,
        guidance="Unrestricted cash at the most recent period end.",
    ),
    ScheduleItem(
        metric="top_customer_revenue_pct",
        label="Largest customer share of revenue",
        unit="%",
        review_area=REVENUE_QUALITY,
        guidance="Share of recurring revenue attributable to the largest account.",
    ),
    ScheduleItem(
        metric="net_revenue_retention_pct",
        label="Net revenue retention",
        unit="%",
        review_area=REVENUE_QUALITY,
        guidance="Retention including expansion, for the most recent cohort year.",
    ),
    ScheduleItem(
        metric="logo_churn_pct",
        label="Logo churn",
        unit="%",
        review_area=REVENUE_QUALITY,
        guidance="Customers lost in the period as a share of opening count.",
    ),
    ScheduleItem(
        metric="tam_usd",
        label="Addressable market",
        unit="USD",
        review_area=MARKET,
        guidance="Addressable market on the segment definition used by the source.",
    ),
    ScheduleItem(
        metric="market_growth_pct",
        label="Market growth rate",
        unit="%",
        review_area=MARKET,
        guidance="Annual growth of the addressable segment.",
    ),
    ScheduleItem(
        metric="competitor_count",
        label="Competitors identified",
        unit="count",
        review_area=MARKET,
        guidance="Direct competitors named in the market review.",
    ),
    ScheduleItem(
        metric="founder_voting_control_pct",
        label="Founder voting control",
        unit="%",
        review_area=GOVERNANCE,
        guidance="Voting rights held by founders after the proposed round.",
    ),
    ScheduleItem(
        metric="independent_board_seats",
        label="Independent board seats",
        unit="count",
        review_area=GOVERNANCE,
        guidance="Board seats held by directors independent of management.",
    ),
    ScheduleItem(
        metric="audit_status",
        label="Audit status",
        unit="text",
        review_area=GOVERNANCE,
        guidance="Whether the most recent statements were independently audited.",
    ),
    ScheduleItem(
        metric="reporting_cadence",
        label="Reporting cadence",
        unit="text",
        review_area=GOVERNANCE,
        guidance="How often the company reports to investors.",
    ),
)

# How a source came to exist. This is a structural fact about the document, not
# a judgement about what it says -- which is why the institution records it at
# intake rather than deciding it later.
SOURCE_KINDS: tuple[Vocabulary, ...] = (
    Vocabulary("audit", "Audited", "Independently audited or certified."),
    Vocabulary("management", "Management-provided", "Supplied by the company."),
    Vocabulary("interview", "Primary interview", "Reference or customer calls."),
    Vocabulary("third_party", "Third-party research", "External research or sizing."),
    Vocabulary("assertion", "Unsupported assertion", "Stated, with nothing behind it."),
)

# How settled a figure is, as the diligence team found it.
FIGURE_STATUSES: tuple[Vocabulary, ...] = (
    Vocabulary("confirmed", "Confirmed", "Corroborated against a primary source."),
    Vocabulary(
        "reported", "Reported", "Stated by a source, not independently checked."
    ),
    Vocabulary("estimated", "Estimated", "Derived or modelled rather than observed."),
    Vocabulary("disputed", "Disputed", "Sources disagree, or the figure is contested."),
    Vocabulary("unknown", "Unknown", "Recorded, but its standing is not established."),
)

_BY_METRIC = {item.metric: item for item in SCHEDULE}
_SOURCE_KIND_LABELS = {entry.key: entry.label for entry in SOURCE_KINDS}
_FIGURE_STATUS_LABELS = {entry.key: entry.label for entry in FIGURE_STATUSES}

# Review area -> the engine's name for the area. Used only to relabel engine
# output on the way to the screen, so the user never reads an internal name.
_ENGINE_AREA_LABELS = {
    "financial_posture": FINANCIAL_POSITION,
    "risk_exposure": REVENUE_QUALITY,
    "market_position": MARKET,
    "governance": GOVERNANCE,
}

# Engine topic -> the heading a committee would recognise.
_ENGINE_TOPIC_LABELS = {
    "growth": "Growth",
    "capital_efficiency": "Capital efficiency",
    "revenue_quality": "Revenue quality",
    "market_opportunity": "Market opportunity",
    "competitive_position": "Competitive position",
    "concentration_risk": "Concentration risk",
    "governance_quality": "Governance quality",
    "financial_transparency": "Financial transparency",
}


def item(metric: str) -> ScheduleItem | None:
    """Return the schedule entry for a metric, or None if it is not required."""
    return _BY_METRIC.get(metric)


def label_for_metric(metric: str) -> str:
    """Return the institutional label for a metric, falling back to the key.

    The fallback matters: if the engine ever reports a metric the schedule does
    not list, showing the raw key is honest. Hiding it would be worse.
    """
    found = _BY_METRIC.get(metric)
    return found.label if found else metric


def label_for_source_kind(kind: str) -> str:
    """Return the institutional label for a source kind."""
    return _SOURCE_KIND_LABELS.get(kind, kind)


def label_for_figure_status(status: str) -> str:
    """Return the institutional label for a figure status."""
    return _FIGURE_STATUS_LABELS.get(status, status)


def label_for_review_area(engine_area: str) -> str:
    """Return the review-area name for an engine area name."""
    return _ENGINE_AREA_LABELS.get(engine_area, engine_area)


def label_for_topic(topic: str) -> str:
    """Return the committee-facing heading for an engine topic."""
    return _ENGINE_TOPIC_LABELS.get(topic, topic.replace("_", " "))


# Whole-word substitutions applied to prose the engine authored before it is
# shown to a user. Every entry replaces an internal name with the institutional
# name for the same thing -- never a paraphrase, never a softening. The product
# is not allowed to rewrite what the engine said, only to say it in the
# institution's vocabulary.
#
# This exists because some engine prose is composed rather than looked up: a
# limiting factor reads "weakest contributing kernel is market_position", and
# there is no field to relabel, only a sentence. The engine is frozen and
# cannot be changed to phrase it differently.
_PROSE_SUBSTITUTIONS: dict[str, str] = {
    **_ENGINE_AREA_LABELS,
    **_ENGINE_TOPIC_LABELS,
    **{entry.metric: entry.label for entry in SCHEDULE},
    "kernels": "review areas",
    "kernel": "review area",
    "packet": "case material",
}

# Applied before the word map, and for one reason only: to drop an internal
# identifier from a sentence that already carries the human label beside it.
# "Claim clm-007 (net_revenue_retention_pct) is contradicted" becomes
# "net_revenue_retention_pct is contradicted", which the word map then finishes.
#
# Nothing is lost by this. The identifier remains in the audit view, which shows
# the reasoning record verbatim -- which is the one place a reader who needs
# `clm-007` is actually looking for it.
_IDENTIFIER_ELISIONS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bClaim clm-\d+ \(([^)]+)\)"), r"\1"),
)

# Longest first, so no key can be swallowed by a shorter one that prefixes it.
_PROSE_PATTERN = re.compile(
    r"\b("
    + "|".join(sorted(map(re.escape, _PROSE_SUBSTITUTIONS), key=len, reverse=True))
    + r")\b"
)


def institutional_text(text: str) -> str:
    """Relabel internal names inside engine-authored prose.

    Identifier elision first, then a whole-word substitution, and nothing else.
    Text containing no internal name passes through byte for byte, which is what
    keeps this a relabelling rather than a rewrite -- and what keeps the
    workspace unable to change the meaning of anything the engine concluded.
    """
    for pattern, replacement in _IDENTIFIER_ELISIONS:
        text = pattern.sub(replacement, text)
    return _PROSE_PATTERN.sub(lambda match: _PROSE_SUBSTITUTIONS[match.group(0)], text)


def metrics_by_review_area() -> dict[str, tuple[ScheduleItem, ...]]:
    """Group the schedule by review area, in schedule order."""
    return {
        area: tuple(entry for entry in SCHEDULE if entry.review_area == area)
        for area in REVIEW_AREAS
    }


def outstanding(recorded_metrics: frozenset[str]) -> tuple[ScheduleItem, ...]:
    """Return the schedule items the case has not recorded a figure for.

    This is the product's own coverage view, computed before anything runs. It
    is what lets the workspace tell a user what is missing while they can still
    go and find it, rather than after an analysis has already been limited by
    the gap.
    """
    return tuple(entry for entry in SCHEDULE if entry.metric not in recorded_metrics)
