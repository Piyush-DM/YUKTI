"""Reproduction script for the `yukti-systems` product-validation run.

Builds the case through the real workspace HTTP API (the same endpoints the
browser UI calls) from the figures mapped by hand out of
`yukti_systems_series_a_packet.txt`, then requests the judgment. Requires the
workspace server running locally first:

    python yukti.py --no-browser

Re-running this against a case store that already has a `yukti-systems` case
will open a second one under a disambiguated id (e.g. `yukti-systems-2`) --
`cases.py::_allocate_id` guarantees a fresh slug rather than colliding.
"""
import json
import urllib.request

BASE = "http://127.0.0.1:8770"


def post(path, body):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        BASE + path, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


# 1. Open the case.
case = post(
    "/api/cases",
    {
        "company": "YUKTI Systems",
        "sector": "Enterprise AI / Investment Intelligence",
        "stage": "Series A",
        "owner": "Demo",
        "requested_decision": "Approve INR 42 crore Series A at INR 280 crore post-money valuation",
        "thesis": (
            "Institutional reasoning platform for enterprise AI; positions YUKTI "
            "as infrastructure for a shift from spreadsheets to software in "
            "investment decision-making."
        ),
    },
)
case_id = case["case"]["case_id"]
print(f"opened case: {case_id}")

# 2. Assemble material: sources, figures, assumptions, flagged conflicts.
# Mapping decisions (why each value/status/source was chosen, and why six
# schedule items were left blank) are explained in FINDINGS.md, not repeated
# here as comments.
sources = [
    {
        "label": "SRC-FIN-SUMMARY",
        "origin": "Financial Summary and Cash Position sections, Series A packet (Sept 2026)",
        "kind": "management",
    },
    {
        "label": "SRC-CUSTOMER-DOC",
        "origin": "Customer success document and Series A customer narrative",
        "kind": "management",
    },
    {
        "label": "SRC-MARKET-EST",
        "origin": "Management's market sizing, Series A investor presentation",
        "kind": "management",
    },
    {
        "label": "SRC-CAP-TABLE",
        "origin": "Cap table, Series A packet",
        "kind": "management",
    },
]

figures = [
    {"metric": "arr_usd", "value": "184000000", "status": "reported", "source_labels": ["SRC-FIN-SUMMARY"]},
    {"metric": "yoy_growth_pct", "value": "490", "status": "estimated", "source_labels": ["SRC-FIN-SUMMARY"]},
    {"metric": "gross_margin_pct", "value": "81", "status": "reported", "source_labels": ["SRC-FIN-SUMMARY"]},
    {"metric": "net_burn_monthly_usd", "value": "14000000", "status": "reported", "source_labels": ["SRC-FIN-SUMMARY"]},
    {"metric": "cash_usd", "value": "97000000", "status": "reported", "source_labels": ["SRC-FIN-SUMMARY"]},
    {"metric": "top_customer_revenue_pct", "value": "19", "status": "reported", "source_labels": ["SRC-CUSTOMER-DOC"]},
    {"metric": "net_revenue_retention_pct", "value": "143", "status": "reported", "source_labels": ["SRC-CUSTOMER-DOC"]},
    {"metric": "tam_usd", "value": "4600000000", "status": "estimated", "source_labels": ["SRC-MARKET-EST"]},
    {"metric": "founder_voting_control_pct", "value": "70", "status": "reported", "source_labels": ["SRC-CAP-TABLE"]},
    # Deliberately not recorded (left outstanding): logo_churn_pct,
    # market_growth_pct, competitor_count, independent_board_seats,
    # audit_status, reporting_cadence -- the packet never states them.
]

assumptions = [
    "Currency: figures are entered in raw INR (1 crore = 10,000,000); the "
    "schedule's USD unit label was not changed for this case, since only "
    "digits are stored.",
    "Net revenue retention (143%) is based on roughly 11 months of "
    "commercial selling, per the packet's own caveat.",
    "Addressable market uses the $4.6B 'investment intelligence segment' "
    "figure, the narrower of two TAM figures in the packet; a broader 'AI "
    "governance and reasoning' market of $18B is also cited but is not the "
    "addressable-segment figure the schedule asks for.",
    "Audit status, reporting cadence, logo churn, market growth rate, "
    "independent board seats and competitor count are left blank: the "
    "packet never states them, and only describes competitor categories "
    "rather than naming a discrete count.",
]

flagged_conflicts = [
    {
        "metric": "arr_usd",
        "note": (
            "An internal finance spreadsheet states ARR of INR 21.7 crore "
            "(217,000,000) as of Aug 2026; finance attributes the gap to "
            "annualized contracted revenue not yet reflected in the "
            "management-reported figure."
        ),
    },
    {
        "metric": "gross_margin_pct",
        "note": (
            "A separate finance document reports 68% gross margin once "
            "model inference and cloud infrastructure costs are included; "
            "management expects the reported figure to hold once inference "
            "is optimized."
        ),
    },
    {
        "metric": "net_burn_monthly_usd",
        "note": (
            "The finance model assumes INR 2.1 crore/month (21,000,000) "
            "burn following planned post-Series-A hiring, against the INR "
            "1.4 crore/month currently reported."
        ),
    },
    {
        "metric": "founder_voting_control_pct",
        "note": (
            "Founders are described elsewhere as owning 68% combined, "
            "which does not match the 70% implied by summing the itemized "
            "cap table (Founder A 46% + Founder B 24%); the packet also "
            "does not distinguish equity ownership from voting control."
        ),
    },
]

detail = post(
    f"/api/cases/{case_id}/material",
    {
        "sources": sources,
        "figures": figures,
        "assumptions": assumptions,
        "flagged_conflicts": flagged_conflicts,
    },
)
print(f"material saved: {len(detail['case']['figures'])} figures, "
      f"{len(detail['case']['sources'])} sources, "
      f"{len(detail['case']['flagged_conflicts'])} flagged conflicts")

# 3. Request the institutional judgment.
result = post(f"/api/cases/{case_id}/analysis", {})
judgment = result["judgment"]
print(
    f"judgment: {judgment['recommendation']} / {judgment['confidence']} "
    f"confidence -- {judgment['judgment_id']}"
)
print(f"record_digest={judgment['record_digest']}")
print(f"material_digest={judgment['material_digest']}")
