# 007 — Rule Extraction Framework

**Status:** Draft for review
**Phase:** 2 — Vedic Reasoning Research
**Depends on:** `shloka_compiler.md`, `vedic_reasoning_methodology.md`
**Feeds:** `canonical_shloka_analysis.md`, `choir_intermediate_representation.md`, `confidence_framework.md`

---

## 1. What this framework must guarantee

The brief asks how rules can be extracted *consistently*. Consistency has a testable
meaning:

> **Two competent analysts, working independently from the same source under this
> framework, produce rules that agree on structure, scope, and conclusion — or disagree in
> a way the framework makes visible and adjudicable.**

The second clause matters as much as the first. Some verses are genuinely contested;
forcing agreement on them would be a fidelity failure. The framework's job is to make
*unforced* disagreement rare and *forced* disagreement explicit.

Consistency is measured, not asserted — see §8.

---

## 2. The canonical rule schema

Every extracted rule instantiates this schema. Fields marked **required** must be present or
the rule is rejected; fields marked *derived* are computed, never authored.

```
Rule ::= {
  ── Identity ────────────────────────────────────────────────
  id                 : ContentAddress        # required, derived
  nominal_id         : string?               # optional human handle
  version            : VersionRef            # required
  supersedes         : RuleID?

  ── Source ──────────────────────────────────────────────────
  source             : {                     # required
      text           : TextID
      locus          : chapter/verse/pāda
      edition        : EditionID             # required — not optional
      translator     : AgentID?              # if translation-derived
      attestation    : critical|printed|corpus|quotation|unverified
      variant_reading: bool
      span           : character offsets
  }

  ── Scope ───────────────────────────────────────────────────
  context            : {                     # required
      tradition      : school lineage
      application    : jātaka|praśna|muhūrta|…
      chart_frame    : rāśi|navāṃśa|…
      reference_frame: EntityRef             # e.g. Lagna, Candra
      temporal_scope : Interval?
      purpose        : [ domain ]?           # empty = all
  }

  ── Quantification ──────────────────────────────────────────
  variables          : [ { name, type, binding } ]

  ── Antecedent ──────────────────────────────────────────────
  preconditions      : [ Constraint ]        # applicability gate
  conditions         : ConditionExpr         # required; the matched structure

  ── Consequent ──────────────────────────────────────────────
  conclusions        : [ {                   # required, non-empty
      proposition    : Proposition
      modality       : indicates|asserts|obliges|permits|forbids
      polarity       : positive|negative
      strength       : ordinal?              # from the text ONLY
      named_result   : SituationalEntityRef? # nāmadheya
  } ]

  ── Defeat ──────────────────────────────────────────────────
  exceptions         : [ {
      ref            : ExceptionID
      type           : rebutting|undercutting|premise
      source         : Source                # often a different verse
      completeness   : known_complete|likely_incomplete|unknown
  } ]

  ── Evidential role ─────────────────────────────────────────
  evidence_class     : primary|corroborating|weak_indication
  independence_key   : hash                  # for correlation discount

  ── Relations ───────────────────────────────────────────────
  cross_references   : [ { ref, kind: defines|restricts|extends|
                                       cites|contradicts } ]

  ── Epistemic state ─────────────────────────────────────────
  confidence         : { extraction, interpretive }   # derived; §6
  ambiguities        : [ AmbiguityRef ]      # open items block execution
  open_questions     : [ string ]
  diagnostics        : [ DiagnosticCode ]

  ── Process ─────────────────────────────────────────────────
  provenance         : { extractor, method, timestamp,
                         adjudicator?, adjudication_grounds? }
  status             : draft|reviewed|accepted|contested|retired
}
```

### 2.1 Why certain fields are mandatory

| Field | Why it cannot be optional |
|---|---|
| `source.edition` | Verse numbering differs between editions; a locus without an edition is unresolvable (004 §0.3) |
| `context.reference_frame` | "The 7th house" denotes different things from Lagna vs from Candra; an unstated frame is an unbound variable (005 §6.4) |
| `conditions` | A rule with no antecedent is not a rule; it is an assertion |
| `exceptions[].completeness` | Exceptions live in other verses; the compiler usually cannot know it found them all (006 §6.3) |
| `independence_key` | Without it, evidence aggregation double-counts (009 §4) |

`exceptions[].completeness` deserves emphasis. Defaulting it to "complete" makes every rule
look more decisive than the evidence supports. The honest default is `unknown`, and moving
a rule to `known_complete` requires positive work — a systematic search of the text for
qualifying clauses.

### 2.2 Fields that may not be hand-set

- **`confidence`** — derived from structure (001 §3.14). An extractor who can type a
  confidence number has an untraceable opinion wearing a number's clothing.
- **`id`** — content address; typing it breaks deduplication.
- **`strength`** — may record only what the *text* states (*pūrṇa*, *alpa*). An extractor's
  sense of how important a rule is has no place in the corpus.

---

## 3. The seven required elements, mapped

The brief lists seven things the framework needs. Each maps to schema fields, and each has
a characteristic failure mode.

| Required | Schema | Characteristic failure |
|---|---|---|
| **Inputs** | `variables`, `context.reference_frame` | Unbound variable silently defaulted → over-general rule |
| **Preconditions** | `preconditions` | Applicability confused with condition (§3.1) |
| **Conditions** | `conditions` | Implicit conditionals missed (locative absolute has no particle) |
| **Outputs** | `conclusions` | *arthavāda* extracted as a conclusion; strength invented |
| **Exceptions** | `exceptions` | Typed rebutting when undercutting; completeness assumed |
| **Supporting evidence** | `source`, `evidence_class`, `cross_references` | Independence not tracked; restatements counted as corroboration |
| **Cross references** | `cross_references` | Unresolved reference admitted as a warning instead of an error |

### 3.1 Precondition vs condition

Both are propositions in the antecedent; the distinction is *what failure means*, following
`computational_primitives.md` §3.9.

- **Precondition** — an applicability gate. Failure means *this rule is not about this
  case*. No inference is produced, and no evidence is recorded.
- **Condition** — a matched requirement. Failure means *the rule applies but did not fire*,
  which is informative: it is recordable as absence-evidence (*anupalabdhi*) where the
  context declares completeness.

A rule scoped to natal charts, evaluated against a horary question, does not "fail to
fire" — it was never applicable. Conflating the two pollutes the evidence base with
irrelevant negatives and makes explanations misleading.

---

## 4. The extraction gate

Not every verse is a rule. Applying the Mīmāṃsā classification
(`vedic_reasoning_methodology.md` §4.3) as a gate is the highest-yield filter available.

```
                    verse
                      │
        ┌─────────────▼──────────────┐
        │ G1  Is it injunctive?      │  optative/gerundive morphology;
        │     vidhi / niṣedha ?      │  conditional structure
        └─────────────┬──────────────┘
              no ─────┴───── yes
               │              │
      classify & store        ▼
      (arthavāda, mantra,  ┌──────────────────────────────┐
       nāmadheya, narrative)│ G2  Is it self-contained?   │
       NOT a rule           │     anuvṛtti resolved?      │
                            └──────────────┬───────────────┘
                                  no ──────┴────── yes
                                   │                │
                            resolve scope           ▼
                            or E-BIND        ┌──────────────────────┐
                                             │ G3  Antecedent AND   │
                                             │     consequent both  │
                                             │     identifiable?    │
                                             └──────────┬───────────┘
                                                   no ──┴── yes
                                                    │        │
                                             definition or   ▼
                                             classification  EXTRACT
```

**G1 is the one that removes the most noise.** A large fraction of śāstric verse is
laudatory, illustrative, or liturgical. Extracting "one with this yoga becomes equal to a
king" as a rule with conclusion `becomes_equal_to_king` produces a corpus of unfalsifiable
superlatives that no downstream machinery can use.

*arthavāda* is not discarded — it is stored, classified, and available as *interpretive
context* (it often indicates how strongly the tradition weights a combination) and as
evidence about authorial intent. It simply does not compile to an executable rule.

**Boundary difficulty.** Some passages are simultaneously commendatory and injunctive.
Mīmāṃsā has extensive machinery for this and CHOIR does not yet adopt it; such verses are
flagged `W-ARTHA` and routed to review. How much of the classical apparatus is needed is
open (004 §8.5).

---

## 5. Extraction protocol

Consistency is a property of the *process*, not of the schema. The schema makes consistency
expressible; the protocol makes it happen.

### 5.1 Dual independent extraction

For any rule entering the authoritative corpus:

1. **Two extractors work independently** from the same attested text, without seeing each
   other's output.
2. Outputs are compared field by field.
3. **Agreement** → the rule advances to `reviewed`.
4. **Disagreement** → adjudication by a third party, who records *grounds*, not merely a
   choice.
5. **Persistent disagreement** → the rule is marked `contested`, and *both* readings are
   retained as context-scoped alternatives. It is not forced.

Step 5 is the one that distinguishes this from ordinary annotation work. A genuinely
contested verse is a fact about the corpus, and recording it as such is more faithful than
recording a coin flip. Contested rules can still execute — they produce *vikalpa* outcomes
(`conflict_resolution.md` §7).

### 5.2 What "extractor" means

An extractor may be a human scholar, the automated pipeline, or the pipeline plus a
reviewer. The provenance records which. Two *automated* extractions are not independent and
do not satisfy §5.1 — they share their failure modes. At least one human extraction is
required for `accepted` status.

### 5.3 Mandatory review triggers

Regardless of agreement, these route to human review — they are the failure modes from
`sanskrit_analysis_pipeline.md` §9 that change *what the rule says*:

| Trigger | Diagnostic |
|---|---|
| Ablative/genitive syncretism on a reference-frame term | `A-SCOPE` |
| Compound classified *bahuvrīhi*, or type undetermined | `A-CMPD` |
| Elision detected but resolved automatically | `A-SCOPE` |
| Possible *arthavāda* | `W-ARTHA` |
| Meaning depends on a contested variant reading | `W-VARIANT` |
| Exception set flagged `likely_incomplete` | `W-EXC` |
| Translation-only derivation | `W-TRANS` |

### 5.4 Anti-patterns

Explicitly prohibited, because each is tempting and each corrupts the corpus:

| Anti-pattern | Why it is prohibited |
|---|---|
| **Harmonising** — silently reconciling texts that disagree | Destroys the disagreement, which is data |
| **Completing** — adding conditions "obviously intended" | Manufactures rules the text does not state |
| **Strengthening** — recording a firmer conclusion than the text supports | Over-generation; the worst failure (006 §8.2) |
| **Flattening** — dropping context to make a rule more general | Produces rules that fire out of scope |
| **Merging** — combining related verses into one rule | Loses independent attestation and separate provenance |
| **Number invention** — assigning a numeric strength absent from the text | Fabricates precision |

---

## 6. Confidence at extraction

Two of the three axes from `computational_primitives.md` §3.14 are set here; the third
(inferential) is computed at execution.

### 6.1 Extraction confidence — *did we read it right?*

```
extraction_confidence = min( stage_confidences )        # 006 §10
                      × ambiguity_penalty( open_count )
                      × attestation_factor( grade )
                      × agreement_factor( dual_extraction )
```

Bounded by the minimum, not the product — a chain is as strong as its weakest link, and
stage confidences are not independent.

### 6.2 Interpretive confidence — *does the tradition agree what it means?*

Distinct from extraction, and independently sourced:

| Input | Effect |
|---|---|
| Commentarial agreement across ṭīkās | ↑ |
| Independent attestation in another text (via content-address unification) | ↑ |
| Translation convergence on conditional structure | ↑ |
| Recorded commentarial dispute | ↓ |
| Rule known to differ by school | ↓ (and forces context split) |
| Exception completeness `unknown` | ↓ |
| Scope inherited rather than stated (*prakaraṇa* < *śruti*) | ↓ |

The last row applies the Mīmāṃsā interpretive priority ordering
(`vedic_reasoning_methodology.md` §5.3) directly as a confidence input: a condition
inherited from context is weaker evidence of meaning than one directly stated. The tradition
supplies not just the ordering but the rationale.

### 6.3 The two are orthogonal

A verse can be transmitted flawlessly, parsed unambiguously, and still be one whose meaning
the commentators have disputed for a thousand years. High extraction, low interpretive.
Conversely a damaged text whose intent is universally agreed: low extraction, high
interpretive. Collapsing these into one number destroys information a reviewer needs.

---

## 7. Normalisation and deduplication

The same rule appears in multiple texts, in multiple phrasings, at different levels of
specificity.

**Canonicalisation** (`shloka_compiler.md` §8.1) normalises: variable naming, condition
ordering, equivalent condition forms, and reference-frame expression. Two verses that
normalise identically produce the same content address and **unify**.

**Unification produces one rule with two provenance records** — a genuine independent
attestation signal, obtained from the identity scheme rather than a matching heuristic.

### 7.1 The near-duplicate problem

Rules that are *similar* but not identical are the hard case, and the risk runs both ways:

| Relationship | Correct handling |
|---|---|
| Exact restatement | Unify; two attestations |
| Restatement with an added condition | **Separate rules**; the second is *apavāda* to the first |
| Restatement with a different conclusion | **Separate rules**; a conflict to be adjudicated |
| Paraphrase, same content | Should unify — but canonicalisation may not reach it |
| Different rule, similar surface | Must **not** unify |

Aggressive normalisation risks merging rows 2, 3 and 5; conservative normalisation misses
row 4 and undercounts attestation. **The framework chooses conservative**: unify only on
exact canonical-form identity; surface near-duplicates as *candidates for review*, never as
automatic merges. Under-merging leaves duplicate rules, which is visible and fixable.
Over-merging silently destroys an exception or a conflict, which is neither.

Embedding-based similarity may generate the review candidates (`knowledge_graph_spec.md`
§2.5 permits proposal) but may not perform the merge.

---

## 8. Measuring consistency

The framework's own acceptance criteria. Without these, "consistent extraction" is a claim
rather than a finding.

| Metric | Method | Target |
|---|---|---|
| **Inter-extractor agreement** | Krippendorff's α per field, over the dual-extraction set | Report per field; structural fields should be high |
| **Structural agreement** | Do both extractions produce the same condition/conclusion shape? | The metric that matters most |
| **Scope agreement** | Same context and reference frame? | High required; scope errors are silent |
| **Exception recall** | Against a gold set with known exceptions | Low recall = over-confident rules |
| **Round-trip fidelity** | 006 §8.2 rubric | No-addition criterion is pass/fail |
| **Over-generation rate** | Rules asserting more than the source | **Target: zero** |
| **Gate precision** | *arthavāda* wrongly extracted as rules | Measured on the gold set |

Agreement should be reported **per field**, not as a single number. Agreement on
`conclusions` and disagreement on `context` is a very different situation from the reverse,
and an aggregate α conceals it.

**The gold set** (100–200 verses, per `sanskrit_analysis_pipeline.md` §10) must deliberately
include: *arthavāda* passages, verses requiring *anuvṛtti*, verses with exceptions in other
chapters, contested verses, and near-duplicate pairs. A gold set of clean cases measures
nothing useful.

---

## 9. Lifecycle

```
draft ──▶ reviewed ──▶ accepted ──▶ (contested) ──▶ retired
  │           │           │                            ▲
  │           │           └────── superseded ──────────┘
  └── rejected (with recorded reason)
```

| Status | Meaning | Executable |
|---|---|---|
| `draft` | Extracted, unreviewed | No |
| `reviewed` | Dual extraction complete or adjudicated | Sandbox only |
| `accepted` | Authoritative | Yes |
| `contested` | Genuine interpretive dispute; alternatives retained | Yes, via *vikalpa* |
| `retired` | Superseded or withdrawn | No — but historical derivations remain replayable |

Nothing is deleted (`knowledge_graph_spec.md` I1/I5). A rule retired because it was
mis-extracted keeps its record, because conclusions drawn from it must remain explicable.

---

## 10. Open questions

1. **Is dual extraction affordable at corpus scale?** Thousands of verses × two scholars is
   the project's dominant cost. Whether automated extraction plus single review is
   sufficient for some rule classes — and which classes — is unresolved and is the main
   throughput question.
2. **Who adjudicates, and by what authority?** §5.1 step 4 presupposes an adjudicator whose
   grounds are accepted. In a tradition with live disagreement, that role is not neutral,
   and the framework should probably record the adjudicator's school.
3. **Exception completeness search.** Moving from `unknown` to `known_complete` requires
   systematically searching for qualifying clauses across a text. Whether this is tractable
   before the whole text is compiled is doubtful — suggesting completeness can only be
   assessed corpus-wide, in a second pass.
4. **Should `strength` be extractable at all?** Textual strength terms are ordinal and
   vary between authorities. Recording them risks false precision downstream; omitting them
   loses a distinction the text draws.
5. **Cross-text authority.** When text A states a rule and text B states its exception,
   whether B's exception applies depends on whether B is authoritative for A — a question
   this framework cannot answer (`conflict_resolution.md` §5.3).
6. **Contested rules and *vikalpa*.** Retaining both readings is faithful, but if a
   substantial fraction of the corpus is contested, execution may produce disjunctions too
   often to be useful. The rate is unknown until extraction runs at scale.
