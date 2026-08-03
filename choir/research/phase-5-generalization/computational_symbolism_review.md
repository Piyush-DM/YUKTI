# 017 — Computational Symbolism Review

**Status:** Draft for review
**Phase:** 5 — Generalization Research
**Depends on:** all prior documents
**Feeds:** `related_work.md`

---

## 1. Purpose, and a warning about novelty claims

This document surveys the symbolic-AI tradition CHOIR sits in, and then does the harder
thing: states precisely **where CHOIR differs, and where it does not**.

The warning first. Almost every individual mechanism in CHOIR exists in the literature:

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

**A project that claimed to have invented any of these would be wrong.** CHOIR's
contribution, if it has one, is in the *composition* and in a small number of requirements
that the literature does not address because its source material does not raise them. §5
states those, and §6 states what would refute the novelty claim.

---

## 2. The tradition

### 2.1 Knowledge representation and ontologies

The line from semantic networks through frames to description logics established the core
apparatus: taxonomies, inheritance, typed relations, formal semantics.

**Woods, *What's in a Link?* (1975)** is the enduring lesson: link types without defined
semantics make a network uninterpretable. CHOIR's response is
`reasoning_ontology.md` §4.1 — every relation declares arity, transitivity, symmetry and
inverse. This is not innovation; it is compliance with a fifty-year-old finding that systems
still routinely violate.

**Cyc's microtheories** deserve particular note: contexts that partition assertions so that
globally inconsistent knowledge remains locally consistent. This is the same insight as
`computational_primitives.md` §3.10, and Cyc had it decades earlier. CHOIR's difference is
narrow: contexts are **derived from source structure** (recension, school, chapter) rather
than hand-declared, and context membership is itself evidence-bearing.

### 2.2 Description logics and OWL

DLs achieved what earlier KR could not: decidable reasoning with well-understood complexity.
OWL made it standard.

**Why CHOIR cannot simply be OWL:**

| DL assumption | CHOIR requirement |
|---|---|
| **Monotonic** — adding axioms never retracts conclusions | *apavāda* retracts by design |
| **Open-world** throughout | Absence-reasoning needs scoped closure (*anupalabdhi*) |
| Consistency is required; inconsistency is fatal | Corpus is inconsistent *by nature*; contexts localise it |
| No native statement-level metadata | Every statement needs confidence, provenance, validity |
| No graded support | Evidence accumulates |

The monotonicity mismatch is fundamental, not a matter of tooling. A system whose central
phenomenon is defeat cannot have a monotonic core.

**What CHOIR takes from DL:** the discipline of asking what is decidable and why.
`reasoning_language.md` §7.3 answers it explicitly — no function symbols, finite domains,
stratification, well-founded defeat.

### 2.3 Rule engines and expert systems

Production systems (OPS5 and descendants; RETE, Forgy 1982) solved efficient many-rules
matching. Expert systems (MYCIN, and the certainty-factor tradition) attempted graded
conclusions and explanation.

**MYCIN is the most instructive precedent**, because it attempted exactly what CHOIR
attempts — graded confidence plus explanation in an institutional domain — and its
weaknesses are the ones CHOIR must avoid:

| MYCIN limitation | CHOIR response |
|---|---|
| Certainty factors were **hand-assigned** | Confidence is derived, never authored (`confidence_framework.md` §1) |
| CF combination assumed independence | Correlation clustering (`evidence_model.md` §4) |
| No source provenance — rules encoded expert opinion | Every rule traces to a locus in an edition |
| Explanation = rule trace only | Seven mandatory components including alternatives and coverage |
| No conflict machinery beyond ordering | Full precedence and *vikalpa* |

The hand-assigned certainty factor is the failure CHOIR's first governing rule exists to
prevent. It is worth being explicit that this is a *known* historical failure mode, not a
hypothetical one.

**What CHOIR takes:** RETE, which fits well (`execution_pipeline.md` §4.1), and the
observation that explanation must be designed in rather than added.

### 2.4 Non-monotonic reasoning and argumentation

The most directly relevant body of work.

- **Default logic, circumscription, defeasible logic** — formalisms for "normally P, unless."
- **Pollock's defeater typology** — rebutting vs undercutting. CHOIR adopts it wholesale, and
  the striking finding of `vedic_reasoning_methodology.md` §2.1 is that the śāstric *upādhi*
  apparatus draws the same distinction independently.
- **Dung's abstract argumentation (1995)** — arguments and attacks, with labelling semantics.
  CHOIR's Layer 1 is a Dung-style framework, and `undecided` is what surfaces as *vikalpa*.
- **ASPIC+ and structured argumentation** — argument structure plus preferences.
- **Legal argumentation (Prakken, Sartor and others)** — precisely CHOIR's problem in a
  different domain: defeasible rules, precedence principles, burden of proof.

**CHOIR is squarely inside this tradition.** The two-layer semantics
(`evidence_model.md` §5.1) is standard argumentation plus a graded layer. Any claim that
CHOIR invented defeasible reasoning would be false.

### 2.5 Semantic web

RDF, SPARQL, OWL, SHACL, and the reification problem
(`knowledge_graph_spec.md` §2.1). **Wikidata's qualifier and reference model** is the most
relevant practical precedent: every statement carries qualifiers and source references,
which is functionally what CHOIR requires. RDF-star generalises it.

CHOIR's departure is n-ary role-labelled relations, driven by kāraka analysis
(`knowledge_graph_spec.md` §2.3) — and RDF is retained as an export target rather than
rejected.

### 2.6 Neuro-symbolic and embeddings

Current work on combining learned representations with symbolic structure. CHOIR takes a
deliberately conservative position — **neural retrieval, symbolic adjudication**
(`knowledge_graph_spec.md` §2.5) — enforced by invariant I9.

This is not a claim that neuro-symbolic integration cannot work. It is a claim about *this*
system's requirements: a conclusion whose warrant includes an embedding score cannot be
traced, cited, or defeated, and traceability is CHOIR's entire value proposition. The line
may be redrawn if a form of learned inference emerges that is genuinely auditable.

---

## 3. What CHOIR does not claim

Stated plainly, because a novelty claim is only credible alongside an honest account of what
is borrowed:

- Not a new logic. The semantics are standard argumentation plus a graded layer.
- Not a new matching algorithm. RETE.
- Not a new ontology methodology. Standard layering and versioning.
- Not the first system with contexts. Cyc.
- Not the first with statement-level metadata. RDF-star, Wikidata.
- Not the first to compile rules from legal text. LegalRuleML, Catala, and the AI-and-law
  literature generally.
- Not the first to attempt graded confidence with explanation. MYCIN.

---

## 4. Where CHOIR differs

Six differences. Each is stated with what it would take to show it is not novel.

### 4.1 Compilation from canonical text with the grammatical derivation preserved

Existing systems formalise *from* a source; the formalisation is an artefact that replaces
the source. CHOIR keeps the derivation chain intact: manuscript span → sandhi split →
morphology → kāraka role → IR node → conclusion.

The practical consequence is in `explainability_framework.md` §8: the system can answer
*"why is the Moon the reference frame and not the subject?"* with *"because it is in the
ablative, which marks apādāna"*. That is a grammatical justification surviving all the way
to a user-facing explanation.

**Not novel if:** an existing system preserves morphosyntactic derivation into its
executable rules. Computational legal systems generally do not — they formalise from a human
reading of the text.

### 4.2 Ambiguity as a first-class IR citizen

Conventional IRs represent determinate programs. CHOIR's HIR represents *unresolved
alternatives* with their consequences, and lowering is blocked until they close
(`choir_intermediate_representation.md` §3.1).

Existing systems handle source ambiguity by resolving it during formalisation — the
resolution happens in a human's head and is not recorded. CHOIR records it as an object with
grounds and an adjudicator, and reuses it via the resolution cache.

**Not novel if:** an existing rule-extraction system carries unresolved readings into its IR
rather than resolving them at authoring time.

### 4.3 The interpretive confidence axis

`confidence_framework.md` §3.2. The literature has extraction confidence (NLP) and
inferential confidence (evidence). It largely lacks **interpretive confidence** — *does the
tradition agree what this text means?* — because Western KR generally assumes an
authoritative formalisation exists.

For a corpus with a thousand-year commentarial dispute, that assumption fails. The axis is
independently sourced (commentarial agreement, school divergence, *prakaraṇa* vs *śruti*
grounding) and cannot be derived from the other two.

**Not novel if:** an existing framework separates "how confident are we in the reading" from
"how confident are we that the reading is what the authority meant."

This is probably CHOIR's strongest individual claim.

### 4.4 *Vikalpa* — terminating in a legitimate disjunction

Argumentation frameworks produce `undecided`, so the *machinery* exists. What is unusual is
treating it as a **first-class, reportable outcome with its own explanation** — including
which precedence principles were tried and why each was unavailable
(`conflict_resolution.md` §8) — rather than as a failure to conclude.

`domain_independence.md` §4 shows this is needed in all five domains.

**Not novel if:** an existing system reports unresolved conflict as a primary output with a
full account of the attempted resolution.

### 4.5 Explanation as projection, using a traditional proof schema

Two parts:

- **Projection, not generation** (`explainability_framework.md` §1). Faithfulness by
  construction. This is a strong architectural commitment, though not unique — trace-based
  explanation is old.
- **The *pañcāvayava* schema.** Adopting a classical Indian proof form as the explanation
  template is, as far as this survey found, not done elsewhere, and it earns its place on
  merit: it forces the warrant to be exhibited, and it handles defeated conclusions without
  modification (`domain_independence.md` §5).

**Not novel if:** trace-projected explanation with an exhibited warrant is standard — the
projection half may well be; the schema half appears not to be.

### 4.6 Influence as a primitive distinct from causation

`computational_primitives.md` §3.7. Most rule systems provide causal or weighted edges and
express modulation as a weight. CHOIR types influence as **second-order** — it targets an
edge and cannot assert a conclusion, enforced in the IR type system
(`choir_intermediate_representation.md` §4.6).

`domain_independence.md` §3 finds three of five domains influence-dominant and none
causation-only.

**Not novel if:** the distinction collapses — i.e. the falsifier in
`computational_primitives.md` §5 succeeds and influence-heavy corpora encode losslessly as
weighted causation. **This remains open and should be tested seriously.**

---

## 5. The composition claim

The strongest honest statement of CHOIR's position is not about any single mechanism:

> Existing systems address *some* of {source fidelity, ambiguity preservation, interpretive
> uncertainty, structured defeat, legitimate disjunction, projected explanation, domain
> independence}. CHOIR is an attempt to address all of them in one architecture, and each
> constrains the others.

The interlocking is the substance:

- Source fidelity requires preserving grammatical derivation → forces role-labelled n-ary
  storage → forces the hypergraph decision.
- Ambiguity preservation → forces the three-level IR.
- Interpretive uncertainty → forces the confidence vector → forbids scalar collapse.
- Structured defeat → forces two-layer semantics → forbids folding defeat into weights.
- Legitimate disjunction → forbids forced resolution → forces resolution objects that record
  what was unavailable.
- Projected explanation → forces reified inferences → which is what makes correlation
  detection free (`evidence_model.md` §4.2).

That last one is the clearest example of the composition paying off: a mechanism required for
explanation turns out to solve the evidence-independence problem at no additional cost.

**This is a design claim, not a theoretical result, and it is unvalidated.** The correct
posture is that CHOIR is a synthesis whose value depends on whether the composition holds
under real corpus load — which `domain_independence.md` §6 is designed to test and which has
not been run.

---

## 6. Threats to the novelty claim

| # | Threat | Status |
|---|---|---|
| T1 | The composition is unremarkable — each piece integrates trivially | Plausible; only implementation will show |
| T2 | Interpretive confidence is subsumed by existing source-reliability models | Needs a closer look at provenance-aware trust models |
| T3 | *Vikalpa* is just `undecided` relabelled | Partly true; the difference is reporting and explanation, which is a smaller claim |
| T4 | Influence reduces to weighted causation | **Open — the framework's own stated falsifier** |
| T5 | Grammatical preservation is unnecessary in practice; users never ask | Testable with real reviewers |
| T6 | The whole thing is LegalRuleML plus a Sanskrit front end | Needs the detailed comparison in `related_work.md` §3 |

T6 is the sharpest and deserves the direct answer given in `related_work.md`: LegalRuleML
provides markup for legal rules with defeasibility and provenance, and is genuinely close in
several respects. The differences are ambiguity representation, the interpretive confidence
axis, derived-not-authored confidence, and *vikalpa* as an outcome. Whether those amount to a
different system or an extension is a fair question that should be answered by comparison,
not assertion.

---

## 7. Open questions

1. **Systematic literature search.** This survey is analytical, drawn from the established
   landscape rather than from a systematic review. A proper search — particularly in AI and
   law, computational Sanskrit, and structured argumentation — is required before any
   external novelty claim is made.
2. **T4 — the influence falsifier** should be attempted seriously during Phase 2 corpus work.
   If it succeeds, the primitive set shrinks and the framework improves.
3. **Interpretive confidence prior art.** T2 needs checking against trust and
   source-reliability models in the semantic web and multi-agent literature.
4. **Is the *pañcāvayava* adoption substantive or presentational?** It structures the
   explanation, but a functionally equivalent schema could be defined without the classical
   framing. The genuine claim is narrower: the classical schema was *already correct* and did
   not need designing.
5. **Neuro-symbolic boundary.** §2.6's hard line is defensible now. Whether it should be
   revisited if auditable learned inference matures is a live question, not a settled one.
