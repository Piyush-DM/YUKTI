# 013 — CHOIR Intermediate Representation

**Status:** Draft for review
**Phase:** 4 — Compiler Research
**Depends on:** all of Phases 1–3
**Feeds:** `reasoning_language.md`, `execution_pipeline.md`, `domain_independence.md`

---

## 1. What the IR is for

The IR is the interface between everything upstream (source texts, grammar, extraction) and
everything downstream (matching, evidence, conflict, explanation). Every design constraint
established in Phases 1–3 must be expressible in it, or that constraint is lost.

**Three requirements are unusual and drive the whole design:**

| # | Requirement | Source | Consequence |
|---|---|---|---|
| **U1** | **Unresolved ambiguity must be representable** | Natural-language source; 006 §7 | A three-level IR, with ambiguity legal only at the top |
| **U2** | **Every node must reach its source span** | Traceability invariant; 012 §4 | Provenance is structural, not annotational |
| **U3** | **Defeat must be structural, not a weight** | 009 §5.1 | Defeaters target *edges*, not nodes |

U1 is the one no conventional IR has. A compiler IR normally represents a program whose
meaning is determined; CHOIR's front end routinely cannot decide, and its correct behaviour
is to carry the alternatives forward rather than guess.

---

## 2. Three levels

```
┌─────────────────────────────────────────────────────────────────┐
│ HIR — High-level IR                                             │
│   Close to the text. Ambiguity-preserving. Lattice-valued.      │
│   Retains: grammatical analysis, rejected alternatives, spans.  │
│   NOT EXECUTABLE while ambiguities are open.                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │  resolve · canonicalise · dedup
┌──────────────────────────▼──────────────────────────────────────┐
│ MIR — Mid-level IR          ★ THE INTERCHANGE LAYER              │
│   Fully resolved. Canonical. Domain-independent.                 │
│   Content-addressed. This is what portability is tested against. │
│   A legal or clinical front end targets MIR directly.            │
└──────────────────────────┬──────────────────────────────────────┘
                           │  index · compile patterns · order
┌──────────────────────────▼──────────────────────────────────────┐
│ LIR — Low-level IR                                              │
│   Execution-ready. Match networks, indexes, evaluation order.   │
│   Adds nothing semantic; adds back-pointers to MIR.             │
└─────────────────────────────────────────────────────────────────┘
```

### 2.1 What each lowering does

| Lowering | Discards | Preserves | Reversible |
|---|---|---|---|
| HIR → MIR | Rejected readings (moved to provenance); grammatical detail (moved to provenance) | All semantics; all spans | Yes, via provenance |
| MIR → LIR | Nothing semantic | Everything + back-pointers | Yes |

**Nothing is deleted at either step** — rejected alternatives move into provenance rather
than vanishing, because a scholar contesting a reading needs to see what was rejected and
why (`shloka_compiler.md` §7.1).

### 2.2 Why MIR is the interchange layer

MIR is where the domain-independence claim lives. It contains no Sanskrit, no grammar, no
Jyotiṣa vocabulary — only the L1 constructs of `reasoning_ontology.md`. A legal front end
parsing statutes emits MIR; a clinical front end parsing guidelines emits MIR; everything
downstream is shared.

`domain_independence.md` §6 measures portability as *the number of MIR schema changes
required to onboard a new domain*. Target: zero.

---

## 3. HIR

### 3.1 The ambiguity node

The construct that distinguishes CHOIR's IR from a conventional one.

```
Ambiguity ::= {
  id            : AmbiguityID
  span          : SourceSpan                   # U2
  kind          : segmentation | morphology | compound_type
                | sense | attachment | scope | modality
  alternatives  : [ {
      reading   : HIRSubtree
      score     : Graded
      evidence  : [ what favours this reading ]
      consequence: string                      # what changes if chosen
  } ]
  status        : open | resolved | contested
  resolution    : {
      chosen    : index
      by        : automatic | AgentRef
      grounds   : string                       # REQUIRED for human resolution
      timestamp
      cache_key : hash                         # for structural reuse
  }?
}
```

**Propagation rule.** Any HIR node whose construction depended on an open ambiguity carries
a reference to it. A rule with open ambiguities:

- ✅ may be inspected, listed, discussed, counted
- ✅ may be queued for adjudication
- ❌ **may not be lowered to MIR**
- ❌ may not execute

`contested` is distinct from `open`: it means adjudication occurred and produced a genuine
disagreement (`rule_extraction_framework.md` §5.1 step 5). Contested ambiguities **do**
lower to MIR — as multiple context-scoped rules, which then produce *vikalpa* at execution.

### 3.2 HIR node set

| Node | Carries |
|---|---|
| `SourceText` | Attested text, edition, locus, variants |
| `Token` | Surface form, span, morphological lattice |
| `Compound` | Constituents, type lattice, head |
| `Parse` | Dependency structure, score |
| `KārakaFrame` | Role assignments (→ becomes hyperedge roles) |
| `ScopeBinding` | *Anuvṛtti* resolution: what was inherited, from where |
| `Proposition` | Typed predicate, pre-canonicalisation |
| `RuleDraft` | Condition/conclusion split, exceptions, modality |
| `Ambiguity` | §3.1 |
| `Diagnostic` | Code, level, message |

The grammatical nodes exist so the explanation layer can answer *"why is the Moon the
reference frame?"* with the kāraka analysis (`explainability_framework.md` §8). They are
dropped at MIR lowering but retained in provenance.

---

## 4. MIR — the core

### 4.1 Rule

```
MIRRule ::= {
  id              : ContentAddress            # hash of canonical form
  version         : VersionRef
  supersedes      : RuleID?

  context         : ContextExpr               # §4.4
  variables       : [ { name, type, binding? } ]
  preconditions   : [ Constraint ]            # applicability gate
  conditions      : ConditionExpr             # §4.2
  conclusions     : [ Conclusion ]            # §4.3
  exceptions      : [ ExceptionRef ]          # attached to the INFERENCE edge
  exception_completeness : known|likely_incomplete|unknown

  evidence_class  : primary|corroborating|weak_indication
  independence_key: IndependenceKey           # 009 §4.2

  provenance      : Provenance                # includes HIR back-pointer + spans
  confidence      : { extraction, interpretive }   # derived; inferential comes later
  status          : draft|reviewed|accepted|contested|retired
}
```

### 4.2 Condition algebra

```
ConditionExpr ::=
    Atom( predicate, args, frame? )
  | And( ConditionExpr… )
  | Or( ConditionExpr… )
  | Not( ConditionExpr )
  | NOf( k, ConditionExpr… )              -- at least k of n
  | Threshold( measure, op, value )
  | ForAll( var, domain, ConditionExpr )
  | Exists( var, domain, ConditionExpr )
  | Absent( ConditionExpr, completeness )  -- anupalabdhi; §4.6
  | Derived( kernel, version, args )       -- computed fact
```

**`NOf`** is present because śāstric and institutional rules routinely say "any three of
these five." Encoding that as a disjunction of conjunctions is exponential and destroys the
structure the explanation needs.

**`frame?` on `Atom`** is the reference-frame parameter (R10). It is a first-class slot, not
an extra argument, because it is a distinct kāraka (*apādāna*) and must remain visible in
explanations.

**`Absent`** carries its completeness declaration inline — absence-reasoning is inadmissible
without it (`evidence_model.md` §3.3), so the type system enforces the condition rather than
leaving it to convention.

### 4.3 Conclusion

```
Conclusion ::= {
  proposition   : Proposition
  modality      : indicates | asserts | obliges | permits | forbids | requires
  polarity      : positive | negative
  strength      : Ordinal?          -- from the source ONLY; null is normal
  named_result  : EntityRef?        -- nāmadheya
  scale_type    : ordinal | interval | ratio    -- when strength present
}
```

`strength: null` is the normal case and must not be defaulted to a number
(`rule_extraction_framework.md` §5.4). `scale_type` is carried so that downstream arithmetic
on ordinals is detectable as the category error it is
(`reasoning_ontology.md` §3.1).

### 4.4 Context

```
ContextExpr ::= {
  tradition       : TraditionRef?
  application     : ApplicationRef?
  frame           : EntityRef?           -- default reference frame
  granularity     : GranularityRef?
  jurisdiction    : JurisdictionRef?     -- L2 may add dimensions
  temporal        : Interval?
  purpose         : [ PurposeRef ]       -- empty = unrestricted
  comparability   : comparable | incomparable_with: [ContextRef]
}
```

**`comparability` is the field that prevents the false-conflict flood.** Marking Parāśara and
Jaimini contexts mutually incomparable stops the detector reporting cross-school differences
as contradictions (`conflict_resolution.md` §4) — the single highest-volume source of
spurious conflict in this corpus. The same field separates jurisdictions in law and
populations in medicine.

### 4.5 Exception

```
Exception ::= {
  id, version
  type          : rebutting | undercutting | premise
  target        : RuleID | InferenceEdgeID       -- U3: targets an EDGE
  condition     : ConditionExpr
  stratum       : int                             -- well-foundedness
  source        : Provenance
  excepted_by   : [ ExceptionRef ]                -- exceptions to exceptions
}
```

**`target` may be an inference edge.** This is U3 and it is why the storage model is a
hypergraph (`knowledge_graph_spec.md` §2): an undercutting defeater attacks the *link*, not
the conclusion. Representing defeat as a weight on the conclusion makes undercutting and
rebutting indistinguishable, which manufactures negative conclusions the corpus never
asserted.

**`stratum`** enforces the well-foundedness requirement (`conflict_resolution.md` §6): an
exception may attack only lower strata. Derivable from the *utsarga/apavāda* structure, since
an *apavāda* is by construction more specific than what it restricts.

### 4.6 Influence — second-order by construction

```
Influence ::= {
  id
  target        : InferenceEdgeID | RuleID    -- an EDGE, always
  effect        : strengthens | weakens | cancels
  magnitude     : Ordinal?
  condition     : ConditionExpr
  source        : Provenance
}
```

The type signature enforces `computational_primitives.md` §3.7: influence modulates an
existing relation and cannot produce one. Jupiter's exaltation cannot accidentally be
modelled as forming the yoga, because `Influence` has no way to assert a conclusion.

This is a good example of a Phase 1 distinction surviving into the type system rather than
remaining a convention.

### 4.7 Canonical form

MIR content addressing requires a canonical serialisation:

1. Variables α-renamed to positional canonical names
2. Commutative operands (`And`, `Or`) sorted by content hash
3. Nested same-operator nodes flattened
4. Condition forms normalised to a preferred equivalent
5. Context fields ordered; absent fields omitted (not nulled)
6. Provenance **excluded** from the hash

Point 6 is what makes independent attestation detectable: two verses stating the same rule
hash identically and unify into one rule with two provenance records
(`evidence_model.md` §4.3). Canonicalisation is deliberately **conservative** — only exact
canonical-form identity unifies (`rule_extraction_framework.md` §7.1), because over-merging
silently destroys an exception or a conflict.

---

## 5. LIR

Adds no semantics. Adds execution structure.

```
LIRRule ::= {
  mir_ref         : RuleID                    -- back-pointer, always
  match_network   : DiscriminationNetwork     -- compiled condition patterns
  index_keys      : [ IndexKey ]
  kernel_deps     : [ { kernel, version } ]   -- pinned for replay
  stratum         : int                       -- evaluation order
  defeater_hooks  : [ ExceptionRef ]
  cost_estimate   : int                       -- match ordering
}
```

**`kernel_deps` version pinning** is required by the replay guarantee
(`explainability_framework.md` §4.1). A conclusion that depended on an ephemeris computation
must record *which* ephemeris, at which version, or it cannot be reproduced.

**`stratum`** is the evaluation order derived from the rule dependency graph, which is what
makes termination provable (`reasoning_language.md` §7.3).

---

## 6. Metadata: structural, not annotational

Every MIR object carries the same metadata envelope. It is part of the type, not an optional
attachment — U2 requires it.

```
Envelope ::= {
  provenance : { source, locus, edition, span, extractor, method,
                 hir_ref, adjudicator? }
  context    : ContextRef
  temporal   : { valid_time, transaction_time, decision_time? }
  confidence : ConfidenceVector          -- derived; never authored
  trace      : { derives_from: [ ObjectID ] }
  version    : VersionRef
  status     : lifecycle state
}
```

Making this structural rather than optional is what prevents the traceability invariant from
degrading. An object that *could* omit provenance eventually will.

---

## 7. Worked example — Gajakesarī through all three levels

From `canonical_shloka_analysis.md`.

### 7.1 HIR (abridged)

```
RuleDraft {
  span: [0..46]
  scope_bindings: [
    { var: application, value: jātaka, from: section_head,
      weight: prakaraṇa }                     -- reduced weight, 010 §5.2
    { var: chart, value: rāśi, from: section_head, weight: prakaraṇa }
  ]
  kāraka_frame: {
    kartṛ:      Token(jīve)      → Guru
    adhikaraṇa: Compound(kendragata)
    apādāna:    Token(candrāt)   → Candra      -- REFERENCE FRAME
  }
  conditions: LocativeAbsolute( kendragate, jīve, frame: candrāt )
  conclusions: [ Nāmadheya( Gajakesari ) ]
  ambiguities: [ A1 resolved, A2 resolved, A3 resolved, A4 resolved ]
  diagnostics: [ E-ATTEST, W-VARIANT ]
}
```

All four ambiguities are resolved, so lowering is permitted. `E-ATTEST` does **not** block
lowering — it blocks *corpus admission*. The rule can exist in MIR with `status: draft`.

### 7.2 MIR

```
MIRRule {
  id: sha256:<canonical>
  context: {
    application: jātaka          -- inherited; weight recorded in provenance
    chart: rāśi                  -- inherited
    frame: jyotisha:graha/Candra -- STATED (apādāna)
    purpose: []                  -- unrestricted; resolved at query time
    comparability: comparable
  }
  variables: [ {G, Graha, Guru}, {M, Graha, Candra} ]
  preconditions: [ defined(position(G)), defined(position(M)) ]
  conditions:
    Atom( occupies_region,
          args: [G, kendra_houses],
          frame: M )                       -- frame is a first-class slot
  conclusions: [ {
    proposition: forms(jyotisha:yoga/Gajakesari)
    modality: indicates
    polarity: positive
    strength: null                          -- NOT invented
  } ]
  exceptions: [ ex_debilitated, ex_combust, ex_afflicted ]
  exception_completeness: unknown
  confidence: { extraction: moderate, interpretive: moderate-high }
  status: draft                             -- E-ATTEST
}

Exception ex_debilitated {
  type: undercutting
  target: <the INFERENCE EDGE of MIRRule>   -- U3, not the conclusion
  condition: Atom( debilitated, [G] )
  stratum: 1
}

Influence exalted {
  target: <the INFERENCE EDGE>              -- second-order
  effect: strengthens
  condition: Atom( exalted, [G] )
}
```

Note what the types enforce without any convention being relied on: `ex_debilitated` cannot
assert `¬forms(Gajakesari)` because an `Exception` has no conclusion field; `exalted` cannot
form the yoga because an `Influence` has no conclusion field either.

### 7.3 LIR

```
LIRRule {
  mir_ref: sha256:<canonical>
  match_network: [
    α: type(G) = Graha ∧ bound(G, Guru)
    α: type(M) = Graha ∧ bound(M, Candra)
    β: house_from(G, M) ∈ {1,4,7,10}       -- kernel-derived
  ]
  index_keys: [ (occupies_region, kartṛ, Guru) ]
  kernel_deps: [ { house_from, v1 } ]       -- pinned for replay
  stratum: 2                                 -- after position derivation
  defeater_hooks: [ ex_debilitated@1, ex_combust@1, ex_afflicted@1 ]
}
```

---

## 8. Serialisation

| Form | Use | Property |
|---|---|---|
| **Canonical binary** (CBOR-class) | Hashing, storage | Deterministic byte order |
| **JSON** | Interchange, inspection | Human-readable; not hashed |
| **CRL text** | Authoring, review | `reasoning_language.md` |

CRL ↔ MIR must round-trip losslessly for `accepted` rules; HIR-level detail is not
recoverable from CRL and is reached through provenance.

---

## 9. Invariants

| # | Invariant | Enforces |
|---|---|---|
| IR1 | No MIR object exists with an open ambiguity | U1 |
| IR2 | Every MIR object has provenance with a source span | U2 |
| IR3 | Exceptions and influences target edges, never conclusions | U3 |
| IR4 | Confidence is present only with a derivation | 011 §1 |
| IR5 | `strength` non-null only if the source stated it | 007 §5.4 |
| IR6 | `Absent` carries a completeness declaration | 009 §3.3 |
| IR7 | Exception strata strictly decrease along attack chains | 010 §6 |
| IR8 | Content address excludes provenance | 013 §4.7 |
| IR9 | Every LIR kernel dependency is version-pinned | 012 §4.1 |
| IR10 | MIR contains no domain-specific *schema* (vocabulary only) | 016 |
| IR11 | Contexts declare comparability | 010 §4 |
| IR12 | `derives_from` closure is acyclic | Traceability |

IR10 is the domain-independence check, and it is mechanically testable: scan MIR schema
definitions for any identifier in an L2 namespace.

---

## 10. Open questions

1. **Is three levels right?** HIR and MIR are clearly distinct (ambiguity). MIR/LIR could
   arguably merge, since LIR adds no semantics — but the split keeps MIR free of execution
   concerns, which is what makes it a clean portability target.
2. **Condition algebra completeness.** §4.2 covers the constructs seen so far. Deontic
   conditionals, temporal operators beyond intervals, and probabilistic qualifiers are not
   yet represented and may be needed for law and medicine.
3. **Canonicalisation aggressiveness.** Conservative canonicalisation under-merges
   paraphrases. Carried from `rule_extraction_framework.md` §10; it is fundamentally a
   trade between missed attestation and silent destruction of exceptions.
4. **Do contested rules belong in MIR?** §3.1 says yes, as multiple context-scoped rules. The
   alternative — a first-class disjunctive rule node — would make *vikalpa* explicit in the
   IR rather than emergent at execution.
5. **Stratum assignment for cross-text exceptions.** IR7 requires strata; when an exception
   comes from a different text, its stratum depends on unresolved authority questions
   (`conflict_resolution.md` §5.3).
6. **Influence composition.** Multiple influences on one edge need a combination policy. The
   IR represents them; it does not yet say how they combine
   (`confidence_framework.md` §9).
