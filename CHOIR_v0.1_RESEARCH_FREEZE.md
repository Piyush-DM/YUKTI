# CHOIR v0.1 — Research Freeze

**Status:** FROZEN — 2026-08-04.
**Type:** Engineering and research freeze. Not a manifesto.
**Supersedes:** nothing. This document sits above the existing record and
indexes it; it does not replace `choir/research/README.md`,
`choir_prototype/FROZEN.md`, or any research deliverable.
**Governs:** what implementation and experimentation may assume, and what they
must treat as open.

---

## 1. Purpose of the Freeze

The first research phase is complete. It produced eighteen research
deliverables across five phases, an executable prototype frozen at V0.1 with a
measured domain-independence result, and a theory-reduction pass that
established which of the project's commitments are load-bearing and which are
contingent.

The freeze exists because the marginal return on further conceptual work is now
lower than the marginal return on implementation evidence. The research phase
answered the questions that could be answered by reasoning. The questions that
remain — whether defeat typing forces a core change, whether saturation is
affordable at corpus scale, whether an institution can act on the artifact —
cannot be settled by argument. They require running the system against real
material.

**The rule from this point forward:**

> A frozen commitment changes only on implementation evidence or experimental
> falsification. It does not change because a more elegant formulation was
> found.

This is deliberate and is the main function of this document. The reduction
phase demonstrated that several of the project's design decisions can be
reformulated, generalised, or replaced without violating anything the theory
requires. That is a fact about the theory, not a reason to act. Reformulation
without evidence is how a research programme spends years without producing a
result.

Consistent with existing project usage, **this freeze is a tripwire, not a
prohibition.** V0.2 is expected to change frozen commitments. The freeze
ensures that when a commitment changes, the change is deliberate, recorded, and
attached to a version bump — rather than something that happens by accident
while the corpus drifts.

---

## 2. Computational Thesis

The project's informal statement of the thesis, retained as written:

> Organizations do not fail because they lack intelligence. They fail because
> they cannot institutionalize reasoning. Current systems produce answers.
> CHOIR attempts to produce institutional judgments by decomposing reasoning
> into multiple deterministic reasoning kernels that independently analyze
> evidence before synthesis.

Stated as a research proposition, in the form the falsification conditions in
§8 test:

> **Proposition C-1.** For decision classes in which evidence is distributed
> across large document collections, is contested, and is revisited over time,
> a judgment produced by (a) translating source material into a canonical
> intermediate representation, (b) decomposing analysis across reasoning
> kernels that cannot observe one another, (c) deriving confidence from
> evidential structure rather than authoring it, and (d) projecting explanation
> from an execution record rather than regenerating it, is **more defensible**
> than a judgment produced by a single undecomposed process.
>
> Where *defensible* means, and is measured only as: the judgment can be
> reconstructed from its record; its explanation cannot diverge from its
> reasoning; its coverage gaps are disclosed rather than absorbed; and it can
> terminate in a declared non-conclusion rather than a manufactured one.

Proposition C-1 is scoped deliberately. The informal statement above is not
falsifiable as written — organizations also fail from misaligned incentives,
resource constraints, and correct reasoning toward wrong objectives. C-1 claims
less and can be tested.

CHOIR does not claim to compute truth. It claims warrant relative to a supplied
corpus. Calibration against outcomes is a domain-dependent property and is out
of scope for v0.1 (§5).

---

## 3. Frozen Commitments

These are **implementation assumptions, not eternal truths.** Each is stable
enough to build against for v0.1. Each has a status recording how much support
it currently has.

Status values: **D** = demonstrated in the V0.1 prototype · **A** = assumed,
not yet demonstrated · **S** = specified in research, not implemented.

### 3.1 Epistemic commitments

Drawn from `choir/research/README.md` §3. These recur across the research
corpus and are the decisions everything else follows from.

| # | Commitment | Status |
|---|---|---|
| E1 | **Fidelity, not truth.** CHOIR claims what a corpus says, never that it is correct. | D |
| E2 | **Confidence is derived, never authored.** No code path accepts a literal confidence value. | D |
| E3 | **Three confidence axes** — extraction, interpretive, inferential — never collapsed. | S |
| E4 | **Undercutting is not rebutting.** Cancellation withdraws a rule; it does not assert the opposite. | S |
| E5 | **Influence is second-order.** It modulates edges and cannot assert conclusions. | S |
| E6 | **Ambiguity is a first-class IR citizen.** The compiler emits diagnostics rather than guessing. | S |
| E7 | **Saturate, then adjudicate.** Fire every rule before resolving anything. | A |
| E8 | ***Vikalpa*** — terminating in a legitimate disjunction is a valid output. | D |
| E9 | **Explanations are projections of the trace**, never regenerated. | D |
| E10 | **Neural retrieval, symbolic adjudication.** Embeddings propose; they never conclude. | A |
| E11 | **Evidence independence is computed**, not assumed. Correlated evidence is discounted. | S |
| E12 | **Nothing is deleted.** Defeated objects are marked and retained. | D |
| E13 | **An unevaluated thing is never a false thing.** Coverage gaps are reported. | D |

### 3.2 Architectural commitments

Drawn from `choir_prototype/FROZEN.md` §1. Frozen at the architecture level,
not as code text.

| # | Commitment | Status |
|---|---|---|
| A1 | The pipeline stages and their order. Changing the order changes what can be explained. | D |
| A2 | The IR shape: entities, claims, evidence, assumptions, relationships, uncertainty, metadata. | D |
| A3 | The kernel contract: `ChoirIR` → `Artifact`. Kernel independence rests on it. | D |
| A4 | Kernels cannot observe the packet, each other, or the synthesizer. | D |
| A5 | Confidence derivation, and the rule that it is never authored. | D |
| A6 | The five decision rules and their ordering. Cross-domain identity rests on it. | D |
| A7 | The core/domain boundary and its one-way dependency. Domain independence rests on it. | D |
| A8 | Renderers are pure projections of the record. | D |
| A9 | Institutional confidence is the minimum across kernels, not the mean. | D |
| A10 | Confidence takes the weakest evidence item, not the average. | D |
| A11 | `CONTESTED` and `INSUFFICIENT_BASIS` are first-class terminal outcomes. | D |

### 3.3 Execution commitments

| # | Commitment | Status |
|---|---|---|
| X1 | **Determinism**: no clock, no randomness, no I/O, no concurrency, no dictionary-order dependence. | D |
| X2 | **Replay**: execution, report, inspection determinism, and projection integrity are separately checkable. | D |
| X3 | **Deterministic kernels are the architecture.** Model-backed execution is legacy and not canonical, per `docs/architecture/DECISION-001_reasoning_execution_substrate.md`. | D |
| X4 | Kernels cite only identifiers present in the IR. | D |

**Recorded qualification on X1.** The reduction phase established that
determinism is not axiomatic. It is the cheapest sufficient mechanism for three
properties that are themselves required: reproducibility of the record,
confidence computed from stated inputs by a stated rule, and verifiable kernel
independence. Determinism is frozen for v0.1 as an *engineering assumption*
that delivers all three at low cost. It is not frozen as a necessary truth, and
§9 reflects this.

**Recorded qualification on E4.** The reduction phase established that typed
defeat is not derivable from the other commitments. It is the theory's
principal empirical hypothesis and is the subject of falsifier F3 (§8). It is
frozen as a specification commitment, not as a demonstrated property.

### 3.4 Known discrepancy in the frozen record

`choir_prototype/FROZEN.md` §1 freezes "the seven pipeline stages and their
order." `choir_prototype/README.md` describes twenty trace steps grouped into
"the five pipeline stages." Both documents are inside the hash-pinned package
and cannot be corrected without destroying the archival record, per the
precedent set in `FROZEN.md` §4. The discrepancy is recorded here rather than
resolved. The stage **ordering** is the frozen commitment (A1); the stage
**count** is not load-bearing, as evidenced by two frozen documents disagreeing
on it while the system functions.

---

## 4. Open Research Questions

**These are tracked research programs, not blockers.** Implementation proceeds
without them being resolved. None of them prevents v0.1 experimentation.

### 4.1 The priority falsifier

**F3 — graded versus structural defeat.** The prototype has no defeat typing
and therefore cannot exercise the falsifier most likely to force a core change.
This is the single highest-value open question in the programme. Resolving it
requires implementing undercutting / rebutting / premise-denying defeat per
`computational_primitives.md` §3.12 and observing whether the core survives.

### 4.2 Carried research gaps

From `choir/research/README.md` §6. G1 (the domain-independence metric had
never been run) was **closed** by the prototype's `--audit`: portability 1.00
across four domains with a hold-out control.

| # | Gap |
|---|---|
| G2 | The benchmark verse is uncited; `E-ATTEST` unresolved; no critical edition checked. |
| G3 | No gold set exists, so no pipeline stage can be evaluated. |
| G4 | The Jyotiṣa technical lexicon does not exist, and sandhi splitting depends on it. |
| G5 | The influence-vs-causation falsifier is untested. |
| G6 | Literature verification queue open; no external novelty claim is currently supportable. |
| G7 | `Proposal` and `Decision` are underspecified; L1 membership of `Decision` is questioned. |
| G8 | Saturation cost at corpus scale is unmeasured and could be prohibitive. |
| G9 | Deontic depth is shallow — modality is a tag, not a logic. Likeliest source of core-schema failure for law. |

### 4.3 Prototype limits carried forward

From `choir_prototype/FROZEN.md` §4.

- No context lattice and no precedence ordering. Conflicts are detected and
  reported, never adjudicated by principle.
- No ambiguity representation. The IR cannot hold an unresolved reading.
- No provenance chain to source text. Evidence cites a source label, not a
  locus in an edition.
- All four demonstrated domains are rule-interpretive with graded evidence. A
  domain unlike these four is untested.
- The prototype IR is a subset of the specified MIR. Portability of the
  prototype core is evidence for, not proof of, portability of the full schema.

### 4.4 Architectural questions surfaced during this phase

Recorded as open. None is resolved by this freeze.

- **The relationship between the prototype and DAALE.** The prototype states it
  is not DAALE architecture. DAALE currently contains no reasoning logic.
  Whether the prototype graduates into DAALE, or DAALE is a separate target,
  is undecided.
- **No decision proposition object.** The artifact carries a recommendation
  about a case, not a motion a body votes on. Surfaced by the institutional
  analysis; bears directly on experimental objective O5 (§6).
- **No representation of loss asymmetry.** Confidence is derived, but the risk
  posture against which it is interpreted is encoded in the decision-rule
  thresholds rather than represented. The same thresholds apply to reversible
  and irreversible decisions.
- **Verification-first architectures are not excluded.** The reduction phase
  produced a separation result: an architecture satisfying the theory's
  requirements can violate substantially all of CHOIR's design decisions. This
  does not show the design is wrong; it shows the design is unforced and must
  be defended on engineering and empirical grounds rather than derived. No
  action follows for v0.1.
- **Materiality is not represented.** Findings are undifferentiated.

---

## 5. Out of Scope for v0.1

Explicitly excluded. Exclusion is a scheduling decision, not a judgment of
value. Several items below were identified as significant during this phase and
are postponed deliberately.

**Institutional layers**

- Governance layers of any kind.
- Institutional policy, mandate, and authority representation.
- Cross-case memory. Precedent, consistency checking across decisions, and any
  reasoning that spans more than one case.
- Calibration. Realized-outcome feedback, track record, and any mechanism by
  which the system learns whether its judgments were correct.
- Committee workflow optimization. Meeting-time reduction, standing-question
  pre-answering, conditions menus, deliberation-cycle state.
- Human roles, accountability assignment, and conflict-of-interest
  representation.
- Time-based mechanisms: assumption expiry, re-examination triggers,
  monitoring plans.

**Postponed from theory reduction**

- The axiomatic reduction produced during this phase is retained as historical
  context. It is **not** the implementation basis for v0.1. Implementation
  proceeds against §3, which is concrete enough to build.
- Alternative confidence encodings, including replacing ordinal bands with a
  structural robustness report.
- Verification-first / certificate-checking architectures.
- Any reformulation of a §3 commitment that is motivated by elegance rather
  than by evidence.

**Engineering**

Carried forward from the prototype's own exclusions: authentication, APIs,
databases, UI, plugin systems, distributed runtime, concurrency, optimisation,
configuration systems, dependency injection, and generic frameworks.

---

## 6. Experimental Objectives

What the prototype must demonstrate before CHOIR v0.2 is considered. Objectives
marked *held at V0.1 scale* are already demonstrated; the experimental phase
tests whether they survive contact with real material at larger scale.

**O1 — Institutional judgment can be generated.** The system produces a
structured judgment from a real case packet, not a constructed sample. *Held at
V0.1 scale on synthetic packets; untested on real material.*

**O2 — Domain independence survives.** Onboarding a new domain requires zero
changes to the core. *Held at V0.1 scale: portability 1.00, four domains, one
hold-out. The experimental test is a fifth domain chosen to break the claim —
quantitative or non-interpretive — rather than to confirm it.*

**O3 — Traceability survives.** Every conclusion resolves to evidence, every
evidence item to a source, at real corpus size. *Partially held: kernels cite
only IR identifiers (X4). Untested: provenance to source loci rather than
labels.*

**O4 — Explanation remains faithful.** Rendering a record twice produces
identical text, and no view can compute a different answer than the pipeline
did. *Held at V0.1 scale via the `projection-integrity` check. The experimental
test is whether it survives explanation at a length a reader will actually
read — faithfulness under summarisation is untested.*

**O5 — Committees can consume the artifact.** A qualified reader can reach a
decision from the artifact without reconstructing the analysis themselves.
*Untested. Contingent on the open questions in §4.4 regarding the decision
proposition object and loss asymmetry; those may prove to be prerequisites
rather than enhancements.*

**O6 — Saturation is affordable.** Firing every rule before adjudicating
remains tractable at corpus scale. *Untested. This is G8, and it is the
objective most likely to fail on engineering rather than epistemic grounds.*

---

## 7. Success Criteria

Measurable evidence that would justify continuing the architecture. Criteria
already carrying a defined metric in the existing corpus are marked as such.

| # | Criterion | Measurement |
|---|---|---|
| S1 | Domain independence holds for a domain chosen adversarially | `--audit` portability remains 1.00 with a fifth, deliberately dissimilar domain. *Existing metric, `domain_independence.md` §6.* |
| S2 | Determinism holds at scale | All four `--replay` checks pass on real-size packets. *Existing metric.* |
| S3 | Projection integrity holds | Rendering one record twice yields identical text, at every output length used. *Existing metric, extended to summarised output.* |
| S4 | Decision rules remain structural | Rule firing continues to be set by evidential structure rather than by domain, across the enlarged corpus. *Existing metric, audit A6.* |
| S5 | The system continues to decline | `CONTESTED` and `INSUFFICIENT_BASIS` are reached on real thin or conflicted packets, without manual intervention. |
| S6 | Coverage is disclosed | Every reported judgment names what was not evaluated. Zero silent omissions under audit. |
| S7 | Traceability is complete | 100% of findings resolve to evidence identifiers present in the IR; zero dangling citations. *Existing metric, X4.* |
| S8 | A qualified reader can decide | A reader unfamiliar with the case reaches the same decision as the artifact's recommendation, or identifies precisely which section they would need to disagree. Measured by trial, not asserted. |

S8 is the only criterion requiring a human trial. It is also the only one that
tests the thesis rather than the machinery.

---

## 8. Falsification Conditions

Experimental outcomes that would require reopening the theory. These are stated
in advance, and stating them in advance is a deliberate property of the
programme.

**F3 — Graded defeat forces a core change.** *Priority falsifier.* If
implementing typed defeat — undercutting, rebutting, premise-denying — cannot
be accommodated without changing the IR, the kernel contract, or the
synthesizer, then the V0.1 core is not the general structure it claims to be.
Reopens: A2, A3, E4.

**F-PORT — A domain requires a core change.** If onboarding a domain forces a
modification to `core/`, portability falls below 1.00 and the
domain-independence result is bounded rather than general. Reopens: A7, and the
central claim of §2 (b).

**F-PROJ — Explanation diverges from reasoning.** If any view can produce a
conclusion the pipeline did not reach, the explanation guarantee fails outright
and E9 is false as implemented. This is the most severe possible failure: it
would mean the system's outputs cannot be trusted even when correct.

**F-SAT — Saturation is unaffordable.** If firing every rule before adjudicating
is computationally prohibitive at corpus scale, E7 must be replaced with a
partial-evaluation strategy, and every coverage claim depending on it (E13, S6)
weakens. This is G8.

**F-IND — Independence is not achievable.** If kernels operating on a shared IR
are found to correlate systematically, then agreement between them is echo
rather than evidence, and the justification for decomposition collapses.
Reopens: A4, and §2 (b).

**F-INFL — Influence asserts.** If second-order influence cannot be kept from
asserting conclusions in practice, E5 fails. This is G5 and remains the
framework's own stated disconfirmation.

**F-CONS — The artifact cannot be consumed.** If qualified readers cannot reach
decisions from the artifact (S8), then the system produces well-founded
reasoning that does not serve its stated purpose. This falsifies the thesis in
§2 without falsifying any commitment in §3 — which is the outcome the programme
should most want to detect early, and the one its current metrics are least
equipped to see.

---

## 9. Engineering Guidance

Implementation should optimize for **clarity, observability, determinism (where
currently assumed), and reproducibility** — not for theoretical expansion.

**Clarity.** Prefer code that can be read in one sitting over code that
generalises. The prototype's stated omissions are the model: kernels are
hardcoded rather than registered because a registry would be an abstraction
with one user; thresholds are constants rather than configuration because they
are judgement calls and a config file would hide that rather than expose it.
Follow that standard.

**Observability.** Components record their own working as they compute; views
only format it. Nothing is reconstructed after the fact. Any new component must
record its derivation at the point of computation, and any new view must be a
pure projection.

**Determinism, where currently assumed.** X1 is frozen for v0.1 as an
engineering assumption, not a necessary truth (§3.3). Implementation should
preserve it, because it delivers reproducibility, derived confidence, and
verifiable independence at low cost. Implementation should **not** treat a
proposal that preserves those three properties by other means as heresy — but
neither should it pursue one during v0.1, since replacing a working mechanism
without evidence is exactly what §1 forbids.

**Reproducibility.** Reproducibility must hold off the machine that produced the
result, not merely on it. A concrete instance from this phase: the prototype's
freeze manifest pins non-Python files by content hash, and a default Windows
clone rewrites line endings, causing `--frozen` to report the architecture as
modified on a machine that changed nothing. The root `.gitattributes` corrects
this. The general lesson is the archival one — an integrity mechanism that only
works locally has not been institutionalized, and the same failure mode should
be expected wherever a hash, a path, a locale, or an environment variable
enters a verification path.

**Scope discipline.** Every §4 item is a research programme, not a task. Do not
partially implement one to make a current problem easier. Do not extend the
architecture to accommodate an out-of-scope item from §5.

**For DAALE implementation.** DAALE's relationship to the prototype is an open
question (§4.4) and this document does not resolve it. Until it is resolved,
DAALE implementation should attach to §3 commitments rather than to prototype
internals, and any decision requiring a choice between them should be written
as a decision note in `docs/architecture/` and left blocked until approved.

---

## 10. Closing Statement

This freeze marks the transition from theoretical development to experimental
validation.

No architectural expansion should occur unless driven by implementation
evidence or explicit falsification of the frozen commitments.
