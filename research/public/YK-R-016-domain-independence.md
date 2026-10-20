# Domain Independence

| | |
|---|---|
| **Document ID** | YK-R-016 |
| **Source** | `choir/research/phase-5-generalization/domain_independence.md` (016) |
| **Series** | CHOIR Research Programme |
| **Revision** | A |
| **Status** | Active |
| **Last Updated** | 2026-08-23 |

## Abstract

The source document states, and then tests, the claim that the same compiler, IR, and execution pipeline serve Jyotiṣa, law, medicine, finance and engineering, with domain variation confined to vocabulary, kernels, and parameters (§1). It maps every L1 primitive across five domains (§2), defines a portability metric (§6), and records a measured result of portability 1.00 against an executable prototype across four domains with an engineering hold-out control (§6.1). The document is explicit that the result is bounded: the prototype exercises a subset of the MIR, and the falsifiers F3 (graded defeat), F6 (influence collapsing into weighted causation) and F7 (cross-domain precedence) remain open or untested (§6.2, §7).

This publication is **Active**: the source is a complete research document, drafted but not accepted as specification. Its own header records its status as "Draft for review". Per `MANIFESTO.md`, every research document is a hypothesis rather than an established truth.

## Research Question

The source states the question as a claim framed so that it can fail (§1):

> **The same compiler, IR, and execution pipeline serve Jyotiṣa, law, medicine, finance and engineering, with domain variation confined to vocabulary, kernels, and parameters.**

The document immediately adds: "This is worth nothing unless it is falsifiable. §6 gives the measurement; §7 gives the conditions under which the claim is refuted." (§1)

The target of the claim is a shared structure, not a shared subject matter. The domains are characterised as **interpretive normative systems** — "bodies of codified rules, stated in natural language by authorities, applied to particular cases, with exceptions, precedence orderings, graded support, and a requirement to justify conclusions by citation" (§1).

The document is equally explicit about what is *not* claimed: that the domains are epistemically equivalent. "Medicine has outcome ground truth and Jyotiṣa does not (`confidence_framework.md` §7.1). The reasoning *machinery* is shared; the *validation* is not. Conflating the two would be the fastest way to discredit the whole project." (§1)

## Finding

### Primitive mapping (§2)

The document instantiates every L1 primitive in five domains — Jyotiṣa, law, medicine, finance, engineering — across twenty rows covering Entity, Agent, Attribute, State, Event, Condition, Constraint (integrity and normative), Rule, the three Exception kinds (undercutting, rebutting, premise), Influence, Causation, Context, the three Evidence kinds (attested, direct, absence), interpretive Confidence, and Provenance.

Its conclusion: "**Every row instantiates in every column.** No primitive is domain-specific, and no domain requires a primitive absent from the set. That is the C3 test of `computational_primitives.md` §1.3, applied exhaustively." (§2)

One cell is marked as a qualification rather than a fit: Causation in Jyotiṣa is recorded as *"(rare — see §3)"*.

### The Influence/Causation split (§3)

`computational_primitives.md` §3.7 admitted Influence as a separate primitive on the grounds that most institutional reasoning is influence-language rather than causal. The source tests that claim by domain:

| Domain | Predominant mode | Evidence (as stated in the source) |
|---|---|---|
| Jyotiṣa | **Influence** | Grahas *indicate*, *strengthen*, *afflict* — the corpus rarely asserts production |
| Law | **Influence** | Mitigating and aggravating factors *modulate* outcomes; only tort causation is genuinely causal |
| Medicine | **Mixed** | Aetiology is causal; prognostic factors are influences |
| Finance | **Influence** | Risk factors *increase* probability; they do not produce events |
| Engineering | **Mixed** | Load *produces* stress; safety factors *modulate* allowables |

"Three of five are influence-dominant and two are genuinely mixed. **No domain is causation-only** — which is what most rule engines implicitly assume by providing only one edge kind." (§3)

The document does not treat this as settled. The falsifier stated in `computational_primitives.md` §5 — that influence-heavy corpora encode losslessly as weighted causation — "remains open, but the cross-domain evidence strengthens rather than weakens the case for keeping the distinction" (§3).

### *Vikalpa* is not a Jyotiṣa peculiarity (§4)

`conflict_resolution.md` §7.1 requires that the system be able to terminate in a disjunction. The source identifies this as "the design decision most likely to be dismissed as an artefact of a fringe domain" and argues that it is not, by tabulating a genuine unresolved split and the consequence of forcing one answer in each of the five domains: a circuit split in law, two guideline-supported options of comparable standing in medicine, two permitted accounting treatments in finance, two acceptable design approaches under one code in engineering, and two authorities giving incompatible readings in Jyotiṣa.

"In every column, collapsing the disjunction **destroys information the decision-maker needs**, and in most it would be affirmatively misleading. A system that always returns one answer is not more decisive; it is less accurate." (§4)

The document further records that the Mīmāṃsā interpretive priority ordering (`conflict_resolution.md` §5.2) generalises: "statutory text outranks a marginal note; an operative clause outranks recitals; a guideline's recommendation outranks its introduction. The tradition supplied a general theory of textual authority, not a parochial one." (§4)

### Explanation schema across domains (§5)

The *pañcāvayava* template (`explainability_framework.md` §3), adopted from Nyāya, is instantiated across Jyotiṣa, law and medicine — *pratijñā*, *hetu*, *udāharaṇa*, *upanaya*, *nigamana* — with worked members in each column. The source notes that legal reasoning already uses a near-identical structure (issue, rule, application, conclusion), and clinical reasoning follows finding → guideline → applicability → recommendation. "The Nyāya schema is a superset that additionally forces the *warrant* to be exhibited with its source — which is exactly what makes an explanation auditable." (§5)

Note that this table covers three domains, not the five used elsewhere in the document.

### The portability metric (§6)

The claim is measured rather than asserted. The metric stated:

> **Onboarding a new domain must require zero changes to L0, L1, MIR schema, or the execution pipeline.**

Protocol: "For each domain: extract 20 representative rules, compile to MIR, execute against test cases, and count changes by category." (§6)

Changes are classified by layer. Permitted and expected at L2: new subject classes under existing L1 branches, new relationship subtypes under existing families, new kernels, authority ranking and confidence weights. New context dimensions are "Permitted, watch" and count weakly against the claim. Counting against the claim at L1: a new relationship family, a new top-level entity branch. Counting as outright failures at the core: an MIR schema change, a new condition-algebra construct, a pipeline stage change.

```
portability = 1 − (core_changes / total_changes)
```

"Target: `core_changes = 0`. Any non-zero value is a finding about the core ontology, to be escalated as a constitutional change (`reasoning_ontology.md` §6.1) rather than patched." (§6)

### Measured result: portability 1.00 (§6.1)

The source records the experiment as run against the executable prototype in `choir_prototype/`, invoked with `python -m choir_prototype --audit`.

Design: the prototype's core (IR, runtime, confidence, conflict detection, synthesis, report, replay) was separated from a domain layer and hash-pinned. Four domains were then built against it — investment (4 kernels, 2 packets), law (4 kernels, 2 packets), medicine (4 kernels, 2 packets), and engineering as hold-out (4 kernels, 1 packet).

"**Engineering is the control.** Investment, law and medicine were the development set — the core was being decoupled while they were written, so a fix could have been tuned to them without anyone noticing. Engineering was written *after* the core was frozen and hashed." (§6.1)

Result, as recorded:

| Check | Result |
|---|---|
| A1 import direction — no core module imports a domain | PASS |
| A2 vocabulary isolation — no domain term in core code | PASS |
| A3 execution — every domain runs on shared code | PASS (7 packets) |
| A4 shared machinery — no domain defines its own synthesizer | PASS |
| A5 core stability — core matches the pinned manifest | PASS (0 of 10 changed) |
| A6 rule identity — one rule ordering serves all domains | PASS |
| A7 hold-out — the control needed no core change | PASS |

```
core changes required to add domains : 0
domain modules added                 : 7
portability = 1 - 0/7 = 1.00
```

"**The strongest single result is A6.** All five decision rules fire across the corpus, and which one fires is determined by evidential structure rather than by domain." (§6.1) R1 insufficient-basis fires for `northwind-seed` (investment) and `harbour-note-claim` (law); R2 live-disagreement for `meridian-supply-claim` (law); R3 proceed-with-conditions for `orbital-series-b` (investment) and `bridge-hanger-assessment` (engineering); R4 proceed for `routine-referral` (medicine); R5 decline for `renal-caution-referral` (medicine).

"Two independent facts are visible here. Rules R1 and R3 each fire in *two different domains*, and each domain reaches *different* outcomes on different packets. Neither would hold if the decision procedure were domain-tuned." (§6.1)

A secondary control is recorded: the investment domain's record digests are byte-identical before and after the core/domain split (`580a5b27…`, `fc4e6908…`), "confirming the refactor changed structure and not results. Asserted in `TestBehaviourPreserved`." (§6.1)

### What the result does not establish (§6.2)

The document states plainly that "The result is real but bounded, and §7 remains the honest register":

- Four domains, "all of which are **rule-interpretive with graded evidence**. A domain unlike these four is untested."
- "**F3 (graded defeat) and F7 (cross-domain precedence) remain open.** The prototype has no defeat typing, so it cannot test whether some domain needs defeat to be graded rather than structural — the falsifier most likely to force a core change."
- "**Deontic depth is untested** (§10.4). The prototype's modality is a tag, not a logic."
- "The prototype is far narrower than the research: no context lattice, no precedence ordering, no ambiguity representation, no provenance chain to source text. Portability of the *prototype* core is evidence for, not proof of, portability of the full MIR schema."

The claim the document says is now supported is narrower than the claim it opened with: "**for rule-interpretive normative domains with graded evidence, the CHOIR core is domain-independent, measured rather than asserted.**" (§6.2)

### Falsifier register (§7)

Per C7 (`computational_primitives.md` §1.7):

| # | Refuting observation | Status as recorded |
|---|---|---|
| F1 | A domain requiring a MIR schema change | **Survived** at prototype scale — four domains, zero core changes (§6.1). Untested for the full MIR |
| F2 | A domain requiring a new relationship family | **Survived** at prototype scale; the four domains needed only `supports` and `contradicts` |
| F3 | A domain where defeat is genuinely graded, not structural | **Untested and now the priority.** The prototype has no defeat typing, so §6.1 could not exercise it |
| F4 | A domain where forcing a single answer is always correct | **Refuted** — §4, and confirmed: `CONTESTED` and `INSUFFICIENT_BASIS` were both reached in domains other than the one they were designed against |
| F5 | A domain with no interpretive dimension (text meaning never contested) | **Likely refuted** — every codified corpus generates interpretive dispute |
| F6 | A domain where influence collapses into weighted causation | Open — §3. The prototype models influence only as second-order modulation and does not test the collapse |
| F7 | Cross-domain reasoning requiring a shared precedence ordering | Untested; probably correctly forbidden |

The document qualifies the two survivals: "F1 and F2 surviving at prototype scale is genuine but limited evidence: the prototype's IR is a subset of the MIR specified in `choir_intermediate_representation.md`, so the test exercised the parts a working system actually needed, not the full schema." (§7)

On F3: "F3 is the most serious. If some domain's exceptions genuinely weaken rather than withdraw, the two-layer semantics (`evidence_model.md` §5.1) would need revision. Candidates worth probing: risk models where a mitigant reduces but does not eliminate exposure. The counter-argument is that such cases are *influences*, not exceptions — but that must be demonstrated on real material, not assumed." (§7)

### Where the domains genuinely differ (§8)

"Honesty about the differences is what makes the shared-machinery claim credible." (§8)

**Validation (§8.1).** Jyotiṣa has **no ground truth for outcomes** and calibrates against textual fidelity and scholar agreement; law has partial ground truth (appellate outcomes, expert agreement); medicine, finance and engineering have outcome ground truth (trial outcomes, realised outcomes, test and failure data). "This is a real asymmetry and it is handled by keeping calibration in L2 (`confidence_framework.md` §7.3). Jyotiṣa calibrates against fidelity, medicine against outcomes, and the framework's structure is identical in both cases." (§8.1)

**Corpus stability (§8.2).** Jyotiṣa is a closed corpus subject to textual criticism only; law and finance change continuously; medicine revises periodically; engineering runs on periodic code cycles. "Law and finance stress the versioning machinery far harder than Jyotiṣa does. A design validated only on a closed corpus may have latent temporal-scoping defects." (§8.2)

**Language (§8.3).** "Only Jyotiṣa needs the Sanskrit pipeline. Legal and clinical text is modern natural language with its own hard problems (statutory cross-reference density, guideline hedging). **The front end is domain-specific by design**; MIR is the shared boundary (`choir_intermediate_representation.md` §2.2)."

**Consequence and risk (§8.4).** Wrong conclusions in medicine, engineering and law cause direct harm. "This does not change the machinery, but it changes deployment posture: escalation thresholds, mandatory review, and how *vikalpa* is presented. These are L2 policy parameters, not core changes."

### Cross-domain convergences (§9)

Three convergences the document describes as "not designed for" and as having "emerged from independent analysis":

1. "**Pollock's undercutting defeaters and the *upādhi* / *apavāda* apparatus describe the same thing.** Two traditions a millennium apart, working on different material, arrived at the same distinction (`vedic_reasoning_methodology.md` §2.1)."
2. "**Nyāya's *hetvābhāsa* and the conflict taxonomy derived independently in `conflict_resolution.md` §3 nearly coincide.**"
3. "**The Mīmāṃsā interpretive priority ordering restates as a general theory of textual authority** that legal and clinical practice already follow informally (§4)."

The document grades this evidence explicitly and low: "Convergent derivation from independent starting points is weak evidence, but it is the kind of weak evidence worth noticing: these distinctions are more likely to be features of codified normative reasoning as such than artefacts of any one tradition." (§9)

## Architectural Implications

**The core/domain boundary is load-bearing and is now enforced mechanically.** The A1–A7 audit (§6.1) makes import direction, vocabulary isolation, shared synthesis, and core hash stability checkable properties rather than intentions. A5 pins the core against a manifest (0 of 10 modules changed); A2 forbids domain terms in core code. Onboarding a new domain is therefore constrained to L2 additions — subject classes, relationship subtypes, kernels, authority rankings, confidence weights (§6).

**Any core change is a constitutional event, not a patch.** The metric declares that a non-zero `core_changes` value "is a finding about the core ontology, to be escalated as a constitutional change (`reasoning_ontology.md` §6.1) rather than patched" (§6). This routes MIR schema changes, condition-algebra additions, and pipeline stage changes through governance rather than through ordinary development.

**Influence must remain a distinct primitive from Causation.** Because no domain examined is causation-only (§3), a single edge kind would misstate what the sources claim — "Modelling a mitigating factor as a cause of a sentence would misstate what a sentencing regime claims, in exactly the way modelling an aspect as a cause misstates what a śāstra claims" (§3).

**Disjunctive termination (*vikalpa*) is a general requirement, not a Jyotiṣa accommodation.** The requirement in `conflict_resolution.md` §7.1 is defended across all five domains (§4), and F4's refuted status (§7) rests on `CONTESTED` and `INSUFFICIENT_BASIS` being reached in domains other than the one they were designed against.

**The front end is domain-specific by design; MIR is the boundary.** Only Jyotiṣa needs the Sanskrit pipeline; a legal front end can be built "without touching anything downstream" (§8.3).

**Risk and consequence are L2 policy, not core.** Escalation thresholds, mandatory review, and *vikalpa* presentation vary by domain but are parameters — "which is itself a point in favour of the layer separation" (§8.4).

**Calibration stays in L2.** The Jyotiṣa/medicine asymmetry in ground truth is absorbed by keeping calibration targets in L2 while the framework's structure remains identical (§8.1).

**Context dimensions need governance.** New context dimensions are permitted but flagged "watch" and count weakly against the claim (§6); §10.3 records the risk that per-domain invention makes cross-domain comparison impossible.

**Deontic depth is the most likely source of a core-breaking result.** Law needs contrary-to-duty conditionals and possibly a full deontic logic, while CRL has modality tags only (`reasoning_language.md` §9.5); the document names this "the most likely source of an F1 refutation" (§10.4).

## Open Questions

From §10 of the source, with the source's own gradings:

1. **Run the metric — done.** §10.1 marks this struck through and completed: portability 1.00 across four domains with a hold-out control (§6.1). "The remaining gap is that the prototype exercises a subset of the MIR, not the whole schema."
2. **F3 — does any domain have genuinely graded defeat?** "Now the highest-priority open question, and the one that would force a core change. The prototype cannot answer it because it has no defeat typing; testing F3 requires adding undercutting/rebutting defeat first." (§10.2)
3. **Context dimension proliferation.** "L2 may add dimensions (`reasoning_ontology.md` §6.1); if each domain invents its own, cross-domain comparison becomes impossible. A registration discipline may be needed." (§10.3)
4. **Deontic depth.** "Law needs contrary-to-duty conditionals and possibly a full deontic logic; CRL has modality tags only (`reasoning_language.md` §9.5). This is the most likely source of an F1 refutation." (§10.4)
5. **Cross-domain reasoning.** "Precedence orderings are incomparable across domains by construction. Probably correct to forbid, but a medical-legal case genuinely spans both." (§10.5)
6. **Does engineering fit at all?** "It is the least examined here. Much engineering reasoning is quantitative and model-based rather than rule-interpretive; the rule-governed part (code compliance) fits well, but that may be a minority of the domain." (§10.6)

Additional unresolved items recorded elsewhere in the source:

- **F6 remains open** — the prototype "models influence only as second-order modulation and does not test the collapse" of influence into weighted causation (§7).
- **F1 and F2 survive only at prototype scale** — the prototype IR is a subset of the MIR in `choir_intermediate_representation.md`, so the full schema is untested (§7).
- **F7 is untested** and only "probably correctly forbidden" (§7).
- **Untested domain shapes** — all four measured domains are rule-interpretive with graded evidence; "A domain unlike these four is untested" (§6.2).
- **Latent temporal-scoping defects** — "A design validated only on a closed corpus may have latent temporal-scoping defects" (§8.2).
- **Prototype scope gaps** — no context lattice, no precedence ordering, no ambiguity representation, no provenance chain to source text (§6.2).

## Related Documents

Documents this source depends on and cites:

- [YK-R-001 — Computational Primitive Specification](YK-R-001-computational-primitive-specification.md) — the primitive set, the C3 and C7 tests (§1.3, §1.7), the Influence/Causation admission (§3.7) and its falsifier (§5)
- [YK-R-002 — Reasoning Ontology](YK-R-002-reasoning-ontology.md) — L2 dimension addition and constitutional-change escalation (§6.1)
- [YK-R-004 — Vedic Reasoning Methodology](YK-R-004-vedic-reasoning-methodology.md) — *upādhi* / *apavāda* and undercutting defeat (§2.1)
- [YK-R-009 — Evidence Model](YK-R-009-evidence-model.md) — the two-layer semantics that F3 would require revising (§5.1)
- [YK-R-010 — Conflict Resolution](YK-R-010-conflict-resolution.md) — *vikalpa* termination (§7.1), Mīmāṃsā interpretive priority (§5.2), conflict taxonomy (§3)
- [YK-R-011 — Confidence Framework](YK-R-011-confidence-framework.md) — ground-truth asymmetry (§7.1) and L2 calibration (§7.3)
- [YK-R-012 — Explainability Framework](YK-R-012-explainability-framework.md) — the *pañcāvayava* template (§3)
- [YK-R-013 — CHOIR Intermediate Representation](YK-R-013-choir-intermediate-representation.md) — the MIR boundary (§2.2) and the schema the prototype only partially exercises
- [YK-R-014 — Reasoning Language (CRL)](YK-R-014-reasoning-language-crl.md) — modality tags only, and deontic depth (§9.5)

Documents this source feeds:

- [YK-R-017 — Computational Symbolism Review](YK-R-017-computational-symbolism-review.md)
- [YK-R-018 — Related Work Survey](YK-R-018-related-work-survey.md)

The source header additionally records its dependency as "all prior documents".
