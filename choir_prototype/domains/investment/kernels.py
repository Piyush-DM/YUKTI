"""The reasoning kernels.

Four independent kernels, each looking at the same IR from a different angle.
They share no state, run in isolation, and cannot observe one another. That
independence is the whole point: when two kernels agree, the agreement means
something, because neither knew what the other concluded.

Every threshold used to turn a number into a stance is a named constant at the
top of the module. There are no hidden magic numbers, so a reader can disagree
with a judgement by pointing at the constant that produced it.
"""

from __future__ import annotations

from collections.abc import Sequence

from choir_prototype.core.contracts import (
    Artifact,
    Finding,
    Stance,
    derive_confidence,
)
from choir_prototype.core.ir import ChoirIR, Claim, Evidence

# This domain's topic vocabulary. Kernels label findings with these so the
# shared synthesizer can group them; the core does not know these strings.
TOPICS = (
    "growth",
    "capital_efficiency",
    "revenue_quality",
    "market_opportunity",
    "competitive_position",
    "concentration_risk",
    "governance_quality",
    "financial_transparency",
)

# --- Financial thresholds ---------------------------------------------------
STRONG_GROWTH_PCT = 40.0
WEAK_GROWTH_PCT = 15.0
HEALTHY_MARGIN_PCT = 70.0
WEAK_MARGIN_PCT = 50.0
COMFORTABLE_RUNWAY_MONTHS = 18.0
TIGHT_RUNWAY_MONTHS = 12.0

# --- Risk thresholds --------------------------------------------------------
CONCENTRATION_ALERT_PCT = 25.0
CONCENTRATION_SEVERE_PCT = 40.0
HEALTHY_NRR_PCT = 110.0
WEAK_NRR_PCT = 95.0
HIGH_CHURN_PCT = 15.0
# Annualised burn as a multiple of ARR. Above 1.0 the company spends more in a
# year than it books in a year.
EFFICIENT_BURN_RATIO = 0.5
UNSUSTAINABLE_BURN_RATIO = 1.0

# --- Market thresholds ------------------------------------------------------
LARGE_TAM_USD = 5_000_000_000.0
STRONG_MARKET_GROWTH_PCT = 15.0
CROWDED_COMPETITOR_COUNT = 12

# --- Governance thresholds --------------------------------------------------
FOUNDER_CONTROL_ALERT_PCT = 50.0
MINIMUM_INDEPENDENT_SEATS = 1


def _collect(
    ir: ChoirIR, predicates: Sequence[str]
) -> tuple[dict[str, Claim], tuple[Evidence, ...], int]:
    """Pull the claims a kernel cares about, with their evidence.

    Returns the claims found keyed by predicate, the de-duplicated evidence
    backing them, and how many of those claims something in the IR contradicts.
    Predicates absent from the packet are simply missing from the result -- that
    absence is what drives the coverage component of confidence.
    """
    found: dict[str, Claim] = {}
    evidence: dict[str, Evidence] = {}
    contradicted = ir.contradicted_claim_ids()
    contradictions = 0

    for predicate in predicates:
        claims = ir.claims_with_predicate(predicate)
        if not claims:
            continue
        claim = claims[0]
        found[predicate] = claim
        for item in ir.evidence_for_claim(claim):
            evidence.setdefault(item.id, item)
        if claim.id in contradicted:
            contradictions += 1

    ordered = tuple(sorted(evidence.values(), key=lambda item: item.id))
    return found, ordered, contradictions


def _number(claim: Claim | None) -> float | None:
    """Read a claim's value as a number, or None if it is not numeric."""
    if claim is None:
        return None
    try:
        return float(claim.value)
    except ValueError:
        return None


class FinancialPostureKernel:
    """Reads the operating numbers: growth, margin, burn, runway."""

    name = "financial_posture"

    PREDICATES = (
        "arr_usd",
        "yoy_growth_pct",
        "gross_margin_pct",
        "net_burn_monthly_usd",
        "cash_usd",
    )

    def run(self, ir: ChoirIR) -> Artifact:
        """Analyse financial posture and return an artifact."""
        found, evidence, contradictions = _collect(ir, self.PREDICATES)
        findings: list[Finding] = []
        unresolved: list[str] = []
        assumptions: list[str] = []

        growth = _number(found.get("yoy_growth_pct"))
        if growth is None:
            unresolved.append("Year-over-year growth was not stated in the packet.")
        else:
            claim = found["yoy_growth_pct"]
            if growth >= STRONG_GROWTH_PCT:
                stance, text = Stance.SUPPORTS, f"Growth of {growth:.0f}% is strong"
            elif growth >= WEAK_GROWTH_PCT:
                stance, text = Stance.NEUTRAL, f"Growth of {growth:.0f}% is moderate"
            else:
                stance, text = Stance.OPPOSES, f"Growth of {growth:.0f}% is weak"
            findings.append(
                Finding(
                    id="fin-growth",
                    topic="growth",
                    stance=stance,
                    statement=(
                        f"{text} against a {STRONG_GROWTH_PCT:.0f}% strong / "
                        f"{WEAK_GROWTH_PCT:.0f}% weak threshold."
                    ),
                    claim_ids=(claim.id,),
                    evidence_ids=claim.evidence_ids,
                )
            )

        margin = _number(found.get("gross_margin_pct"))
        if margin is None:
            unresolved.append("Gross margin was not stated in the packet.")
        else:
            claim = found["gross_margin_pct"]
            if margin >= HEALTHY_MARGIN_PCT:
                stance = Stance.SUPPORTS
                text = f"Gross margin of {margin:.0f}% is healthy for the category"
            elif margin >= WEAK_MARGIN_PCT:
                stance = Stance.CONDITIONAL
                text = f"Gross margin of {margin:.0f}% is serviceable but thin"
            else:
                stance = Stance.OPPOSES
                text = f"Gross margin of {margin:.0f}% is below the viable band"
            findings.append(
                Finding(
                    id="fin-margin",
                    topic="revenue_quality",
                    stance=stance,
                    statement=f"{text}.",
                    claim_ids=(claim.id,),
                    evidence_ids=claim.evidence_ids,
                )
            )

        cash = _number(found.get("cash_usd"))
        burn = _number(found.get("net_burn_monthly_usd"))
        if cash is None or burn is None:
            unresolved.append(
                "Runway could not be derived: cash or net burn was missing."
            )
        elif burn <= 0:
            findings.append(
                Finding(
                    id="fin-runway",
                    topic="capital_efficiency",
                    stance=Stance.SUPPORTS,
                    statement="Company is not burning cash; runway is unbounded.",
                    claim_ids=(found["cash_usd"].id, found["net_burn_monthly_usd"].id),
                )
            )
        else:
            runway = cash / burn
            assumptions.append(
                "Runway is derived as cash / net monthly burn, holding burn flat."
            )
            if runway >= COMFORTABLE_RUNWAY_MONTHS:
                stance = Stance.SUPPORTS
            elif runway >= TIGHT_RUNWAY_MONTHS:
                stance = Stance.CONDITIONAL
            else:
                stance = Stance.OPPOSES
            findings.append(
                Finding(
                    id="fin-runway",
                    topic="capital_efficiency",
                    stance=stance,
                    statement=(
                        f"Derived runway is {runway:.1f} months against a "
                        f"{COMFORTABLE_RUNWAY_MONTHS:.0f}-month comfort floor."
                    ),
                    claim_ids=(
                        found["cash_usd"].id,
                        found["net_burn_monthly_usd"].id,
                    ),
                    evidence_ids=tuple(
                        sorted(
                            set(found["cash_usd"].evidence_ids)
                            | set(found["net_burn_monthly_usd"].evidence_ids)
                        )
                    ),
                )
            )

        return Artifact(
            kernel_name=self.name,
            findings=tuple(findings),
            evidence_references=tuple(item.id for item in evidence),
            confidence=derive_confidence(
                evidence=evidence,
                expected_inputs=len(self.PREDICATES),
                found_inputs=len(found),
                contradiction_count=contradictions,
            ),
            assumptions=tuple(assumptions),
            unresolved_questions=tuple(unresolved),
        )


class RiskExposureKernel:
    """Reads concentration, retention and churn."""

    name = "risk_exposure"

    PREDICATES = (
        "top_customer_revenue_pct",
        "net_revenue_retention_pct",
        "logo_churn_pct",
        "net_burn_monthly_usd",
        "arr_usd",
    )

    def run(self, ir: ChoirIR) -> Artifact:
        """Analyse risk exposure and return an artifact."""
        found, evidence, contradictions = _collect(ir, self.PREDICATES)
        findings: list[Finding] = []
        unresolved: list[str] = []

        concentration = _number(found.get("top_customer_revenue_pct"))
        if concentration is None:
            unresolved.append("Customer concentration was not disclosed.")
        else:
            claim = found["top_customer_revenue_pct"]
            if concentration >= CONCENTRATION_SEVERE_PCT:
                stance = Stance.OPPOSES
                text = f"Top customer is {concentration:.0f}% of revenue -- severe"
            elif concentration >= CONCENTRATION_ALERT_PCT:
                stance = Stance.CONDITIONAL
                text = f"Top customer is {concentration:.0f}% of revenue -- elevated"
            else:
                stance = Stance.SUPPORTS
                text = f"Top customer is {concentration:.0f}% of revenue -- diversified"
            findings.append(
                Finding(
                    id="risk-concentration",
                    topic="concentration_risk",
                    stance=stance,
                    statement=(
                        f"{text} against a {CONCENTRATION_SEVERE_PCT:.0f}% severe / "
                        f"{CONCENTRATION_ALERT_PCT:.0f}% elevated threshold."
                    ),
                    claim_ids=(claim.id,),
                    evidence_ids=claim.evidence_ids,
                )
            )

        retention = _number(found.get("net_revenue_retention_pct"))
        churn = _number(found.get("logo_churn_pct"))
        if retention is None and churn is None:
            unresolved.append("Neither retention nor churn was disclosed.")
        else:
            signals: list[str] = []
            negative = False
            claim_ids: list[str] = []
            evidence_ids: set[str] = set()

            if retention is not None:
                claim = found["net_revenue_retention_pct"]
                claim_ids.append(claim.id)
                evidence_ids.update(claim.evidence_ids)
                if retention >= HEALTHY_NRR_PCT:
                    signals.append(f"net revenue retention {retention:.0f}% is healthy")
                elif retention >= WEAK_NRR_PCT:
                    signals.append(f"net revenue retention {retention:.0f}% is flat")
                    negative = True
                else:
                    signals.append(f"net revenue retention {retention:.0f}% is eroding")
                    negative = True

            if churn is not None:
                claim = found["logo_churn_pct"]
                claim_ids.append(claim.id)
                evidence_ids.update(claim.evidence_ids)
                if churn >= HIGH_CHURN_PCT:
                    signals.append(f"logo churn {churn:.0f}% is high")
                    negative = True
                else:
                    signals.append(f"logo churn {churn:.0f}% is contained")

            findings.append(
                Finding(
                    id="risk-retention",
                    topic="revenue_quality",
                    stance=Stance.OPPOSES if negative else Stance.SUPPORTS,
                    statement=f"Revenue durability: {'; '.join(signals)}.",
                    claim_ids=tuple(claim_ids),
                    evidence_ids=tuple(sorted(evidence_ids)),
                )
            )

        burn = _number(found.get("net_burn_monthly_usd"))
        arr = _number(found.get("arr_usd"))
        if burn is None or arr is None or arr <= 0:
            unresolved.append(
                "Burn efficiency could not be assessed: burn or ARR was missing."
            )
        else:
            ratio = (burn * 12) / arr
            if ratio < EFFICIENT_BURN_RATIO:
                stance = Stance.SUPPORTS
            elif ratio < UNSUSTAINABLE_BURN_RATIO:
                stance = Stance.CONDITIONAL
            else:
                stance = Stance.OPPOSES
            findings.append(
                Finding(
                    id="risk-burn",
                    topic="capital_efficiency",
                    stance=stance,
                    statement=(
                        f"Annualised burn is {ratio:.2f}x ARR against a "
                        f"{EFFICIENT_BURN_RATIO:.2f}x efficient / "
                        f"{UNSUSTAINABLE_BURN_RATIO:.2f}x unsustainable threshold."
                    ),
                    claim_ids=(
                        found["net_burn_monthly_usd"].id,
                        found["arr_usd"].id,
                    ),
                    evidence_ids=tuple(
                        sorted(
                            set(found["net_burn_monthly_usd"].evidence_ids)
                            | set(found["arr_usd"].evidence_ids)
                        )
                    ),
                )
            )

        # Only flag contradictions on claims this kernel actually read. A
        # contradiction elsewhere in the packet is not this kernel's business.
        contradicted = ir.contradicted_claim_ids()
        for claim in sorted(found.values(), key=lambda item: item.id):
            if claim.id in contradicted:
                unresolved.append(
                    f"Claim {claim.id} ({claim.predicate}) is contradicted "
                    "elsewhere in the packet; this finding is provisional."
                )

        return Artifact(
            kernel_name=self.name,
            findings=tuple(findings),
            evidence_references=tuple(item.id for item in evidence),
            confidence=derive_confidence(
                evidence=evidence,
                expected_inputs=len(self.PREDICATES),
                found_inputs=len(found),
                contradiction_count=contradictions,
            ),
            assumptions=(),
            unresolved_questions=tuple(unresolved),
        )


class MarketPositionKernel:
    """Reads addressable market, market growth and competitive density."""

    name = "market_position"

    PREDICATES = ("tam_usd", "market_growth_pct", "competitor_count")

    def run(self, ir: ChoirIR) -> Artifact:
        """Analyse market position and return an artifact."""
        found, evidence, contradictions = _collect(ir, self.PREDICATES)
        findings: list[Finding] = []
        unresolved: list[str] = []
        assumptions: list[str] = []

        tam = _number(found.get("tam_usd"))
        market_growth = _number(found.get("market_growth_pct"))
        if tam is None and market_growth is None:
            unresolved.append("No market sizing or market growth figure was supplied.")
        else:
            signals: list[str] = []
            positive = False
            claim_ids: list[str] = []
            evidence_ids: set[str] = set()

            if tam is not None:
                claim = found["tam_usd"]
                claim_ids.append(claim.id)
                evidence_ids.update(claim.evidence_ids)
                billions = tam / 1_000_000_000
                if tam >= LARGE_TAM_USD:
                    signals.append(f"addressable market ${billions:.1f}B is large")
                    positive = True
                else:
                    signals.append(f"addressable market ${billions:.1f}B is modest")

            if market_growth is not None:
                claim = found["market_growth_pct"]
                claim_ids.append(claim.id)
                evidence_ids.update(claim.evidence_ids)
                if market_growth >= STRONG_MARKET_GROWTH_PCT:
                    signals.append(f"market growing {market_growth:.0f}% a year")
                    positive = True
                else:
                    signals.append(f"market growing only {market_growth:.0f}% a year")

            findings.append(
                Finding(
                    id="mkt-opportunity",
                    topic="market_opportunity",
                    stance=Stance.SUPPORTS if positive else Stance.NEUTRAL,
                    statement=f"Market opportunity: {'; '.join(signals)}.",
                    claim_ids=tuple(claim_ids),
                    evidence_ids=tuple(sorted(evidence_ids)),
                )
            )

        competitors = _number(found.get("competitor_count"))
        if competitors is None:
            unresolved.append("Competitive density was not characterised.")
        else:
            claim = found["competitor_count"]
            crowded = competitors >= CROWDED_COMPETITOR_COUNT
            findings.append(
                Finding(
                    id="mkt-competition",
                    topic="competitive_position",
                    stance=Stance.CONDITIONAL if crowded else Stance.SUPPORTS,
                    statement=(
                        f"{competitors:.0f} named competitors against a crowding "
                        f"threshold of {CROWDED_COMPETITOR_COUNT}."
                    ),
                    claim_ids=(claim.id,),
                    evidence_ids=claim.evidence_ids,
                )
            )

        for item in evidence:
            if item.quality.value == "estimated":
                assumptions.append(
                    f"Market figures from {item.id} are estimates, not measurements."
                )

        return Artifact(
            kernel_name=self.name,
            findings=tuple(findings),
            evidence_references=tuple(item.id for item in evidence),
            confidence=derive_confidence(
                evidence=evidence,
                expected_inputs=len(self.PREDICATES),
                found_inputs=len(found),
                contradiction_count=contradictions,
            ),
            assumptions=tuple(assumptions),
            unresolved_questions=tuple(unresolved),
        )


class GovernanceKernel:
    """Reads control, board composition and reporting quality."""

    name = "governance"

    PREDICATES = (
        "founder_voting_control_pct",
        "independent_board_seats",
        "audit_status",
        "reporting_cadence",
    )

    def run(self, ir: ChoirIR) -> Artifact:
        """Analyse governance posture and return an artifact."""
        found, evidence, contradictions = _collect(ir, self.PREDICATES)
        findings: list[Finding] = []
        unresolved: list[str] = []

        control = _number(found.get("founder_voting_control_pct"))
        seats = _number(found.get("independent_board_seats"))
        if control is None and seats is None:
            unresolved.append("Neither voting control nor board composition was given.")
        else:
            signals: list[str] = []
            concerning = False
            claim_ids: list[str] = []
            evidence_ids: set[str] = set()

            if control is not None:
                claim = found["founder_voting_control_pct"]
                claim_ids.append(claim.id)
                evidence_ids.update(claim.evidence_ids)
                if control >= FOUNDER_CONTROL_ALERT_PCT:
                    signals.append(f"founders retain {control:.0f}% voting control")
                    concerning = True
                else:
                    signals.append(f"founder voting control is {control:.0f}%")

            if seats is not None:
                claim = found["independent_board_seats"]
                claim_ids.append(claim.id)
                evidence_ids.update(claim.evidence_ids)
                if seats < MINIMUM_INDEPENDENT_SEATS:
                    signals.append("no independent board seats")
                    concerning = True
                else:
                    signals.append(f"{seats:.0f} independent board seat(s)")

            findings.append(
                Finding(
                    id="gov-control",
                    topic="governance_quality",
                    stance=Stance.CONDITIONAL if concerning else Stance.SUPPORTS,
                    statement=f"Control and oversight: {'; '.join(signals)}.",
                    claim_ids=tuple(claim_ids),
                    evidence_ids=tuple(sorted(evidence_ids)),
                )
            )

        audit = found.get("audit_status")
        if audit is None:
            unresolved.append("Audit status was not stated.")
        else:
            audited = audit.value.lower() == "audited"
            findings.append(
                Finding(
                    id="gov-transparency",
                    topic="financial_transparency",
                    stance=Stance.SUPPORTS if audited else Stance.OPPOSES,
                    statement=f"Financial statements are {audit.value}.",
                    claim_ids=(audit.id,),
                    evidence_ids=audit.evidence_ids,
                )
            )

        if "reporting_cadence" not in found:
            unresolved.append("Reporting cadence was not stated.")

        return Artifact(
            kernel_name=self.name,
            findings=tuple(findings),
            evidence_references=tuple(item.id for item in evidence),
            confidence=derive_confidence(
                evidence=evidence,
                expected_inputs=len(self.PREDICATES),
                found_inputs=len(found),
                contradiction_count=contradictions,
            ),
            assumptions=(),
            unresolved_questions=tuple(unresolved),
        )


def all_kernels() -> tuple[
    FinancialPostureKernel, RiskExposureKernel, MarketPositionKernel, GovernanceKernel
]:
    """Return every kernel, in fixed dispatch order."""
    return (
        FinancialPostureKernel(),
        RiskExposureKernel(),
        MarketPositionKernel(),
        GovernanceKernel(),
    )
