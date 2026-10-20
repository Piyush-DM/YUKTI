# Rule Extraction Framework

| | |
|---|---|
| **Document ID** | YK-R-007 |
| **Source** | `choir/research/phase-2-vedic/rule_extraction_framework.md` (007) |
| **Series** | CHOIR Research Programme |
| **Revision** | A |
| **Status** | Active |
| **Last Updated** | 2026-08-23 |

## Abstract

This document specifies how rules are extracted from śāstric verse into CHOIR: a canonical
rule schema with mandatory and derived fields (§2), a Mīmāṃsā-based gate that decides which
verses are rules at all (§4), a dual independent extraction protocol with adjudication and a
`contested` outcome (§5), two orthogonal confidence axes set at extraction time (§6), a
deliberately conservative unification policy (§7), and acceptance metrics against a gold set
(§8). Its governing definition of consistency is that two competent analysts working
independently from the same source produce rules that agree on structure, scope, and
conclusion — or disagree in a way the framework makes visible and adjudicable (§1). The
source document is carried in the repository as `Status: Draft for review`; per
`choir/research/README.md`, all 18 research deliverables are drafted, none is accepted, and
every document is a hypothesis. This document is drafted but not accepted as specification.

## Research Question

The source states the brief it answers in §1: "The brief asks how rules can be extracted
*consistently*." It then fixes a testable meaning for consistency rather than leaving it as
a claim, in a block quotation:

> **Two competent analysts, working independently from the same source under this
> framework, produce rules that agree on structure, scope, and conclusion — or disagree in
> a way the framework makes visible and adjudicable.**

The document is explicit that the second clause carries equal weight: "Some verses are
genuinely contested; forcing agreement on them would be a fidelity failure. The framework's
job is to make *unforced* disagreement rare and *forced* disagreement explicit" (§1). It
also states that "Consistency is measured, not asserted — see §8."

A second question runs beneath the first, posed in §3: the brief lists seven required
elements (inputs, preconditions, conditions, outputs, exceptions, supporting evidence, cross
references), and the framework must map each to schema fields and name its characteristic
failure mode.

## Finding

### The canonical rule schema and what may not be authored

Every extracted rule instantiates a single schema (§2). Fields marked **required** must be
present or the rule is rejected; fields marked *derived* are computed, never authored. The
schema is grouped into Identity, Source, Scope, Quantification, Antecedent, Consequent,
Defeat, Evidential role, Relations, Epistemic state, and Process blocks. Required fields
include `version`, the full `source` block (with `edition`, `attestation` graded
`critical|printed|corpus|quotation|unverified`, `variant_reading`, and character `span`), the
`context` block, `conditions`, and a non-empty `conclusions` list. Conclusions carry a
`modality` drawn from `indicates|asserts|obliges|permits|forbids`, a `polarity`, an optional
ordinal `strength`, and an optional `named_result` (*nāmadheya*). Exceptions are typed
`rebutting|undercutting|premise` and carry a `completeness` value of
`known_complete|likely_incomplete|unknown`. Under Epistemic state, the schema annotates
`ambiguities` with the constraint that open items block execution.

The document argues five fields cannot be optional (§2.1):

| Field | Why it cannot be optional |
|---|---|
| `source.edition` | Verse numbering differs between editions; a locus without an edition is unresolvable (004 §0.3) |
| `context.reference_frame` | "The 7th house" denotes different things from Lagna vs from Candra; an unstated frame is an unbound variable (005 §6.4) |
| `conditions` | A rule with no antecedent is not a rule; it is an assertion |
| `exceptions[].completeness` | Exceptions live in other verses; the compiler usually cannot know it found them all (006 §6.3) |
| `independence_key` | Without it, evidence aggregation double-counts (009 §4) |

`exceptions[].completeness` is singled out: defaulting it to "complete" makes every rule look
more decisive than the evidence supports. The honest default is `unknown`, and moving a rule
to `known_complete` requires positive work — a systematic search of the text for qualifying
clauses (§2.1).

Three fields may not be hand-set (§2.2). `confidence` is derived from structure (001 §3.14);
the document's stated reason is that "An extractor who can type a confidence number has an
untraceable opinion wearing a number's clothing." `id` is a content address, and typing it
breaks deduplication. `strength` may record only what the *text* states (*pūrṇa*, *alpa*);
an extractor's sense of how important a rule is has no place in the corpus.

### The seven required elements and their characteristic failures

§3 maps each of the brief's seven required elements to schema fields and names the failure
mode characteristic of it:

| Required | Schema | Characteristic failure |
|---|---|---|
| **Inputs** | `variables`, `context.reference_frame` | Unbound variable silently defaulted → over-general rule |
| **Preconditions** | `preconditions` | Applicability confused with condition (§3.1) |
| **Conditions** | `conditions` | Implicit conditionals missed (locative absolute has no particle) |
| **Outputs** | `conclusions` | *arthavāda* extracted as a conclusion; strength invented |
| **Exceptions** | `exceptions` | Typed rebutting when undercutting; completeness assumed |
| **Supporting evidence** | `source`, `evidence_class`, `cross_references` | Independence not tracked; restatements counted as corroboration |
| **Cross references** | `cross_references` | Unresolved reference admitted as a warning instead of an error |

### Precondition versus condition

§3.1 draws the distinction by what failure means, following `computational_primitives.md`
§3.9. A **precondition** is an applicability gate: failure means the rule is not about this
case, no inference is produced, and no evidence is recorded. A **condition** is a matched
requirement: failure means the rule applies but did not fire, which is informative and is
recordable as absence-evidence (*anupalabdhi*) where the context declares completeness. The
worked case given is a rule scoped to natal charts evaluated against a horary question — it
does not fail to fire, it was never applicable. Conflating the two "pollutes the evidence
base with irrelevant negatives and makes explanations misleading" (§3.1).

### The extraction gate: not every verse is a rule

§4 applies the Mīmāṃsā classification from `vedic_reasoning_methodology.md` §4.3 as a
three-gate filter, and calls it "the highest-yield filter available":

- **G1 — Is it injunctive (*vidhi* / *niṣedha*)?** Tested by optative/gerundive morphology
  and conditional structure. A "no" routes the verse to classification and storage as
  *arthavāda*, mantra, *nāmadheya*, or narrative — not a rule.
- **G2 — Is it self-contained; is *anuvṛtti* resolved?** A "no" routes to scope resolution or
  an `E-BIND` diagnostic.
- **G3 — Are antecedent and consequent both identifiable?** A "no" makes it a definition or
  classification; a "yes" proceeds to EXTRACT.

The document states that **G1 removes the most noise**: a large fraction of śāstric verse is
laudatory, illustrative, or liturgical, and extracting "one with this yoga becomes equal to a
king" as a rule with conclusion `becomes_equal_to_king` "produces a corpus of unfalsifiable
superlatives that no downstream machinery can use" (§4). *arthavāda* is not discarded — it is
stored, classified, and available as interpretive context (it often indicates how strongly
the tradition weights a combination) and as evidence about authorial intent; it simply does
not compile to an executable rule.

The source records a boundary difficulty here: some passages are simultaneously commendatory
and injunctive. "Mīmāṃsā has extensive machinery for this and CHOIR does not yet adopt it;
such verses are flagged `W-ARTHA` and routed to review. How much of the classical apparatus
is needed is open (004 §8.5)" (§4).

### The extraction protocol

§5 states the governing claim that "Consistency is a property of the *process*, not of the
schema. The schema makes consistency expressible; the protocol makes it happen."

**Dual independent extraction** (§5.1) applies to any rule entering the authoritative corpus:
two extractors work independently from the same attested text without seeing each other's
output; outputs are compared field by field; agreement advances the rule to `reviewed`;
disagreement goes to adjudication by a third party who records *grounds*, not merely a
choice; and persistent disagreement marks the rule `contested`, with *both* readings retained
as context-scoped alternatives. The document identifies step 5 as what distinguishes this
from ordinary annotation work: "A genuinely contested verse is a fact about the corpus, and
recording it as such is more faithful than recording a coin flip." Contested rules can still
execute — they produce *vikalpa* outcomes (`conflict_resolution.md` §7).

On what counts as an extractor (§5.2): an extractor may be a human scholar, the automated
pipeline, or the pipeline plus a reviewer, and provenance records which. **Two automated
extractions are not independent and do not satisfy §5.1 — they share their failure modes. At
least one human extraction is required for `accepted` status.**

Certain conditions route to human review regardless of agreement, because they are the
failure modes from `sanskrit_analysis_pipeline.md` §9 that change *what the rule says*
(§5.3):

| Trigger | Diagnostic |
|---|---|
| Ablative/genitive syncretism on a reference-frame term | `A-SCOPE` |
| Compound classified *bahuvrīhi*, or type undetermined | `A-CMPD` |
| Elision detected but resolved automatically | `A-SCOPE` |
| Possible *arthavāda* | `W-ARTHA` |
| Meaning depends on a contested variant reading | `W-VARIANT` |
| Exception set flagged `likely_incomplete` | `W-EXC` |
| Translation-only derivation | `W-TRANS` |

Six anti-patterns are explicitly prohibited, "because each is tempting and each corrupts the
corpus" (§5.4): **harmonising** (silently reconciling texts that disagree — destroys the
disagreement, which is data); **completing** (adding conditions "obviously intended" —
manufactures rules the text does not state); **strengthening** (recording a firmer conclusion
than the text supports — over-generation, which the document calls "the worst failure",
citing 006 §8.2); **flattening** (dropping context to make a rule more general — produces
rules that fire out of scope); **merging** (combining related verses into one rule — loses
independent attestation and separate provenance); and **number invention** (assigning a
numeric strength absent from the text — fabricates precision).

### Two orthogonal confidence axes

Two of the three axes from `computational_primitives.md` §3.14 are set at extraction; the
third (inferential) is computed at execution (§6).

Extraction confidence answers *did we read it right?* (§6.1):

```
extraction_confidence = min( stage_confidences )        # 006 §10
                      × ambiguity_penalty( open_count )
                      × attestation_factor( grade )
                      × agreement_factor( dual_extraction )
```

It is "Bounded by the minimum, not the product — a chain is as strong as its weakest link,
and stage confidences are not independent."

Interpretive confidence answers *does the tradition agree what it means?* and is
independently sourced (§6.2). Commentarial agreement across ṭīkās, independent attestation in
another text via content-address unification, and translation convergence on conditional
structure raise it. Recorded commentarial dispute lowers it; a rule known to differ by school
lowers it and forces a context split; exception completeness `unknown` lowers it; and scope
inherited rather than stated (*prakaraṇa* < *śruti*) lowers it. That last row applies the
Mīmāṃsā interpretive priority ordering from `vedic_reasoning_methodology.md` §5.3 directly as
a confidence input: "a condition inherited from context is weaker evidence of meaning than
one directly stated. The tradition supplies not just the ordering but the rationale."

§6.3 argues the two axes are orthogonal and must not be collapsed: a verse can be transmitted
flawlessly, parsed unambiguously, and still be one whose meaning the commentators have
disputed for a thousand years (high extraction, low interpretive); conversely a damaged text
whose intent is universally agreed (low extraction, high interpretive). "Collapsing these
into one number destroys information a reviewer needs."

### Normalisation, deduplication, and the choice of conservatism

Canonicalisation (`shloka_compiler.md` §8.1) normalises variable naming, condition ordering,
equivalent condition forms, and reference-frame expression; two verses that normalise
identically produce the same content address and **unify**. Unification produces one rule with
two provenance records — "a genuine independent attestation signal, obtained from the identity
scheme rather than a matching heuristic" (§7).

The near-duplicate problem is named as the hard case, with risk running both ways (§7.1):

| Relationship | Correct handling |
|---|---|
| Exact restatement | Unify; two attestations |
| Restatement with an added condition | **Separate rules**; the second is *apavāda* to the first |
| Restatement with a different conclusion | **Separate rules**; a conflict to be adjudicated |
| Paraphrase, same content | Should unify — but canonicalisation may not reach it |
| Different rule, similar surface | Must **not** unify |

The source states the exposure in both directions: "Aggressive normalisation risks merging rows
2, 3 and 5" — the added-condition, different-conclusion, and different-rule rows — while
"conservative normalisation misses row 4 and undercounts attestation." The framework chooses
conservative: unify only on exact canonical-form identity; surface near-duplicates as
*candidates for review*, never as automatic merges. The stated asymmetry is that
"Under-merging leaves duplicate rules, which is visible and fixable. Over-merging silently
destroys an exception or a conflict, which is neither." Embedding-based similarity may generate
the review candidates (`knowledge_graph_spec.md` §2.5 permits proposal) but may not perform the
merge. The cost of the choice is the one the source names on the conservative side: the
paraphrase row is missed and attestation is undercounted.

### Measuring consistency

§8 sets the framework's own acceptance criteria, on the stated grounds that "Without these,
'consistent extraction' is a claim rather than a finding."

| Metric | Method | Target |
|---|---|---|
| **Inter-extractor agreement** | Krippendorff's α per field, over the dual-extraction set | Report per field; structural fields should be high |
| **Structural agreement** | Do both extractions produce the same condition/conclusion shape? | The metric that matters most |
| **Scope agreement** | Same context and reference frame? | High required; scope errors are silent |
| **Exception recall** | Against a gold set with known exceptions | Low recall = over-confident rules |
| **Round-trip fidelity** | 006 §8.2 rubric | No-addition criterion is pass/fail |
| **Over-generation rate** | Rules asserting more than the source | **Target: zero** |
| **Gate precision** | *arthavāda* wrongly extracted as rules | Measured on the gold set |

Agreement is to be reported **per field**, not as a single number: agreement on `conclusions`
with disagreement on `context` is a very different situation from the reverse, and an
aggregate α conceals it. The gold set (100–200 verses, per `sanskrit_analysis_pipeline.md`
§10) must deliberately include *arthavāda* passages, verses requiring *anuvṛtti*, verses with
exceptions in other chapters, contested verses, and near-duplicate pairs — "A gold set of
clean cases measures nothing useful" (§8).

No measurement results are reported. The metrics are specified; the source document records
no α figures, no recall figures, and no gate-precision figures, and does not state that the
gold set has been built.

### Lifecycle

Rules move `draft → reviewed → accepted → (contested) → retired`, with `superseded` re-entering
at `retired` and `rejected` (with recorded reason) as an exit from `draft` (§9).

| Status | Meaning | Executable |
|---|---|---|
| `draft` | Extracted, unreviewed | No |
| `reviewed` | Dual extraction complete or adjudicated | Sandbox only |
| `accepted` | Authoritative | Yes |
| `contested` | Genuine interpretive dispute; alternatives retained | Yes, via *vikalpa* |
| `retired` | Superseded or withdrawn | No — but historical derivations remain replayable |

Nothing is deleted (`knowledge_graph_spec.md` I1/I5). "A rule retired because it was
mis-extracted keeps its record, because conclusions drawn from it must remain explicable"
(§9).

### Status of this document

The source is carried as `Status: Draft for review`. This publication is a drafted research
document, not an accepted specification. The programme index (`choir/research/README.md`)
records that all 18 research deliverables are drafted, that none is accepted, and that every
document is a hypothesis; `MANIFESTO.md` states the underlying instruction in narrower terms —
"Treat every computational object as a hypothesis rather than an established truth."

## Architectural Implications

The schema fixes what a CHOIR rule is at rest, and several of its constraints are binding on
components downstream of extraction. Because `confidence` and `id` are derived and `strength`
is textual-only (§2.2), no interface may accept an authored value for them; a confidence
number that arrives from a human is, in the document's terms, an untraceable opinion. Because
`independence_key` is required, evidence aggregation in the evidence model has the field it
needs to avoid double-counting restatements (009 §4).

The precondition/condition split (§3.1) constrains what execution may record. Only condition
failure is admissible as absence-evidence (*anupalabdhi*), and only where the context declares
completeness; precondition failure must produce neither inference nor evidence. Explanation
output inherits this: conflating them makes explanations misleading.

The gate (§4) constrains the corpus boundary. *arthavāda*, mantra, *nāmadheya*, and narrative
are stored and classified but do not compile to executable rules. For *arthavāda* specifically,
the source records that it remains available as interpretive context and as evidence about
authorial intent, so that material is reachable by the system without entering the executable
rule set. The source makes no equivalent claim for mantra, *nāmadheya*, or narrative.

The `contested` status is load-bearing for execution, not merely for bookkeeping: contested
rules execute and produce *vikalpa* outcomes (`conflict_resolution.md` §7), and both readings
are retained as context-scoped alternatives (§5.1, §9). Retirement does not delete
(`knowledge_graph_spec.md` I1/I5), because historical derivations must remain replayable — a
constraint on storage and on the explainability path.

The conservative unification rule (§7.1) constrains the knowledge graph's identity mechanics:
unification is permitted only on exact canonical-form identity, so attestation counts are
derived from the content-address scheme rather than from similarity matching. Embedding-based
similarity is admitted as a proposer of review candidates and prohibited as a merger.

The requirement that at least one human extraction is present for `accepted` status (§5.2)
constrains any fully automated pipeline: automation can reach `reviewed` (sandbox-only
execution) but cannot on its own produce an authoritative rule under this framework.

## Open Questions

The source records six open questions in §10, plus two further unresolved items noted in the
body.

1. **Is dual extraction affordable at corpus scale?** (§10, item 1) Thousands of verses × two
   scholars is described as the project's dominant cost. Whether automated extraction plus
   single review is sufficient for some rule classes — and which classes — is unresolved, and
   is stated to be the main throughput question.
2. **Who adjudicates, and by what authority?** (§10, item 2) §5.1 step 4 presupposes an adjudicator
   whose grounds are accepted. In a tradition with live disagreement that role is not neutral,
   and the document says the framework "should probably record the adjudicator's school" —
   itself a hedged recommendation, not a settled rule.
3. **Exception completeness search.** (§10, item 3) Moving from `unknown` to `known_complete`
   requires systematically searching a text for qualifying clauses. Whether this is tractable
   before the whole text is compiled is called doubtful, suggesting completeness can only be
   assessed corpus-wide, in a second pass.
4. **Should `strength` be extractable at all?** (§10, item 4) Textual strength terms are ordinal and
   vary between authorities. Recording them risks false precision downstream; omitting them
   loses a distinction the text draws. Unresolved.
5. **Cross-text authority.** (§10, item 5) When text A states a rule and text B states its
   exception, whether B's exception applies depends on whether B is authoritative for A — "a
   question this framework cannot answer" (`conflict_resolution.md` §5.3).
6. **Contested rules and *vikalpa*.** (§10, item 6) Retaining both readings is faithful, but if a
   substantial fraction of the corpus is contested, execution may produce disjunctions too
   often to be useful. The rate is unknown until extraction runs at scale.

Two further unresolved items appear in the body:

- **Commendatory-and-injunctive passages** (§4). Mīmāṃsā has extensive machinery for verses
  that are simultaneously *arthavāda* and *vidhi*; CHOIR does not yet adopt it. Such verses
  are flagged `W-ARTHA` and routed to review, and how much of the classical apparatus is
  needed is open (004 §8.5).
- **Paraphrase unification** (§7.1). Paraphrases with the same content should unify, "but
  canonicalisation may not reach it" — an acknowledged gap in the conservative policy, with no
  remedy specified.

No consistency measurements are reported against the §8 metrics; the targets (including the
zero over-generation target) are stated as acceptance criteria, not as achieved results.

## Related Documents

Depends on:

- [YK-R-006 — Shloka Compiler](YK-R-006-shloka-compiler.md) — canonicalisation (§8.1), stage
  confidence (§10), round-trip fidelity rubric and over-generation (§8.2), exception
  completeness (§6.3)
- [YK-R-004 — Vedic Reasoning Methodology](YK-R-004-vedic-reasoning-methodology.md) — Mīmāṃsā
  classification used as the extraction gate (§4.3), interpretive priority ordering (§5.3),
  edition/locus resolution (§0.3), open apparatus question (§8.5)

Feeds:

- [YK-R-008 — Canonical Shloka Analysis (Benchmark)](YK-R-008-canonical-shloka-analysis-benchmark.md)
- [YK-R-013 — CHOIR Intermediate Representation](YK-R-013-choir-intermediate-representation.md)
- [YK-R-011 — Confidence Framework](YK-R-011-confidence-framework.md)

Cited:

- [YK-R-001 — Computational Primitive Specification](YK-R-001-computational-primitive-specification.md)
  — precondition/condition distinction (§3.9), the three confidence axes (§3.14)
- [YK-R-003 — Knowledge Graph Specification](YK-R-003-knowledge-graph-specification.md) —
  similarity may propose but not merge (§2.5), non-deletion invariants I1/I5
- [YK-R-005 — Sanskrit Analysis Pipeline](YK-R-005-sanskrit-analysis-pipeline.md) — failure
  modes behind the mandatory review triggers (§9), gold set size (§10), reference-frame
  binding (§6.4)
- [YK-R-009 — Evidence Model](YK-R-009-evidence-model.md) — independence and correlation
  discount (§4)
- [YK-R-010 — Conflict Resolution](YK-R-010-conflict-resolution.md) — *vikalpa* outcomes for
  contested rules (§7), cross-text authority (§5.3)
