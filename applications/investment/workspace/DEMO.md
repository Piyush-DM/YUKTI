# YUKTI — 30-second demo path

A deterministic click sequence. Follow it exactly and the numbers below will
match, every time, on any machine — which is itself the thing being
demonstrated. The engine has no clock, no randomness and no network, so the
same material always reaches the same conclusion.

Run it once before the room fills.

---

## A correction to the requested script

The script as briefed opens **"the Northstar case"**. Do not demo Northstar.

`Northstar Grid Infrastructure Series C` is fixture data in
`applications/investment/prototype-ui/` — the product prototype that
`DECISION-003` superseded and that is scheduled for retirement. Its analysis is
a hand-written mock. `test_user_cases_cannot_attach_northstar_fixture_analysis`
exists specifically to stop that fixture leaking into real cases.

Demoing it would mean showing an investor a mock while describing it as the
engine. The reference case below is the real one: it runs the frozen CHOIR
pipeline end to end and every figure on screen comes back out of the persisted
record.

**Demo case: Orbital Logistics — Series B.**

---

## Before they walk in

**1. Start the server.**

```bash
python -m applications.investment.workspace
```

Open `http://localhost:8770`.

**2. Put the demo case in its starting state.** The live path below begins at a
case that has material on file and *no judgment yet* — that is what makes "Run
analysis" the first thing you touch.

- **Open case** → fill six fields. Anything sensible; suggested:
  - Company `Orbital Logistics`
  - Stage `Series B`
  - Sector `Supply chain software`
  - Case owner `A. Rao`
  - Requested decision `Approve a $12M Series B allocation`
  - Thesis — one line, your own words.
- **Open case** to save. You land on **Material**.
- Click **Use reference material**, then **Save material**.
- Stop. **Do not click into Judgment.** The case must sit at status
  *Material assembled*.

**3. Leave the browser on the case register, nothing selected.**

If you have run the demo before, the case will already carry a judgment.
Either open a second case for the live run, or delete
`reports/workspace/<case-id>/` and repeat step 2.

---

## The live path — six beats, about 30 seconds

| # | Action | What to say while it happens |
|---|---|---|
| 1 | Click **Orbital Logistics — Series B** in the register | "One case is one decision the committee has to make." |
| 2 | **Judgment** tab → **Request institutional judgment** | "The material is on file. Nothing has been concluded yet." |
| 3 | The **Executing** panel appears immediately | "It is running. Notice there is no percentage — we can't see inside the run, so we don't draw a number nobody measured." |
| 4 | Stages land one at a time, then the decision | "Now it's back, and each line is an artifact it actually produced." |
| 5 | Scroll to **Where the review areas disagree (1)** | "Four review areas that cannot see each other's work. One of them disagrees, and we surface it rather than average it away." |
| 6 | Scroll to **Evidence references (5)** | "Every source the judgment cited, and the standing it was recorded under." |

Beats 5 and 6 are **scrolls, not clicks** — both sections are always visible.
A board packet does not hide its evidence behind a disclosure control. Say so
if anyone asks why they aren't collapsed.

---

## The numbers, so you know instantly if something is wrong

Deterministic for the reference material. If any of these differ, something
changed — stop and check rather than talking over it.

| Where | Expected |
|---|---|
| Headline | **Proceed With Conditions** |
| Institutional confidence | **Low** |
| Conditions | **5** |
| Where the review areas disagree | **1** |
| Independent agreement | **1** |
| Evidence references | **5** |
| Execution record | **6 artifacts** |
| Material | **MATERIAL-001 (v1)** |
| Record digest | begins **`e5524640`** |

Both digests are for the reference material exactly as shipped, on a case
opened fresh. Verified by walking this path end to end rather than by reading
it off an older run — an earlier draft of this file quoted `9ba1d434`, which is
the digest of a *development* case whose material had since been edited. If
yours differs, your material differs; that is the mechanism working, not a
fault.

**Limited by** reads:

> 1 unresolved topic disagreement(s); weakest contributing review area is
> Market (weakest evidence is estimated (SRC-MARKET))

---

## The two lines worth landing

**On the execution record.** "Every one of those is a real artifact with a
real identifier. If two of us run this case, we get the same digest — and if
we don't, one of us has different material, and the digest tells us which."

**On confidence being Low.** This is the strongest moment in the demo and the
easiest to fumble. Low is not a defect — it is the system declining to
overclaim on a thin evidence base, and it names what limited it. Read the
**Limited by** line out loud. A tool that returns "High confidence" on
everything is the thing this product exists to replace.

---

## If something goes wrong

**"Request institutional judgment" is disabled.** The case has no material.
Material tab → Use reference material → Save material.

**The stages appear all at once.** Your machine is set to reduced motion. That
is the accessible path working correctly, not a fault — the staged reveal is
presentation, so it is skipped rather than shortened. Nothing is lost; the
record is identical.

**You showed an older build.** Shouldn't happen — the server sends
`Cache-Control: no-store` precisely so a last-minute change can't be masked by
a cached `app.js`. If you suspect it anyway, hard-reload.

**A second run created a second judgment.** Expected, and worth showing rather
than hiding: re-analysis never overwrites. The previous judgment stays
readable and any decision recorded against it still resolves. Open **Judgment
history** and show it.

**Re-running identical material changed nothing.** Also correct. The engine is
deterministic, so an identical digest means the same conclusion from the same
material, and recording it twice would put an event in institutional history
that never happened.

---

## What not to promise

Say these plainly if asked; each is recorded in the repository and each is
better volunteered than discovered.

- **No authentication.** The workspace attributes decisions to named people
  and has no identity layer beneath it. Local single-user tool today.
- **Concurrent edits overwrite.** Two analysts on one case lose each other's
  work silently.
- **Sources are references, not documents.** Nothing is uploaded, stored or
  parsed. A source is a label, a description and a recorded standing.
- **One domain.** The engine's reference implementation supports investment
  cases. Domain independence is measured (`--audit`, portability 1.00 across
  four domains) but the product is bound to this one.
