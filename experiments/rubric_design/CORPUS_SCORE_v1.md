# Corpus score — RUBRIC_v1, first pass (2026-09-14)

Step 7 of `RUBRIC_v1.md`'s own pipeline: run the rubric against what already
exists in the repo, and check whether the dimensions actually discriminate
or move together. They mostly discriminate — but two genuine defects turned
up in the process, one in the rubric's own definitions and one a real bug in
an experiment harness. Both are reported below, not smoothed over.

## The corpus

| Group | What | n | Produced by |
|---|---|---|---|
| **A** | `rubric_reproduction` gemini-2.5-flash L-lo responses | 10 | external model imitating the rubric |
| **B** | `messy_intake` scenarios | 5 | real frozen engine, keyword + model readers |
| **C** | `orbital-series-b` worked example | 1 | real frozen engine, static reference |
| **D** | `meridian-robotics` — a real, persisted, **decided** case | 1 | real frozen engine, through the actual workspace app, with a committee ledger entry |

D was not anticipated in `RUBRIC_v1.md` §7 — found while scoring, at
`reports/workspace/meridian-robotics/`. It's the only item in the corpus with
a genuine committee decision attached (`Approved with conditions`, ledger
rationale on file), which makes it the sharpest test of D1, D8, and D9.

## Scores

| Dim | A (n=10) | B (n=5) | C (n=1) | D (n=1) | Discriminates on this corpus? |
|---|---|---|---|---|---|
| D1 Framing | **untestable** | **untestable** | **untestable** | PARTIAL | No — see defect 1 |
| D2 Provenance | PASS 10/10 | PASS 5/5 | PASS | PASS | No — every guard held |
| D3 Evidence Fitness | PASS (inherited) | PASS/mixed | PASS | not checked | Weakly — see caveat |
| D5 Warrant | **PASS 10/10** | PASS (trivial) | PASS (trivial) | PASS (trivial) | **Yes — sharply, by corpus group** |
| Repro (gate) | n/a — wrong axis | PASS | PASS | PASS (same code path) | n/a for A, PASS elsewhere |
| D8 Independent Challenge | FAIL 10/10 | FAIL 5/5 | FAIL | **FAIL** | No — uniform FAIL, including real data |
| D9 Thresholds | PARTIAL | PARTIAL | PARTIAL | PARTIAL | No — corpus-level property, as predicted |
| D10 Auditability | PASS 10/10 | **FAIL 5/5** | PASS | PASS | **Yes — sharply, and it's a real bug** |
| D4′ Area Independence | 2 data points, both fire correctly | (source of 1 of the 2) | (source of the other) | no conflict case | Provisional — see below |
| D6′ Ordinal Uncertainty | PASS (a), (b)/(c) untested adversarially | PASS by construction | PASS by construction | PASS by construction | Provisional — see below |

## The two real findings

### D10 fails on the messy_intake corpus, and it's a fixable bug, not an architecture gap

Confirmed by checking what's actually on disk:
`experiments/messy_intake/frozen/*.evidence.json` exists for all 5 memos —
but no `05-record.json` for any of them. `memos.py`'s `run_memo` calls
`EvidenceRecord.replay()` inside `tempfile.TemporaryDirectory()`, which is
deleted the moment the `with` block exits. The verdict gets printed and
compared; the reasoning trace that produced it is thrown away on every run.

Corpus C and D prove this isn't an architecture limitation —
`reports/vertical-slice/orbital-series-b/05-record.json` and
`reports/workspace/meridian-robotics/judgments/JUDGMENT-001/05-record.json`
are both sitting on disk, fully cold-auditable, produced by the same
`request_judgment` code path `messy_intake` calls. The harness just doesn't
keep what it computes. This is the one dimension in the whole exercise that
produced a clean PASS/PASS/FAIL/PASS pattern instead of moving with
everything else — proof D10 is measuring something D2/D5/Repro don't, and a
concrete, small fix (persist to a real directory instead of a temp one, or
copy `05-record.json` out before the context manager exits).

### D8 is FAIL everywhere, including the one real committee decision in the repo

Not a corpus artifact — checked directly against `meridian-robotics`, the
only item here with an actual committee ledger entry. Two concrete signals,
both null:

- **0 of 15 intake records were edited.** Every model-proposed figure was
  accepted as-is (`edited: false` on all 15, single `recorded_on` date) —
  no correction event, which `IntakeRecord.edited` exists specifically to
  distinguish from a rubber-stamp.
- **The ledger rationale restates the judgment rather than contesting it.**
  `"Runway and concentration to be resolved before drawdown"` names exactly
  the conditions the judgment itself already generated
  (`support leads, but conditional findings remain outstanding`) — nothing
  in the record indicates the committee surfaced anything the automated
  pipeline hadn't already flagged.

This doesn't mean the decision was wrong. It means there is currently no
artifact in this repository, real or experimental, that would let anyone
distinguish a genuinely challenged decision from a rubber-stamped one. That
is `DECISION-008`'s gap, now with a load-bearing example instead of an
abstract description.

## One defect in the rubric itself, not the corpus

**D1 (Framing) is untestable against every engine-level artifact.**
`analysis.compose_document` deliberately excludes `requested_decision` and
`thesis` from what reaches the frozen engine (`context_yukti.md` §6,
`analysis.py`'s own docstring: case metadata "exists for people rather than
for reasoning" and would change the document without changing a single
conclusion). That's the right design choice for the engine — but it means
D1's observable-evidence definition, written against the workspace `Case`
object, has nothing to check in `05-record.json`, the L-lo response format,
or the vertical-slice document. It only produced a real score against
corpus D, the one item with an actual `Case`.

**Where D was checkable, it wasn't clean.** `meridian-robotics.thesis` is an
empty string. `requested_decision` is set and prior to analysis, so PASS on
that half; `thesis` — the actual framing rationale beyond the bare ask — was
never filled in, so PARTIAL overall, not PASS. A real, if narrow, framing
gap in the one real case in the corpus.

**Consequence for `RUBRIC_v1.md`:** D1 needs a redefinition scoped to what's
actually observable at the artifact being scored — for engine-level
artifacts, the nearest available signal is probably whether the *packet's*
own scope (company, sector, stage, what schedule was applied) is stated and
unchanged, not the committee-level `requested_decision`/`thesis` pair. Flagged
here, not fixed — fixing a dimension's definition after seeing it fail to
apply is a real edit to `RUBRIC_v1.md` and should happen as a deliberate
step, not folded into a corpus-scoring pass.

## D4′ and D6′ — still provisional, evidence got slightly stronger

**D4′ (Area Independence).** `RUBRIC_v1.md` named one data point
(`messy_intake`'s `5-contested`). Scoring the corpus surfaced a second,
independent of it: `orbital-series-b` itself carries one genuine
topic-level disagreement in its ground truth (`revenue_quality`), which
gemini reproduced correctly in all 10 samples (`agreements`/`disagreements`
tier-2 fields matched exactly, per `FINDINGS.md`). Two real conflict cases,
different topics, both fired correctly, neither corpus shows kernels
collapsing into perfect correlation. Still short of the corpus-level *rate*
`RUBRIC_v1.md` asked for before promotion — a benchmark with a known ratio
of agreement-expected to conflict-expected cases, not two hand-picked
positives — but the provisional status is measurably less shaky than when it
was written.

**D6′ (Ordinal Uncertainty Fidelity).** Sub-check (a) — stated confidence
never exceeds the weakest cited evidence's rank — checked mechanically
across all 10 gemini samples: holds 10/10, exactly. Sub-checks (b) and (c)
look fine on inspection (limiting-factor strings name specific sources, not
generic labels; INSUFFICIENT and LOW carry different stated causes) but
were not adversarially stress-tested — nothing in this corpus was
constructed specifically to probe the absent-vs-weak boundary the way
`5-contested` was constructed to probe D4′. Remains provisional for that
reason, not because anything failed.

## What this pass didn't do

- **D3** was scored by inheriting the "findings/citations matched ground
  truth" result from `compare.py`, not by independently re-reading each
  citation's relevance. `RUBRIC_v1.md` flagged D3 as the one dimension
  requiring real semantic judgment rather than a mechanical check — this
  pass didn't do that judgment fresh, it borrowed a proxy. Worth doing
  properly before D3 is trusted on a corpus that hasn't already been
  independently verified by other means.
- **No adversarial corpus.** Every item scored here was produced by a
  guard-railed pipeline (fabrication checks, digest verification, a
  frozen engine). D2, D5, Repro, and D6′(a) all scored a clean PASS
  everywhere partly *because* nothing here was built to break them. D10's
  and D8's failures are real precisely because they came from artifacts
  that weren't specifically hardened against those two checks. The next
  useful corpus addition is deliberately broken cases — a fabricated
  citation, a rule misapplication, a rubber-stamped review — to find out
  whether D2/D5/D6′ actually catch what they claim to, rather than simply
  never having been asked to.
