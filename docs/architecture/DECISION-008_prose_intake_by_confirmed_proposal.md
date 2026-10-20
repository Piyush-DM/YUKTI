# Decision Required: prose intake by confirmed proposal

**Status: Proposed. Not accepted.** Raised because the conversational surface
reads pasted prose, and `DECISION-002` names and declines the obvious way of
doing that. This note asks for the narrower thing instead.

## The question

May the product read free prose into *proposed* figures that a person confirms
one at a time, and record the passage each confirmed figure came from?

## Why it needs asking

`DECISION-002` is approved and binding, and it considered this territory:

> **Option B — the document is prose, and parsing extracts.**
> **Option C — the document is prose, and a model extracts.**
>
> *"Deciding that a sentence asserts `net_revenue_retention_pct = 104` backed by
> `SRC-DECK` at status `disputed` is interpretation, and interpretation is
> exactly what the IR exists to make inspectable. It would land in a layer with
> no confidence derivation, no trace, and no evidence model — which is to say, an
> unaudited reasoning step in front of the audited ones. It also makes the
> slice's central property untestable: with an extractor in the path there is no
> way to distinguish 'the pipeline works' from 'the extractor guessed well
> today.'"*
>
> Approved: **"Documents may represent packets. They may not interpret them."**
> Option B remains unapproved and *"is still where the provenance work in the
> research freeze section 4.3 belongs."*

That objection is correct and is not being asked to move. What follows is
narrower than Option B, and the difference is one step.

## The distinction this note turns on

**Who authors the figure.**

Under Option B, the extractor authors it: prose goes in, a figure lands in
material, and no person attested it. That is the unaudited reasoning step, and
it is what makes "the pipeline works" indistinguishable from "the extractor
guessed well today."

Under this proposal the *reader* authors it. The reader is shown a proposed
value, its standing, its source, the sentence it was read from, and the reason
it was read that way. They accept, correct, or reject each one. Nothing reaches
the case store, the material digest, or the engine until they do.

That act — a person deciding a figure is `104`, `reported`, backed by `SRC-DECK`
— is the act the product **already** has them perform, today, by typing it into
the diligence schedule. The implementation log calls it out as unrecorded:

> *"Evidence formation is still unrecorded. A human typing `status: estimated`
> performs an unaudited judgement. Material identity now records that they did it
> and when, but not why or from what."*

So the epistemic act is unchanged. What changes is that it is now **evidenced**:
the figure arrives with the passage behind it, and that passage is kept.

## What this closes

`CHOIR_v0.1_RESEARCH_FREEZE.md` §4.3, carried as a prototype limit:

> *"No provenance chain to source text. Evidence cites a source label, not a
> locus in an edition."*

A confirmed proposal records the locus. This is the first thing in the product
that does, and `DECISION-002` itself names §4.3 as where this work belongs.

## Decision

Approve prose intake **only** in this shape:

1. **Proposals are not material.** `intake.propose` / `intake.read` return
   suggestions. They touch no store, no digest, no engine.
2. **A person confirms every figure.** Accepting is per-figure, with the value,
   standing and source all editable at the point of acceptance.
3. **A figure may not cite an unregistered source.** Sources the prose names are
   also proposed, and are also confirmed, before any figure may cite them. The
   existing `_validate_material` rule is unchanged and still enforced.
4. **Confirmed figures enter material by the existing route.** `record_material`,
   with its validation and its snapshot. Intake can put nothing on file that the
   diligence screen could not.
5. **Provenance is recorded outside material identity.** `IntakeRecord` is
   append-only on the case and is deliberately absent from `material_payload`.
   Two reasons: a figure typed by hand and the same figure accepted from a memo
   are the same material and must hash the same; and every existing decision
   verifies against a digest computed without it, which folding it in would
   silently invalidate.
6. **The reader is never asked to trust an opaque reading.** Every proposal
   states the phrase that triggered it and how the number was read.

## The reader defaults, stated as a weakness

A proposal's `status` is defaulted from the kind of source it was attributed to
(`audit` → `confirmed`, `third_party` → `estimated`, and so on). That mapping is
a convenience, and it is the part of this most likely to be rubber-stamped: a
reader who accepts fifteen figures without reading them has performed a worse
judgement than one who typed fifteen figures, not a better one.

Two things hold against it, and neither is sufficient on its own: the standing
is editable in the accept step, and `IntakeRecord.edited` records whether the
reader changed the reading. The second is what makes rubber-stamping visible
after the fact rather than merely disapproved of.

## The deterministic reader, and the model that is not wired

The reader shipped here is deterministic: a keyword-and-unit pass over the
fifteen metrics the diligence schedule already names. No model, no network. Same
prose in, same proposals out.

That is deliberate and is not merely caution. A confirmation step is only a real
check if the thing being confirmed is reproducible — a reader cannot meaningfully
check a proposal nobody can regenerate. It also keeps the workspace standard
library only, and keeps every proposal testable in the existing suite.

`intake.propose_from_assistant` is declared, unimplemented, and raises. A model
occupying that seam would be **advisory**, consistent with `DECISION-001`
("model calls are advisory only, never authoritative"), and would have to meet
the same contract: return `Proposal` objects, each carrying the span it came
from, each still requiring confirmation. Wiring one is a further ruling, not a
refactor, and this note does not grant it.

## What is explicitly *not* proposed

- Extraction that writes material without confirmation. That is Option B and
  stays unapproved.
- Any change to `choir_prototype/`, the IR, or what reaches the engine. The
  engine still receives a serialised packet composed by `analysis.compose_document`,
  exactly as before.
- Any model call anywhere in the product.
- Provenance inside the material digest. See point 5.

## Options considered

**A — Approve as scoped above.** *Proposed.* Closes §4.3's provenance gap in the
product, removes the retyping that makes the workspace unusable on real material,
and leaves authorship with the person it already belongs to.

**B — Decline; keep intake structured.** The workspace stays honest and stays
unusable on anything but an already-structured pack. The §4.3 gap stays open.

**C — Approve prose extraction without confirmation.** This is `DECISION-002`
Option B. Not proposed, and named here only so the record shows it was not
adopted by omission.

## Consequences if approved

- New: `intake.py` (proposer), `explain.py` (record-projected answers),
  `IntakeRecord` on `Case`, `CaseStore.accept_intake`, three routes
  (`/read`, `/accept`, `/ask`), and a chat surface at `ui/index.html`.
- `choir_prototype/` untouched; `--frozen` INTACT and `--audit` portability 1.00.
- Material digests unchanged, so every existing ledger entry still verifies.
- The chat answers only from the record and declines otherwise, which is
  commitment E9 extended into a conversational surface.

## Approval Status

**Proposed. Requires architect acceptance.** Until then the intake path is
implemented but rests on an unapproved note, which is the same governance gap
already recorded for `choir_prototype/` and the vertical slice — recorded here
rather than left to be discovered.
