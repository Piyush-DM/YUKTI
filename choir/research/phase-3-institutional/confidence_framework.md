# 011 — Confidence Framework

**Status:** Draft for review
**Phase:** 3 — Institutional Reasoning
**Depends on:** `evidence_model.md`, `rule_extraction_framework.md`
**Feeds:** `explainability_framework.md`, `execution_pipeline.md`
**Reserved DAALE boundary:** `daale/ontology/confidence.py`
**Fills:** `choir/research/R004_Uncertainty_Representation.md` (currently empty)

---

## 1. Two governing rules

Everything in this document follows from two commitments.

> **1. Confidence is derived, never authored.**
> No extractor, no rule author, no reviewer may type a number. Confidence is a function of
> evidence structure. A hand-set confidence is an untraceable opinion wearing a number's
> clothing, and it cannot be explained, audited, or recomputed when the corpus changes.

> **2. Confidence is a vector, not a scalar.**
> Three orthogonal axes, which may be *presented* as a summary but must remain decomposable
> on demand. Collapsing them destroys the information a reviewer needs most.

---

## 2. Why one number is not enough

Consider three conclusions, each of which a single-scalar system would report identically:

| Case | Extraction | Interpretive | Inferential | What is actually true |
|---|---|---|---|---|
| A | High | High | Low | We know exactly what the rule says; the tradition agrees; the evidence here is thin |
| B | Low | High | High | The text is damaged, but everyone agrees what it means, and evidence is strong |
| C | High | Low | High | Clean text, strong evidence, **and a thousand-year interpretive dispute** |

These require completely different responses. Case A wants more evidence. Case B wants a
better manuscript. Case C wants a scholar, and no amount of additional data will help.

A scalar of ~0.6 for all three is not a compression; it is a loss of the diagnostic content.

---

## 3. The three axes

### 3.1 Extraction confidence — *did we read the text correctly?*

Set during compilation (`shloka_compiler.md` §10, `rule_extraction_framework.md` §6.1).

```
extraction = min( stage_confidences )
           × ambiguity_penalty( open_ambiguities )
           × attestation_factor( source_grade )
           × agreement_factor( dual_extraction )
```

| Input | Direction | Note |
|---|---|---|
| Weakest pipeline stage | Caps everything | **Minimum, not product** — §5.1 |
| Open ambiguities | ↓ | Unresolved readings; blocks execution entirely if any remain |
| Attestation grade | ↓ | critical edition > printed > corpus > quotation > unverified |
| Dual-extraction agreement | ↑ | Independent agreement raises it; disagreement caps it |
| Variant-dependent meaning | ↓ | `W-VARIANT` |
| Translation-only derivation | Hard ceiling | Grammatical justification chain absent |

### 3.2 Interpretive confidence — *does the tradition agree what it means?*

Set during extraction, revised as commentary is added.

| Input | Direction | Note |
|---|---|---|
| Commentarial agreement | ↑ | Across independent commentaries |
| Independent attestation | ↑ | Detected structurally via content addressing (`evidence_model.md` §4.3) |
| Translation convergence on structure | ↑ | Weak signal, but automatable |
| Recorded commentarial dispute | ↓ | |
| Differs by school | ↓ | And forces a context split |
| Scope inherited rather than stated | ↓ | *prakaraṇa* < *śruti* (`conflict_resolution.md` §5.2) |
| Exception completeness `unknown` | ↓ | We may not know what qualifies this rule |

The *prakaraṇa* < *śruti* row applies the Mīmāṃsā interpretive priority ordering as a direct
confidence input. This is a case where the tradition supplies not only a ranking but the
rationale for it.

### 3.3 Inferential confidence — *how strongly does the evidence support this conclusion?*

Computed at execution, from the two-layer evidence model (`evidence_model.md` §5.1).

| Input | Direction | Note |
|---|---|---|
| Independent supporting clusters | ↑ | **Clusters, not items** — §4.2 |
| Contradicting evidence | ↓ | Surviving contradiction after Layer 1 |
| Balanced evidence | → uncertainty | Raises the uncertainty component, not disbelief |
| Source authority of supporting rules | ↑ | Domain-supplied ranking |
| Rule specificity | ↑ | A specific rule that fires says more |
| Derivation depth | ↓ | Long defeasible chains attenuate |
| Defeaters checked and not fired | ↑ | **Only under the observability condition** |
| Defeater chain truncated | → uncertainty | Coverage is incomplete; must not read as support |
| Conflict resolved by a single contestable principle | ↓ | From `principles_unavailable` |

### 3.4 Composition — the axes do not multiply

```
reported_confidence = ⟨ extraction, interpretive, inferential ⟩

summary = min( extraction, interpretive, aggregate(inferential) )
```

**The summary is a minimum, not a product or an average.** A conclusion cannot be more
reliable than the reading of the text it rests on. If extraction is low, the conclusion is
low, regardless of how much evidence accumulated on top of a misreading.

Averaging would let strong inferential support compensate for a bad reading — which is
precisely backwards, and is how systems end up confidently wrong.

---

## 4. Emergence: how confidence is built

### 4.1 Formation and strength are separate

From `vedic_reasoning_methodology.md` §5.1 (R9): the corpus distinguishes whether a
combination **forms** (boolean) from how **strong** it is (graded). CHOIR preserves this.

```
forms?    ──▶ boolean; determined by conditions and defeaters
strength  ──▶ graded; determined by modulating influences
confidence──▶ graded; determined by evidence structure
```

These are three different things and collapsing any pair loses information:

- Formation × strength collapsed → cancellation becomes inexpressible, because cancellation
  operates on formation, not on strength.
- Strength × confidence collapsed → "a strong indication we are unsure about" cannot be
  distinguished from "a weak indication we are sure about."

The second confusion is extremely common in scoring systems and is worth guarding against
explicitly.

### 4.2 Evidence count is cluster count

Naive count of supporting items is the single largest source of overconfidence
(`evidence_model.md` §1). Confidence rises with **independent clusters**, not with items.

From the worked example in `evidence_model.md` §9: five apparently supporting items reduce
to one effective cluster plus two independent absence confirmations. A count-based system
would have overstated warrant roughly fivefold.

### 4.3 Saturation

```
aggregate(e₁ … eₙ) < ceiling( strongest_evidence_class )
```

An unbounded quantity of weak, correlated evidence must not approach certainty. A conclusion
supported only by weak indications is capped below one supported by a primary attested rule,
however many weak indications accumulate. Without saturation the system can be talked into
certainty by volume.

### 4.4 Absence-evidence is conditional

"No defeater fired" raises confidence **only if** the defeater corpus is complete for that
context (`evidence_model.md` §3.3). Where completeness is not declared, unfired defeaters
contribute **uncertainty**, not support.

This is the difference between:

- *"Jupiter is not in a kendra"* — sound; the chart is complete for positions.
- *"No cancelling yoga is present"* — **not** sound unless the cancellation corpus is
  complete, which it typically is not.

`canonical_shloka_analysis.md` §9.2 reports exactly this gap rather than treating the
unchecked exception-to-exception as absent.

---

## 5. Anti-patterns

Named explicitly because each is tempting, each looks rigorous, and each is wrong.

### 5.1 Multiplying dependent probabilities

`0.9 × 0.9 × 0.9 × 0.9 = 0.66` — from four stages that were each "very good," and which are
not independent (a bad segmentation causes a bad parse). Multiplication both understates
strong chains and dilutes a single catastrophic failure. **Use the minimum** where the
factors are stages of one chain.

### 5.2 False precision

`0.7342` implies a measurement that was never made. Confidence should be reported at a
granularity the inputs justify — for most of this corpus, an ordinal band
(`high / moderate / low / insufficient`) is the honest resolution, with the underlying
computation available for those who want it.

This connects to `reasoning_ontology.md` §3.1: strength values in the source are **ordinal**,
and arithmetic on ordinals is a category error the ontology is designed to make detectable.

### 5.3 Confidence laundering

A confident-looking number derived from unconfident inputs. Guarded against by §3.4's
minimum rule and by requiring decomposition on demand: any presented summary must be
expandable into its axes and their inputs.

### 5.4 Monotone accumulation

Every additional weak item nudging confidence upward, without bound. Guarded by saturation
(§4.3) and by clustering (§4.2).

### 5.5 Authored confidence

The rule this framework opens with. Any code path that permits a literal confidence value to
be attached to an object is a defect, not a convenience.

### 5.6 Treating unresolved as neutral

A *vikalpa* outcome is not "50/50." It is *two admissible alternatives*, each with its own
confidence vector. Averaging them into a middling scalar destroys the finding.

---

## 6. Presentation

Different audiences need different renderings of the same vector
(`explainability_framework.md` §6).

| Audience | Rendering |
|---|---|
| Practitioner | Ordinal band + the single largest limiting factor |
| Scholar | Full vector + interpretive inputs + commentarial dispute record |
| Auditor | Full vector + every input + the derivation |
| Subject | Ordinal band + plain statement of what is uncertain and why |

**The limiting factor must always be named.** "Moderate confidence" is much less useful than
"moderate confidence — limited by an unverified citation." The second tells the reader what
would change it, which is the actionable content.

---

## 7. Calibration

### 7.1 The honest position

**Confidence must be calibrated against something.** What that something is differs by
domain, and CHOIR must not pretend otherwise.

| Domain | Ground truth available? | Calibration target |
|---|---|---|
| Jyotiṣa | **No outcome ground truth** | **Textual fidelity + scholar agreement** |
| Law | Partial | Appellate outcomes; expert agreement |
| Medicine | Yes | Trial outcomes; guideline concordance |
| Finance | Yes | Realised outcomes |
| Engineering | Yes | Test and failure data |

For Jyotiṣa the calibration target is **fidelity, not prediction**
(`vedic_reasoning_methodology.md` §0.2). The question a well-calibrated CHOIR answers is
*"when the system says high confidence that the corpus asserts X, does it?"* — not
*"does X happen?"*

Stating this plainly is not a limitation; it is what makes the confidence numbers mean
something. A system that reported predictive confidence for Jyotiṣa would be reporting a
quantity it has no way to calibrate.

### 7.2 Methods

| Where ground truth exists | Method |
|---|---|
| Outcome-bearing domains | Brier score; reliability diagrams; per-band accuracy |
| Fidelity-calibrated domains | Scholar agreement rate per confidence band |

**Reliability by band** is the key check in both cases: of the conclusions reported at
"high," what fraction survive expert review? If high-band and moderate-band conclusions
survive at the same rate, the bands carry no information and the model is miscalibrated
regardless of its internal elegance.

### 7.3 Recalibration

Calibration data feeds back into the weights — which are **L2 domain configuration**
(`reasoning_ontology.md` §2.1), not core. Recalibration changes a domain's parameters, never
the framework's structure. This keeps the mechanism stable while the parameters learn.

---

## 8. Worked example

Chart A from `canonical_shloka_analysis.md` §9.1.

**Extraction axis**

| Input | Value |
|---|---|
| Stage minimum | Capped by S0 — `E-ATTEST`, no verifiable edition |
| Open ambiguities | 0 (all four resolved) |
| Attestation | `unverified` — lowest grade |
| Dual extraction | Not performed |
| → **extraction** | **Moderate**, limited by attestation |

**Interpretive axis**

| Input | Value |
|---|---|
| Structure uncontested | ↑ |
| Scope inherited (*prakaraṇa*), not stated | ↓ |
| Exception completeness `unknown` | ↓ |
| → **interpretive** | **Moderate-high** |

**Inferential axis**

| Input | Value |
|---|---|
| Independent supporting clusters | 1 (five items → one cluster; `evidence_model.md` §9) |
| Contradicting evidence | None |
| Defeaters checked, not fired | 3 — but **completeness not declared** → uncertainty, not support |
| Positive modulation (exaltation) | ↑ strength, **not** confidence |
| Derivation depth | 1 — shallow, good |
| → **inferential** | **Moderate**, limited by single cluster and undeclared completeness |

**Reported**

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

Three things to note:

1. **Strength is reported separately from confidence.** "A strong indication we are only
   moderately confident about" is expressible; a scalar system cannot say it.
2. **The limiting factor is named**, so the reader knows what would improve the answer.
3. **The coverage gap is stated**, not buried — the system reports what it did not check.

---

## 9. Open questions

1. **Ordinal or numeric internally?** Ordinal bands are honest for presentation, but
   aggregation operators want numbers. Whether to compute numerically and present ordinally
   (risking false precision leaking through) or to compute ordinally (losing resolution) is
   unresolved.
2. **Cluster reduction policy** — carried from `evidence_model.md` §10.1; it directly sets
   inferential confidence.
3. **Is the minimum rule too strict?** §3.4 lets one weak axis dominate. Defensible for
   extraction (a misreading really does poison everything) but possibly harsh for
   interpretive: a rule whose meaning is disputed may still be confidently *applicable* under
   one reading, reported via *vikalpa*.
4. **Calibrating interpretive confidence** requires scholar agreement data at scale, which
   does not currently exist for this corpus and would have to be produced.
5. **Uncertainty vs disbelief.** Subjective logic distinguishes them; the presentation layer
   currently does not. "We have no evidence" and "we have evidence against" must not render
   identically, and §6 does not yet specify how they differ.
6. **Confidence of resolutions.** A `Resolution` object has its own confidence
   (`conflict_resolution.md` §8). How that propagates into the confidence of conclusions
   downstream of the resolution is not specified here.
