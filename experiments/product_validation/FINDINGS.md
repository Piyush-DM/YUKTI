# Product validation run — `yukti-systems` (2026-09-16)

One observed, reproducible run of the shipped workspace product
(`applications/investment/workspace`) against a realistic, deliberately messy
Series A packet. This documents what happened — it is not a rubric score and
does not feed `experiments/rubric_design/`.

## Input packet

`yukti_systems_series_a_packet.txt` (this directory) — a fictional/synthetic
Series A diligence packet for "YUKTI Systems Pvt. Ltd.," built to contain the
kind of internal self-contradiction a real diligence pack has: two different
ARR figures (₹18.4cr vs ₹21.7cr), two different gross margins (81% vs 68%),
two different burn figures (₹1.4cr vs ₹2.1cr/month), a cap-table sum that
doesn't match a prose claim (70% vs "68% combined"), and several schedule
items the packet simply never states.

## How the run was produced

1. `python yukti.py --no-browser` — local server, `http://127.0.0.1:8770`.
2. `python build_yukti_systems_case.py` (this directory) — opens the case and
   posts the material below through the real `/api/cases` and
   `/api/cases/<id>/material` endpoints (the same ones the browser UI calls).
3. `POST /api/cases/yukti-systems/analysis` — requests the judgment.

The figure-by-figure mapping from packet prose to the fixed 15-item schedule
(`applications/investment/workspace/diligence.py::SCHEDULE`) was done by
hand, not by the prose-intake reader — this run exercises the engine and the
Material/Judgment/Audit surfaces, not the intake readers.

## Material admitted to the engine — 9 of 15 figures

| Metric | Value | Standing | Source |
|---|---|---|---|
| Annual recurring revenue | ₹18.4cr (184,000,000) | Reported | SRC-FIN-SUMMARY |
| Year-over-year growth | 490% | Estimated | SRC-FIN-SUMMARY |
| Gross margin | 81% | Reported | SRC-FIN-SUMMARY |
| Net monthly burn | ₹1.4cr (14,000,000) | Reported | SRC-FIN-SUMMARY |
| Cash on hand | ₹9.7cr (97,000,000) | Reported | SRC-FIN-SUMMARY |
| Largest customer share of revenue | 19% | Reported | SRC-CUSTOMER-DOC |
| Net revenue retention | 143% | Reported | SRC-CUSTOMER-DOC |
| Addressable market | $4.6B (4,600,000,000) | Estimated | SRC-MARKET-EST |
| Founder voting control | 70% | Reported | SRC-CAP-TABLE |

**4 registered sources**, all `management` standing — nothing in this packet
is independently audited: SRC-FIN-SUMMARY, SRC-CUSTOMER-DOC, SRC-MARKET-EST,
SRC-CAP-TABLE (origins in `build_yukti_systems_case.py`).

**6 schedule items left blank, deliberately** — the packet never states them:
logo churn, market growth rate, competitors identified (only categories are
named, not a discrete count), independent board seats, audit status,
reporting cadence.

**4 flagged conflicts** (recorded, not silently resolved):
- `arr_usd` — a separate internal spreadsheet states ₹21.7cr.
- `gross_margin_pct` — a separate finance document states 68% once inference/cloud costs are included.
- `net_burn_monthly_usd` — the finance model assumes ₹2.1cr/month post-hiring.
- `founder_voting_control_pct` — the packet elsewhere states founders own "68% combined," which doesn't match the 70% the itemized cap table sums to.

## Resulting judgment

**Proceed With Conditions — Low confidence** (`JUDGMENT-001`).

- Rationale: "2 of 4 review areas reached a usable confidence band. Weighted
  support 4 against opposition 1, with 2 conditional finding(s)."
- Financial position: Low confidence, "3 contradicted claim(s) in scope" —
  the three flagged financial conflicts (ARR, gross margin, net burn) surface
  here as contested claims, not as a resolved pick.
- Revenue quality and risk: Low, 2 contradicted claims in scope; findings
  otherwise support (concentration 19%, NRR 143% both read favorably).
- Market: **Insufficient** — only 1 of 3 expected inputs present (TAM only).
- Governance: **Insufficient** — only 1 of 4 expected inputs present (founder
  voting control only); audit status and reporting cadence explicitly named
  as not stated.
- Agreement: Financial position and Revenue quality independently agree
  revenue quality is healthy (81% margin, 143% NRR) without seeing each
  other's work.
- No topic-level disagreements — each flagged conflict reached the engine as
  a single contested value, not as two competing findings.

### Key derived finding

**Runway: 6.9 months** (cash ₹9.7cr ÷ burn ₹1.4cr/month), against an
18-month comfort floor — computed by the engine from the recorded figures,
not stated anywhere in the packet. The packet's own narrative claims
"approximately 30 months of runway" from the Series A; that figure only
holds if the finance model's *projected* post-hiring burn (₹2.1cr/month,
itself the flagged conflict) is used instead of the currently reported
figure, and even then does not reconcile cleanly. This is the sharpest gap
between what the packet asserts and what its own recorded figures support.

### Conditions produced

- Capital efficiency: annualised burn is 0.91x ARR against a 0.50x
  efficient / 1.00x unsustainable threshold.
- Governance quality: founders retain 70% voting control.

## Persisted record

`reports/workspace/yukti-systems/judgments/JUDGMENT-001/` (gitignored, not
committed — generated output):

- `record_digest` (SHA-256, the reasoning): `90d1eda3ee3c41adf79a35079485ebae90b1d514fcb309c764acf8247732b22e`
- `material_digest` (SHA-256, what it was formed from): `739c7c2efb33ce3c7cea155d7e98e1ac21e3bbdde78d776ef282234b14e416ad`
- `snapshot_id`: `MATERIAL-001` (version 1)

`05-record.json` in that directory is the full canonical record;
`06-report.txt` is the human-readable full reasoning trace.
