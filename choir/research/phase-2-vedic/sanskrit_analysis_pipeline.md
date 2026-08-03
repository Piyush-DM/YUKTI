# 005 — Sanskrit Analysis Pipeline

**Status:** Draft for review
**Phase:** 2 — Vedic Reasoning Research
**Depends on:** `vedic_reasoning_methodology.md`
**Feeds:** `shloka_compiler.md`, `rule_extraction_framework.md`, `canonical_shloka_analysis.md`

---

## 1. The governing design principle

Sanskrit śāstric verse is ambiguous at every level: the same character string admits
multiple word segmentations, the same word form admits multiple morphological analyses, the
same compound admits multiple internal structures, and the same sentence admits multiple
dependency parses. Verse makes this worse — metre reorders constituents and permits
elision.

The instinctive engineering response — resolve each ambiguity as early as possible and pass
one answer forward — is wrong here, and wrong in a way that is expensive to undo.

> **Principle: ambiguity-preserving until evidence is available.**
>
> Each stage produces a *lattice* of ranked alternatives, not a single output. Ambiguity is
> resolved at the latest stage that has evidence bearing on it, and every resolution is
> recorded with its justification.

The reason is structural, not stylistic. Segmentation ambiguity is frequently resolvable
only by semantics ("does this reading yield a coherent astrological rule?"), and semantics
is four stages downstream. A pipeline that commits at stage 2 cannot use stage 6's evidence.

Three consequences follow:

1. **Every stage is lattice-in, lattice-out**, with a pruning budget rather than a
   single-best decision.
2. **Every resolution is a recorded object** — which alternative, on what grounds, by whom
   or by what model — feeding extraction confidence
   (`rule_extraction_framework.md` §6).
3. **Later stages may reject earlier choices**, reactivating a pruned alternative. The
   pipeline is a constraint solver more than a conveyor belt.

---

## 2. Pipeline overview

```
  Source text (manuscript / edition / digital corpus)
        │
   ┌────▼─────────────────────────────────────────────┐
   │ S0  Normalisation      script → SLP1/IAST         │  deterministic
   ├──────────────────────────────────────────────────┤
   │ S1  Metrical analysis  identify chandas, pādas    │  constrains S2
   ├──────────────────────────────────────────────────┤
   │ S2  Sandhi splitting   → segmentation lattice     │  HIGH ambiguity
   ├──────────────────────────────────────────────────┤
   │ S3  Morphology         → analysis lattice         │  prunes S2
   ├──────────────────────────────────────────────────┤
   │ S4  Compound (samāsa)  → structure + relation     │  HIGH ambiguity
   ├──────────────────────────────────────────────────┤
   │ S5  Anvaya / dependency parse                     │  prunes S2–S4
   ├──────────────────────────────────────────────────┤
   │ S6  Kāraka labelling   → semantic roles           │  prunes S5
   ├──────────────────────────────────────────────────┤
   │ S7  Anuvṛtti resolution (cross-verse inheritance) │  CRITICAL
   ├──────────────────────────────────────────────────┤
   │ S8  Semantic frame     → domain-typed predicates  │  prunes everything
   └────┬─────────────────────────────────────────────┘
        ▼
   CHOIR HIR  (ambiguity-preserving IR — see 013 §3)
```

Note the reverse arrows: pruning flows *backward*. S8 semantic plausibility is the
strongest disambiguator available and must be able to invalidate an S2 segmentation.

---

## 3. S0 — Normalisation

Deterministic and unglamorous, but it is where provenance is established.

- **Script normalisation.** Devanāgarī, IAST, ITRANS, Harvard-Kyoto and other encodings all
  occur in digital sources. Internal representation is **SLP1** (one byte per phoneme,
  which makes sandhi rules expressible as simple string operations); **IAST** is the display
  and identifier form.
- **Unicode normalisation** (NFC), and handling of the *anusvāra*/*candrabindu* and
  *avagraha* variants, which differ between editions.
- **Edition capture.** Text, edition, editor, page/verse locus, and variant readings from
  the apparatus criticus where available.

**Variant readings are not noise.** Where an edition records variants, all are carried
forward as parallel branches with edition-attributed provenance. A rule whose meaning
depends on a contested reading must show that in its confidence
(`confidence_framework.md` §3.1).

---

## 4. S1 — Metrical analysis (and why it comes first)

Identifying the metre before segmenting is a deliberate ordering choice, and it pays for
itself.

Classical verse metres are defined by syllable count and light/heavy (*laghu*/*guru*)
patterns per quarter-verse (*pāda*). *Anuṣṭubh*, the workhorse śloka metre, is 4 pādas of 8
syllables. Longer metres (*upajāti*, *vasantatilakā*, *śārdūlavikrīḍita*, …) have fixed
syllable patterns.

**Why this constrains segmentation:**

1. **Pāda boundaries are usually word boundaries.** Sandhi across a pāda boundary is
   restricted, so metre supplies high-confidence split points for free.
2. **Syllable count is a hard checksum.** A segmentation implying the wrong syllable count
   for the identified metre is *invalid*, not merely unlikely. This prunes the S2 lattice
   substantially before any lexical work.
3. **Light/heavy patterns disambiguate vowel length**, which in turn disambiguates case
   endings — a long final vowel and a short one can be different cases.

**Caveat.** Metrical requirements also *cause* distortions: word order is rearranged for
metre, particles are inserted as padding (*pādapūraṇa*), and forms are occasionally
irregular to fit. So metre helps segmentation while *hurting* parsing — S5 must not assume
prose word order. This trade is worth making because segmentation errors are more expensive
than parse errors: a bad split produces nonsense words, whereas a bad parse produces a
recoverable wrong reading.

---

## 5. S2 — Sandhi splitting

The hardest stage, and the one where most pipelines fail.

### 5.1 The problem

*Sandhi* is obligatory euphonic combination at morpheme and word boundaries. Written
Sanskrit runs words together with their boundaries phonologically transformed. Splitting is
the inverse, and it is **massively non-deterministic**: a single surface string may admit
dozens of valid splits, most of them lexically real.

Compounding the difficulty: the operation is lossy. Several distinct underlying sequences
map to the same surface form, so the inverse is a genuine one-to-many relation, not a hard
parse.

### 5.2 Approaches

| Approach | Mechanism | Strengths | Weaknesses |
|---|---|---|---|
| **Rule-based / FST** | Pāṇinian sandhi rules as finite-state transducers | Complete, explainable, high recall | Massive over-generation; no ranking |
| **Lexicon-driven lattice** | Generate splits, keep those whose segments are attested forms; shortest-path or weighted search | Prunes hard; well understood | Fails on unattested proper nouns and technical terms |
| **Statistical / neural** | Seq2seq or tagging models trained on aligned corpora | Best single-best accuracy reported in the literature | Opaque; needs training data; degrades on domain-specific vocabulary |

### 5.3 Recommended architecture

**Generate broadly, rank statistically, validate morphologically, prune late.**

```
metre constraints (S1)
        │
        ▼
   FST over-generation  ──▶  lexicon filter  ──▶  neural reranking  ──▶  n-best lattice
                                                                             │
                                       morphological validity (S3) ◀─────────┘
                                       semantic plausibility (S8) ◀── prune
```

Key decisions:

- **Keep n-best, not 1-best.** The correct split for a technical śāstric line is frequently
  not the highest-scoring one under a general-domain model, because Jyotiṣa vocabulary is
  specialised.
- **Domain lexicon is mandatory.** Graha names, rāśi names, yoga names, technical terms.
  Without it, `gajakesarī` may be split into constituents and the *name of the yoga* — which
  is the rule's conclusion — vanishes.
- **Record the alternatives that were rejected.** They are needed if a scholar contests the
  reading, and they feed extraction confidence.

### 5.4 Failure signature

A wrong split does not usually produce an obvious error; it produces a *different valid
sentence*. This is why S2 errors must be caught downstream by semantic implausibility
rather than by local validity checks, and why the lattice must survive that far.

---

## 6. S3–S6 — Morphology, compounds, parse, roles

### 6.1 S3 — Morphological analysis

Sanskrit is richly inflected: nominals decline for 8 cases × 3 numbers × 3 genders; verbs
inflect for person, number, tense/mood (*lakāra*), voice and derivational class.

The analysis is **many-to-many**: one surface form maps to multiple (stem, features)
analyses. *Guruḥ* is unambiguously nominative singular masculine; many forms are not — the
genitive singular and ablative singular of *a*-stems are homographs, for example, and that
particular syncretism matters enormously here (see §6.4).

Output is a lattice of `(stem, POS, features)` tuples with scores, feeding back to prune S2.

### 6.2 S4 — Compound (*samāsa*) analysis

Compounds are pervasive in śāstra and carry much of the conditional content.

| Type | Structure | Head | Example pattern |
|---|---|---|---|
| *tatpuruṣa* | Determinative; first member in a case relation to second | Second | "king-of-mountains" |
| *karmadhāraya* | Descriptive; both refer to the same thing | Second | "blue-lotus" |
| *dvigu* | Numerical | Second | "three-worlds" |
| *bahuvrīhi* | Exocentric / possessive | **Outside** | "one whose X is Y" |
| *dvandva* | Copulative; coordination | Both | "X-and-Y" |
| *avyayībhāva* | Adverbial | First (indeclinable) | "according-to-ability" |

**The *bahuvrīhi* hazard.** Its referent is *not* any constituent — the compound denotes
something possessing the described property. Misclassifying a *bahuvrīhi* as a *tatpuruṣa*
does not produce a slightly-off reading; it produces a reading about the wrong entity
entirely. In a rule corpus this silently changes what the rule is about.

Analysis requires three decisions per compound: **constituency** (where the boundaries are,
recursively), **type**, and **head**. All three are ambiguous; all three feed the lattice.

### 6.3 S5 — *Anvaya* and dependency parsing

*Anvaya* is the traditional commentarial operation of reordering verse into prose order —
and it is exactly a dependency parse presented as a word sequence. Commentaries that supply
*anvaya* are therefore **gold-standard parse annotations**, which is a significant and
under-exploited resource: the tradition has been publishing parse trees for centuries.

Sanskrit's relatively free word order means dependency parsing (not constituency parsing)
is the right formalism; morphology carries the information that word order carries in
English. Verse reordering makes surface-order heuristics actively misleading.

### 6.4 S6 — *Kāraka* labelling

The payoff stage. Pāṇini's *kāraka* system assigns semantic roles to participants in an
action:

| *Kāraka* | Role | Typical case | CHOIR mapping |
|---|---|---|---|
| *kartṛ* | Agent | Nominative | Subject / situated entity |
| *karma* | Patient / object | Accusative | Affected entity |
| *karaṇa* | Instrument | Instrumental | Means / mechanism |
| *sampradāna* | Recipient | Dative | Beneficiary |
| *apādāna* | Source / point of departure | **Ablative** | **Reference frame** |
| *adhikaraṇa* | Locus | **Locative** | **Location / containing region** |

**Kāraka is not case.** The mapping is many-to-many: the same role surfaces in different
cases depending on voice and construction, and the same case realises different roles. This
is why S6 is a distinct stage and not a lookup on S3's output.

**Two mappings do the heavy lifting in Jyotiṣa:**

- ***adhikaraṇa* (locative) → occupancy.** "*meṣe*" = "in Aries" is a locus relation. This
  is the most common single construction in the corpus.
- ***apādāna* (ablative) → reference frame.** "*candrāt*" = "from the Moon" specifies the
  point of reckoning. This is the construction that carries the parameter identified as
  requirement R10 in `vedic_reasoning_methodology.md` §7.

**This is the load-bearing insight of the whole pipeline:** kāraka roles map directly onto
the role-labelled participants of a CHOIR hyperedge (`knowledge_graph_spec.md` §4.2). The
grammatical analysis is not translated away — it *becomes* the storage structure. A reader
asking "why is the Moon the reference frame and not the subject?" gets the answer
"because it is in the ablative, which marks *apādāna*," straight out of the trace.

The ablative/genitive syncretism noted in §6.1 is therefore not a pedantic worry: reading
*candrāt* as a genitive would turn a reference frame into a possessor and change the rule.

---

## 7. S7 — *Anuvṛtti*: the stage that is usually missing

***Anuvṛtti*** is the carrying-forward of terms from a preceding verse or sūtra into
subsequent ones. It is systematic in Pāṇini and common in śāstric verse generally.

**The consequence is severe: a śloka is frequently not self-contained.** Its subject, its
scope condition, or its context may be stated once at the head of a section and silently
inherited by everything that follows. Extracting verses independently produces rules with
missing conditions — rules that are *over-general*, and therefore fire when they should not.

This is a **scope inheritance problem**, structurally identical to lexical scoping in
programming languages. The compiler analogy in `shloka_compiler.md` §5 treats it exactly
that way: an unresolved elided argument is a *free variable*, and resolving it is *name
binding* against an enclosing scope.

**Requirements:**

1. Section structure (chapter, topical division, *adhikaraṇa*) must be captured at ingest,
   not discarded as formatting. It *is* the scope chain.
2. Elided arguments must be detected — a predicate lacking a required kāraka role signals
   inheritance.
3. Resolution walks outward through enclosing scopes to the nearest binding.
4. Unresolved elisions are **errors, not defaults**. A rule with an unbound free variable is
   marked incomplete and does not enter the executable corpus.
5. Every inheritance is recorded in provenance: this rule's subject came from verse *n*.

Mīmāṃsā's *prakaraṇa* (contextual setting) is the traditional name for the relevant scope
level, and its position in the interpretive priority ordering
(`vedic_reasoning_methodology.md` §5.3) tells us how much weight an inherited condition
carries relative to an explicit one — inherited scope is *weaker* than direct statement.
That ordering transfers directly into extraction confidence.

---

## 8. S8 — Semantic frame construction

The final stage maps the kāraka-labelled parse onto domain-typed predicates, and is the
strongest disambiguator in the pipeline because most readings that survive S2–S7 are
semantically absurd.

Three operations:

1. **Lexical sense resolution against the domain ontology.** *Guru* → the graha Jupiter or a
   teacher; *rāhu* → the node or the mythological figure. Resolved by the ontology's
   namespace separation (`reasoning_ontology.md` §7.1), scored by co-occurrence with other
   resolved terms in the verse.
2. **Predicate typing.** `saṃsthita` (situated) + `adhikaraṇa` + `apādāna` → a
   `PositionalRelation` with a reference frame.
3. **Modality detection.** Optative (*vidhi-liṅ*) → injunctive; this drives the *vidhi* /
   *arthavāda* extraction gate from `vedic_reasoning_methodology.md` §4.3.

**Backward pruning fires here.** A segmentation that yields no typeable predicate is
demoted; if a lower-ranked S2 alternative yields a clean frame, it is promoted and the
promotion is recorded. This is the mechanism that makes the lattice worth carrying.

---

## 9. Ambiguity taxonomy and where each is resolved

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

The three bolded rows are the failure modes that change *what the rule says* rather than
degrading quality. They receive mandatory human review in the extraction protocol
(`rule_extraction_framework.md` §5).

---

## 10. Resources and their status

Digital Sanskrit has a real ecosystem; the pipeline should consume it rather than rebuild
it. Categories, with the caveat that **specific capabilities, licences and current
maintenance status must be verified before any dependency is taken**:

| Category | What exists | Use |
|---|---|---|
| Morphological analysers / readers | Rule-based analysers and "reader" systems that perform joint segmentation and morphological analysis (the Sanskrit Heritage platform is the best-known) | S2–S3 |
| Digital corpora with annotation | Large lemmatised and morphologically annotated corpora (the Digital Corpus of Sanskrit is the principal one) | Training data, lexicon |
| Treebanks | Dependency treebanks, including kāraka-annotated material from Indian NLP groups | S5–S6 training and evaluation |
| Lexica | Digitised classical dictionaries (Monier-Williams and others), machine-readable | S3, S8 |
| Neural models | Published work on neural sandhi splitting, compound analysis and dependency parsing | S2, S4, S5 rerankers |

**Two gaps the project must fill itself:**

1. **A Jyotiṣa technical lexicon.** General Sanskrit resources do not reliably cover
   graha/rāśi/bhāva/yoga terminology as *technical* terms with fixed reference. This is
   prerequisite to S2 (§5.3) and is the highest-value early artefact.
2. **A domain-annotated gold set.** Needed to evaluate the pipeline at all. Proposed:
   100–200 verses, dual-annotated, covering the ambiguity taxonomy in §9.

---

## 11. Evaluation

Per-stage metrics, because end-to-end accuracy hides where the loss occurs:

| Stage | Metric | Note |
|---|---|---|
| S1 | Metre identification accuracy | Should be near-perfect |
| S2 | Split accuracy @1 / @5 / @20 | @k matters more than @1 given the lattice design |
| S3 | Morphological analysis accuracy | Per token |
| S4 | Compound type + boundary accuracy | Report *bahuvrīhi* separately |
| S5 | Labelled attachment score | Standard dependency metric |
| S6 | Kāraka labelling F1 | Report *apādāna* and *adhikaraṇa* separately |
| S7 | Elision detection recall; resolution precision | **Recall matters most — a missed elision is a silent over-general rule** |
| S8 | Frame accuracy vs gold | End of pipeline |
| End-to-end | Rule-level exact match; scholar agreement | The number that counts |

**Oracle analysis is mandatory:** measure end-to-end accuracy given a perfect S2, then a
perfect S5, and so on. This localises where effort pays, and it is the only way to know
whether the lattice design is earning its cost.

**The metric that matters most is S7 recall**, because its failure mode is silent. A missed
elision yields a well-formed, confident, *wrong-scope* rule — the most dangerous artefact
this pipeline can produce.

---

## 12. Open questions

1. **How much can be automated at acceptable fidelity?** Plausibly S0–S3 largely, S4–S6
   with review, S7–S8 with substantial review. Unknown until the gold set exists.
2. **Should commentarial *anvaya* be used as training data?** It is abundant and
   high-quality, but commentators disagree, and a commentary's *anvaya* embeds its
   interpretation. Using it as gold imports one school's reading.
3. **Translation-first as a fallback path.** For texts with no reliable digital Sanskrit,
   extracting from a translation is possible but loses the grammatical justification chain.
   Whether such rules are admitted at reduced confidence, or excluded, is unresolved and
   affects corpus coverage significantly.
4. **Variant readings as parallel branches** (§3) could multiply the lattice
   combinatorially where an edition records many variants. A pruning policy is needed.
5. **Does the reverse-pruning architecture terminate?** S8 invalidating S2 and triggering
   re-analysis needs a cycle bound and a proof that it converges.
