# Shloka Compiler

| | |
|---|---|
| **Document ID** | YK-R-006 |
| **Source** | `choir/research/phase-2-vedic/shloka_compiler.md` (006) |
| **Series** | CHOIR Research Programme |
| **Revision** | A |
| **Status** | Active |
| **Last Updated** | 2026-08-23 |

## Abstract

This document specifies the six transformations that carry a Sanskrit verse to an executable
rule, and states what each one preserves and what it loses (§1). It argues that
translation is a validation artefact generated from the analysis rather than a stage in the
compilation path (§3), that *anuvṛtti* resolution is exactly scope resolution and
cross-reference resolution is exactly linking — in both cases unresolved references are
errors, not warnings (§5.2, §6.2) — and that unresolved ambiguity is a first-class compiler
output emitted for scholar adjudication rather than guessed at (§1.1, §7).

The source document is marked **Status: Draft for review** and is published here as an
**Active** research document: drafted, but **not accepted as specification**. The
document-level statement of that condition is made by `choir/research/README.md`: "All 18
deliverables drafted. None accepted. Every document is a hypothesis, per `MANIFESTO.md`."
`MANIFESTO.md` itself states the rule at the level of objects rather than documents: "Treat
every computational object as a hypothesis rather than an established truth."

## Research Question

The source states its own framing at §1: "The brief specifies the pipeline to be researched:
`Shloka → Translation → Grammar → Meaning → Reasoning → Computational Graph → Executable
Rule`. Each arrow is a transformation with its own inputs, outputs, failure modes, and
information loss. This document specifies all six and states what is preserved across each."

A second question is embedded in the framing and is answered against the brief rather than
with it: whether translation belongs in that chain at all (§3).

## Finding

### The compiler analogy is load-bearing, and it breaks in exactly one place

The document states that "the compiler analogy is used seriously, not decoratively," on the
ground that "every stage has a genuine counterpart in conventional compilation, and the
correspondence is load-bearing: it tells us what the hard problems are and where the
established solutions live" (§1). The correspondence table it gives:

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

Two of these are called exact — scope resolution and linking — and the document says they
"are the ones that catch the errors most likely to produce silently wrong rules" (§1).

The analogy is stated to break in one place, and the break is not treatable by engineering:
"A conventional compiler's source language is unambiguous by construction. Ours is not, and
no amount of engineering will make it so" (§1.1). The consequence is stated as a governing
property:

> **CHOIR is a compiler whose front end cannot always decide, and whose correct behaviour
> in that case is to emit a diagnostic rather than a guess.** (§1.1)

This makes the shloka compiler "an **interactive** compiler with a human adjudication gate,"
and makes "*ambiguity a first-class output* rather than an internal difficulty" (§1.1).

### Stage A — Shloka → Attested Text

The document adds a stage the brief's chain leaves implicit, "and it is where most downstream
errors originate" (§2). Input is a verse as encountered; output is an attested textual object
with full provenance. Operations: script normalisation (SLP1 internal, IAST display, citing
005 §3); locus assignment per edition, "since numbering varies"; edition capture; variant
collection as parallel branches; and attestation grading, ordered "critical edition > printed
edition > digital corpus > quotation."

The named failure mode is the unattested quotation: "A verse circulating in secondary
literature without an edition reference is extremely common and is the dominant source of
citation error." Such text is admitted with `attestation: unverified` and "is barred from the
authoritative corpus until checked" (§2). Information preserved at this stage: "everything.
This stage is purely additive."

### Stage B — translation is removed from the compilation path

The document qualifies the brief in a way it says "changes the architecture":

> **Translation is a validation artefact, not a compilation stage.** (§3)

The reason given is information loss: "Compiling *through* a translation loses the
grammatical structure that Stage C depends on — case, voice, mood, compound type. English
cannot carry the ablative-as-reference-frame distinction that carries requirement R10" (§3).
The dependency is therefore inverted — grammar and meaning are computed from the text, and
translation is generated *from* the analysis so a reviewer can check the analysis. That check
is the round-trip test of §8.2, which the document says "is far more useful than
translation-first."

One exception is recorded: texts with no reliable Sanskrit source. A translation-only path
exists, produces rules flagged `derivation: translation-only`, and "carries a hard confidence
ceiling because the grammatical justification chain is absent." The document explicitly leaves
open "whether such rules enter the authoritative corpus at all," citing 005 §12.3 (§3).

Existing translations "are used as evidence, not as input": agreement across translations on
conditional structure raises interpretive confidence, disagreement flags the verse for review,
and "translation divergence is one of the better automated signals for 'this verse is
contested'" (§3).

### Stage C — Text → Grammar

This stage is "the pipeline S0–S6 of `sanskrit_analysis_pipeline.md`, entire" (§4). Its output
is "a *forest* of kāraka-labelled dependency analyses with scores" — not a single parse.
Information preserved is "the full lattice, with pruning decisions recorded," and every
surviving analysis "retains character-offset spans into the source, so any downstream object
can point back at the exact substring it came from." The document states that "this
span-preservation is what makes the traceability invariant reach all the way to the
manuscript" (§4).

Failure modes are deferred to 005 §9 in full, with three named as silent: "ablative/genitive
syncretism, *bahuvrīhi* misclassification, and undetected elision" (§4).

### Stage D — Grammar → Meaning

Three operations in order (§5).

**Symbol resolution is deliberately restricted.** Sanskrit technical terms resolve against
domain namespaces (`guru` → `choir:jyotisha/graha/Guru` rather than
`choir:jyotisha/social/Guru`), "**But polysemy internal to the domain is *not* resolved
here.**" Following `vedic_reasoning_methodology.md` §3.1, "when the rule concludes something
about Sūrya, the question of whether that means *father*, *bone* or *authority* is answered by
the query's purpose, at execution time. Resolving it at compile time would bake one reading
into the corpus and make it answer only one kind of question" (§5.1). The split is stated as:

> Compile-time resolution: **which entity**.
> Run-time resolution: **which signification of that entity**. (§5.1)

***Anuvṛtti* resolution is scope binding** — stage S7 of the Sanskrit pipeline, "and the exact
analogue of name binding" (§5.2). The worked illustration is a section head establishing scope
("In the matter of natal charts, reckoned from the Ascendant…") and a verse that overrides the
reference frame locally (*candrāt*) while inheriting the application (*jātaka*): "…Jupiter in a
kendra from the Moon yields Gajakesarī." The rule is unconditional: "Unbound free variables are
**compile errors**. A rule whose subject or scope is unresolved does not enter the corpus.
Emitting it with a guessed default is the single most damaging thing this compiler could do,
because the result is a well-formed over-general rule that fires where it should not."

**Modality detection** maps optative/gerundive morphology to injunctive force, feeding the
*vidhi* / *arthavāda* gate of `vedic_reasoning_methodology.md` §4.3. "Non-injunctive verses are
classified and stored, but not compiled to rules. They remain available as *context* and as
commentarial evidence" (§5.3).

The document marks this stage as the point where "**Information loss begins**": metre is
dropped (recorded, not carried), poetic figures are noted but not modelled, word order is
normalised. "All are retained in the source mapping and none affect rule semantics — this is
the first *deliberate* loss and it is documented as such" (§5.3).

### Stage E — Meaning → Reasoning

The step that identifies antecedent, consequent, and what modifies the link (§6). Structural
decomposition is given as:

| Element | Grammatical signal | Example marker |
|---|---|---|
| Condition | Conditional particle; locative absolute; relative clause | *cet*, *yadi*, *yadā*; locative absolute |
| Conclusion | Main clause; optative verb | *bhavet*, *syāt* |
| Scope restriction | Adverbial; scope-limiting compound | *jātake*, *divā* |
| Exception | Adversative particle; negated condition | *tu*, *kintu*, *na tu* |
| Strength qualifier | Adjective on the conclusion; degree term | *pūrṇa*, *alpa* |
| Named result | *nāmadheya* construction | *nāma*, *saṃjñā* |

The document names a hazard here: "Sanskrit's conditional constructions are various and
frequently *implicit* — a locative absolute carries conditional force with no overt particle at
all… a verse can be a conditional rule without containing anything a keyword search would find."
Recognising implicit conditionals "requires the dependency parse, which is one of the arguments
for not compiling through translation" (§6.1).

**Cross-reference resolution is linking** (§6.2), with four stated properties: unresolved
references are errors, not warnings; references resolve against a *versioned* corpus, so a rule
records which version of e.g. the *kendra* definition it was compiled against; circular
definitions are detected and rejected; and the dependency graph "is what enables incremental
recompilation when a definition changes."

**Exceptions default to undercutting** (§6.3), typed per `computational_primitives.md` §3.12.
"A cancellation clause in śāstra almost never asserts the opposite conclusion; it withdraws the
rule. Typing an exception as rebutting requires positive textual evidence that the opposite is
asserted. Getting this default backwards manufactures conclusions the corpus never made." The
document also concedes a limit it cannot engineer away: exceptions "are frequently in *different
verses*, sometimes different chapters, and occasionally different texts. The compiler cannot
always know it has found them all — which is why `exception_completeness` is tracked as a
distinct confidence input (`confidence_framework.md` §3.2) rather than assumed."

### Stage F — Reasoning → Computational Graph (HIR)

Emission into the high-level IR specified in `choir_intermediate_representation.md` §3. "The
distinguishing property: **HIR represents unresolved ambiguity explicitly.**" The recorded
shape:

```
Ambiguity {
  id, span,                      # where in the source
  kind: segmentation | compound_type | sense | attachment | scope,
  alternatives: [ { reading, score, consequence } ],
  status: open | resolved | contested,
  resolution: { chosen, by, grounds, timestamp }?
}
```

"Every downstream object that depends on an open ambiguity inherits a reference to it. A rule
with open ambiguities can still be *inspected*, *discussed*, and *counted* — it simply cannot be
*executed* until they are closed." The document states this "is the structural difference from a
conventional compiler, and it is why HIR is a distinct layer rather than an implementation
detail" (§7).

The adjudication loop runs compile → ambiguity diagnostics → scholar review → recorded
resolution → resolution cache, which is then "reused automatically on structurally identical
cases" (§7.1). The document emphasises the cache on the grounds that "śāstric verse is
formulaic: the same constructions recur across hundreds of verses. A resolution recorded once —
'in this construction, *candrāt* is *apādāna*, not genitive' — applies automatically to every
structurally identical instance thereafter, with provenance naming the original adjudication.
The scholar's cost is front-loaded and amortised." Cached resolutions "are themselves versioned
and revisable. Revising one invalidates and recompiles everything that used it."

### Stage G — Graph → Executable Rule

HIR → MIR → LIR, per `choir_intermediate_representation.md` §§4–5.

| Lowering | Operation | Loses | Preserves |
|---|---|---|---|
| **HIR → MIR** | Resolve ambiguities; canonicalise; normalise; dedup | Rejected alternatives (moved to provenance) | Source spans; all semantics |
| **MIR → LIR** | Index; compile match patterns; order for execution | Nothing semantic | Everything, plus back-pointers |

"**MIR is the interchange layer** — domain-independent, fully resolved, canonical. It is what
`domain_independence.md` tests portability against, and what a legal or clinical front end would
also target" (§8.1). Canonicalisation "is what makes content addressing work
(`reasoning_ontology.md` §7.2): two verses stating the same rule normalise to the same MIR, hash
identically, and unify — producing one rule with two independent attestations. That is a genuine
evidential signal obtained for free from the identity scheme."

**The round-trip test** is the compiler's primary self-check (§8.2): compile the shloka to a
rule, decompile the rule to a paraphrase, compare the paraphrase to the original. The document
is explicit that "this is a **fidelity test**, not an equivalence test — the paraphrase will not
be the verse — and it is scored by human review against a rubric":

| Criterion | Question |
|---|---|
| Condition fidelity | Are the antecedents the same, with the same scope? |
| Conclusion fidelity | Is the consequent the same, with the same strength and modality? |
| Exception fidelity | Are all exceptions present and correctly typed? |
| Scope fidelity | Same context, same reference frame? |
| No addition | Does the rule assert anything the verse does not? |

The last criterion "is the one that catches the worst failures. **Over-generation is more
dangerous than under-generation**: a missing rule is a gap; an invented rule is a falsehood with
a citation attached" (§8.2).

### Diagnostics

The taxonomy is "modelled on compiler error levels, because the severity distinctions are the
same" (§9).

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

The document records that "`W-ARTHA` and `W-EXC` are the two warnings that most often indicate a
real problem, and both resist automation — they are the natural focus of scholar review time"
(§9).

### Confidence propagation

Each stage contributes to extraction confidence per `confidence_framework.md` §3.1, and "the
composition rule is deliberately pessimistic":

> Stage confidences do **not** multiply. Extraction confidence is bounded by the *minimum*
> stage confidence, then reduced further for open ambiguities. (§10)

Two reasons are given against multiplication: "stage confidences are not independent (a bad
segmentation causes a bad parse), and multiplication of many high values produces a misleadingly
low result while a single catastrophic stage failure gets diluted. A chain is as strong as its
weakest link, and this one is literally a chain." The stated formula:

```
extraction_confidence = min(stage_confidences) × ambiguity_penalty(open_count)
                      × attestation_factor(source_grade)
```

"Human adjudication *raises* the relevant stage confidence, with the adjudication recorded — so a
scholar-resolved ambiguity is not merely closed, it is closed *by someone*, on the record" (§10).

## Architectural Implications

**The compilation chain is Text → Grammar → Meaning → Reasoning → HIR → MIR → LIR, with
translation outside it** (§3, §12). The source frames this as a qualification to the brief —
"Translation is a validation artefact, not a compilation stage" — rather than as a conformance
rule for implementers. What it does state is that translations enter as generated review
artefacts and as evidence, and that translation-only derivations carry the `W-TRANS` warning
and a hard confidence ceiling.

**Ambiguity must be representable in the IR, not merely handled in the front end.** Because HIR
carries explicit `Ambiguity` records and downstream objects inherit references to open ones, the
executability gate is structural: a rule with open ambiguities is inspectable, discussable and
countable but not executable (§7). This is the source's stated reason for HIR being a distinct
layer rather than an implementation detail.

**Two error classes are hard rejections rather than degradations.** Unbound *anuvṛtti* variables
(`E-BIND`) and unresolved cross-references (`E-LINK`) keep a rule out of the corpus (§5.2, §6.2);
circular definitions (`E-CYCLE`) are fatal. The document's justification is that the failure mode
of guessing is a well-formed over-general rule, which is worse than absence.

**Symbolic interpretation is deferred to execution time.** Compile-time resolves which entity;
run-time resolves which signification (§5.1). A corpus that resolved symbolism early would, per
the source, "answer only one kind of question."

**Versioning and incremental recompilation are required, not optional.** Rules record the corpus
version of every definition they link against, cached resolutions are versioned and revisable,
and revising one "invalidates and recompiles everything that used it" (§6.2, §7.1).

**MIR is the portability contract.** It is the layer `domain_independence.md` tests against and
the target a legal or clinical front end would also emit to (§8.1); canonicalisation at MIR is
what makes content addressing and independent-attestation unification work
(`reasoning_ontology.md` §7.2).

**Throughput may be bounded by scholar availability.** The adjudication gate, the human-scored
round-trip rubric, and the two hand-reviewed warnings all place scholars on the critical path;
the source raises this as an open planning constraint rather than a solved one, conditional on
Stage E not being automatable (§11, open questions 1 and 4).

## Open Questions

The source records five (§11), reproduced with its own hedges:

1. **Can Stage E be automated at all?** "Identifying antecedent/consequent structure in
   metrically-reordered verse with implicit conditionals may be irreducibly interpretive. If it
   is not automatable, throughput is bounded by scholar availability and the project should be
   planned around that."
2. **Resolution cache generalisation.** "Structural identity is safe. Structural *similarity*
   would generalise much further but risks propagating an error across hundreds of rules. Where
   the line sits is unresolved and consequential."
3. **Cross-text linking.** Exceptions stated in a different text raise a question "the compiler
   cannot answer alone: is that text *authoritative* for this one? This is a source-authority
   question (`conflict_resolution.md` §5.3), not a compilation question, but it blocks linking."
4. **Round-trip scoring cost.** The round-trip test "requires human review per rule, which does
   not scale. Whether an automated paraphrase-similarity proxy is trustworthy enough for triage —
   given the neural/symbolic boundary in `knowledge_graph_spec.md` §2.5 — is open. Note that using
   it for *triage of review effort* does not violate that boundary; using it as a fidelity *score*
   would."
5. **Incremental recompilation scope.** "Revising a cached resolution or a definition invalidates
   dependents transitively. Whether the blast radius is manageable at corpus scale is unknown."

Two further items are left unresolved outside §11: whether translation-only rules enter the
authoritative corpus at all (§3, deferred to 005 §12.3), and the source's own status — it is
marked "Draft for review," and no acceptance is recorded.

## Related Documents

**Depends on:**

- [YK-R-005 — Sanskrit Analysis Pipeline](YK-R-005-sanskrit-analysis-pipeline.md) — supplies stages S0–S6 (Stage C) and S7 (*anuvṛtti* resolution), the script/attestation conventions of §2, and the failure modes deferred to at §4.
- [YK-R-004 — Vedic Reasoning Methodology](YK-R-004-vedic-reasoning-methodology.md) — supplies the run-time symbolism rule (§3.1) and the *vidhi* / *arthavāda* gate (§4.3).

**Feeds:**

- [YK-R-013 — CHOIR Intermediate Representation](YK-R-013-choir-intermediate-representation.md) — HIR §3 and the HIR → MIR → LIR lowerings §§4–5.
- [YK-R-007 — Rule Extraction Framework](YK-R-007-rule-extraction-framework.md)
- [YK-R-008 — Canonical Shloka Analysis (Benchmark)](YK-R-008-canonical-shloka-analysis-benchmark.md)

**Cited:**

- [YK-R-001 — Computational Primitive Specification](YK-R-001-computational-primitive-specification.md) — §3.12, exception typing (undercutting vs rebutting).
- [YK-R-002 — Reasoning Ontology](YK-R-002-reasoning-ontology.md) — §7.2, content addressing.
- [YK-R-003 — Knowledge Graph Specification](YK-R-003-knowledge-graph-specification.md) — §2.5, the neural/symbolic boundary.
- [YK-R-010 — Conflict Resolution](YK-R-010-conflict-resolution.md) — §5.3, source authority.
- [YK-R-011 — Confidence Framework](YK-R-011-confidence-framework.md) — §3.1 extraction confidence, §3.2 `exception_completeness`.
- [YK-R-016 — Domain Independence](YK-R-016-domain-independence.md) — portability tested against MIR.
