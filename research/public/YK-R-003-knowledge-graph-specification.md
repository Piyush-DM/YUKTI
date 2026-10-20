# Knowledge Graph Specification

| | |
|---|---|
| **Document ID** | YK-R-003 |
| **Source** | `choir/research/phase-1-foundations/knowledge_graph_spec.md` (003) |
| **Series** | CHOIR Research Programme |
| **Revision** | A |
| **Status** | Active |
| **Last Updated** | 2026-08-23 |

## Abstract

This document fixes the shape of CHOIR's knowledge store. It derives three requirements —
statement-level metadata, edges as edge targets, and native n-ary relations — assesses RDF
triples, labelled property graphs, hypergraphs, semantic networks and knowledge graph
embeddings against them, and decides on a typed, directed, role-labelled hypergraph as the
model of record with an LPG projection and an RDF-star export (§1–§3). It specifies node and
hyperedge schemas, an index set chosen for rule matching, and twelve machine-checkable store
invariants (§4–§6).

The source carries the status "Draft for review". This publication is Active: the research
document is drafted but **not** accepted as specification. `choir/research/README.md` records
the programme-level position — "All 18 deliverables drafted. None accepted. Every document is a
hypothesis, per `MANIFESTO.md`" — where `MANIFESTO.md` itself states the underlying formulation
as "[t]reat every computational object as a hypothesis rather than an established truth". The
source document itself does not cite `MANIFESTO.md` for its own status. It records that it
"only fixes the *shape*" (§4.3), that physical realisation is "[n]ot decided here" (§8), and —
in its single citation of `MANIFESTO.md`, which is to scope — that "implementation is
deliberately deferred" (§8).

## Research Question

The source does not label a research question in a dedicated section. Its own framing, stated
at the head of §1, is: "Before comparing storage models, state the requirement that eliminates
most of them." The document therefore sets out to determine which storage model CHOIR's
knowledge graph should use, by first deriving the requirements that decide the question and
then assessing the candidate models against them. §9 restates the same question in the form of
its answer: "Three requirements decide the model."

## Finding

### The three deciding requirements (§1)

The source takes two mandatory structures from `reasoning_ontology.md` §4.2 and a third from
`computational_primitives.md` §3.6:

1. **Every relationship instance carries metadata** — confidence, provenance, context,
   temporal validity. The source stresses the distinction: "Not the relationship *type*; every
   individual *instance*."
2. **Relationships can be targets of other relationships.** "An undercutting defeater attacks
   an inference link. An influence edge modulates another edge's weight."
3. **Relations are natively n-ary.** A śāstric rule condition such as *"Jupiter in a kendra
   counted from the Moon, in a night birth, unaspected by Saturn"* is "a single relational fact
   with four arguments plus a reference frame." Decomposing it into binary edges "does not
   merely add nodes — it destroys the fact that these arguments belong to one assertion, which
   is precisely what the rule matches on."

The stated consequence: any storage model that cannot do all three natively forces an encoding
workaround, "and the workaround will leak into every query, every rule, and every explanation."

### Candidate assessment (§2)

| Model | Verdict as recorded in the source |
|---|---|
| RDF triples (+ OWL) (§2.1) | "Excellent as an **interchange format**. Poor as a working store" |
| Labelled property graph (§2.2) | "Excellent as a **traversal and query projection**. Insufficient as the model of record" |
| Hypergraph (§2.3) | "Correct as the **model of record**" |
| Semantic networks (§2.4) | "Not a candidate; a cautionary requirement" |
| Knowledge graph embeddings (§2.5) | Retrieval only; "Embeddings may propose. They may never conclude." |

**RDF (§2.1).** The source credits RDF with genuine standards, "[d]ecidable description-logic
reasoning over a well-understood fragment", SPARQL, tooling and vocabulary reuse, and formal
semantics, so that "what the graph entails" is a defined question — a property "which almost
nothing else can say". The disqualifying weakness is reification: a triple has no identity. Four workarounds are assessed. Standard reification costs four extra
triples per statement, "[a] 5× blow-up, and the reified statement is not asserted, so
entailment does not flow through it." Named graphs/quads are workable for *context* but "one
slot cannot carry confidence *and* provenance *and* validity interval independently."
Singleton properties "[e]xplode… the vocabulary and break… schema reasoning." RDF-star /
SPARQL-star is called "the modern answer" — it "genuinely fixes requirement 1 and largely fixes
requirement 2", with the caveat that "[i]ts semantics are newer and support is less uniform
than plain RDF", making it "the strongest RDF-family option." n-ary is not native; the standard
workaround is an intermediate event node, "exactly the manual reification that requirement 3
says we will be doing constantly." The verdict rests on the observation that CHOIR's dominant
operation — attaching and querying statement-level metadata — "is the operation RDF makes most
awkward."

**Labelled property graph (§2.2).** Requirement 1 is "native and free"; traversal performance
is excellent "and traversal is what rule matching mostly is." Four weaknesses are recorded. It
has **no formal semantics** — "'What does this graph entail' has no standard answer. Any
inference is application code." The source treats this as an acknowledged cost rather than a
disqualifier on its own, noting the semantics burden lands on CHOIR "which, as it turns out, is
where we want it anyway (§4.3), but it must be a conscious choice." Edges cannot be edge
endpoints, so requirement 2 fails; n-ary needs an intermediate node, so requirement 3 fails;
and property values are typically flat, so "nested metadata gets serialised into strings, which
then cannot be queried."

**Hypergraph (§2.3).** All three requirements are met: requirement 3 natively (the
four-argument condition becomes one hyperedge with roles `{subject: Guru, frame: Candra,
region: kendra, qualifier: night-birth}`); requirement 1 natively "*if* hyperedges have
identity, which in any practical encoding they do"; and requirement 2 follows, since "a
hyperedge with identity can be a participant in another hyperedge." The source adds a
domain-specific argument: "**Role-labelling aligns exactly with kāraka analysis.**" Pāṇini's
kāraka system assigns semantic roles (agent, locus, source, instrument) to participants in a
single action, so "[a] kāraka-analysed śloka *is* a role-labelled hyperedge", making the
mapping from `sanskrit_analysis_pipeline.md` §6 to storage "near-mechanical rather than a lossy
translation." The recorded weaknesses are not minor: "Fewer off-the-shelf engines. No standard
query language. Formal semantics must be supplied. Naive implementations have poor traversal
locality."

**Semantic networks (§2.4).** Quillian and the frame systems are treated as the historical
ancestor whose durable contributions — inheritance hierarchies, typed links, spreading
activation — are already absorbed into the other models. Their known failure, "diagnosed by
Woods in *What's in a Link?*", is named as the one CHOIR must avoid: "**link types with no
defined semantics**." This is why `reasoning_ontology.md` §4.1 forces every relation to declare
arity, transitivity, symmetry and inverse.

**Embeddings and the neural/symbolic boundary (§2.5).** Embeddings are credited with
approximate retrieval, candidate generation, fuzzy paraphrase matching, suggesting plausible
missing links, and clustering near-duplicate rules across recensions. What they cannot do is
"[j]ustify anything": an embedding score "is not evidence in the sense of
`computational_primitives.md` §3.11 — it has no source, no derivation, and no defeater
structure. It cannot be traced, and it cannot be explained beyond 'the vectors were close.'"
The source states the boundary as a hard rule:

> **Neural retrieval, symbolic adjudication.**
> Embeddings may propose. They may never conclude.
>
> Permitted: candidate generation, deduplication proposals, search ranking, alignment
> suggestions, anomaly flagging for human review.
> Forbidden: contributing to a confidence score, satisfying a rule condition, resolving a
> conflict, or appearing in an explanation as a reason.

Anything an embedding surfaces enters the graph only after a symbolic or human check and
carries provenance recording that its origin was a retrieval suggestion. Without this line,
traceability (001 §3.16) "fails silently — the worst failure mode, because the system still
produces confident-looking explanations."

### The decision (§3)

A **hypergraph of record — typed, directed, n-ary, role-labelled participants, statement-level
metadata, immutable and versioned** — with, in the source's own count, two projections: an LPG
projection for traversal and rule matching, and an RDF-star export for interoperability and
external reasoners. The §3 diagram places a third derived store alongside them — a vector index
for retrieval **only** — and marks all three "derived, rebuildable".

"**Only the hypergraph is authoritative.** Projections are caches: derivable, disposable,
rebuildable. No conclusion may depend on a projection-only fact."

The source argues against itself before concluding. It asks "Why not just use RDF-star and skip
the layer?" and answers that RDF-star "is the closest alternative and a defensible choice",
losing native n-ary role-labelling (requirement 3) — "the requirement most tied to the Sanskrit
pipeline." The layered design keeps RDF-star as an export target "so the interoperability
benefit is retained without paying the encoding cost on every write." Projection lag must be
explicit: a projection carries the version of the record graph it was built from, and queries
against a stale projection are detectable.

### Schemas (§4)

The **Node** schema (§4.1) carries `id` (ContentAddress or NominalID), `kind`, `class`,
multilingual `labels` (IAST, Devanāgarī, English), `attributes` (definitional only, per 001
§3.3), `provenance`, `created`, `version`, `supersedes` and `status`. The source draws
attention to an omission: "no `state` field. States are time-indexed and therefore modelled as
hyperedges with validity intervals, not as node properties. Putting mutable state on nodes is
the single most common way graph systems lose their temporal audit trail."

The **Hyperedge** schema (§4.2) is called "the unit that matters". It carries `relation` (from
the seven families), `participants` as `{role, target, optional}` where `target` may be a
`NodeID` **or** a `HyperedgeID`, `arity`, `polarity`, `modality`
(`asserts|indicates|obliges|permits|forbids|requires`), the context reference, three time
fields (`valid_time`, `decision_time`, `transaction_time`), `confidence` marked "DERIVED, never
authored", `provenance`, `evidence`, `defeated_by` ("marked, never deleted"), `derives_from`
(the traceability closure), `version` and `status`.

The source justifies each field against a named requirement:

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

**Semantics are an acknowledged debt (§4.3).** "Choosing a hypergraph means no inherited formal
semantics." The obligation is discharged elsewhere — in `reasoning_language.md` §7, which fixes
the entailment relation over this structure (defeasible, non-monotonic, with a well-founded
defeater ordering). "This document only fixes the *shape*; the meaning is specified there.
Storing without defined semantics is the Woods failure of §2.4 and is not acceptable."

### Indexing (§5)

Indexes are chosen for rule matching, "not analytics": class extension (`class → nodes`),
role-participation (`(relation, role, target) → hyperedges`), context, a temporal interval tree
over `valid_time` (serving daśā windows among others), provenance (`source_locus → objects`),
content address (dedup and independent-attestation detection), defeater (`target →
exceptions`), and a vector index marked "Retrieval **only** (§2.5)". The role-participation
index is identified as the hot path: "rule conditions are patterns over `(relation, role,
target)` triples, and matching is intersection over these postings lists."

### Invariants (§6)

Twelve machine-checkable invariants, stated as the properties the store must maintain and
intended to populate the currently empty `choir/ontology/relationship_validation.md`:

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

The source singles out I9 as fragile in practice: "It is easy to state and easy to violate
accidentally the first time someone wants 'just a little' similarity in a score."

### Worked example (§7)

The core Gajakesarī condition — *Jupiter situated in a kendra counted from the Moon* — is
encoded both ways. As binary triples it takes six triples plus an intermediate node, "and the
fact that these belong to one assertion is implicit"; the source annotates the RDF sketch with
"`# confidence? provenance? context? → reify again, or lose them`". As one role-labelled
hyperedge the assertion is a single object with metadata attached directly: relation
`choir:core/PositionalRelation#occupies-region`, arity 3, modality `indicates`, context
`ctx:{ tradition: parāśara, chart: rāśi, application: jātaka }`, and participants

- `kartṛ` → `jyotisha:graha/Guru` (the situated one)
- `adhikaraṇa` → `jyotisha:region/Kendra` (the locus)
- `apādāna` → `jyotisha:graha/Candra` (the reckoning point)

"The roles are the kāraka labels recovered by the Sanskrit pipeline: `kartṛ` (agent / situated
entity), `adhikaraṇa` (locus), `apādāna` (point of reckoning, realised by the ablative
*candrāt*). The grammatical analysis survives into storage rather than being flattened away —
which is what makes the explanation able to say *why* the Moon is the reference frame and not
the subject." The example is developed fully in `canonical_shloka_analysis.md`.

## Architectural Implications

The source names the DAALE boundaries it touches: `daale/ontology/relationships.py` and
`evidence.py`.

- **Single source of truth.** Only the hypergraph is authoritative; the LPG projection, the
  RDF-star export and the vector index are caches. No conclusion may depend on a
  projection-only fact (§3). Invariant I10 makes projection lag detectable rather than silent.
- **CHOIR must supply its own formal semantics.** The choice of a hypergraph forfeits any
  inherited entailment relation. The source records this as a non-optional debt discharged in
  `reasoning_language.md` §7 (§4.3, §9), not as something this document settles.
- **Kāraka analysis survives into storage.** Role-labelled participants mean the grammatical
  analysis produced by `sanskrit_analysis_pipeline.md` §6 is preserved rather than flattened,
  "which is what keeps grammatical justification available at explanation time" (§9).
- **A hard neural/symbolic boundary.** Embeddings propose, never conclude; enforced by invariant
  I9 (§2.5, §9). Anything an embedding surfaces requires a symbolic or human check and carries
  provenance recording its retrieval origin.
- **Time and state modelling.** States are hyperedges with validity intervals, not node
  properties (§4.1), and every hyperedge carries three time fields for tri-temporal audit
  (001 §3.17).
- **Non-destruction and traceability become storage-level checks.** I5 (defeated objects marked,
  never removed) and I6 (`derives_from` closure acyclic) turn the invariants of 001 §3.11 and
  §3.16 into machine-checkable acceptance criteria on the store (§6).
- **Indexing follows rule matching, not analytics** (§5), with `(relation, role, target)` as the
  core match primitive.

## Open Questions

The source records five open items (§8), plus further unresolved matter elsewhere:

1. **Physical realisation.** A hypergraph can be implemented over a relational store, an LPG
   with a strict reification convention, or a dedicated engine. "Not decided here; the logical
   model is the commitment, and per `MANIFESTO.md` scope, implementation is deliberately
   deferred."
2. **Context inheritance in queries.** Whether a query scoped to a specific context should
   automatically see facts from more general contexts (lattice-upward closure) is "a semantics
   question with real performance consequences. Deferred to `reasoning_language.md`."
3. **Content addressing and near-duplicates.** Hashing canonical form unifies exact
   restatements; paraphrases across recensions will not unify. Whether normalisation should be
   aggressive enough to unify them — "at the risk of merging genuinely different rules — is
   unresolved, and interacts with `rule_extraction_framework.md` §7."
4. **Retraction versus defeat.** I5 forbids deletion, but a rule extracted in error (a mis-parse,
   not a defeat) differs from a rule defeated by an exception. "Both are currently `status`
   values; whether they need different machinery is open."
5. **Projection consistency model.** Whether projections must be transactionally consistent with
   the record graph or may be eventually consistent "affects whether a rule match can observe a
   torn state."

Additionally recorded as unsettled or as costs carried forward: the formal semantics of the
store are not fixed by this document and remain owed to `reasoning_language.md` §7 (§4.3);
hypergraphs have "[f]ewer off-the-shelf engines[,] [n]o standard query language" and "[n]aive
implementations have poor traversal locality" (§2.3); RDF-star's "semantics are newer and
support is less uniform than plain RDF" (§2.1); and invariant I9 "is the one that requires
ongoing vigilance" (§6). The source's own status line reads "Draft for review", and the
document validates no claim empirically — it presents a design decision and its justification,
with the worked example (§7) as illustration rather than measurement.

## Related Documents

- [YK-R-001 — Computational Primitive Specification](YK-R-001-computational-primitive-specification.md) — declared dependency; supplies requirement 3 (§3.6), evidence (§3.11), and the invariants cited throughout §4 and §6.
- [YK-R-002 — Reasoning Ontology](YK-R-002-reasoning-ontology.md) — declared dependency; supplies the two mandatory structures (§4.2) and the relation-declaration requirement (§4.1) invoked against the Woods failure.
- [YK-R-013 — CHOIR Intermediate Representation](YK-R-013-choir-intermediate-representation.md) — declared downstream ("Feeds").
- [YK-R-015 — Execution Pipeline](YK-R-015-execution-pipeline.md) — declared downstream ("Feeds").
- [YK-R-005 — Sanskrit Analysis Pipeline](YK-R-005-sanskrit-analysis-pipeline.md) — cited for the kāraka mapping (§6) that role-labelled hyperedges preserve (§2.3, §4.2, §7).
- [YK-R-014 — Reasoning Language (CRL)](YK-R-014-reasoning-language-crl.md) — cited as the document that discharges the formal-semantics debt (§7), and as the document open question 2 is deferred to — not resolved by (§4.3, §8).
- [YK-R-008 — Canonical Shloka Analysis (Benchmark)](YK-R-008-canonical-shloka-analysis-benchmark.md) — cited as where the Gajakesarī example is developed fully (§7).
- [YK-R-007 — Rule Extraction Framework](YK-R-007-rule-extraction-framework.md) — cited as interacting with open question 3 on near-duplicate unification (§7 of that document, per §8 here).
- [YK-R-011 — Confidence Framework](YK-R-011-confidence-framework.md) — cited as the source of the three-axis confidence model required by the `confidence` field (§4.2).
