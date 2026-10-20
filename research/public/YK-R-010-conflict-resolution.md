# Conflict Resolution

| | |
|---|---|
| **Document ID** | YK-R-010 |
| **Source** | `choir/research/phase-3-institutional/conflict_resolution.md` (010) |
| **Series** | CHOIR Research Programme |
| **Revision** | A |
| **Status** | Active |
| **Last Updated** | 2026-08-23 |

## Abstract

This document specifies how CHOIR detects, classifies, and resolves disagreement between
rules: a seven-class conflict taxonomy (§3), a context-splitting step applied before any
precedence reasoning (§4), a partial-order precedence scheme drawn from *utsarga/apavāda*,
Pāṇinian metarules and Mīmāṃsā interpretive ordering (§5), well-foundedness requirements for
defeater chains (§6), and six resolution outcomes including *vikalpa* — a terminal
disjunction — and escalation (§7). Its governing commitment is that the system must never
silently pick a winner, and that "unresolved" is a legitimate output (§1).

The source carries the status **Draft for review** and is published here as **Active**: it is
a complete research document that has been drafted but **not accepted as specification**.
`choir/research/README.md` records the programme-level position: "All 18 deliverables
drafted. None accepted. Every document is a hypothesis, per `MANIFESTO.md`." MANIFESTO.md
itself states the underlying formulation as "Treat every computational object as a hypothesis
rather than an established truth."

## Research Question

The source does not state a research question under that heading. It opens (§1) by framing
the problem it addresses: when two rules disagree, most systems pick one, and CHOIR's
commitment is different. The commitment the document sets out to work through is stated
verbatim as:

> **Never silently pick. Every resolution is an inference with its own grounds, its own
> provenance, and its own defeasibility — and "unresolved" is a legitimate output.**

The document's task is therefore to work out what machinery that commitment requires: how
conflicts are detected, what kinds there are, which of them are not really conflicts, what
orderings can decide between rules, when no ordering is available, and what the system should
emit when nothing decides.

## Finding

### The commitment and its two consequences (§1)

Two consequences follow from the governing commitment. First, a resolution is itself a
`Resolution` object, subject to the same machinery as any other inference — resolutions can
be contested, superseded, and defeated. Second, the pipeline must be able to **terminate in a
disjunction** (*vikalpa*, §7). The source's stated reason is that a system that always
returns one answer cannot be faithful to a corpus that genuinely contains unresolved splits,
and that all five reference domains do.

### Detection (§2)

Conflict detection runs **after** saturation, not during rule firing
(`execution_pipeline.md` §4). The stated reason is that precedence depends on the *full* set
of fired rules: a rule may win by specificity against one competitor and lose by source
authority against another, and neither judgement is available mid-match.

The detection condition is three-conjunct:

```
conflict(i₁, i₂)  ⟺  contexts_overlap(i₁.context, i₂.context)
                   ∧ incompatible(i₁.conclusion, i₂.conclusion)
                   ∧ both_undefeated(i₁, i₂)
```

The source notes that all three conjuncts matter: dropping the first produces the
false-conflict flood of §4; dropping the third reports conflicts between an inference and
something already withdrawn.

### Taxonomy (§3)

Seven classes. The source observes that the first three are what people usually mean by
"conflict"; the last four are where real corpora actually cause trouble.

| # | Class | Shape | Example |
|---|---|---|---|
| C1 | **Contradictory** | *P* and *¬P* | One rule indicates a result; another denies it |
| C2 | **Incompatible** | Mutually exclusive, not negations | Two rules assign different exclusive classifications |
| C3 | **Degree** | Same direction, different strength | Both indicate; one strongly, one weakly |
| C4 | **Applicability** | Both claim to govern the same case | General rule and specific rule overlap |
| C5 | **Definitional** | Same term, different definitions | Schools define *kendra* reckoning differently; statutes define "resident" differently |
| C6 | **Temporal** | Rules in force at different times | Superseded statute vs current; earlier vs later recension |
| C7 | **Meta** | Conflicting *resolution* rules | Specificity favours one, recency the other |

Nyāya's *hetvābhāsa* taxonomy is mapped onto this partition as a cross-check (§3.1):
*viruddha* → C1; *satpratipakṣa* → C1/C2 **with no precedence available**, routing to §7;
*asiddha* → premise defeat, not a conflict; *bādhita* → resolved by §5.3; *savyabhicāra* → a
non-discriminating condition, a rule-quality defect. The source characterises the agreement
between the two traditions carefully: that they arrive at nearly the same partition is
"weak but genuine evidence" the partition is natural rather than arbitrary. It does not claim
more.

Two entries in the taxonomy carry explicit qualifications:

- **C3 is not a conflict** (§3.2). It is listed for completeness and then dismissed: two
  rules indicating the same conclusion with different strengths are corroborating evidence,
  handled by aggregation (`evidence_model.md` §5), not by resolution. The source calls
  treating C3 as conflict a common modelling error that generates enormous spurious volume.
- **C5 is the worst** (§3.3), because it is **silent**. Two rules using *kendra* under
  different reckoning conventions do not appear to conflict — they appear to agree, or to
  address different cases, while actually computing different things. Detection requires that
  definitions be first-class, versioned objects with explicit links from every rule that uses
  them (`rule_extraction_framework.md` §2, `cross_references`). The source states flatly that
  a rule referencing a definition by name rather than by versioned identifier **cannot be
  checked for C5 at all**.

### Context splitting comes first, always (§4)

The source's stated position is that **most apparent contradictions are context collisions**.
Two rules that appear to contradict frequently were never meant to co-apply; their scoping
conditions were left implicit in the source — different school, application, chart, or epoch
— and the collision is an artefact of extraction dropping the scope rather than a genuine
disagreement. The procedure is: check whether the contexts actually overlap (if not, record
as disjoint — not a conflict); if they do, check for a missing discriminator (school,
application, epoch, reference frame, granularity); if one is found, re-scope both rules and
record the split as an inference; only otherwise is the conflict genuine and passed to §5.

**Cross-school difference is not conflict** (`vedic_reasoning_methodology.md` §7, R13).
Parāśara and Jaimini rules are different systems, not competitors. The source states that if
the context lattice keeps schools incomparable the detector never reports them as
contradictory, and that this is the single highest-volume source of false conflict in this
corpus. The same pattern is asserted to hold elsewhere: two jurisdictions' statutes do not
conflict; two guidelines for different populations do not conflict; two design codes for
different load cases do not conflict.

The cost of getting this wrong is stated directly: without context splitting, a corpus of
*n* rules from *k* schools generates conflicts roughly proportional to the cross-product, and
the conflict queue becomes unusable.

### Precedence is a partial order (§5)

Precedence is explicitly a **partial order, not a total one**. Incomparability is a real
outcome and leads to §7 rather than to an arbitrary tiebreak (§5, §5.4).

**Structural precedence** (§5.1), applied in this order:

| # | Principle | Classical form | Rule |
|---|---|---|---|
| P1 | **Specificity** | *apavāda* over *utsarga*; *lex specialis* | The rule with the strictly stronger condition wins |
| P2 | **Phase** | *pūrvatrāsiddham* (A. 8.2.1) | Rules in a later designated phase are invisible to earlier ones |
| P3 | **Recency** | *vipratiṣedhe paraṃ kāryam* (A. 1.4.2); *lex posterior* | Where scope is equal, the later rule prevails |
| P4 | **Authority** | *bādha*; *lex superior* | The higher-ranked source prevails (§5.3) |

Two constraints are stated on these. **P1 requires strict containment**: rule A is more
specific than B only if A's condition *entails* B's; two rules with merely *different*
conditions are not ordered by specificity — a distinction the source says is routinely fudged
and that produces wrong resolutions when it is. **P3 is the weakest and is applied last**
among the structural principles; "later" is well-defined for a single text's internal
ordering (Pāṇini's case) and for dated statutes, but is **not** well-defined across
recensions of a text with a contested transmission history
(`vedic_reasoning_methodology.md` §0.3). Where composition order is uncertain, the source
states that P3 is unavailable and "must not be faked".

**Interpretive precedence** (§5.2). Where the conflict concerns what a text *means* rather
than which rule governs, the Mīmāṃsā six-fold ordering is adopted directly:

> *śruti* > *liṅga* > *vākya* > *prakaraṇa* > *sthāna* > *samākhyā*

| Ground | Meaning | Weight |
|---|---|---|
| *śruti* | Direct statement in the text | Highest |
| *liṅga* | Indicatory force of a word | |
| *vākya* | Syntactic connection | |
| *prakaraṇa* | Contextual setting | |
| *sthāna* | Position in the text | |
| *samākhyā* | Name or title | Lowest |

The source records one consequence already in use in Phase 2: an inherited scope condition
(*prakaraṇa*) carries less interpretive weight than a stated one (*śruti*), which is why the
benchmark rule's inherited application scope reduces its interpretive confidence
(`canonical_shloka_analysis.md` §4.4). The document further claims the ordering generalises —
statutory text outranks a marginal note, a guideline's recommendation outranks its
introductory discussion, a contract's operative clause outranks its recitals — and concludes
that the tradition's ordering "turns out to be a general theory of textual authority, not a
parochial one".

**Source authority** (§5.3). The ranking itself is **domain-supplied** (L2 per
`reasoning_ontology.md` §2.1); the *machinery* is core. The source states this separation is
what keeps the engine domain-independent. Example rankings are given for Jyotiṣa (*mūla* text
> classical *ṭīkā* > later commentary > modern exposition), Law, Medicine, Finance, and
Engineering.

The section records an explicit unresolved problem — **the unresolved cross-text problem**:
when text A states a rule and text B states its exception, whether B's exception applies to A
depends on whether B is authoritative *for* A. Within a lineage this is answerable; across
lineages it often is not (`rule_extraction_framework.md` §10.5). Where authority is
undetermined, P4 is unavailable, which the source describes as a common route into §7.

### Defeater chains and well-foundedness (§6)

Exceptions have exceptions (*nīca-bhaṅga* annulling a debilitation-based cancellation);
chains are normal, and the machinery must terminate. Well-foundedness requires that the
attack relation be acyclic and that every chain terminate in an unattacked node, enforced by
three mechanisms: cycle detection at compile time (a cyclic attack set is `E-CYCLE`,
rejected); stratification (exceptions are assigned a level and may attack only lower levels,
derivable from the *utsarga/apavāda* structure since an *apavāda* is by construction more
specific than what it restricts); and a depth bound with reporting — if the bound is hit the
system reports `defeater_chain_truncated` rather than returning a result as if the analysis
completed. The source ties the third to `canonical_shloka_analysis.md` §9.2: the system must
report what it did not evaluate, and "a confident answer that quietly skipped half the
defeater chain is worse than an explicit partial result."

The **meta-conflict regress** (C7) — resolution rules are objects and can themselves conflict
— is stopped by a small set of **stipulated root axioms**: the precedence principles of §5.1
in a fixed order, declared rather than derived. The source's justification is that declaring
them makes the stopping point explicit and contestable rather than hidden in implementation.
It does not claim the ordering is itself justified; see Open Questions.

### Resolution outcomes (§7)

Six outcomes. The source notes that the tradition names three that most engines lack, and
that these are the ones that make honest reporting possible.

| Outcome | Classical | Meaning | Output |
|---|---|---|---|
| **Preempt** | *bādha* | One rule cancels the other | Winner's conclusion; loser recorded as defeated |
| **Restrict** | *apavāda* | The specific carves out from the general | Both retained, scopes adjusted |
| **Conjoin** | *samuccaya* | Both apply together | Both conclusions |
| **Split** | — | Contexts separated (§4) | Both, in disjoint contexts |
| ***Vikalpa*** | *vikalpa* | **Both admissible; neither defeats the other** | **A disjunction, with support for each** |
| **Escalate** | — | Requires human judgement | Queued; no automatic conclusion |

***Vikalpa*** (§7.1) is a **terminal, legitimate state of analysis**: two rules conflict,
precedence is unavailable or incomparable, and the correct output is both alternatives with
their support, not a forced choice. The emitted structure carries each alternative with its
supporting rules and evidence and a decomposed confidence, and a final `Why unresolved` field
recording which precedence principles were tried and why each was unavailable or
incomparable. The source is explicit that this last line is what distinguishes *vikalpa* from
an evasion: "'Unresolved' is only acceptable when the system can say *what it tried*."

The document asserts this is not a Jyotiṣa peculiarity, listing genuine unresolved splits in
Law (a circuit split; two defensible readings of an ambiguous provision), Medicine (two
guideline-supported treatment options of comparable standing), Finance (two permitted
accounting treatments), and Engineering (two acceptable design approaches under the same
code). Its stated conclusion is that a system collapsing these to one answer is not more
useful but less honest, and that the collapse discards information the decision-maker needs.

**Escalation** (§7.2) is required — not merely permitted — when precedence is incomparable
*and* the alternatives have materially different consequences; when a definitional conflict
(C5) is detected; when a defeater chain was truncated; when resolution would rely on an
authority ranking marked uncertain; or when the conflict is between contexts the lattice
marks incomparable (cross-school). The escalation record carries the full conflict analysis
so the human decision is made on the same material the system used, and the human's
resolution is recorded as a `Resolution` object with its grounds, feeding the resolution
cache (`shloka_compiler.md` §7.1).

### The resolution object (§8)

```
Resolution ::= {
  id, version
  conflict          : ConflictRef
  outcome           : preempt|restrict|conjoin|split|vikalpa|escalate
  winner            : InferenceRef?          # absent for vikalpa/split
  grounds           : [ { principle, applied, result } ]   # ALL tried, in order
  principles_unavailable : [ { principle, reason } ]       # ← required
  resolved_by       : automatic | human
  adjudicator       : AgentRef?
  adjudicator_school: string?                # authority is not neutral
  confidence        : derived
  provenance, timestamp
  status            : active | superseded | contested
}
```

`principles_unavailable` is mandatory. The source's reason: recording only the principle that
decided the matter hides whether the resolution was overdetermined (several principles
agreed) or hung on a single contestable ground, and that difference is exactly what a
reviewer needs. `adjudicator_school` is present because in a live tradition the adjudicator is
not a neutral party (`rule_extraction_framework.md` §10.2).

### Worked example (§9)

Two extracted, fired rules: **R1** — *Jupiter in a kendra from the Moon indicates
Gajakesarī*, context `{application: jātaka, chart: rāśi}`, source verse V1; and **R2** —
*Jupiter debilitated withdraws the indication*, same context, source verse V2.

Detection succeeds on all three conjuncts. Classification is **C4 applicability**, not C1 —
the source notes R2 does not assert ¬Gajakesarī, it withdraws R1's warrant, realised as an
undercutting defeater. Context splitting finds no missing discriminator (same school,
application, chart), so the conflict is genuine. Precedence: P1 specificity applies, since
R2's condition (kendra **and** debilitated) entails R1's (kendra) — strict containment, R2
wins; P2 is not applicable (no phase declaration); **P3 is unavailable** because composition
order across these verses is not established; P4 is not reached. The outcome is `restrict`,
identified as *apavāda*, matching the behaviour traced in `canonical_shloka_analysis.md` §9.2.
The recorded `Resolution` lists all three unavailable or unreached principles with reasons and
a confidence of "high — strict containment; single unambiguous principle".

The source closes the example with a negative observation rather than a favourable one: had
P1 not applied — two rules with merely different conditions — P3 would have been unavailable,
P4 would depend on whether V1 and V2 are equally authoritative, and the likely outcome would
be `vikalpa` or escalation. It remarks on "how quickly a plausible variation reaches it".

### Lifecycle (§10)

A conflict moves `detected → classified → split-attempted`, and thence to one of:
`not-a-conflict (disjoint)`, `resolved (automatic)`, `vikalpa (terminal)`, or `escalated`,
with escalation leading to `resolved (human)` or `irreducible`. The source defines
`irreducible` as a real terminal state — a conflict a human has examined and determined
cannot be resolved on available grounds — and distinguishes it from `vikalpa`: in *vikalpa*
both options are *admissible*, whereas irreducible means the matter is undetermined and
further evidence is required. All states are retained, so a later change to the authority
ranking or the corpus can trigger re-evaluation of everything that depended on a resolution.

## Architectural Implications

- **Pipeline ordering is constrained.** Conflict detection must be a post-saturation pass,
  not a step inside rule firing, because precedence is only computable over the full fired
  set (§2, `execution_pipeline.md` §4).
- **Definitions must be first-class, versioned objects** with explicit links from every rule
  that uses them. Without that, C5 definitional conflict is undetectable — a requirement the
  source places on `rule_extraction_framework.md` §2, and what it calls a strong argument for
  the linking discipline of `shloka_compiler.md` §6.2 (§3.3).
- **The context lattice suppresses the highest-volume source of false conflict.** The source
  states that if the lattice keeps schools incomparable the detector never reports them as
  contradictory, and that this is what prevents the cross-product conflict flood. It asserts
  that the same pattern holds elsewhere — jurisdictions, populations, load cases — without
  stating that the lattice marks those incomparable (§4).
- **Resolution must be representable as a first-class object with negative fields.** The
  `Resolution` record requires `principles_unavailable`, an explicitly mandatory field, and
  `adjudicator_school` (§1, §8).
- **The output type of the engine must admit disjunction and non-answers.** `vikalpa` and
  `irreducible` are the states the source calls terminal, and escalation is queued with no
  automatic conclusion, so downstream consumers — including the explainability layer this
  document feeds — cannot assume a single conclusion (§7, §10).
- **Truncation and unavailability must be reported, not silently absorbed.** This applies to
  `defeater_chain_truncated` (§6) and to any principle that turns out to be inapplicable
  (§8, §11 item 1).
- **Domain independence rests on the L1/L2 split for authority.** The authority ranking is
  domain-supplied L2 configuration; the precedence machinery is core (§5.3,
  `reasoning_ontology.md` §2.1).
- **State retention enables re-evaluation.** Because all lifecycle states are kept, a change
  to the authority ranking or corpus can trigger re-evaluation of dependent resolutions —
  a capability whose tractability the source itself flags as untested (§10, §11 item 5).
- The source reserves the DAALE boundary `daale/ontology/contradiction.py` for this work, and
  records that it fills `choir/research/R001_Institutional_Arbitration.md` and
  `R005_Contradiction_Lifecycle.md`, both of which it notes are currently empty.

## Open Questions

The source records six open questions in §11, reproduced here with its own hedging:

1. **Is specificity always computable?** P1 needs entailment between conditions. For
   propositional conditions this is decidable; with quantifiers and kernel-computed
   predicates it may not be. Where entailment is undecidable, P1 silently becomes unavailable
   — and the source states that this must be *reported*, not assumed.
2. **Should *vikalpa* be weighted?** The classical notion treats options as equally
   admissible. Where confidences differ substantially, presenting them as equal alternatives
   may mislead — but ranking them re-imports the forced choice *vikalpa* exists to avoid. The
   source leaves this unresolved.
3. **Meta-conflict root axioms.** §6 stipulates the P1–P4 ordering. The source states that
   ordering is itself a substantive claim and that different domains may need different ones,
   which would make it L2 configuration rather than an L1 axiom.
4. **Escalation volume.** If the corpus is substantially contested, escalation may exceed
   available human capacity. The rate is **unknown until extraction runs at scale**
   (`rule_extraction_framework.md` §10.6).
5. **Re-evaluation blast radius.** Changing an authority ranking invalidates every resolution
   that relied on P4. Whether this is tractable at corpus scale is **untested**.
6. **Cross-domain conflict.** If CHOIR ever reasons across domains simultaneously, the
   precedence orderings are incomparable by construction. The source judges it "probably
   correct to forbid, but unexamined."

Two further limitations are recorded elsewhere in the document rather than in §11: the
unresolved cross-text authority problem, where whether text B's exception applies to text A
is often unanswerable across lineages (§5.3), and the unavailability of P3 wherever
composition order is not established (§5.1, §9). The source also qualifies its own
cross-tradition evidence as "weak but genuine" (§3.1).

## Related Documents

- [YK-R-004 — Vedic Reasoning Methodology](YK-R-004-vedic-reasoning-methodology.md) — declared dependency; supplies *hetvābhāsa* (§2.2), the cross-school non-conflict ruling R13 (§7), and the transmission-history caveat (§0.3)
- [YK-R-009 — Evidence Model](YK-R-009-evidence-model.md) — declared dependency; aggregation of corroborating evidence (§5), which handles C3
- [YK-R-015 — Execution Pipeline](YK-R-015-execution-pipeline.md) — declared consumer; post-saturation placement of conflict detection (§4)
- [YK-R-012 — Explainability Framework](YK-R-012-explainability-framework.md) — declared consumer
- [YK-R-002 — Reasoning Ontology](YK-R-002-reasoning-ontology.md) — cited for the L1/L2 split governing domain-supplied authority rankings (§2.1)
- [YK-R-006 — Shloka Compiler](YK-R-006-shloka-compiler.md) — cited for the definition-linking discipline (§6.2) and the resolution cache (§7.1)
- [YK-R-007 — Rule Extraction Framework](YK-R-007-rule-extraction-framework.md) — cited for `cross_references` (§2), adjudicator neutrality (§10.2), cross-text authority (§10.5), and extraction scale (§10.6)
- [YK-R-008 — Canonical Shloka Analysis (Benchmark)](YK-R-008-canonical-shloka-analysis-benchmark.md) — cited for interpretive confidence reduction (§4.4) and the traced *apavāda* behaviour and reporting principle (§9.2)
