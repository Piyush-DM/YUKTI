# Rubric candidate-set decision record — v1

**Status: FROZEN 2026-09-14.** The 8/2/1 split below is the fixed input to
`RUBRIC_v1.md` and everything downstream of it. No retroactive tweaking of the
split unless new evidence genuinely invalidates a candidate — the two
accepted-but-unresolved items (#4, #6) are worked *forward*, in
`RUBRIC_v1.md`, not by editing this record. A v2 snapshot is expected once
they resolve; that will be a version transition, not a correction of this one.

**Date:** 2026-09-11 (frozen 2026-09-14)
**Why this lives in `experiments/` and not `choir/research/` or
`docs/architecture/`:** it is neither a CHOIR research deliverable (the
Vedic-to-institutional-reasoning translation cycle in `choir/research/` — see
that directory's `README.md`, which reserves R001–R007 for a specific,
already-scoped 18-document programme this doesn't belong to) nor an
architecture ruling in the `docs/architecture/DECISION-*` sense (nothing here
binds an implementation choice). It is design-governance research, explicitly
provisional, which is what `experiments/` already holds — see
`../rubric_reproduction/` and `../messy_intake/` for the same pattern.

---

## 1. What this is

Two distinct artifacts, not to be confused with each other:

- **Level 1 — candidate rubric dimensions.** Eleven proposed properties a
  defensible institutional reasoning engine must have (framing, provenance,
  evidence fitness, alternatives, inference soundness, uncertainty,
  reproducibility, independent challenge, decision thresholds, auditability,
  transparency), each drawn from an external standard or professional
  discipline (ISO/IEC 15026-2 assurance cases, PCAOB AS 1105, W3C PROV, NIST
  AI RMF, OECD AI Principles, EU AI Act Art. 13, IAASB professional
  skepticism, intelligence-community Analysis of Competing Hypotheses). Full
  per-dimension detail (What / Why / How to measure / Failure modes /
  Sources / Limitations) was supplied 2026-09-11 and is not reproduced here
  — this record captures the sieve's decision, not the source material.
- **Level 2 — the meta-rubric.** The sieve that decides whether a Level-1
  candidate deserves to become an actual engineering requirement, rather than
  a sophisticated-sounding but untestable principle. It is a design-governance
  artifact and is **not** intended to become part of YUKTI's runtime
  reasoning architecture.

The risk this two-level structure exists to prevent, stated directly: it is
possible to produce ten extremely well-cited rubric dimensions that are
nonetheless bullshit as engineering requirements — "YUKTI must be
transparent" sounds excellent and tests nothing.

## 2. The meta-rubric (the sieve)

Ten criteria applied to each Level-1 candidate:

| Criterion | Question |
|---|---|
| Necessity | Does this capture a genuinely important failure mode? |
| Non-redundancy | Is it meaningfully different from the other candidates? |
| Validity | Is there evidence that satisfying it relates to better reasoning/decisions? |
| Operationalizability | Can we actually test whether YUKTI satisfies it? |
| Falsifiability | Can YUKTI demonstrably fail it? |
| Evidence strength | How strong is the research supporting the requirement? |
| Scope | Does it apply to an institutional reasoning engine, not merely an AI assistant? |
| Independence | Does it measure something distinct from traceability/determinism restated? |
| Failure sensitivity | Would this catch a materially dangerous reasoning failure? |
| Engineering usefulness | Can the result become an actual design/test requirement? |

## 3. The candidate pool and verdict

**8 accepted → 2 accepted-but-unresolved (rework required before freezing) → 1
merged/cut.**

| # | Candidate | Verdict | Why |
|---|---|---|---|
| 1 | Decision Framing & Scope | **Accepted** | Highest necessity and failure-sensitivity of the set. YUKTI has no structured framing step today — this is the architecture's largest current gap. |
| 2 | Evidence Provenance & Integrity | **Accepted** | Already substantially implemented (`IntakeRecord`, evidence spans, `material_digest`). Best-operationalized candidate as-is. |
| 3 | Evidence Fitness (relevance/reliability/sufficiency) | **Accepted, partial** | Non-redundant against Provenance — verified-but-irrelevant evidence is a real, distinct failure. YUKTI implements only the *reliability* third (evidence-quality rank); relevance and sufficiency are unimplemented. |
| 4 | Hypotheses & Alternatives Management | **Accepted, unresolved** | Necessity is real. As written, its test ("count hypotheses considered") assumes open-ended hypothesis generation, which does not describe YUKTI's four *fixed* kernels. Stays mandatory; must be redefined for a fixed-kernel architecture before it can be operationalized. |
| 5 | Inference Soundness / Warrant | **Accepted** | Best-grounded of the eleven in what already exists — this is E9 and X4 in different vocabulary. |
| 6 | Uncertainty Management | **Accepted, unresolved** | Necessity is real; the source material's own evidence-strength was its weakest section. Open question that must be settled before freezing: does "quantify uncertainty" mean CHOIR's ordinal HIGH/MODERATE/LOW/INSUFFICIENT bands are insufficient, or is the candidate asking for probabilistic-confidence machinery CHOIR does not have and should not import wholesale? Stays mandatory; needs a YUKTI-specific treatment built on the ordinal bands actually in use, not an import of probabilistic confidence apparatus. |
| 7 | Reproducibility & Determinism | **Accepted — foundational control, not a peer-weight validity dimension** | Necessary; demoted deliberately, not cut. The source material states reproducibility ≠ correctness. This is not hypothetical for this project: `experiments/rubric_reproduction/FINDINGS.md` (2026-09-11, same day) is a live instance — reasoning variance measured at 0 across 8–10 replays, while the underlying rubric's correctness remained an open question throughout. A system can be perfectly reproducible and consistently wrong. It still gets tested and enforced; it does not carry equal conceptual weight to Warrant or Independent Challenge. |
| 8 | Independent Challenge & Review | **Accepted** | Highest failure-sensitivity for YUKTI specifically. Currently a hard zero: model-proposes/human-confirms (the shipped intake path, still ungoverned per `DECISION-008`) is single-pass confirmation, not independent challenge. |
| 9 | Decision Criteria & Thresholds | **Accepted** | Maps directly onto the kernels' undocumented numeric thresholds (e.g. `DOMINANCE_MARGIN = 3`). YUKTI already gets one part of this right independently — institutional confidence takes the weakest review area rather than an average, which is exactly the "don't average out a weak pillar" principle this candidate names. |
| 10 | Auditability & Reconstruction Capability | **Accepted** | Already substantially implemented (append-only ledger, the `material_digest`/`record_digest` pair, `verify_ledger`). |
| 11 | Transparency & Explainability | **Merged / cut as a standalone dimension** | Fails non-redundancy against Warrant (an intelligible derivation) and Auditability (a legible log) directly — the source material flagged this itself. Its proposed test ("can a stakeholder summarize the rationale") is also the softest of the eleven: a survey, not a mechanical check, unlike every other candidate's test. Keeping it separate risks double-counting the same failure under three names. |

## 4. The three calls made explicitly, and why

**Reproducibility stays, demoted rather than cut.** The temptation is to treat
"reproducibility ≠ correctness" as a reason to drop it toward irrelevance.
Rejected: the distinction is exactly why it matters as a *foundational
control* — it catches drift, tampering, and implementation bugs, which
Warrant and Independent Challenge do not catch on their own. It is tested and
enforced like every other accepted candidate; it simply does not sit at the
same conceptual weight as the validity dimensions.

**#4 and #6 stay mandatory despite being unresolved.** The alternative — quietly
dropping them because they don't yet fit the architecture, or quietly bending
the architecture to fit their as-written form — was rejected on the same
principle either way: the research does not get to dictate the architecture
by default, and the architecture does not get to veto a real requirement by
default. Both stay open, explicitly, until each is redefined against what
YUKTI actually is (fixed kernels, ordinal bands) rather than what a
general-purpose reasoning system might be.

**#11 merges rather than surviving as a diluted tenth-and-a-half pillar.** Its
content is real and worth keeping — an intelligible, legible system is
better than an opaque one — but it is not an independent failure mode; it is
a quality property *of* Warrant and Auditability, not a third thing.

## 5. Next steps

1. Rework #4 (Hypotheses & Alternatives Management) into a form testable
   against four fixed, independent kernels rather than open-ended hypothesis
   generation.
2. Rework #6 (Uncertainty Management) into a form built on CHOIR's existing
   ordinal confidence bands, not an import of probabilistic machinery.
3. Re-run the meta-rubric (§2) against both revised definitions.
4. Only then freeze a final set and retire this snapshot as superseded by v2.
