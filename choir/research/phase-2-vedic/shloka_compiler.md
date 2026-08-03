# 006 — Shloka Compiler

**Status:** Draft for review
**Phase:** 2 — Vedic Reasoning Research
**Depends on:** `sanskrit_analysis_pipeline.md`, `vedic_reasoning_methodology.md`
**Feeds:** `choir_intermediate_representation.md`, `rule_extraction_framework.md`, `canonical_shloka_analysis.md`

---

## 1. The transformation chain

The brief specifies the pipeline to be researched:

```
Shloka → Translation → Grammar → Meaning → Reasoning → Computational Graph → Executable Rule
```

Each arrow is a transformation with its own inputs, outputs, failure modes, and information
loss. This document specifies all six and states what is preserved across each.

**The compiler analogy is used seriously, not decoratively.** Every stage has a genuine
counterpart in conventional compilation, and the correspondence is load-bearing: it tells
us what the hard problems are and where the established solutions live.

| Shloka compiler stage | Conventional compiler | What transfers |
|---|---|---|
| Normalisation + sandhi splitting | Lexical analysis | Tokenisation; but here it is *ambiguous* |
| Morphology + compounds + parse | Syntactic analysis | Parse forests, not parse trees |
| Kāraka + sense resolution | Semantic analysis | Type checking against the ontology |
| *Anuvṛtti* resolution | **Name binding / scope resolution** | Exact analogy; free variables must bind |
| Frame → HIR | IR generation | Lowering |
| Normalisation, dedup | Optimisation | Canonicalisation |
| Cross-reference resolution | **Linking** | Unresolved references are errors |
| MIR → LIR | Code generation | Target-specific lowering |

The two exact analogies — scope resolution and linking — are the ones that catch the errors
most likely to produce silently wrong rules.

### 1.1 The one place the analogy breaks

A conventional compiler's source language is unambiguous by construction. Ours is not, and
no amount of engineering will make it so.

> **CHOIR is a compiler whose front end cannot always decide, and whose correct behaviour
> in that case is to emit a diagnostic rather than a guess.**

This makes the shloka compiler an **interactive** compiler with a human adjudication gate,
and it makes *ambiguity a first-class output* rather than an internal difficulty. The
consequences are worked out in §7.

---

## 2. Stage A — Shloka → Attested Text

Before translation there is a step the brief's chain leaves implicit, and it is where most
downstream errors originate.

**Input:** a verse, as encountered — in an edition, a website, a translation, a quotation.
**Output:** an attested textual object with full provenance.

| Operation | Purpose |
|---|---|
| Script normalisation | SLP1 internal, IAST display (005 §3) |
| Locus assignment | Text, chapter, verse — **per edition**, since numbering varies |
| Edition capture | Editor, publication, apparatus |
| Variant collection | All recorded readings, as parallel branches |
| Attestation grading | Critical edition > printed edition > digital corpus > quotation |

**Failure mode: the unattested quotation.** A verse circulating in secondary literature
without an edition reference is extremely common and is the dominant source of citation
error. Such text is admitted with `attestation: unverified` and is barred from the
authoritative corpus until checked.

**Information preserved:** everything. This stage is purely additive.

---

## 3. Stage B — Text → Translation

The brief places translation early. It needs a qualification that changes the architecture.

> **Translation is a validation artefact, not a compilation stage.**

Compiling *through* a translation loses the grammatical structure that Stage C depends on —
case, voice, mood, compound type. English cannot carry the ablative-as-reference-frame
distinction that carries requirement R10.

So the dependency is inverted:

```
Text ──▶ Grammar ──▶ Meaning ──┬──▶ Reasoning ──▶ …    (the compilation path)
                               │
                               └──▶ Translation        (generated, for review)
```

Translation is *generated from* the analysis and used to let a reviewer check the analysis.
This is the **round-trip test** of §8.2, and it is far more useful than translation-first.

**The exception:** texts with no reliable Sanskrit source. A translation-only path exists,
produces rules flagged `derivation: translation-only`, and carries a hard confidence
ceiling because the grammatical justification chain is absent. Whether such rules enter the
authoritative corpus at all is open (005 §12.3).

**Existing translations are used as evidence, not as input.** Multiple translations that
agree on the conditional structure raise interpretive confidence; disagreement flags the
verse for review. Translation divergence is one of the better automated signals for
"this verse is contested."

---

## 4. Stage C — Text → Grammar

This is the pipeline S0–S6 of `sanskrit_analysis_pipeline.md`, entire.

**Input:** attested text (+ variants).
**Output:** a *forest* of kāraka-labelled dependency analyses with scores.

**Information preserved:** the full lattice, with pruning decisions recorded. Every surviving
analysis retains character-offset spans into the source, so any downstream object can point
back at the exact substring it came from. This span-preservation is what makes the
traceability invariant reach all the way to the manuscript.

**Failure modes:** §9 of 005 in full; the three silent ones are ablative/genitive
syncretism, *bahuvrīhi* misclassification, and undetected elision.

---

## 5. Stage D — Grammar → Meaning

Where a parse becomes a domain-typed proposition. Three operations, in order.

### 5.1 Symbol resolution — with a deliberate restriction

Sanskrit technical terms resolve against domain namespaces:
`guru` → `choir:jyotisha/graha/Guru` rather than `choir:jyotisha/social/Guru`.

**But polysemy internal to the domain is *not* resolved here.** Following
`vedic_reasoning_methodology.md` §3.1: when the rule concludes something about Sūrya, the
question of whether that means *father*, *bone* or *authority* is answered by the query's
purpose, at execution time. Resolving it at compile time would bake one reading into the
corpus and make it answer only one kind of question.

> Compile-time resolution: **which entity**.
> Run-time resolution: **which signification of that entity**.

### 5.2 *Anuvṛtti* resolution — scope binding

Stage S7 of the Sanskrit pipeline, and the exact analogue of name binding.

```
Section head:  "In the matter of natal charts, reckoned from the Ascendant…"
                        │  establishes scope
Verse n:       "…Jupiter in a kendra from the Moon yields Gajakesarī."
                        │  overrides frame locally (candrāt), inherits application (jātaka)
```

Unbound free variables are **compile errors**. A rule whose subject or scope is unresolved
does not enter the corpus. Emitting it with a guessed default is the single most damaging
thing this compiler could do, because the result is a well-formed over-general rule that
fires where it should not.

### 5.3 Modality detection

Optative / gerundive morphology → injunctive force, feeding the *vidhi* / *arthavāda* gate
(`vedic_reasoning_methodology.md` §4.3). Non-injunctive verses are classified and stored,
but not compiled to rules. They remain available as *context* and as commentarial evidence.

**Information loss begins here.** Metre is dropped (recorded, not carried). Poetic figures
are noted but not modelled. Word order is normalised. All are retained in the source
mapping and none affect rule semantics — this is the first *deliberate* loss and it is
documented as such.

---

## 6. Stage E — Meaning → Reasoning

The step that turns a proposition into a *rule*: identifying which parts are antecedent,
which consequent, and what modifies the link.

### 6.1 Structural decomposition

| Element | Grammatical signal | Example marker |
|---|---|---|
| Condition | Conditional particle; locative absolute; relative clause | *cet*, *yadi*, *yadā*; locative absolute |
| Conclusion | Main clause; optative verb | *bhavet*, *syāt* |
| Scope restriction | Adverbial; scope-limiting compound | *jātake*, *divā* |
| Exception | Adversative particle; negated condition | *tu*, *kintu*, *na tu* |
| Strength qualifier | Adjective on the conclusion; degree term | *pūrṇa*, *alpa* |
| Named result | *nāmadheya* construction | *nāma*, *saṃjñā* |

Sanskrit's conditional constructions are various and frequently *implicit* — a locative
absolute carries conditional force with no overt particle at all. This is a real extraction
hazard: a verse can be a conditional rule without containing anything a keyword search
would find. Recognising implicit conditionals requires the dependency parse, which is one of
the arguments for not compiling through translation.

### 6.2 Cross-reference resolution — linking

Rules reference other rules and definitions constantly: *kendra* is defined elsewhere;
combustion has its own rule; debilitation is a table.

This is **linking**, with the same properties:

- Unresolved references are errors, not warnings.
- References resolve against a *versioned* corpus, so a rule compiled against one version of
  the *kendra* definition records that dependency.
- Circular definitions are detected and rejected.
- The dependency graph is what enables incremental recompilation when a definition changes.

### 6.3 Exception attachment and typing

Exceptions are attached to the rule and typed per `computational_primitives.md` §3.12.

**Default to undercutting.** A cancellation clause in śāstra almost never asserts the
opposite conclusion; it withdraws the rule. Typing an exception as rebutting requires
positive textual evidence that the opposite is asserted. Getting this default backwards
manufactures conclusions the corpus never made.

Exceptions are frequently in *different verses*, sometimes different chapters, and
occasionally different texts. The compiler cannot always know it has found them all —
which is why `exception_completeness` is tracked as a distinct confidence input
(`confidence_framework.md` §3.2) rather than assumed.

---

## 7. Stage F — Reasoning → Computational Graph (HIR)

Emission into the high-level IR, specified in `choir_intermediate_representation.md` §3.

The distinguishing property: **HIR represents unresolved ambiguity explicitly.**

```
Ambiguity {
  id, span,                      # where in the source
  kind: segmentation | compound_type | sense | attachment | scope,
  alternatives: [ { reading, score, consequence } ],
  status: open | resolved | contested,
  resolution: { chosen, by, grounds, timestamp }?
}
```

Every downstream object that depends on an open ambiguity inherits a reference to it. A
rule with open ambiguities can still be *inspected*, *discussed*, and *counted* — it simply
cannot be *executed* until they are closed.

This is the structural difference from a conventional compiler, and it is why HIR is a
distinct layer rather than an implementation detail.

### 7.1 The adjudication loop

```
        compile ──▶ ambiguity diagnostics ──▶ scholar review
           ▲                                        │
           │                                        ▼
        resolution cache ◀────────── recorded resolution
     (reused automatically on
      structurally identical cases)
```

The resolution cache is worth emphasising. Śāstric verse is formulaic: the same
constructions recur across hundreds of verses. A resolution recorded once — "in this
construction, *candrāt* is *apādāna*, not genitive" — applies automatically to every
structurally identical instance thereafter, with provenance naming the original
adjudication. The scholar's cost is front-loaded and amortised.

Cached resolutions are themselves versioned and revisable. Revising one invalidates and
recompiles everything that used it — which is exactly the incremental-recompilation
machinery from §6.2.

---

## 8. Stage G — Graph → Executable Rule

HIR → MIR → LIR, per `choir_intermediate_representation.md` §§4–5.

### 8.1 What each lowering does

| Lowering | Operation | Loses | Preserves |
|---|---|---|---|
| **HIR → MIR** | Resolve ambiguities; canonicalise; normalise; dedup | Rejected alternatives (moved to provenance) | Source spans; all semantics |
| **MIR → LIR** | Index; compile match patterns; order for execution | Nothing semantic | Everything, plus back-pointers |

**MIR is the interchange layer** — domain-independent, fully resolved, canonical. It is what
`domain_independence.md` tests portability against, and what a legal or clinical front end
would also target.

**Canonicalisation** is what makes content addressing work (`reasoning_ontology.md` §7.2):
two verses stating the same rule normalise to the same MIR, hash identically, and unify —
producing one rule with two independent attestations. That is a genuine evidential signal
obtained for free from the identity scheme.

### 8.2 The round-trip test

The compiler's primary self-check:

```
Shloka ──compile──▶ Rule ──decompile──▶ Paraphrase ──compare──▶ Original
```

A rule that cannot be paraphrased back into something a scholar recognises as the verse's
content has lost something. This is a **fidelity test**, not an equivalence test — the
paraphrase will not be the verse — and it is scored by human review against a rubric:

| Criterion | Question |
|---|---|
| Condition fidelity | Are the antecedents the same, with the same scope? |
| Conclusion fidelity | Is the consequent the same, with the same strength and modality? |
| Exception fidelity | Are all exceptions present and correctly typed? |
| Scope fidelity | Same context, same reference frame? |
| No addition | Does the rule assert anything the verse does not? |

The last criterion is the one that catches the worst failures. **Over-generation is more
dangerous than under-generation**: a missing rule is a gap; an invented rule is a
falsehood with a citation attached.

---

## 9. Diagnostics

The compiler's diagnostic taxonomy — modelled on compiler error levels, because the
severity distinctions are the same.

| Level | Meaning | Corpus admission |
|---|---|---|
| **Fatal** | Cannot proceed | Rejected |
| **Error** | Structurally incomplete | Rejected until fixed |
| **Ambiguity** | Multiple readings; needs adjudication | Held, not executable |
| **Warning** | Compiles, but suspicious | Admitted, flagged |
| **Note** | Informational | Admitted |

| Code | Level | Condition |
|---|---|---|
| `E-ATTEST` | Error | No verifiable edition |
| `E-SEG` | Error | No valid segmentation |
| `E-BIND` | Error | Unresolved free variable (*anuvṛtti* failure) |
| `E-LINK` | Error | Unresolved cross-reference |
| `E-CYCLE` | Fatal | Circular definition |
| `A-SEG` | Ambiguity | Multiple coherent segmentations |
| `A-CMPD` | Ambiguity | Compound type undetermined |
| `A-SCOPE` | Ambiguity | Multiple candidate scope bindings |
| `A-SENSE` | Ambiguity | Unresolved lexical sense |
| `W-ARTHA` | Warning | May be *arthavāda*; injunctive force uncertain |
| `W-EXC` | Warning | Exception set may be incomplete |
| `W-TRANS` | Warning | Translation-only derivation |
| `W-VARIANT` | Warning | Meaning depends on a contested reading |
| `N-DEDUP` | Note | Unified with an existing rule (independent attestation) |

`W-ARTHA` and `W-EXC` are the two warnings that most often indicate a real problem, and
both resist automation — they are the natural focus of scholar review time.

---

## 10. Confidence propagation

Each stage contributes to **extraction confidence** (`confidence_framework.md` §3.1). The
composition rule is deliberately pessimistic:

> Stage confidences do **not** multiply. Extraction confidence is bounded by the *minimum*
> stage confidence, then reduced further for open ambiguities.

Multiplication is wrong here for two reasons: stage confidences are not independent (a bad
segmentation causes a bad parse), and multiplication of many high values produces a
misleadingly low result while a single catastrophic stage failure gets diluted. A chain is
as strong as its weakest link, and this one is literally a chain.

```
extraction_confidence = min(stage_confidences) × ambiguity_penalty(open_count)
                      × attestation_factor(source_grade)
```

Human adjudication *raises* the relevant stage confidence, with the adjudication recorded —
so a scholar-resolved ambiguity is not merely closed, it is closed *by someone*, on the
record.

---

## 11. Open questions

1. **Can Stage E be automated at all?** Identifying antecedent/consequent structure in
   metrically-reordered verse with implicit conditionals may be irreducibly interpretive.
   If it is not automatable, throughput is bounded by scholar availability and the project
   should be planned around that.
2. **Resolution cache generalisation.** Structural identity is safe. Structural
   *similarity* would generalise much further but risks propagating an error across
   hundreds of rules. Where the line sits is unresolved and consequential.
3. **Cross-text linking.** Exceptions stated in a different text raise a question the
   compiler cannot answer alone: is that text *authoritative* for this one? This is a
   source-authority question (`conflict_resolution.md` §5.3), not a compilation question,
   but it blocks linking.
4. **Round-trip scoring cost.** §8.2 requires human review per rule, which does not scale.
   Whether an automated paraphrase-similarity proxy is trustworthy enough for triage —
   given the neural/symbolic boundary in `knowledge_graph_spec.md` §2.5 — is open. Note
   that using it for *triage of review effort* does not violate that boundary; using it as
   a fidelity *score* would.
5. **Incremental recompilation scope.** Revising a cached resolution or a definition
   invalidates dependents transitively. Whether the blast radius is manageable at corpus
   scale is unknown.

---

## 12. Summary

- The chain is **Text → Grammar → Meaning → Reasoning → HIR → MIR → LIR**, with
  **translation moved out of the compilation path** and used as a generated validation
  artefact instead.
- Two compiler analogies are exact and load-bearing: ***anuvṛtti* is scope resolution**
  (unbound variables are errors) and **cross-reference resolution is linking**
  (unresolved references are errors).
- **Ambiguity is a first-class output.** The compiler emits diagnostics for a scholar rather
  than guessing, and records every adjudication in a **resolution cache** that amortises
  across the formulaic verse of the corpus.
- **Compile-time resolves which entity; run-time resolves which signification.** Resolving
  symbolism early would restrict the corpus to one kind of question.
- **Exceptions default to undercutting**; typing one as rebutting requires positive textual
  evidence.
- Extraction confidence is the **minimum** across stages, not the product — the chain is as
  strong as its weakest link.
- The **round-trip test** scores fidelity, and its most important criterion is *no
  addition*: over-generation is worse than under-generation, because an invented rule is a
  falsehood carrying a citation.
