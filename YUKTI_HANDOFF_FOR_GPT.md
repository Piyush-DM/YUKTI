# YUKTI — Current-State Technical Handoff

**Audience:** an LLM (GPT) with zero access to prior conversation. Read this to independently
determine the single most valid next technical step toward YUKTI.

**Repo:** `C:\Users\PIYUSH\Desktop\YUKTI`, branch `main`, HEAD `05c777d` ("Add CHOIR research
docs and investment workspace polish", 2026-08-21). **Large uncommitted working tree** — see §6.

**Naming (this vocabulary appears almost nowhere in the repo; it is supplied context):**
- **YUKTI** — the company / the product layer.
- **CHOIR** — the research theory: *Computational Heuristics for Ontological Institutional
  Reasoning*. Frozen at v0.1.
- **DAALE** — the reference reasoning engine / execution substrate. In one independently-built
  working copy it is expanded "Deterministic Adversarial Analytical Logic Engine"; that
  expansion is **not** canonical.

---

## 1. CURRENT STATE

### 1a. What YUKTI does today, end to end

There are **three code areas at very different maturities**, not yet reconciled with each other.
The only thing that runs end-to-end as a "product" is the investment committee workspace:

```
Analyst opens a case in a browser (stdlib HTTP server, port 8770)
  → registers Sources (documents, by reference — nothing is uploaded/ingested)
  → fills a fixed 15-figure "diligence schedule" grouped into 4 "review areas",
     every figure citing a registered source (uncitable figure = rejected at save)
  → clicks "Request judgment"
       → workspace composes a JSON "document" (the deal packet serialised)
       → calls applications/investment/vertical_slice (the reference pipeline)
       → vertical_slice parses doc → InvestmentPacket → CHOIR IR
             → 4 independent deterministic kernels → structured artifacts
             → deterministic synthesizer → recommendation + confidence + conditions
             → renders a report; persists 6 stage artifacts + digests to reports/workspace/<case>/judgments/<id>/
       → workspace reads 05-record.json BACK (never holds live objects) and
         relabels engine prose into institutional language ("kernel" → "review area", etc.)
  → analyst sees: recommendation, confidence band + limiting factor, conditions,
     kernel disagreements, "what was not established", full audit view
  → analyst records a committee decision in the Decision Ledger, bound permanently
     to that judgment id + material snapshot id
  → re-analysis after a material change creates a NEW judgment; the old one is marked
     superseded and left byte-identical; old decisions keep resolving forever
```

Run it: `python -m applications.investment.workspace` → `http://127.0.0.1:8770/`.

The reference case `orbital-series-b` reaches **PROCEED_WITH_CONDITIONS at LOW confidence,
5 conditions, 1 kernel disagreement, 1 independent agreement**.

**Crucial:** the sample "document" is the frozen `ORBITAL_SERIES_B` packet *serialised* — a
test asserts the parsed packet is *equal* to the packet baked into the prototype, so intake
provably adds no interpretation. **The system has never been run on real case material.**

### 1b. Implemented and working

| Component | State |
|---|---|
| `choir_prototype/` | **Frozen at V0.1**, hash-pinned, stdlib-only, no network, **no LLM call anywhere**. The only running reasoning pipeline. `--frozen` → INTACT. `--replay` → 4 determinism/projection checks pass. `--audit` → portability 1.00 across investment/law/medicine/engineering (engineering = post-freeze hold-out). ~75 own tests. |
| `applications/investment/vertical_slice/` | Document(JSON) → packet → frozen pipeline → 6 persisted stage artifacts + `metadata.json` digests. Plumbing only, adds no reasoning. 17 tests. `DECISION-002` approved. |
| `applications/investment/workspace/` | YUKTI application **V1**. Case register, source register, diligence schedule, judgment view, audit view, decision ledger. Supersession (append-only judgments; decisions bind forward-only). Material Snapshot layer (`material_digest` ≠ `record_digest`; ships a reproduced digest collision as `TestMaterialIdentity`'s first test). 46 tests. `DECISION-003/004/006` approved. No auth, no concurrency control, one domain. |
| `daale/conformance/` | **DAALE v0 Phase 0.** The 28 frozen CHOIR §3 commitments (E1–E13, A1–A11, X1–X4) as a machine-readable register + a lock that resolves every citation by parsing source into syntax trees. `python -m daale conformance` → **HOLDS: 20 conforming, 8 unexercised, 0 unresolved.** First (and only) row of the traceability matrix with a real upstream source. |
| `daale/execution/` | **DAALE v0 Phases 1–2.** The D-Core: input-bound execution identity, CHOIR contract validation, in-memory lease-guarded Reasoning State Store, append-only clock-free trace, **7-check candidate-to-commit gate**, `DETERMINISTIC_ORIGINS` allow-list `{dcore, rfabric, algorithm}`. **Has no evaluator and emits no judgment** (`emits_judgment=False` on every summary, with the reason attached). `test_the_d_core_has_no_evaluator` guards this mechanically. |
| `website/`, `film/`, `research/public/` | Public-facing layers (static site built with Vite; a Remotion film; a published `YK-*` research/decision set). Not load-bearing for the thesis. |

Canonical validation gate currently green: `ruff check`, `ruff format --check`,
`python -m unittest` (**264 tests pass** in the working tree; 237 at v0 closure),
`compileall`, `mypy --strict` (44 files at v0 closure).

### 1c. Partially implemented

- **Dependency index** (`daale/execution/dependencies.py` + `daale/tests/test_dependencies.py`)
  — the answer-independent half of DAALE Phase 3 (structural graph over IR objects: which
  claims depend on which evidence). **Built in the working tree, NOT committed.** Ships
  `TestRealIrShape`, which pins a known defect (see §5).
- **R-Fabric ↔ D-Core integration** (`daale/DAALE/DAALE/`) — a whole nested tree copied in
  from a separate machine location `D:\DAALE`, **staged but not committed, and non-runnable
  in this checkout** (its imports need a Windows directory junction `D:\DAALE\daale` that
  was never recreated here; `D-Core` is not even a valid Python module name). Contains:
  - `R-Fabric/` — an **independently built, LLM-backed** pipeline (copy of `D:\daale_v0_1`):
    6 base "kernels" (ANALYST, CONTRARIAN, FIRST_PRINCIPLES, EXPANSIONIST, OUTSIDER,
    HISTORIAN) run in parallel as separate LLM calls (OpenRouter, default NVIDIA Nemotron 3
    Ultra Free), then an ADVERSARY LLM pass over their outputs, then a **deterministic policy
    engine** that computes metrics from validated findings and selects an ordered rule →
    `ADVANCE` / `HOLD` / `REJECT` / `ESCALATE`. Has its own `CHOIR_CONTRACT_DRAFT.md`
    (explicitly "not the canonical CHOIR spec").
  - `D-Core/rfabric.py` — a bridge translating a finished R-Fabric JSON trace into a
    commitment-A2-shaped package + one `Candidate` with `origin="rfabric"`, run through the
    unchanged 7-check gate.
  - `docs/architecture/DECISION-005_RULING_rfabric_evaluates.md.bak` — a ruling
    ("**R-Fabric evaluates; D-Core commits**") scoped **only to the `D:\DAALE` working
    copy**, explicitly *not* amending the canonical `DECISION-005`. It exists only as a
    `.bak` inside the nested tree; it was never promoted to the canonical
    `docs/architecture/`.
  - 3 offline (fixture-backed) R-Fabric runs on disk (all `served_model:
    offline-fixture/*`), and one committed D-Core admission record
    (`reports/daale/rfabric_admission/8cbac366…txt`) showing the offline `REJECT` decision
    packet committed as `rfabric-judgment:DD-001 v1`, `emits_judgment: False`. **Zero
    live-LLM runs are committed anywhere.**
- **`research/public/` YK-* publication set** + `website/tools/build-research.mjs` +
  website document/archive features — staged, uncommitted.
- **`temp_dump/research/active/`** (untracked) — 5 dense R-Fabric design docs dated
  2026-08-24 (see §6). Design only; explicitly "not touching `daale/`".

### 1d. Planned, not implemented

- **The evaluator.** DAALE cannot produce a judgment. Whoever/whatever evaluates is
  `DECISION-005`, which is **INVALIDATED with no replacement recorded** (§7).
- DAALE Phases 3 (planner) – 8 (institutional pilot).
- Defeat typing (undercutting / rebutting / premise-denying) — the priority falsifier F3.
- Conflict adjudication (precedence principles, context lattice) — conflicts are detected
  and reported, never resolved by principle.
- Ambiguity as a first-class IR citizen; provenance chain to source loci (evidence cites a
  label, not a locus in an edition).
- A decision-proposition object (the artifact carries a recommendation about a case, not a
  motion a body votes on).
- Authentication / access control; persistence (state store is in-memory); concurrent-edit
  handling (material is replaced wholesale — two analysts overwrite each other silently).
- Real case material → experimental objective **O1**; qualified-reader trial → **O5 / S8**.
- Every `choir/specifications/SPEC-*.md` is **0 bytes**. All four. Same for
  `choir/ontology/*.md` and `choir/proposals/proposal_001/*`. The ~7,700-line research
  corpus under `choir/research/phase-*/` is drafted but **not accepted**.

---

## 2. CORE THESIS

### 2a. What YUKTI is fundamentally trying to achieve

From `CHOIR_v0.1_RESEARCH_FREEZE.md` §2, informal statement (retained verbatim):

> Organizations do not fail because they lack intelligence. They fail because they cannot
> institutionalize reasoning. Current systems produce answers. CHOIR attempts to produce
> **institutional judgments** by decomposing reasoning into multiple deterministic reasoning
> kernels that independently analyze evidence before synthesis.

Falsifiable form — **Proposition C-1**: for decision classes where evidence is distributed
across large document collections, is contested, and is revisited over time, a judgment
produced by (a) translating source into a canonical intermediate representation, (b)
decomposing analysis across kernels that cannot observe one another, (c) deriving confidence
from evidential structure rather than authoring it, (d) projecting explanation from an
execution record rather than regenerating it — is **more defensible** than a judgment from a
single undecomposed process.

*Defensible*, measured only as: the judgment can be reconstructed from its record; its
explanation cannot diverge from its reasoning; its coverage gaps are disclosed rather than
absorbed; it can terminate in a declared non-conclusion rather than a manufactured one.

CHOIR explicitly does **not** claim to compute truth — only *fidelity* / *warrant relative to
a supplied corpus*. Calibration against real-world outcomes is out of scope for v0.1.

### 2b. What makes it different from "just use an LLM/agent/framework"

Claimed differentiators, each with a mechanical enforcement point in `choir_prototype/`:

| Claim | Mechanism | Enforced by |
|---|---|---|
| Confidence is **derived, never authored** | `derive_confidence()` takes only structural facts (evidence quality, input coverage, contradiction count); no code path accepts a literal confidence value | `TestDerivedConfidence`; `Confidence` has no literal constructor path |
| Weakest evidence sets the ceiling; institutional confidence is the **minimum across kernels**, not the mean | `_weakest()`, `lowest_band()` | prototype tests |
| Kernels are **independent** — cannot see the packet, each other, or the synthesizer | pipeline hands each kernel only the `ChoirIR`; runtime is sequential single-threaded | `TestKernelIndependence` |
| The system can **decline** | `CONTESTED` and `INSUFFICIENT_BASIS` are first-class terminal outcomes (rules R1, R2, R6) | reached in multiple domains |
| Explanation is a **projection of the record**, never regenerated | renderers/inspection views read the record; nothing recomputes | `projection-integrity` check in `--replay` |
| **Nothing is deleted** — defeated objects marked and retained | IR keeps contradicted claims | commitment E12 (but see §4 — cites nothing) |
| **Domain independence is measured, not asserted** | `--audit` runs 7 mechanical checks over the source tree + live runs | portability 1.00, engineering hold-out |

### 2c. Demonstrated vs merely designed

**Demonstrated (in the frozen V0.1 prototype, on synthetic packets):** derived confidence
(D), *vikalpa* / legitimate-disjunction outputs (D), explanation-as-projection (D), "nothing
deleted" at the IR level (D), coverage-gap reporting (D), determinism/replay (D),
minimum-not-mean institutional confidence (D), **domain independence — portability 1.00,
4 domains, 1 post-freeze hold-out, all 5 decision rules fire, 2 fire in ≥2 domains** (D).

**Designed / specified but not implemented (status A or S in the freeze):** three
confidence axes never collapsed (S), undercutting ≠ rebutting / typed defeat (S — this is
the theory's *principal empirical hypothesis*, falsifier F3), influence as strictly
second-order (S), ambiguity as first-class IR (S), "saturate then adjudicate" affordable at
scale (A), neural-retrieval / symbolic-adjudication split (A), computed evidence
independence (S).

**Not tested at all:** everything about real material (O1); whether a qualified reader can
consume the artifact (O5 / S8 / falsifier F-CONS — *the only test of the thesis rather than
the machinery*); saturation cost at corpus scale (F-SAT); whether kernels on a shared IR
correlate systematically, making agreement "echo not evidence" (F-IND); provenance to
source loci (O3); faithfulness under summarisation (O4).

---

## 3. ARCHITECTURE

### 3a. Components and relationships

```
CHOIR (theory, frozen v0.1)         — defines ontology, commitments, invariants, falsifiers
   │  research corpus: choir/research/phase-*/ (drafted, NOT accepted)
   │  frozen record:   CHOIR_v0.1_RESEARCH_FREEZE.md §3 = 28 commitments (accepted content)
   ▼
choir_prototype/  (frozen V0.1, hash-pinned, stdlib-only)   — the ONLY running reasoner
   core/   ir.py · contracts.py (Kernel protocol, Artifact, derive_confidence) ·
           domain.py · runtime.py · synthesizer.py · pipeline.py · report.py ·
           inspection.py · replay.py
   domains/ investment/{packets,translator,kernels} · law.py · medicine.py · engineering.py
   │  "This is not YUKTI and not DAALE architecture" — its own README
   ▼
applications/investment/
   vertical_slice/   — document intake + persist-every-stage; calls choir_prototype as a
                       library, unmodified. Canonical reference for "how the engine is called."
   workspace/        — YUKTI application V1. analysis.py is the ONLY door to the engine:
                       composes a document → calls vertical_slice → reads 05-record.json back
                       → relabels prose. Computes no judgment of its own (2 boundary tests).
   prototype-ui/, prototype_risk_rik/  — SUPERSEDED (prototype_risk_rik is the legacy
                       OpenAI-Responses-API path retired by DECISION-001). Not yet removed.
   ▼
daale/  (v0 CLOSED 2026-08-14)      — "canonical control plane; it does not reason"
   conformance/  — 28 frozen commitments as checkable register + citation-resolving lock
   execution/    — D-Core: identity, contract, state store, trace, 7-check commit gate.
                   Invariant: ANYTHING may propose; ONLY the D-Core commits.
                   NO evaluator. NO judgment. Stops exactly at the DECISION-005 boundary.
   execution/dependencies.py  — Phase 3 dependency index (working tree, uncommitted)
   ontology/, (reasoning/, arbitration/, traceability/, runtime/)  — docstring stubs only

daale/DAALE/DAALE/  (staged, uncommitted, non-runnable here — a copied working copy)
   R-Fabric/  — LLM-backed: 6 base kernels ∥ + adversary pass → deterministic policy engine
   D-Core/    — copy of daale/ ; rfabric.py bridges an R-Fabric trace → Candidate(origin="rfabric")
   run_pipeline.py  — runs R-Fabric as a subprocess, then offers its decision packet to D-Core
```

### 3b. Important data/control flows

**Frozen pipeline (`choir_prototype/core/pipeline.py::execute`)** — one function, read top to
bottom, every stage boundary is a real boundary:

```
packet ──domain.translate (shape mapping, NO reasoning)──▶ ChoirIR
ChoirIR ──"ir-sealed" trace step: kernels get the IR and nothing else──▶
  run_kernels: for each of 4 kernels (fixed order): kernel.run(ir) → Artifact;
               validate every cited id exists in the IR (X4); record trace
artifacts ──synthesize(artifacts) ; synthesizer never sees the IR or packet──▶
  _topic_views → agreements/disagreements
  _tally      → weighted by producing kernel's confidence band (INSUFFICIENT weighs 0);
                every line recorded with running totals
  _decide     → ordered rules R1..R6, EVERY rule recorded fired-or-not:
                R1 insufficient-basis (usable kernels < 2)         → INSUFFICIENT_BASIS
                R2 live-disagreement (disagreements>0, margin<3)   → CONTESTED
                R3 proceed-with-conditions (support>oppose, cond>0)→ PROCEED_WITH_CONDITIONS
                R4 proceed (support>oppose)                        → PROCEED
                R5 decline (oppose>support)                        → DECLINE
                R6 balanced-fallback (support==oppose)             → CONTESTED
  _synthesis_confidence → lowest_band across usable kernels (min, not mean)
Synthesis ──render(record) : pure projection──▶ report
```

**The kernels are hand-written threshold functions.** Example
(`domains/investment/kernels.py`, `FinancialPostureKernel`): reads predicates
`{arr_usd, yoy_growth_pct, gross_margin_pct, net_burn_monthly_usd, cash_usd}`; if
`growth >= 40` → `Stance.SUPPORTS`, `>= 15` → `NEUTRAL`, else `OPPOSES`; derives runway =
cash/burn, compares to 18/12-month constants. Every threshold is a named module constant.
Four kernels: `financial_posture`, `risk_exposure`, `market_position`, `governance`. **There
is no learning, no search, no model call — the "reasoning" is a fixed analyst rubric
expressed as code.**

**DAALE D-Core commit gate (`daale/execution/commit.py::run_gate`)** — 7 named checks in
plan order: `references-current-execution`, `inputs-exist-and-are-not-superseded`,
`structure-valid-under-choir`, `respects-active-execution-plan` (**INACTIVE** — needs the
Phase 3 planner; reports INACTIVE, never PASSED), `required-provenance-present`,
`no-stale-write-or-race`, `terminal-state-assigned`. Any FAILED → `REJECTED`. All active
pass → origin decides: in `DETERMINISTIC_ORIGINS {dcore, rfabric, algorithm}` → `VALIDATED`
→ committed; **anything else → `REVIEW_REQUIRED`** (escalated, never committed). Allow-list,
default-deny.

### 3c. Repository structure (the parts that matter)

```
CHOIR_v0.1_RESEARCH_FREEZE.md   canonical CHOIR v0.1 reference (freeze; thesis; 28 commitments;
                                open questions; out-of-scope; objectives O1–O6; success S1–S8;
                                falsifiers F3/F-PORT/F-PROJ/F-SAT/F-IND/F-INFL/F-CONS)
DAALE_v0_CLOSURE.md             canonical DAALE v0 closure + freeze (+ §10 governance update)
IMPLEMENTATION_QUEUE.md         backlog + operating rules (no runtime behaviour without an
                                approved spec OR direct architectural instruction)
MANIFESTO.md                    NB: actually an AI research-task prompt, not a manifesto (left
                                deliberately; rewriting it is the owner's call)
docs/architecture/DECISION-00{1..7}*.md   the ADRs (see §7)
docs/development/IMPLEMENTATION_LOG.md     append-only narrative of every implementation cycle
docs/traceability/TRACEABILITY_MATRIX.md  spec→artifact links (mostly "None — outside chain")
choir/                          research corpus (phase-1..5 drafted); SPEC-*/ontology/proposals ALL EMPTY
choir_prototype/                frozen V0.1 engine (FROZEN.md, freeze.py hash-pins every file)
applications/investment/        vertical_slice/ (ref impl) + workspace/ (product V1) + 2 superseded
daale/                          v0 conformance + execution (closed/frozen); dependencies.py uncommitted
daale/DAALE/DAALE/              staged, uncommitted, inert copy of the D:\DAALE R-Fabric experiment
temp_dump/                      non-canonical working area; "nothing leaves without a ruling"
research/public/, website/, film/   public layers
.gitattributes  (* text=auto eol=lf)   LOAD-BEARING: without it a Windows clone rewrites
                                       choir_prototype markdown to CRLF and --frozen falsely
                                       reports MODIFIED
```

### 3d. Important implementation decisions and constraints

- **`choir_prototype/` is frozen at the architecture level and hash-pinned at the file
  level.** Python is pinned by *normalised syntax tree* (survives `ruff format`), other files
  by content hash. Editing any file to fix even prose trips `--frozen` and destroys the
  archival/hold-out evidence chain. Corrections go in the root `README.md` instead. The
  freeze is a *tripwire, not a prohibition* — V0.2 is expected to change frozen commitments,
  but only on implementation evidence or falsification, **never because a more elegant
  formulation was found**, and always attached to a version bump.
- **stdlib-only is deliberate** in `choir_prototype/` — it is what makes determinism
  auditable. An independent review's Pydantic-strict recommendation was declined for this
  reason.
- **DAALE v0 is architecturally frozen but NOT hash-pinned** — it is a component expected to
  change on a DECISION-005 ruling; pinning it would assert a permanence nobody intends.
- **No database anywhere.** Institutional state is one JSON file per case under
  `reports/workspace/<case>/`. `reports/` is "generated output, not committed."
- **The product cannot display a conclusion the record does not contain** — it reads
  `05-record.json` back rather than holding live objects. Commitment E9 extended into the
  product.
- **Two digests, two claims:** `record_digest` proves the *reasoning* was identical;
  `material_digest` proves the *material* was identical. The second does not follow from the
  first (the frozen engine flattens `reported` vs `estimated` to the same `Uncertainty.LIKELY`
  — a demonstrated hash collision motivated the Material Snapshot layer).
- **Governance rule:** implementation only from an approved SPEC or direct architectural
  instruction; if a task needs an architectural choice, *write the decision note first and
  wait for approval*. All SPECs are empty, so every code area except the conformance lock is
  formally "outside the approved chain" (a recorded, unresolved governance gap).

---

## 4. VALIDATION — everything actually done, with results

| # | What was run | Result |
|---|---|---|
| V1 | `choir_prototype --audit` (domain-independence metric, 7 mechanical checks) | **Portability = 1 − 0/7 = 1.00.** 0 core changes to add 4 domains. Engineering domain written *after* the core was frozen + hash-pinned = genuine hold-out. Strongest sub-result **A6**: all 5 decision rules fire across the corpus; R1 fires for investment+law, R3 for investment+engineering — which rule fires is set by evidential structure, not domain. |
| V2 | `choir_prototype --replay` (4 checks) | `execution-determinism`, `report-determinism`, `inspection-determinism`, `projection-integrity` all pass on all packets. Record digest = SHA-256 over IR+artifacts+synthesis+trace. |
| V3 | `choir_prototype --frozen` | **INTACT** — architecture unchanged since freeze, with vertical_slice + workspace + daale all in the tree. |
| V4 | `python -m daale conformance` (citation-resolving lock over the 28 frozen commitments) | **HOLDS: 20 conforming, 8 unexercised, 0 unresolved.** The 8 unexercised are *classified* (not queued): `research-open` E4/E5/E7, `prototype-limit` E6, `specified-not-implemented` E3/E11, `decision-required` E10, `evidence-discrepancy` E12. |
| V5 | `python -m unittest` (full canonical suite) | **264 pass** in the current working tree (237 at v0 closure; 77 of those are `daale/`). `mypy --strict` clean across 44 files at closure. |
| V6 | Workspace "verified by use" walkthroughs (browser, not only tests) | orbital-series-b → **PROCEED_WITH_CONDITIONS / LOW confidence / 5 conditions / 1 disagreement / 1 independent agreement**; ledger pins the decision to record digest `9ba1d434…`. Supersession walkthrough: edit a figure → re-analyse → JUDGMENT-001 superseded by JUDGMENT-002, digests differ, LEDGER-001 still binds to JUDGMENT-001 and still verifies. |
| V7 | Material-identity collision probe (shipped as a test) | `status: reported` vs `status: estimated` on the same figure → **identical `record_digest` (`580a5b27…`), COLLISION: True.** Both map to `Uncertainty.LIKELY`; status appears nowhere else in the IR. This is why `material_digest` exists and is order-sensitive. |
| V8 | DAALE D-Core live check (3 candidates, one execution) | `rfabric` origin committed; `llm` origin escalated to REVIEW_REQUIRED; a candidate with no provenance rejected. 10 trace events. `emits_judgment: False` with reason attached. |
| V9 | R-Fabric offline (fixture) pipeline → D-Core admission (in `daale/DAALE/DAALE/`) | R-Fabric decision packet = **REJECT** (rule `P080-CRITICAL-FAILURE`: fixture marks 2 critical requirements `NOT_SATISFIED`, no HIGH adversarial challenge disputes them). D-Core admitted the *decision packet as a candidate object*: `rfabric-judgment:DD-001 v1`, state **committed**, all active gate checks passed, check 4 INACTIVE, `emits_judgment: False`. **All 3 on-disk runs use `offline-fixture/*` models. No live-LLM run is recorded.** |

**Evidence that currently supports the thesis:** (1) domain independence is *measured* and
holds with an adversarial-ish hold-out; (2) determinism, replay, and projection-integrity
hold mechanically; (3) confidence is structurally underivable-by-hand — no literal path
exists; (4) the system reaches `CONTESTED` / `INSUFFICIENT_BASIS` on thin/conflicted packets
without intervention; (5) append-only institutional history with supersession + dual-axis
(reasoning / material) verification is implemented and verified live.

**Evidence still missing (all of it about whether the thesis *matters*):** no run on real
material (**O1**); no qualified-reader trial (**O5 / S8 / F-CONS** — the only test of the
thesis rather than the machinery); typed defeat unimplemented so **F3** (the priority
falsifier) cannot be exercised; saturation cost unmeasured (**F-SAT**); kernel-correlation
untested (**F-IND**); provenance-to-loci untested (**O3**); faithfulness under summarisation
untested (**O4**); no 5th, deliberately-dissimilar domain (**S1**).

---

## 5. KNOWN FAILURES / WEAKNESSES

### 5a. Doesn't work / can't run

- **DAALE emits no judgment.** By design — but it means the "reference reasoning engine" is
  today a validation-and-commit control plane with nothing to commit but externally-produced
  packets.
- **The nested `daale/DAALE/DAALE/` tree does not run in this checkout.** Its tests
  `from daale import …` and there is no `daale` package/junction here; `D-Core` is not a
  valid module name. It is staged but inert.
- **All `choir/specifications/SPEC-*.md` are 0 bytes.** The governance rule "no runtime
  behaviour without an approved spec" is dead in practice; everything runs on "direct
  architectural instruction" instead, widening a recorded traceability gap.

### 5b. The place the implementation may be proving the WRONG thing

**The "independent reasoning kernels" are hand-authored threshold functions.**
`domains/investment/kernels.py` is ~600 lines of `if value >= NAMED_CONSTANT:
Stance.SUPPORTS`. "Domain independence 1.00" is real, but what is portable is a *fixed
scoring rubric and a synthesis procedure* — not "reasoning." Two kernels "independently
agreeing" on capital efficiency (`financial_posture` runway vs `risk_exposure` burn ratio)
is two threshold checks over partially overlapping inputs. A skeptic's read: the prototype
demonstrates **"a deterministic institutional-analysis rubric can be made portable,
inspectable, and made to decline"** — which is valuable but is *not* the thesis's claim that
*decomposing reasoning* beats a single undecomposed pass. Nothing in the corpus yet
distinguishes "we computed structure" from "we hard-coded an analyst's checklist."

Corollary risk for any future experiment: the fair control for Arm-B ("YUKTI") is **not** a
naive LLM — it is an LLM handed *this same rubric* as a prompt ("cite evidence IDs, list
what you couldn't determine, say CONTESTED if evidence conflicts"). If that control matches
YUKTI, the deterministic machinery is unjustified — and the freeze itself already concedes
this in §4.4 ("verification-first architectures are not excluded… the design is unforced and
must be defended on engineering and empirical grounds rather than derived").

### 5c. Architectural concerns / edge cases

- **IR ↔ contract vocabulary mismatch (open, pinned by `TestRealIrShape`).** The frozen
  engine's real IR *fails* DAALE v0's contract gate on **7 violations**: `contract.py`'s
  `REFERENCE_FIELDS = ("cites","source","target","supports","about")` are invented — real
  claims use `evidence_ids` / `subject_id`, relationships use `source_id`/`target_id`,
  `evidence.source` is a prose label not an id; `uncertainty` is a per-claim field, not the
  7th top-level section commitment A2's prose implies; the engine emits no `choir_version`.
  Unresolved question: **is commitment A2's prose the contract, or is the frozen engine's
  actual IR the contract?** Not answerable inside `daale/`. On Fork B's critical path.
- **E12 ("Nothing is deleted") is marked demonstrated (status D) and cites nothing.** Either
  the evidence exists and was never recorded, or the status is optimistic. Must be
  adjudicated, *not* closed by finding something plausible to cite (that would manufacture
  the traceability the lock measures).
- **All 4 audited domains are rule-interpretive with graded evidence.** A quantitative or
  non-interpretive 5th domain is untested — portability 1.00 could be an artifact of picking
  4 similar domains (S1).
- **The prototype IR is a subset of the specified MIR**; portability of the subset is
  evidence for, not proof of, portability of the full schema.
- **In-memory state store.** Every R-Fabric admission opens a fresh store and commits at
  v1 — no cross-run versioning until a persistence layer exists.
- **Kernels share a fixed topic *vocabulary*** (an enum per domain) so the synthesizer can
  group findings — a coupling point the "kernels share nothing" framing understates.
- Repo hygiene: a junk file named `bject {` sits in the repo root (a `less` help-text dump
  from a mis-redirected command).

### 5d. The governance discrepancy in the uncommitted work

The staged `daale/DAALE/DAALE/` integration auto-commits **LLM-derived findings** through
`origin="rfabric"`. That collides with three canonical positions:
- **DECISION-001**: "model calls are advisory only, never authoritative."
- **DECISION-007**: `rfabric` was allow-listed as "parallel evaluation of *deterministic*
  kernels… reproducible"; "everything… that can disagree with itself — LLM, human, external
  tool — is deliberately absent"; adding/relying on an origin "requires an approved
  decision."
- **`temp_dump/research/active/` (2026-08-24) rulings**: the 5-kernel R-Fabric roster is
  *model-agnostic* and **all kernels default to `REVIEW_REQUIRED`**; R-Fabric "currently
  contributes nothing to the deterministic auto-commit pathway"; "Inkling" (the intended
  Analyst model, = Thinking Machines Lab's open-weights model) is **non-deterministic by the
  vendor's own docs."
The working-copy ruling's defence is that the *policy engine's decision* is a deterministic
function of *validated* findings — but the findings themselves are LLM-authored, which
DECISION-001 says means the model *authors* them. This is unreconciled, and the ruling lives
only as a `.bak` inside the nested tree, never promoted to canonical `docs/architecture/`.

---

## 6. RECENT WORK

### 6a. Most recent committed change

`05c777d` (2026-08-21) — converted `choir/research/` placeholder files to filled `.txt`
content, added the constitutional distillation protocol (R007) and a legacy-system-adoption
doc, started `yukti-platform/` with a "general reasoning baseline", continued the investment
workspace UI polish sprint. The 5 commits before it (`d54b750`…`0790928`) were the DAALE v0
closure and a UI "polish sprint" (visual foundation, navigation, staged execution read-out,
board-packet framing, skeletons/press feedback).

### 6b. Uncommitted working tree (what was in progress when work stopped)

Large and heterogeneous:
1. **The entire `daale/DAALE/DAALE/` R-Fabric ↔ D-Core integration** copied from a separate
   machine location `D:\DAALE` (built 2026-08-29). Carries its own working-copy-only ruling
   "R-Fabric evaluates; D-Core commits" (`.bak` only). Non-runnable here (§5a).
2. **`research/public/` — 26 published `YK-*` docs** (`YK-R-001..018` research,
   `YK-D-001..007` decisions, `YK-P-007` protocol) + `_manifest.json` +
   `website/tools/build-research.mjs` + `website/public/research/*.json` +
   website document/archive pages. A publication layer over the internal corpus.
3. **`daale/execution/dependencies.py` + `daale/tests/test_dependencies.py`** — the
   answer-independent half of DAALE Phase 3 (dependency index over IR objects). Ships
   `TestRealIrShape` pinning the IR/contract mismatch (§5c).
4. `choir/research/*.txt` → `.md` renames (staged).
5. `create_pdf.py` (+ modified) and PDF outputs; `website/` homepage + stylesheet rebuild
   (gold-on-black), `website/judgment.html`, `home.js`, `nav-toggle.js`, `home.css` (all
   untracked).

### 6c. Design work in `temp_dump/` (untracked, 2026-08-24) — the intended next architecture

Five dense docs, all "not touching `daale/`", all awaiting architect rulings:
- **`…_daale_hybrid_execution_architecture_source_plan.md`** — verbatim transcription of the
  external "DAALE Hybrid Execution Architecture for YUKTI" doc (the "v0 plan"
  `DAALE_v0_CLOSURE.md` §7.5 says is "recorded nowhere in this repository"). CPU/GPU analogy:
  **D-Core** = small deterministic canonical authority; **R-Fabric** = non-authoritative
  parallel accelerator; **Planner**; **Reasoning State Store** (6 areas); **Candidate-to-Commit
  Protocol** (the 7 checks); **canonical/counterfactual/replay lanes**; **coprocessor
  adapters** (LLM/human/tool propose, D-Core commits). 8-phase roadmap; phases 0–2 = what
  `daale/` already has.
- **`…_r-fabric_governance_model.md`** — Fork A (R-Fabric implements CHOIR semantics inside
  `daale/`) vs **Fork B** (R-Fabric calls the frozen `choir_prototype` kernels). "This is
  `DECISION-005`'s question, restated at the R-Fabric boundary." Naming the governance model
  doesn't need the fork closed; *building* it does.
- **`…_r-fabric_worker_charter_reconciliation.md`** — Inkling confirmed (Thinking Machines
  Lab MoE, ~975B/41B, temp fixed at 1.0, "thinking-effort" dial, **no reproducibility
  guarantee**). Ruled: interpretive workers escalate to `REVIEW_REQUIRED`; Synthesis is a
  distinct stage after R-Fabric; **no `daale/` code touched**. Superseded same day: the
  4-worker roster (Evidence/Analyst/Adversary/Forecaster) → a **5-kernel roster**
  (Historian-Librarian, Contrarian, First-Principles, Expansionist, Outsider), traceable to
  R007 Stage 4 (Outsider is genuinely new).
- **`…_r-fabric_kernel_definitions.md`** — model-agnostic contracts for the 5 kernels
  (epistemic question / role / input / output / purpose / failure boundary / execution
  contract). All 5 default to `REVIEW_REQUIRED` until an implementation proves reproducibility;
  "R-Fabric may end up with zero kernels on the deterministic pathway" preserved as
  acceptable.
- **`…_r-fabric_topology_challenge.md`** — adversarial redesign: all 5 kernels independent at
  generation time; cross-referencing moves *inside* Synthesis as a deterministic "phase 1
  reconciliation" (structural comparison over declared pointers, judges nothing) before
  "phase 2 decision"; one frozen snapshot taken once at dispatch; a coverage/rejection ledger
  as a first-class Synthesis input.

### 6d. Blockers / unresolved decisions (from `temp_dump/…/blocked/` + handoffs)

1. **The evaluator question** — see §7. Everything DAALE Phase 3+ waits on it. The Phase 3
   handoff (`2026-08-22_daale_phase3_entry.md`) says: give the ruling, or start the
   dependency index (done, uncommitted).
2. **IR ↔ contract vocabulary mismatch** (§5c) — a ruling on "A2 prose vs engine IR."
3. **E12 adjudication.**
4. Whether the staged `daale/DAALE/DAALE/` work is promoted, and if so how its ruling
   reconciles with DECISION-001/007 and the 08-24 research.
5. The external "v0 plan" still has no recorded disposition in the repo.
6. Whether Synthesis needs its own escalation origin (`rfabric-worker` vs `rfabric-synthesis`).
7. The decision-proposition object (may be a *prerequisite* for O5, not an enhancement).

---

## 7. CURRENT DECISION STATE — do not reinterpret or replace these

### 7a. The ADRs (`docs/architecture/DECISION-00N_*.md`)

| ADR | Status | Ruling (do not silently revisit) |
|---|---|---|
| **DECISION-001** | **Approved 2026-08-04** | Deterministic kernels **are** the architecture. Model-backed execution is *legacy and non-canonical*. Model calls are **advisory only, never authoritative** ("a model emitting a value into a schema *authors* it"). Replay/determinism checks mandatory. |
| **DECISION-002** | **Approved + broadened 2026-08-06** | A "document" for v0.1 is a **serialised packet**, not prose. Product-generated packet documents allowed. Documents may *represent* packets; they may **not interpret** them. Prose+extraction remains unapproved. |
| **DECISION-003** | **Approved 2026-08-06** | Product lives at **`applications/investment/workspace/`**; a top-level `yukti/` package is **rejected**. **"Review areas"** is canonical user-facing terminology (replaces "RIK Positions"; "RIK" is legacy). "Propositions" is deliberately *not offered* (no decision-proposition object exists). Product obtains a judgment by composing a document → calling the vertical slice → reading the record back. Research-freeze §5 engineering exclusions apply to the **engine**, not to product layers. |
| **DECISION-004** | **Approved 2026-08-06** | **Judgment supersession.** Judgments are append-only, identified, dated; re-analysis creates a *new* judgment and marks the old one superseded (byte-identical, still resolvable). A decision binds **permanently** to the judgment it was recorded against and **forward-only** (cannot be recorded against a superseded judgment). Identical record digest → return existing judgment, do not duplicate. |
| **DECISION-005** | **INVALIDATED 2026-08-22. No replacement recorded.** | *Historical* status preserved verbatim as "**Open. Not accepted.**" — **not** Approved, **not** Rejected: the question was never answered, the decision was retired. The question: *what is DAALE, and who evaluates* — **option A** (DAALE evaluates for itself, CHOIR semantics inside `daale/`) or **option B** (DAALE calls the frozen `choir_prototype` kernels). The invalidation selected neither and introduced no replacement evaluator architecture. **The evaluator boundary in `daale/` stands unchanged until the architectural artifact that supersedes this ADR is recorded.** No implementation may assume A, B, C ("DAALE retired as a name"), or D ("DAALE is the product-side engine boundary"). Nothing may be moved into or out of `daale/` on an assumed answer. |
| **DECISION-006** | **Approved 2026-08-06** | **Material Snapshot layer.** Institutional material has an immutable identity; every saved state is hashed at full fidelity, versioned, appended to the case's material register. A judgment binds to the snapshot in force when it ran. Ledger verification covers reasoning and material as **separate** claims. `material_digest` is order-sensitive (engine claim ids are positional). Sources stay references — nothing uploaded/ingested. |
| **DECISION-007** | **Approved 2026-08-14** | **Candidate escalation = allow-list, default-deny.** `DETERMINISTIC_ORIGINS = {"dcore", "rfabric", "algorithm"}` in `daale/execution/commit.py`. Pass all active checks + origin in the list → `VALIDATED` (may commit); **anything else → `REVIEW_REQUIRED`** (escalated, never committed). `rfabric` was included as "parallel evaluation of *deterministic* kernels… reproducible." **Adding an origin to the list grants canonical write authority and requires an approved decision.** There is *no review workflow* behind escalation (marks a candidate and stops). |

### 7b. Frozen commitments & invariants

- **CHOIR v0.1 freeze (`CHOIR_v0.1_RESEARCH_FREEZE.md` §3):** 28 commitments — epistemic
  **E1–E13**, architectural **A1–A11**, execution **X1–X4**. Status per commitment: D
  (demonstrated), A (assumed), S (specified). A frozen commitment changes **only on
  implementation evidence or falsification**, attached to a version bump — never for
  elegance. Tripwire, not prohibition. Load-bearing subset: pipeline stage *ordering* (A1),
  IR shape (A2), kernel contract `ChoirIR → Artifact` (A3), kernel non-observation (A4),
  derived-never-authored confidence (A5/E2), the 5 decision rules and their order (A6),
  core/domain one-way dependency (A7), renderers as pure projections (A8/E9), min-not-mean
  institutional confidence (A9), weakest-evidence ceiling (A10), `CONTESTED` /
  `INSUFFICIENT_BASIS` as first-class (A11), determinism (X1), separately-checkable replay
  (X2), deterministic kernels are canonical (X3), kernels cite only IR ids (X4).
- **DAALE v0 closure freeze (`DAALE_v0_CLOSURE.md` §5):** 10 frozen properties — input-bound
  execution identity; order-sensitive identity; lease-guarded serialised canonical writes;
  stale reads refused not applied; the 7 gate-check names; a check that cannot run reports
  `INACTIVE` never `PASSED`; escalation is an allow-list; the trace is append-only and
  clock-free; neither `conformance/` nor `execution/` imports the engine; unexercised
  commitments are never reported as conforming. Enforced by the conformance lock + test
  suite + `test_the_d_core_has_no_evaluator`.
- **`choir_prototype/` is hash-pinned** (`freeze.py`); `python -m choir_prototype --frozen`
  must stay INTACT; corrections go in root `README.md`, not the package. `.gitattributes`
  (`* text=auto eol=lf`) must not be deleted.

### 7c. Numbering / state / naming conventions

- ADRs: `DECISION-00N`. Research: internal `R00N` (e.g. `R007`), published `YK-R-0NN`
  (research), `YK-D-00N` (decisions), `YK-P-00N` (protocols); manifest at
  `research/public/_manifest.json`.
- Conformance commitments: `E#` / `A#` / `X#`. Gate-check names are canonical strings
  (`references-current-execution`, …). Candidate states:
  `PROPOSED → VALIDATED → COMMITTED` / `REJECTED` / `REVIEW_REQUIRED`.
- Workspace: `JUDGMENT-00N`, `LEDGER-00N`, `MATERIAL-00N`; case ids are company-name slugs.
- R-Fabric bridge ids: `rfabric-candidate:<run-id>`, `rfabric-judgment:<case-id>`,
  `origin="rfabric"`; R-Fabric's own contract version string is
  `"CHOIR-CONTRACT-DRAFT-0.1"` (deliberately *not* `"0.1"` — it must not overclaim
  compliance with the canonical freeze).
- Pipeline stage *count* is explicitly **not** load-bearing (FROZEN.md says 7, README says
  5, the slice says 6 — the *ordering* is the frozen commitment).

### 7d. Process invariants

- Implementation only from an approved SPEC **or** direct architectural instruction. Need an
  architectural choice → write the decision note first, wait for approval.
- `temp_dump/` custodian protocol: nothing there is canonical; nothing leaves without a
  ruling; the repo agent may not promote artifacts, modify canonical architecture, or create
  numbered decisions from inside it.
- Collaboration mode (owner's standing instruction): challenge and check for coherence,
  don't agree reflexively; test every decision against **"does this reinforce institutional
  reasoning?"** — reject it (including your own proposal) if not. Surface contradictions
  between stated thesis and actual artifacts rather than routing around them.

---

## 8. THE ROAD AHEAD — 3–5 technically meaningful next steps (Claude's current view)

### Step 1 — Record the canonical evaluator ruling that supersedes DECISION-005

**What:** a real `docs/architecture/DECISION-008` (or a formal supersession of 005) that
picks one of: **A** implement CHOIR semantics inside `daale/`; **B** DAALE calls the frozen
`choir_prototype` kernels through the gate (Fork B in the governance doc); **C** the
"third answer" — an LLM-backed R-Fabric whose *deterministic policy engine* produces the
candidate and whose per-kernel findings escalate, with the D-Core committing — and
explicitly reconcile C against DECISION-001 and DECISION-007 (does an LLM-authored finding
riding `origin="rfabric"` violate "model calls never authoritative"? the 08-24 research says
yes).
**Why it matters:** every DAALE phase 3–8 is blocked on this; the repo currently ships an
engine that *structurally cannot emit a judgment*; and a working-copy ruling that contradicts
canonical governance is sitting staged, about to be answered by accident — which is the
exact failure DECISION-005 was written to prevent.
**Evidence it produces:** an unblocked, single implementation path; a decision record; and
clarity on whether YUKTI's engine is deterministic-kernels, frozen-prototype-kernels, or
LLM-kernels-behind-a-deterministic-gate — three materially different systems.

### Step 2 — Resolve the IR ↔ contract vocabulary mismatch

**What:** rule whether commitment A2's prose or the frozen engine's actual emitted IR is the
contract, then either correct `daale/execution/contract.py` (`REFERENCE_FIELDS`,
`IR_SECTIONS`, `choir_version` handling) to the real vocabulary, or annotate A2 and note the
frozen prototype's divergence as a conformance finding. Un-pin `TestRealIrShape`.
**Why it matters:** DAALE v0's contract gate today *rejects the frozen engine's own output*
on 7 violations; under Fork B this is on the critical path; the uncommitted dependency index
currently traverses a fixture vocabulary, not real objects.
**Evidence it produces:** the frozen engine's real IR passes the D-Core gate; the dependency
index runs over real `03-ir.json`; one recorded, checkable answer to "what is CHOIR's IR
shape."

### Step 3 — Run the frozen pipeline on ONE real, messy case (first true test of O1)

**What:** take a genuine investment (or other-domain) decision with real source documents,
real provenance, real internal contradictions; put it through
`workspace → vertical_slice → choir_prototype`; inspect every stage artifact.
**Why it matters:** *every* result to date is on `ORBITAL_SERIES_B`, which is the frozen
in-code packet serialised. O1 ("institutional judgment can be generated from a *real* case
packet") is explicitly *held only at V0.1 scale on synthetic packets*.
**Evidence it produces:** whether the translator's conservative defaults degrade gracefully;
whether coverage disclosure and the decline path fire appropriately on real thinness;
whether determinism and projection-integrity survive non-toy input; a concrete list of what
the threshold kernels cannot see in real material.

### Step 4 — The qualified-reader trial (S8 / falsifier F-CONS)

**What:** give a domain expert *only* the workspace judgment artifact for a real case (no
system, no re-analysis) and measure whether they can reach the recommendation — or precisely
locate the section they'd need to disagree with — vs. the same expert given a conventional
analyst memo for the same case.
**Why it matters:** the freeze names this "the only criterion requiring a human trial… the
only one that tests the thesis rather than the machinery." F-CONS ("qualified readers cannot
reach decisions from the artifact") is "the outcome the programme should most want to detect
early, and the one its current metrics are least equipped to see."
**Evidence it produces:** the first direct evidence for or against "more defensible" as
*consumable by an institution*, not just *internally consistent*.

### Step 5 — Exercise falsifier F3 (typed defeat) in the prototype, OR add an adversarial 5th domain (S1)

**What (F3):** implement undercutting / rebutting / premise-denying defeat per
`computational_primitives.md §3.12` in a V0.2 branch and observe whether it can be
accommodated without changing the IR (A2), the kernel contract (A3), or the synthesizer.
**What (S1):** onboard a 5th domain chosen to *break* the portability claim — quantitative
or non-interpretive — and re-run `--audit`.
**Why it matters:** F3 is "the single highest-value open question in the whole programme";
S1 tests whether portability 1.00 is real or an artifact of 4 rule-interpretive
graded-evidence domains. Both have pre-declared falsification conditions — a negative result
is a *result*, not a setback.
**Evidence it produces:** either the V0.1 core generalises (strong support for §2b) or a
named, pre-registered falsifier fires (which the freeze treats as the point of the exercise).

---

## 9. WHAT WOULD ACTUALLY PROVE YUKTI IS WORKING?

### The claim under test (state it precisely, because the weak version is trivially true)

**NOT** "an LLM can produce a good institutional memo." **NOT** "structured output with
citations is nice."

**The claim:** for contested, evidence-distributed, revisited decisions, a judgment built by
*decomposed, mutually-blind, record-projected* reasoning is **more defensible** — measurably
more *reconstructible*, more *gap-honest*, more *appropriately willing to decline*, and with
an explanation that *cannot diverge* from the reasoning — than a judgment from a single
undecomposed pass, **even when both reach the same recommendation.**

### The smallest convincing experiment: a blind, head-to-head defensibility trial on real material

**Inputs.** N ≥ 10 real decision cases with the structure the thesis targets: evidence
spread across multiple documents, at least one genuine internal contradiction, and a later
revisit or known outcome. Investment-committee packets fit; the `workspace` already models
this exact shape (Case → Sources → 15-figure diligence schedule → Judgment → Ledger).

**Arm A (control).** A strong single LLM given the same source documents and asked for a
recommendation + rationale + confidence + "what you could not determine." Run it **twice** —
once naive, once **given the `domains/investment/kernels.py` rubric as a prompt** ("apply
these thresholds; cite the evidence id behind every claim; if two findings you'd weight
oppositely both hold, output CONTESTED; if you can't find ≥50% of the inputs a section
needs, output INSUFFICIENT"). The rubric-prompted control is the one that matters — it is
the honest test of whether *computing* the structure beats *asking for* it.

**Arm B (YUKTI).** The same documents → `workspace` → `vertical_slice` → frozen pipeline →
the judgment artifact (recommendation; per-review-area findings with cited claim/evidence
ids; derived confidence + named limiting factor; conditions; disagreements; "what was not
established"; audit trace; `record_digest` + `material_digest`).

**Judges.** Domain experts who saw neither system run, blind to which arm produced which
artifact.

**Four measurements that operationalise "defensible":**

1. **Reconstruction.** Judge gets *only* the artifact (no system, no sources). Can they
   restate how the conclusion was reached and name every load-bearing evidence item?
   Metric: % of conclusions fully reconstructible. YUKTI should approach 100% (X4: every
   finding cites ids present in the IR). A prose memo should not.

2. **Explanation non-divergence (falsifier F-PROJ).** Independently re-derive the
   recommendation from the artifact's stated findings + the R1–R6 rules
   (`choir_prototype/core/synthesizer.py::_decide`). Does any faithful reading produce a
   *different* recommendation than the system emitted? YUKTI's `projection-integrity` check
   says zero — verify it holds on real material **and under summarisation** (O4 is untested).
   Any divergence in Arm A counts against it; any in Arm B **falsifies E9**.

3. **Gap disclosure.** Seed 3 known gaps per case (delete a figure / a source). Does the
   system surface each one *unprompted*? YUKTI: coverage < `MINIMUM_COVERAGE` (0.5) →
   `INSUFFICIENT`, and the runtime names the missing predicates. Measure how often each arm
   silently proceeds. Metric: % of seeded gaps surfaced.

4. **Calibrated refusal.** Include cases where the evidence genuinely does not support a
   decision. Does the system decline (`CONTESTED` / `INSUFFICIENT_BASIS`) rather than
   manufacture an answer? Metric: refusal precision/recall against expert consensus on which
   cases were decidable.

### The distinguishing result

YUKTI's thesis is **validated** iff, on identical real inputs and blind to arm, expert judges
rate **Arm B more reconstructible, more gap-honest, and more appropriately declining than the
rubric-prompted Arm A — including on the cases where both arms reach the same
recommendation**, and Arm B shows **zero** explanation-divergence where Arm A shows some.

YUKTI's thesis is **not** validated (the machinery is ceremony) if the **rubric-prompted
Arm A** matches Arm B on all four axes. Then a single LLM told to cite ids, list unknowns,
and decline on conflict does the same job, and the frozen IR / mutually-blind kernels /
deterministic synthesizer are unforced — exactly the "verification-first architectures are
not excluded" separation the freeze §4.4 already concedes.

**The sharp failure signal to watch for:** if Arm B's advantage over the *naive* control
disappears the moment the control is handed the kernel rubric, YUKTI is currently proving
that *specifying* structure works — not that *computing* it deterministically works. Because
`domains/investment/kernels.py` today **is** a hand-written analyst rubric, this risk is
live, and the experiment must include the rubric-prompted control or it proves nothing.

### Files/modules whoever runs this needs

| Purpose | Path |
|---|---|
| Produces the Arm B artifact (the product surface) | `applications/investment/workspace/` (run: `python -m applications.investment.workspace`) |
| The callable pipeline; `05-record.json` is the canonical record | `applications/investment/vertical_slice/run.py` |
| The decision logic a judge re-derives against (R1–R6) | `choir_prototype/core/synthesizer.py::_decide` |
| Derived confidence (no literal path) | `choir_prototype/core/contracts.py::derive_confidence` |
| **The rubric that IS the reasoning today** — give this to the Arm A control | `choir_prototype/domains/investment/kernels.py` |
| The F-PROJ / projection-integrity check to extend to real + summarised output | `choir_prototype/core/replay.py` |
| The intended tests, already written as prose | `CHOIR_v0.1_RESEARCH_FREEZE.md` §6 (O1, O5), §7 (S1, S8), §8 (F3, F-PROJ, F-SAT, F-IND, F-CONS) |
| Material identity (dual-digest verification) | `applications/investment/workspace/material.py` |

### Cheaper precursors that each produce real evidence

- **Kernel-correlation check (F-IND), offline, now:** run all 4 kernels over the existing
  4-domain corpus; measure whether their stances covary across packets more than independent
  analysis would. If they correlate systematically, "independent agreement" is echo, and §2b
  is weakened without needing any real data.
- **The rubric-prompted control alone, on the synthetic corpus:** prompt one LLM with
  `kernels.py`'s thresholds + R1–R6 and compare its outputs to the frozen pipeline's on all
  existing packets. If it matches, that is an early, cheap negative signal about the value of
  determinism-as-mechanism.
- **Projection-integrity under summarisation:** take existing `06-report.txt` records, have
  an LLM summarise them to memo length, and check no summary implies a different
  recommendation than R1–R6 produced. Tests O4 with zero new data.
