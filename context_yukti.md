# context_yukti.md

A deep-context reference for YUKTI: what it is, how the current system is built,
the state of every major component, the open contradictions, and the forks that
decide where it goes next.

Written 2026-09-07. This is a synthesis document, not a spec. Where it states a
constant or a rule, the source of truth is the code named in that section; check
against it before relying on a number.

---

## 1. What YUKTI is

**YUKTI is a company.** Its product goal, held constant across every design
argument:

> Take an institution from messy, incomplete, partly-unreliable evidence to a
> **judgment it can defend later** — to LPs, regulators, an auditor, or its own
> future committee — *faster than doing it by hand, without sacrificing
> auditability.*

"Defensible" has three parts, and every part of the architecture maps to one:

| Requirement | Meaning | What serves it today |
|---|---|---|
| **Provenance** | which facts did we rely on, and where did each come from | source register, evidence spans, `IntakeRecord` |
| **Integrity** | is the analysis we are looking at the analysis that was actually produced | content digests, append-only judgments, projection-from-record |
| **Warrant** | does the conclusion follow, under a stated standard of reasoning | the frozen deterministic kernel pipeline (`choir_prototype`) |

The load-bearing bet is on **warrant**: YUKTI encodes the standard of reasoning
as a *frozen deterministic function*, so "does the conclusion follow" reduces to
"re-run the function and compare digests."

### The thesis (canonical, supplied 2026-08-04; not written anywhere in the repo)

> Organizations do not fail because they lack intelligence. They fail because
> they cannot **institutionalize reasoning**. LLMs produce answers; YUKTI
> produces *institutional judgments* by decomposing reasoning into multiple
> deterministic cognitive kernels that independently analyze evidence before
> synthesis.

YUKTI is explicitly **not** an AI assistant, a workflow-automation tool, or
another multi-agent framework. The standing test for any decision, including
proposals in this document: **"Does this reinforce institutional reasoning?"**
If not, reject it.

### The three names

| Name | What it is | Expansion |
|---|---|---|
| **YUKTI** | the company | (Sanskrit: *yukti* — reasoned method, device, argument) |
| **CHOIR** | the research theory | *Computational Heuristics for Ontological Institutional Reasoning* — **appears in no file in the repo** |
| **DAALE** | the reference reasoning engine | expansion never supplied; do not invent one |

The working engine is `choir_prototype/`. Its own README states "This is not
YUKTI and not DAALE architecture" — it is a frozen research prototype that the
product currently depends on. See §7 and §10 for that tension.

---

## 2. The mechanism, end to end

The full path from a pasted memo to a recorded committee decision. Steps 3 and 7
are the only points a human acts; everything between runs unattended and
deterministically.

```
raw prose
   │  1. read                (intake.py  |  assistant.py — optional model)
   ▼
proposed figures + proposed sources     (each carries the text span it came from)
   │  2. attribute + classify
   ▼
   │  3. HUMAN CONFIRMS       accept / edit / reject each proposal
   ▼
recorded material            (cases.record_material — same route a typed figure takes)
   │  4. FREEZE               (material.compute_material_digest → MaterialSnapshot)
   ▼
material_digest  ══════════ the reproducibility boundary ══════════
   │  5. compose + execute    (analysis.compose_document → vertical_slice.execute_slice)
   ▼
   ├─ translate              domain material → CHOIR IR (evidence, claims, uncertainty)
   ├─ 4 independent kernels   financial_posture · risk_exposure · market_position · governance
   ├─ synthesize             compare kernels, apply decision rules R1–R6
   ▼
reasoning record (05-record.json)  →  record_digest
   │  6. project              (analysis.read_judgment — reads the record back from disk)
   ▼
institutional view           recommendation · per-area confidence · findings · agreements/disagreements
   │  7. HUMAN DECIDES        LedgerEntry binds judgment_id + record_digest + material_digest
   ▼
ledger (append-only)  →  verify_ledger re-resolves both digests on demand
```

### The rubric, as implemented

Source: `choir_prototype/core/synthesizer.py`,
`choir_prototype/domains/investment/{kernels,translator}.py`,
`applications/investment/workspace/diligence.py`.

**Diligence schedule — 15 metrics, 4 review areas.** Every figure the engine
reads is one of these:

- *Financial position* — `arr_usd`, `yoy_growth_pct`, `gross_margin_pct`, `net_burn_monthly_usd`, `cash_usd`
- *Revenue quality and risk* — `top_customer_revenue_pct`, `net_revenue_retention_pct`, `logo_churn_pct`
- *Market* — `tam_usd`, `market_growth_pct`, `competitor_count`
- *Governance* — `founder_voting_control_pct`, `independent_board_seats`, `audit_status`, `reporting_cadence`

**Evidence quality** is derived from the *kind* of the source, never chosen
free-hand:

| Source kind | Evidence quality | Rank |
|---|---|---|
| `audit` | AUDITED | 3 |
| `management`, `interview` | REPORTED | 2 |
| `third_party` | ESTIMATED | 1 |
| `assertion` | ASSERTED | 0 |

**Kernels** (`domains/investment/kernels.py`, fixed dispatch order): four
hand-written threshold functions — `FinancialPostureKernel`,
`RiskExposureKernel`, `MarketPositionKernel`, `GovernanceKernel`. Each reads only
its own predicates from the IR, cites only IR ids, and emits findings with a
stance (`supports` / `opposes` / `conditional` / `neutral`) on a topic, plus a
confidence band and a coverage figure. No kernel sees the thesis, the requested
decision, or the other kernels' output.

**Per-kernel confidence band**: HIGH / MODERATE / LOW / INSUFFICIENT (weights
3 / 2 / 1 / 0), a function of evidence quality, coverage, and internal
contradiction. A kernel whose coverage is below the floor is dropped as
*unusable*.

**Synthesis** (`synthesizer.py`) — compares the usable kernels and applies, in
order, recording every rule whether or not it fires:

| Rule | Fires when | Outcome |
|---|---|---|
| **R1** insufficient-basis | usable kernels < `MINIMUM_USABLE_KERNELS` (2) | INSUFFICIENT_BASIS |
| **R2** live-disagreement | any topic has opposing stances **and** support−oppose margin < `DOMINANCE_MARGIN` (3) | CONTESTED |
| **R3** proceed-with-conditions | support > oppose **and** ≥1 conditional finding | PROCEED_WITH_CONDITIONS |
| **R4** proceed | support > oppose | PROCEED |
| **R5** decline | oppose > support | DECLINE |
| **R6** balanced-fallback | support == oppose | CONTESTED |

Findings are weighted by band (a HIGH finding outweighs a LOW one; INSUFFICIENT
kernels contribute 0).

**Institutional confidence = the weakest usable review area** (min, not mean).
One thin area caps the whole judgment. `CONTESTED` and `INSUFFICIENT_BASIS` are
first-class outcomes, not failure states.

### The commitments (what the architecture promises and how it is enforced)

| ID | Commitment | Enforcement |
|---|---|---|
| **E9** | An explanation is a *projection of the trace*, never regenerated | the view is built by reading `05-record.json` back from disk (`analysis.read_judgment`); it cannot display a conclusion the record does not contain |
| **E2** | Confidence is *derived*, never authored | no code path accepts a typed confidence; it is computed in the synthesizer |
| **X4** | Kernels cite only IR ids | kernel findings carry `evidence_ids`; the workspace and experiments assert no raw claim text leaks |
| **A6** | Five decision rules, evaluated in fixed order, all recorded | `synthesizer._decide` appends a `RuleEvaluation` for every rule, fired or not |

### The freeze

`choir_prototype/freeze.py` pins every file in the package: Markdown by content
hash, Python by *normalised-AST* hash (so formatting-only edits survive but logic
changes trip `--frozen`). `.gitattributes` (`* text=auto eol=lf`) is required or
a Windows checkout rewrites line endings and `--frozen` falsely reports
MODIFIED. **`python -m choir_prototype --frozen` currently exits 0.**

---

## 3. Object model

`applications/investment/workspace/cases.py`. One JSON file per case under
`reports/workspace/<case-id>/`; no database.

| Object | Role | Notes |
|---|---|---|
| `Case` | one institutional decision and everything assembled against it | status is *derived* from the record (Draft → Material assembled → Analysed → Decided) |
| `Source` | one document in the register | `(label, origin, kind)`; `kind` drives evidence quality |
| `Figure` | one recorded schedule figure | `(metric, value, status, source_labels)`; **this is the scalar the engine reasons over** |
| `FlaggedConflict` | a contradiction the team found between sources | hand-entered |
| `IntakeRecord` | *how* a figure came to be recorded — the prose it was read from | carries `quote`, `basis`, `edited`; **deliberately outside `material_payload`** so a typed figure and the same figure lifted from a memo hash identically |
| `MaterialSnapshot` | immutable material identity at a point in time | `material_digest` at full institutional fidelity, including vocabulary the engine flattens; order-sensitive |
| `JudgmentRecord` | one analysis, kept forever | `record_digest` + `material_digest` + `snapshot_id`; superseded, never replaced |
| `LedgerEntry` | one committee decision against a judgment | binds `judgment_id` + both digests; `rationale` is a single free-text string |

**The known weak spot in the object model:** `Figure` assumes every material
fact is a *scalar keyed to a predefined metric*. Relations ("the CEO and CFO are
siblings"), qualifications ("the auditor issued a going-concern opinion"),
narrative shape, and definitional disputes have no representation and are
silently dropped at intake. The `LedgerEntry.rationale` string is the least
structured object in the system despite being the single most important artifact
for the product goal. See §10.

---

## 4. Memory / identity model

Source: `applications/investment/workspace/material.py`, `cases.py`;
`docs/architecture/DECISION-004`, `DECISION-006`.

- **Append-only.** Judgments are never overwritten. A new analysis *supersedes*
  the current one and leaves it fully resolvable on disk.
- **Two digests, deliberately not collapsed.**
  - `record_digest` — content hash of the reasoning record. Proves two runs
    *reasoned identically*.
  - `material_digest` — hash of the recorded material at full fidelity. Proves
    two runs *read the same material*. **Strictly finer than `record_digest`**:
    the engine flattens distinctions the institution records (e.g. `reported`
    vs `estimated` both collapse to `LIKELY` in the translator), so two
    materially different packs can produce one reasoning record.
- **Supersession keys on material, not reasoning.** A change to what the
  institution assembled creates a new judgment *even when the conclusion is
  unchanged* — institutional history records deliberation over material, not
  only changes of mind.
- **Forward-only binding.** A decision binds to the exact judgment it was taken
  against. Re-analysing the case never touches an earlier decision.
- **`verify_ledger`** re-resolves every decision to artifacts on disk carrying
  its cited digests, on two axes (reasoning identity, material identity). Both
  must hold or the decision reads as unverifiable.

---

## 5. Repository map

| Path | What it is | State |
|---|---|---|
| `choir_prototype/` | the frozen deterministic engine (v0.1, ~4,200 lines, stdlib only, "No LLM call anywhere") | **frozen, hash-pinned, `--frozen` green** |
| `applications/investment/vertical_slice/` | document → engine bridge (`execute_slice`, `read_document`, `DOCUMENT_VERSION`); carries the Orbital Logistics worked example | stable |
| `applications/investment/workspace/` | **the product surface** — server, chat UI, record UI, intake, assistant, explain, cases, analysis, material, diligence | **active development** |
| `applications/investment/prototype_risk_rik/` | legacy reasoning path that calls the OpenAI Responses API | **superseded by DECISION-001; retirement not yet scheduled** |
| `daale/` | conformance harness + execution / D-Core layer + ontology | real code now (~2,600 lines conformance+execution); canonical definition still open |
| `daale/DAALE/DAALE/D-Core/`, `.../R-Fabric/` | a nested working tree dumped into the repo | **staging cruft — dozens of staged new files, not integrated** |
| `experiments/rubric_reproduction/` | the experiment that decides the central fork (see §9) | scaffold complete, at the pre-run audit gate |
| `experiments/messy_intake/` | messy-prose → same-verdict harness + the reader/reasoning freeze boundary | built 2026-09-07; reasoning variance proven 0 |
| `choir/` | research notes, specifications, ontology, proposals | see §10 item 3 — specs are 0-byte; `choir/research/phase-*/` holds the real content |
| `docs/architecture/` | decision notes DECISION-001 … 008 | the governance record (see §8) |
| `website/` | marketing site — separate track | homepage rebuilt Sept 2026 (gold-on-black); archive pages on old design |
| `yukti.py` / `yukti.cmd` / `yukti.sh` | zero-arg launcher for the workspace app | loads `.env`, checks Python ≥ 3.12, delegates to `server.main` |
| `bject {` (repo root) | a truncated file from a botched shell redirect | **delete it** |

---

## 6. Component state — detail

### `choir_prototype/` — the engine
- **Status:** frozen v0.1. `--frozen` exits 0. Stdlib-only, deterministic.
- **What it does:** `execute(packet, DOMAIN)` → translate → 4 kernels → synthesize → `(result, synthesis)`; `05-record.json` is the archival record.
- **Constraints:** every file hash-pinned; prose corrections go in the root `README.md`, never in-package. `FROZEN.md` §6 is stale on purpose. V0.2 may change what `FROZEN.md` lists as mutable.
- **Risk it carries:** the kernels are hand-written thresholds. Whether they encode a *defensible* standard or merely a *plausible-looking* one is unvalidated. This is the project's central open question.

### `applications/investment/workspace/` — the product
- **`server.py`** — stdlib HTTP server; `argparse` (`--host/--port/--no-browser/--check-assist`); routes for worked-example, read, accept, ask. Browser auto-open in a `Timer` thread. Stable.
- **`cases.py`** — the JSON store; `open_case`, `record_material`, `accept_intake`, `append_judgment`, `append_ledger_entry`, `verify_ledger` support. Backward-compatible loading (every field added after the first cases uses `.get` with a default). Stable.
- **`analysis.py`** — the *only* module that touches the engine. `compose_document` (deliberately drops owner/date/thesis/requested-decision so metadata cannot move a conclusion), `request_judgment`, `read_judgment`, `verify_ledger`. Stable; covered by `test_judgment_matches_the_engine_directly` and `test_case_metadata_does_not_reach_the_engine`.
- **`material.py`** — `compute_material_digest`, `MaterialSnapshot`, `next_snapshot`. Implemented per DECISION-006. Stable.
- **`diligence.py`** — the 15-metric `SCHEDULE`, `FIGURE_STATUSES`, review-area / topic relabelling, `outstanding()`. Stable.
- **`intake.py`** — deterministic keyword reader: prose → `Proposal`s, one per metric, each with its text span. **Negation-aware source recognition added 2026-09-07** (`_mention_standing` classifies each source mention present / absent / unknown; only *present* registers a source). Reads 15/15 on clean prose, 4–7/15 on genuinely messy prose — this is the known ceiling of the no-model path.
- **`assistant.py`** — the **optional** language-model layer. Off unless `ANTHROPIC_API_KEY` is set. Two jobs only: (1) read prose into `Proposal`s (better than the keyword reader on messy text — 15/15 where the keyword reader gets 4); (2) rephrase an answer `explain.py` already computed. Two enforced anti-fabrication guards: a proposed quote must be a literal substring of the text; a phrased answer may introduce no number absent from the record. Wired to Claude Fable 5.1 via the Experiential Labs gateway (`YUKTI_ASSIST_BASE_URL`). **Model reads are non-deterministic** — repeated reads of the same memo produce different evidence records (measured: memo 2 gave 4 distinct records in 5 reads, on `audit_status` and `reporting_cadence`).
- **`explain.py`** — record-projected Q&A. Classifies intent, answers from the judgment record only (`_recommendation`, `_why`, `_confidence`, `_conditions`, `_gaps`, `_contested`, `_evidence`, `_improve`, `_status`, `_decision`, `_provenance`). Weakest-area lookup is `max` over band order. Stable.
- **`ui/`** — `index.html` is an LLM-style chat surface (Harvey-AI-inspired: one chat bar, proposal cards with Accept/Edit/Reject, verdict card, guided flows); `record.html` is the older workspace shell; `chat.js` / `chat.css` / `app.js`. Functional prototype.
- **Tests:** the workspace suite passes (part of the 310-test full run). `--frozen` intact; conformance holds; ruff clean outside the `daale/DAALE/` staging dump.

### `daale/`
- **Status:** has real code now — a conformance harness (`conformance/commitments.py`, `classification.py`, `lock.py`, `report.py`), an execution / D-Core layer (`execution/{dcore,commit,contract,identity,state,trace,dependencies}.py`), and a populated ontology (`ontology/{base,confidence,contradiction,decision,evidence,proposal,relationships}.py`). `daale.cli doctor` passes.
- **Open:** DECISION-005 — *the canonical definition of DAALE* — is **still not accepted**. Whether DAALE is "the reference reasoning engine" that reasons, or a conformance/execution wrapper around `choir_prototype`, is unresolved. The Aug-2026 contradiction "DAALE contains no reasoning" is *partly* addressed (there is code) but not *resolved* (its role is undefined).
- `daale/DAALE/DAALE/D-Core/` + `R-Fabric/` — a separate nested working tree that was dumped in and staged. Not wired to anything. Treat as cruft pending a decision to integrate or remove.

### `experiments/rubric_reproduction/`
- **Purpose:** answer the central fork — *can a single LLM, given the same investment rubric the deterministic kernels use, reproduce the frozen pipeline's outputs?* If yes, the deterministic machinery may be unnecessary. If no, the machinery is doing real work.
- **State:** scaffold complete — `rubric.md` (literal transcription of the kernel logic with a machine-readable constants block), `ground_truth.py` (derives expected outputs from the live frozen implementation, not copied values), `build_prompt.py`, `compare.py` (tiered match / partial / divergence + an X4 leakage check), `run.py` (stops at "prompts generated; awaiting external model responses"), tests. Prompts generated for two cases (`orbital-series-b`, `northwind-seed`). **Never run against an LLM.** It was left at the pre-experiment audit gate; the verdict recorded there was "READY FOR L-LO" pending a final operator check.
- **Design constraint honoured:** the experiment is not optimised to make YUKTI win. A faithful reproduction of the current implementation was preserved even where it makes the control unusually strong.

### `experiments/messy_intake/` (built 2026-09-07)
- **`evidence.py`** — the reader/reasoning freeze boundary. `EvidenceRecord` = canonical, hashable reader output; its `digest` covers only what reaches the engine (sources + `metric/value/status/source_label`) and excludes quotes, reader name, timestamp — mirroring `material_digest`'s exclusion of provenance. `replay()` feeds a frozen record through the engine with no prose consulted; `replay_is_stable(times=N)` asserts one `record_digest` and one verdict across N replays.
- **`memos.py`** — five messy memos, each paired with a sealed verdict computed from the frozen engine: 1-control (worked example rewritten messily — must reproduce `Proceed With Conditions / Low`), 2-strong (`Proceed / High`), 3-weak (`Decline / Low`), 4-thin (`Insufficient Basis`), 5-contested (`Contested / Moderate`). `--repeat N` probes reading variance.
- **Findings:** reasoning variance = **0** across all memos and readers (8–10 replays each) — the engine is a pure function of the frozen record. Model reading variance is real and localised (memo 2's High/Moderate flip is a two-field reading wobble on `audit_status` / `reporting_cadence`, not an engine defect). The negation fix is verified: "no cap table" no longer registers a cap-table source.

### `website/`
- Homepage rebuilt Sept 2026 to a gold-on-black institutional design from Piyush's mockups; three self-contained files (`index.html`, `src/styles/home.css`, `src/scripts/home.js`), no web fonts. Archive pages (`documents.html`, `document.html`, `judgment.html`, `tokens.html`) still on the old "blueprint editorial" design and out of scope. Open item: the waitlist submit URL (`ACCESS_URL` in `home.js`) is still empty.

---

## 7. Governance and decision notes

`docs/architecture/`. The project's rule: no implementation without an approved
decision note (template in `docs/architecture/README.md`). Prefer writing a note
over silently choosing.

| Note | Subject | Status |
|---|---|---|
| DECISION-001 | reasoning execution substrate | **Approved 2026-08-04** — deterministic kernels; the OpenAI path is legacy |
| DECISION-002 | document intake for the vertical slice | **Approved 2026-08-06, broadened** — documents may *represent* packets, not *interpret* them; prose+extraction was declined here |
| DECISION-003 | product application architecture | **Approved 2026-08-06** |
| DECISION-004 | judgment supersession | **Approved 2026-08-06, implemented** |
| DECISION-005 | canonical definition of DAALE | **Open. Not accepted.** |
| DECISION-006 | material snapshot layer | **Approved 2026-08-06, implemented** |
| DECISION-007 | candidate escalation rule | **Approved 2026-08-14** (DAALE v0 closure) |
| DECISION-008 | prose intake by confirmed proposal | **Proposed. Not accepted.** — this is the governance question hanging over the entire workspace intake path and the `assistant.py` model layer |

**DECISION-008 is the one to resolve next.** The workspace already implements
"model proposes → human confirms → figure enters by the normal route." It runs,
it is tested, and it is *not yet sanctioned*. Until DECISION-008 is ruled on,
the conversational surface and the model layer are ahead of governance.

---

## 8. Open contradictions and risks

Carried forward from the 2026-08-04 repo reading and this conversation's
analysis. Each is an open question, not a bug to fix unilaterally.

1. **The kernels may be "proving the wrong thing."** The architecture makes
   "does the conclusion follow" reproducible, but reproducibility of an
   arbitrary standard is not a defensible standard. If a prospect's analyst
   asks "why is `top_customer_revenue_pct > 35%` the line?", the honest answer
   today is "a threshold we chose." `experiments/rubric_reproduction` exists to
   test whether the kernels track expert judgment. **Until it runs, the moat is
   unproven.**

2. **The architecture froze the easy part.** Threshold arithmetic over 15 clean
   numbers is not the hard part of institutional judgment. The hard parts —
   choosing which dimensions matter for *this* deal, calibrating trust in each
   source, deciding which contradictions are load-bearing, catching a wrong
   frame — are all resolved in the *unaudited human pre-step* before
   `record_material`. The bit-perfect audit trail wraps the 10% that did not
   need it.

3. **Intake is a single point of epistemic failure treated as a thin
   membrane.** Everything downstream of `record_material` is audited; everything
   upstream (model proposes, human accepts) is where all real error enters, and
   it gets one `IntakeRecord` with a quote and an `edited` bool. No second
   reviewer, no independent confirmation, no record of what the human
   considered and rejected. The chat UI actively encourages fast click-through
   acceptance.

4. **The memory model records states, not deliberation.** Append-only judgments
   capture what the *machine* concluded at each material state. They do not
   capture the committee's reasoning — objections raised, who dissented, "we
   proceeded despite CONTESTED because of side knowledge about the founder."
   The decision, the product's whole point, is a free-text field.

5. **`prototype_risk_rik` still calls OpenAI.** DECISION-001 made deterministic
   kernels the substrate and marked this path legacy; retirement is still
   unscheduled. Two prototypes embodying opposite theories of "what a kernel
   is" still coexist.

6. **`choir/specifications/SPEC-*.md`, `choir/ontology/*.md`,
   `choir/proposals/` are 0-byte.** The real research content is in
   `choir/research/phase-*/`. The governance rule ("no implementation without
   an approved spec") is either dead or the prototypes are out of governance.

7. **DAALE's role is undefined** (DECISION-005 open), and a nested
   `daale/DAALE/DAALE/` working tree is staged but unintegrated.

8. **`MANIFESTO.md` is a second-person AI prompt, not a manifesto.** Left alone
   deliberately — it is load-bearing and rewriting it is Piyush's call.

---

## 9. Where it is headed

### The fork that decides everything

`experiments/rubric_reproduction` has one job: does a single LLM with the
written rubric reproduce the frozen pipeline's verdicts?

- **If yes** — the deterministic machinery is not pulling its weight on
  *warrant*. Keep it for reproducibility and as a research object, but the
  product's differentiation has to come from provenance and integrity, not from
  "the verdict is computed."
- **If no** — the kernels are doing real work that an LLM cannot replicate
  faithfully, and the frozen-verdict architecture is validated. Invest in
  making that determinism *visible and useful* rather than merely virtuous.

Everything below is downstream of this result.

### Near-term product moves (architecture-safe — no change to CHOIR, the IR, the
kernels, the commitments, or the material layer)

Ranked. These exploit properties the architecture already has but the product
does not surface.

1. **Defend the rubric.** Make `rubric.md` a first-class, versioned,
   rationale-per-threshold artifact — auditable by a serious evaluator (under
   NDA if needed). Do *not* publish it publicly or claim "standard" status until
   the reproduction experiment shows it tracks expert judgment. This is the
   prerequisite for every other move having credibility.
2. **Signed process-integrity bundle.** Export `{frozen artifacts + record_digest
   + material_digest + timestamp}`, signed. The claim is scoped: "this is the
   judgment the engine produced from this exact material, and here is how to
   re-derive the identical digest." A process claim, not a correctness claim —
   so it can ship *now*, independent of move 1.
3. **Exhaustive judgment changelog.** Between judgment N and N+1: every figure
   that changed, every finding that changed stance, every confidence that
   moved, whether the recommendation changed. **No causal "because"** — that
   would be regenerated reasoning and would break E9. Pure set-difference over
   two records. Uniquely possible because of supersession + material snapshots
   + determinism.
4. **Trace as the audit layer.** Keep the reasoning trace navigable (click any
   clause → finding → IR claims → figures → source spans; the data is all in
   the record). Position the memo as the deliverable and the trace as the
   dispute-resolution layer — not the headline.
5. **Honest `INSUFFICIENT_BASIS` / `CONTESTED`.** When the engine withholds a
   verdict, render the missing schedule items grouped by review area and, for
   CONTESTED, the opposing findings verbatim with their evidence. Exhaustive,
   **unranked** — ranking by "impact" would require imputing values for absent
   figures.

**Explicitly do not:** grow the model's surface. Adding phrasing personality,
chat, or any model role beyond "propose figures from prose" makes YUKTI feel
like the tools it is structurally unlike. Harden the one model role
(determinism, a calibration record of model-proposed vs human-corrected
figures, the guardrails); add no new ones.

### The deeper rebuild (only if the reproduction experiment says the kernels do
not track expert judgment)

If the frozen verdict is "reproducibility of possibly-wrong," the product goal
(defensibility) is better served by making the machine a **conformance checker**
rather than a verdict producer. The converged shape of that rebuild:

- **Object model → a typed evidence graph.** `Measurement` / `Assertion` /
  `Relation` / `Qualification` nodes; analyst-authored `Claim`s with
  support/contradiction edges to evidence; `ReviewDimension`s marked
  load-bearing *per case*. Degenerates cleanly to today's 15-metric schedule
  when all evidence is measurements.
- **Workflow → frame → propose → challenge → confirm → author → check.** A
  cheap up-front framing step (which dimensions are load-bearing here, what is
  the one deal-specific dimension) captures the decision the current system
  leaves implicit. A deterministic *challenge pass* (unsupported claim,
  uncovered dimension, contradiction with higher-quality evidence) plus a human
  review queue attacks the intake single-point-of-failure. The **human authors
  the judgment**, mapping each conclusion to the standard; the engine returns
  conforms / fails, not a recommendation.
- **Rubric → a documented reasoning standard**, versioned, rationale per rule,
  mostly *procedural* ("every load-bearing dimension must be evidenced",
  "contradictions resolved or flagged"). Residual numeric thresholds are
  committee-owned defaults, visible and attributable — not system constants.
- **Memory → the deliberation graph** is the record: evidence + claims +
  challenges + resolutions + authored judgment + decision + structured dissent
  `(objection, raised_by, disposition)`. `evidence_digest` + `record_digest`
  over the graph; supersession keys on evidence change.

**Survives from the current architecture regardless of the fork:** append-only +
digests + supersession; projection-from-record (E9); confidence derived not
authored (E2); the model proposes, never authors evidence. The framing,
trust-calibration, and materiality decisions becoming first-class recorded
objects is settled independent of the fork — leaving them in an unaudited
pre-step is the current architecture's clearest misrepresentation of the
problem.

---

## 10. How to run it

```bash
# the product
python yukti.py                         # launches the workspace app, opens a browser
python yukti.py --check-assist          # verify the optional model wiring

# the engine
python -m choir_prototype --frozen      # must exit 0
python -m choir_prototype               # run the worked example

# tests (venv interpreter has pytest; system interpreter has anthropic)
./.venv/Scripts/python.exe -m pytest -q                 # 310 tests, all passing
YUKTI_ASSIST=off ./.venv/Scripts/python.exe -m pytest -q

# the experiments
./.venv/Scripts/python.exe -m pytest experiments/ -q
python -m experiments.messy_intake.memos                # keyword reader
python -m experiments.messy_intake.memos --model        # model reader (needs a key)
python -m experiments.messy_intake.memos --model --repeat 5   # reading-variance probe

# conformance
python -m daale.cli doctor
```

**Configuration** (`.env` at repo root, gitignored, append-only — it holds a
secret):

```
ANTHROPIC_API_KEY=xpl_...                    # Experiential Labs key
YUKTI_ASSIST_BASE_URL=https://api.experientiallabs.ai
YUKTI_ASSIST_MODEL=claude-fable-5
YUKTI_ASSIST=off                             # kill switch
```

The model layer sends diligence material to the Experiential Labs gateway. The
workspace is fully functional with `YUKTI_ASSIST=off` — the deterministic reader
and record projection are the product, not the fallback.

---

## 11. One-paragraph summary

YUKTI turns messy investment evidence into an auditable institutional judgment by
freezing the *reasoning* — a deterministic 4-kernel pipeline (`choir_prototype`,
hash-pinned, stdlib-only) — so that "does the conclusion follow" reduces to a
digest comparison, and wrapping it in provenance and integrity machinery
(evidence spans, material snapshots, append-only supersession, projection from
the record). The product surface (`applications/investment/workspace/`) is a
chat UI where a language model proposes figures from prose and a human confirms
each one before it enters material. The central unproven claim is that the
hand-written kernels encode a *defensible* standard rather than a plausible one;
`experiments/rubric_reproduction` is built to test it and has not yet been run.
The next governance decision is DECISION-008 (sanction the model-proposes /
human-confirms intake path, which already ships). The clearest architectural
weakness is that framing, trust calibration, and materiality — the hard parts —
happen in an unaudited human pre-step, and the committee's own decision is a
free-text field.
