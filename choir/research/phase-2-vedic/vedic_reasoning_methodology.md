# 004 — Vedic Reasoning Methodology

**Status:** Draft for review
**Phase:** 2 — Vedic Reasoning Research
**Depends on:** `computational_primitives.md`, `reasoning_ontology.md`
**Feeds:** `rule_extraction_framework.md`, `conflict_resolution.md`, `explainability_framework.md`

---

## 0. Scope, method, and honest limits

### 0.1 The question

*How do classical Jyotiṣa texts actually reason?* Not: are their conclusions correct. The
object of study is the **inferential machinery** — what counts as a reason, how rules
compose, what defeats what, how conflict is settled.

### 0.2 What CHOIR claims and does not claim

Restating the commitment from `computational_primitives.md` §0.1, because this document is
where it is most likely to be misread:

- **Claimed:** that a given rule is what a given text says; that a conclusion follows from
  that rule under stated semantics; that the derivation is reconstructible.
- **Not claimed:** that the rule is true of the world, or that the predictions it licenses
  are borne out.

Jyotiṣa's predictive claims are not empirically supported, and CHOIR is not evidence for
them. What Jyotiṣa *does* offer — and the reason it is a good source domain for this
research — is one of the most highly developed **defeasible rule corpora** in existence:
thousands of interacting conditional rules with explicit cancellation conditions, strength
gradations, reference-frame parameterisation, contextual scoping and centuries of
commentarial conflict resolution. As a stress test for a reasoning compiler it is harder
than most legal corpora.

The validation target is therefore **textual fidelity**, not predictive accuracy. This is
stated plainly here so that no downstream document has to hedge.

### 0.3 A caution about sources

Two source-critical facts must be carried into every extraction:

- **Textual instability.** *Bṛhat Parāśara Horā Śāstra*, the most-cited Jyotiṣa source, has
  a contested transmission history: it circulates in multiple recensions of differing
  length, and its received form is generally regarded by scholars as considerably later
  than its attributed authorship. Verse numbering differs between editions.
- **Translation drift.** Most working practitioners use translations, and translations
  differ substantially — particularly on quantifiers, conditionals, and the scope of
  exception clauses, which is exactly what a rule compiler depends on.

**Operational consequence:** every extracted rule must record its *edition* and
*translator*, not merely "BPHS ch. X". Citations that cannot be checked against a stated
edition are marked `citation_unverified` and carry reduced extraction confidence. This is
enforced in `rule_extraction_framework.md` §5.

### 0.4 Sanskrit terms

Transliteration is IAST. Technical terms are given in transliteration on first use with a
gloss, then used untranslated, because the English glosses are lossy in precisely the ways
that matter.

---

## 1. Why the classical logical tradition is the right lens

Jyotiṣa did not develop its reasoning apparatus in isolation. It is a *śāstra*, and śāstric
argument inherits a shared toolkit from three neighbouring disciplines:

| Discipline | Contributes | CHOIR relevance |
|---|---|---|
| **Nyāya** | Theory of inference and of evidence-kinds; fallacy taxonomy | Evidence typing; conflict classification |
| **Mīmāṃsā** | Rule interpretation, injunction theory, precedence ordering | Conflict resolution; extraction gating |
| **Vyākaraṇa** (Pāṇinian grammar) | Meta-rules governing rule application | Rule ordering; blocking; exception handling |

This is the central finding of this document: **the tradition supplies its own
conflict-resolution and explanation machinery**, and it is more precisely specified than
what most modern rule engines ship with. CHOIR does not need to invent these; it needs to
formalise them.

---

## 2. Observation and evidence: the *pramāṇa* framework

Classical Indian epistemology types knowledge by its *means of acquisition* (*pramāṇa*).
Schools differ on how many are accepted; the Nyāya set of four and the Mīmāṃsā extension to
six are the relevant ones.

| *Pramāṇa* | Gloss | Modern analogue | CHOIR evidence type |
|---|---|---|---|
| *pratyakṣa* | Perception | Direct observation | `direct` |
| *anumāna* | Inference | Rule-based derivation | `derived` |
| *upamāna* | Comparison / analogy | Case-based, analogical reasoning | `analogical` |
| *śabda* | Reliable testimony | Authority; cited source | `attested` |
| *arthāpatti* | Postulation | Abduction; inference to best explanation | `abductive` |
| *anupalabdhi* | Non-apprehension | **Negation as failure** | `absence` |

Two of these deserve emphasis.

**`anupalabdhi` — reasoning from absence.** The Mīmāṃsā (and Advaita) recognition of
non-apprehension as an independent means of knowledge is a direct precursor of
*negation as failure*: from the non-observation of *X* where *X* would have been observed
had it been present, infer *¬X*. Crucially, the classical formulation includes the
**observability condition** — non-apprehension licenses denial only where apprehension
*would have occurred*. That condition is exactly what modern closed-world reasoning gets
wrong when it is applied naively to incomplete data. CHOIR adopts the qualified form:
absence-evidence is admissible only where the context declares the relevant domain
complete. See `evidence_model.md` §3.4.

**`śabda` — testimony.** Textual authority is a *first-class* means of knowledge in this
tradition, not a fallback. This is what makes the corpus a normative system rather than an
empirical one, and it is what makes source-authority ranking (`conflict_resolution.md` §5)
central rather than peripheral.

### 2.1 *Vyāpti* — the warrant, and its defeater

An inference (*anumāna*) is licensed by *vyāpti*: an invariable concomitance between the
reason (*hetu*) and what is inferred (*sādhya*) — "wherever there is smoke, there is fire."

*Vyāpti* is established by:

- *anvaya* — positive co-presence (where *hetu*, there *sādhya*)
- *vyatireka* — negative co-absence (where no *sādhya*, no *hetu*)

and is threatened by:

- ***upādhi*** — a conditioning factor that vitiates the pervasion: an unstated additional
  condition on which the concomitance actually depends.

***upādhi* is an undercutting defeater.** It does not assert the opposite conclusion; it
shows the inferential link was never warranted in the first place. The correspondence with
Pollock's *undercutting defeater* (`computational_primitives.md` §3.12) is exact, and it is
a striking convergence between two traditions separated by a millennium. CHOIR's exception
typology is therefore not an imposition on the corpus — it is a formalisation of a
distinction the corpus already draws.

### 2.2 *Hetvābhāsa* — a native conflict taxonomy

Nyāya classifies defective reasons. The standard five:

| *Hetvābhāsa* | Defect | CHOIR conflict class |
|---|---|---|
| *savyabhicāra* / *anaikāntika* | Inconclusive — the reason strays; occurs with and without the *sādhya* | Non-discriminating condition |
| *viruddha* | Contradictory — the reason proves the opposite | Rebutting defeat |
| *satpratipakṣa* | Counterbalanced — an equally strong reason for the opposite | **Genuine tie → *vikalpa* or escalation** |
| *asiddha* | Unestablished — a premise fails | Premise defeat |
| *bādhita* | Contradicted — a stronger means of knowledge overrides | Precedence loss (*bādha*) |

This maps almost one-to-one onto the conflict typology derived independently in
`conflict_resolution.md` §3. *satpratipakṣa* is the significant one: the tradition has a
name for **a conflict that is genuinely balanced**, and treats it as a terminal state of
analysis rather than something to be broken arbitrarily. Most rule engines cannot represent
this. CHOIR must (see §5.3).

---

## 3. Analogy and symbolism

### 3.1 The symbol resolution problem

Jyotiṣa's vocabulary is systematically polysemous by design. A single significator maps to
a whole field of referents across domains:

| Sūrya (Sun) indicates | Domain |
|---|---|
| Father, authority, the king | Social / relational |
| Bone, the right eye, vitality | Physical / medical |
| The east | Directional |
| Soul, self | Metaphysical |
| Gold, copper | Substance |

This is not vagueness; it is a **structured mapping**, and the tradition supplies the
structure: *kāraka* (significator) assignments, *bhāva* (house) significations, and
elemental/qualitative correspondences.

**The computational problem is sense selection.** When a rule concludes "Sūrya is
afflicted," the referent is fixed by the **question being asked**, not by the rule. A
medical query selects the physical mapping; a query about paternal relations selects the
social one.

**This is what `Context.purpose` is for** (`computational_primitives.md` §3.10). The
`purpose` dimension of the context is not decorative — it is the disambiguation parameter,
and without it the rule is genuinely under-determined. A system that resolves symbols at
extraction time rather than query time will produce a corpus that answers only one kind of
question.

**Design rule:** symbol → referent mappings are stored as *context-scoped relations*, not
resolved during compilation. The compiler preserves the symbol; the executor resolves it
against the query context and records which mapping it used.

### 3.2 Analogy as inference (*upamāna*)

Analogical transfer appears throughout: a graha in a sign it rules behaves "as a person in
their own home"; a debilitated graha "as one in a foreign land." These are not ornament —
they license inferences about strength and behaviour.

Modelled as an `analogical` inference license (001 §3.13), which is **strongly defeasible**
and must record the correspondence explicitly: source structure, target structure, mapped
relations, and — critically — the relations *not* mapped. An analogy that does not state
its limits cannot be defeated, and an undefeatable inference is not a reasoning step.

---

## 4. Conditional logic and exception handling

### 4.1 *Utsarga* and *apavāda*

The general rule / exception pair is the fundamental structure of śāstric rule systems.

- ***utsarga*** — the general rule
- ***apavāda*** — the exception, which carves out a region from the general rule

The relationship is **not** "the exception contradicts the rule." It is: the exception
*restricts the domain* of the general rule. Where the exception applies, the general rule
was never applicable. This matters computationally: a defeated general rule does not
produce a negated conclusion, it produces *no* conclusion from that source, leaving the
field to other evidence.

This is the *undercutting* pattern again, and it is the tradition's default.

### 4.2 *Bhaṅga* — cancellation

Jyotiṣa has a specific and heavily-developed cancellation apparatus. A configuration that
would ordinarily yield a result is cancelled under stated conditions — the best-known
family being *nīca-bhaṅga* (cancellation of debilitation), where a graha in its sign of
debilitation has that weakness annulled under specified conditions.

**Cancellation is layered, and this is where fidelity gets hard:**

```
base configuration       →  yields result R
  + cancellation cond.   →  R suppressed
    + counter-condition  →  cancellation itself annulled → R restored (sometimes modified)
```

Exceptions to exceptions are *normal*, not edge cases. This is decisive for the design of
`Exception` as a first-class object rather than a boolean field
(`computational_primitives.md` §3.12), and for the well-foundedness requirement on defeater
chains in `conflict_resolution.md` §6.

The commentarial literature disagrees substantially about the precise conditions for
*nīca-bhaṅga*. That disagreement is **interpretive confidence** (011 §3), not extraction
error, and must be recorded as such rather than resolved by picking a favourite.

### 4.3 The *vidhi* apparatus from Mīmāṃsā

Mīmāṃsā developed to interpret Vedic injunctions and is, functionally, a jurisprudence of
textual rules. Its classification of statement types is directly usable as an
**extraction gate**:

| Type | Nature | Extract as a rule? |
|---|---|---|
| *vidhi* | Injunction — enjoins an action or asserts a relation | ✅ Yes |
| *niṣedha* | Prohibition | ✅ Yes, with negative modality |
| *arthavāda* | Commendatory or explanatory passage; praise, blame, narrative | ❌ **No** |
| *nāmadheya* | Naming — assigns a designation | ✅ As a definition, not a rule |
| *mantra* | Liturgical formula | ❌ No |

**The *arthavāda* exclusion is the single most valuable extraction heuristic available.**
A large fraction of śāstric verse is laudatory or illustrative — "one who has this
combination becomes like Indra himself." Naively extracting such lines as rules produces a
corpus full of unfalsifiable superlatives. Mīmāṃsā already solved this classification
problem and supplies criteria for it.

Note the grammatical signal: injunctions characteristically appear in the **optative**
(*vidhi-liṅ*) or use gerundive/necessitative forms. This is a *morphological* feature the
Sanskrit pipeline can detect, making the gate partly automatable
(`sanskrit_analysis_pipeline.md` §7, `canonical_shloka_analysis.md` §4).

---

## 5. Rule composition and conflict

### 5.1 How Jyotiṣa rules compose

The corpus composes rules in a consistent pipeline shape:

```
static configuration          positions, dignities, aspects
        ↓
combination detection         yoga rules fire → named results
        ↓
strength modulation           bala computations weight each result
        ↓
cancellation / affliction     bhaṅga and affliction rules defeat or weaken
        ↓
temporal activation           daśā / gochara gate when a result manifests
        ↓
aggregate judgement           surviving indications combined
```

Three observations with direct design consequences:

1. **Detection and strength are separate stages.** A yoga either forms or does not (boolean
   condition), and *separately* has a strength (graded). Collapsing these into one weighted
   score loses the corpus's own distinction, and makes cancellation — which operates on
   formation, not on strength — inexpressible.

2. ***Bala* is an explicit quantitative apparatus.** *Ṣaḍbala* ("six-fold strength") sums
   positional, directional, temporal, motional, natural and aspectual components. That the
   tradition specifies a *multi-component additive strength model with named components* is
   remarkable, and it maps onto CHOIR's confidence decomposition requirement rather well.
   Caveat: the components are ordinal-to-interval at best, and the received computations
   vary between authorities — so the *structure* is adoptable, the *numbers* are not
   authoritative. Cf. the `Measure.scale_type` warning in `reasoning_ontology.md` §3.1.

3. **Temporal activation is a separate gate.** A combination present in a chart is held to
   manifest during particular periods. This is a clean instance of the *valid time* vs
   *decision time* separation (001 §3.17): the configuration is timeless relative to the
   chart; the activation window is not.

### 5.2 Hierarchical reasoning

Judgements are built at multiple levels, and lower levels feed higher ones:

```
graha (planet)  →  bhāva (house)  →  yoga (combination)  →  daśā (period)  →  overall
```

Each level has its own rules, and higher-level rules can override lower-level indications.
This is a **stratified rule system**, and stratification is what makes termination
provable (`reasoning_language.md` §7.3). It is also why `execution_pipeline.md` §4 can
compute derived facts in dependency order rather than needing a general fixpoint over
everything at once.

### 5.3 Conflict resolution: what the tradition supplies

This is where the classical apparatus most exceeds standard rule-engine practice.

**Mīmāṃsā's interpretive priority ordering.** Where sources of meaning conflict, Jaimini's
system ranks them:

> *śruti* (direct statement) > *liṅga* (indicatory power of a word) > *vākya* (syntactic
> connection) > *prakaraṇa* (contextual setting) > *sthāna* (position) > *samākhyā* (name)

A rule grounded in an explicit statement outranks one grounded in contextual placement,
which outranks one grounded in a name. This is a **ready-made precedence lattice for
interpretive conflict**, and it is adopted directly in `conflict_resolution.md` §5.2.

**Pāṇinian meta-rules (*paribhāṣā*).** The *Aṣṭādhyāyī* is a rule system with explicit
rules about rule application. Two are directly reusable:

- ***vipratiṣedhe paraṃ kāryam*** (A. 1.4.2) — where two rules of equal scope conflict, the
  later prevails. This is *lex posterior*, stated as a formal meta-rule roughly two and a
  half millennia before its Latin restatement.
- ***pūrvatrāsiddham*** (A. 8.2.1) — rules in a designated section are treated as
  "not having taken effect" with respect to earlier rules, imposing a **phase ordering** on
  rule application.

Together with *utsarga/apavāda* (*lex specialis*), the tradition supplies specificity,
recency, and phase-ordering meta-rules — the three axes any serious rule-conflict system
needs.

**Resolution outcomes.** Mīmāṃsā names outcomes that most engines lack:

| Outcome | Meaning | Engine support elsewhere |
|---|---|---|
| *bādha* | Sublation — the stronger rule cancels the weaker | Common |
| *samuccaya* | Conjunction — both apply together | Common |
| ***vikalpa*** | **Optionality — both are admissible; either may be followed** | **Rare** |

***vikalpa* is the important one.** It is a legitimate terminal state in which two rules
conflict, neither defeats the other, and the correct output is *both alternatives with
their support*, not a forced choice. Combined with *satpratipakṣa* (§2.2), the tradition
both recognises balanced conflict and prescribes what to do about it.

CHOIR must therefore be able to **terminate in a disjunction**. A system that always
returns one answer cannot be faithful to this corpus — and, as `domain_independence.md` §4
shows, it cannot be faithful to law or medicine either, where genuine unresolved splits are
routine.

---

## 6. Context dependence

Context is not an afterthought in this corpus; conclusions are systematically parameterised
by it.

| Context dimension | Values | Effect |
|---|---|---|
| *Varga* (divisional chart) | Rāśi (D-1), Navāṃśa (D-9), and others | The same configuration read in a different varga yields different conclusions |
| Reference frame | From Lagna; from Candra; from a graha | **Changes what "the 7th house" denotes** |
| Birth condition | *divā* / *rātri* (day / night) | Gates whole rule families |
| Application | *jātaka* (natal), *praśna* (horary), *muhūrta* (electional) | Different rule corpora entirely |
| School | Parāśara, Jaimini, Tājika, and others | Different and sometimes incompatible systems |
| Query purpose | Medical, relational, vocational | Selects the symbol mapping (§3.1) |

**Reference frame is the most computationally consequential.** Counting "from the Moon"
rather than "from the Ascendant" is a *parameter of the rule*, expressed grammatically by
the ablative case. This is why role-labelled n-ary storage matters
(`knowledge_graph_spec.md` §7): the reference frame is a distinct argument of the
positional relation, and flattening it into a binary edge loses it.

**School incompatibility is not conflict.** Parāśara and Jaimini rules are not competitors
to be adjudicated; they are *different systems*. Mixing them produces incoherence. The
context lattice must keep them separated, and the conflict detector must not report
cross-school differences as contradictions. This is the primary practical use of the
context lattice: **most apparent contradictions are context collisions**
(`conflict_resolution.md` §4).

---

## 7. Summary of computational requirements derived from the corpus

Requirements this analysis imposes on the rest of the system:

| # | Requirement | Source in the tradition | Specified in |
|---|---|---|---|
| R1 | Six evidence types, including absence-evidence with an observability condition | *pramāṇa*, *anupalabdhi* | `evidence_model.md` §3 |
| R2 | Undercutting defeat distinct from rebutting defeat | *upādhi*, *apavāda* | `computational_primitives.md` §3.12 |
| R3 | Exceptions to exceptions, arbitrarily nested, well-founded | *bhaṅga* layering | `conflict_resolution.md` §6 |
| R4 | Precedence by specificity, recency, and phase | *utsarga/apavāda*, A. 1.4.2, A. 8.2.1 | `conflict_resolution.md` §5 |
| R5 | Interpretive precedence ordering for textual conflict | Mīmāṃsā six-fold ordering | `conflict_resolution.md` §5.2 |
| R6 | **Termination in a disjunction** (`vikalpa`) as a first-class outcome | *vikalpa*, *satpratipakṣa* | `conflict_resolution.md` §7 |
| R7 | Extraction gate excluding non-injunctive passages | *arthavāda* / *vidhi* distinction | `rule_extraction_framework.md` §4 |
| R8 | Symbol resolution deferred to query context | *kāraka* polysemy | `execution_pipeline.md` §3 |
| R9 | Separation of formation (boolean) from strength (graded) | yoga vs *bala* | `confidence_framework.md` §4 |
| R10 | Reference frame as an explicit rule parameter | ablative reckoning | `knowledge_graph_spec.md` §7 |
| R11 | Explanation structured as claim/reason/rule/application/conclusion | *pañcāvayava* | `explainability_framework.md` §3 |
| R12 | Conflict taxonomy including "genuinely balanced" | *hetvābhāsa* | `conflict_resolution.md` §3 |
| R13 | Cross-school difference is not contradiction | school contexts | `conflict_resolution.md` §4 |

R11 refers to the Nyāya five-membered demonstration (*pañcāvayava*): *pratijñā* (thesis),
*hetu* (reason), *udāharaṇa* (general rule with example), *upanaya* (application to the
case), *nigamana* (conclusion). It is a fully-formed explanation schema and is adopted as
CHOIR's explanation template — see `explainability_framework.md` §3.

---

## 8. Open questions

1. **How much *bala* arithmetic is authoritative?** The component *structure* is
   well-attested; the numeric weights vary by authority and edition. Whether CHOIR should
   ship any default weights, or force the user to select an authority, is unresolved.
2. **Is *arthāpatti* distinct from abduction in a way that matters computationally?** The
   classical formulation is narrower than modern inference-to-best-explanation. Treating
   them as identical may be a fidelity loss.
3. **Should school contexts be siblings or incomparable?** If Parāśara and Jaimini are
   incomparable in the lattice, no cross-school conflict can ever be adjudicated — probably
   correct, but it forecloses synthesis that practitioners do perform.
4. **Where does *anupalabdhi*'s observability condition come from computationally?** It
   requires declaring a domain complete. Who declares it, and on what authority, is
   unresolved and matters for R1.
5. **The extent of the *arthavāda* boundary.** Some passages are simultaneously
   commendatory and injunctive. Mīmāṃsā has extensive machinery for this; how much of it
   CHOIR needs is unknown until extraction is attempted at scale.
