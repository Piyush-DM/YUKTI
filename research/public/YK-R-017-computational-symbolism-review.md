# Computational Symbolism Review

| | |
|---|---|
| **Document ID** | YK-R-017 |
| **Source** | `choir/research/phase-5-generalization/computational_symbolism_review.md` (017) |
| **Series** | CHOIR Research Programme |
| **Revision** | A |
| **Status** | Active |
| **Last Updated** | 2026-08-23 |

## Abstract

The source document surveys the symbolic-AI tradition CHOIR sits in and then states "precisely **where CHOIR differs, and where it does not**" (§1). It records that almost every individual mechanism in CHOIR already exists in the literature, tabulates nine such mechanisms against their prior art, lists seven things CHOIR does not claim (§3), and reduces the novelty claim to six specific differences (§4) plus a composition claim (§5), each stated with the observation that would refute it. The document is explicit that the composition claim "is a design claim, not a theoretical result, and it is unvalidated" (§5), that the survey is analytical rather than a systematic literature review (§7), and that one of its own threats — influence reducing to weighted causation — remains open (§6, T4).

This publication is **Active**: the source is a complete research document, drafted but not accepted as specification. Its own header records its status as "Draft for review". Per `MANIFESTO.md`, every research document is a hypothesis rather than an established truth.

## Research Question

The source states its purpose under a heading that names the risk it is guarding against — "Purpose, and a warning about novelty claims" (§1):

> This document surveys the symbolic-AI tradition CHOIR sits in, and then does the harder
> thing: states precisely **where CHOIR differs, and where it does not**.

The question is therefore not "what is CHOIR?" but "what, if anything, in CHOIR is new, and under what conditions would that claim fail?" The document sets the warning first: "Almost every individual mechanism in CHOIR exists in the literature" (§1), and "**A project that claimed to have invented any of these would be wrong.**" It then narrows the claim it intends to defend: "CHOIR's contribution, if it has one, is in the *composition* and in a small number of requirements that the literature does not address because its source material does not raise them. §5 states those, and §6 states what would refute the novelty claim." (§1)

## Finding

### The prior art, stated first (§1)

The document opens by conceding nine mechanisms to the literature:

| CHOIR mechanism | Prior art |
|---|---|
| Defeasible rules with exceptions | Defeasible logic; non-monotonic reasoning |
| Undercutting vs rebutting defeat | Pollock's defeater typology |
| Argumentation-based conflict resolution | Dung's abstract argumentation; ASPIC+ |
| Contexts partitioning truth | Cyc microtheories; RDF named graphs |
| Reified statements with metadata | RDF reification; RDF-star; Wikidata qualifiers |
| Discrimination-network matching | RETE |
| Dependency-tracked retraction | TMS / ATMS |
| Ontology layering and versioning | Standard KR practice |
| Legal rule markup with provenance | LegalRuleML |

### The tradition (§2)

**Knowledge representation and ontologies (§2.1).** The line from semantic networks through frames to description logics established "taxonomies, inheritance, typed relations, formal semantics". Woods, *What's in a Link?* (1975) is named as "the enduring lesson: link types without defined semantics make a network uninterpretable"; CHOIR's response — every relation declaring arity, transitivity, symmetry and inverse (`reasoning_ontology.md` §4.1) — is characterised without credit: "This is not innovation; it is compliance with a fifty-year-old finding that systems still routinely violate." Cyc's microtheories are singled out as the same insight as `computational_primitives.md` §3.10, "and Cyc had it decades earlier". The stated difference is deliberately small: "contexts are **derived from source structure** (recension, school, chapter) rather than hand-declared, and context membership is itself evidence-bearing."

**Description logics and OWL (§2.2).** The document credits DLs with "decidable reasoning with well-understood complexity" and then states why CHOIR cannot simply be OWL:

| DL assumption | CHOIR requirement |
|---|---|
| **Monotonic** — adding axioms never retracts conclusions | *apavāda* retracts by design |
| **Open-world** throughout | Absence-reasoning needs scoped closure (*anupalabdhi*) |
| Consistency is required; inconsistency is fatal | Corpus is inconsistent *by nature*; contexts localise it |
| No native statement-level metadata | Every statement needs confidence, provenance, validity |
| No graded support | Evidence accumulates |

"The monotonicity mismatch is fundamental, not a matter of tooling. A system whose central phenomenon is defeat cannot have a monotonic core." (§2.2) What CHOIR takes from DL is stated as a discipline rather than a mechanism: "the discipline of asking what is decidable and why", answered in `reasoning_language.md` §7.3 — "no function symbols, finite domains, stratification, well-founded defeat."

**Rule engines and expert systems (§2.3).** Production systems (OPS5 and descendants; RETE, Forgy 1982) are credited with efficient many-rules matching. MYCIN is named "the most instructive precedent, because it attempted exactly what CHOIR attempts — graded confidence plus explanation in an institutional domain — and its weaknesses are the ones CHOIR must avoid":

| MYCIN limitation | CHOIR response |
|---|---|
| Certainty factors were **hand-assigned** | Confidence is derived, never authored (`confidence_framework.md` §1) |
| CF combination assumed independence | Correlation clustering (`evidence_model.md` §4) |
| No source provenance — rules encoded expert opinion | Every rule traces to a locus in an edition |
| Explanation = rule trace only | Seven mandatory components including alternatives and coverage |
| No conflict machinery beyond ordering | Full precedence and *vikalpa* |

"The hand-assigned certainty factor is the failure CHOIR's first governing rule exists to prevent. It is worth being explicit that this is a *known* historical failure mode, not a hypothetical one." (§2.3) What CHOIR takes: "RETE, which fits well (`execution_pipeline.md` §4.1), and the observation that explanation must be designed in rather than added."

**Non-monotonic reasoning and argumentation (§2.4).** Described as "the most directly relevant body of work" — default logic, circumscription and defeasible logic as formalisms for "normally P, unless"; Pollock's rebutting/undercutting typology, which "CHOIR adopts wholesale", with the recorded finding from `vedic_reasoning_methodology.md` §2.1 that "the śāstric *upādhi* apparatus draws the same distinction independently"; Dung's abstract argumentation (1995), where "CHOIR's Layer 1 is a Dung-style framework, and `undecided` is what surfaces as *vikalpa*"; ASPIC+ and structured argumentation; and legal argumentation (Prakken, Sartor and others), "precisely CHOIR's problem in a different domain".

The section's conclusion is a concession: "**CHOIR is squarely inside this tradition.** The two-layer semantics (`evidence_model.md` §5.1) is standard argumentation plus a graded layer. Any claim that CHOIR invented defeasible reasoning would be false." (§2.4)

**Semantic web (§2.5).** RDF, SPARQL, OWL, SHACL and the reification problem (`knowledge_graph_spec.md` §2.1). "**Wikidata's qualifier and reference model** is the most relevant practical precedent: every statement carries qualifiers and source references, which is functionally what CHOIR requires. RDF-star generalises it." CHOIR's stated departure is "n-ary role-labelled relations, driven by kāraka analysis (`knowledge_graph_spec.md` §2.3) — and RDF is retained as an export target rather than rejected."

**Neuro-symbolic and embeddings (§2.6).** CHOIR's position is recorded as "deliberately conservative — **neural retrieval, symbolic adjudication** (`knowledge_graph_spec.md` §2.5) — enforced by invariant I9". The document is careful about the scope of that position: "This is not a claim that neuro-symbolic integration cannot work. It is a claim about *this* system's requirements: a conclusion whose warrant includes an embedding score cannot be traced, cited, or defeated, and traceability is CHOIR's entire value proposition. The line may be redrawn if a form of learned inference emerges that is genuinely auditable."

### What CHOIR does not claim (§3)

Stated by the source "plainly, because a novelty claim is only credible alongside an honest account of what is borrowed":

- Not a new logic. The semantics are standard argumentation plus a graded layer.
- Not a new matching algorithm. RETE.
- Not a new ontology methodology. Standard layering and versioning.
- Not the first system with contexts. Cyc.
- Not the first with statement-level metadata. RDF-star, Wikidata.
- Not the first to compile rules from legal text. LegalRuleML, Catala, and the AI-and-law literature generally.
- Not the first to attempt graded confidence with explanation. MYCIN.

### Where CHOIR differs (§4)

Six differences, "each stated with what it would take to show it is not novel".

**4.1 Compilation from canonical text with the grammatical derivation preserved.** "Existing systems formalise *from* a source; the formalisation is an artefact that replaces the source. CHOIR keeps the derivation chain intact: manuscript span → sandhi split → morphology → kāraka role → IR node → conclusion." The stated practical consequence, from `explainability_framework.md` §8, is that the system can answer *"why is the Moon the reference frame and not the subject?"* with *"because it is in the ablative, which marks apādāna"* — "a grammatical justification surviving all the way to a user-facing explanation." Not novel if an existing system preserves morphosyntactic derivation into its executable rules; the source adds that "Computational legal systems generally do not — they formalise from a human reading of the text."

**4.2 Ambiguity as a first-class IR citizen.** "Conventional IRs represent determinate programs. CHOIR's HIR represents *unresolved alternatives* with their consequences, and lowering is blocked until they close (`choir_intermediate_representation.md` §3.1)." Existing systems "handle source ambiguity by resolving it during formalisation — the resolution happens in a human's head and is not recorded. CHOIR records it as an object with grounds and an adjudicator, and reuses it via the resolution cache." Not novel if an existing rule-extraction system carries unresolved readings into its IR rather than resolving them at authoring time.

**4.3 The interpretive confidence axis.** `confidence_framework.md` §3.2. "The literature has extraction confidence (NLP) and inferential confidence (evidence). It largely lacks **interpretive confidence** — *does the tradition agree what this text means?* — because Western KR generally assumes an authoritative formalisation exists." For a corpus with a thousand-year commentarial dispute that assumption fails; the axis "is independently sourced (commentarial agreement, school divergence, *prakaraṇa* vs *śruti* grounding) and cannot be derived from the other two." Not novel if an existing framework separates "how confident are we in the reading" from "how confident are we that the reading is what the authority meant." The source grades this one: "This is probably CHOIR's strongest individual claim."

**4.4 *Vikalpa* — terminating in a legitimate disjunction.** The document concedes the machinery exists: "Argumentation frameworks produce `undecided`, so the *machinery* exists." What it claims is unusual is "treating it as a **first-class, reportable outcome with its own explanation** — including which precedence principles were tried and why each was unavailable (`conflict_resolution.md` §8) — rather than as a failure to conclude", with `domain_independence.md` §4 cited as showing the need in all five domains. Not novel if an existing system reports unresolved conflict as a primary output with a full account of the attempted resolution.

**4.5 Explanation as projection, using a traditional proof schema.** Two parts, graded differently. Projection rather than generation (`explainability_framework.md` §1) gives "faithfulness by construction", but the source qualifies it: "This is a strong architectural commitment, though not unique — trace-based explanation is old." The *pañcāvayava* schema — "adopting a classical Indian proof form as the explanation template" — "is, as far as this survey found, not done elsewhere, and it earns its place on merit: it forces the warrant to be exhibited, and it handles defeated conclusions without modification (`domain_independence.md` §5)." The falsifier is stated with the split preserved: "Not novel if: trace-projected explanation with an exhibited warrant is standard — the projection half may well be; the schema half appears not to be."

**4.6 Influence as a primitive distinct from causation.** `computational_primitives.md` §3.7. "Most rule systems provide causal or weighted edges and express modulation as a weight. CHOIR types influence as **second-order** — it targets an edge and cannot assert a conclusion, enforced in the IR type system (`choir_intermediate_representation.md` §4.6)." `domain_independence.md` §3 is cited as finding "three of five domains influence-dominant and none causation-only". The falsifier is the framework's own: "Not novel if: the distinction collapses — i.e. the falsifier in `computational_primitives.md` §5 succeeds and influence-heavy corpora encode losslessly as weighted causation. **This remains open and should be tested seriously.**"

### The composition claim (§5)

"The strongest honest statement of CHOIR's position is not about any single mechanism":

> Existing systems address *some* of {source fidelity, ambiguity preservation, interpretive
> uncertainty, structured defeat, legitimate disjunction, projected explanation, domain
> independence}. CHOIR is an attempt to address all of them in one architecture, and each
> constrains the others.

The interlocking is stated as the substance of the claim:

- Source fidelity requires preserving grammatical derivation → forces role-labelled n-ary storage → forces the hypergraph decision.
- Ambiguity preservation → forces the three-level IR.
- Interpretive uncertainty → forces the confidence vector → forbids scalar collapse.
- Structured defeat → forces two-layer semantics → forbids folding defeat into weights.
- Legitimate disjunction → forbids forced resolution → forces resolution objects that record what was unavailable.
- Projected explanation → forces reified inferences → which is what makes correlation detection free (`evidence_model.md` §4.2).

"That last one is the clearest example of the composition paying off: a mechanism required for explanation turns out to solve the evidence-independence problem at no additional cost." (§5)

The section then withdraws any claim to having demonstrated this: "**This is a design claim, not a theoretical result, and it is unvalidated.** The correct posture is that CHOIR is a synthesis whose value depends on whether the composition holds under real corpus load — which `domain_independence.md` §6 is designed to test and which has not been run." (§5)

### Threats to the novelty claim (§6)

| # | Threat | Status as recorded |
|---|---|---|
| T1 | The composition is unremarkable — each piece integrates trivially | Plausible; only implementation will show |
| T2 | Interpretive confidence is subsumed by existing source-reliability models | Needs a closer look at provenance-aware trust models |
| T3 | *Vikalpa* is just `undecided` relabelled | Partly true; the difference is reporting and explanation, which is a smaller claim |
| T4 | Influence reduces to weighted causation | **Open — the framework's own stated falsifier** |
| T5 | Grammatical preservation is unnecessary in practice; users never ask | Testable with real reviewers |
| T6 | The whole thing is LegalRuleML plus a Sanskrit front end | Needs the detailed comparison in `related_work.md` §3 |

On T6, which the source calls "the sharpest": "LegalRuleML provides markup for legal rules with defeasibility and provenance, and is genuinely close in several respects. The differences are ambiguity representation, the interpretive confidence axis, derived-not-authored confidence, and *vikalpa* as an outcome. Whether those amount to a different system or an extension is a fair question that should be answered by comparison, not assertion." (§6)

## Architectural Implications

**The core cannot be monotonic, and cannot be OWL.** Because *apavāda* retracts by design and the corpus is "inconsistent *by nature*", the DL assumption set is incompatible; the source states this is "fundamental, not a matter of tooling" (§2.2). What is retained from DL is the obligation to state decidability grounds explicitly, answered in `reasoning_language.md` §7.3.

**Confidence must be derived, never authored.** The MYCIN comparison identifies the hand-assigned certainty factor as "a *known* historical failure mode, not a hypothetical one", and names it as the failure that CHOIR's first governing rule in `confidence_framework.md` §1 exists to prevent (§2.3).

**Explanation must be designed in rather than added.** Recorded as one of the two things CHOIR takes from the expert-system tradition (§2.3), and realised as projection rather than generation (`explainability_framework.md` §1) so that faithfulness holds by construction (§4.5).

**Contexts are derived from source structure, not hand-declared.** This is the stated narrow difference from Cyc microtheories, and it carries a second commitment: "context membership is itself evidence-bearing" (§2.1).

**Relations must declare their semantics.** Woods' 1975 finding is treated as a binding constraint on `reasoning_ontology.md` §4.1 rather than an innovation (§2.1).

**Storage is n-ary and role-labelled, with RDF as an export target.** Driven by kāraka analysis (`knowledge_graph_spec.md` §2.3); RDF "is retained as an export target rather than rejected" (§2.5).

**The neural boundary is invariant I9: neural retrieval, symbolic adjudication.** Justified by the requirement that a conclusion's warrant be traceable, citable and defeasible — "a conclusion whose warrant includes an embedding score cannot be traced, cited, or defeated" (§2.6). The source records the line as revisable "if a form of learned inference emerges that is genuinely auditable".

**Ambiguity cannot be resolved silently at authoring time.** Lowering is blocked until alternatives close (`choir_intermediate_representation.md` §3.1), and each resolution is an object with grounds and an adjudicator (§4.2).

**Influence is second-order and type-enforced.** It "targets an edge and cannot assert a conclusion", enforced in the IR type system (`choir_intermediate_representation.md` §4.6) (§4.6).

**Unresolved conflict is a reportable outcome, not a failure.** *Vikalpa* must carry its own explanation, including which precedence principles were tried and why each was unavailable (`conflict_resolution.md` §8) (§4.4).

**The composition constrains each part.** The dependency chain in §5 forbids specific simplifications by name: scalar collapse of the confidence vector, folding defeat into weights, and forced resolution of legitimate disjunctions.

## Open Questions

From §7 of the source:

1. **Systematic literature search.** "This survey is analytical, drawn from the established landscape rather than from a systematic review. A proper search — particularly in AI and law, computational Sanskrit, and structured argumentation — is required before any external novelty claim is made." (§7)
2. **T4 — the influence falsifier** "should be attempted seriously during Phase 2 corpus work. If it succeeds, the primitive set shrinks and the framework improves." (§7)
3. **Interpretive confidence prior art.** "T2 needs checking against trust and source-reliability models in the semantic web and multi-agent literature." (§7)
4. **Is the *pañcāvayava* adoption substantive or presentational?** "It structures the explanation, but a functionally equivalent schema could be defined without the classical framing. The genuine claim is narrower: the classical schema was *already correct* and did not need designing." (§7)
5. **Neuro-symbolic boundary.** "§2.6's hard line is defensible now. Whether it should be revisited if auditable learned inference matures is a live question, not a settled one." (§7)

Additional unresolved items recorded elsewhere in the source:

- **The composition claim is unvalidated.** "This is a design claim, not a theoretical result, and it is unvalidated" — the test in `domain_independence.md` §6 "has not been run" (§5). (Note: the source document records this as not run at time of writing.)
- **T1 is unresolved** — whether the composition is unremarkable is "Plausible; only implementation will show" (§6).
- **T3 is partly conceded** — "*Vikalpa* is just `undecided` relabelled" is "Partly true; the difference is reporting and explanation, which is a smaller claim" (§6).
- **T5 is untested** — whether grammatical preservation matters in practice is "Testable with real reviewers" (§6).
- **T6 is unanswered pending comparison** — the LegalRuleML question "should be answered by comparison, not assertion", via `related_work.md` §3 (§6).
- **Each of the six differences in §4 carries an unrefuted "not novel if" condition**, which the survey did not systematically test against the literature (§4.1–§4.6, §7).

## Related Documents

Documents this source cites:

- [YK-R-001 — Computational Primitive Specification](YK-R-001-computational-primitive-specification.md) — contexts (§3.10), Influence as a primitive (§3.7), and the influence falsifier (§5) that T4 turns on
- [YK-R-002 — Reasoning Ontology](YK-R-002-reasoning-ontology.md) — relation semantics: arity, transitivity, symmetry, inverse (§4.1)
- [YK-R-003 — Knowledge Graph Specification](YK-R-003-knowledge-graph-specification.md) — the reification problem (§2.1), kāraka-driven n-ary relations (§2.3), neural retrieval / symbolic adjudication (§2.5)
- [YK-R-004 — Vedic Reasoning Methodology](YK-R-004-vedic-reasoning-methodology.md) — the *upādhi* apparatus converging on Pollock's typology (§2.1)
- [YK-R-009 — Evidence Model](YK-R-009-evidence-model.md) — correlation clustering (§4), correlation detection from reified inferences (§4.2), two-layer semantics (§5.1)
- [YK-R-010 — Conflict Resolution](YK-R-010-conflict-resolution.md) — *vikalpa* reported with the precedence principles attempted (§8)
- [YK-R-011 — Confidence Framework](YK-R-011-confidence-framework.md) — confidence derived never authored (§1), the interpretive axis (§3.2)
- [YK-R-012 — Explainability Framework](YK-R-012-explainability-framework.md) — explanation as projection (§1), grammatical justification surviving into explanation (§8)
- [YK-R-013 — CHOIR Intermediate Representation](YK-R-013-choir-intermediate-representation.md) — HIR ambiguity and blocked lowering (§3.1), second-order influence typing (§4.6)
- [YK-R-014 — Reasoning Language (CRL)](YK-R-014-reasoning-language-crl.md) — decidability grounds (§7.3)
- [YK-R-015 — Execution Pipeline](YK-R-015-execution-pipeline.md) — RETE (§4.1)
- [YK-R-016 — Domain Independence](YK-R-016-domain-independence.md) — *vikalpa* across five domains (§4), the *pañcāvayava* schema handling defeated conclusions (§5), influence-dominance across domains (§3), and the corpus-load test (§6) the composition claim depends on

Documents this source feeds:

- [YK-R-018 — Related Work Survey](YK-R-018-related-work-survey.md) — named in the source header as what this document feeds, and carrying the detailed LegalRuleML comparison (§3) that T6 defers to

The source header additionally records its dependency as "all prior documents".
