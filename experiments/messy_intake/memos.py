"""Messy prose test set, each with the verdict the frozen engine must reach.

The set makes two claims at once:

1. Messy prose and clean prose reach the **same judgment**. Memo 1 is the
   worked example rewritten the way a person actually writes -- words for
   numbers, shorthand units, asides -- and it must land on the reference
   verdict unchanged. A memo that should not support a decision must not
   produce one anyway (memos 3 and 4).

2. Once a reader has produced a structured evidence record, that record is the
   reproducibility boundary. The engine, replayed against one frozen record any
   number of times, must return a byte-identical reasoning record. Reading
   variance is allowed and measured; reasoning variance is a hard failure.

Each memo is paired with the verdict computed from the frozen engine on the
figure set the memo is meant to yield. That pairing is fixed: if the reader
drifts, the reached verdict and the recorded verdict stop matching and the run
says so. A mismatch is a finding about the reader, never a reason to edit the
expectation.

Run:
    python -m experiments.messy_intake.memos              # keyword reader
    python -m experiments.messy_intake.memos --model      # language model
    python -m experiments.messy_intake.memos --model --repeat 5   # reading variance
    python -m experiments.messy_intake.memos --write      # dump the memos as .txt
"""

from __future__ import annotations

import argparse
import pathlib
import sys
from dataclasses import dataclass

REPOSITORY_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

try:  # the launcher loads .env for the server; the harness must do it itself
    from dotenv import load_dotenv

    load_dotenv(REPOSITORY_ROOT / ".env")
except ImportError:  # pragma: no cover - only the --model path needs a key
    pass

from applications.investment.workspace.assistant import (  # noqa: E402
    AssistantUnavailable,
)
from experiments.messy_intake.evidence import (  # noqa: E402
    KEYWORD_READER,
    MODEL_READER,
    EvidenceRecord,
    read_evidence,
    reading_variance,
)

FROZEN_DIR = pathlib.Path(__file__).resolve().parent / "frozen"


@dataclass(frozen=True)
class Expected:
    """The verdict the frozen engine reaches for this memo's figure set."""

    recommendation: str
    confidence: str
    conditions: int
    contested: int
    outstanding: int

    def as_tuple(self) -> tuple[str, str, int, int, int]:
        return (
            self.recommendation,
            self.confidence,
            self.conditions,
            self.contested,
            self.outstanding,
        )


@dataclass(frozen=True)
class Memo:
    name: str
    why: str
    text: str
    expected: Expected


# --------------------------------------------------------------------------
# 1. The control. Same figures as the worked example, written the way a person
#    actually writes them. Messiness must not move the verdict.
# --------------------------------------------------------------------------

CONTROL = Memo(
    name="1-control-messy",
    why="Same material as the worked example, maximally messy prose. "
    "The verdict must be identical -- messiness is not information.",
    text="""\
Notes from the Orbital call, unedited.

Topline: they closed the year at around eighteen million of recurring revenue,
and the independent audit signed that off. Growth was a shade over sixty
percent - 62 exactly, same audit. Margin sits at 74 points on those audited
statements.

Burn is running about 1.4m/mo against roughly twenty-one million of cash at year
end, both per the audit.

Concentration is the thing I'd push on: biggest logo is 38 pct of revenue, that's
straight from the management deck. Deck also claims NRR of 104. Churn is ~11%
although the reference calls with customers muddy that a little.

Third party market sizing puts the addressable market at 8.4 billion, growing 19
a year, with 14 players named.

Cap table: founders keep 56% of the votes and there's one independent seat on the
certified capitalisation table. Accounts are audited. They report monthly per the
deck.
""",
    expected=Expected("Proceed With Conditions", "Low", 5, 1, 0),
)


# --------------------------------------------------------------------------
# 2. A genuinely good company, cleanly evidenced. Everything audited, nothing
#    conditional. Tests that the engine can say yes without hedging.
# --------------------------------------------------------------------------

STRONG = Memo(
    name="2-strong",
    why="A clean, well-evidenced company with no conditional findings. "
    "Tests that PROCEED at HIGH confidence is reachable at all.",
    text="""\
Helio Systems, Series B. Everything below comes off the independent audit unless
I say otherwise.

Recurring revenue finished at twenty-four million, up 58% year over year. Gross
margin is 82%. They burn 700k a month against thirty million of cash, so runway
is long.

Customer base is spread - largest customer is only 12% of revenue. Net revenue
retention 128%, logo churn 4%.

The audit also carries the market work: addressable market nine billion, growing
24% a year, five direct competitors.

Per the certified capitalisation table, founders hold 31% of the votes and there
are three independent board seats. Statements are audited and they report
monthly.
""",
    expected=Expected("Proceed", "High", 0, 0, 0),
)


# --------------------------------------------------------------------------
# 3. A bad company, thinly evidenced. Tests that the engine declines, and that
#    it does so on the weighted findings rather than on vibes.
# --------------------------------------------------------------------------

WEAK = Memo(
    name="3-weak",
    why="A company that should not clear. Tests that DECLINE is reached, "
    "and that weak sourcing caps confidence rather than blocking a verdict.",
    text="""\
Pallas Retail - everything here is from the management deck, nothing independent.

ARR three million, growth only 6% year on year, gross margin 34%. They're burning
600k a month with three million in the bank.

Their largest customer is 61% of revenue. Net revenue retention 74%, logo churn
29%.

Market: third-party research puts the addressable market at 800 million growing
3% a year with 31 competitors.

Founders hold 78% of the votes, no independent board seats. Statements are
unaudited. They report annually.
""",
    expected=Expected("Decline", "Low", 2, 0, 0),
)


# --------------------------------------------------------------------------
# 4. Almost nothing on file, and the memo says so twice. Tests INSUFFICIENT
#    BASIS -- and that "no cap table" does not register a cap table.
# --------------------------------------------------------------------------

THIN = Memo(
    name="4-thin",
    why="A near-empty packet whose closing line asserts absences. Tests "
    "INSUFFICIENT BASIS, and that a negated source mention creates no source.",
    text="""\
Very early look at Kestrel Instruments, almost nothing firm yet.

From the founder's email summary: they're at about nine hundred thousand of
recurring revenue, and he says growth is 140%.

The trade association sector note sizes the market at two billion, growing 11% a
year.

Nothing else has been shared. No accounts, no cap table, no customer data.
""",
    expected=Expected("Insufficient Basis", "Insufficient", 0, 0, 11),
)


# --------------------------------------------------------------------------
# 5. Two review areas that genuinely disagree, with neither dominating. Tests
#    that a live disagreement is reported rather than resolved by weight.
# --------------------------------------------------------------------------

SPLIT = Memo(
    name="5-contested",
    why="Financial position and Revenue quality reach opposite conclusions "
    "with no dominant side. Tests CONTESTED -- the engine reports the split.",
    text="""\
Vantage Data, partial pack. Only the audited financials have come through so far.

Per the independent audit: recurring revenue is ten million, growth 22%, and
gross margin is a healthy 78%.

Same audit on the customer side: largest customer is 30% of revenue, net revenue
retention is 88%, and logo churn is 5%.

Nothing yet on cash, burn, the market, or the cap table - those are still
outstanding with the company.
""",
    expected=Expected("Contested", "Moderate", 1, 1, 9),
)


MEMOS = (CONTROL, STRONG, WEAK, THIN, SPLIT)


@dataclass(frozen=True)
class Outcome:
    memo: Memo
    evidence: EvidenceRecord
    frozen_path: pathlib.Path
    reasoning_stable: bool
    replays: int
    record_digest_count: int
    verdict: tuple[str, str, int, int, int] | None
    note: str = ""

    @property
    def verdict_matches(self) -> bool:
        return self.verdict == self.memo.expected.as_tuple()


def run_memo(memo: Memo, *, reader: str, replays: int) -> Outcome:
    """Read the memo, freeze the evidence, then replay it through the engine.

    The freeze is literal: the evidence record is written to disk before the
    engine is run, and the engine is run only from that record. Replaying it
    ``replays`` times and checking the reasoning record is invariant is the
    reproducibility claim; the verdict comparison is secondary to it.
    """
    try:
        evidence = read_evidence(memo.name, memo.text, reader=reader)
    except AssistantUnavailable as exc:
        return Outcome(
            memo=memo,
            evidence=EvidenceRecord(reader, memo.name, "", (), (), ()),
            frozen_path=FROZEN_DIR / f"{memo.name}.{reader}.evidence.json",
            reasoning_stable=True,
            replays=0,
            record_digest_count=0,
            verdict=None,
            note=f"reader unavailable: {exc}",
        )
    FROZEN_DIR.mkdir(exist_ok=True)
    frozen_path = FROZEN_DIR / f"{memo.name}.{reader}.evidence.json"
    frozen_path.write_text(evidence.to_json(), encoding="utf-8")

    if not evidence.figures:
        return Outcome(
            memo=memo,
            evidence=evidence,
            frozen_path=frozen_path,
            reasoning_stable=True,
            replays=0,
            record_digest_count=0,
            verdict=None,
            note="no citeable evidence was read; the engine was not run",
        )

    persist_root = FROZEN_DIR / f"{memo.name}.{reader}.case"
    check = evidence.replay_is_stable(times=replays, persist_root=persist_root)
    verdict = check.verdict if check.stable else None
    return Outcome(
        memo=memo,
        evidence=evidence,
        frozen_path=frozen_path,
        reasoning_stable=check.stable,
        replays=replays,
        record_digest_count=len(check.record_digests),
        verdict=verdict,
        note=(
            ""
            if check.stable
            else f"engine produced {len(check.record_digests)} distinct records "
            f"from one frozen evidence record: {sorted(check.verdicts)}"
        ),
    )


def _report(outcomes: list[Outcome]) -> int:
    reasoning_failures = [o for o in outcomes if not o.reasoning_stable]
    verdict_diffs = [
        o for o in outcomes if o.verdict is not None and not o.verdict_matches
    ]

    print("evidence frozen, then replayed through the engine\n")
    for outcome in outcomes:
        memo, evidence = outcome.memo, outcome.evidence
        caps = "SRC-CAPTABLE" in {s.label for s in evidence.sources}
        header = (
            f"{memo.name:<16} reader={evidence.reader}  "
            f"evidence={evidence.digest[:12]}  "
            f"figures={len(evidence.figures):>2}/15"
        )
        if evidence.unattributed:
            header += f"  (+{len(evidence.unattributed)} uncited)"
        print(header)
        print(f"    sources: {sorted(s.label for s in evidence.sources) or '(none)'}")

        if outcome.verdict is None and not outcome.reasoning_stable:
            print(f"    REASONING VARIANCE -- {outcome.note}")
        elif outcome.verdict is None:
            print(f"    {outcome.note}")
        else:
            got = outcome.verdict
            mark = "MATCH " if outcome.verdict_matches else "DIFFER"
            print(
                f"    reasoning: 1 record across {outcome.replays} replays  "
                f"[{mark}]"
            )
            print(
                f"    verdict:   {got[0]} / {got[1]}  "
                f"(conditions {got[2]}, contested {got[3]}, outstanding {got[4]})"
            )
            if not outcome.verdict_matches:
                exp = memo.expected
                print(
                    f"    sealed:    {exp.recommendation} / {exp.confidence}  "
                    f"(conditions {exp.conditions}, contested {exp.contested}, "
                    f"outstanding {exp.outstanding})  <- reading, not reasoning"
                )
        if memo.name == "4-thin":
            print(
                f"    memo-4 guard: negated 'no cap table' -> "
                f"cap-table source registered: {caps}  "
                f"({'FAIL' if caps else 'ok'})"
            )
        print()

    print("-" * 72)
    print(
        f"reasoning variance: {len(reasoning_failures)} "
        f"(must be 0 -- one frozen record, one engine output)"
    )
    print(
        f"verdict vs sealed:  {len(outcomes) - len(verdict_diffs)}"
        f"/{len(outcomes)} reproduced"
        + (
            f"; {len(verdict_diffs)} moved in the read: "
            f"{[o.memo.name for o in verdict_diffs]}"
            if verdict_diffs
            else ""
        )
    )
    caps_fail = any(
        "SRC-CAPTABLE" in {s.label for s in o.evidence.sources}
        for o in outcomes
        if o.memo.name == "4-thin"
    )
    print(f"memo-4 negation:    {'FAIL' if caps_fail else 'fixed'}")

    return 1 if (reasoning_failures or caps_fail) else 0


def _repeat(reader: str, runs: int) -> int:
    """Read every memo ``runs`` times and report how the evidence varied."""
    print(f"reading each memo {runs}x with the {reader} reader\n")
    unstable: list[str] = []
    for memo in MEMOS:
        try:
            variance = reading_variance(
                memo.name, memo.text, reader=reader, runs=runs
            )
        except AssistantUnavailable as exc:
            print(f"{memo.name:<16} reader unavailable: {exc}\n")
            continue
        digests = variance.digests
        line = (
            f"{memo.name:<16} {variance.distinct} distinct / {runs} reads   "
            f"{[d[:8] for d in sorted(set(digests))]}"
        )
        print(line)
        if not variance.stable:
            unstable.append(memo.name)
            for detail in variance.differences():
                print(f"    {detail}")
        print()

    print("-" * 72)
    if unstable:
        print(
            f"reading variance present in: {unstable}\n"
            "each distinct evidence record is internally deterministic through "
            "the engine; the variance above is entirely in the read."
        )
    else:
        print("no reading variance: every read produced the same evidence record.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="messy-intake")
    parser.add_argument(
        "--model", action="store_true", help="read figures with the language model"
    )
    parser.add_argument(
        "--repeat",
        type=int,
        metavar="N",
        help="read each memo N times and report evidence-record variance",
    )
    parser.add_argument(
        "--replays",
        type=int,
        default=8,
        help="times to replay each frozen record through the engine (default 8)",
    )
    parser.add_argument(
        "--write", action="store_true", help="write the memos out as .txt and stop"
    )
    args = parser.parse_args(argv)

    here = pathlib.Path(__file__).resolve().parent
    if args.write:
        for memo in MEMOS:
            (here / f"{memo.name}.txt").write_text(memo.text, encoding="utf-8")
        print(f"wrote {len(MEMOS)} memos to {here}")
        return 0

    reader = MODEL_READER if args.model else KEYWORD_READER
    if args.repeat:
        return _repeat(reader, args.repeat)

    outcomes = [
        run_memo(memo, reader=reader, replays=args.replays) for memo in MEMOS
    ]
    return _report(outcomes)


if __name__ == "__main__":
    raise SystemExit(main())
