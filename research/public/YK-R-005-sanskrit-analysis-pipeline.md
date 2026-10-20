# Sanskrit Analysis Pipeline

| | |
|---|---|
| **Document ID** | YK-R-005 |
| **Source** | `choir/research/phase-2-vedic/sanskrit_analysis_pipeline.md` (005) |
| **Series** | CHOIR Research Programme |
| **Revision** | A |
| **Status** | Active |
| **Last Updated** | 2026-08-23 |

## Abstract

This document specifies a nine-stage pipeline (S0–S8) for analysing Sanskrit śāstric verse into the CHOIR ambiguity-preserving intermediate representation, governed by a single principle: ambiguity is preserved as a lattice of ranked alternatives until evidence bearing on it is available, and pruning flows backward from later stages to earlier ones (§1, §2). It asserts as "the load-bearing insight of the whole pipeline" that *kāraka* roles map directly onto the role-labelled participants of a CHOIR hyperedge — the grammatical analysis becomes the storage structure rather than being translated away (§6.4) — and heads its *anuvṛtti* (cross-verse inheritance) stage "the stage that is usually missing": a scope-resolution stage whose failure mode is a silent, well-formed, over-general rule (§7, §11). Both are design positions; the source reports no measured results.

The document is carried at status **Active**: it is drafted but **not accepted as specification**. Per `choir/research/README.md`, all 18 research deliverables are drafted and none accepted: "Every document is a hypothesis, per `MANIFESTO.md`." Its own status line reads "Draft for review".

## Research Question

The source does not state a single interrogative research question. It states a governing design principle and derives the pipeline from it (§1):

> **Principle: ambiguity-preserving until evidence is available.**
>
> Each stage produces a *lattice* of ranked alternatives, not a single output. Ambiguity is
> resolved at the latest stage that has evidence bearing on it, and every resolution is
> recorded with its justification.

The question the document sets out to answer is therefore how Sanskrit śāstric verse — "ambiguous at every level" — is to be analysed into CHOIR's representation without committing to resolutions before the evidence that would settle them exists. The document names the instinctive alternative and rejects it: resolving each ambiguity as early as possible and passing one answer forward "is wrong here, and wrong in a way that is expensive to undo" (§1). Its stated reason is structural: segmentation ambiguity is frequently resolvable only by semantics, and semantics is four stages downstream, so "a pipeline that commits at stage 2 cannot use stage 6's evidence" (§1).

## Finding

### The pipeline and its direction of flow

The pipeline runs S0 Normalisation → S1 Metrical analysis → S2 Sandhi splitting → S3 Morphology → S4 Compound (*samāsa*) analysis → S5 *Anvaya* / dependency parse → S6 *Kāraka* labelling → S7 *Anuvṛtti* resolution → S8 Semantic frame, emitting CHOIR HIR (§2). The document marks S2 and S4 as HIGH ambiguity and S7 as CRITICAL.

The distinguishing structural claim is that pruning flows *backward*: "S8 semantic plausibility is the strongest disambiguator available and must be able to invalidate an S2 segmentation" (§2). Three consequences are drawn from the governing principle (§1):

1. **Every stage is lattice-in, lattice-out**, with a pruning budget rather than a single-best decision.
2. **Every resolution is a recorded object** — which alternative, on what grounds, by whom or by what model — feeding extraction confidence (`rule_extraction_framework.md` §6).
3. **Later stages may reject earlier choices**, reactivating a pruned alternative. The pipeline is described as "a constraint solver more than a conveyor belt."

### S0 — Normalisation, and variant readings

S0 is "deterministic and unglamorous, but it is where provenance is established" (§3). Internal representation is **SLP1**, chosen because one byte per phoneme makes sandhi rules expressible as simple string operations; **IAST** is the display and identifier form. Unicode NFC normalisation is applied, along with handling of *anusvāra*/*candrabindu* and *avagraha* variants that differ between editions. Edition capture records text, edition, editor, page/verse locus, and variant readings from the apparatus criticus where available.

The document states that **variant readings are not noise**: where an edition records variants, all are carried forward as parallel branches with edition-attributed provenance, and a rule whose meaning depends on a contested reading must show that in its confidence (`confidence_framework.md` §3.1).

### S1 — Metre first, and the trade it forces

Identifying metre before segmenting is called "a deliberate ordering choice, and it pays for itself" (§4). Classical metres are defined by syllable count and *laghu*/*guru* patterns per *pāda*; *anuṣṭubh* is 4 pādas of 8 syllables. Three constraints on segmentation are given: pāda boundaries are usually word boundaries and sandhi across them is restricted, so metre supplies high-confidence split points for free; syllable count is "a hard checksum" such that a segmentation implying the wrong count is *invalid*, not merely unlikely; and light/heavy patterns disambiguate vowel length, which disambiguates case endings.

The section records a caveat against itself. Metrical requirements also *cause* distortions — word order rearranged for metre, particles inserted as padding (*pādapūraṇa*), occasionally irregular forms — so "metre helps segmentation while *hurting* parsing", and S5 must not assume prose word order. The trade is defended on the ground that segmentation errors are more expensive than parse errors: "a bad split produces nonsense words, whereas a bad parse produces a recoverable wrong reading" (§4).

### S2 — Sandhi splitting: "the hardest stage, and the one where most pipelines fail"

Splitting is the inverse of an obligatory euphonic combination and is "massively non-deterministic": a single surface string may admit dozens of valid splits, most of them lexically real. The operation is lossy — several distinct underlying sequences map to the same surface form — so the inverse is "a genuine one-to-many relation, not a hard parse" (§5.1).

The document compares three approaches (§5.2):

| Approach | Mechanism | Strengths | Weaknesses |
|---|---|---|---|
| **Rule-based / FST** | Pāṇinian sandhi rules as finite-state transducers | Complete, explainable, high recall | Massive over-generation; no ranking |
| **Lexicon-driven lattice** | Generate splits, keep those whose segments are attested forms; shortest-path or weighted search | Prunes hard; well understood | Fails on unattested proper nouns and technical terms |
| **Statistical / neural** | Seq2seq or tagging models trained on aligned corpora | Best single-best accuracy reported in the literature | Opaque; needs training data; degrades on domain-specific vocabulary |

The recommended architecture is "**Generate broadly, rank statistically, validate morphologically, prune late**" — FST over-generation, then lexicon filter, then neural reranking, into an n-best lattice, with morphological validity from S3 and semantic plausibility from S8 pruning back into it (§5.3). Three decisions are named: keep n-best rather than 1-best, because "the correct split for a technical śāstric line is frequently not the highest-scoring one under a general-domain model, because Jyotiṣa vocabulary is specialised"; a domain lexicon is **mandatory** — without graha, rāśi, yoga and technical terms, "`gajakesarī` may be split into constituents and the *name of the yoga* — which is the rule's conclusion — vanishes"; and rejected alternatives must be recorded, both for scholarly contest and because they feed extraction confidence.

The failure signature is stated explicitly: a wrong split "does not usually produce an obvious error; it produces a *different valid sentence*." This is given as the reason S2 errors must be caught downstream by semantic implausibility rather than local validity checks, "and why the lattice must survive that far" (§5.4).

### S3–S6 — Morphology, compounds, parse, roles

**S3.** Sanskrit nominals decline for 8 cases × 3 numbers × 3 genders; verbs inflect for person, number, tense/mood (*lakāra*), voice and derivational class. The analysis is many-to-many. The document flags one syncretism as consequential: the genitive singular and ablative singular of *a*-stems are homographs, and "that particular syncretism matters enormously here" (§6.1). Output is a lattice of `(stem, POS, features)` tuples with scores, feeding back to prune S2.

**S4.** Compounds "carry much of the conditional content" (§6.2). Six types are tabulated — *tatpuruṣa*, *karmadhāraya*, *dvigu*, *bahuvrīhi*, *dvandva*, *avyayībhāva* — with the head of a *bahuvrīhi* marked as lying **outside** the compound. The **bahuvrīhi hazard** is stated as a class of error rather than a degradation: misclassifying a *bahuvrīhi* as a *tatpuruṣa* "does not produce a slightly-off reading; it produces a reading about the wrong entity entirely. In a rule corpus this silently changes what the rule is about." Three decisions are required per compound — constituency (recursively), type, and head — and all three are ambiguous and feed the lattice.

**S5.** *Anvaya*, the traditional commentarial reordering of verse into prose order, "is exactly a dependency parse presented as a word sequence." Commentaries supplying *anvaya* are therefore treated as **gold-standard parse annotations**, described as "a significant and under-exploited resource: the tradition has been publishing parse trees for centuries" (§6.3). Dependency, not constituency, parsing is held to be the right formalism because word order is relatively free and morphology carries what word order carries in English; verse reordering makes surface-order heuristics "actively misleading."

**S6 — the payoff stage.** Pāṇini's *kāraka* system assigns semantic roles to participants in an action, mapped by the document to CHOIR as follows (§6.4):

| *Kāraka* | Role | Typical case | CHOIR mapping |
|---|---|---|---|
| *kartṛ* | Agent | Nominative | Subject / situated entity |
| *karma* | Patient / object | Accusative | Affected entity |
| *karaṇa* | Instrument | Instrumental | Means / mechanism |
| *sampradāna* | Recipient | Dative | Beneficiary |
| *apādāna* | Source / point of departure | **Ablative** | **Reference frame** |
| *adhikaraṇa* | Locus | **Locative** | **Location / containing region** |

"**Kāraka is not case.**" The mapping is many-to-many — the same role surfaces in different cases depending on voice and construction, and the same case realises different roles — which is why S6 is a distinct stage and not a lookup on S3's output. Two mappings are said to do the heavy lifting in Jyotiṣa: *adhikaraṇa* (locative) → occupancy, "*meṣe*" = "in Aries", "the most common single construction in the corpus"; and *apādāna* (ablative) → reference frame, "*candrāt*" = "from the Moon", the construction carrying the parameter identified as requirement R10 in `vedic_reasoning_methodology.md` §7.

The document names this "the load-bearing insight of the whole pipeline": kāraka roles map directly onto the role-labelled participants of a CHOIR hyperedge (`knowledge_graph_spec.md` §4.2). "The grammatical analysis is not translated away — it *becomes* the storage structure." A reader asking why the Moon is the reference frame and not the subject gets the answer "because it is in the ablative, which marks *apādāna*," straight out of the trace. The ablative/genitive syncretism of §6.1 is accordingly "not a pedantic worry: reading *candrāt* as a genitive would turn a reference frame into a possessor and change the rule."

### S7 — *Anuvṛtti*: "the stage that is usually missing"

*Anuvṛtti* is the carrying-forward of terms from a preceding verse or sūtra into subsequent ones — systematic in Pāṇini and common in śāstric verse generally. "The consequence is severe: a śloka is frequently not self-contained." Subject, scope condition, or context may be stated once at the head of a section and silently inherited, so extracting verses independently produces rules with missing conditions — "rules that are *over-general*, and therefore fire when they should not" (§7).

The document identifies this as a **scope inheritance problem, structurally identical to lexical scoping in programming languages**; the compiler analogy in `shloka_compiler.md` §5 treats an unresolved elided argument as a *free variable* and its resolution as *name binding* against an enclosing scope. Five requirements are recorded: section structure (chapter, topical division, *adhikaraṇa*) must be captured at ingest, "not discarded as formatting. It *is* the scope chain"; elided arguments must be detected, a predicate lacking a required kāraka role signalling inheritance; resolution walks outward through enclosing scopes to the nearest binding; **unresolved elisions are errors, not defaults**, and a rule with an unbound free variable is marked incomplete and does not enter the executable corpus; and every inheritance is recorded in provenance.

Mīmāṃsā's *prakaraṇa* (contextual setting) is named as the traditional name for the relevant scope level, and its position in the interpretive priority ordering (`vedic_reasoning_methodology.md` §5.3) determines how much weight an inherited condition carries relative to an explicit one — "inherited scope is *weaker* than direct statement." That ordering transfers directly into extraction confidence.

### S8 — Semantic frame construction

S8 maps the kāraka-labelled parse onto domain-typed predicates and "is the strongest disambiguator in the pipeline because most readings that survive S2–S7 are semantically absurd" (§8). Three operations: lexical sense resolution against the domain ontology (*guru* → the graha Jupiter or a teacher; *rāhu* → the node or the mythological figure), resolved by the ontology's namespace separation (`reasoning_ontology.md` §7.1) and scored by co-occurrence with other resolved terms in the verse; predicate typing, where `saṃsthita` (situated) + *adhikaraṇa* + *apādāna* yields a `PositionalRelation` with a reference frame; and modality detection, where the optative (*vidhi-liṅ*) marks the injunctive and drives the *vidhi* / *arthavāda* extraction gate from `vedic_reasoning_methodology.md` §4.3.

Backward pruning fires at S8: a segmentation yielding no typeable predicate is demoted, and if a lower-ranked S2 alternative yields a clean frame it is promoted and the promotion recorded. "This is the mechanism that makes the lattice worth carrying."

### Ambiguity taxonomy

The document tabulates each ambiguity against the stage that introduces it, the stage that resolves it, and the residual risk (§9):

| Ambiguity | Stage introduced | Resolved by | Residual risk |
|---|---|---|---|
| Segmentation | S2 | S3 morphology + S8 semantics | Two readings both coherent → scholar |
| Vowel length | S0/S2 | S1 metre | Low |
| Case syncretism | S3 | S5 parse + S6 role fit | **Ablative/genitive → wrong frame** |
| Compound boundary | S4 | S8 semantics | Medium |
| Compound type | S4 | Head-fit + semantics | ***bahuvrīhi* → wrong referent** |
| Lexical sense | S8 | Domain co-occurrence | Medium; deferred senses stay open |
| Elided argument | S7 | Scope walk | **Unresolved → rule rejected** |
| Attachment | S5 | Kāraka fit | Medium |
| Metrical padding | S1 | Filler-particle lexicon | Low |
| Referential scope | S7 | Section structure | High for verse-only sources |

The three bolded rows are identified as "the failure modes that change *what the rule says* rather than degrading quality," and they receive mandatory human review in the extraction protocol (`rule_extraction_framework.md` §5).

### Resources: what exists, and two gaps the project must fill itself

The document holds that the pipeline "should consume" the existing digital Sanskrit ecosystem "rather than rebuild it," and attaches an explicit caveat: "**specific capabilities, licences and current maintenance status must be verified before any dependency is taken**" (§10). Categories listed are morphological analysers/readers performing joint segmentation and morphological analysis (the Sanskrit Heritage platform named as best-known) for S2–S3; lemmatised and morphologically annotated corpora (the Digital Corpus of Sanskrit named as principal) for training data and lexicon; dependency treebanks including kāraka-annotated material from Indian NLP groups for S5–S6; digitised classical dictionaries (Monier-Williams and others) for S3 and S8; and published neural work on sandhi splitting, compound analysis and dependency parsing as S2, S4, S5 rerankers.

Two gaps are stated as the project's own to fill. First, **a Jyotiṣa technical lexicon** — general Sanskrit resources "do not reliably cover graha/rāśi/bhāva/yoga terminology as *technical* terms with fixed reference"; it is prerequisite to S2 (§5.3) and named "the highest-value early artefact." Second, **a domain-annotated gold set**, "needed to evaluate the pipeline at all," proposed as 100–200 verses, dual-annotated, covering the §9 ambiguity taxonomy.

### Evaluation, and what is not yet measured

Evaluation is specified per stage "because end-to-end accuracy hides where the loss occurs" (§11): metre identification accuracy at S1 ("should be near-perfect"); split accuracy @1/@5/@20 at S2, where "@k matters more than @1 given the lattice design"; per-token morphological accuracy at S3; compound type and boundary accuracy at S4, with *bahuvrīhi* reported separately; labelled attachment score at S5; kāraka labelling F1 at S6, with *apādāna* and *adhikaraṇa* reported separately; elision detection recall and resolution precision at S7; frame accuracy against gold at S8; and rule-level exact match plus scholar agreement end-to-end, "the number that counts."

Two statements bear on the standing of the design itself. **Oracle analysis is called mandatory** — measuring end-to-end accuracy given a perfect S2, then a perfect S5, and so on — because "it is the only way to know whether the lattice design is earning its cost." And **the metric that matters most is S7 recall**, "because its failure mode is silent. A missed elision yields a well-formed, confident, *wrong-scope* rule — the most dangerous artefact this pipeline can produce."

No measured results are reported anywhere in the source. The gold set required to evaluate the pipeline does not yet exist (§10, §12 item 1), so the pipeline's accuracy at every stage, and whether the lattice architecture earns its cost, are unmeasured.

## Architectural Implications

- **The CHOIR HIR must be ambiguity-preserving.** The pipeline emits into "CHOIR HIR (ambiguity-preserving IR — see 013 §3)" (§2). A single-reading IR would discard the lattice the design depends on.

- **Kāraka roles become the storage structure.** The mapping of kāraka roles onto role-labelled participants of a CHOIR hyperedge (`knowledge_graph_spec.md` §4.2) is stated as the pipeline's load-bearing insight (§6.4). Ablative → reference frame and locative → occupancy are the two mappings the source says carry the Jyotiṣa corpus, and the ablative case is the construction carrying requirement R10 from `vedic_reasoning_methodology.md` §7.

- **Explainability is a by-product of the grammar, not an added layer.** Because the analysis is not translated away, the justification "because it is in the ablative, which marks *apādāna*" comes "straight out of the trace" (§6.4).

- **Provenance and confidence obligations.** Contested editorial readings must surface in a rule's confidence (`confidence_framework.md` §3.1); every resolution is a recorded object feeding extraction confidence (`rule_extraction_framework.md` §6); every *anuvṛtti* inheritance is recorded in provenance; and inherited scope is weighted below direct statement per the Mīmāṃsā interpretive priority ordering (`vedic_reasoning_methodology.md` §5.3).

- **Ingest must preserve document structure.** Section structure "*is* the scope chain" and must be captured at ingest rather than discarded as formatting (§7).

- **A gate on the executable corpus.** Rules with unbound free variables are marked incomplete and do not enter the executable corpus (§7, requirement 4). Unresolved elisions are errors, not defaults.

- **Mandatory human review for three failure modes.** Ablative/genitive syncretism, *bahuvrīhi* misclassification, and unresolved elision change what a rule says and are routed to human review under `rule_extraction_framework.md` §5 (§9).

- **A prerequisite artefact ahead of pipeline work.** The Jyotiṣa technical lexicon is prerequisite to S2 and is named the highest-value early artefact (§10).

- **The compiler framing is shared, not incidental.** The scope-resolution treatment of *anuvṛtti* as free variables and name binding is the same framing as `shloka_compiler.md` §5 (§7).

## Open Questions

The source records five open questions (§12), plus unresolved items elsewhere in the text:

1. **How much can be automated at acceptable fidelity?** Plausibly S0–S3 largely, S4–S6 with review, S7–S8 with substantial review — "Unknown until the gold set exists" (§12 item 1).
2. **Should commentarial *anvaya* be used as training data?** It is abundant and high-quality, "but commentators disagree, and a commentary's *anvaya* embeds its interpretation. Using it as gold imports one school's reading" (§12 item 2).
3. **Translation-first as a fallback path.** Extracting from a translation is possible for texts with no reliable digital Sanskrit but "loses the grammatical justification chain." Whether such rules are admitted at reduced confidence or excluded "is unresolved and affects corpus coverage significantly" (§12 item 3).
4. **Variant readings as parallel branches** (§3) "could multiply the lattice combinatorially where an edition records many variants. A pruning policy is needed" (§12 item 4).
5. **Does the reverse-pruning architecture terminate?** "S8 invalidating S2 and triggering re-analysis needs a cycle bound and a proof that it converges" (§12 item 5). No such bound or proof is given in the source.

Further items the source records as unresolved or unbuilt:

- The **Jyotiṣa technical lexicon** and the **domain-annotated gold set** do not exist and must be built by the project (§10). The gold set is a precondition for evaluating the pipeline at all.
- **No stage of the pipeline is reported as measured.** The source calls oracle analysis mandatory and states that "it is the only way to know whether the lattice design is earning its cost" (§11). It reports no results from that analysis, or from any per-stage metric.
- **Third-party resource dependencies are unverified**: "specific capabilities, licences and current maintenance status must be verified before any dependency is taken" (§10). Named systems are cited by reputation, not by evaluation.
- **Residual ambiguity that no stage resolves**: where two segmentations are both coherent, resolution falls to a scholar; deferred lexical senses "stay open"; referential scope carries "High" residual risk for verse-only sources (§9).
- The document's own status is **"Draft for review"**. `choir/research/README.md` records that all 18 research deliverables are drafted, none accepted, and that "Every document is a hypothesis, per `MANIFESTO.md`" — MANIFESTO.md's own formulation being "Treat every computational object as a hypothesis rather than an established truth". Nothing in this document has been accepted as specification.

## Related Documents

- [YK-R-004 — Vedic Reasoning Methodology](YK-R-004-vedic-reasoning-methodology.md) — the source's stated dependency; supplies requirement R10 (§7), the *vidhi* / *arthavāda* extraction gate (§4.3), and the interpretive priority ordering including *prakaraṇa* (§5.3).
- [YK-R-006 — Shloka Compiler](YK-R-006-shloka-compiler.md) — fed by this document; §5 supplies the free-variable / name-binding treatment of *anuvṛtti*.
- [YK-R-007 — Rule Extraction Framework](YK-R-007-rule-extraction-framework.md) — fed by this document; §6 consumes recorded resolutions as extraction confidence, §5 defines the mandatory human review protocol.
- [YK-R-008 — Canonical Shloka Analysis (Benchmark)](YK-R-008-canonical-shloka-analysis-benchmark.md) — fed by this document.
- [YK-R-003 — Knowledge Graph Specification](YK-R-003-knowledge-graph-specification.md) — §4.2 defines the role-labelled hyperedge participants onto which kāraka roles map.
- [YK-R-002 — Reasoning Ontology](YK-R-002-reasoning-ontology.md) — §7.1 supplies the namespace separation used for lexical sense resolution at S8.
- [YK-R-011 — Confidence Framework](YK-R-011-confidence-framework.md) — §3.1 governs how contested editorial readings surface in confidence.
- [YK-R-013 — CHOIR Intermediate Representation](YK-R-013-choir-intermediate-representation.md) — §3 defines the ambiguity-preserving IR that is this pipeline's output.
