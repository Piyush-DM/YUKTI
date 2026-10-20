# Canonical Shloka Analysis (Benchmark)

| | |
|---|---|
| **Document ID** | YK-R-008 |
| **Source** | `choir/research/phase-2-vedic/canonical_shloka_analysis.md` (008) |
| **Series** | CHOIR Research Programme |
| **Revision** | A |
| **Status** | Active |
| **Last Updated** | 2026-08-23 |

## Abstract

This document carries a single half-verse stating the formation of **Gajakesarī yoga** end to end through every layer of the CHOIR pipeline — original Sanskrit, word-by-word analysis, grammar, meaning, reasoning structure, extracted rule, reasoning-language form, execution, and explanation — and fixes that worked example as the project's reference benchmark against which any pipeline change is validated (§1). It records fifteen acceptance criteria (B1–B15) that a pipeline must reproduce, of which B5, B9 and B13 are identified as discriminating (§11). It also records that the verse's citation is unverified: the rule carries diagnostic `E-ATTEST`, cannot enter the authoritative corpus, and is admitted only as a *methodological* benchmark (§1.2, §7).

**Status note.** This document is Active: it is a complete research document, drafted, and **not accepted as specification**. The source itself is marked "Draft for review" (§ header). `choir/research/README.md` records the programme-level position — "All 18 deliverables drafted. None accepted. Every document is a hypothesis, per `MANIFESTO.md`." `MANIFESTO.md` itself states the underlying commitment as "Treat every computational object as a hypothesis rather than an established truth."

## Research Question

The source states its purpose rather than posing a question. Its framing (§1):

> One shloka is carried end to end — original Sanskrit → word-by-word → grammar → meaning → reasoning → rule graph → computational rule → execution — to serve as the project's benchmark. Any change to the pipeline is validated against this worked example.

The selection criterion is stated in §1.1: the verse was chosen because it exercises, in sixteen syllables, six of the hardest problems identified in Phase 2 — locative absolute (*sati saptamī*) carrying conditional force with no conditional particle; the ablative *candrāt* as a reference-frame parameter (R10); a *nāmadheya* naming construction; two compounds of different types; an elided subject (*yogaḥ*); a polysemous technical term (*jīva*); and well-known cancellation conditions located in other verses. The source states plainly why an easier verse was rejected: "A verse containing an explicit *cet* ("if") would have been easier and would have tested nothing" (§1.1).

## Finding

### The benchmark rule cannot be admitted to the corpus

Before any analysis, §1.2 records the attestation status under the heading "read this first":

> **`attestation: unverified` · diagnostic `E-ATTEST`**
>
> The verse below is given in a form widely circulated in Jyotiṣa literature and commonly associated with the Gajakesarī yoga. **It has not been checked against a critical edition, and no chapter/verse locus is asserted here.** Formulations of this yoga vary between texts and recensions.

Under `rule_extraction_framework.md` §2.1, `source.edition` is mandatory, and the source states that the rule therefore **cannot enter the authoritative corpus** in its present state (§1.2). It is admitted as a *methodological* benchmark — the analysis chain is the deliverable, and the rule carries its own diagnostic. The source describes this as deliberate: the framework's first requirement is that unverifiable citations be visible rather than laundered, and the benchmark should demonstrate the framework rather than quietly exempt itself from it (§1.2). The stated resolution task is to locate the verse in a stated edition, record editor and locus, collect variants, and re-run the analysis; the expected outcome is that only §2 and §12 change.

### Layer 0 — text and metre, with an unresolved anomaly

The half-verse is given in Devanāgarī, IAST (*candrāt kendragate jīve gajakesari-saṃjñakaḥ*) and SLP1 internal form (§2). The metrical analysis (§2.1) gives two pādas of eight syllables each, consistent with **anuṣṭubh**, of which this is a half-verse.

The metrical check did not pass cleanly:

> **Diagnostic `W-VARIANT` (review item):** the fine-grained *laghu/guru* pattern check for pāda *a* does not cleanly match the *pathyā* form of anuṣṭubh. This may indicate a permitted *vipulā* variant, a transmission variant, or a paraphrase rather than an attested verse. **Flagged for review alongside the citation task.**

The source treats this as the checksum working, not failing: "A pipeline that reported 'metre OK' here would be less useful" (§2.1). The pāda boundary after *jīve* is nonetheless used as a high-confidence segmentation anchor.

### Layer 1 — word-by-word and the four recorded ambiguities

Sandhi splitting is described as unusually clean (§3). Four ambiguities are recorded and resolved (§3.1):

| ID | Kind | Resolution | Grounds (as stated) |
|---|---|---|---|
| `A1` | Case syncretism — *candrāt* ablative or genitive-class reading | **Ablative** | *a*-stem *candra*: ablative sg. is *candrāt*, genitive sg. is *candrasya*. **Unambiguous here.** |
| `A2` | Lexical sense — *jīva* = "living being, soul" or Jupiter (Bṛhaspati) | **Jupiter** | Domain lexicon; co-occurrence with *kendra* and *candra*; the verse is Jyotiṣa |
| `A3` | Compound type — *gajakesari-saṃjñaka* | **Possessive/derivative** | *-ka* suffix on *saṃjñā*; means "having the designation X", referent outside |
| `A4` | Elision — subject of *saṃjñakaḥ* | ***yogaḥ*** | Masculine nominative singular agreement; *nāmadheya* construction; section context |

The source calls `A1` "the important non-event": `sanskrit_analysis_pipeline.md` §9 flags ablative/genitive syncretism as a silent, rule-changing failure mode, and here the *a*-stem paradigm distinguishes them cleanly. In a verse using a stem where they coincide, this row "would be a mandatory review trigger" (§3.1). `A2` is stated as the concrete case behind the finding that a domain lexicon is the highest-value early artefact: without a Jyotiṣa lexicon, *jīve* reads as "in a living being" and the entire rule dissolves (§3.1).

### Layer 2 — grammar

**Compounds (§4.1).** *kendra-gata* is a *tatpuruṣa* (locative-determinative), head *gata*, sense "gone to / situated in a kendra". *gajakesari-saṃjñaka* is a derivative possessive whose referent lies **outside the constituents** — the thing *having* the designation, i.e. the yoga. The source identifies the second as the *bahuvrīhi*-class hazard in live form: read as a *tatpuruṣa* it "would denote *the designation itself* rather than *the thing designated*, and the rule's conclusion would become a statement about a name rather than about a configuration" (§4.1).

**Locative absolute (§4.2).** The two locatives *kendragate jīve* form a **locative absolute** (*sati saptamī*), and the source states in emphasis: "**This construction carries conditional force with no conditional particle.**" There is no *cet*, no *yadi*, no *yadā*. Any keyword-based extraction method "finds nothing here and either discards the verse or — worse — extracts it as an unconditional assertion that Gajakesarī yoga simply exists."

**Kāraka labelling (§4.3).** *jīve* is *kartṛ* of the participle (Jupiter); *kendragate* is *adhikaraṇa* (the kendra region); *candrāt* is ***apādāna***, the point of reckoning (the Moon); elided *(yogaḥ)* is *kartṛ* of the main predicate. The source identifies "***apādāna* → reference frame" as "the load-bearing mapping": it fixes that kendras are counted from the Moon, not from the Ascendant, "which is what makes this yoga distinct from the ordinary Ascendant-relative reading, and is precisely requirement R10." When the explanation system is asked why the Moon is the reference frame, the answer available in the trace is "because it is in the ablative, which marks *apādāna*" — the grammatical justification survives to the user because kāraka roles become hyperedge participant roles (`knowledge_graph_spec.md` §7) rather than being translated away.

**Anuvṛtti (§4.4).** The source states that "[t]wo things are inherited from the section, not stated in the verse", and the table beneath that sentence lists three: the elided subject *yogaḥ* (interpretive weight High), the application *jātaka* (**Reduced**), and the chart rāśi/D-1 (**Reduced**). The count and the table disagree in the source; the three tabulated rows are reproduced here as given. The reduction applies the Mīmāṃsā interpretive priority ordering (`vedic_reasoning_methodology.md` §5.3) as a confidence input, on the stated ground that *prakaraṇa* ranks below *śruti* — a scope condition inherited from context is weaker evidence of meaning than one directly stated. The source states this is why "the extracted rule's interpretive confidence is not maximal despite an otherwise clean analysis."

### Layer 3 — meaning, and three absences

The literal reading given is: *"Jupiter being situated in an angle from the Moon, [there arises the combination] designated Gajakesarī."* The structured reading records modality *indicates* — "the verse asserts formation, not an outcome" — reference frame Moon (stated, ablative), and **Strength: None stated** (§5).

§5.1 lists three absences "each of which an undisciplined extractor would fill in":

1. **No outcome.** Fame, wealth and eloquence come from *other* verses; merging them would violate the *no merging* anti-pattern (`rule_extraction_framework.md` §5.4) and destroy separate provenance.
2. **No strength.** Any numeric strength would be invented — the *number invention* anti-pattern.
3. **No exceptions.** The cancellation conditions are well known and are **elsewhere**; the rule is extracted with `exceptions.completeness: unknown`, "which is the honest default".

The extraction gate (§5.2) passes G1 (injunctive — defining/*nāmadheya* force, not *arthavāda*) and G3 (antecedent and consequent both identifiable), and fails G2 (self-contained) — resolved via *anuvṛtti*. Verdict: **EXTRACT**. Had the verse read "…and such a one becomes equal to Indra in fame," G1 would have classified that clause as *arthavāda* and excluded it from the rule while retaining it as interpretive context.

### Layer 4 — reasoning structure and exception typing

The reasoning structure (§6) records context (reference_frame Candra STATED; application and chart inherited with reduced weight), preconditions, the condition `house_of(Guru, frame = Candra) ∈ {1, 4, 7, 10}`, the conclusion `forms(Gajakesarī_yoga)` with modality *indicates* and strength not stated, and exceptions with `completeness: UNKNOWN`: Guru debilitated (*nīca*), Guru combust (*asta*), Guru afflicted by malefics.

The source names the exception typing as "the substantive claim here": all three candidates are **undercutting**; none asserts an opposite conclusion. "A cancelled Gajakesarī does not indicate the *reverse* of the yoga's results. It indicates *nothing from this rule*, leaving the field to other evidence." Typing these as rebutting defeaters "would manufacture negative conclusions the corpus never asserts" — the error `computational_primitives.md` §3.12 exists to prevent (§6).

### Layer 5 — the extracted rule and why confidence is capped

The canonical-schema rule (§7) records `source.edition: null` with the inline comment "blocks corpus admission", `attestation: unverified`, `variant_reading: unknown`, `strength: null` with the comment "not stated — NOT invented", `exceptions.completeness: unknown` ("honest default") with all three candidate refs `TBD`, `diagnostics: [E-ATTEST, W-VARIANT, W-EXC]`, and `status: draft` with the comment "cannot advance without an edition". Confidence is recorded as `extraction: moderate` and `interpretive: moderate-high`.

§7.1 explains the extraction figure: "The grammar is clean and every ambiguity resolved. Confidence is nonetheless capped by the **minimum-stage rule** (`shloka_compiler.md` §10): S0 attestation failed (`E-ATTEST`) and S1 raised `W-VARIANT`. A perfect parse of a text you cannot cite is still a rule you cannot rely on." The source adds that this is "the framework behaving correctly on its own benchmark, and it is worth more than a clean-looking score."

### Layer 6 — reasoning-language form

The rule is rendered in the reasoning language (§8) with `SOURCE unverified -- E-ATTEST`, `WHEN house_of(G) FROM M IN kendra`, `THEN INDICATES forms(Gajakesari)`, three `UNDERCUT WHEN` clauses each marked `-- source TBD`, and `COMPLETENESS unknown`. Two surface features are stated to earn their place from the grammar: **`FROM M`** is a first-class clause rather than a helper argument, because *apādāna* is a distinct kāraka, so the reference frame is syntactically visible in the rule text as it is in the verse; and **`UNDERCUT WHEN`** is a distinct keyword from any rebutting form, so the exception type cannot be left implicit.

### Layer 7 — execution on two charts

The source states plainly that the charts are "**Two synthetic charts**… Positions are illustrative constructions, not real ephemeris output" (§9).

**Chart A — clean fire (§9.1).** Candra in Meṣa, Guru in Karka (exaltation sign), Sūrya in Vṛścika. `house_from(Guru, Candra) = 4`, which is in `kendra_houses`. Three defeaters checked, none fired. Result: `forms(Gajakesari)` — indicated. The trace records confidence as extraction moderate (`E-ATTEST`), interpretive moderate-high, inferential single primary rule undefeated and positively modulated, and then "→ NOT high: capped by extraction". The exaltation appears as an **influence edge**, second-order: it "modulates the edge, does not produce it". The source states the reason: "Jupiter's exaltation does not *cause* the yoga and does not form it — the yoga is formed by position alone." This is the Influence/Causation distinction (`computational_primitives.md` §3.7) — "modelled as a causal edge, exaltation would appear to be part of the yoga's formation, which the verse does not say."

**Chart B — defeated (§9.2).** Candra in Meṣa, Guru in Makara (debilitation sign). `house_from(Guru, Candra) = 10`, in `kendra_houses` — "the rule DOES fire". The defeater `debilitated(Guru)` then fires as undercutting. Result: indication **withdrawn**. The trace states explicitly what the effect is *not*: "⚠ NOT: ¬forms(Gajakesari)" and "⚠ NOT: an inverse or negative result", with residue "no indication from THIS rule; other evidence unaffected". The defeater's own source is `TBD` — "`E-ATTEST` on the exception too". The trace closes with an open item:

> OPEN: nīca-bhaṅga conditions may annul this cancellation (exception-to-the-exception, 004 §4.2). Not evaluated — those rules are not extracted. Recorded as: incomplete_defeater_analysis

§9.3 states four things Chart B demonstrates, "each of which a conventional rule engine typically gets wrong": the rule fired and was then defeated, and these are distinct events both recorded (systems that filter conditions early cannot distinguish "did not apply" from "applied and was withdrawn"); undercutting ≠ negation; the residue is correct, with other evidence untouched; and the system reports what it did not evaluate — "A system that reported a confident final answer here would be overstating its own coverage."

### Layer 8 — explanation

Both charts are rendered in the *pañcāvayava* schema (`explainability_framework.md` §3), the Nyāya five-membered demonstration used as CHOIR's explanation template (§10). Chart A's *udāharaṇa* carries the tag *(citation unverified)*; Chart B's *udāharaṇa* carries *(source of the exception unverified)*, and its *nigamana* states: "Therefore no indication follows from this rule. This is **not** a contrary indication. Conditions that may annul the debilitation were not evaluated, so this conclusion is provisional."

The source's assessment: "The template accommodates negative and defeated conclusions without modification, which is a genuine argument for adopting it over an ad-hoc explanation format. The last sentence of each *nigamana* carries the confidence and coverage caveats into the reader's view rather than leaving them in a footnote" (§10).

### Acceptance criteria

§11 fixes fifteen criteria that any pipeline change must reproduce:

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

The source designates **B5, B9 and B13** as the discriminating criteria: "A pipeline can score well on the others while failing these three, and a pipeline that fails any of them will produce a corpus that looks correct and reasons wrongly" (§11).

## Architectural Implications

- **Do not compile through translation.** The source states this as one of two architectural decisions justified concretely by the locative absolute: "English renderings supply an 'if' that is not in the source; the conditional force must be recovered from the *case morphology*, which translation destroys" (`shloka_compiler.md` §3, cited at §4.2).
- **Dependency parsing is required, not optional** (`sanskrit_analysis_pipeline.md` §6.3, cited at §4.2).
- **Kāraka roles must survive into the graph.** Because kāraka roles become hyperedge participant roles (`knowledge_graph_spec.md` §7), the grammatical justification for the reference frame remains available to the explanation system rather than being translated away (§4.3).
- **A Jyotiṣa domain lexicon is the highest-value early artefact.** The `A2` resolution is the concrete case behind that finding (`sanskrit_analysis_pipeline.md` §10, cited at §3.1); without a Jyotiṣa lexicon, *jīve* reads as "in a living being" and the entire rule dissolves.
- **Inherited scope must reduce confidence rather than be silently accepted.** The Mīmāṃsā interpretive priority ordering (`vedic_reasoning_methodology.md` §5.3) enters as a confidence input on *prakaraṇa*-inherited context (§4.4).
- **Confidence is capped by the minimum stage, not averaged** (`shloka_compiler.md` §10, cited at §7.1); attestation failure at S0 caps an otherwise clean parse.
- **Mandatory citation blocks corpus admission.** `source.edition` being mandatory under `rule_extraction_framework.md` §2.1 keeps this rule at `status: draft` and out of the authoritative corpus (§1.2, §7).
- **Exception typing must be explicit in the reasoning language.** `UNDERCUT WHEN` is a distinct keyword from any rebutting form so the type cannot be left implicit, and `FROM M` is a first-class clause because *apādāna* is a distinct kāraka (§8).
- **Undercutting must not be compiled to negation**, and influence must not be compiled to causation (`computational_primitives.md` §3.12 and §3.7, cited at §6 and §9.1).
- **Firing and defeat must be recorded as distinct events**; early condition filtering makes "did not apply" indistinguishable from "applied and was withdrawn" (§9.3).
- ***Pañcāvayava* is adopted as the explanation template** on the stated ground that it accommodates negative and defeated conclusions without modification (`explainability_framework.md` §3, cited at §10).
- **B1–B15 constitute the acceptance test for the compiler** (§11); the source's header records that this document "is the reference benchmark" and feeds "every downstream document; the acceptance test for the compiler".

## Open Questions

The source records the following outstanding work on this benchmark (§12), and further unresolved items elsewhere in the document:

1. **`E-ATTEST` is unresolved.** The verse must be located in a stated critical edition, with editor, locus and variants recorded, and `W-VARIANT` resolved metrically. "Until then the benchmark is methodological only" (§12 item 1). The rule's `source.text`, `source.locus` are `TBD` and `source.edition` is `null` (§7).
2. **`W-VARIANT` is unresolved.** The *laghu/guru* pattern for pāda *a* does not cleanly match *pathyā*; whether this is a permitted *vipulā*, a transmission variant, or a paraphrase is not determined (§2.1).
3. **The three exception verses are not extracted.** Their refs are `TBD` and the defeater chain is stipulated rather than grounded (§7, §9.2, §12 item 2).
4. **Exception completeness is `unknown`** — the source states this is the honest default, not a resolved value (§5.1, §6, §7).
5. **The *nīca-bhaṅga* conditions are not extracted and were not evaluated.** Chart B records this as `incomplete_defeater_analysis`, and the source lists their extraction as needed to give the benchmark a genuine exception-to-exception and exercise the well-foundedness requirement (§9.2, §12 item 3).
6. **The outcome verses are not extracted**, so the benchmark does not yet exercise multi-rule evidence accumulation across independent sources (§12 item 4).
7. **No *vikalpa* case is present.** A second verse whose formulation of this yoga differs is needed to cover contested extraction and disjunctive termination (§12 item 5).
8. **The tradition context is unestablished.** "The verse as given does not identify its school; whether it is Parāśara-aligned affects the context lattice and therefore cross-school conflict handling" (§12 item 6). The rule records `tradition: unspecified` (§7).
9. **The execution results rest on synthetic charts.** Positions are stated to be illustrative constructions, not real ephemeris output (§9).

The source states that items 2–5 of §12 "turn this from a single-rule benchmark into a small but complete corpus exercising every mechanism in Phases 3 and 4. That is the recommended next milestone."

## Related Documents

The source records its dependencies as 004–007 and states that it feeds "every downstream document; the acceptance test for the compiler". Documents it depends on or cites directly:

- [YK-R-001 — Computational Primitive Specification](YK-R-001-computational-primitive-specification.md) — cited at §6 (§3.12, rebutting vs undercutting) and §9.1 (§3.7, Influence/Causation)
- [YK-R-002 — Reasoning Ontology](YK-R-002-reasoning-ontology.md) — cited at §9.1 for the `house_from` kernel (§6.2)
- [YK-R-003 — Knowledge Graph Specification](YK-R-003-knowledge-graph-specification.md) — cited at §4.3 for kāraka roles as hyperedge participant roles (§7)
- [YK-R-004 — Vedic Reasoning Methodology](YK-R-004-vedic-reasoning-methodology.md) — dependency; cited at §1.1, §4.4, §6 and §9.2
- [YK-R-005 — Sanskrit Analysis Pipeline](YK-R-005-sanskrit-analysis-pipeline.md) — dependency; cited at §2.1, §3.1, §4.1 and §4.2
- [YK-R-006 — Shloka Compiler](YK-R-006-shloka-compiler.md) — dependency; cited at §1.1, §4.2 and §7.1
- [YK-R-007 — Rule Extraction Framework](YK-R-007-rule-extraction-framework.md) — dependency; cited at §1.1, §1.2, §3.1, §5.1 and §7
- [YK-R-012 — Explainability Framework](YK-R-012-explainability-framework.md) — cited at §10 for the *pañcāvayava* schema (§3)
- [YK-R-014 — Reasoning Language (CRL)](YK-R-014-reasoning-language-crl.md) — cited at §8 for the rule surface form (§4)
