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

## Unlinked Implementation

This matrix exists to record approved links from specifications to artifacts.
It currently cannot, because **every `choir/specifications/SPEC-*.md` file is
empty** while two executable code areas exist.

The traceability chain therefore has no upstream end. This is recorded rather
than hidden, per the maintenance note below about keeping `Pending` visible —
and because a project whose thesis is that reasoning must be traceable should
not quietly exempt its own artifacts from traceability.

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
