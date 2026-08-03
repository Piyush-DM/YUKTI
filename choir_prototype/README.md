# CHOIR Prototype V0.1 — FROZEN

> **Architecture frozen at V0.1.** Work continues in V0.2. See
> [FROZEN.md](FROZEN.md) for what the freeze protects, what V0.1 did and did not
> establish, and the recommended V0.2 scope.
>
> ```bash
> python -m choir_prototype --frozen
> ```

A deterministic, executable proof that independent reasoning kernels can consume
a canonical intermediate representation and produce structured institutional
reasoning.

**This is not YUKTI and not DAALE architecture.** It is evidence that the
computational model works. It is deliberately small enough to read in one
sitting.

---

## Run it

```bash
python -m choir_prototype
```

That is the whole thing. No install, no configuration, no services, no network,
no API keys.

```bash
python -m choir_prototype --list
python -m choir_prototype --packet northwind-seed
python -m choir_prototype --audit          # measure domain independence
```

## Domain independence — measured, not asserted

`domain_independence.md` §6 defines a falsifiable metric: **onboarding a new domain must
require zero changes to the core.** `--audit` runs it.

Four domains share one core:

| Domain | Packet shape | Kernels |
|---|---|---|
| Investment | source documents + data points | 4 |
| Law | authorities + case facts | 4 |
| Medicine | guidance + observations | 4 |
| **Engineering (hold-out)** | references + parameters | 4 |

**Engineering is the control.** Investment, law and medicine were the development set — the
core was being decoupled while they were written, so a fix could have been tuned to them.
Engineering was written *after* the core was frozen and hash-pinned.

```
core changes required to add domains : 0
domain modules added                 : 7
portability = 1 - 0/7 = 1.00
```

The audit is mechanical — seven checks computed over the source tree and over live runs,
not assertions in a docstring:

| | Check |
|---|---|
| A1 | no core module imports a domain module |
| A2 | no domain term appears in core identifiers or runtime strings |
| A3 | every domain runs end to end on shared code |
| A4 | no domain defines its own synthesizer, runtime or confidence rule |
| A5 | core modules match the pinned manifest |
| A6 | one decision-rule ordering serves every domain |
| A7 | the hold-out domain required no core change |

**The strongest result is A6.** All five decision rules fire across the corpus, and which
one fires is set by evidential structure rather than by domain:

| Rule | Fired for | Domains |
|---|---|---|
| R1 insufficient-basis | `northwind-seed`, `harbour-note-claim` | investment, **law** |
| R2 live-disagreement | `meridian-supply-claim` | law |
| R3 proceed-with-conditions | `orbital-series-b`, `bridge-hanger-assessment` | investment, **engineering** |
| R4 proceed | `routine-referral` | medicine |
| R5 decline | `renal-caution-referral` | medicine |

Two rules fire in two different domains each, and each domain reaches different outcomes on
different packets. Neither would hold if the decision procedure were domain-tuned.

**What it does not establish.** All four domains are rule-interpretive with graded evidence.
Graded defeat (falsifier F3) and deontic depth remain untested — the prototype has no defeat
typing, so it cannot exercise the falsifier most likely to force a core change. The audit
says so in its own output rather than leaving it to this README.

## Read it — the four inspection views

If you have never seen CHOIR before, do not start with the report. Step through
the pipeline in order:

```bash
python -m choir_prototype --inspect ir          # 1. what the packet became
python -m choir_prototype --inspect artifacts   # 2. what each kernel saw
python -m choir_prototype --inspect synthesis   # 3. how the decision was computed
python -m choir_prototype --inspect trace       # 4. every step, with boundaries
python -m choir_prototype --inspect all         # all four, in pipeline order
```

**`--inspect ir`** shows the intermediate representation the kernels will
receive: every entity, claim, evidence item and relationship, plus which claims
each evidence item backs. It ends with integrity checks — claims with no
evidence, claims citing sources that do not exist, evidence backing nothing.

**`--inspect artifacts`** opens each kernel. For every one it shows the inputs it
went looking for and whether the packet supplied them, the **confidence
derivation as numbered rules**, each finding with the claims and evidence behind
it, and what the kernel could not conclude.

```
CONFIDENCE DERIVATION
  rule 0: inputs -- 2 evidence item(s), coverage 5/5 (100%), 0 contradiction(s)
  rule 1: evidence present -> continue
  rule 2: coverage 100% >= 50% minimum -> continue
  rule 3: weakest evidence is SRC-DECK (reported) -> start at moderate
  rule 4: no contradictions -> no downgrade
  rule 5: no coverage cap applied
  result: moderate (limited by: weakest evidence is reported (SRC-DECK))
```

**`--inspect synthesis`** is the answer to "why this recommendation". Five steps:
every finding grouped by topic with agreements and disagreements marked, the
weighted tally **with running totals line by line**, every decision rule in order
showing which fired and which did not, how institutional confidence was taken,
and the result.

```
  [  no ] R1 insufficient-basis
           if: usable kernels < 2
           observed: 4 usable of 4
           -> fall through
  [  no ] R2 live-disagreement
           if: disagreements > 0 and margin < 3
           observed: 1 disagreement(s), margin 6
           -> fall through
  [FIRED] R3 proceed-with-conditions
           if: support > opposition and conditional findings > 0
           observed: support 7, opposition 1, conditional 5
           -> PROCEED_WITH_CONDITIONS
  (3 later rule(s) never evaluated)
```

Rules that did **not** fire are shown too. Knowing the decision came within a
3-point margin of `CONTESTED` is usually more informative than the answer.

**`--inspect trace`** shows all 20 steps grouped into the five pipeline stages,
with what entered and left each one — including the handoff step that states, in
the record, that kernels cannot see the packet, each other, or the synthesizer.

---

## What you will see

The report walks the pipeline in order:

```
Investment Packet
      |
      v  translator.py      -- maps domain shapes to IR. No reasoning.
Domain Translation
      |
      v  ir.py              -- entities, claims, evidence, assumptions,
CHOIR IR                       relationships, uncertainty, metadata
      |
      v  runtime.py         -- dispatch, collect, validate, trace
Independent Reasoning Kernels  (kernels.py -- four of them)
      |
      v  contracts.py       -- findings, evidence refs, confidence,
Structured Artifacts            assumptions, unresolved questions
      |
      v  synthesizer.py     -- agreements, disagreements, recommendation
Institutional Recommendation
      |
      v  report.py          -- projection of the record, nothing recomputed
Execution Report
```

Two sample packets are included, because one does not demonstrate the thesis:

| Packet | What it shows |
|---|---|
| `orbital-series-b` (default) | A well-documented deal. Kernels reach a usable conclusion **while genuinely disagreeing** about revenue quality, and independently **agree** about capital efficiency. |
| `northwind-seed` | A thin packet. Most kernels cannot see enough to conclude anything, and the system returns `INSUFFICIENT BASIS` rather than guessing. |

---

## The four properties this proves

**1. The IR is a real boundary.**
Kernels receive `ChoirIR` and nothing else — not the packet, not each other's
output, not the synthesizer. The translator does no reasoning; the kernels do no
translation. Tested in `TestKernelIndependence`.

**2. Independent agreement means something.**
Because no kernel can observe another, two kernels landing on the same stance is
information rather than an echo. In the default packet, `financial_posture`
(runway of 15.0 months) and `risk_exposure` (burn at 0.93x ARR) reach the same
conditional view of capital efficiency without either knowing the other ran.

**3. Confidence is derived, never authored.**
There is no code path that lets a kernel type in a confidence value. Every band
comes from `derive_confidence`, which reads evidence quality, input coverage and
contradiction count, and always names its **limiting factor** — so the report can
say what would improve the answer, not just how good it currently is.

Two rules are deliberately unforgiving:

- Confidence takes the **weakest** evidence item, not the average. One asserted
  source caps a set of audited ones.
- Institutional confidence takes the **minimum** across kernels, not the mean.
  In the default packet two kernels are `moderate`, and the synthesis is still
  `low`, because `market_position` rests on estimates.

**4. The system can decline.**
`CONTESTED` and `INSUFFICIENT BASIS` are first-class outcomes. A live
disagreement is reported as a disagreement; a packet with too little evidence is
reported as unassessed. Neither is collapsed into a decisive-sounding answer.

---

## Determinism and replay

No clock, no randomness, no I/O, no concurrency, no dictionary-order dependence.
Trace steps are numbered rather than timestamped, precisely so two runs match.

```bash
python -m choir_prototype --replay
```

This checks two claims that are **not the same claim**:

| Check | What it proves | What its failure would mean |
|---|---|---|
| `execution-determinism` | Re-running produces an identical record | The pipeline holds state |
| `report-determinism` | Re-running renders identical text | — |
| `inspection-determinism` | Re-running renders identical inspection views | — |
| `projection-integrity` | Rendering **one** record twice gives the same text | The renderer is doing reasoning of its own |

The last one is the important one. It is what makes every view in this package
trustworthy: they read the record, they never re-derive it. A view that could
compute a different answer than the pipeline did would be worse than no view.

The record digest is a SHA-256 over the full structured record — IR, artifacts,
synthesis and trace. Two people running the same packet can compare one hash and
know they saw the same reasoning.

---

## Files

The tree is split into a domain-neutral core and a domain layer. **Dependencies point one
way only** — `core/` never imports from `domains/`, checked by audit A1.

```
choir_prototype/
├── core/                 domain-neutral; frozen and hash-pinned
│   ├── ir.py             the intermediate representation
│   ├── contracts.py      kernel interface, Artifact, derived confidence
│   ├── domain.py         the extension point a domain plugs into
│   ├── runtime.py        dispatch, collect, validate, trace
│   ├── synthesizer.py    artifacts → recommendation; records its working
│   ├── pipeline.py       the stages, top to bottom
│   ├── report.py         renders the record; recomputes nothing
│   ├── inspection.py     the four inspection views; also pure projections
│   └── replay.py         record digests and replay verification
├── domains/              one module per domain
│   ├── investment/       packets + translator + kernels
│   ├── law.py
│   ├── medicine.py
│   └── engineering.py    the hold-out control
├── audit.py              the domain-independence measurement
└── tests/                75 tests, each naming the claim it defends
```

**Adding a domain** means adding one file and one line in `domains/__init__.py`. The file
supplies four things: packets, a `translate` function, kernels, and a topic vocabulary.
Everything else — IR, runtime, confidence, conflict detection, synthesis, report,
inspection, replay — is shared and cannot be overridden. That non-overridability is what
makes cross-domain agreement meaningful rather than a coincidence of configuration.

Run the tests:

```bash
python -m unittest discover -s choir_prototype -t .
```

### How observability stays honest

Components record their own working as they compute; the views only format it.

- `Confidence.derivation` is written by `derive_confidence` as each rule fires.
- `Synthesis.tally_detail` is written by `_tally` as the running totals move.
- `Synthesis.rules_evaluated` is written by `_decide` for every rule, fired or
  not.
- `TraceEntry.inputs` / `.outputs` / `.notes` are written at each boundary.

None of this is reconstructed after the fact. That is enforced by
`projection-integrity` in `--replay` and by `TestReplay`.

---

## Architecture frozen at V0

The pipeline, the IR, the kernel contract, the four kernels, every threshold and
every decision rule are **frozen**. The observability work added ways to see how
a decision was reached; it changed no decision.

`TestArchitectureFrozen` is the guard: it pins the recommendations, the weighted
tallies (`support 7, opposition 1, conditional 5`), every kernel's confidence
band, and the kernel count. If observability work ever moves an outcome, those
tests fail.

---

## What was deliberately not built

No authentication, APIs, databases, UI, plugins, distributed runtime,
concurrency, optimisation, configuration systems, dependency injection, or
generic frameworks. No LLM call anywhere.

Some specific omissions worth naming, since they are the obvious next questions:

- **Kernels are hardcoded, not registered.** `all_kernels()` returns a tuple.
  A registry would be an abstraction with one user.
- **The topic list is a fixed enum.** Kernels share a *vocabulary* so the
  synthesizer can detect agreement; they share no reasoning. Making it
  extensible would be future-proofing.
- **Confidence bands are ordinal with integer weights.** No probability model,
  because the inputs do not justify one.
- **Thresholds are constants in `kernels.py`.** They are judgement calls, and
  putting them in a config file would hide that rather than expose it.

---

## Relationship to the CHOIR research

The prototype implements a small, executable subset of the research in
[`choir/research/`](../choir/research/). Where the two meet:

| Prototype behaviour | Research document |
|---|---|
| Confidence derived, never authored; limiting factor named | 011 `confidence_framework.md` §1 |
| Institutional confidence is the minimum, not the average | 011 §3.4 |
| Weakest evidence sets the ceiling | 011 §5.1 |
| Agreement requires independent kernels | 009 `evidence_model.md` §4 |
| `CONTESTED` as a legitimate terminal outcome | 010 `conflict_resolution.md` §7.1 (*vikalpa*) |
| Report is a projection of the record, never regenerated | 012 `explainability_framework.md` §1 |
| Kernels must cite only ids present in the IR | 012 §9 (X4, source reachability) |
| Unresolved questions reported, not silently dropped | 015 `execution_pipeline.md` §12 |

The prototype is **narrower than the research on purpose**. It has no defeat
typing, no context lattice, no precedence ordering, no ambiguity representation,
and no provenance chain back to source text. Those are the next things to prove,
not things this version pretends to have.
