# CHOIR Intermediate Representation

| | |
|---|---|
| **Document ID** | YK-R-013 |
| **Source** | `choir/research/phase-4-compiler/choir_intermediate_representation.md` (013) |
| **Series** | CHOIR Research Programme |
| **Revision** | A |
| **Status** | Active |
| **Last Updated** | 2026-08-23 |

## Abstract

This document specifies a three-level intermediate representation — HIR, MIR, LIR — that sits between CHOIR's source-text front end and its matching, evidence, conflict, and explanation machinery (§1, §2). Its central claim is that three requirements the source calls **unusual** — representable unresolved ambiguity, structural provenance to a source span, and defeat modelled as an attack on an inference *edge* rather than a weight on a node — drive the whole design, and that MIR is the layer at which the domain-independence claim is tested (§2, §2.2). Of the three, the source claims outright novelty for only one: "U1 is the one no conventional IR has" (§1). The source carries the status **"Draft for review"**; it is a complete research document, drafted, and is **not accepted as specification**. `choir/research/README.md` records the programme-level position — all 18 deliverables drafted, none accepted, every document a hypothesis — citing `MANIFESTO.md`, whose own formulation is to "[t]reat every computational object as a hypothesis rather than an established truth."

## Research Question

The source does not pose its question as an interrogative. Its own framing, in §1, is that "The IR is the interface between everything upstream (source texts, grammar, extraction) and everything downstream (matching, evidence, conflict, explanation)," and that "Every design constraint established in Phases 1–3 must be expressible in it, or that constraint is lost."

The document therefore sets out to answer: what intermediate representation can carry every constraint established in Phases 1–3 without loss — given that CHOIR's front end "routinely cannot decide" the meaning of its source, and that "its correct behaviour is to carry the alternatives forward rather than guess" (§1)?

## Finding

### The three unusual requirements

The document identifies three requirements as the drivers of the whole design (§1):

| # | Requirement | Source | Consequence |
|---|---|---|---|
| **U1** | **Unresolved ambiguity must be representable** | Natural-language source; 006 §7 | A three-level IR, with ambiguity legal only at the top |
| **U2** | **Every node must reach its source span** | Traceability invariant; 012 §4 | Provenance is structural, not annotational |
| **U3** | **Defeat must be structural, not a weight** | 009 §5.1 | Defeaters target *edges*, not nodes |

The source states plainly that "U1 is the one no conventional IR has. A compiler IR normally represents a program whose meaning is determined" (§1).

### Three levels, and what each lowering costs

HIR is close to the text, ambiguity-preserving, lattice-valued, and retains grammatical analysis, rejected alternatives, and spans; it is **not executable while ambiguities are open**. MIR is fully resolved, canonical, domain-independent, and content-addressed — "This is what portability is tested against," and "A legal or clinical front end targets MIR directly." LIR is execution-ready — match networks, indexes, evaluation order — and "Adds nothing semantic; adds back-pointers to MIR" (§2).

| Lowering | Discards | Preserves | Reversible |
|---|---|---|---|
| HIR → MIR | Rejected readings (moved to provenance); grammatical detail (moved to provenance) | All semantics; all spans | Yes, via provenance |
| MIR → LIR | Nothing semantic | Everything + back-pointers | Yes |

"**Nothing is deleted at either step**" — rejected alternatives move into provenance rather than vanishing, "because a scholar contesting a reading needs to see what was rejected and why" (§2.1, citing `shloka_compiler.md` §7.1).

MIR is designated the interchange layer because it is where the domain-independence claim lives: "It contains no Sanskrit, no grammar, no Jyotiṣa vocabulary — only the L1 constructs of `reasoning_ontology.md`" (§2.2). The source records that `domain_independence.md` §6 measures portability as *the number of MIR schema changes required to onboard a new domain*, with a target of zero (§2.2). This is stated as a target, not as a measured result.

### The ambiguity node and its propagation rule

The `Ambiguity` node is described as "The construct that distinguishes CHOIR's IR from a conventional one" (§3.1). Its kinds are `segmentation | morphology | compound_type | sense | attachment | scope | modality`; each alternative carries a reading, a graded score, evidence favouring it, and a statement of *what changes if chosen*. Resolution records `by : automatic | AgentRef`, and `grounds` is marked **REQUIRED for human resolution** (§3.1).

The propagation rule is that any HIR node whose construction depended on an open ambiguity carries a reference to it. A rule with open ambiguities (§3.1):

- may be inspected, listed, discussed, counted
- may be queued for adjudication
- **may not be lowered to MIR**
- may not execute

`contested` is held distinct from `open`: it "means adjudication occurred and produced a genuine disagreement" (`rule_extraction_framework.md` §5.1 step 5). Contested ambiguities **do** lower to MIR — as multiple context-scoped rules, "which then produce *vikalpa* at execution" (§3.1).

The HIR node set retains `SourceText`, `Token`, `Compound`, `Parse`, `KārakaFrame`, `ScopeBinding` (*anuvṛtti* resolution: what was inherited, from where), `Proposition`, `RuleDraft`, `Ambiguity`, and `Diagnostic` (§3.2). The grammatical nodes exist so the explanation layer can answer *"why is the Moon the reference frame?"* with the kāraka analysis (`explainability_framework.md` §8); "They are dropped at MIR lowering but retained in provenance" (§3.2).

### MIR: constructs whose types do the enforcing

The recurring argument of §4 is that distinctions established in earlier phases are made to survive in the type system rather than as convention.

The `MIRRule` record itself (§4.1) carries the rule's context, variables, preconditions, conditions, conclusions, exceptions and completeness declaration, evidence class, independence key, provenance, confidence, and lifecycle status. Its confidence field is annotated `{ extraction, interpretive } -- derived; inferential comes later`: inferential confidence is not represented at MIR in this document and is deferred (§4.1).

- **`NOf(k, …)`** in the condition algebra is present "because śāstric and institutional rules routinely say 'any three of these five.' Encoding that as a disjunction of conjunctions is exponential and destroys the structure the explanation needs" (§4.2).
- **`frame?` on `Atom`** is a first-class slot, not an extra argument, "because it is a distinct kāraka (*apādāna*) and must remain visible in explanations" (§4.2).
- **`Absent`** carries its completeness declaration inline: absence-reasoning — *anupalabdhi* — "is inadmissible without it (`evidence_model.md` §3.3), so the type system enforces the condition rather than leaving it to convention" (§4.2).
- **`strength: null` is the normal case** on a `Conclusion` and "must not be defaulted to a number" (§4.3, citing `rule_extraction_framework.md` §5.4). `scale_type` is carried "so that downstream arithmetic on ordinals is detectable as the category error it is" (§4.3, citing `reasoning_ontology.md` §3.1).
- **`comparability`** on `ContextExpr` "is the field that prevents the false-conflict flood." Marking Parāśara and Jaimini contexts mutually incomparable stops the detector reporting cross-school differences as contradictions — described as "the single highest-volume source of spurious conflict in this corpus." The same field separates jurisdictions in law and populations in medicine (§4.4).
- **`Exception.target` may be an inference edge.** "This is U3 and it is why the storage model is a hypergraph (`knowledge_graph_spec.md` §2): an undercutting defeater attacks the *link*, not the conclusion. Representing defeat as a weight on the conclusion makes undercutting and rebutting indistinguishable, which manufactures negative conclusions the corpus never asserted" (§4.5).
- **`stratum`** enforces well-foundedness — an exception may attack only lower strata — and is "Derivable from the *utsarga/apavāda* structure, since an *apavāda* is by construction more specific than what it restricts" (§4.5).
- **`Influence`** targets an edge, always, and has no way to assert a conclusion. "Jupiter's exaltation cannot accidentally be modelled as forming the yoga, because `Influence` has no way to assert a conclusion." The source calls this "a good example of a Phase 1 distinction surviving into the type system rather than remaining a convention" (§4.6).

### Canonical form and content addressing

MIR content addressing requires a canonical serialisation: α-renaming of variables to positional canonical names; commutative operands of `And`/`Or` sorted by content hash; nested same-operator nodes flattened; condition forms normalised to a preferred equivalent; context fields ordered with absent fields omitted rather than nulled; and **provenance excluded from the hash** (§4.7).

The exclusion of provenance "is what makes independent attestation detectable: two verses stating the same rule hash identically and unify into one rule with two provenance records" (§4.7, citing `evidence_model.md` §4.3). Canonicalisation is described as "deliberately **conservative** — only exact canonical-form identity unifies (`rule_extraction_framework.md` §7.1), because over-merging silently destroys an exception or a conflict" (§4.7). The source records the cost of that choice as an open question (§10.3): conservative canonicalisation under-merges paraphrases.

### LIR and metadata

LIR "Adds no semantics. Adds execution structure" (§5). `kernel_deps` version pinning is required by the replay guarantee: "A conclusion that depended on an ephemeris computation must record *which* ephemeris, at which version, or it cannot be reproduced" (§5, citing `explainability_framework.md` §4.1). `stratum` at LIR is the evaluation order derived from the rule dependency graph, "which is what makes termination provable" (§5, citing `reasoning_language.md` §7.3).

Every MIR object carries the same metadata envelope — provenance, context, temporal (valid, transaction, and optional decision time), a confidence vector marked "derived; never authored", a `derives_from` trace, version, and lifecycle status. "It is part of the type, not an optional attachment — U2 requires it," and "An object that *could* omit provenance eventually will" (§6).

### Worked example: Gajakesarī

The worked example, taken from `canonical_shloka_analysis.md`, carries one rule through all three levels (§7). At HIR, scope bindings for `application: jātaka` and `chart: rāśi` are inherited from the section head at *prakaraṇa* weight — "reduced weight, 010 §5.2" — and the kāraka frame assigns *kartṛ* to `jīve` → Guru, *adhikaraṇa* to `kendragata`, and *apādāna* to `candrāt` → Candra, the reference frame (§7.1).

All four ambiguities are resolved, so lowering is permitted. The HIR draft nonetheless carries two diagnostics, `E-ATTEST` and `W-VARIANT` (§7.1). The source is explicit that `E-ATTEST` "does **not** block lowering — it blocks *corpus admission*. The rule can exist in MIR with `status: draft`" (§7.1); the variant-reading warning `W-VARIANT` is recorded on the example without further comment. The MIR form accordingly carries `status: draft` with the comment `-- E-ATTEST`, `strength: null` with the comment `-- NOT invented`, `exception_completeness: unknown`, and `confidence: { extraction: moderate, interpretive: moderate-high }` (§7.2).

The example's stated point is what the types enforce without convention: "`ex_debilitated` cannot assert `¬forms(Gajakesari)` because an `Exception` has no conclusion field; `exalted` cannot form the yoga because an `Influence` has no conclusion field either" (§7.2).

### Serialisation and invariants

Three serialised forms are specified: canonical binary (CBOR-class) for hashing and storage, with deterministic byte order; JSON for interchange and inspection, human-readable and **not hashed**; and CRL text for authoring and review. "CRL ↔ MIR must round-trip losslessly for `accepted` rules; HIR-level detail is not recoverable from CRL and is reached through provenance" (§8).

Twelve invariants are recorded (§9): no MIR object with an open ambiguity (IR1); every MIR object has provenance with a source span (IR2); exceptions and influences target edges, never conclusions (IR3); confidence present only with a derivation (IR4); `strength` non-null only if the source stated it (IR5); `Absent` carries a completeness declaration (IR6); exception strata strictly decrease along attack chains (IR7); content address excludes provenance (IR8); every LIR kernel dependency is version-pinned (IR9); MIR contains no domain-specific *schema*, vocabulary only (IR10); contexts declare comparability (IR11); the `derives_from` closure is acyclic (IR12).

Of these, the source singles out IR10: it "is the domain-independence check, and it is mechanically testable: scan MIR schema definitions for any identifier in an L2 namespace" (§9). The source does not report having run that scan.

## Architectural Implications

- **MIR is the portability contract.** Because MIR contains only L1 constructs of `reasoning_ontology.md` and no Sanskrit, grammar, or Jyotiṣa vocabulary, a legal front end parsing statutes and a clinical front end parsing guidelines each emit MIR and share everything downstream (§2.2). Onboarding cost is defined as the number of MIR schema changes required, with a target of zero (§2.2), and the check is mechanised as IR10 (§9).
- **The storage model must be a hypergraph.** U3 requires that an exception or influence target an inference *edge*; the source states this directly as the reason for the hypergraph model in `knowledge_graph_spec.md` §2 (§4.5).
- **Ambiguity gates execution, not inspection.** IR1 means the compiler may hold, list, and queue rules that are not yet decidable, but they cannot be lowered or executed (§3.1, §9). The source frames adjudication as a permission — such a rule "may be queued for adjudication," alongside being inspected, listed, discussed, and counted — rather than as a required pipeline stage; what it does require is that a human resolution record `grounds` (§3.1).
- **Corpus admission and IR admission are separate gates.** `E-ATTEST` blocks corpus admission but not lowering; a rule may exist in MIR at `status: draft` (§7.1).
- **Provenance is load-bearing for evidence, not decoration.** Excluding provenance from the content address is what makes independent attestation detectable and permits one rule to hold two provenance records (§4.7); making the envelope structural is what keeps the traceability invariant from degrading (§6).
- **Replay constrains execution-layer design.** Every LIR kernel dependency must be version-pinned, so kernels such as ephemeris computations require stable versioning to satisfy the replay guarantee (§5, IR9).
- **Conflict detection depends on declared context comparability.** IR11 requires contexts to declare comparability; without it, cross-school, cross-jurisdiction, and cross-population differences surface as contradictions (§4.4, §9).
- **Explanation constrains the front end.** Grammatical HIR nodes exist so the explanation layer can answer questions such as the choice of reference frame with kāraka analysis; they are dropped at lowering but retained in provenance (§3.2).

## Open Questions

The source records six open questions (§10), reproduced here in its own terms:

1. **Is three levels right?** HIR and MIR are clearly distinct on ambiguity. MIR and LIR "could arguably merge, since LIR adds no semantics — but the split keeps MIR free of execution concerns, which is what makes it a clean portability target."
2. **Condition algebra completeness.** §4.2 "covers the constructs seen so far. Deontic conditionals, temporal operators beyond intervals, and probabilistic qualifiers are not yet represented and may be needed for law and medicine."
3. **Canonicalisation aggressiveness.** "Conservative canonicalisation under-merges paraphrases." Carried from `rule_extraction_framework.md` §10; "it is fundamentally a trade between missed attestation and silent destruction of exceptions."
4. **Do contested rules belong in MIR?** §3.1 says yes, as multiple context-scoped rules. "The alternative — a first-class disjunctive rule node — would make *vikalpa* explicit in the IR rather than emergent at execution."
5. **Stratum assignment for cross-text exceptions.** IR7 requires strata; "when an exception comes from a different text, its stratum depends on unresolved authority questions" (`conflict_resolution.md` §5.3).
6. **Influence composition.** "Multiple influences on one edge need a combination policy. The IR represents them; it does not yet say how they combine" (`confidence_framework.md` §9).

Further items the source records rather than resolves:

- The document's own status is **"Draft for review."** It is drafted and not accepted as specification; `choir/research/README.md` records that all 18 deliverables are drafted, none accepted, and that every document is a hypothesis, citing `MANIFESTO.md`.
- The portability target of zero MIR schema changes is stated as a target measured elsewhere (`domain_independence.md` §6), not as a result obtained here (§2.2).
- IR10 is stated to be mechanically testable by scanning MIR schema definitions for L2-namespace identifiers; no result of such a scan is reported (§9).
- The MIR confidence vector holds `extraction` and `interpretive` only; the record is annotated "inferential comes later," so inferential confidence is not represented at MIR here (§4.1).
- In the worked example, `exception_completeness` is `unknown`, the confidence vector is `{ extraction: moderate, interpretive: moderate-high }` (§7.2), and the HIR draft carries a `W-VARIANT` diagnostic that the source does not discuss (§7.1).
- HIR-level detail is not recoverable from CRL and is reachable only through provenance; lossless round-tripping is required only for `accepted` rules (§8).

## Related Documents

Depends on all of Phases 1–3 (source header):

- [YK-R-001 — Computational Primitive Specification](YK-R-001-computational-primitive-specification.md) — cited at §4.6 (`computational_primitives.md` §3.7)
- [YK-R-002 — Reasoning Ontology](YK-R-002-reasoning-ontology.md) — cited at §2.2 and §4.3
- [YK-R-003 — Knowledge Graph Specification](YK-R-003-knowledge-graph-specification.md) — cited at §4.5
- [YK-R-004 — Vedic Reasoning Methodology](YK-R-004-vedic-reasoning-methodology.md) — Phase 2 dependency
- [YK-R-005 — Sanskrit Analysis Pipeline](YK-R-005-sanskrit-analysis-pipeline.md) — Phase 2 dependency
- [YK-R-006 — Shloka Compiler](YK-R-006-shloka-compiler.md) — cited at §1 (U1) and §2.1
- [YK-R-007 — Rule Extraction Framework](YK-R-007-rule-extraction-framework.md) — cited at §3.1, §4.3, §4.7, §10.3
- [YK-R-008 — Canonical Shloka Analysis (Benchmark)](YK-R-008-canonical-shloka-analysis-benchmark.md) — source of the worked example, §7
- [YK-R-009 — Evidence Model](YK-R-009-evidence-model.md) — cited at §1 (U3), §4.2, §4.7
- [YK-R-010 — Conflict Resolution](YK-R-010-conflict-resolution.md) — cited at §4.4, §4.5, §7.1, §10.5
- [YK-R-011 — Confidence Framework](YK-R-011-confidence-framework.md) — cited at §9 (IR4) and §10.6
- [YK-R-012 — Explainability Framework](YK-R-012-explainability-framework.md) — cited at §1 (U2), §3.2, §5

Feeds (source header):

- [YK-R-014 — Reasoning Language (CRL)](YK-R-014-reasoning-language-crl.md) — cited at §5 and §8
- [YK-R-015 — Execution Pipeline](YK-R-015-execution-pipeline.md)
- [YK-R-016 — Domain Independence](YK-R-016-domain-independence.md) — cited at §2.2 and §9 (IR10)
