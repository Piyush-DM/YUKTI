# Document Intake for the Vertical Slice

| | |
|---|---|
| **Document ID** | YK-D-002 |
| **Source** | `docs/architecture/DECISION-002_document_intake_for_the_vertical_slice.md` (DECISION-002) |
| **Series** | Architecture Decisions |
| **Revision** | A |
| **Status** | Published |
| **Last Updated** | 2026-08-23 |

## Abstract

This decision fixes what a "document" is for v0.1 of the investment vertical slice, and what the parsing layer in front of the CHOIR intermediate representation is permitted to do to it. It approves **Option A — the document is the packet, serialised** — under which parsing is deserialisation plus structural validation, with no extraction, no inference, and no defaulting (§ Options, § Recommendation). The source records the ruling as **"Approved 2026-08-06, and broadened"**, with product-generated serialised packet documents approved on the same terms and one binding principle: "Documents may represent packets. They may not interpret them." (§ Approval Status).

## Research Question

The source states its question explicitly (§ Decision):

> **What is a "document" for v0.1, and what is a parsing layer allowed to do to it?**

The document explains why the question had to be settled at all. The vertical slice was specified as: fixed sample document → parsing layer → intermediate representation → reasoning layer → canonical report → rendered report. Everything from the intermediate representation onward already existed in `choir_prototype/` and was used unchanged. The first arrow did not exist — `choir_prototype/` begins at a *packet*, an already-structured deal file, and "has no notion of a document at all" (§ Decision).

The source states that the question "is load-bearing because the answer determines whether the slice is plumbing or a new reasoning stage." It records that `CHOIR_v0.1_RESEARCH_FREEZE.md` §4.3 documents that the prototype has **no provenance chain to source text** — evidence cites a source label, not a locus in an edition — and that "any answer that involves reading prose starts paying down that gap, which is a research programme," citing §9, *scope discipline*: "do not partially implement one to make a current problem easier" (§ Decision).

## Finding

### The three options as posed

The source states three options (§ Options):

| Option | The document is | Parsing does |
|---|---|---|
| **A** | the packet, serialised — a JSON file in the deal team's own shape: sources, data points, stated assumptions, noted conflicts | deserialisation plus structural validation; "No extraction, no inference, no defaulting." |
| **B** | prose — a deal memo in natural language | extraction: an extraction layer "that identifies metrics, values, sources and conflicts" |
| **C** | prose | as B, "with a language model performing extraction upstream of the IR" |

### Why Option B was rejected

The source's objection is that "**Option B invents a reasoning stage and calls it parsing.**" Deciding that a sentence asserts `net_revenue_retention_pct = 104` backed by `SRC-DECK` at status `disputed` "is interpretation, and interpretation is exactly what the IR exists to make inspectable." Such a decision "would land in a layer with no confidence derivation, no trace, and no evidence model — which is to say, an unaudited reasoning step in front of the audited ones" (§ Tradeoffs).

The source adds a second, testability objection: Option B "makes the slice's central property untestable: with an extractor in the path there is no way to distinguish 'the pipeline works' from 'the extractor guessed well today.'" (§ Tradeoffs).

### Why Option C was rejected

The source states that "**Option C is the same objection plus a settled one.**" `DECISION-001` approved deterministic kernels as the architecture; extraction upstream of the IR "is explicitly left open there as *a different decision*, and it is the one CHOIR commitment E10 (embeddings propose, they never conclude) governs." Adopting extraction "as a side effect of building a plumbing slice would be the worst possible way to decide it." The source further states that Option C "breaks X1 outright, and with it every artifact this slice persists" (§ Tradeoffs).

### Why Option A was adopted

The source states that "**Option A costs the least and proves the most.**" Because the sample document is the frozen `ORBITAL_SERIES_B` packet serialised, "the parsed result can be asserted *equal* to the packet inside the prototype. That single assertion is the whole guarantee that intake added no semantics — and it is a guarantee neither B nor C can offer at any price." (§ Tradeoffs).

The cost is stated by the source rather than elided: "Its cost is honest and stated: the slice demonstrates O1 machinery, not O1 itself, since the input is still a constructed sample rather than real material." (§ Tradeoffs).

The recommendation section gives the reason in terms of layer discipline: Option A "is the only option that keeps the parsing layer at the same discipline the domain translator already holds — map shapes, preserve what the source said, reason about nothing — and the only one whose correctness can be checked rather than assessed" (§ Recommendation).

The source does not retire Option B. It records that "Option B remains the right next step and is where the provenance work in §4.3 belongs. It should be taken deliberately, with a locus model, and not folded into a plumbing change." (§ Recommendation).

### Consequences as recorded

The source records the following consequences (§ Consequences):

- Document intake lives in `applications/investment/vertical_slice/parse.py` and raises only *structural* errors. Unknown `kind` and `status` vocabulary "falls through to the translator's existing conservative defaults rather than being rejected at intake, because that mapping is the translator's decision and duplicating it would create a second place to change it."
- `choir_prototype/` is untouched. `--frozen` reports INTACT and `--audit` reports portability 1.00 with the slice in the tree.
- The document format is versioned (`yukti-investment-document/0.1`) and a document declaring any other version is refused. "This is the hook Option B will need."
- "The slice does not close §4.3. It does not add provenance to source loci, and nothing here should be read as evidence that it did."
- "No claim is made against experimental objective O1. The input is a constructed sample; O1 requires real material."

### Approval, as given, and the broadening

The ruling is recorded as **"Approved 2026-08-06, and broadened."** Product-generated serialised packet documents are approved, "provided they introduce no semantic interpretation beyond the canonical packet." The source states that the architectural principle is unchanged and still binding (§ Approval Status):

> Documents may represent packets. They may not interpret them.

The broadening is tied to a specific recorded overrun: "This settles the boundary overrun recorded in the implementation log: the workspace composes a fresh document per case, which is a document that is not the frozen sample. It stays inside the approved principle -- the composition is a shape mapping with no extraction -- and is now explicitly authorised rather than merely defensible." (§ Approval Status).

The same section restates the limit of the approval: "Option B (prose plus extraction) remains unapproved and is still where the provenance work in the research freeze section 4.3 belongs."

## Architectural Implications

The following are the implications the source itself draws.

**The parsing layer is not a reasoning stage.** Intake is held to the discipline the domain translator already holds — "map shapes, preserve what the source said, reason about nothing" — so that the intermediate representation remains the place where interpretation is made inspectable (§ Recommendation, § Tradeoffs). Any layer that assigned metric, value, source, and status from prose would sit in front of the audited stages without confidence derivation, trace, or evidence model (§ Tradeoffs).

**Correctness of intake is checkable rather than assessable.** Because the sample document is the frozen `ORBITAL_SERIES_B` packet serialised, the parsed result can be asserted equal to the packet inside the prototype; that equality assertion is, per the source, "the whole guarantee that intake added no semantics" (§ Tradeoffs).

**The prototype boundary is preserved.** `choir_prototype/` is untouched; `--frozen` reports INTACT and `--audit` reports portability 1.00 with the slice in the tree (§ Consequences).

**Vocabulary decisions stay with the translator.** Unknown `kind` and `status` values are not rejected at intake but fall through to the translator's existing conservative defaults, to avoid creating a second place to change that mapping (§ Consequences).

**A versioned format is the designated extension point.** The document format is versioned as `yukti-investment-document/0.1`, other versions are refused, and the source identifies this version gate as "the hook Option B will need" (§ Consequences).

**Deferred, and explicitly not decided here.** Extraction upstream of the IR remains a separate decision left open by `DECISION-001` and governed by CHOIR commitment E10 (embeddings propose, they never conclude); the source states it must not be settled as a side effect of a plumbing slice (§ Tradeoffs).

**The generative boundary for product documents.** Product-generated serialised packet documents — including the workspace composing a fresh document per case — are authorised only so long as they introduce "no semantic interpretation beyond the canonical packet," under the binding principle that documents may represent packets but may not interpret them (§ Approval Status).

## Open Questions

The source records the following as unresolved, out of scope, or explicitly not claimed:

- **Provenance to source loci is not addressed.** "The slice does not close §4.3. It does not add provenance to source loci, and nothing here should be read as evidence that it did." (§ Consequences). The gap itself is stated in § Decision: the prototype has no provenance chain to source text; evidence cites a source label, not a locus in an edition.
- **No claim is made against experimental objective O1.** "The input is a constructed sample; O1 requires real material." (§ Consequences). The slice "demonstrates O1 machinery, not O1 itself" (§ Tradeoffs).
- **Option B (prose plus extraction) remains unapproved.** It is recorded as "the right next step," to be taken deliberately and with a locus model, and not folded into a plumbing change (§ Recommendation, § Approval Status).
- **Extraction upstream of the IR is an open, separate decision.** `DECISION-001` leaves it explicitly open as a different decision, governed by CHOIR commitment E10 (§ Tradeoffs).
- **The locus model referred to in § Recommendation is not specified here.** Not stated in the source document.

## Related Documents

- [YK-D-001 — Reasoning Execution Substrate](YK-D-001-reasoning-execution-substrate.md) — cited in the source as `DECISION-001`, which approved deterministic kernels as the architecture and left extraction upstream of the IR open as a different decision (§ Tradeoffs).

No other publication in the index is cited by the source document. Its remaining references — `CHOIR_v0.1_RESEARCH_FREEZE.md` (§4.3, §9), the implementation log, `choir_prototype/`, and `applications/investment/vertical_slice/parse.py` — are not publications in this series.
