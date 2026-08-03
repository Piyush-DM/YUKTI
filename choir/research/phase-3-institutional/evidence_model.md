# 009 — Evidence Model

**Status:** Draft for review
**Phase:** 3 — Institutional Reasoning
**Depends on:** `computational_primitives.md`, `vedic_reasoning_methodology.md`
**Feeds:** `confidence_framework.md`, `conflict_resolution.md`, `explainability_framework.md`
**Reserved DAALE boundary:** `daale/ontology/evidence.py`
**Fills:** `choir/research/R003_Evidence_Representation.md` (currently empty)

---

## 1. The problem the model must solve

Institutional reasoning accumulates. A conclusion is rarely licensed by one rule; it is
supported by several, opposed by others, qualified by exceptions, and weighted by the
authority of its sources. The model must say how that accumulation works.

The naive approach — count supporting items, count contradicting items, subtract — fails on
a specific and pervasive problem:

> **Evidence items are not independent, and treating them as if they were is the dominant
> source of overconfidence in rule-based systems.**

Five verses restating one rule are not five reasons. Two clinical guidelines citing the same
trial are not two studies. Three appellate decisions following one precedent are not three
authorities. Each of these looks like accumulating support and is in fact one piece of
evidence counted repeatedly.

§4 is the core of this document, and correlation handling is the reason it is long.

---

## 2. What evidence is

Per `computational_primitives.md` §3.11, evidence is not data. Data is raw; evidence is data
*plus a bearing relation to a specific claim*.

```
Evidence ::= {
  id            : ContentAddress
  claim         : PropositionRef        # what it bears on — REQUIRED
  polarity      : supporting | contradicting | balanced
  weight        : Graded                # derived, never authored
  pramāṇa       : EvidenceType          # §3
  derivation    : direct | derived | inherited   # §4.1
  independence  : IndependenceKey       # §4.2 — the critical field
  source        : Provenance
  context       : ContextRef
  valid_time    : Interval
  defeated_by   : [ ExceptionRef ]      # marked, never deleted
  status        : active | defeated | superseded
}
```

The `claim` field is mandatory because the same observation is evidence for one proposition
and irrelevant to another. Storing evidence without its claim produces a pool of facts that
cannot be aggregated.

---

## 3. Evidence types

The typology follows the *pramāṇa* framework (`vedic_reasoning_methodology.md` §2), which
turns out to be a better fit than the usual source-type taxonomies because it classifies by
*how the knowledge was acquired*, which is what determines its defeat conditions.

| Type | *Pramāṇa* | Acquisition | Defeated by |
|---|---|---|---|
| `direct` | *pratyakṣa* | Observation / measurement / chart input | Instrument error; misreading |
| `derived` | *anumāna* | Rule application | Defeat of the rule or its inputs |
| `analogical` | *upamāna* | Structural correspondence to a precedent | Disanalogy in a relevant respect |
| `attested` | *śabda* | Statement in an authoritative source | Source authority challenge; misreading |
| `abductive` | *arthāpatti* | Best available explanation | A better explanation |
| `absence` | *anupalabdhi* | **Non-observation where observation was expected** | Failure of the observability condition |

### 3.1 `attested` is first-class

In every domain CHOIR targets, textual authority is a primary means of knowledge, not a
fallback. A statute *is* the evidence. A śāstric verse *is* the evidence. This is what makes
these normative rather than empirical systems, and it is why source-authority ranking
(`conflict_resolution.md` §5.3) is central machinery rather than a tiebreaker.

### 3.2 `analogical` must carry its limits

An analogical evidence item must record the mapped correspondences **and the relations not
mapped**. An analogy without stated limits cannot be defeated by disanalogy, and an
undefeatable defeasible inference is a contradiction in terms.

### 3.3 `absence` and the observability condition

The classical formulation of *anupalabdhi* includes a restriction that modern closed-world
reasoning routinely drops:

> Non-apprehension licenses denial **only where apprehension would have occurred** had the
> thing been present.

Absence-evidence is therefore admissible only where the context **declares the relevant
domain complete**:

```
Absence(P) is admissible in context C
  iff C.completeness_declaration covers domain(P)
```

Without the declaration, "not observed" means *unknown*, not *false*.

| Domain | Where the declaration is safe | Where it is not |
|---|---|---|
| Jyotiṣa | Planetary positions — the chart is complete by construction | Yogas: the corpus is not exhaustively extracted |
| Law | An exhaustive statutory list | Case law — always potentially incomplete |
| Medicine | A completed test panel | Undocumented history |

The Jyotiṣa row is instructive. "Jupiter is not in a kendra" is sound absence-reasoning: the
chart fixes all positions. "No cancelling yoga is present" is **not** sound unless the
cancellation corpus is complete — which, per `rule_extraction_framework.md` §2.1, it is
typically not. This is exactly the gap `canonical_shloka_analysis.md` §9.2 reports as
`incomplete_defeater_analysis` rather than concealing.

**Who declares completeness** is unresolved (`vedic_reasoning_methodology.md` §8.4). The
declaration is itself an authority claim and should carry provenance.

---

## 4. Independence — the core of the model

### 4.1 Derivation classes

| Class | Meaning | Independence |
|---|---|---|
| `direct` | Observed at the source | Independent unless the instrument is shared |
| `derived` | Produced by a rule from other evidence | **Shares the ancestry of its inputs** |
| `inherited` | Holds by virtue of a structural relation (subclass, part-of) | **Fully dependent on the parent** |

Inherited evidence is the most dangerous, because it multiplies effortlessly. If a property
inherits down a class hierarchy, every subclass instance appears to contribute fresh
support for a claim about the parent — a straightforward double count.

### 4.2 The independence key

Every evidence item carries an `IndependenceKey`: a structure identifying **what it
ultimately rests on**.

```
IndependenceKey ::= {
  root_sources   : set of SourceID       # texts / observations at the base
  root_rules     : set of RuleID         # rules in the derivation
  kernel_versions: set of KernelRef      # computations relied upon
}
```

Two evidence items are **independent** iff their keys are disjoint. They are **correlated**
to the degree their keys overlap.

This is computable rather than estimated, because `derives_from` closure is already
maintained for the traceability invariant (`computational_primitives.md` §3.16). The
independence key is the same closure, projected onto roots. **Correlation detection comes
free from a mechanism the system needs anyway** — which is a strong argument for the
reification-heavy storage design in `knowledge_graph_spec.md`.

### 4.3 Independent attestation, detected structurally

Content addressing (`reasoning_ontology.md` §7.2) unifies two textual statements of the
same rule into one rule with two provenance records. That is a *genuine* independence
signal: two texts, two transmission lines, one rule.

Contrast with two rules derived from the same verse — same root source, fully correlated,
no additional support. The system distinguishes these without a heuristic, because the
identity scheme already does.

**The remaining hard case** is textual dependence: text B copies text A. Two provenance
records exist, but they are not independent transmissions. Detecting this requires
philological stemma information — which text descends from which — and that is
domain-expert input, not computation. The model provides the field (`source.stemma_parent`)
and cannot populate it automatically.

### 4.4 Aggregation with correlation discount

Aggregation operates on the **independence partition**, not on the item list:

```
1. Partition evidence for a claim into correlation clusters
   (items sharing root sources / rules)
2. Reduce each cluster to a single effective item
   — weight = strongest in cluster, NOT the sum
3. Aggregate across clusters using a saturating operator
```

Step 2 is deliberately conservative: five restatements of one rule contribute what the
strongest single statement contributes. They may raise *interpretive* confidence — the
tradition evidently agreed — but they do not multiply *inferential* support. The two axes
stay separate (`confidence_framework.md` §3).

---

## 5. Aggregation operators assessed

| Approach | Fit | Verdict |
|---|---|---|
| **Bayesian** | Requires priors and a likelihood model. Neither is available for a normative corpus — there is no base rate for "a statute means X" | ✗ Not as the primary operator |
| **Dempster–Shafer** | Represents ignorance explicitly (a genuine advantage), but Dempster's rule behaves pathologically under high conflict, producing counterintuitive results precisely where conflict matters most | ✗ Rejected on that failure |
| **Subjective logic** | Opinion triples ⟨belief, disbelief, uncertainty⟩; handles ignorance without the conflict pathology; supports source discounting | ✅ Good fit for the graded layer |
| **Argumentation (Dung / ASPIC+)** | Determines which arguments *survive* attack. Exactly right for defeasible structure; but binary — no gradation | ✅ Good fit for the structural layer |
| **Weighted voting** | Simple, explainable; ignores structure and correlation entirely | ✗ Too naive alone |

### 5.1 Decision: two layers, in order

> **Structure first, then gradation. Never both in one number.**

```
   Layer 1 — STRUCTURAL (argumentation)
   Which arguments survive defeat?
   Output: a set of surviving arguments. Binary. Explainable.
        │
        │  only survivors proceed
        ▼
   Layer 2 — GRADED (correlation-aware, saturating)
   How strongly do the survivors support the claim?
   Output: a graded opinion with an uncertainty component.
```

The reason for the ordering is that **defeat is not a matter of degree**. An undercut
inference is withdrawn, not weakened (`canonical_shloka_analysis.md` §9.2). Folding defeat
into a weight makes a defeated inference contribute a small positive amount, which is both
wrong and unexplainable — the system would be saying "this rule was cancelled, so it counts
slightly."

Layer 1 also produces the material the explanation needs: what attacked what, and what
survived (`explainability_framework.md` §5).

### 5.2 Saturation requirement

The Layer 2 operator must be **saturating**: an unbounded quantity of weak, weakly-correlated
evidence must not approach certainty.

```
aggregate(e₁ … eₙ) < ceiling(strongest_evidence_class)
```

A conclusion supported only by weak indications is capped below one supported by a primary
attested rule, regardless of count. Without this, the system can be talked into certainty by
volume — the characteristic failure of additive scoring schemes.

---

## 6. Polarity, and why "neutral" is two things

| Polarity | Meaning | Store against the claim? | Informative? |
|---|---|---|---|
| `supporting` | Raises warrant | ✅ | ✅ |
| `contradicting` | Lowers warrant | ✅ | ✅ |
| `balanced` | Bears on the claim, symmetric effect | ✅ | ✅ **Yes** |
| *(irrelevant)* | No bearing | ❌ **Do not store** | ✗ |

Collapsing these into one "neutral" value conflates *"we looked and it cuts both ways"* with
*"this has nothing to do with the claim."* The first is a finding; the second is noise. A
claim with substantial balanced evidence is in a very different epistemic position from one
with none, and the explanation must be able to say so.

`balanced` is the evidential counterpart of *satpratipakṣa* (`vedic_reasoning_methodology.md`
§2.2) — the tradition's name for a genuinely counterbalanced reason — and it feeds the
*vikalpa* outcome in `conflict_resolution.md` §7.

---

## 7. Strength

Evidence weight is **derived** from structural properties, never authored
(`computational_primitives.md` §3.14).

| Input | Effect | Notes |
|---|---|---|
| Evidence type | Type-specific ceiling | `attested` from a primary source > `analogical` |
| Source authority | Scales weight | **Domain-supplied ranking** (L2, per `reasoning_ontology.md` §2.1) |
| Rule specificity | More specific → higher when it fires | *lex specialis* as a weight, not only as precedence |
| Derivation depth | Longer chains → attenuated | Each defeasible step compounds uncertainty |
| Extraction confidence | Caps the weight | Cannot rely more on a rule than on the reading of it |
| Attestation independence | Raises interpretive weight only | §4.3 — not inferential weight |

**Derivation depth attenuation** is worth stating explicitly: a conclusion four defeasible
inferences deep is weaker than one directly supported, even if every step looked strong.
Long chains are where rule systems quietly become fiction.

---

## 8. Lifecycle and the non-destruction invariant

```
proposed ──▶ admitted ──▶ active ──┬──▶ defeated   (marked, retained)
                │                  ├──▶ superseded (new version)
                │                  └──▶ withdrawn  (source retracted)
                └──▶ rejected (recorded with reason)
```

**Defeated evidence is never deleted** (`knowledge_graph_spec.md` I5). Three reasons:

1. The explanation must say what was considered and rejected — a conclusion reached after
   weighing contrary evidence differs from one reached in ignorance of it, even when the
   conclusion is identical.
2. Defeat is context-relative. Evidence defeated in one context may be live in another.
3. Defeaters can themselves be defeated (*nīca-bhaṅga*), which restores the original — and
   restoration is impossible if the evidence was removed.

**Withdrawal is different from defeat**: a source retracted, an extraction found erroneous.
Withdrawn evidence is also retained, but conclusions depending on it are flagged for
re-derivation rather than merely re-weighted.

---

## 9. Worked example

From `canonical_shloka_analysis.md` §9.1 — the evidence supporting `forms(Gajakesari)` in
Chart A:

| # | Evidence | Type | Polarity | Independence root |
|---|---|---|---|---|
| e1 | Rule `gajakesari_formation` fired | `derived` | supporting | `{source: TBD-verse, rule: gajakesari_formation}` |
| e2 | position(Guru) = Karka | `direct` | supporting | `{chart_input}` |
| e3 | position(Candra) = Meṣa | `direct` | supporting | `{chart_input}` |
| e4 | debilitation defeater not fired | `absence` | supporting | `{ontology:debilitation_table}` |
| e5 | combustion defeater not fired | `absence` | supporting | `{kernel:combustion, chart_input}` |
| e6 | exalted(Guru, Karka) | `attested` | *modulating* | `{ontology:exaltation_table}` |

**Correlation analysis:**

- e2 and e3 share `chart_input` → **one cluster**. Two positions from one chart are not two
  independent observations of the yoga's formation.
- e1 derives from e2 and e3 → **same cluster**; e1 is not additional support, it is the
  *conclusion* of that cluster.
- e4 and e5 are absence-evidence resting on different roots → independent of each other, but
  **admissible only under the observability condition** (§3.3). The chart is complete for
  positions, so both are sound. Note that "no *other* cancelling condition exists" would
  **not** be sound, and is correctly not claimed.
- e6 is an **influence**, not support for formation (`computational_primitives.md` §3.7). It
  modulates the strength of the indication and must not enter the support tally.

**Result:** one effective supporting cluster, two independent absence confirmations, one
positive modulation. Naive counting would have reported *five supporting items*, and would
have overstated the warrant roughly fivefold.

---

## 10. Open questions

1. **Cluster reduction policy.** §4.4 takes the strongest item in a cluster. An alternative
   is a within-cluster diminishing sum. The conservative choice is taken because
   overconfidence is the failure mode being guarded against, but it may under-credit genuine
   partial independence.
2. **Textual stemma.** §4.3 cannot detect copying between texts without philological input.
   How much of the corpus this affects is unknown and could be substantial.
3. **Completeness declarations.** Who may declare a domain complete for absence-reasoning,
   and with what authority? Unresolved, and it gates a whole evidence type.
4. **Is `balanced` stable under re-evaluation?** Evidence balanced at one point may become
   unbalanced when more is extracted. Whether balance should be recomputed or recorded as of
   a decision time interacts with the tri-temporal model.
5. **Cross-context aggregation.** Whether evidence from a more general context contributes to
   a specific-context claim (lattice-upward closure) is the same open question as
   `knowledge_graph_spec.md` §8.2, and it has a large effect on evidence volume.
6. **Subjective-logic parameterisation.** §5 selects the family; the specific fusion operator
   (cumulative, averaging, weighted) is not fixed, and the choice matters for how
   independent sources combine.
