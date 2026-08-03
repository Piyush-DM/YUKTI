# 003 — Knowledge Graph Specification

**Status:** Draft for review
**Phase:** 1 — Computational Foundations
**Depends on:** `computational_primitives.md`, `reasoning_ontology.md`
**Feeds:** `choir_intermediate_representation.md`, `execution_pipeline.md`
**Reserved DAALE boundaries touched:** `daale/ontology/relationships.py`, `evidence.py`

---

## 1. The requirement that decides everything

Before comparing storage models, state the requirement that eliminates most of them.

From `reasoning_ontology.md` §4.2, two structures are mandatory:

1. **Every relationship instance carries metadata** — confidence, provenance, context,
   temporal validity. Not the relationship *type*; every individual *instance*.
2. **Relationships can be targets of other relationships.** An undercutting defeater
   attacks an inference link. An influence edge modulates another edge's weight.

And from `computational_primitives.md` §3.6, a third:

3. **Relations are natively n-ary.** A śāstric rule condition such as *"Jupiter in a kendra
   counted from the Moon, in a night birth, unaspected by Saturn"* is a single relational
   fact with four arguments plus a reference frame. Decomposing it into binary edges does
   not merely add nodes — it destroys the fact that these arguments belong to one
   assertion, which is precisely what the rule matches on.

Any storage model that cannot do all three natively will force an encoding workaround, and
the workaround will leak into every query, every rule, and every explanation.

---

## 2. Candidate models assessed

### 2.1 RDF triples (+ OWL)

**Shape.** `⟨subject, predicate, object⟩`. Standardised, with formal semantics, a mature
reasoning stack (OWL DL, RDFS entailment), and universal interoperability.

**Strengths.** Genuine standards. Decidable description-logic reasoning over a
well-understood fragment. SPARQL. Enormous tooling and vocabulary reuse. Formal semantics
means "what the graph entails" is a defined question, which almost nothing else can say.

**The disqualifying weakness — reification.** A triple has no identity, so attaching
confidence or provenance to a *statement* requires one of:

- *Standard reification* — four extra triples per statement (`rdf:subject`,
  `rdf:predicate`, `rdf:object`, plus the type). A 5× blow-up, and the reified statement is
  not asserted, so entailment does not flow through it.
- *Named graphs / quads* — a fourth slot, usually used for provenance. Workable for
  *context* (this is how Cyc-style microtheories are typically realised) but one slot
  cannot carry confidence *and* provenance *and* validity interval independently.
- *Singleton properties* — mint a unique predicate per statement. Explodes the vocabulary
  and breaks schema reasoning.
- *RDF-star / SPARQL-star* — the modern answer: quoted triples as first-class terms. This
  genuinely fixes requirement 1 and largely fixes requirement 2. Its semantics are newer
  and support is less uniform than plain RDF, but it is the strongest RDF-family option.

**n-ary.** Not native. The standard workaround is an intermediate "event node"
(the *n-ary relation pattern*), which is exactly the manual reification that requirement 3
says we will be doing constantly.

**Verdict.** Excellent as an **interchange format**. Poor as a working store, because
CHOIR's dominant operation — attaching and querying statement-level metadata — is the
operation RDF makes most awkward.

### 2.2 Labelled property graph (Neo4j, and similar)

**Shape.** Nodes and directed edges, both carrying arbitrary key/value properties.

**Strengths.** Requirement 1 is native and free — edges have properties. Traversal
performance is excellent, and traversal is what rule matching mostly is. Mature operational
tooling. Query languages (Cypher, and the GQL standard) are pleasant for path patterns.

**Weaknesses.**
- **No formal semantics.** "What does this graph entail" has no standard answer. Any
  inference is application code. For a system whose entire value is auditable inference,
  this pushes the semantics burden onto CHOIR — which, as it turns out, is where we want it
  anyway (§4.3), but it must be a conscious choice.
- **Edges cannot be edge endpoints.** Requirement 2 fails. Attacking an inference link
  requires reifying that link as a node — the same workaround, in a different syntax.
- **n-ary** requires an intermediate node. Requirement 3 fails.
- Property values are typically flat; nested metadata gets serialised into strings, which
  then cannot be queried.

**Verdict.** Excellent as a **traversal and query projection**. Insufficient as the model
of record.

### 2.3 Hypergraph

**Shape.** A hyperedge connects *n* nodes, and — in the directed, typed variant — assigns
each participant a **role**.

**Strengths.**
- Requirement 3 is native. The four-argument condition above is one hyperedge with roles
  `{subject: Guru, frame: Candra, region: kendra, qualifier: night-birth}`.
- Requirement 1 is native *if* hyperedges have identity, which in any practical encoding
  they do.
- Requirement 2 follows: a hyperedge with identity can be a participant in another
  hyperedge.
- **Role-labelling aligns exactly with kāraka analysis.** Pāṇini's kāraka system assigns
  semantic roles (agent, locus, source, instrument) to participants in a single action.
  A kāraka-analysed śloka *is* a role-labelled hyperedge. The mapping from
  `sanskrit_analysis_pipeline.md` §6 to storage is then near-mechanical rather than a
  lossy translation.

**Weaknesses.** Fewer off-the-shelf engines. No standard query language. Formal semantics
must be supplied. Naive implementations have poor traversal locality.

**Verdict.** Correct as the **model of record**.

### 2.4 Semantic networks

The historical ancestor (Quillian, and the frame systems that followed). Their durable
contributions — inheritance hierarchies, typed links, spreading activation — are absorbed
into the models above. Their known failure, diagnosed by Woods in *What's in a Link?*, is
exactly the one CHOIR must avoid: **link types with no defined semantics**. This is why
`reasoning_ontology.md` §4.1 forces every relation to declare arity, transitivity,
symmetry and inverse. Not a candidate; a cautionary requirement.

### 2.5 Knowledge graph embeddings

Vector representations of entities and relations (the TransE / RotatE / ComplEx family,
and modern text-embedding hybrids).

**What they are good at.** Approximate retrieval, candidate generation, fuzzy matching of
paraphrases, suggesting plausible missing links, clustering near-duplicate rules across
recensions.

**What they cannot do.** Justify anything. An embedding score is not evidence in the sense
of `computational_primitives.md` §3.11 — it has no source, no derivation, and no defeater
structure. It cannot be traced, and it cannot be explained beyond "the vectors were close."

**The architectural boundary — stated as a hard rule:**

> **Neural retrieval, symbolic adjudication.**
> Embeddings may propose. They may never conclude.
>
> Permitted: candidate generation, deduplication proposals, search ranking, alignment
> suggestions, anomaly flagging for human review.
> Forbidden: contributing to a confidence score, satisfying a rule condition, resolving a
> conflict, or appearing in an explanation as a reason.

Anything an embedding surfaces enters the graph only after a symbolic or human check, and
carries provenance recording that its origin was a retrieval suggestion. Without this line,
traceability (001 §3.16) fails silently — the worst failure mode, because the system still
produces confident-looking explanations.

---

## 3. Decision: hypergraph of record, with two projections

```
                    ┌──────────────────────────────┐
                    │   HYPERGRAPH OF RECORD       │
                    │   typed · directed · n-ary   │
                    │   role-labelled participants │
                    │   statement-level metadata   │
                    │   immutable + versioned      │
                    └──────────────┬───────────────┘
                                   │ derived, rebuildable
                  ┌────────────────┼────────────────┐
                  ▼                ▼                ▼
        ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
        │ LPG          │  │ RDF-star     │  │ Vector       │
        │ projection   │  │ export       │  │ index        │
        │              │  │              │  │              │
        │ traversal,   │  │ interop,     │  │ retrieval    │
        │ rule match   │  │ external     │  │ ONLY         │
        │              │  │ reasoners    │  │              │
        └──────────────┘  └──────────────┘  └──────────────┘
```

**Only the hypergraph is authoritative.** Projections are caches: derivable, disposable,
rebuildable. No conclusion may depend on a projection-only fact. This keeps a single
source of truth while getting query performance from the LPG and interoperability from RDF.

**Why not just use RDF-star and skip the layer?** It is the closest alternative and a
defensible choice. It loses native n-ary role-labelling (requirement 3), which is the
requirement most tied to the Sanskrit pipeline. The layered design keeps RDF-star as an
export target, so the interoperability benefit is retained without paying the encoding cost
on every write.

**Projection lag** must be explicit: a projection carries the version of the record graph
it was built from, and queries against a stale projection are detectable.

---

## 4. Schemas

### 4.1 Node

```
Node ::= {
  id            : ContentAddress | NominalID     # per ontology §7.2
  kind          : PrimitiveKind                  # Entity | Event | Condition | …
  class         : OntologyClass                  # choir:jyotisha/Graha
  labels        : { lang|script → string }       # IAST, Devanāgarī, English…
  attributes    : { name → Value }               # definitional only (001 §3.3)
  provenance    : Provenance
  created       : TransactionTime
  version       : VersionRef
  supersedes    : NodeID?
  status        : active | deprecated | retired
}
```

Note what is **absent**: no `state` field. States are time-indexed and therefore modelled
as hyperedges with validity intervals, not as node properties. Putting mutable state on
nodes is the single most common way graph systems lose their temporal audit trail.

### 4.2 Hyperedge (the unit that matters)

```
Hyperedge ::= {
  id            : ContentAddress
  relation      : RelationType                   # from the 7 families
  participants  : [ { role : RoleName,
                      target : NodeID | HyperedgeID,   # ← edges can be targets
                      optional : bool } ]
  arity         : int
  polarity      : asserted | negated
  modality      : asserts|indicates|obliges|permits|forbids|requires

  context       : ContextRef                     # which scope this holds in
  valid_time    : Interval                       # when it is true of the world
  decision_time : Instant?                       # when it was concluded
  transaction_time : Instant                     # when recorded

  confidence    : ConfidenceRecord               # DERIVED, never authored
  provenance    : Provenance
  evidence      : [ EvidenceRef ]
  defeated_by   : [ ExceptionRef ]               # marked, never deleted
  derives_from  : [ HyperedgeID | InferenceID ]  # traceability closure

  version       : VersionRef
  status        : active | superseded | defeated | retracted
}
```

Every field earns its place against a named requirement:

| Field | Required by |
|---|---|
| `participants[].role` | Kāraka mapping (005 §6); n-ary requirement |
| `target: HyperedgeID` | Second-order influence & undercutting defeat (002 §4.2) |
| `context` | Contradiction tolerance (001 §3.10) |
| Three time fields | Tri-temporal audit (001 §3.17) |
| `confidence` | Three-axis model (011) |
| `defeated_by` | Non-destruction invariant (001 §3.11) |
| `derives_from` | Traceability invariant (001 §3.16) |
| `modality` | Deontic domains; normative constraints (001 §3.9) |

### 4.3 Semantics must be supplied by CHOIR

Choosing a hypergraph means no inherited formal semantics. That obligation is discharged in
`reasoning_language.md` §7, which fixes the entailment relation over this structure
(defeasible, non-monotonic, with a well-founded defeater ordering). This document only
fixes the *shape*; the meaning is specified there. Storing without defined semantics is the
Woods failure of §2.4 and is not acceptable.

---

## 5. Indexing

Rule matching, not analytics, is the dominant workload. Indexes are chosen for it.

| Index | Key | Serves |
|---|---|---|
| Class extension | `class → nodes` | Type-scoped rule matching |
| Role-participation | `(relation, role, target) → hyperedges` | The core match primitive |
| Context | `context → hyperedges` | Scoped evaluation; context-lattice queries |
| Temporal | Interval tree over `valid_time` | Time-scoped queries; daśā windows |
| Provenance | `source_locus → objects` | "Show me everything from this verse" |
| Content address | `hash → object` | Dedup; independent-attestation detection |
| Defeater | `target → exceptions` | Fast defeat checking during adjudication |
| Vector | embedding → candidates | Retrieval **only** (§2.5) |

The role-participation index is the hot path: rule conditions are patterns over
`(relation, role, target)` triples, and matching is intersection over these postings lists.

---

## 6. Invariants

Machine-checkable properties the store must maintain. These populate the empty
`choir/ontology/relationship_validation.md`.

| # | Invariant | Rationale |
|---|---|---|
| I1 | Nodes and hyperedges are immutable once written; change = new version + `supersedes` | Historical re-derivability (002 §7.3) |
| I2 | Every hyperedge has a non-empty `context` | No context-free assertions (001 §3.10) |
| I3 | Every hyperedge has `provenance` naming a source or a kernel | No fact without an origin |
| I4 | `confidence` is present only where a derivation exists; never hand-set | Confidence is computed (001 §3.14) |
| I5 | Defeated objects are marked, never removed | Non-destruction (001 §3.11) |
| I6 | `derives_from` closure is acyclic | Traceability terminates |
| I7 | `subclass-of` and `part-of` closures are acyclic | Ontology check V8 |
| I8 | Every participant role is declared legal for that relation type | Woods requirement |
| I9 | No conclusion's `derives_from` closure contains a vector-index object | Neural/symbolic boundary (§2.5) |
| I10 | Projections declare the record-graph version they were built from | Stale-read detection |
| I11 | Arity matches the relation's declaration | Schema integrity |
| I12 | `valid_time` ⊆ the context's temporal scope | Contexts bound their contents |

I9 is the one that requires ongoing vigilance. It is easy to state and easy to violate
accidentally the first time someone wants "just a little" similarity in a score.

---

## 7. Worked example

Encoding the core Gajakesarī condition (developed fully in `canonical_shloka_analysis.md`):

> *Jupiter situated in a kendra counted from the Moon.*

**As binary triples** — 6 triples plus an intermediate node, and the fact that these belong
to one assertion is implicit:

```
_:c1  rdf:type          jyot:PositionCondition .
_:c1  jyot:subject      jyot:Guru .
_:c1  jyot:referenceFrame jyot:Candra .
_:c1  jyot:region       jyot:Kendra .
# confidence? provenance? context? → reify again, or lose them
```

**As one role-labelled hyperedge** — the assertion is one object, and metadata attaches
directly:

```
Hyperedge {
  id: sha256:9f2c…
  relation: choir:core/PositionalRelation#occupies-region
  participants: [
    { role: kartṛ      , target: jyotisha:graha/Guru    },   # the situated one
    { role: adhikaraṇa , target: jyotisha:region/Kendra },   # the locus
    { role: apādāna    , target: jyotisha:graha/Candra  }    # the reckoning point
  ]
  arity: 3
  modality: indicates
  context: ctx:{ tradition: parāśara, chart: rāśi, application: jātaka }
  valid_time: [chart_epoch, chart_epoch]
  confidence: ⟨extraction: high, interpretive: high, inferential: —⟩
  provenance: ⟨ text: …, locus: …, edition: …, extractor: …, method: … ⟩
  derives_from: [ shloka_parse:… ]
}
```

The roles are the kāraka labels recovered by the Sanskrit pipeline: `kartṛ` (agent /
situated entity), `adhikaraṇa` (locus), `apādāna` (point of reckoning, realised by the
ablative *candrāt*). The grammatical analysis survives into storage rather than being
flattened away — which is what makes the explanation able to say *why* the Moon is the
reference frame and not the subject.

---

## 8. Open questions

1. **Physical realisation.** A hypergraph can be implemented over a relational store, an
   LPG with a strict reification convention, or a dedicated engine. Not decided here; the
   logical model is the commitment, and per `MANIFESTO.md` scope, implementation is
   deliberately deferred.
2. **Context inheritance in queries.** Whether a query scoped to a specific context should
   automatically see facts from more general contexts (lattice-upward closure) is a
   semantics question with real performance consequences. Deferred to
   `reasoning_language.md`.
3. **Content addressing and near-duplicates.** Hashing canonical form unifies *exact*
   restatements. Paraphrases across recensions will not unify. Whether normalisation should
   be aggressive enough to unify them — at the risk of merging genuinely different rules —
   is unresolved, and interacts with `rule_extraction_framework.md` §7.
4. **Retraction versus defeat.** I5 forbids deletion, but a rule extracted in error (a
   mis-parse, not a defeat) is different from a rule defeated by an exception. Both are
   currently `status` values; whether they need different machinery is open.
5. **Projection consistency model.** Whether projections must be transactionally consistent
   with the record graph or may be eventually consistent affects whether a rule match can
   observe a torn state.

---

## 9. Summary

- Three requirements decide the model: **statement-level metadata**, **edges as edge
  targets**, and **native n-ary relations**. RDF fails the first two without RDF-star and
  the third always; LPG fails the last two.
- **Decision: a typed, directed, role-labelled hypergraph as the model of record**, with an
  LPG projection for traversal and an RDF-star export for interoperability. Only the
  hypergraph is authoritative.
- Role-labelled participants let **kāraka analysis survive into storage**, which is what
  keeps grammatical justification available at explanation time.
- **Neural retrieval, symbolic adjudication** — embeddings propose, never conclude;
  enforced by invariant I9.
- Choosing a hypergraph means **CHOIR must supply its own formal semantics**; that debt is
  discharged in `reasoning_language.md` §7 and is non-optional.
- Twelve store invariants (I1–I12) give the graph machine-checkable acceptance criteria.
