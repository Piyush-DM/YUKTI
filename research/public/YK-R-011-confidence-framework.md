# Confidence Framework

| | |
|---|---|
| **Document ID** | YK-R-011 |
| **Source** | `choir/research/phase-3-institutional/confidence_framework.md` (011) |
| **Series** | CHOIR Research Programme |
| **Revision** | A |
| **Status** | Active |
| **Last Updated** | 2026-08-23 |

## Abstract

The source document specifies how CHOIR computes and reports confidence: as a three-axis vector — extraction, interpretive, inferential — derived from evidence structure rather than authored by any human, and summarised by the **minimum** of the three axes rather than by a product or an average (§1, §3.4). It names six anti-patterns it holds to be wrong (§5), states plainly that for Jyotiṣa there is no outcome ground truth and that the calibration target must therefore be textual fidelity rather than prediction (§7.1), and closes with six unresolved questions, including whether confidence should be computed ordinally or numerically at all (§9).

This publication is Active: the source document is drafted but **not accepted as specification**. Its own header records its status as "Draft for review," and per `MANIFESTO.md` every research document is a hypothesis — the manifesto's instruction is to treat every computational object as a hypothesis rather than an established truth.

## Research Question

The source does not carry a section labelled "research question." The question it sets out to answer is stated through its framing in §1–§3: how should a reasoning system represent and compute confidence such that the number is derivable rather than authored, and such that it does not destroy the diagnostic information a reviewer needs?

§2 poses this concretely. Three conclusions that a single-scalar system would report identically — roughly 0.6 for all three — are in fact in completely different situations, and "a scalar of ~0.6 for all three is not a compression; it is a loss of the diagnostic content" (§2).

The three axes are each stated as a question in the source's own headings (§3):

- Extraction confidence — *did we read the text correctly?* (§3.1)
- Interpretive confidence — *does the tradition agree what it means?* (§3.2)
- Inferential confidence — *how strongly does the evidence support this conclusion?* (§3.3)

§7.1 adds a further question the document treats as unavoidable: confidence must be calibrated against something, and the document asks what that something is per domain — for Jyotiṣa, *"when the system says high confidence that the corpus asserts X, does it?"* — not *"does X happen?"*

## Finding

### Two governing rules (§1)

The document states that everything in it follows from two commitments, given as block quotations:

> **1. Confidence is derived, never authored.**
> No extractor, no rule author, no reviewer may type a number. Confidence is a function of evidence structure. A hand-set confidence is an untraceable opinion wearing a number's clothing, and it cannot be explained, audited, or recomputed when the corpus changes.

> **2. Confidence is a vector, not a scalar.**
> Three orthogonal axes, which may be *presented* as a summary but must remain decomposable on demand. Collapsing them destroys the information a reviewer needs most.

### Why one number is not enough (§2)

The document works this through a three-case table:

| Case | Extraction | Interpretive | Inferential | What is actually true |
|---|---|---|---|---|
| A | High | High | Low | We know exactly what the rule says; the tradition agrees; the evidence here is thin |
| B | Low | High | High | The text is damaged, but everyone agrees what it means, and evidence is strong |
| C | High | Low | High | Clean text, strong evidence, **and a thousand-year interpretive dispute** |

Its conclusion is that these require completely different responses: "Case A wants more evidence. Case B wants a better manuscript. Case C wants a scholar, and no amount of additional data will help" (§2).

### The three axes (§3)

**Extraction confidence** (§3.1) is set during compilation, citing `shloka_compiler.md` §10 and `rule_extraction_framework.md` §6.1. The document gives it as:

```
extraction = min( stage_confidences )
           × ambiguity_penalty( open_ambiguities )
           × attestation_factor( source_grade )
           × agreement_factor( dual_extraction )
```

Its inputs are the weakest pipeline stage (which caps everything — a **minimum, not a product**, per §5.1); open ambiguities, which lower it and "block execution entirely if any remain"; attestation grade, ordered `critical edition > printed > corpus > quotation > unverified`; dual-extraction agreement, which raises it when independent extractions agree and caps it when they disagree; variant-dependent meaning (`W-VARIANT`), which lowers it; and translation-only derivation, which imposes a hard ceiling because the grammatical justification chain is absent.

**Interpretive confidence** (§3.2) is set during extraction and revised as commentary is added. Raising inputs: commentarial agreement across independent commentaries; independent attestation, "detected structurally via content addressing" (`evidence_model.md` §4.3); and translation convergence on structure, which the document marks as "a weak signal, but automatable." Lowering inputs: recorded commentarial dispute; a reading that differs by school (which also forces a context split); scope inherited rather than stated — *prakaraṇa* < *śruti*, citing `conflict_resolution.md` §5.2; and exception completeness recorded as `unknown`, on the grounds that "we may not know what qualifies this rule."

On the *prakaraṇa* < *śruti* row the document notes that it "applies the Mīmāṃsā interpretive priority ordering as a direct confidence input. This is a case where the tradition supplies not only a ranking but the rationale for it" (§3.2).

**Inferential confidence** (§3.3) is computed at execution from the two-layer evidence model (`evidence_model.md` §5.1). Its inputs are independent supporting clusters (**clusters, not items**, per §4.2); contradicting evidence surviving Layer 1; balanced evidence, which raises "the uncertainty component, not disbelief"; source authority of supporting rules, from a domain-supplied ranking; rule specificity, since "a specific rule that fires says more"; derivation depth, where long defeasible chains attenuate; defeaters checked and not fired, which raise confidence **only under the observability condition**; a truncated defeater chain, which yields uncertainty because "coverage is incomplete; must not read as support"; and conflict resolved by a single contestable principle, drawn from `principles_unavailable`, which lowers it.

**Composition** (§3.4). The document is explicit that the axes do not multiply:

```
reported_confidence = ⟨ extraction, interpretive, inferential ⟩

summary = min( extraction, interpretive, aggregate(inferential) )
```

"**The summary is a minimum, not a product or an average.** A conclusion cannot be more reliable than the reading of the text it rests on. If extraction is low, the conclusion is low, regardless of how much evidence accumulated on top of a misreading" (§3.4). Averaging, it argues, "would let strong inferential support compensate for a bad reading — which is precisely backwards, and is how systems end up confidently wrong."

### Emergence (§4)

**Formation and strength are separate** (§4.1). Citing `vedic_reasoning_methodology.md` §5.1 (R9), the document states that the corpus distinguishes whether a combination **forms** (boolean) from how **strong** it is (graded), and that CHOIR preserves this:

```
forms?    ──▶ boolean; determined by conditions and defeaters
strength  ──▶ graded; determined by modulating influences
confidence──▶ graded; determined by evidence structure
```

Collapsing formation with strength makes cancellation inexpressible, "because cancellation operates on formation, not on strength." Collapsing strength with confidence means "a strong indication we are unsure about" cannot be distinguished from "a weak indication we are sure about." The document records that "the second confusion is extremely common in scoring systems and is worth guarding against explicitly."

**Evidence count is cluster count** (§4.2). Naive counting of supporting items is called "the single largest source of overconfidence" (`evidence_model.md` §1). From the worked example in `evidence_model.md` §9, five apparently supporting items reduce to one effective cluster plus two independent absence confirmations; "a count-based system would have overstated warrant roughly fivefold."

**Saturation** (§4.3):

```
aggregate(e₁ … eₙ) < ceiling( strongest_evidence_class )
```

An unbounded quantity of weak, correlated evidence must not approach certainty; a conclusion supported only by weak indications is capped below one supported by a primary attested rule, "however many weak indications accumulate. Without saturation the system can be talked into certainty by volume."

**Absence-evidence is conditional** (§4.4). "No defeater fired" raises confidence **only if** the defeater corpus is complete for that context (`evidence_model.md` §3.3); where completeness is not declared, unfired defeaters contribute **uncertainty, not support**. The document contrasts *"Jupiter is not in a kendra"* — sound, because the chart is complete for positions — with *"No cancelling yoga is present"* — **not** sound unless the cancellation corpus is complete, "which it typically is not." It records that `canonical_shloka_analysis.md` §9.2 reports exactly this gap rather than treating the unchecked exception-to-exception as absent.

### Anti-patterns (§5)

The document names six, "because each is tempting, each looks rigorous, and each is wrong."

| # | Anti-pattern | The document's position |
|---|---|---|
| §5.1 | Multiplying dependent probabilities | `0.9 × 0.9 × 0.9 × 0.9 = 0.66` from four stages each "very good" and not independent (a bad segmentation causes a bad parse). Multiplication "both understates strong chains and dilutes a single catastrophic failure." **Use the minimum** where the factors are stages of one chain. |
| §5.2 | False precision | `0.7342` "implies a measurement that was never made." For most of this corpus an ordinal band (`high / moderate / low / insufficient`) "is the honest resolution," with the underlying computation available on request. Connects to `reasoning_ontology.md` §3.1: strength values in the source are **ordinal**, and arithmetic on ordinals "is a category error the ontology is designed to make detectable." |
| §5.3 | Confidence laundering | A confident-looking number derived from unconfident inputs. Guarded by §3.4's minimum rule and by requiring decomposition on demand: any presented summary must be expandable into its axes and their inputs. |
| §5.4 | Monotone accumulation | Every additional weak item nudging confidence upward without bound. Guarded by saturation (§4.3) and clustering (§4.2). |
| §5.5 | Authored confidence | "Any code path that permits a literal confidence value to be attached to an object is a defect, not a convenience." |
| §5.6 | Treating unresolved as neutral | A *vikalpa* outcome "is not '50/50.' It is *two admissible alternatives*, each with its own confidence vector. Averaging them into a middling scalar destroys the finding." |

### Presentation (§6)

Different audiences need different renderings of the same vector, citing `explainability_framework.md` §6:

| Audience | Rendering |
|---|---|
| Practitioner | Ordinal band + the single largest limiting factor |
| Scholar | Full vector + interpretive inputs + commentarial dispute record |
| Auditor | Full vector + every input + the derivation |
| Subject | Ordinal band + plain statement of what is uncertain and why |

"**The limiting factor must always be named.** 'Moderate confidence' is much less useful than 'moderate confidence — limited by an unverified citation.' The second tells the reader what would change it, which is the actionable content" (§6).

### Calibration (§7)

§7.1 is headed "The honest position." Confidence must be calibrated against something; what that something is differs by domain, "and CHOIR must not pretend otherwise."

| Domain | Ground truth available? | Calibration target |
|---|---|---|
| Jyotiṣa | **No outcome ground truth** | **Textual fidelity + scholar agreement** |
| Law | Partial | Appellate outcomes; expert agreement |
| Medicine | Yes | Trial outcomes; guideline concordance |
| Finance | Yes | Realised outcomes |
| Engineering | Yes | Test and failure data |

For Jyotiṣa the calibration target is **fidelity, not prediction** (`vedic_reasoning_methodology.md` §0.2). The document states that stating this plainly "is not a limitation; it is what makes the confidence numbers mean something. A system that reported predictive confidence for Jyotiṣa would be reporting a quantity it has no way to calibrate" (§7.1).

Methods (§7.2): Brier score, reliability diagrams and per-band accuracy where ground truth exists; scholar agreement rate per confidence band for fidelity-calibrated domains. **Reliability by band** is named as the key check in both cases: "of the conclusions reported at 'high,' what fraction survive expert review? If high-band and moderate-band conclusions survive at the same rate, the bands carry no information and the model is miscalibrated regardless of its internal elegance."

Recalibration (§7.3): calibration data feeds back into the weights, which are **L2 domain configuration** (`reasoning_ontology.md` §2.1), not core. "Recalibration changes a domain's parameters, never the framework's structure."

### Worked example (§8)

Chart A, from `canonical_shloka_analysis.md` §9.1.

On the extraction axis, the stage minimum is capped by S0 — `E-ATTEST`, no verifiable edition; open ambiguities are 0 (all four resolved); attestation is `unverified`, the lowest grade; dual extraction was not performed. The axis resolves to **moderate**, limited by attestation.

On the interpretive axis, structure is uncontested (raising); scope is inherited (*prakaraṇa*), not stated (lowering); exception completeness is `unknown` (lowering). The axis resolves to **moderate-high**.

On the inferential axis, independent supporting clusters number 1 (five items reduced to one cluster, `evidence_model.md` §9); there is no contradicting evidence; three defeaters were checked and did not fire, "but **completeness not declared** → uncertainty, not support"; positive modulation (exaltation) raises **strength, not confidence**; derivation depth is 1, "shallow, good." The axis resolves to **moderate**, limited by the single cluster and undeclared completeness.

The reported output is given as:

```
Gajakesarī: INDICATED

confidence   = ⟨ extraction: moderate,
                 interpretive: moderate-high,
                 inferential: moderate ⟩
summary      = moderate                      (minimum of the three)
strength     = elevated                      (exaltation modulates — SEPARATE axis)
limiting factor = unverified citation (E-ATTEST)
coverage note   = defeater corpus completeness not declared
```

The document draws three points from this: strength is reported separately from confidence, so that "a strong indication we are only moderately confident about" is expressible where a scalar system cannot say it; the limiting factor is named, "so the reader knows what would improve the answer"; and the coverage gap is stated rather than buried — "the system reports what it did not check" (§8).

### Negative results and admissions recorded by the source

The document does not present the framework as complete or validated. It records that: the Jyotiṣa domain has **no outcome ground truth** at all (§7.1); calibrating interpretive confidence "requires scholar agreement data at scale, which does not currently exist for this corpus and would have to be produced" (§9.4); the presentation layer does not currently distinguish uncertainty from disbelief, and §6 "does not yet specify how they differ" (§9.5); whether confidence is computed ordinally or numerically internally is unresolved (§9.1); the minimum rule may be too strict for the interpretive axis (§9.3); and propagation of a `Resolution` object's own confidence into downstream conclusions "is not specified here" (§9.6). In the worked example, defeater-corpus completeness was **not declared**, so three unfired defeaters were counted as uncertainty rather than support (§8).

## Architectural Implications

The source names a reserved DAALE boundary for this work: `daale/ontology/confidence.py`. It also records that it **fills** `choir/research/R004_Uncertainty_Representation.md`, which it describes as "currently empty."

The following constraints follow from the document's own stated commitments:

- **No API may accept an authored confidence value.** Under §1 rule 1 and §5.5, "any code path that permits a literal confidence value to be attached to an object is a defect, not a convenience." This applies to extractors, rule authors and reviewers alike.
- **Confidence is stored and passed as a three-element vector**, not a scalar. A summary may be presented, but §1 rule 2 and §5.3 require it to remain decomposable on demand into its axes and their inputs.
- **Aggregation uses minimum, not product or average**, where the factors are stages of one chain (§3.4, §5.1). Extraction acts as a hard cap on the reported summary.
- **Strength, formation and confidence are three separate fields** (§4.1). Formation is boolean; strength and confidence are graded and are determined by different things — modulating influences versus evidence structure. The worked example reports `strength = elevated` alongside `summary = moderate` (§8).
- **Evidence aggregation counts independent clusters, and is saturating** (§4.2, §4.3). Item counts must not drive confidence, and no accumulation of weak correlated evidence may approach the ceiling of the strongest evidence class present.
- **Absence-of-defeater is conditional on a declared completeness flag** (§4.4). Where completeness is not declared, the unfired defeaters must contribute uncertainty and the coverage gap must be surfaced, not suppressed.
- **Open ambiguities block execution.** §3.1 records that unresolved readings block execution entirely if any remain.
- **Presentation must always name the limiting factor** (§6), and must render per audience: practitioner, scholar, auditor, subject.
- **Confidence weights are L2 domain configuration, not core** (§7.3, citing `reasoning_ontology.md` §2.1). Recalibration is a parameter change within a domain; it must not alter the framework's structure.
- **Ordinals must not be arithmetically combined.** §5.2 ties this to `reasoning_ontology.md` §3.1, where the ontology is stated to be designed to make such a category error detectable.
- **Domain onboarding must declare a calibration target** (§7.1). For Jyotiṣa that target is textual fidelity plus scholar agreement, and the system must not report predictive confidence for it.

## Open Questions

The source records six, in §9, reproduced here in its own terms:

1. **Ordinal or numeric internally?** Ordinal bands are honest for presentation, but aggregation operators want numbers. Whether to compute numerically and present ordinally (risking false precision leaking through) or to compute ordinally (losing resolution) is unresolved.
2. **Cluster reduction policy** — carried from `evidence_model.md` §10.1; it directly sets inferential confidence.
3. **Is the minimum rule too strict?** §3.4 lets one weak axis dominate. The document calls this defensible for extraction — "a misreading really does poison everything" — but "possibly harsh for interpretive: a rule whose meaning is disputed may still be confidently *applicable* under one reading, reported via *vikalpa*."
4. **Calibrating interpretive confidence** requires scholar agreement data at scale, "which does not currently exist for this corpus and would have to be produced."
5. **Uncertainty vs disbelief.** Subjective logic distinguishes them; the presentation layer currently does not. "We have no evidence" and "we have evidence against" must not render identically, and §6 does not yet specify how they differ.
6. **Confidence of resolutions.** A `Resolution` object has its own confidence (`conflict_resolution.md` §8). How that propagates into the confidence of conclusions downstream of the resolution is not specified here.

Two further items are recorded outside §9 and remain unsettled in this document: the Jyotiṣa domain has no outcome ground truth against which predictive confidence could ever be checked (§7.1), and in the worked example the defeater corpus completeness is not declared, leaving coverage incomplete (§8).

## Related Documents

Dependencies declared by the source:

- [YK-R-009 — Evidence Model](YK-R-009-evidence-model.md) — `evidence_model.md`; supplies the two-layer evidence model (§3.3), clustering and overconfidence (§4.2), content-addressed independent attestation (§3.2), the completeness condition for absence-evidence (§4.4), and the worked five-items-to-one-cluster reduction (§8).
- [YK-R-007 — Rule Extraction Framework](YK-R-007-rule-extraction-framework.md) — `rule_extraction_framework.md` §6.1; where extraction confidence is set.

Documents the source says it feeds:

- [YK-R-012 — Explainability Framework](YK-R-012-explainability-framework.md) — `explainability_framework.md` §6; the per-audience rendering of the vector (§6).
- [YK-R-015 — Execution Pipeline](YK-R-015-execution-pipeline.md) — `execution_pipeline.md`.

Documents the source cites:

- [YK-R-002 — Reasoning Ontology](YK-R-002-reasoning-ontology.md) — `reasoning_ontology.md` §3.1 (ordinal strength values) and §2.1 (weights as L2 domain configuration).
- [YK-R-004 — Vedic Reasoning Methodology](YK-R-004-vedic-reasoning-methodology.md) — `vedic_reasoning_methodology.md` §5.1 (R9), formation versus strength; §0.2, fidelity not prediction.
- [YK-R-006 — Shloka Compiler](YK-R-006-shloka-compiler.md) — `shloka_compiler.md` §10; where extraction confidence is set during compilation.
- [YK-R-008 — Canonical Shloka Analysis (Benchmark)](YK-R-008-canonical-shloka-analysis-benchmark.md) — `canonical_shloka_analysis.md` §9.1 (Chart A, the worked example) and §9.2 (the reported coverage gap).
- [YK-R-010 — Conflict Resolution](YK-R-010-conflict-resolution.md) — `conflict_resolution.md` §5.2 (*prakaraṇa* < *śruti*) and §8 (the confidence of a `Resolution`).
