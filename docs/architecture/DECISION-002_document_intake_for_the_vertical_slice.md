# Decision Required: document intake for the vertical slice

**Status: Pending architect approval.** The implementation it describes exists,
under the direct architectural instruction to build the first complete vertical
slice. This note records the choice that instruction did not settle, so that
approving or reversing it is a deliberate act rather than an archaeology
exercise. See "Approval Status" below for what happens if it is rejected.

## Decision

The vertical slice was specified as: fixed sample document → parsing layer →
intermediate representation → reasoning layer → canonical report → rendered
report. Everything from the intermediate representation onward already exists in
`choir_prototype/` and was used unchanged.

The first arrow did not exist. `choir_prototype/` begins at a *packet* — an
already-structured deal file — and has no notion of a document at all. So the
decision is:

**What is a "document" for v0.1, and what is a parsing layer allowed to do to
it?**

This is load-bearing because the answer determines whether the slice is
plumbing or a new reasoning stage. `CHOIR_v0.1_RESEARCH_FREEZE.md` §4.3 records
that the prototype has **no provenance chain to source text** — evidence cites a
source label, not a locus in an edition. Any answer that involves reading prose
starts paying down that gap, which is a research programme (§9, *scope
discipline*: "do not partially implement one to make a current problem easier").

## Options

**Option A — the document is the packet, serialised.** A JSON file in the deal
team's own shape: sources, data points, stated assumptions, noted conflicts.
Parsing is deserialisation plus structural validation. No extraction, no
inference, no defaulting.

**Option B — the document is prose, and parsing extracts.** A deal memo in
natural language, with an extraction layer that identifies metrics, values,
sources and conflicts.

**Option C — the document is prose, and a model extracts.** As B, with a
language model performing extraction upstream of the IR.

## Tradeoffs

**Option B invents a reasoning stage and calls it parsing.** Deciding that a
sentence asserts `net_revenue_retention_pct = 104` backed by `SRC-DECK` at
status `disputed` is interpretation, and interpretation is exactly what the IR
exists to make inspectable. It would land in a layer with no confidence
derivation, no trace, and no evidence model — which is to say, an unaudited
reasoning step in front of the audited ones. It also makes the slice's central
property untestable: with an extractor in the path there is no way to
distinguish "the pipeline works" from "the extractor guessed well today."

**Option C is the same objection plus a settled one.** `DECISION-001` approved
deterministic kernels as the architecture; extraction upstream of the IR is
explicitly left open there as *a different decision*, and it is the one CHOIR
commitment E10 (embeddings propose, they never conclude) governs. Adopting it as
a side effect of building a plumbing slice would be the worst possible way to
decide it. It also breaks X1 outright, and with it every artifact this slice
persists.

**Option A costs the least and proves the most.** Because the sample document is
the frozen `ORBITAL_SERIES_B` packet serialised, the parsed result can be
asserted *equal* to the packet inside the prototype. That single assertion is
the whole guarantee that intake added no semantics — and it is a guarantee
neither B nor C can offer at any price. Its cost is honest and stated: the slice
demonstrates O1 machinery, not O1 itself, since the input is still a constructed
sample rather than real material.

## Recommendation

**Option A.** It is the only option that keeps the parsing layer at the same
discipline the domain translator already holds — map shapes, preserve what the
source said, reason about nothing — and the only one whose correctness can be
checked rather than assessed.

Option B remains the right next step and is where the provenance work in §4.3
belongs. It should be taken deliberately, with a locus model, and not folded
into a plumbing change.

## Consequences

- Document intake lives in `applications/investment/vertical_slice/parse.py` and
  raises only *structural* errors. Unknown `kind` and `status` vocabulary falls
  through to the translator's existing conservative defaults rather than being
  rejected at intake, because that mapping is the translator's decision and
  duplicating it would create a second place to change it.
- `choir_prototype/` is untouched. `--frozen` reports INTACT and `--audit`
  reports portability 1.00 with the slice in the tree.
- The document format is versioned (`yukti-investment-document/0.1`) and a
  document declaring any other version is refused. This is the hook Option B
  will need.
- The slice does not close §4.3. It does not add provenance to source loci, and
  nothing here should be read as evidence that it did.
- No claim is made against experimental objective O1. The input is a constructed
  sample; O1 requires real material.

## Approval Status

Pending architect approval.

If Option A is rejected, the reversal is contained: delete
`applications/investment/vertical_slice/` and the two rows referencing it in
`docs/traceability/TRACEABILITY_MATRIX.md`. Nothing outside that directory
depends on it, by construction.
