# Traceability Matrix

This matrix records approved links from specifications to implementation
artifacts. It is intentionally sparse until source specifications contain
accepted content.

## Matrix

| Source SPEC | Concept | Architectural Component | Implementation File | Unit Tests | Benchmark | Documentation | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pending | Pending | DAALE ontology scaffold | `daale/ontology/` | `daale/tests/test_ontology_scaffold.py` | Pending | `daale/ontology/README.md` | Scaffold only; no behavior approved. |
| **None — see note** | Executable reasoning pipeline | CHOIR prototype (frozen V0.1) | `choir_prototype/` | `choir_prototype/tests/` (75) | `--audit`, portability 1.00 | `choir_prototype/README.md`, `FROZEN.md` | **Outside the approved chain.** Built from research drafts, not from an accepted SPEC. |
| **None — see note** | Model-backed vertical slice | Investment prototype | `applications/investment/prototype_risk_rik/` | `.../tests/` | None | `.../README.md` | **Outside the approved chain, and legacy** per `DECISION-001`. |
| **None — see note** | Document intake | Vertical slice parsing layer | `applications/investment/vertical_slice/parse.py` | `.../tests/test_vertical_slice.py` (`TestDocumentIntake`) | None | `DECISION-002`, `.../README.md` | **Approved and broadened** 2026-08-06: documents may represent packets, never interpret them. |
| **None — see note** | End-to-end execution path | Vertical slice run and artifacts | `applications/investment/vertical_slice/run.py` | `.../tests/test_vertical_slice.py` (`TestSliceExecution`, `TestSliceDeterminism`) | Reuses `--replay`; no new metric | `.../README.md` | Downstream of intake it composes frozen V0.1 components only; adds no reasoning. |
| **None — see note** | Institutional workflow (case → material → judgment → decision) | Investment committee workspace | `applications/investment/workspace/` | `.../tests/test_workspace.py` (34) | None | `DECISION-003`, `.../README.md` | **Approved** 2026-08-06. Product layer; computes no judgment. |
| **None — see note** | Append-only institutional history | Judgment supersession | `applications/investment/workspace/cases.py`, `analysis.py` | `TestSupersession` (7) | `verify_ledger` | `DECISION-004` | **Approved and implemented** 2026-08-06. Decisions bind permanently to the judgment they were recorded against. |
| **None — see note** | Institutional material identity | Material Snapshot layer | `applications/investment/workspace/material.py` | `TestMaterialIdentity` (12) | `material_digest`; collision probe | `DECISION-006` | **Approved and implemented** 2026-08-06. Product-layer only; `record_digest` unchanged. |
| **None — see note** | Canonical definition of DAALE | *unresolved* | none | none | none | `DECISION-005` | **Open ADR.** No implementation may assume an answer. |
| `CHOIR_v0.1_RESEARCH_FREEZE.md` §3 | Frozen commitments, as executable contract | DAALE conformance lock (Phase 0) | `daale/conformance/` | `daale/tests/test_conformance.py` (21) | 28 commitments: 20 conforming, 8 unexercised, 0 unresolved | `daale/README.md` | **First row with a real upstream source.** §3 is accepted frozen content; the register transcribes it and the lock resolves every citation. No `DECISION-005` dependency. |
| **None — see note** | Engine boundary (product must not reason) | Workspace analysis projection | `applications/investment/workspace/analysis.py` | `TestJudgment.test_judgment_matches_the_engine_directly`, `TestSynthesisBoundary` | None | `.../README.md` | Judgment is a projection of the persisted record, extending commitment E9 into the product. |

## Unlinked Implementation

This matrix exists to record approved links from specifications to artifacts.
For most rows it still cannot, because **every `choir/specifications/SPEC-*.md`
file is empty** while five executable code areas exist.

The traceability chain therefore has no upstream end *for those rows*. This is
recorded rather than hidden, per the maintenance note below about keeping
`Pending` visible — and because a project whose thesis is that reasoning must be
traceable should not quietly exempt its own artifacts from traceability.

**One end now exists.** `CHOIR_v0.1_RESEARCH_FREEZE.md` §3 is accepted, frozen
content stating twenty-eight commitments concretely enough to check, and
`daale/conformance/` transcribes them into a register whose every citation is
resolved mechanically. That does not populate the `SPEC-*` files and does not
substitute for them; it means the frozen commitments — as distinct from the
unwritten specifications — now have a checkable downstream chain, and that
breaking a link in it fails a test. Two findings surfaced immediately and are
carried rather than papered over: eight commitments have no evidence at all, and
**E12 ("Nothing is deleted") is marked demonstrated while nothing in the
repository is cited for it.**

The research programme in `choir/research/phase-*/` supplies the substance the
prototype was actually built from, and `choir/research/README.md` §5.1 maps
each empty `SPEC-*` file to the research that would populate it. Populating
those files is a specification act requiring approval; it is not maintenance.

## Maintenance Notes

- Add rows only when the source specification and implementation relationship
  are documented.
- Keep `Pending` values visible instead of hiding missing artifacts.
- If a row requires an architecture decision, write the decision note first and
  leave the row blocked until approval.
