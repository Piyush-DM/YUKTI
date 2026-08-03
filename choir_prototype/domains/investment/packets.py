"""Sample investment packets.

These are the *input* to the pipeline, in domain shape. They are deliberately
not the IR: they look like something a deal team would assemble, and turning
them into the IR is the translator's job.

Two packets are provided because one is not enough to show the thesis:

- ``orbital-series-b`` is a well-documented deal where the kernels reach a
  usable conclusion while genuinely disagreeing about one topic.
- ``northwind-seed`` is a thin packet where most kernels cannot see enough to
  conclude anything. The system should decline rather than guess.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceDocument:
    """A document supplied with the packet."""

    label: str
    origin: str
    kind: str


@dataclass(frozen=True)
class DataPoint:
    """One figure or fact from the packet, with the documents behind it."""

    metric: str
    value: str
    source_labels: tuple[str, ...]
    status: str


@dataclass(frozen=True)
class NotedConflict:
    """A conflict the deal team flagged between the packet's own sources."""

    metric: str
    note: str


@dataclass(frozen=True)
class InvestmentPacket:
    """Structured investment information, before translation."""

    id: str
    title: str
    company_name: str
    sector: str
    stage: str
    sources: tuple[SourceDocument, ...]
    data_points: tuple[DataPoint, ...]
    stated_assumptions: tuple[str, ...]
    noted_conflicts: tuple[NotedConflict, ...]


ORBITAL_SERIES_B = InvestmentPacket(
    id="orbital-series-b",
    title="Orbital Logistics -- Series B",
    company_name="Orbital Logistics Inc.",
    sector="supply chain software",
    stage="Series B",
    sources=(
        SourceDocument(
            label="SRC-AUDIT-FY24",
            origin="Independent audit of FY2024 statements",
            kind="audit",
        ),
        SourceDocument(
            label="SRC-DECK",
            origin="Management investor deck, Q1",
            kind="management",
        ),
        SourceDocument(
            label="SRC-CAPTABLE",
            origin="Certified capitalisation table",
            kind="audit",
        ),
        SourceDocument(
            label="SRC-MARKET",
            origin="Third-party market sizing report",
            kind="third_party",
        ),
        SourceDocument(
            label="SRC-CUSTOMER",
            origin="Reference calls with six customers",
            kind="interview",
        ),
    ),
    data_points=(
        DataPoint("arr_usd", "18000000", ("SRC-AUDIT-FY24",), "confirmed"),
        DataPoint("yoy_growth_pct", "62", ("SRC-AUDIT-FY24", "SRC-DECK"), "confirmed"),
        DataPoint("gross_margin_pct", "74", ("SRC-AUDIT-FY24",), "confirmed"),
        DataPoint("net_burn_monthly_usd", "1400000", ("SRC-AUDIT-FY24",), "confirmed"),
        DataPoint("cash_usd", "21000000", ("SRC-AUDIT-FY24",), "confirmed"),
        DataPoint("top_customer_revenue_pct", "38", ("SRC-DECK",), "reported"),
        DataPoint("net_revenue_retention_pct", "104", ("SRC-DECK",), "disputed"),
        DataPoint("logo_churn_pct", "11", ("SRC-DECK", "SRC-CUSTOMER"), "reported"),
        DataPoint("tam_usd", "8400000000", ("SRC-MARKET",), "estimated"),
        DataPoint("market_growth_pct", "19", ("SRC-MARKET",), "estimated"),
        DataPoint("competitor_count", "14", ("SRC-MARKET",), "estimated"),
        DataPoint("founder_voting_control_pct", "56", ("SRC-CAPTABLE",), "confirmed"),
        DataPoint("independent_board_seats", "1", ("SRC-CAPTABLE",), "confirmed"),
        DataPoint("audit_status", "audited", ("SRC-AUDIT-FY24",), "confirmed"),
        DataPoint("reporting_cadence", "monthly", ("SRC-DECK",), "reported"),
    ),
    stated_assumptions=(
        "The FY2024 audit scope covers all operating subsidiaries.",
        "Market sizing uses the vendor's own segment definition.",
    ),
    noted_conflicts=(
        NotedConflict(
            metric="net_revenue_retention_pct",
            note=(
                "Customer reference calls describe contraction at two accounts, "
                "which is inconsistent with the retention figure in the deck."
            ),
        ),
    ),
)


NORTHWIND_SEED = InvestmentPacket(
    id="northwind-seed",
    title="Northwind Instruments -- Seed",
    company_name="Northwind Instruments Ltd.",
    sector="laboratory hardware",
    stage="Seed",
    sources=(
        SourceDocument(
            label="SRC-FOUNDER",
            origin="Founder email summary",
            kind="assertion",
        ),
        SourceDocument(
            label="SRC-SECTOR",
            origin="Trade association sector note",
            kind="third_party",
        ),
    ),
    data_points=(
        DataPoint("arr_usd", "400000", ("SRC-FOUNDER",), "reported"),
        DataPoint("yoy_growth_pct", "120", ("SRC-FOUNDER",), "reported"),
        DataPoint("tam_usd", "1200000000", ("SRC-SECTOR",), "estimated"),
        DataPoint("market_growth_pct", "7", ("SRC-SECTOR",), "estimated"),
    ),
    stated_assumptions=("Founder figures are unaudited and self-reported.",),
    noted_conflicts=(),
)


PACKETS = {
    ORBITAL_SERIES_B.id: ORBITAL_SERIES_B,
    NORTHWIND_SEED.id: NORTHWIND_SEED,
}
