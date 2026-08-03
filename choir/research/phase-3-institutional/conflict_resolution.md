# 010 — Conflict Resolution

**Status:** Draft for review
**Phase:** 3 — Institutional Reasoning
**Depends on:** `vedic_reasoning_methodology.md`, `evidence_model.md`
**Feeds:** `execution_pipeline.md`, `explainability_framework.md`
**Reserved DAALE boundary:** `daale/ontology/contradiction.py`
**Fills:** `choir/research/R001_Institutional_Arbitration.md`, `R005_Contradiction_Lifecycle.md` (both currently empty)

---

## 1. The governing commitment

When two rules disagree, most systems pick one. CHOIR's commitment is different, and it
shapes everything below:

> **Never silently pick. Every resolution is an inference with its own grounds, its own
> provenance, and its own defeasibility — and "unresolved" is a legitimate output.**

Two consequences:

1. A resolution is itself a `Resolution` object, subject to the same machinery as any other
   inference. Resolutions can be contested, superseded, and defeated.
2. The pipeline must be able to **terminate in a disjunction** (*vikalpa*, §7). A system
   that always returns one answer cannot be faithful to a corpus that genuinely contains
   unresolved splits — and all five reference domains do.

---

## 2. Detection: what counts as a conflict

Conflict detection runs **after** saturation, not during rule firing
(`execution_pipeline.md` §4). The reason is that precedence depends on the *full* set of
fired rules: a rule may win by specificity against one competitor and lose by source
authority against another, and neither judgement is available mid-match.

Two inferences conflict when:

```
conflict(i₁, i₂)  ⟺  contexts_overlap(i₁.context, i₂.context)
                   ∧ incompatible(i₁.conclusion, i₂.conclusion)
                   ∧ both_undefeated(i₁, i₂)
```

All three conjuncts matter. Dropping the first produces the false-conflict flood of §4;
dropping the third reports conflicts between an inference and something already withdrawn.

---

## 3. Conflict taxonomy

Seven classes. The first three are what people usually mean by "conflict"; the last four are
where real corpora actually cause trouble.

| # | Class | Shape | Example |
|---|---|---|---|
| C1 | **Contradictory** | *P* and *¬P* | One rule indicates a result; another denies it |
| C2 | **Incompatible** | Mutually exclusive, not negations | Two rules assign different exclusive classifications |
| C3 | **Degree** | Same direction, different strength | Both indicate; one strongly, one weakly |
| C4 | **Applicability** | Both claim to govern the same case | General rule and specific rule overlap |
| C5 | **Definitional** | Same term, different definitions | Schools define *kendra* reckoning differently; statutes define "resident" differently |
| C6 | **Temporal** | Rules in force at different times | Superseded statute vs current; earlier vs later recension |
| C7 | **Meta** | Conflicting *resolution* rules | Specificity favours one, recency the other |

### 3.1 The classical taxonomy maps onto this

Nyāya's *hetvābhāsa* (`vedic_reasoning_methodology.md` §2.2) classifies defective reasons,
and the correspondence is close enough to be useful as a cross-check:

| *Hetvābhāsa* | Class here |
|---|---|
| *viruddha* (contradictory) | C1 |
| *satpratipakṣa* (counterbalanced) | C1/C2 **with no precedence available** → §7 |
| *asiddha* (unestablished) | Premise defeat — not a conflict |
| *bādhita* (overridden by a stronger means) | Resolved by §5.3 |
| *savyabhicāra* (inconclusive) | Non-discriminating condition — a rule-quality defect |

That two traditions arrive at nearly the same partition is weak but genuine evidence the
partition is natural rather than arbitrary.

### 3.2 Degree conflict (C3) is not a conflict

C3 is listed for completeness and then dismissed: two rules indicating the same conclusion
with different strengths are **corroborating evidence**, handled by aggregation
(`evidence_model.md` §5), not by resolution. Treating C3 as conflict is a common modelling
error that generates enormous spurious volume.

### 3.3 Definitional conflict (C5) is the worst

C5 is the most damaging because it is **silent**. Two rules using *kendra* under different
reckoning conventions do not appear to conflict — they appear to agree, or to address
different cases, while actually computing different things.

Detection requires that **definitions be first-class, versioned objects** with explicit
links from every rule that uses them (`rule_extraction_framework.md` §2, `cross_references`).
A rule that references a definition by name rather than by versioned identifier cannot be
checked for C5 at all. This is a strong argument for the linking discipline in
`shloka_compiler.md` §6.2.

---

## 4. Context splitting: the first move, always

> **Most apparent contradictions are context collisions.**

Two rules that appear to contradict frequently were never meant to co-apply. Their scoping
conditions were left implicit in the source — different school, different application,
different chart, different epoch — and the collision is an artefact of extraction dropping
the scope, not a genuine disagreement.

```
      apparent conflict
             │
   ┌─────────▼──────────────────────────────┐
   │  Do the contexts actually overlap?     │
   └─────────┬──────────────────────────────┘
        no ──┴── yes
         │        │
    NOT A         ▼
    CONFLICT   ┌───────────────────────────────────┐
    (record    │ Is there a missing discriminator? │
     as        │ (school, application, epoch,      │
     disjoint) │  reference frame, granularity)    │
               └─────────┬─────────────────────────┘
                  yes ───┴─── no
                   │           │
            SPLIT CONTEXTS     ▼
            re-scope both   GENUINE CONFLICT → §5
            rules; record
            the split as
            an inference
```

**Cross-school difference is not conflict** (`vedic_reasoning_methodology.md` §7, R13).
Parāśara and Jaimini rules are different systems, not competitors. If the context lattice
keeps schools incomparable, the detector never reports them as contradictory — which is
correct, and which is the single highest-volume source of false conflict in this corpus.

The same pattern holds elsewhere: two jurisdictions' statutes do not conflict; two
guidelines for different populations do not conflict; two design codes for different load
cases do not conflict.

**Cost of getting this wrong:** without context splitting, a corpus of *n* rules from *k*
schools generates conflicts roughly proportional to the cross-product, and the conflict
queue becomes unusable.

---

## 5. Precedence

Precedence is a **partial order**, not a total one. Incomparability is a real outcome and
leads to §7 rather than to an arbitrary tiebreak.

### 5.1 Structural precedence

Applied in this order:

| # | Principle | Classical form | Rule |
|---|---|---|---|
| P1 | **Specificity** | *apavāda* over *utsarga*; *lex specialis* | The rule with the strictly stronger condition wins |
| P2 | **Phase** | *pūrvatrāsiddham* (A. 8.2.1) | Rules in a later designated phase are invisible to earlier ones |
| P3 | **Recency** | *vipratiṣedhe paraṃ kāryam* (A. 1.4.2); *lex posterior* | Where scope is equal, the later rule prevails |
| P4 | **Authority** | *bādha*; *lex superior* | The higher-ranked source prevails (§5.3) |

**P1 requires strict containment.** Rule A is more specific than B only if A's condition
*entails* B's. Two rules with merely *different* conditions are not ordered by specificity —
a distinction that is routinely fudged and that produces wrong resolutions when it is.

**P3 is the weakest and is applied last** among the structural principles. "Later" is
well-defined for a single text's internal ordering (Pāṇini's case) and for dated statutes.
It is **not** well-defined across recensions of a text with a contested transmission history
(`vedic_reasoning_methodology.md` §0.3). Where composition order is uncertain, P3 is
unavailable and must not be faked.

### 5.2 Interpretive precedence

Where the conflict concerns **what a text means** rather than which rule governs, Mīmāṃsā
supplies a six-fold ordering, adopted directly:

> *śruti* > *liṅga* > *vākya* > *prakaraṇa* > *sthāna* > *samākhyā*

| Ground | Meaning | Weight |
|---|---|---|
| *śruti* | Direct statement in the text | Highest |
| *liṅga* | Indicatory force of a word | |
| *vākya* | Syntactic connection | |
| *prakaraṇa* | Contextual setting | |
| *sthāna* | Position in the text | |
| *samākhyā* | Name or title | Lowest |

A reading grounded in an explicit statement beats one grounded in contextual placement,
which beats one grounded in a section heading.

This has a direct consequence already used in Phase 2: an inherited scope condition
(*prakaraṇa*) carries **less** interpretive weight than a stated one (*śruti*) — which is
why the benchmark rule's inherited application scope reduces its interpretive confidence
(`canonical_shloka_analysis.md` §4.4).

It also generalises cleanly: statutory text outranks a marginal note; a guideline's
recommendation outranks its introductory discussion; a contract's operative clause outranks
its recitals. The tradition's ordering turns out to be a general theory of textual
authority, not a parochial one.

### 5.3 Source authority

The ranking itself is **domain-supplied** (L2 per `reasoning_ontology.md` §2.1); the
*machinery* is core. This separation is what keeps the engine domain-independent.

| Domain | Typical ranking (highest first) |
|---|---|
| Jyotiṣa | *mūla* text > classical *ṭīkā* > later commentary > modern exposition |
| Law | Constitution > statute > regulation > guidance > commentary |
| Medicine | Systematic review/RCT > cohort > case series > expert opinion |
| Finance | Statute > regulation > contract > market convention |
| Engineering | Mandatory code > referenced standard > handbook > practice note |

**The unresolved cross-text problem.** When text A states a rule and text B states its
exception, whether B's exception applies to A depends on whether B is authoritative *for*
A. Within a lineage this is answerable; across lineages it often is not
(`rule_extraction_framework.md` §10.5). Where authority is undetermined, P4 is unavailable —
which is a common route into §7.

### 5.4 Incomparability

Where no principle applies, or two principles point opposite ways with no meta-ordering
(C7), the pair is **incomparable**. This is not a failure; it is the correct finding, and it
routes to §7.

---

## 6. Defeater chains and well-foundedness

Exceptions have exceptions (*nīca-bhaṅga* annulling a debilitation-based cancellation).
Chains are normal, and the machinery must terminate.

```
  R  ──────────▶ conclusion
  ▲
  │ undercut
  E₁ ── attacks the inference
  ▲
  │ undercut
  E₂ ── attacks E₁  → R's conclusion is restored
  ▲
  │
  E₃ ── attacks E₂  → withdrawn again
```

**Well-foundedness requirement.** The attack relation must be acyclic, and every chain must
terminate in an unattacked node. Enforced by:

1. **Cycle detection at compile time.** A cyclic attack set is `E-CYCLE`, rejected.
2. **Stratification.** Exceptions are assigned a level; an exception may attack only lower
   levels. This is derivable from the *utsarga/apavāda* structure, since an *apavāda* is by
   construction more specific than what it restricts.
3. **Depth bound with reporting.** If a bound is hit, the system reports
   `defeater_chain_truncated` rather than returning a result as if the analysis completed.

Point 3 restates the principle from `canonical_shloka_analysis.md` §9.2: the system must
report what it did not evaluate. A confident answer that quietly skipped half the defeater
chain is worse than an explicit partial result.

**Meta-conflict regress (C7).** Resolution rules are objects and can themselves conflict.
The regress is stopped by a small set of **stipulated root axioms** — the precedence
principles of §5.1 in a fixed order — which are declared, not derived. Declaring them makes
the stopping point explicit and contestable rather than hidden in implementation.

---

## 7. Resolution outcomes

Six outcomes. The tradition names three that most engines lack, and they are the ones that
make honest reporting possible.

| Outcome | Classical | Meaning | Output |
|---|---|---|---|
| **Preempt** | *bādha* | One rule cancels the other | Winner's conclusion; loser recorded as defeated |
| **Restrict** | *apavāda* | The specific carves out from the general | Both retained, scopes adjusted |
| **Conjoin** | *samuccaya* | Both apply together | Both conclusions |
| **Split** | — | Contexts separated (§4) | Both, in disjoint contexts |
| ***Vikalpa*** | *vikalpa* | **Both admissible; neither defeats the other** | **A disjunction, with support for each** |
| **Escalate** | — | Requires human judgement | Queued; no automatic conclusion |

### 7.1 *Vikalpa* — the outcome that matters

*Vikalpa* is a **terminal, legitimate state of analysis**: two rules conflict, precedence is
unavailable or incomparable, and the correct output is *both alternatives with their
support*, not a forced choice.

```
CONCLUSION: vikalpa
  ├─ Alternative 1: <conclusion A>
  │    ├─ supported by: <rules, evidence>
  │    └─ confidence: <decomposed>
  ├─ Alternative 2: <conclusion B>
  │    ├─ supported by: <rules, evidence>
  │    └─ confidence: <decomposed>
  └─ Why unresolved: <which precedence principles were tried and why
                      each was unavailable or incomparable>
```

The last line is what distinguishes this from an evasion. "Unresolved" is only acceptable
when the system can say *what it tried*.

**This is not a Jyotiṣa peculiarity.** Genuine unresolved splits are routine everywhere:

| Domain | *Vikalpa* in practice |
|---|---|
| Law | A circuit split; two defensible readings of an ambiguous provision |
| Medicine | Two guideline-supported treatment options of comparable standing |
| Finance | Two permitted accounting treatments |
| Engineering | Two acceptable design approaches under the same code |

A system that collapses these to one answer is not more useful; it is less honest, and in
each of these domains the collapse discards information the decision-maker needs.

### 7.2 Escalation

Escalation is required — not merely permitted — when:

- Precedence is incomparable **and** the alternatives have materially different consequences
- A definitional conflict (C5) is detected
- A defeater chain was truncated
- Resolution would rely on an authority ranking marked uncertain
- The conflict is between contexts the lattice marks incomparable (cross-school)

The escalation record carries the full conflict analysis, so the human decision is made on
the same material the system used — and the human's resolution is recorded as a
`Resolution` object with its grounds, feeding the resolution cache
(`shloka_compiler.md` §7.1).

---

## 8. The resolution object

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

`principles_unavailable` is mandatory. Recording only the principle that decided the matter
hides whether the resolution was overdetermined (several principles agreed) or hung on a
single contestable ground. That difference is exactly what a reviewer needs.

`adjudicator_school` acknowledges that in a live tradition the adjudicator is not a neutral
party (`rule_extraction_framework.md` §10.2).

---

## 9. Worked example

Two rules, both extracted, both fired:

- **R1** — *Jupiter in a kendra from the Moon indicates Gajakesarī.*
  Context: `{application: jātaka, chart: rāśi}`. Source: verse V1.
- **R2** — *Jupiter debilitated withdraws the indication.*
  Context: same. Source: verse V2.

**Detection.** Contexts overlap ✓. Conclusions incompatible ✓ (one indicates, one
withdraws). Both undefeated ✓. → conflict.

**Classification.** Not C1: R2 does not assert ¬Gajakesarī, it withdraws R1's warrant. This
is **C4 applicability**, realised as an undercutting defeater.

**Context split (§4).** Same school, same application, same chart. No missing discriminator.
→ genuine.

**Precedence.**

| Principle | Result |
|---|---|
| P1 specificity | R2's condition (kendra **and** debilitated) entails R1's (kendra). **Strict containment → R2 wins.** |
| P2 phase | Not applicable — no phase declaration |
| P3 recency | **Unavailable** — composition order across these verses is not established |
| P4 authority | Not reached |

**Outcome:** `restrict`. R1 holds generally; R2 carves out the debilitated case. This is
*apavāda*, and it is exactly the behaviour traced in `canonical_shloka_analysis.md` §9.2.

**Recorded:**

```
Resolution {
  outcome: restrict
  grounds: [ { P1 specificity, applied: true, result: R2 restricts R1 } ]
  principles_unavailable: [
    { P2, reason: no phase declaration in source },
    { P3, reason: composition order not established across these verses },
    { P4, reason: not reached — P1 decided }
  ]
  resolved_by: automatic
  confidence: high — strict containment; single unambiguous principle
}
```

Had P1 *not* applied — two rules with merely different conditions — P3 would have been the
next candidate and would have been unavailable, P4 would then depend on whether V1 and V2
are equally authoritative, and the likely outcome would be **`vikalpa` or escalation**. That
is the correct behaviour, and it is worth noting how quickly a plausible variation reaches
it.

---

## 10. Lifecycle

```
detected ──▶ classified ──▶ split-attempted ──┬──▶ not-a-conflict (disjoint)
                                              ├──▶ resolved (automatic)
                                              ├──▶ vikalpa (terminal)
                                              └──▶ escalated ──▶ resolved (human)
                                                            └──▶ irreducible
```

`irreducible` is a real terminal state: a conflict a human has examined and determined
cannot be resolved on available grounds. It is distinct from `vikalpa` (where both options
are *admissible*) — irreducible means the matter is undetermined and further evidence is
required.

All states are retained. A resolved conflict keeps its record so that a later change to the
authority ranking or the corpus can trigger re-evaluation of everything that depended on it.

---

## 11. Open questions

1. **Is specificity always computable?** P1 needs entailment between conditions. For
   propositional conditions this is decidable; with quantifiers and kernel-computed
   predicates it may not be. Where entailment is undecidable, P1 silently becomes
   unavailable — and that must be *reported*, not assumed.
2. **Should *vikalpa* be weighted?** The classical notion treats options as equally
   admissible. Where confidences differ substantially, presenting them as equal alternatives
   may mislead — but ranking them re-imports the forced choice *vikalpa* exists to avoid.
3. **Meta-conflict root axioms.** §6 stipulates the P1–P4 ordering. That ordering is itself
   a substantive claim and different domains may need different ones — which would make it
   L2 configuration rather than an L1 axiom.
4. **Escalation volume.** If the corpus is substantially contested, escalation may exceed
   available human capacity. The rate is unknown until extraction runs at scale
   (`rule_extraction_framework.md` §10.6).
5. **Re-evaluation blast radius.** Changing an authority ranking invalidates every resolution
   that relied on P4. Whether this is tractable at corpus scale is untested.
6. **Cross-domain conflict.** If CHOIR ever reasons across domains simultaneously, the
   precedence orderings are incomparable by construction. Probably correct to forbid, but
   unexamined.
