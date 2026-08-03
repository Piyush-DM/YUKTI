# 008 — Canonical Shloka Analysis (Benchmark)

**Status:** Draft for review — **this document is the reference benchmark**
**Phase:** 2 — Vedic Reasoning Research
**Depends on:** 004–007
**Feeds:** every downstream document; the acceptance test for the compiler

---

## 1. Purpose and selection

One shloka is carried end to end — original Sanskrit → word-by-word → grammar → meaning →
reasoning → rule graph → computational rule → execution — to serve as the project's
benchmark. Any change to the pipeline is validated against this worked example.

### 1.1 Why this verse

The chosen verse states the formation of **Gajakesarī yoga**. It was selected because it
exercises, in sixteen syllables, six of the hardest problems identified in Phase 2:

| Feature present | Exercises | Documented in |
|---|---|---|
| **Locative absolute** (*sati saptamī*) | Conditional force with **no conditional particle** | 006 §6.1, 007 §3 |
| **Ablative** *candrāt* | Reference frame as a rule parameter (R10) | 004 §7, 005 §6.4 |
| ***nāmadheya*** naming construction | Named result vs asserted outcome | 004 §4.3 |
| **Two compounds of different types** | *tatpuruṣa* vs derivative/possessive | 005 §6.2 |
| **Elided subject** (*yogaḥ*) | *Anuvṛtti* / scope binding | 005 §7 |
| **Polysemous technical term** *jīva* | Domain lexicon dependency | 005 §8 |
| Well-known **cancellation** conditions | Undercutting defeat; exceptions in other verses | 004 §4.2 |

A verse containing an explicit *cet* ("if") would have been easier and would have tested
nothing. This one has conditional force carried entirely by a case construction, which is
the failure mode most likely to defeat a keyword-based extractor.

### 1.2 Citation status — read this first

> **`attestation: unverified` · diagnostic `E-ATTEST`**
>
> The verse below is given in a form widely circulated in Jyotiṣa literature and commonly
> associated with the Gajakesarī yoga. **It has not been checked against a critical
> edition, and no chapter/verse locus is asserted here.** Formulations of this yoga vary
> between texts and recensions.

Under `rule_extraction_framework.md` §2.1, `source.edition` is mandatory and this rule
therefore **cannot enter the authoritative corpus** in its present state. It is admitted
here as a *methodological* benchmark: the analysis chain is the deliverable, and the rule
carries its own diagnostic.

This is deliberate. The framework's first requirement is that unverifiable citations be
visible rather than laundered, and the benchmark should demonstrate the framework rather
than quietly exempt itself from it.

**Resolution task:** locate the verse in a stated edition, record editor and locus, collect
variants, then re-run this analysis. The expected outcome is that only §2 and §12 change.

---

## 2. Layer 0 — Original Sanskrit

**Devanāgarī**

> चन्द्रात् केन्द्रगते जीवे गजकेसरिसंज्ञकः ।

**IAST**

> *candrāt kendragate jīve gajakesari-saṃjñakaḥ*

**SLP1 (internal form)**

> `candrAt kendragate jIve gajakesarisaMjYakaH`

### 2.1 Metrical analysis (S1)

| Pāda | Text | Syllables |
|---|---|---|
| a | *candrāt kendragate jīve* | 8 |
| b | *gajakesari-saṃjñakaḥ* | 8 |

8 + 8 is consistent with **anuṣṭubh**, the standard śloka metre, of which this is a
half-verse (two pādas).

> **Diagnostic `W-VARIANT` (review item):** the fine-grained *laghu/guru* pattern check for
> pāda *a* does not cleanly match the *pathyā* form of anuṣṭubh. This may indicate a
> permitted *vipulā* variant, a transmission variant, or a paraphrase rather than an
> attested verse. **Flagged for review alongside the citation task.**

Recording this rather than suppressing it is the point. The metrical checksum
(`sanskrit_analysis_pipeline.md` §4) did its job: it detected something worth a scholar's
attention. A pipeline that reported "metre OK" here would be less useful.

The pāda boundary after *jīve* is nonetheless a high-confidence segmentation anchor, and it
is used as such in §3.

---

## 3. Layer 1 — Word-by-word

Sandhi splitting (S2) is unusually clean here: the pāda boundary supplies one split, and
*candrāt kendragate* is written separately in most transmissions.

| # | Form | Split | Stem | Analysis |
|---|---|---|---|---|
| 1 | *candrāt* | — | *candra* | m., **ablative sg.** |
| 2 | *kendragate* | *kendra + gate* | *kendra-gata* | m., **locative sg.**, past passive participle head |
| 3 | *jīve* | — | *jīva* | m., **locative sg.** |
| 4 | *gajakesari-saṃjñakaḥ* | *gajakesari + saṃjñaka* | *gajakesari-saṃjñaka* | m., **nominative sg.** |
| — | *(yogaḥ)* | **elided** | *yoga* | m., nominative sg. — supplied by *anuvṛtti* |

### 3.1 Ambiguities recorded at this layer

| ID | Kind | Alternatives | Resolution | Grounds |
|---|---|---|---|---|
| `A1` | Case syncretism | *candrāt* = ablative sg. **or** (for some stems) genitive-class reading | **Ablative** | *a*-stem *candra*: ablative sg. is *candrāt*; genitive sg. is *candrasya*. **Unambiguous here.** |
| `A2` | Lexical sense | *jīva* = "living being, soul" **or** Jupiter (Bṛhaspati) | **Jupiter** | Domain lexicon; co-occurrence with *kendra* and *candra*; the verse is Jyotiṣa |
| `A3` | Compound type | *gajakesari-saṃjñaka* — *tatpuruṣa* or possessive | **Possessive/derivative** | *-ka* suffix on *saṃjñā*; means "having the designation X", referent outside |
| `A4` | Elision | Subject of *saṃjñakaḥ* | ***yogaḥ*** | Masculine nominative singular agreement; *nāmadheya* construction; section context |

**`A1` is the important non-event.** `sanskrit_analysis_pipeline.md` §9 flags
ablative/genitive syncretism as a silent, rule-changing failure mode. Here the *a*-stem
paradigm distinguishes them cleanly, so the reference frame is recovered with high
confidence. In a verse using a stem where they coincide, this row would be a mandatory
review trigger (`rule_extraction_framework.md` §5.3).

**`A2` demonstrates the lexicon dependency.** Without a Jyotiṣa lexicon, *jīve* reads as
"in a living being" and the entire rule dissolves. This is the concrete case behind
`sanskrit_analysis_pipeline.md` §10's finding that a domain lexicon is the highest-value
early artefact.

---

## 4. Layer 2 — Grammar

### 4.1 Compound analysis (S4)

**`kendra-gata`** — *tatpuruṣa* (locative-determinative)
- Constituents: *kendra* (angle: houses 1, 4, 7, 10) + *gata* (past passive participle of
  √*gam*, "gone")
- Head: *gata* (second member)
- Sense: "gone to / situated in a kendra"
- Inflected as locative sg. *kendragate*, agreeing with *jīve*

**`gajakesari-saṃjñaka`** — derivative possessive
- Constituents: *gajakesari* (itself *gaja* "elephant" + *kesarin* "lion") + *saṃjñā*
  "designation" + *-ka*
- Referent: **outside the constituents** — the thing *having* the designation, i.e. the yoga
- Sense: "designated Gajakesarī"

The second compound is the *bahuvrīhi*-class hazard from `sanskrit_analysis_pipeline.md`
§6.2 in live form. Read as a *tatpuruṣa*, it would denote *the designation itself* rather
than *the thing designated*, and the rule's conclusion would become a statement about a
name rather than about a configuration.

### 4.2 Syntactic structure (S5) — the locative absolute

The two locatives *kendragate jīve* form a **locative absolute** (*sati saptamī*): a
participle and its subject both in the locative, functioning as a subordinate clause.

```
                    saṃjñakaḥ  (nom. sg., predicate)
                   /          \
        [yogaḥ]                gajakesari-  (designation)
        (elided subject)
              │
              │ conditioned by
              ▼
        ═══ LOCATIVE ABSOLUTE ═══
             jīve  (loc. sg.)  ── subject of the participle
               │
               └── kendragate  (loc. sg., participle)
                         │
                         └── candrāt  (abl.) ── point of reckoning
```

> **This construction carries conditional force with no conditional particle.**

There is no *cet*, no *yadi*, no *yadā*. Any extraction method that locates conditionals by
keyword finds nothing here and either discards the verse or — worse — extracts it as an
unconditional assertion that Gajakesarī yoga simply exists.

This is the concrete justification for two architectural decisions:

- **Do not compile through translation** (`shloka_compiler.md` §3). English renderings
  supply an "if" that is not in the source; the conditional force must be recovered from
  the *case morphology*, which translation destroys.
- **Dependency parsing is required, not optional** (`sanskrit_analysis_pipeline.md` §6.3).

### 4.3 Kāraka labelling (S6)

| Word | Case | *Kāraka* | Role in the rule |
|---|---|---|---|
| *jīve* | Locative (absolute) | *kartṛ* of the participle | The situated entity — **Jupiter** |
| *kendragate* | Locative (absolute) | *adhikaraṇa* | The locus — **kendra region** |
| *candrāt* | Ablative | ***apādāna*** | **The point of reckoning — the Moon** |
| *(yogaḥ)* | Nominative (elided) | *kartṛ* of the main predicate | The named result |

***apādāna* → reference frame is the load-bearing mapping.** The ablative marks the point
*from which* something is measured or departs. Here it fixes that kendras are counted from
the Moon, not from the Ascendant — which is what makes this yoga distinct from the
ordinary Ascendant-relative reading, and is precisely requirement R10.

When the explanation system is later asked *"why is the Moon the reference frame rather
than the subject?"*, the answer available in the trace is: **"because it is in the ablative,
which marks *apādāna*."** The grammatical justification survives all the way to the user
because kāraka roles become hyperedge participant roles
(`knowledge_graph_spec.md` §7) rather than being translated away.

### 4.4 *Anuvṛtti* resolution (S7)

Two things are inherited from the section, not stated in the verse:

| Inherited | Value | Source | Interpretive weight |
|---|---|---|---|
| Elided subject | *yogaḥ* | Agreement + *nāmadheya* pattern | High |
| Application | *jātaka* (natal) | Section scope (*prakaraṇa*) | **Reduced** — *prakaraṇa* ranks below *śruti* |
| Chart | rāśi (D-1) | Section scope | **Reduced**, same reason |

The reduction applies the Mīmāṃsā interpretive priority ordering
(`vedic_reasoning_methodology.md` §5.3) as a confidence input: a scope condition *inherited*
from context is weaker evidence of meaning than one *directly stated*. This is recorded, not
silently accepted — and it is why the extracted rule's interpretive confidence is not
maximal despite an otherwise clean analysis.

---

## 5. Layer 3 — Meaning

**Literal:** *"Jupiter being situated in an angle from the Moon, [there arises the
combination] designated Gajakesarī."*

**Structured:**

| Element | Content |
|---|---|
| Condition | Jupiter occupies a kendra, reckoned from the Moon |
| Conclusion | A named configuration, *Gajakesarī*, obtains |
| Modality | *indicates* — the verse asserts formation, not an outcome |
| Scope | Natal application; rāśi chart *(inherited)* |
| Reference frame | **Moon** *(stated, ablative)* |
| Strength | **None stated** |

### 5.1 What the verse does *not* say

Three absences, each of which an undisciplined extractor would fill in:

1. **No outcome.** The verse names a configuration. Fame, wealth and eloquence come from
   *other* verses. Merging them here would violate the *no merging* anti-pattern
   (`rule_extraction_framework.md` §5.4) and destroy separate provenance.
2. **No strength.** Any numeric strength would be invented — the *number invention*
   anti-pattern.
3. **No exceptions.** The cancellation conditions are well known and are **elsewhere**.
   The rule is therefore extracted with `exceptions.completeness: unknown`, which is the
   honest default (§7.2).

### 5.2 Extraction gate

| Gate | Result |
|---|---|
| G1 — injunctive? | ✅ Yes. Defining/*nāmadheya* force; not *arthavāda* — no praise, no outcome, no simile |
| G2 — self-contained? | ⚠️ No. Requires *anuvṛtti* (§4.4) — **resolved** |
| G3 — antecedent and consequent both identifiable? | ✅ Yes (§4.2) |

**→ EXTRACT.**

Had this verse read "…and such a one becomes equal to Indra in fame," G1 would have
classified that clause as *arthavāda* and excluded it from the rule while retaining it as
interpretive context.

---

## 6. Layer 4 — Reasoning structure

```
  ┌─────────────────────────────────────────────────────────────┐
  │ CONTEXT   tradition: (unspecified in verse)                 │
  │           application: jātaka        ← inherited, weight ↓  │
  │           chart: rāśi                ← inherited, weight ↓  │
  │           reference_frame: Candra    ← STATED (ablative)    │
  └────────────────────────────┬────────────────────────────────┘
                               │
  ┌────────────────────────────▼────────────────────────────────┐
  │ PRECONDITIONS   chart is natal · Candra has a position      │
  │                 Guru has a position                         │
  └────────────────────────────┬────────────────────────────────┘
                               │
  ┌────────────────────────────▼────────────────────────────────┐
  │ CONDITION                                                   │
  │   house_of(Guru, frame = Candra) ∈ {1, 4, 7, 10}            │
  │                                    └── kendra, defined      │
  │                                        elsewhere → LINK     │
  └────────────────────────────┬────────────────────────────────┘
                               │  indicates
  ┌────────────────────────────▼────────────────────────────────┐
  │ CONCLUSION                                                  │
  │   forms(Gajakesarī_yoga)      modality: indicates           │
  │                               strength: not stated          │
  └────────────────────────────┬────────────────────────────────┘
                               │
  ┌────────────────────────────▼────────────────────────────────┐
  │ EXCEPTIONS   completeness: UNKNOWN                          │
  │   candidates from other verses, each requiring its own      │
  │   extraction and citation:                                  │
  │     · Guru debilitated (nīca)         → undercutting        │
  │     · Guru combust (asta)             → undercutting        │
  │     · Guru afflicted by malefics      → undercutting        │
  │   ALL are undercutting: they withdraw the indication;       │
  │   NONE asserts an opposite conclusion.        (004 §4.2)    │
  └─────────────────────────────────────────────────────────────┘
```

**The exception typing is the substantive claim here.** A cancelled Gajakesarī does not
indicate the *reverse* of the yoga's results. It indicates *nothing from this rule*, leaving
the field to other evidence. Typing these as rebutting defeaters would manufacture negative
conclusions the corpus never asserts — the error `computational_primitives.md` §3.12 exists
to prevent.

---

## 7. Layer 5 — Extracted rule (canonical schema)

Per `rule_extraction_framework.md` §2:

```yaml
id: sha256:<canonical-form-hash>
nominal_id: gajakesari_formation

source:
  text: TBD                          # ← E-ATTEST
  locus: TBD
  edition: null                      # ← blocks corpus admission
  attestation: unverified
  variant_reading: unknown

context:
  tradition: unspecified
  application: jātaka                # inherited (prakaraṇa)
  chart_frame: rāśi                  # inherited (prakaraṇa)
  reference_frame: jyotisha:graha/Candra    # STATED — ablative
  purpose: []                        # unrestricted; resolved at query time

variables:
  - { name: G, type: Graha, binding: jyotisha:graha/Guru }
  - { name: M, type: Graha, binding: jyotisha:graha/Candra }

preconditions:
  - chart.application == jātaka
  - defined(position(G)) ∧ defined(position(M))

conditions:
  expr: house_from(G, M) ∈ kendra_houses
  links:
    - { ref: def:kendra_houses, kind: defines }        # {1,4,7,10}
    - { ref: def:house_from,    kind: defines }        # counting kernel

conclusions:
  - proposition: forms(jyotisha:yoga/Gajakesari)
    modality: indicates
    polarity: positive
    strength: null                   # not stated — NOT invented
    named_result: jyotisha:yoga/Gajakesari

exceptions:
  completeness: unknown              # honest default
  candidates:
    - { ref: TBD, type: undercutting, condition: debilitated(G) }
    - { ref: TBD, type: undercutting, condition: combust(G) }
    - { ref: TBD, type: undercutting, condition: afflicted(G) }

evidence_class: primary
independence_key: <hash of canonical condition+conclusion>

confidence:
  extraction:   moderate     # clean parse; blocked by E-ATTEST and W-VARIANT
  interpretive: moderate-high # structure uncontested; scope inherited, not stated

ambiguities: [A1 resolved, A2 resolved, A3 resolved, A4 resolved]
diagnostics: [E-ATTEST, W-VARIANT, W-EXC]
status: draft                        # cannot advance without an edition
```

### 7.1 Why extraction confidence is only *moderate*

The grammar is clean and every ambiguity resolved. Confidence is nonetheless capped by the
**minimum-stage rule** (`shloka_compiler.md` §10): S0 attestation failed (`E-ATTEST`) and S1
raised `W-VARIANT`. A perfect parse of a text you cannot cite is still a rule you cannot
rely on.

This is the framework behaving correctly on its own benchmark, and it is worth more than a
clean-looking score.

---

## 8. Layer 6 — Reasoning language form

Per `reasoning_language.md` §4:

```
RULE gajakesari_formation
  VERSION 1
  SOURCE   unverified                        -- E-ATTEST
  WITHIN   application = jātaka,             -- inherited
           chart       = rāśi                -- inherited

  GIVEN    G : Graha = Guru
           M : Graha = Candra

  WHEN     house_of(G) FROM M IN kendra

  THEN     INDICATES forms(Gajakesari)

  EXCEPT   UNDERCUT WHEN debilitated(G)      -- source TBD
           UNDERCUT WHEN combust(G)          -- source TBD
           UNDERCUT WHEN afflicted(G)        -- source TBD
           COMPLETENESS unknown

  SUPPORTED_BY  source(unverified)
  CONFIDENCE    DERIVED
```

Two surface features earn their place from the grammar:

- **`FROM M`** is a first-class clause, not a helper argument, because *apādāna* is a
  distinct kāraka. The reference frame is syntactically visible in the rule text, matching
  its visibility in the verse.
- **`UNDERCUT WHEN`** is a distinct keyword from any rebutting form, so the exception type
  cannot be left implicit.

---

## 9. Layer 7 — Execution

Two synthetic charts, chosen so the rule fires cleanly in one and is defeated in the other.
Positions are illustrative constructions, not real ephemeris output.

### 9.1 Chart A — clean fire

| Body | Rāśi | Note |
|---|---|---|
| Candra (Moon) | Meṣa (Aries) | reference frame |
| Guru (Jupiter) | Karka (Cancer) | **exaltation sign** |
| Sūrya (Sun) | Vṛścika (Scorpio) | ~4 signs from Guru → not combust |

**Derived-fact computation** (kernel `house_from`, per `reasoning_ontology.md` §6.2):

```
Aries → Cancer:  Aries 1 · Taurus 2 · Gemini 3 · Cancer 4
house_from(Guru, Candra) = 4
4 ∈ {1, 4, 7, 10} = kendra_houses        ✓
```

**Defeater check:**

| Exception | Test | Result |
|---|---|---|
| debilitated(Guru) | Guru debilitated in Makara; here in Karka | ✗ not fired |
| combust(Guru) | Sun in Vṛścika, Guru in Karka — well beyond the combustion orb | ✗ not fired |
| afflicted(Guru) | No malefic association in this chart | ✗ not fired |

**Result:** `forms(Gajakesari)` — **indicated**.

**Trace:**

```
CONCLUSION  forms(Gajakesari)                        [indicated]
  ├─ RULE        gajakesari_formation v1
  ├─ BINDINGS    G = Guru, M = Candra
  ├─ CONDITION   house_from(Guru, Candra) = 4 ∈ kendra   ✓
  │    ├─ position(Guru) = Karka        [chart input]
  │    ├─ position(Candra) = Meṣa       [chart input]
  │    └─ kernel house_from v1          [deterministic]
  ├─ DEFEATERS   3 checked, 0 fired
  ├─ INFLUENCE   exalted(Guru, Karka) ──strengthens──▶ this indication
  │              (second-order: modulates the edge, does not produce it)
  └─ CONFIDENCE  extraction: moderate  (E-ATTEST)
                 interpretive: moderate-high
                 inferential:  single primary rule, undefeated,
                               positively modulated
                 → NOT high: capped by extraction
```

Note the influence edge. Jupiter's exaltation does not *cause* the yoga and does not form
it — the yoga is formed by position alone. Exaltation **modulates the strength** of the
indication. This is the Influence/Causation distinction
(`computational_primitives.md` §3.7) doing real work: modelled as a causal edge, exaltation
would appear to be part of the yoga's formation, which the verse does not say.

### 9.2 Chart B — defeated

| Body | Rāśi | Note |
|---|---|---|
| Candra (Moon) | Meṣa (Aries) | reference frame |
| Guru (Jupiter) | Makara (Capricorn) | **debilitation sign** |
| Sūrya (Sun) | Vṛścika (Scorpio) | not combust |

**Derived-fact computation:**

```
Aries → Capricorn:  Ari 1 · Tau 2 · Gem 3 · Can 4 · Leo 5 · Vir 6
                    Lib 7 · Sco 8 · Sag 9 · Cap 10
house_from(Guru, Candra) = 10
10 ∈ {1, 4, 7, 10} = kendra_houses       ✓  — the rule DOES fire
```

**Defeater check:**

| Exception | Test | Result |
|---|---|---|
| debilitated(Guru) | Guru debilitated in Makara | ✅ **FIRES — undercutting** |
| combust(Guru) | Beyond orb | ✗ |
| afflicted(Guru) | None | ✗ |

**Result:** indication **withdrawn**. The rule fired; the inference is undercut.

**Trace:**

```
CONCLUSION  forms(Gajakesari)                        [UNDERCUT]
  ├─ RULE        gajakesari_formation v1
  ├─ CONDITION   house_from(Guru, Candra) = 10 ∈ kendra  ✓  (satisfied)
  ├─ DEFEATER    debilitated(Guru)  type: UNDERCUTTING   ✅ fired
  │    ├─ position(Guru) = Makara       [chart input]
  │    ├─ debilitation(Guru) = Makara   [ontology, jyotisha L2]
  │    └─ source: TBD                   [E-ATTEST on the exception too]
  ├─ EFFECT      the inference link is withdrawn
  │              ⚠ NOT: ¬forms(Gajakesari)
  │              ⚠ NOT: an inverse or negative result
  └─ RESIDUE     no indication from THIS rule;
                 other evidence unaffected

  OPEN: nīca-bhaṅga conditions may annul this cancellation
        (exception-to-the-exception, 004 §4.2).
        Not evaluated — those rules are not extracted.
        Recorded as: incomplete_defeater_analysis
```

### 9.3 What Chart B demonstrates

Four things, each of which a conventional rule engine typically gets wrong:

1. **The rule fired and was then defeated.** These are distinct events, both recorded.
   Systems that filter conditions early cannot distinguish "did not apply" from "applied
   and was withdrawn" — and the two have completely different explanations.
2. **Undercutting ≠ negation.** The output is *no indication*, not a negative indication.
3. **The residue is correct.** Other evidence about the chart is untouched; only this rule's
   contribution is removed.
4. **The system reports what it did not evaluate.** The possible exception-to-the-exception
   is flagged rather than silently ignored. A system that reported a confident final answer
   here would be overstating its own coverage.

---

## 10. Layer 8 — Explanation

Rendered in the *pañcāvayava* schema (`explainability_framework.md` §3), which is the Nyāya
five-membered demonstration used as CHOIR's explanation template.

**Chart A:**

| Member | Content |
|---|---|
| ***pratijñā*** (thesis) | This chart indicates the formation of Gajakesarī yoga. |
| ***hetu*** (reason) | Because Jupiter occupies the 4th house counted from the Moon. |
| ***udāharaṇa*** (rule + example) | Wherever Jupiter is situated in a kendra reckoned from the Moon, the combination designated Gajakesarī arises — as stated in the source verse *(citation unverified)*. |
| ***upanaya*** (application) | Here, the Moon is in Aries and Jupiter in Cancer, which is the 4th from the Moon and therefore a kendra. |
| ***nigamana*** (conclusion) | Therefore Gajakesarī is indicated; and since Jupiter is exalted in Cancer, the indication is positively modulated. No cancelling condition was found among the three checked. |

**Chart B:**

| Member | Content |
|---|---|
| ***pratijñā*** | This chart does **not** yield an indication of Gajakesarī yoga from this rule. |
| ***hetu*** | Because although the positional condition is met, Jupiter is debilitated. |
| ***udāharaṇa*** | The general rule holds wherever Jupiter is in a kendra from the Moon; but debilitation withdraws the indication *(source of the exception unverified)*. |
| ***upanaya*** | Here Jupiter is in Capricorn — the 10th from the Moon, hence a kendra, so the rule applies — but Capricorn is Jupiter's sign of debilitation. |
| ***nigamana*** | Therefore no indication follows from this rule. This is **not** a contrary indication. Conditions that may annul the debilitation were not evaluated, so this conclusion is provisional. |

The template accommodates negative and defeated conclusions without modification, which is
a genuine argument for adopting it over an ad-hoc explanation format. The last sentence of
each *nigamana* carries the confidence and coverage caveats into the reader's view rather
than leaving them in a footnote.

---

## 11. Benchmark acceptance criteria

Any pipeline change must reproduce all of these:

| # | Criterion | Layer |
|---|---|---|
| B1 | Metre identified as anuṣṭubh; pattern anomaly raised as `W-VARIANT` | §2.1 |
| B2 | *candrāt* analysed as ablative, **not** genitive | §3.1 A1 |
| B3 | *jīva* resolved to Jupiter, not "living being" | §3.1 A2 |
| B4 | *gajakesari-saṃjñaka* analysed as possessive; referent outside constituents | §4.1 |
| B5 | **Locative absolute detected and read as conditional** — no particle present | §4.2 |
| B6 | *apādāna* mapped to `reference_frame`, not to subject or object | §4.3 |
| B7 | Elided *yogaḥ* recovered; inherited scope marked as reduced-weight | §4.4 |
| B8 | Conclusion is formation only — **no outcome, no strength invented** | §5.1 |
| B9 | Exceptions typed **undercutting**; completeness `unknown` | §6 |
| B10 | `E-ATTEST` raised; rule does **not** reach `accepted` | §7 |
| B11 | Extraction confidence capped by minimum stage, not averaged | §7.1 |
| B12 | Chart A: fires, undefeated, influence edge second-order | §9.1 |
| B13 | Chart B: fires **then** is undercut; output is *no indication*, not negation | §9.2 |
| B14 | Chart B reports unevaluated exception-to-exception | §9.2 |
| B15 | Explanation renders in *pañcāvayava*, including the defeated case | §10 |

**B5, B9 and B13 are the discriminating criteria.** A pipeline can score well on the others
while failing these three, and a pipeline that fails any of them will produce a corpus that
looks correct and reasons wrongly.

---

## 12. Outstanding work on this benchmark

1. **Resolve `E-ATTEST`** — locate the verse in a stated critical edition; record editor,
   locus, and variants; resolve `W-VARIANT` metrically. Until then the benchmark is
   methodological only.
2. **Extract the three exception verses** with their own citations, so the defeater chain is
   grounded rather than stipulated.
3. **Extract the *nīca-bhaṅga* conditions**, giving the benchmark a genuine
   exception-to-exception and exercising the well-foundedness requirement.
4. **Extract the outcome verses** separately, so the benchmark exercises multi-rule evidence
   accumulation across independent sources.
5. **Add a *vikalpa* case** — a second verse whose formulation of this yoga differs, so the
   benchmark also covers contested extraction and disjunctive termination.
6. **Establish the tradition context.** The verse as given does not identify its school;
   whether it is Parāśara-aligned affects the context lattice and therefore cross-school
   conflict handling.

Items 2–5 turn this from a single-rule benchmark into a small but complete corpus
exercising every mechanism in Phases 3 and 4. That is the recommended next milestone.
