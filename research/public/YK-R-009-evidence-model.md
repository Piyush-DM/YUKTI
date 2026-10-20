# Evidence Model

| | |
|---|---|
| **Document ID** | YK-R-009 |
| **Source** | `choir/research/phase-3-institutional/evidence_model.md` (009) |
| **Series** | CHOIR Research Programme |
| **Revision** | A |
| **Status** | Active |
| **Last Updated** | 2026-08-23 |

## Abstract

The document specifies how CHOIR represents an evidence item, how evidence items are typed
by *pramāṇa*, and how they are aggregated in support of a claim (§2, §3, §4). Its central
commitment is that evidence items are not independent, and that treating them as if they were
is "the dominant source of overconfidence in rule-based systems" (§1) — so aggregation runs
over an independence partition rather than over an item list (§4.4), with defeasible structure
settled before any grading is applied (§5.1). The source carries its own status line, **Draft
for review**; this publication is drafted but not accepted as specification, and per
`MANIFESTO.md` every research document is a hypothesis.

## Research Question

The source states the problem directly in §1: institutional reasoning accumulates, and "the
model must say how that accumulation works." A conclusion is "rarely licensed by one rule; it
is supported by several, opposed by others, qualified by exceptions, and weighted by the
authority of its sources" (§1). The question is therefore how to accumulate evidence for a
claim without the naive method — count supporting items, count contradicting items, subtract
— which the source says fails on a specific and pervasive problem, stated in §1 as a
displayed claim:

> **Evidence items are not independent, and treating them as if they were is the dominant
> source of overconfidence in rule-based systems.**

The source names its own centre of gravity: "§4 is the core of this document, and correlation
handling is the reason it is long" (§1).

## Finding

### Evidence is data plus a bearing relation

Per `computational_primitives.md` §3.11, cited in §2, evidence is not data: "Data is raw;
evidence is data *plus a bearing relation to a specific claim*." The record carries `id`,
`claim`, `polarity`, `weight`, `pramāṇa`, `derivation`, `independence`, `source`, `context`,
`valid_time`, `defeated_by`, and `status` (§2). Two properties of the schema are asserted in
the surrounding prose: `weight` is "derived, never authored", and `defeated_by` entries are
"marked, never deleted". The `claim` field is mandatory "because the same observation is
evidence for one proposition and irrelevant to another. Storing evidence without its claim
produces a pool of facts that cannot be aggregated" (§2). The `independence` field is labelled
in the schema itself as "the critical field".

### The typology follows *pramāṇa*, because acquisition determines defeat

§3 adopts the *pramāṇa* framework of `vedic_reasoning_methodology.md` §2, on the stated
ground that it "turns out to be a better fit than the usual source-type taxonomies because it
classifies by *how the knowledge was acquired*, which is what determines its defeat
conditions."

| Type | *Pramāṇa* | Acquisition | Defeated by |
|---|---|---|---|
| `direct` | *pratyakṣa* | Observation / measurement / chart input | Instrument error; misreading |
| `derived` | *anumāna* | Rule application | Defeat of the rule or its inputs |
| `analogical` | *upamāna* | Structural correspondence to a precedent | Disanalogy in a relevant respect |
| `attested` | *śabda* | Statement in an authoritative source | Source authority challenge; misreading |
| `abductive` | *arthāpatti* | Best available explanation | A better explanation |
| `absence` | *anupalabdhi* | **Non-observation where observation was expected** | Failure of the observability condition |

Three consequences are drawn. `attested` is first-class (§3.1): "In every domain CHOIR
targets, textual authority is a primary means of knowledge, not a fallback. A statute *is* the
evidence. A śāstric verse *is* the evidence." This is why source-authority ranking
(`conflict_resolution.md` §5.3) is "central machinery rather than a tiebreaker" (§3.1).
`analogical` evidence must record the mapped correspondences **and the relations not mapped**,
because "an analogy without stated limits cannot be defeated by disanalogy, and an
undefeatable defeasible inference is a contradiction in terms" (§3.2).

### `absence` carries the observability condition

§3.3 restores a restriction on *anupalabdhi* that the source says "modern closed-world
reasoning routinely drops":

> Non-apprehension licenses denial **only where apprehension would have occurred** had the
> thing been present.

Formally, absence-evidence is admissible only where the context declares the relevant domain
complete: `Absence(P) is admissible in context C iff C.completeness_declaration covers
domain(P)`. Without the declaration, "'not observed' means *unknown*, not *false*" (§3.3).

| Domain | Where the declaration is safe | Where it is not |
|---|---|---|
| Jyotiṣa | Planetary positions — the chart is complete by construction | Yogas: the corpus is not exhaustively extracted |
| Law | An exhaustive statutory list | Case law — always potentially incomplete |
| Medicine | A completed test panel | Undocumented history |

The Jyotiṣa row is called instructive (§3.3): "Jupiter is not in a kendra" is sound
absence-reasoning because the chart fixes all positions; "No cancelling yoga is present" is
**not** sound unless the cancellation corpus is complete — which, per
`rule_extraction_framework.md` §2.1, it typically is not. The source notes that this is
"exactly the gap `canonical_shloka_analysis.md` §9.2 reports as `incomplete_defeater_analysis`
rather than concealing." It also records a limit on its own machinery: **who declares
completeness is unresolved** (`vedic_reasoning_methodology.md` §8.4), and "the declaration is
itself an authority claim and should carry provenance" (§3.3).

### Independence is computed, not estimated

§4.1 distinguishes three derivation classes: `direct` (independent unless the instrument is
shared), `derived` (**shares the ancestry of its inputs**), and `inherited` (**fully dependent
on the parent**). Inherited evidence is called "the most dangerous, because it multiplies
effortlessly": if a property inherits down a class hierarchy, "every subclass instance appears
to contribute fresh support for a claim about the parent — a straightforward double count"
(§4.1).

Every item therefore carries an `IndependenceKey` identifying "what it ultimately rests on" —
`root_sources`, `root_rules`, `kernel_versions` (§4.2). "Two evidence items are **independent**
iff their keys are disjoint. They are **correlated** to the degree their keys overlap." The
source argues this is computable rather than estimated, because the `derives_from` closure is
already maintained for the traceability invariant (`computational_primitives.md` §3.16), and
"the independence key is the same closure, projected onto roots." It draws the design
conclusion explicitly: "**Correlation detection comes free from a mechanism the system needs
anyway** — which is a strong argument for the reification-heavy storage design in
`knowledge_graph_spec.md`" (§4.2).

§4.3 adds that content addressing (`reasoning_ontology.md` §7.2) unifies two textual
statements of the same rule into one rule with two provenance records, which is "a *genuine*
independence signal: two texts, two transmission lines, one rule" — as against two rules
derived from the same verse, which are "same root source, fully correlated, no additional
support." The system distinguishes these "without a heuristic, because the identity scheme
already does."

**The source records a hard case it cannot solve.** §4.3: textual dependence — text B copies
text A — yields two provenance records that are not independent transmissions. "Detecting this
requires philological stemma information — which text descends from which — and that is
domain-expert input, not computation. The model provides the field (`source.stemma_parent`)
and cannot populate it automatically."

### Aggregation runs over clusters, and is deliberately conservative

§4.4 specifies aggregation over the independence partition, not the item list:

```
1. Partition evidence for a claim into correlation clusters
   (items sharing root sources / rules)
2. Reduce each cluster to a single effective item
   — weight = strongest in cluster, NOT the sum
3. Aggregate across clusters using a saturating operator
```

Step 2 is described as "deliberately conservative": five restatements of one rule contribute
what the strongest single statement contributes. They may raise *interpretive* confidence —
"the tradition evidently agreed" — but do not multiply *inferential* support, and the two axes
stay separate (`confidence_framework.md` §3).

### Operators assessed, and two rejected outright

§5 assesses candidate aggregation operators and records negative verdicts:

| Approach | Fit | Verdict |
|---|---|---|
| **Bayesian** | Requires priors and a likelihood model. Neither is available for a normative corpus — there is no base rate for "a statute means X" | ✗ Not as the primary operator |
| **Dempster–Shafer** | Represents ignorance explicitly (a genuine advantage), but Dempster's rule behaves pathologically under high conflict, producing counterintuitive results precisely where conflict matters most | ✗ Rejected on that failure |
| **Subjective logic** | Opinion triples ⟨belief, disbelief, uncertainty⟩; handles ignorance without the conflict pathology; supports source discounting | ✅ Good fit for the graded layer |
| **Argumentation (Dung / ASPIC+)** | Determines which arguments *survive* attack. Exactly right for defeasible structure; but binary — no gradation | ✅ Good fit for the structural layer |
| **Weighted voting** | Simple, explainable; ignores structure and correlation entirely | ✗ Too naive alone |

The decision in §5.1 is two layers, in a fixed order:

> **Structure first, then gradation. Never both in one number.**

Layer 1 is structural (argumentation): which arguments survive defeat, output a set of
surviving arguments, binary and explainable. Only survivors proceed to Layer 2, which is
graded, correlation-aware and saturating: how strongly the survivors support the claim, output
a graded opinion with an uncertainty component (§5.1).

The stated reason for the ordering is that "**defeat is not a matter of degree**. An undercut
inference is withdrawn, not weakened (`canonical_shloka_analysis.md` §9.2). Folding defeat into
a weight makes a defeated inference contribute a small positive amount, which is both wrong and
unexplainable — the system would be saying 'this rule was cancelled, so it counts slightly.'"
Layer 1 also produces the material the explanation needs — what attacked what, and what
survived (`explainability_framework.md` §5).

§5.2 imposes a saturation requirement: `aggregate(e₁ … eₙ) < ceiling(strongest_evidence_class)`.
"A conclusion supported only by weak indications is capped below one supported by a primary
attested rule, regardless of count. Without this, the system can be talked into certainty by
volume — the characteristic failure of additive scoring schemes."

### Polarity separates "counterbalanced" from "irrelevant"

§6 keeps `supporting`, `contradicting` and `balanced` all stored against the claim and all
informative, while *irrelevant* items are not stored at all. Collapsing these into one
"neutral" value "conflates *'we looked and it cuts both ways'* with *'this has nothing to do
with the claim.'* The first is a finding; the second is noise." `balanced` is identified as the
evidential counterpart of *satpratipakṣa* (`vedic_reasoning_methodology.md` §2.2) — "the
tradition's name for a genuinely counterbalanced reason" — and it feeds the *vikalpa* outcome
in `conflict_resolution.md` §7.

### Strength is derived from structure

§7 holds that evidence weight is derived from structural properties, never authored
(`computational_primitives.md` §3.14): evidence type sets a type-specific ceiling; source
authority scales weight via a **domain-supplied ranking** (L2, per `reasoning_ontology.md`
§2.1); rule specificity raises weight when a rule fires, so *lex specialis* acts "as a weight,
not only as precedence"; derivation depth attenuates, because "each defeasible step compounds
uncertainty"; extraction confidence caps the weight, because one "cannot rely more on a rule
than on the reading of it"; and attestation independence raises interpretive weight only, not
inferential weight (§4.3). The source underlines the depth rule: "a conclusion four defeasible
inferences deep is weaker than one directly supported, even if every step looked strong. Long
chains are where rule systems quietly become fiction" (§7).

### Nothing is deleted

§8 gives the lifecycle — `proposed → admitted → active`, branching to `defeated` (marked,
retained), `superseded` (new version) or `withdrawn` (source retracted), with `rejected`
recorded with a reason. **Defeated evidence is never deleted** (`knowledge_graph_spec.md` I5),
for three stated reasons: the explanation must say what was considered and rejected, since "a
conclusion reached after weighing contrary evidence differs from one reached in ignorance of
it, even when the conclusion is identical"; defeat is context-relative, so evidence defeated in
one context may be live in another; and defeaters can themselves be defeated (*nīca-bhaṅga*),
"which restores the original — and restoration is impossible if the evidence was removed."
Withdrawal is distinguished from defeat: withdrawn evidence is also retained, but conclusions
depending on it "are flagged for re-derivation rather than merely re-weighted" (§8).

### Worked example: the correlation discount, quantified once

§9 works the evidence supporting `forms(Gajakesari)` in Chart A, taken from
`canonical_shloka_analysis.md` §9.1:

| # | Evidence | Type | Polarity | Independence root |
|---|---|---|---|---|
| e1 | Rule `gajakesari_formation` fired | `derived` | supporting | `{source: TBD-verse, rule: gajakesari_formation}` |
| e2 | position(Guru) = Karka | `direct` | supporting | `{chart_input}` |
| e3 | position(Candra) = Meṣa | `direct` | supporting | `{chart_input}` |
| e4 | debilitation defeater not fired | `absence` | supporting | `{ontology:debilitation_table}` |
| e5 | combustion defeater not fired | `absence` | supporting | `{kernel:combustion, chart_input}` |
| e6 | exalted(Guru, Karka) | `attested` | *modulating* | `{ontology:exaltation_table}` |

The correlation analysis (§9): e2 and e3 share `chart_input` and form one cluster, because
"two positions from one chart are not two independent observations of the yoga's formation";
e1 derives from e2 and e3 and joins the same cluster, since "e1 is not additional support, it
is the *conclusion* of that cluster"; e4 and e5 rest on different roots and are independent of
each other, but admissible only under the observability condition of §3.3 — the chart is
complete for positions, so both are sound, while "no *other* cancelling condition exists"
would **not** be sound and "is correctly not claimed"; and e6 is an influence, not support for
formation (`computational_primitives.md` §3.7), which "modulates the strength of the indication
and must not enter the support tally."

The result is one effective supporting cluster, two independent absence confirmations, and one
positive modulation. "Naive counting would have reported *five supporting items*, and would
have overstated the warrant roughly fivefold" (§9). The source states this factor for this one
worked chart; it does not report a measured error rate over a corpus.

### Status of this document

The source is marked "Draft for review" and is a Phase 3 (Institutional Reasoning) research
document. It is drafted but not accepted as specification, and per `MANIFESTO.md` every
research document is a hypothesis. Several of its central mechanisms are stated as designs
rather than as implemented and measured behaviour: the Layer 2 fusion operator is not fixed
(§10.6), the cluster reduction policy is chosen on conservative grounds rather than on
evidence (§10.1), and the stemma field cannot be populated automatically (§4.3).

## Architectural Implications

The source reserves the DAALE boundary `daale/ontology/evidence.py` for this model, and
records that it fills `choir/research/R003_Evidence_Representation.md`, which is currently
empty (header).

For storage: the independence key is the `derives_from` closure projected onto roots (§4.2),
so correlation detection requires no separate mechanism, and the source treats this as "a
strong argument for the reification-heavy storage design in `knowledge_graph_spec.md`" (§4.2).
Content addressing (`reasoning_ontology.md` §7.2) must remain the identity scheme, since it is
what distinguishes genuine independent attestation from restatement without a heuristic (§4.3).

For execution: aggregation cannot be a single scoring pass. §5.1 requires an argumentation
layer that settles defeat first and a graded layer that runs only over survivors, and forbids
combining them into one number. The graded operator must be saturating (§5.2) and must operate
on clusters rather than items (§4.4). Layer 1's attack/survival record is the material that
`explainability_framework.md` §5 consumes.

For the ontology: `weight` must be derived, never authored (§7, per `computational_primitives.md`
§3.14); `claim` must be mandatory on every evidence item (§2); evidence must never be deleted,
only marked (§8, per `knowledge_graph_spec.md` I5), because *nīca-bhaṅga* restoration depends on
retention; and `balanced` must be a distinct stored polarity, since it feeds the *vikalpa*
outcome in `conflict_resolution.md` §7 (§6). Interpretive and inferential confidence must stay
on separate axes (§4.4, per `confidence_framework.md` §3).

For domain configuration: source-authority ranking is domain-supplied (L2, per
`reasoning_ontology.md` §2.1) and is central machinery, not a tiebreaker (§3.1, §7). Contexts
must be able to carry a `completeness_declaration`, since an entire evidence type — `absence` —
is gated on it (§3.3), and that declaration should carry provenance because it is itself an
authority claim.

## Open Questions

The source records six open questions in §10, and further unresolved points in the body.

1. **Cluster reduction policy** (§10.1). §4.4 takes the strongest item in a cluster; an
   alternative is a within-cluster diminishing sum. "The conservative choice is taken because
   overconfidence is the failure mode being guarded against, but it may under-credit genuine
   partial independence."
2. **Textual stemma** (§10.2). §4.3 cannot detect copying between texts without philological
   input. "How much of the corpus this affects is unknown and could be substantial."
3. **Completeness declarations** (§10.3). "Who may declare a domain complete for
   absence-reasoning, and with what authority? Unresolved, and it gates a whole evidence type."
   §3.3 records the same gap, referring to `vedic_reasoning_methodology.md` §8.4.
4. **Is `balanced` stable under re-evaluation?** (§10.4). Evidence balanced at one point may
   become unbalanced when more is extracted; whether balance should be recomputed or recorded
   as of a decision time "interacts with the tri-temporal model."
5. **Cross-context aggregation** (§10.5). Whether evidence from a more general context
   contributes to a specific-context claim (lattice-upward closure) "is the same open question
   as `knowledge_graph_spec.md` §8.2, and it has a large effect on evidence volume."
6. **Subjective-logic parameterisation** (§10.6). §5 selects the family; "the specific fusion
   operator (cumulative, averaging, weighted) is not fixed, and the choice matters for how
   independent sources combine."

Additionally, the source notes that the cancellation corpus for Jyotiṣa is typically not
complete (§3.3, per `rule_extraction_framework.md` §2.1), which is the gap
`canonical_shloka_analysis.md` §9.2 reports as `incomplete_defeater_analysis`; and that the
worked example's independence root for e1 carries a placeholder source, `TBD-verse` (§9).

## Related Documents

Depends on:

- [YK-R-001 — Computational Primitive Specification](YK-R-001-computational-primitive-specification.md) (`computational_primitives.md`; §2, §4.2, §7, §9)
- [YK-R-004 — Vedic Reasoning Methodology](YK-R-004-vedic-reasoning-methodology.md) (`vedic_reasoning_methodology.md`; §3, §3.3, §6)

Feeds:

- [YK-R-010 — Conflict Resolution](YK-R-010-conflict-resolution.md) (`conflict_resolution.md`; §3.1, §6)
- [YK-R-011 — Confidence Framework](YK-R-011-confidence-framework.md) (`confidence_framework.md`; §4.4)
- [YK-R-012 — Explainability Framework](YK-R-012-explainability-framework.md) (`explainability_framework.md`; §5.1)

Cites:

- [YK-R-002 — Reasoning Ontology](YK-R-002-reasoning-ontology.md) (`reasoning_ontology.md`; §4.3, §7)
- [YK-R-003 — Knowledge Graph Specification](YK-R-003-knowledge-graph-specification.md) (`knowledge_graph_spec.md`; §4.2, §8, §10.5)
- [YK-R-007 — Rule Extraction Framework](YK-R-007-rule-extraction-framework.md) (`rule_extraction_framework.md`; §3.3)
- [YK-R-008 — Canonical Shloka Analysis (Benchmark)](YK-R-008-canonical-shloka-analysis-benchmark.md) (`canonical_shloka_analysis.md`; §3.3, §5.1, §9)
