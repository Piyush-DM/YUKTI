# 014 — Reasoning Language (CRL)

**Status:** Draft for review
**Phase:** 4 — Compiler Research
**Depends on:** `choir_intermediate_representation.md`
**Feeds:** `execution_pipeline.md`, `domain_independence.md`

---

## 1. Purpose and design constraints

CRL — the CHOIR Reasoning Language — is the human-facing surface syntax for MIR. It is what
a scholar or domain expert reads when reviewing an extracted rule, and what they write when
authoring one directly.

It is **not** a general-purpose logic programming language. It is deliberately restricted so
that termination is provable and every construct maps to a MIR node.

**Design constraints, in priority order:**

1. **Reviewable by a domain expert who is not a programmer.** The primary reader is a
   Sanskritist, a lawyer, or a clinician.
2. **Lossless round-trip with MIR** for accepted rules.
3. **No construct without a MIR counterpart.** The surface cannot express more than the IR.
4. **Distinctions that matter must be syntactically visible** — exception type, reference
   frame, modality, completeness. Anything left implicit will be got wrong.
5. **Confidence cannot be written.** There is no syntax for a confidence literal.

Constraint 4 is why CRL is more verbose than it could be. `UNDERCUT WHEN` is longer than
`unless`, and the length is the point: an author must state which kind of defeater this is.

---

## 2. The shape the brief specifies

The research brief sketches:

```
WHEN Condition AND Condition
THEN Inference
SUPPORTED_BY Evidence
EXCEPT Condition
```

CRL keeps this shape and adds what Phases 1–3 established is necessary:

| Addition | Required by |
|---|---|
| `WITHIN` — context scope | Contradiction tolerance (001 §3.10) |
| `FROM` — reference frame | R10; *apādāna* (005 §6.4) |
| `INDICATES` / `ASSERTS` / `OBLIGES` … — modality | Deontic domains (001 §3.9) |
| `UNDERCUT` vs `REBUT` vs `DENY` | Defeater typology (001 §3.12) |
| `COMPLETENESS` | Exception completeness (007 §2.1) |
| `ABSENT … ASSUMING COMPLETE` | *anupalabdhi* observability (009 §3.3) |
| `CONFIDENCE DERIVED` | Confidence is computed (011 §1) |

---

## 3. Grammar

```ebnf
rule        ::= "RULE" ident
                version? source? within?
                given?
                requires?
                "WHEN" condition
                "THEN" conclusion+
                except?
                supported?
                "CONFIDENCE" "DERIVED"
                "END"

version     ::= "VERSION" integer
source      ::= "SOURCE" ( citation | "unverified" )
citation    ::= text ":" locus [ "ED" edition ]
within      ::= "WITHIN" ctxbind ( "," ctxbind )*
ctxbind     ::= ident "=" value
              | "INCOMPARABLE" "WITH" ident+

given       ::= "GIVEN" binding+
binding     ::= ident ":" type [ "=" value ]

requires    ::= "REQUIRES" condition            (* applicability gate *)

condition   ::= disjunction
disjunction ::= conjunction ( "OR" conjunction )*
conjunction ::= primary ( "AND" primary )*
primary     ::= atom
              | "NOT" primary
              | "(" condition ")"
              | "ANY" integer "OF" "(" condition ("," condition)+ ")"
              | "ABSENT" "(" condition ")" "ASSUMING" "COMPLETE" ident
              | quantified

quantified  ::= ("FOR" "ALL" | "EXISTS") ident "IN" domain ":" condition

atom        ::= predicate "(" arg ("," arg)* ")" [ frame ]
              | expr compare expr
frame       ::= "FROM" expr                     (* apādāna — reference frame *)

conclusion  ::= modality proposition [ strength ] [ "NAMED" ident ]
modality    ::= "INDICATES" | "ASSERTS" | "OBLIGES"
              | "PERMITS"   | "FORBIDS" | "REQUIRES_THAT"
strength    ::= "STRENGTH" ordinal              (* only if the source states it *)

except      ::= "EXCEPT" defeater+ [ "COMPLETENESS" completeness ]
defeater    ::= "UNDERCUT" "WHEN" condition [ source ]
              | "REBUT"    "WHEN" condition "ASSERTING" proposition [ source ]
              | "DENY"     "WHEN" condition [ source ]
completeness::= "KNOWN" | "LIKELY_INCOMPLETE" | "UNKNOWN"

supported   ::= "SUPPORTED_BY" evidenceref+
```

### 3.1 Notable syntactic choices

**`REBUT ... ASSERTING <proposition>` requires the proposition.** A rebutting defeater must
state what it concludes instead. This makes the rebutting/undercutting distinction impossible
to fudge: if the author cannot name the opposite conclusion, the defeater is undercutting.
Given that undercutting is the śāstric default (`shloka_compiler.md` §6.3), making rebutting
the syntactically expensive option is the right bias.

**`FROM` is a clause on the atom, not an argument.** It corresponds to a distinct kāraka and
must remain visible in explanations. Writing `house_of(G) FROM M` rather than
`house_from(G, M)` keeps the reference frame syntactically marked.

**`ABSENT(...) ASSUMING COMPLETE <domain>`** makes the observability condition unavoidable.
There is no way to write absence-reasoning without declaring what is assumed complete —
enforcing `evidence_model.md` §3.3 at the syntax level rather than by review.

**`CONFIDENCE DERIVED` is mandatory boilerplate.** It exists to make the absence of a
confidence literal conspicuous. A reader looking for where the number is set finds an
explicit statement that it is computed.

---

## 4. Examples

### 4.1 The benchmark rule

```
RULE gajakesari_formation
  VERSION 1
  SOURCE  unverified                      -- E-ATTEST: blocks acceptance
  WITHIN  application = jātaka,           -- inherited (prakaraṇa)
          chart       = rāśi              -- inherited (prakaraṇa)

  GIVEN   G : Graha = Guru
          M : Graha = Candra

  REQUIRES defined(position(G)) AND defined(position(M))

  WHEN    house_of(G) FROM M IN kendra

  THEN    INDICATES forms(Gajakesari) NAMED Gajakesari
          -- no STRENGTH clause: the source states none

  EXCEPT  UNDERCUT WHEN debilitated(G)
          UNDERCUT WHEN combust(G)
          UNDERCUT WHEN afflicted(G)
          COMPLETENESS UNKNOWN

  SUPPORTED_BY source(unverified)
  CONFIDENCE DERIVED
END
```

Compare with a naive encoding: `if jupiter_in_kendra_from_moon and not debilitated: yoga =
True`. That version loses the modality, the reference frame's grammatical status, the
exception typing, the completeness qualification, the context scope, and the source — six
distinctions that Phases 1–3 established as load-bearing.

### 4.2 An influence (separate declaration)

```
INFLUENCE exaltation_strengthens_gajakesari
  TARGETS  gajakesari_formation           -- targets the RULE's inference edge
  WHEN     exalted(G)
  EFFECT   STRENGTHENS
  SOURCE   unverified
END
```

`INFLUENCE` has no `THEN` clause. It is syntactically incapable of asserting a conclusion,
which enforces `computational_primitives.md` §3.7 in the grammar rather than by convention.

### 4.3 `ANY n OF` — the construct that resists encoding

```
RULE composite_indication
  WHEN  ANY 3 OF ( cond_a(X), cond_b(X), cond_c(X),
                   cond_d(X), cond_e(X) )
  THEN  INDICATES result(X)
  CONFIDENCE DERIVED
END
```

Expanded to disjunctive normal form this is ten conjunctions, and the explanation would say
"one of ten alternative condition sets was met" rather than "three of five criteria were
satisfied, namely a, c and d." The threshold structure is what the reader needs.

### 4.4 Cross-domain — the same constructs, different vocabulary

```
RULE limitation_bar
  VERSION 2
  SOURCE  "Limitation Act": "s.5" ED "2023 consolidation"
  WITHIN  jurisdiction = X, application = civil_claim

  GIVEN   C : Claim

  WHEN    elapsed(accrual_date(C), filing_date(C)) > period(claim_type(C))

  THEN    FORBIDS proceed(C)

  EXCEPT  DENY  WHEN disability_at_accrual(C)      SOURCE "…": "s.28"
          REBUT WHEN acknowledged(C) ASSERTING permits(proceed(C))
                                                  SOURCE "…": "s.29"
          COMPLETENESS LIKELY_INCOMPLETE

  CONFIDENCE DERIVED
END
```

```
RULE renal_dose_reduction
  SOURCE  "Guideline G": "§4.2" ED "v3.1"
  WITHIN  population = adult, setting = inpatient

  GIVEN   P : Patient, D : Drug = drug_x

  WHEN    egfr(P) < 30 AND prescribed(P, D)

  THEN    RECOMMENDS reduce_dose(P, D) STRENGTH moderate

  EXCEPT  UNDERCUT WHEN on_dialysis(P)   SOURCE "Guideline G": "§4.5"
          COMPLETENESS KNOWN

  CONFIDENCE DERIVED
END
```

Three domains, one grammar, zero core changes. The legal example uses `FORBIDS`, the clinical
one `RECOMMENDS`; both are modality values, not new syntax. `domain_independence.md` §6
measures exactly this.

Note the legal rule uses all three defeater types — a *disability* provision denies a
premise, an *acknowledgement* provision rebuts with an explicit opposite conclusion, and the
distinction between them is legally significant.

---

## 5. Type system

| Type | Note |
|---|---|
| `Entity` and its subtypes | From L1; L2 refines |
| `Proposition` | Result of a condition |
| `Ordinal` | Ranked; **arithmetic prohibited** |
| `Measure` | Value + unit + scale type |
| `Interval` | Temporal |
| `ContextRef`, `SourceRef`, `RuleRef` | Reference types |

Type checking is against the ontology (`reasoning_ontology.md`), and it catches real errors:

- Predicate applied to the wrong entity type
- Reference frame that is not a valid frame entity
- **Arithmetic on an ordinal** — the `Measure.scale_type` check
- A defeater whose stratum does not decrease
- Rebutting defeater without an asserted proposition (grammar catches this)
- Absence without a completeness declaration (grammar catches this)

The last two being grammar errors rather than type errors is deliberate: they are the
distinctions most often elided, so they are made unwriteable rather than merely invalid.

---

## 6. What CRL deliberately cannot express

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

A language is defined as much by what it forbids as by what it permits. Each row here
corresponds to a failure mode identified in Phases 1–3.

---

## 7. Semantics

`knowledge_graph_spec.md` §4.3 incurred a debt: choosing a hypergraph means CHOIR inherits
no formal semantics and must supply its own. This section discharges it.

### 7.1 Two-layer semantics

Mirroring the evidence model (`evidence_model.md` §5.1):

**Layer 1 — structural (argumentation).** Rules and defeaters induce an argumentation
framework: arguments are inference instances; attacks are defeater relations. Acceptability
is determined by a labelling — each argument `in`, `out`, or `undecided`.

- Undercutting defeat removes the *inference*, not the conclusion.
- Rebutting defeat is a symmetric attack between conclusions.
- Premise defeat removes an argument's support.
- **`undecided` is a real output** and is what surfaces as *vikalpa*
  (`conflict_resolution.md` §7.1).

Grounded (sceptical) labelling is the default: an argument is `in` only if all its attackers
are `out`. This is the conservative choice and is appropriate where the cost of asserting a
defeated conclusion exceeds the cost of withholding one.

**Layer 2 — graded.** Only `in` arguments proceed to confidence computation
(`confidence_framework.md`). Defeat is never a weight.

### 7.2 Non-monotonicity

Adding a rule can *retract* a conclusion. This is intended: it is what *apavāda* means.
Consequences:

- Conclusions are stamped with the corpus version that produced them.
- Adding rules triggers re-evaluation of dependents (via `derives_from`).
- Historical conclusions remain replayable under their original version
  (`reasoning_ontology.md` §7.3).

### 7.3 Termination

Guaranteed by four restrictions, which is why §6 forbids what it forbids:

1. **No function symbols.** No term construction, so the Herbrand universe is finite.
2. **Finite domains.** Quantifiers range over finite, known extensions.
3. **Stratification.** Rules are assigned strata by dependency; recursion within a stratum is
   prohibited. Derivable from the hierarchical structure of the corpus
   (`vedic_reasoning_methodology.md` §5.2).
4. **Well-founded defeat.** Attack strata strictly decrease (`choir_intermediate_representation.md`
   IR7).

Together: evaluation reaches a fixpoint in bounded steps, and the bound is computable from
the corpus.

**Where a bound is hit** — a truncated defeater chain — the system reports it rather than
returning a result as though analysis completed
(`conflict_resolution.md` §6, `explainability_framework.md` §2.2).

### 7.4 Context semantics

A rule scoped to context `c` is evaluated against facts in `c`. Whether it also sees facts
from more general contexts (lattice-upward closure) remains open
(`knowledge_graph_spec.md` §8.2). Two readings:

| Reading | Effect |
|---|---|
| **Closed** — only exact context | Predictable; may miss genuinely applicable general facts |
| **Upward-closed** — inherits from more general contexts | Natural; risks importing facts that do not hold in the specific context |

Per `MANIFESTO.md`, both are recorded rather than collapsed. The current inclination is
**closed by default, with explicit `INHERITS` opt-in**, because silent inheritance is
exactly the *anuvṛtti* failure mode (`sanskrit_analysis_pipeline.md` §7) reappearing at
execution time.

---

## 8. Tooling requirements

| Capability | Why |
|---|---|
| Round-trip check MIR ↔ CRL | Constraint 2 |
| Type check against the ontology | §5 |
| Stratification check | §7.3 |
| Well-foundedness check | IR7 |
| Diff two rule versions | Supersession review |
| Render with source alongside | Scholar review (`canonical_shloka_analysis.md`) |
| Multi-script identifiers (IAST / Devanāgarī) | `reasoning_ontology.md` §7.1 |

Identifiers must accept Devanāgarī and IAST as display forms over stable opaque identifiers,
so a Sanskritist reads *guru* and a lawyer reads `jyotisha:graha/Guru` for the same object.

---

## 9. Open questions

1. **Is CRL genuinely reviewable by non-programmers?** Constraint 1 is the whole point and is
   untested. It needs trial with actual Sanskritists and lawyers, and the answer may force
   simplification that conflicts with constraint 4.
2. **Grounded vs preferred semantics.** §7.1 chooses grounded (sceptical). Preferred
   semantics would return more conclusions with less certainty. The choice interacts with how
   often *vikalpa* is produced, which is unmeasured.
3. **Context closure.** §7.4 is unresolved and materially affects both results and
   performance.
4. **Should `INFLUENCE` be part of `RULE`?** Separating it emphasises second-order status but
   scatters related content across declarations.
5. **Deontic depth.** `OBLIGES` / `PERMITS` / `FORBIDS` are modality tags, not a full deontic
   logic. Whether obligations need proper deontic semantics — contrary-to-duty conditionals,
   for instance — is unexamined and matters for law.
6. **Temporal operators.** Only interval predicates are supported. Rules of the form "within
   30 days of X" are expressible via `Derived` kernels, which hides the temporal structure
   from the reasoner.
