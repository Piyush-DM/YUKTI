# 016 — Domain Independence

**Status:** Draft for review
**Phase:** 5 — Generalization Research
**Depends on:** all prior documents
**Feeds:** `computational_symbolism_review.md`, `related_work.md`

---

## 1. The claim, stated so it can fail

> **The same compiler, IR, and execution pipeline serve Jyotiṣa, law, medicine, finance and
> engineering, with domain variation confined to vocabulary, kernels, and parameters.**

This is worth nothing unless it is falsifiable. §6 gives the measurement; §7 gives the
conditions under which the claim is refuted.

**What is being claimed.** These are all **interpretive normative systems**: bodies of
codified rules, stated in natural language by authorities, applied to particular cases, with
exceptions, precedence orderings, graded support, and a requirement to justify conclusions
by citation. That shared structure is the target.

**What is not being claimed.** That the domains are epistemically equivalent. Medicine has
outcome ground truth and Jyotiṣa does not (`confidence_framework.md` §7.1). The reasoning
*machinery* is shared; the *validation* is not. Conflating the two would be the fastest way
to discredit the whole project.

---

## 2. Primitive mapping

Every L1 primitive, instantiated in five domains.

| CHOIR primitive | Jyotiṣa | Law | Medicine | Finance | Engineering |
|---|---|---|---|---|---|
| **Entity** | Graha, rāśi, bhāva | Person, instrument, court | Patient, organ, pathogen | Counterparty, instrument | Component, joint, material |
| **Agent** | Native (chart subject) | Party, judge | Clinician, patient | Trader, issuer | Designer, operator |
| **Attribute** | Natural benefic/malefic | Instrument type | Blood type | Instrument class | Material grade |
| **State** | Occupies a rāśi; dignity | In default; in force | eGFR 28; stage II | Rated BBB; in breach | Under load; corroded |
| **Event** | Daśā onset; transit | Filing; breach; service | Onset; dose administered | Trade; default | Load application; failure |
| **Condition** | In a kendra from the Moon | Resident; over 18 | eGFR < 30 | Coverage ratio < 1.2 | Stress > allowable |
| **Constraint (integrity)** | One rāśi per graha | One jurisdiction per court | One blood type | One legal entity per LEI | Conservation laws |
| **Constraint (normative)** | Ritual prescription | Statutory duty | Standard of care | Covenant | Code requirement |
| **Rule** | Yoga verse | Statutory section | Guideline recommendation | Covenant clause | Design code clause |
| **Exception (undercutting)** | *bhaṅga* / cancellation | Exemption; proviso | Contraindication | Carve-out | Waiver; exclusion |
| **Exception (rebutting)** | Conflicting *vidhi* | Provision asserting the contrary | Competing recommendation | Overriding clause | Overriding code |
| **Exception (premise)** | Precondition failure | Fact not established | Test not performed | Data unavailable | Assumption violated |
| **Influence** | Aspect strengthens | Mitigating factor | Comorbidity worsens | Guarantee improves | Safety factor modulates |
| **Causation** | *(rare — see §3)* | Proximate cause | Pathogen causes disease | Default causes loss | Load produces stress |
| **Context** | Varga; school; application | Jurisdiction; court level; era | Population; setting; version | Jurisdiction; product | Load case; code edition |
| **Evidence (attested)** | *śabda* — the verse | Statutory text; precedent | Guideline; trial | Contract; regulation | Standard clause |
| **Evidence (direct)** | Chart positions | Findings of fact | Test results | Market data | Measurements |
| **Evidence (absence)** | No cancelling condition | No contrary authority | Negative test | No filing | No defect found |
| **Confidence (interpretive)** | Commentarial dispute | Judicial disagreement | Guideline grade | Legal opinion divergence | Code interpretation |
| **Provenance** | Text, recension, edition | Statute, section, version | Guideline, version | Contract, clause | Standard, edition |

**Every row instantiates in every column.** No primitive is domain-specific, and no domain
requires a primitive absent from the set. That is the C3 test of
`computational_primitives.md` §1.3, applied exhaustively.

---

## 3. The Influence/Causation split, tested across domains

`computational_primitives.md` §3.7 admitted Influence as a separate primitive on the grounds
that most institutional reasoning is influence-language rather than causal. Testing that
claim:

| Domain | Predominant mode | Evidence |
|---|---|---|
| Jyotiṣa | **Influence** | Grahas *indicate*, *strengthen*, *afflict* — the corpus rarely asserts production |
| Law | **Influence** | Mitigating and aggravating factors *modulate* outcomes; only tort causation is genuinely causal |
| Medicine | **Mixed** | Aetiology is causal; prognostic factors are influences |
| Finance | **Influence** | Risk factors *increase* probability; they do not produce events |
| Engineering | **Mixed** | Load *produces* stress; safety factors *modulate* allowables |

Three of five are influence-dominant and two are genuinely mixed. **No domain is
causation-only** — which is what most rule engines implicitly assume by providing only one
edge kind.

The falsifier stated in `computational_primitives.md` §5 — that influence-heavy corpora
encode losslessly as weighted causation — remains open, but the cross-domain evidence
strengthens rather than weakens the case for keeping the distinction. Modelling a mitigating
factor as a cause of a sentence would misstate what a sentencing regime claims, in exactly
the way modelling an aspect as a cause misstates what a śāstra claims.

---

## 4. *Vikalpa* is not a Jyotiṣa peculiarity

`conflict_resolution.md` §7.1 requires that the system be able to terminate in a
disjunction. This is the design decision most likely to be dismissed as an artefact of a
fringe domain. It is not.

| Domain | Genuine unresolved split | Consequence of forcing one answer |
|---|---|---|
| Jyotiṣa | Two authorities give incompatible readings | Erases a live tradition-internal debate |
| Law | Circuit split; two defensible readings of ambiguous text | Misrepresents settled law where none exists |
| Medicine | Two guideline-supported options of comparable standing | Removes a legitimate clinical choice |
| Finance | Two permitted accounting treatments | Asserts a requirement that does not exist |
| Engineering | Two acceptable design approaches under one code | Forecloses a compliant option |

In every column, collapsing the disjunction **destroys information the decision-maker
needs**, and in most it would be affirmatively misleading. A system that always returns one
answer is not more decisive; it is less accurate.

Similarly, the Mīmāṃsā interpretive priority ordering (`conflict_resolution.md` §5.2) turns
out to generalise: statutory text outranks a marginal note; an operative clause outranks
recitals; a guideline's recommendation outranks its introduction. The tradition supplied a
general theory of textual authority, not a parochial one.

---

## 5. Explanation schema across domains

The *pañcāvayava* template (`explainability_framework.md` §3) was adopted from Nyāya. Its
portability is a strong test of whether it was the right choice.

| Member | Jyotiṣa | Law | Medicine |
|---|---|---|---|
| *pratijñā* (thesis) | This chart indicates X | This claim is time-barred | Reduce the dose |
| *hetu* (reason) | Because Jupiter is in a kendra from the Moon | Because more than six years elapsed | Because eGFR is 28 |
| *udāharaṇa* (rule + source) | Wherever Jupiter is in a kendra from the Moon…, per verse V | Claims must be brought within six years, per s.5 | Reduce when eGFR < 30, per Guideline §4.2 |
| *upanaya* (application) | Here Jupiter is 4th from the Moon | Here accrual was 2017, filing 2025 | Here eGFR is 28, below 30 |
| *nigamana* (conclusion) | Therefore X, at confidence C | Therefore barred, unless s.28 disability applies | Therefore reduce, unless on dialysis |

Legal reasoning already uses a near-identical structure (issue, rule, application,
conclusion), and clinical reasoning follows finding → guideline → applicability →
recommendation. The Nyāya schema is a superset that additionally forces the *warrant* to be
exhibited with its source — which is exactly what makes an explanation auditable.

---

## 6. The portability metric

The claim is measured, not asserted.

> **Onboarding a new domain must require zero changes to L0, L1, MIR schema, or the
> execution pipeline.**

**Protocol.** For each domain: extract 20 representative rules, compile to MIR, execute
against test cases, and count changes by category.

| Category | Layer | Permitted | Counts against the claim |
|---|---|---|---|
| New subject classes under existing L1 branches | L2 | ✅ Expected | No |
| New relationship subtypes under existing families | L2 | ✅ Expected | No |
| New kernels | L2 | ✅ Expected | No |
| Authority ranking, confidence weights | L2 | ✅ Expected | No |
| New context dimensions | L2 | ⚠️ Permitted, watch | Weakly |
| **New relationship family** | L1 | ❌ | **Yes** |
| **New top-level entity branch** | L1 | ❌ | **Yes** |
| **MIR schema change** | Core | ❌ | **Yes — fails** |
| **New condition-algebra construct** | Core | ❌ | **Yes — fails** |
| **Pipeline stage change** | Core | ❌ | **Yes — fails** |

**Scoring:**

```
portability = 1 − (core_changes / total_changes)
```

Target: `core_changes = 0`. Any non-zero value is a finding about the core ontology, to be
escalated as a constitutional change (`reasoning_ontology.md` §6.1) rather than patched.

### 6.1 Status: MEASURED — portability 1.00

The experiment has been run against the executable prototype in
[`choir_prototype/`](../../../choir_prototype/). Run it with:

```bash
python -m choir_prototype --audit
```

**Design.** The prototype's core (IR, runtime, confidence, conflict detection, synthesis,
report, replay) was separated from a domain layer and hash-pinned. Four domains were then
built against it:

| Domain | Packet shape | Kernels | Packets |
|---|---|---|---|
| Investment | source documents + data points | 4 | 2 |
| Law | authorities + case facts | 4 | 2 |
| Medicine | guidance + observations | 4 | 2 |
| **Engineering (hold-out)** | references + parameters | 4 | 1 |

**Engineering is the control.** Investment, law and medicine were the development set — the
core was being decoupled while they were written, so a fix could have been tuned to them
without anyone noticing. Engineering was written *after* the core was frozen and hashed.

**Result.**

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

**The strongest single result is A6.** All five decision rules fire across the corpus, and
which one fires is determined by evidential structure rather than by domain:

| Rule | Fired for | Domain |
|---|---|---|
| R1 insufficient-basis | `northwind-seed`, `harbour-note-claim` | investment, **law** |
| R2 live-disagreement | `meridian-supply-claim` | law |
| R3 proceed-with-conditions | `orbital-series-b`, `bridge-hanger-assessment` | investment, **engineering** |
| R4 proceed | `routine-referral` | medicine |
| R5 decline | `renal-caution-referral` | medicine |

Two independent facts are visible here. Rules R1 and R3 each fire in *two different
domains*, and each domain reaches *different* outcomes on different packets. Neither would
hold if the decision procedure were domain-tuned.

**A secondary control.** The investment domain's record digests are byte-identical before
and after the core/domain split
(`580a5b27…`, `fc4e6908…`), confirming the refactor changed structure and not results.
Asserted in `TestBehaviourPreserved`.

### 6.2 What this does not establish

The result is real but bounded, and §7 remains the honest register:

- Four domains, all of which are **rule-interpretive with graded evidence**. A domain unlike
  these four is untested.
- **F3 (graded defeat) and F7 (cross-domain precedence) remain open.** The prototype has no
  defeat typing, so it cannot test whether some domain needs defeat to be graded rather than
  structural — the falsifier most likely to force a core change.
- **Deontic depth is untested** (§10.4). The prototype's modality is a tag, not a logic.
- The prototype is far narrower than the research: no context lattice, no precedence
  ordering, no ambiguity representation, no provenance chain to source text. Portability of
  the *prototype* core is evidence for, not proof of, portability of the full MIR schema.

The claim that is now supported: **for rule-interpretive normative domains with graded
evidence, the CHOIR core is domain-independent, measured rather than asserted.**

---

## 7. What would refute the claim

Per C7 (`computational_primitives.md` §1.7), the falsifiers:

| # | Refuting observation | Status |
|---|---|---|
| F1 | A domain requiring a MIR schema change | **Survived** at prototype scale — four domains, zero core changes (§6.1). Untested for the full MIR |
| F2 | A domain requiring a new relationship family | **Survived** at prototype scale; the four domains needed only `supports` and `contradicts` |
| F3 | A domain where defeat is genuinely graded, not structural | **Untested and now the priority.** The prototype has no defeat typing, so §6.1 could not exercise it |
| F4 | A domain where forcing a single answer is always correct | **Refuted** — §4, and confirmed: `CONTESTED` and `INSUFFICIENT_BASIS` were both reached in domains other than the one they were designed against |
| F5 | A domain with no interpretive dimension (text meaning never contested) | **Likely refuted** — every codified corpus generates interpretive dispute |
| F6 | A domain where influence collapses into weighted causation | Open — §3. The prototype models influence only as second-order modulation and does not test the collapse |
| F7 | Cross-domain reasoning requiring a shared precedence ordering | Untested; probably correctly forbidden |

F1 and F2 surviving at prototype scale is genuine but limited evidence: the prototype's IR
is a subset of the MIR specified in `choir_intermediate_representation.md`, so the test
exercised the parts a working system actually needed, not the full schema.

F3 is the most serious. If some domain's exceptions genuinely weaken rather than withdraw,
the two-layer semantics (`evidence_model.md` §5.1) would need revision. Candidates worth
probing: risk models where a mitigant reduces but does not eliminate exposure. The
counter-argument is that such cases are *influences*, not exceptions — but that must be
demonstrated on real material, not assumed.

---

## 8. Where the domains genuinely differ

Honesty about the differences is what makes the shared-machinery claim credible.

### 8.1 Validation

| Domain | Ground truth | Calibration target |
|---|---|---|
| Jyotiṣa | **None for outcomes** | Textual fidelity; scholar agreement |
| Law | Partial | Appellate outcomes; expert agreement |
| Medicine | Yes | Trial outcomes |
| Finance | Yes | Realised outcomes |
| Engineering | Yes | Test and failure data |

This is a real asymmetry and it is handled by keeping calibration in L2
(`confidence_framework.md` §7.3). Jyotiṣa calibrates against fidelity, medicine against
outcomes, and the framework's structure is identical in both cases.

### 8.2 Corpus stability

| Domain | Rate of change | Effect |
|---|---|---|
| Jyotiṣa | Closed; textual criticism only | Incremental recompilation rare |
| Law | Continuous | Versioning and temporal scoping are heavily exercised |
| Medicine | Periodic revision | Supersession matters |
| Finance | Continuous | Both regulation and contracts change |
| Engineering | Periodic code cycles | Edition management is central |

Law and finance stress the versioning machinery far harder than Jyotiṣa does. A design
validated only on a closed corpus may have latent temporal-scoping defects.

### 8.3 Language

Only Jyotiṣa needs the Sanskrit pipeline. Legal and clinical text is modern natural language
with its own hard problems (statutory cross-reference density, guideline hedging). **The
front end is domain-specific by design**; MIR is the shared boundary
(`choir_intermediate_representation.md` §2.2). This is a feature: it is what allows a legal
front end to be built without touching anything downstream.

### 8.4 Consequence and risk

Wrong conclusions in medicine, engineering and law cause direct harm. This does not change
the machinery, but it changes deployment posture: escalation thresholds, mandatory review,
and how *vikalpa* is presented. These are L2 policy parameters, not core changes — which is
itself a point in favour of the layer separation.

---

## 9. The strongest cross-domain evidence

Three convergences that were not designed for and that emerged from independent analysis:

1. **Pollock's undercutting defeaters and the *upādhi* / *apavāda* apparatus describe the
   same thing.** Two traditions a millennium apart, working on different material, arrived
   at the same distinction (`vedic_reasoning_methodology.md` §2.1).
2. **Nyāya's *hetvābhāsa* and the conflict taxonomy derived independently in
   `conflict_resolution.md` §3 nearly coincide.**
3. **The Mīmāṃsā interpretive priority ordering restates as a general theory of textual
   authority** that legal and clinical practice already follow informally (§4).

Convergent derivation from independent starting points is weak evidence, but it is the kind
of weak evidence worth noticing: these distinctions are more likely to be features of
codified normative reasoning as such than artefacts of any one tradition.

---

## 10. Open questions

1. ~~**Run the metric.**~~ **Done** — §6.1, portability 1.00 across four domains with a
   hold-out control. The remaining gap is that the prototype exercises a subset of the MIR,
   not the whole schema.
2. **F3** — does any domain have genuinely graded defeat? Now the highest-priority open
   question, and the one that would force a core change. The prototype cannot answer it
   because it has no defeat typing; testing F3 requires adding undercutting/rebutting
   defeat first.
3. **Context dimension proliferation.** L2 may add dimensions
   (`reasoning_ontology.md` §6.1); if each domain invents its own, cross-domain comparison
   becomes impossible. A registration discipline may be needed.
4. **Deontic depth.** Law needs contrary-to-duty conditionals and possibly a full deontic
   logic; CRL has modality tags only (`reasoning_language.md` §9.5). This is the most likely
   source of an F1 refutation.
5. **Cross-domain reasoning.** Precedence orderings are incomparable across domains by
   construction. Probably correct to forbid, but a medical-legal case genuinely spans both.
6. **Does engineering fit at all?** It is the least examined here. Much engineering reasoning
   is quantitative and model-based rather than rule-interpretive; the rule-governed part
   (code compliance) fits well, but that may be a minority of the domain.
