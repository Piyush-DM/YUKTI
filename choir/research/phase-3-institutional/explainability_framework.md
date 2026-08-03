# 012 — Explainability Framework

**Status:** Draft for review
**Phase:** 3 — Institutional Reasoning
**Depends on:** `vedic_reasoning_methodology.md`, `evidence_model.md`, `conflict_resolution.md`, `confidence_framework.md`
**Feeds:** `execution_pipeline.md`
**Fills:** `choir/research/R006_Traceability.md` (currently empty)

---

## 1. The governing constraint

> **Explanations are *projections of the execution record*. They are never regenerated,
> paraphrased, or reconstructed by a separate process.**

This is the single most important design decision in this document, and it is what
distinguishes a CHOIR explanation from a plausible-sounding narrative.

If an explanation is produced by asking a second system "why might this conclusion have been
reached?", the result is a *rationalisation*: fluent, convincing, and unconnected to what
actually happened. It will remain fluent and convincing when the reasoning was wrong, which
makes it worse than no explanation.

Because CHOIR's explanations are views over the trace, **faithfulness is guaranteed by
construction**. There is no separate model that could disagree with the reasoning, because
there is no separate model.

**Consequence for the architecture:** the trace is not a debugging artefact produced on
request. It is a primary output, produced always, and the traceability invariant
(`computational_primitives.md` §3.16) is what makes explanation possible at all. This is why
`knowledge_graph_spec.md` reifies every inference.

---

## 2. What every explanation must answer

The brief requires that every inference answer "Why?". Five components, all mandatory:

| # | Component | Question answered |
|---|---|---|
| E1 | **Rule chain** | Which rules fired, in what order, with what bindings? |
| E2 | **Evidence** | What supported this, what opposed it, how was it weighted? |
| E3 | **Exceptions** | Which defeaters were checked? Which fired? **Which did not?** |
| E4 | **Alternative conclusions** | What else was live, and why did it lose? |
| E5 | **Supporting texts** | What sources, at what loci, in what editions? |

Plus two CHOIR additions that fall out of Phase 3:

| # | Component | Question answered |
|---|---|---|
| E6 | **Confidence decomposition** | How confident, on which axis, limited by what? |
| E7 | **Coverage** | What was **not** evaluated? |

### 2.1 E3 must include negative results

*"These three cancellation conditions were checked and none applied"* is part of the
explanation, not housekeeping. A conclusion reached after checking for defeaters differs
epistemically from one reached without looking — even when the conclusion is identical.

### 2.2 E7 is the component systems usually omit

A system that reports only what it did is overstating its coverage by omission. If a
defeater chain was truncated, if an exception corpus is incomplete, if a precedence
principle was unavailable — the explanation must say so.

`canonical_shloka_analysis.md` §9.2 demonstrates this: the trace reports
`incomplete_defeater_analysis` for the unevaluated *nīca-bhaṅga* conditions rather than
presenting a clean result. That report is more valuable than the conclusion it qualifies.

---

## 3. The explanation schema: *pañcāvayava*

CHOIR adopts the Nyāya five-membered demonstration as its explanation template. It is not an
ornament; it is a fully-formed schema that maps exactly onto the execution record.

| Member | Content | Drawn from |
|---|---|---|
| ***pratijñā*** — thesis | The claim | `Inference.conclusion` |
| ***hetu*** — reason | Why, in this case | Matched `conditions` |
| ***udāharaṇa*** — general rule + example | The warrant, with its source | `Rule` + `Provenance` |
| ***upanaya*** — application | How the general rule applies here | `bindings` + derived facts |
| ***nigamana*** — conclusion | Therefore, with qualification | Conclusion + confidence + coverage |

### 3.1 Why adopt it rather than invent a format

Four properties, all of which had to be designed for otherwise:

1. **It separates the rule from its application.** *udāharaṇa* states the general warrant;
   *upanaya* states the instantiation. Most generated explanations blur these, producing
   "Jupiter is in a kendra so there is fame" without ever stating the rule — which makes the
   reasoning uninspectable.
2. **It requires the warrant to be exhibited**, not merely relied upon. The general rule
   must be stated, with its example, which forces source citation into the structure.
3. **It handles negative and defeated conclusions without modification**
   (`canonical_shloka_analysis.md` §10 shows both cases in the same template).
4. **It is the corpus's own explanatory form**, so explanations of śāstric reasoning are
   legible to people trained in that tradition — a genuine and rare fidelity property.

Property 3 is the one that would be hardest to retrofit. Ad-hoc explanation formats are
almost always designed around successful firing and become awkward when the answer is
"nothing follows from this rule."

### 3.2 It generalises

The schema is not Jyotiṣa-specific. Legal reasoning already uses something close to it —
issue, rule, application, conclusion — and clinical reasoning follows finding →
guideline → applicability → recommendation. See `domain_independence.md` §5.

---

## 4. Trace structure

The trace is a DAG, not a list. Explanations are *walks* over it at chosen depths.

```
CONCLUSION
├── INFERENCE (rule, bindings, license)
│   ├── RULE ──▶ SOURCE ──▶ TEXT/LOCUS/EDITION
│   ├── CONDITIONS
│   │   ├── satisfied: [ facts, each → their own derivation ]
│   │   └── unsatisfied: [ … ]                      ← retained
│   ├── DERIVED FACTS
│   │   └── KERNEL(version) ──▶ inputs              ← replayable
│   ├── DEFEATERS
│   │   ├── fired:     [ exception, type, source ]
│   │   ├── not fired: [ exception, why not ]       ← E3
│   │   └── not evaluated: [ exception, why not ]   ← E7
│   ├── INFLUENCES (second-order; modulate, not produce)
│   └── EVIDENCE
│       ├── clusters: [ items, independence key ]   ← E2
│       └── contradicting: [ … ]
├── CONFLICTS
│   └── RESOLUTION
│       ├── principles applied
│       └── principles unavailable + reasons        ← E4
├── CONFIDENCE
│   └── ⟨extraction, interpretive, inferential⟩ + limiting factor   ← E6
└── COVERAGE
    └── what was not evaluated, and why             ← E7
```

Every node carries back-pointers to source spans, reaching all the way to character offsets
in the attested text (`shloka_compiler.md` §4). A user can go from a conclusion to the exact
substring of the verse that licensed it.

### 4.1 The replay guarantee

> Given the same inputs, the same corpus version, the same kernel versions, and the same
> resolution policy, replaying a trace reproduces the identical conclusion.

This is the traceability invariant made operational, and it is what makes E1–E7 verifiable
rather than merely asserted. It requires the determinism constraints in
`reasoning_ontology.md` §6.2 (kernels are pure) and the version pinning in
`execution_pipeline.md` §7.

---

## 5. Alternatives and counterfactuals

### 5.1 Why alternatives must be shown (E4)

A conclusion reached where nothing else was live differs from one that narrowly beat a
competitor. Suppressing the competitor makes the first look like the second.

For every alternative conclusion that was live:

| Field | Content |
|---|---|
| The alternative | What it would have concluded |
| Its support | Rules and evidence |
| Why it lost | Defeated / preempted / lower confidence / out of context |
| The margin | How close it was |

Where the alternative was **not** defeated but merely unpreferred, the outcome is
*vikalpa* (`conflict_resolution.md` §7.1) and **both are presented**. The explanation must
not narrate a forced choice as though it were a determination.

### 5.2 Counterfactual explanation

The rule graph supports a directly useful question: *what minimal change would flip this?*

```
Chart B (defeated):
  "This would have been indicated had Jupiter not been debilitated.
   The positional condition was satisfied — 10th from the Moon is a kendra."
```

Computable by walking the conditions and defeaters for minimal sets whose alteration changes
the outcome. This is often the most informative thing the system can say, because it
identifies the *load-bearing* fact rather than reciting all of them.

---

## 6. Audiences

Four renderings, one trace. Because all are projections, they cannot disagree with each
other or with the reasoning.

| Audience | Depth | Emphasis | Omits |
|---|---|---|---|
| **Practitioner** | Shallow | Conclusion, main reason, confidence band, limiting factor | Full evidence graph; resolution internals |
| **Scholar** | Deep | Source loci, grammatical derivation, commentarial disputes, interpretive confidence | Kernel internals |
| **Auditor** | Complete | Every input, version pin, replay instructions | Nothing |
| **Subject** | Shallow, plain language | What was concluded, what it rests on, **what is uncertain** | Technical vocabulary |

### 6.1 Constraints on rendering

- **Never render a conclusion without its confidence band and limiting factor**
  (`confidence_framework.md` §6). "Moderate confidence — limited by an unverified citation"
  tells the reader what would change the answer; "moderate confidence" does not.
- **Never render a *vikalpa* as a single answer**, at any depth. If the practitioner view
  cannot fit two alternatives, it shows that there are two and links to them.
- **Never omit coverage gaps** from any view. A truncated defeater chain appears in the
  practitioner view too, in one sentence.
- **The scholar view must expose the grammatical derivation** — the kāraka analysis that
  fixed the reference frame is the answer to "why the Moon and not the Ascendant"
  (`canonical_shloka_analysis.md` §4.3).

---

## 7. Anti-patterns

| Anti-pattern | Why it is prohibited |
|---|---|
| **Post-hoc generation** | Produces plausible narratives disconnected from the reasoning; stays plausible when the reasoning is wrong |
| **Selective tracing** | Showing only supporting evidence; the omission is the distortion |
| **Confidence without a limiting factor** | Unactionable |
| **Silent coverage gaps** | Overstates completeness by omission |
| **Collapsed *vikalpa*** | Presents a genuine split as a determination |
| **Untraceable derived facts** | A kernel output with no version pin cannot be replayed |
| **Explaining a conclusion the system did not reach** | Any divergence between explanation and record is a defect, not a presentation choice |

The first is the important one, because it is what almost every contemporary system does,
and because the output is *more* convincing than a faithful explanation would be.

---

## 8. Worked example

From `canonical_shloka_analysis.md` §9.2 — Chart B, where the rule fired and was undercut.
Practitioner view first, then the scholar's expansion of a single point.

**Practitioner view**

> **Gajakesarī yoga: not indicated.**
>
> Jupiter is in the 10th house from the Moon, which is a kendra, so the positional condition
> for Gajakesarī is met. However, Jupiter is in Capricorn, its sign of debilitation, and
> debilitation withdraws this indication.
>
> This is **not** a contrary indication — it means this particular rule contributes nothing
> here. Other factors in the chart are unaffected.
>
> *Confidence: moderate — limited by an unverified citation for the source verse.*
> *Coverage: conditions that can annul debilitation were not evaluated; those rules have not
> been extracted. This conclusion is provisional.*

Every mandatory component is present in six sentences: rule chain, the defeater that fired,
the correct semantics of undercutting, the confidence band with its limiting factor, and the
coverage gap.

**Scholar expansion — "why is the Moon the reference frame?"**

> The verse reads *candrāt kendragate jīve*. *Candrāt* is the ablative singular of *candra*.
> In the *a*-stem paradigm the ablative singular (*candrāt*) is formally distinct from the
> genitive singular (*candrasya*), so the case is unambiguous here.
>
> The ablative marks the kāraka *apādāna* — the point from which something is reckoned —
> which fixes the Moon as the reference frame rather than as the subject of the condition.
> The subject is *jīve* (Jupiter), in the locative, forming a locative absolute with
> *kendragate*.
>
> This construction carries conditional force **with no conditional particle present**. The
> reading depends on the case morphology, not on any lexical marker.
>
> *Note: the source verse is not yet verified against a critical edition (`E-ATTEST`), and a
> metrical anomaly in the first pāda is flagged for review (`W-VARIANT`).*

This is the property that most justifies the architecture: the grammatical justification
survives from the manuscript to the user, because kāraka roles became hyperedge participant
roles instead of being translated away.

---

## 9. Verification

Explainability is a testable property.

| # | Test | Method | Fails if |
|---|---|---|---|
| X1 | **Replay** | Re-execute from the trace | Any divergence in the conclusion |
| X2 | **Completeness** | Check E1–E7 present on every conclusion | Any missing |
| X3 | **Faithfulness** | Diff the explanation against the record | Any claim not in the record |
| X4 | **Source reachability** | Follow every citation to a locus and span | Any dangling citation |
| X5 | **Negative coverage** | Confirm unfired defeaters are reported | Any silent omission |
| X6 | **Counterfactual soundness** | Apply the stated minimal change; re-run | The outcome does not flip |
| X7 | **Cross-view consistency** | Compare the four audience renderings | Any contradiction |
| X8 | **Coverage honesty** | Confirm every truncation is reported | Any silent truncation |

X3 is trivially satisfiable given §1 — a projection cannot contain what the record does not.
It is retained as a regression test precisely because the temptation to "improve" an
explanation with generated prose will recur, and X3 is what catches it.

X6 is the strongest test of whether the rule graph is correct, because it checks the
system's causal model of its own reasoning against its actual behaviour.

---

## 10. Open questions

1. **Trace size.** A full trace with every unfired defeater and every unsatisfied condition
   may substantially exceed the conclusion in size. Whether to materialise it always or
   reconstruct it on demand from a compact log is an engineering question with a correctness
   constraint: reconstruction must be provably equivalent.
2. **Explaining *absence*.** "No evidence was found" needs the observability condition
   (`evidence_model.md` §3.3) rendered comprehensibly, and there is no obvious plain-language
   form for "this absence is informative because the domain is complete."
3. **Explaining aggregation.** Cluster-based correlation discounting (§`evidence_model.md`
   §4.4) is correct but unintuitive. A reader who sees five citations and is told they count
   as one needs that explained without a lecture on independence.
4. **Natural-language generation.** Templated text is faithful but stilted. Generated text is
   fluent but reintroduces the §1 hazard. A constrained middle — generation restricted to
   surface realisation of record-derived content, with X3 enforced automatically — is
   plausible but unproven, and the failure mode is severe.
5. **Explaining *vikalpa* without implying a preference.** Presentation order alone suggests
   ranking. Whether ordering can be made genuinely neutral is unresolved
   (`conflict_resolution.md` §11.2).
6. **Subject-facing explanation of a system whose domain lacks predictive validity.** For
   Jyotiṣa, the subject view must convey that the system reports *what the tradition says*,
   not *what will happen*, without either editorialising or misleading. This is a real
   design problem and it is not solved here.
