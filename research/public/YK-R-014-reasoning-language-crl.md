# Reasoning Language (CRL)

| | |
|---|---|
| **Document ID** | YK-R-014 |
| **Source** | `choir/research/phase-4-compiler/reasoning_language.md` (014) |
| **Series** | CHOIR Research Programme |
| **Revision** | A |
| **Status** | Active |
| **Last Updated** | 2026-08-23 |

## Abstract

This document specifies CRL — the CHOIR Reasoning Language — as the human-facing surface
syntax for MIR, giving its design constraints, an EBNF grammar, worked examples in three
domains, a type system, an explicit list of what the language cannot express, and a formal
semantics (§1–§8). It discharges a debt recorded in `knowledge_graph_spec.md` §4.3: choosing
a hypergraph means CHOIR inherits no formal semantics and must supply its own (§7). The
source carries the status "Draft for review" and records six open questions of its own,
including that its primary design constraint — reviewability by non-programmers — is untested
(§9).

**Status note.** This document is Active: it is a complete research document, drafted, and
**not accepted as specification**. Per `choir/research/README.md`, every document in this
series is a hypothesis — all 18 deliverables drafted, none accepted. Nothing below should be
read as a governing ruling.

## Research Question

The source frames its task in §1: CRL "is the human-facing surface syntax for MIR. It is what
a scholar or domain expert reads when reviewing an extracted rule, and what they write when
authoring one directly." The question is therefore what surface syntax makes the distinctions
established in Phases 1–3 visible to a domain expert who is not a programmer, while remaining
restricted enough "that termination is provable and every construct maps to a MIR node" (§1).

§7 states a second question the document sets out to answer, inherited as a debt:
`knowledge_graph_spec.md` §4.3 "incurred a debt: choosing a hypergraph means CHOIR inherits no
formal semantics and must supply its own. This section discharges it."

## Finding

### Design constraints and the deliberate cost of verbosity (§1)

The document states five design constraints, in priority order (§1):

1. **Reviewable by a domain expert who is not a programmer.** "The primary reader is a
   Sanskritist, a lawyer, or a clinician."
2. **Lossless round-trip with MIR** for accepted rules.
3. **No construct without a MIR counterpart.** "The surface cannot express more than the IR."
4. **Distinctions that matter must be syntactically visible** — exception type, reference
   frame, modality, completeness. "Anything left implicit will be got wrong."
5. **Confidence cannot be written.** "There is no syntax for a confidence literal."

The source is explicit that CRL is "**not** a general-purpose logic programming language"
(§1), and that constraint 4 is the reason for its verbosity: "`UNDERCUT WHEN` is longer than
`unless`, and the length is the point: an author must state which kind of defeater this is"
(§1).

### Additions to the brief's shape (§2)

The research brief sketched `WHEN … THEN … SUPPORTED_BY … EXCEPT …`. CRL keeps that shape and
adds seven constructs, each traced by the source to a prior phase (§2):

| Addition | Required by |
|---|---|
| `WITHIN` — context scope | Contradiction tolerance (001 §3.10) |
| `FROM` — reference frame | R10; *apādāna* (005 §6.4) |
| `INDICATES` / `ASSERTS` / `OBLIGES` … — modality | Deontic domains (001 §3.9) |
| `UNDERCUT` vs `REBUT` vs `DENY` | Defeater typology (001 §3.12) |
| `COMPLETENESS` | Exception completeness (007 §2.1) |
| `ABSENT … ASSUMING COMPLETE` | *anupalabdhi* observability (009 §3.3) |
| `CONFIDENCE DERIVED` | Confidence is computed (011 §1) |

### Grammar and the syntactic choices it encodes (§3, §3.1)

§3 gives a full EBNF grammar for `RULE` declarations: optional `VERSION`, `SOURCE`, `WITHIN`,
`GIVEN` and `REQUIRES` clauses; a `WHEN` condition; one or more `THEN` conclusions; an
optional `EXCEPT` block; an optional `SUPPORTED_BY`; and a mandatory `CONFIDENCE DERIVED`
before `END`. Conditions admit `AND`, `OR`, `NOT`, parenthesisation, `ANY n OF (…)`,
`ABSENT (…) ASSUMING COMPLETE <ident>`, and `FOR ALL` / `EXISTS` quantification over a domain.
Modality is one of `INDICATES`, `ASSERTS`, `OBLIGES`, `PERMITS`, `FORBIDS`, `REQUIRES_THAT`;
`STRENGTH` is admitted "only if the source states it". Defeaters are `UNDERCUT WHEN`,
`REBUT WHEN … ASSERTING <proposition>`, or `DENY WHEN`, with `COMPLETENESS` one of `KNOWN`,
`LIKELY_INCOMPLETE`, `UNKNOWN`.

§3.1 records four choices and their rationale:

- **`REBUT … ASSERTING <proposition>` requires the proposition.** "A rebutting defeater must
  state what it concludes instead… if the author cannot name the opposite conclusion, the
  defeater is undercutting." Because undercutting is "the śāstric default"
  (`shloka_compiler.md` §6.3), the source holds that "making rebutting the syntactically
  expensive option is the right bias."
- **`FROM` is a clause on the atom, not an argument.** "It corresponds to a distinct kāraka
  and must remain visible in explanations." Writing `house_of(G) FROM M` rather than
  `house_from(G, M)` keeps the reference frame syntactically marked.
- **`ABSENT(...) ASSUMING COMPLETE <domain>`** makes the observability condition unavoidable,
  "enforcing `evidence_model.md` §3.3 at the syntax level rather than by review."
- **`CONFIDENCE DERIVED` is mandatory boilerplate.** "It exists to make the absence of a
  confidence literal conspicuous."

### Worked examples (§4)

**The benchmark rule (§4.1).** The Gajakesari formation is written with
`SOURCE unverified` and the inline annotation `-- E-ATTEST: blocks acceptance`;
`WITHIN application = jātaka, chart = rāśi` (both marked inherited, *prakaraṇa*);
`GIVEN G : Graha = Guru`, `M : Graha = Candra`; `WHEN house_of(G) FROM M IN kendra`;
`THEN INDICATES forms(Gajakesari) NAMED Gajakesari`, with the comment "no STRENGTH clause: the
source states none"; three `UNDERCUT WHEN` defeaters (debilitated, combust, afflicted) and
`COMPLETENESS UNKNOWN`. The source compares this against a naive encoding
(`if jupiter_in_kendra_from_moon and not debilitated: yoga = True`) and states that the naive
version "loses the modality, the reference frame's grammatical status, the exception typing,
the completeness qualification, the context scope, and the source — six distinctions that
Phases 1–3 established as load-bearing" (§4.1).

**Influence as a separate declaration (§4.2).** `INFLUENCE` has `TARGETS`, `WHEN`, `EFFECT`
and `SOURCE` clauses but "no `THEN` clause. It is syntactically incapable of asserting a
conclusion, which enforces `computational_primitives.md` §3.7 in the grammar rather than by
convention."

**`ANY n OF` (§4.3).** The source justifies the construct on explanation grounds: expanded to
disjunctive normal form, `ANY 3 OF` five conditions "is ten conjunctions, and the explanation
would say 'one of ten alternative condition sets was met' rather than 'three of five criteria
were satisfied, namely a, c and d.' The threshold structure is what the reader needs."

**Cross-domain (§4.4).** A legal rule (`limitation_bar`, sourced to `"Limitation Act": "s.5"
ED "2023 consolidation"`) and a clinical rule (`renal_dose_reduction`) are written in the same
grammar. The source concludes: "Three domains, one grammar, zero core changes… both are
modality values, not new syntax. `domain_independence.md` §6 measures exactly this." It also
notes that the legal rule "uses all three defeater types — a *disability* provision denies a
premise, an *acknowledgement* provision rebuts with an explicit opposite conclusion, and the
distinction between them is legally significant."

One textual point is worth recording for a reader checking the grammar against the examples:
§4.4 states that the clinical example's `RECOMMENDS` is a modality value; the `modality`
production given in §3 enumerates `INDICATES`, `ASSERTS`, `OBLIGES`, `PERMITS`, `FORBIDS`,
`REQUIRES_THAT`, and `RECOMMENDS` does not appear in that enumeration. The source does not
comment on the difference.

### Type system (§5)

Types are `Entity` and its subtypes (from L1, refined by L2), `Proposition`, `Ordinal`
("Ranked; **arithmetic prohibited**"), `Measure` (value + unit + scale type), `Interval`
(temporal), and the reference types `ContextRef`, `SourceRef`, `RuleRef`. Type checking is
against the ontology (`reasoning_ontology.md`) and the source lists six errors it catches:
predicate applied to the wrong entity type; a reference frame that is not a valid frame
entity; arithmetic on an ordinal (the `Measure.scale_type` check); a defeater whose stratum
does not decrease; a rebutting defeater without an asserted proposition; and absence without a
completeness declaration. The last two are caught by the grammar, not the type checker, and
the source states this is deliberate: "they are the distinctions most often elided, so they
are made unwriteable rather than merely invalid" (§5).

### What CRL deliberately cannot express (§6)

| Not expressible | Why |
|---|---|
| A confidence literal | Confidence is derived (011 §1) |
| A strength not in the source | Number invention (007 §5.4) |
| Untyped defeat | Type must be stated |
| Absence without completeness | Observability condition (009 §3.3) |
| Context-free rules | Every rule needs a scope (`WITHIN` may be empty but must be considered) |
| Function symbols / term construction | Termination (§7.3) |
| Unrestricted recursion | Termination (§7.3) |
| Side effects | Replay guarantee (012 §4.1) |
| An influence with a conclusion | Influence is second-order (001 §3.7) |

"A language is defined as much by what it forbids as by what it permits. Each row here
corresponds to a failure mode identified in Phases 1–3" (§6).

### Semantics (§7)

**Two layers (§7.1),** mirroring `evidence_model.md` §5.1. Layer 1 is structural: rules and
defeaters induce an argumentation framework in which arguments are inference instances and
attacks are defeater relations, with each argument labelled `in`, `out`, or `undecided`.
Undercutting defeat "removes the *inference*, not the conclusion"; rebutting defeat "is a
symmetric attack between conclusions"; premise defeat "removes an argument's support"; and
"**`undecided` is a real output** and is what surfaces as *vikalpa*"
(`conflict_resolution.md` §7.1). Grounded (sceptical) labelling is the default — "an argument
is `in` only if all its attackers are `out`" — described as "the conservative choice… where
the cost of asserting a defeated conclusion exceeds the cost of withholding one." Layer 2 is
graded: "Only `in` arguments proceed to confidence computation… Defeat is never a weight."

**Non-monotonicity (§7.2).** "Adding a rule can *retract* a conclusion. This is intended: it
is what *apavāda* means." Consequences recorded: conclusions are stamped with the corpus
version that produced them; adding rules triggers re-evaluation of dependents via
`derives_from`; historical conclusions remain replayable under their original version
(`reasoning_ontology.md` §7.3).

**Termination (§7.3)** is guaranteed by four restrictions — no function symbols (so the
Herbrand universe is finite); finite domains for quantifiers; stratification, with recursion
within a stratum prohibited and strata derivable from the corpus's hierarchical structure
(`vedic_reasoning_methodology.md` §5.2); and well-founded defeat, attack strata strictly
decreasing (`choir_intermediate_representation.md` IR7). "Together: evaluation reaches a
fixpoint in bounded steps, and the bound is computable from the corpus." Where a bound is hit
— a truncated defeater chain — "the system reports it rather than returning a result as though
analysis completed" (`conflict_resolution.md` §6, `explainability_framework.md` §2.2).

**Context semantics (§7.4) is unresolved.** Whether a rule scoped to context `c` also sees
facts from more general contexts (lattice-upward closure) "remains open"
(`knowledge_graph_spec.md` §8.2). Two readings are recorded:

| Reading | Effect |
|---|---|
| **Closed** — only exact context | Predictable; may miss genuinely applicable general facts |
| **Upward-closed** — inherits from more general contexts | Natural; risks importing facts that do not hold in the specific context |

"Per `MANIFESTO.md`, both are recorded rather than collapsed. The current inclination is
**closed by default, with explicit `INHERITS` opt-in**, because silent inheritance is exactly
the *anuvṛtti* failure mode (`sanskrit_analysis_pipeline.md` §7) reappearing at execution
time" (§7.4). The source records this as an inclination, not a decision.

### Tooling requirements (§8)

Seven capabilities are listed: round-trip check MIR ↔ CRL (constraint 2); type check against
the ontology (§5); stratification check (§7.3); well-foundedness check (IR7); diff two rule
versions (supersession review); render with source alongside (scholar review,
`canonical_shloka_analysis.md`); and multi-script identifiers, IAST and Devanāgarī
(`reasoning_ontology.md` §7.1). On the last: "Identifiers must accept Devanāgarī and IAST as
display forms over stable opaque identifiers, so a Sanskritist reads *guru* and a lawyer reads
`jyotisha:graha/Guru` for the same object" (§8).

## Architectural Implications

- **The surface cannot outrun the IR.** Constraint 3 fixes CRL as strictly no more expressive
  than MIR, and constraint 2 requires lossless round-trip for accepted rules (§1). Any MIR
  change that adds a node kind is a prerequisite for the corresponding CRL construct, not a
  consequence of one.
- **Certain errors are made unwriteable rather than merely invalid.** Rebutting without an
  asserted proposition, and absence without a completeness declaration, are grammar errors by
  design (§3.1, §5). This moves enforcement of `evidence_model.md` §3.3 and the defeater
  typology out of review and into parsing.
- **Confidence is structurally excluded from authoring.** There is no confidence literal, and
  `CONFIDENCE DERIVED` is mandatory boilerplate (§1, §3.1, §6). Confidence remains the
  responsibility of `confidence_framework.md`; defeat "is never a weight" (§7.1).
- **`INFLUENCE` is second-order by grammar.** Having no `THEN` clause, it cannot assert a
  conclusion, enforcing `computational_primitives.md` §3.7 syntactically (§4.2).
- **Termination is bought by expressive restriction.** No function symbols, finite domains,
  stratification, well-founded defeat (§7.3) — and §6 forbids function symbols and
  unrestricted recursion precisely to preserve this. Any future relaxation removes the
  computable bound.
- **Truncation is reported, not hidden.** Hitting a bound surfaces as a reported condition
  rather than a completed analysis (§7.3), which is a requirement on
  `conflict_resolution.md` and `explainability_framework.md`.
- **`undecided` must be representable downstream.** It is "a real output" surfacing as
  *vikalpa* (§7.1), so consumers of execution results cannot assume a two-valued answer.
- **Non-monotonicity imposes versioning obligations.** Conclusions carry the corpus version;
  dependents are re-evaluated on rule addition; historical conclusions stay replayable (§7.2).
- **Domain independence is claimed and delegated for measurement.** "Three domains, one
  grammar, zero core changes… `domain_independence.md` §6 measures exactly this" (§4.4) — the
  claim is asserted here and tested elsewhere.
- **Tooling is a precondition, not an accessory.** The seven capabilities in §8, including
  multi-script identifiers over stable opaque identifiers, are stated as requirements for CRL
  to serve its intended readers.

## Open Questions

The source records six open questions in §9, plus one unresolved item in §7.4:

1. **Is CRL genuinely reviewable by non-programmers?** "Constraint 1 is the whole point and is
   untested. It needs trial with actual Sanskritists and lawyers, and the answer may force
   simplification that conflicts with constraint 4" (§9.1).
2. **Grounded vs preferred semantics.** §7.1 chooses grounded (sceptical). "Preferred
   semantics would return more conclusions with less certainty. The choice interacts with how
   often *vikalpa* is produced, which is unmeasured" (§9.2).
3. **Context closure.** "§7.4 is unresolved and materially affects both results and
   performance" (§9.3). §7.4 records an inclination — closed by default with explicit
   `INHERITS` opt-in — but not a decision.
4. **Should `INFLUENCE` be part of `RULE`?** "Separating it emphasises second-order status but
   scatters related content across declarations" (§9.4).
5. **Deontic depth.** "`OBLIGES` / `PERMITS` / `FORBIDS` are modality tags, not a full deontic
   logic. Whether obligations need proper deontic semantics — contrary-to-duty conditionals,
   for instance — is unexamined and matters for law" (§9.5).
6. **Temporal operators.** "Only interval predicates are supported. Rules of the form 'within
   30 days of X' are expressible via `Derived` kernels, which hides the temporal structure
   from the reasoner" (§9.6).

The benchmark rule in §4.1 additionally carries `SOURCE unverified` with the annotation
`-- E-ATTEST: blocks acceptance`, and `COMPLETENESS UNKNOWN`; the `INFLUENCE` example in §4.2
is likewise `SOURCE unverified`.

## Related Documents

- [YK-R-013 — CHOIR Intermediate Representation](YK-R-013-choir-intermediate-representation.md) — depends on; CRL is the surface syntax for MIR, and IR7 supplies well-founded defeat (§1, §7.3)
- [YK-R-015 — Execution Pipeline](YK-R-015-execution-pipeline.md) — feeds
- [YK-R-016 — Domain Independence](YK-R-016-domain-independence.md) — feeds; §6 measures the cross-domain claim of §4.4
- [YK-R-001 — Computational Primitive Specification](YK-R-001-computational-primitive-specification.md) — cited at §2 (§3.9, §3.10, §3.12), §4.2 and §6 (§3.7)
- [YK-R-002 — Reasoning Ontology](YK-R-002-reasoning-ontology.md) — cited at §5, §7.2 (§7.3) and §8 (§7.1)
- [YK-R-003 — Knowledge Graph Specification](YK-R-003-knowledge-graph-specification.md) — cited at §7 (§4.3, the semantics debt) and §7.4 (§8.2)
- [YK-R-004 — Vedic Reasoning Methodology](YK-R-004-vedic-reasoning-methodology.md) — cited at §7.3 (§5.2)
- [YK-R-005 — Sanskrit Analysis Pipeline](YK-R-005-sanskrit-analysis-pipeline.md) — cited at §2 (§6.4, *apādāna*) and §7.4 (§7, *anuvṛtti*)
- [YK-R-006 — Shloka Compiler](YK-R-006-shloka-compiler.md) — cited at §3.1 (§6.3, undercutting as śāstric default)
- [YK-R-007 — Rule Extraction Framework](YK-R-007-rule-extraction-framework.md) — cited at §2 (§2.1) and §6 (§5.4)
- [YK-R-008 — Canonical Shloka Analysis (Benchmark)](YK-R-008-canonical-shloka-analysis-benchmark.md) — cited at §8 (scholar review)
- [YK-R-009 — Evidence Model](YK-R-009-evidence-model.md) — cited at §2 and §6 (§3.3), §3.1 (§3.3) and §7.1 (§5.1)
- [YK-R-010 — Conflict Resolution](YK-R-010-conflict-resolution.md) — cited at §7.1 (§7.1, *vikalpa*) and §7.3 (§6)
- [YK-R-011 — Confidence Framework](YK-R-011-confidence-framework.md) — cited at §2 and §6 (§1), and §7.1
- [YK-R-012 — Explainability Framework](YK-R-012-explainability-framework.md) — cited at §6 (§4.1, replay guarantee) and §7.3 (§2.2)
