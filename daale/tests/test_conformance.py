"""Tests for the DAALE Phase 0 conformance lock.

Three things are defended here, in rising order of importance.

1. **The register transcribes the freeze.** Every §3 commitment is present
   exactly once, with the support status the freeze assigns it.
2. **The resolver actually resolves.** A checker that always returns "found" is
   indistinguishable from a working one until you hand it something that does
   not exist. ``test_a_fabricated_citation_does_not_resolve`` is that negative
   control, and it is the test that makes every other passing result mean
   something.
3. **The lock carries no engine dependency.** This is what allows Phase 0 to
   proceed while ``DECISION-005`` is open, so it is asserted mechanically in a
   subprocess rather than claimed in a docstring.
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from datetime import date
from pathlib import Path

from daale.conformance import (
    COMMITMENTS,
    Commitment,
    Evidence,
    EvidenceKind,
    Outcome,
    Status,
    as_dict,
    build_evidence_index,
    evaluate,
    lock,
    render,
)
from daale.conformance.commitments import ARCHITECTURAL, EPISTEMIC, EXECUTION

ROOT = Path(__file__).resolve().parents[2]

EXPECTED_IDS = (
    tuple(f"E{n}" for n in range(1, 14))
    + tuple(f"A{n}" for n in range(1, 12))
    + tuple(f"X{n}" for n in range(1, 5))
)


class TestRegister(unittest.TestCase):
    """The register is a faithful transcription of research freeze §3."""

    def test_every_frozen_commitment_is_present_once(self) -> None:
        """§3 states 13 epistemic, 11 architectural and 4 execution commitments."""
        ids = tuple(c.commitment_id for c in COMMITMENTS)
        self.assertEqual(ids, EXPECTED_IDS)
        self.assertEqual(len(set(ids)), len(ids))

    def test_every_commitment_carries_a_statement(self) -> None:
        """A commitment nobody can read is not a contract."""
        for commitment in COMMITMENTS:
            with self.subTest(commitment=commitment.commitment_id):
                self.assertTrue(commitment.statement.strip())

    def test_groups_are_the_three_the_freeze_declares(self) -> None:
        """No fourth grouping is invented."""
        groups = {c.group for c in COMMITMENTS}
        self.assertEqual(groups, {EPISTEMIC, ARCHITECTURAL, EXECUTION})

    def test_unimplemented_commitments_cite_nothing(self) -> None:
        """A commitment the freeze marks assumed or specified has no evidence.

        Citing evidence for something the freeze says is not implemented would
        be the register asserting more than its source does.
        """
        for commitment in COMMITMENTS:
            if commitment.status in (Status.ASSUMED, Status.SPECIFIED):
                with self.subTest(commitment=commitment.commitment_id):
                    self.assertEqual(commitment.evidence, ())


class TestResolution(unittest.TestCase):
    """The resolver distinguishes evidence that exists from evidence that does not."""

    def setUp(self) -> None:
        self.index = build_evidence_index(ROOT)

    def test_a_fabricated_citation_does_not_resolve(self) -> None:
        """The negative control. Without it, every other pass is meaningless."""
        fabricated = Commitment(
            "Z1",
            EXECUTION,
            "A commitment citing a test that was never written.",
            Status.DEMONSTRATED,
            (Evidence(EvidenceKind.TEST, "TestThisWasNeverWritten"),),
        )
        report = evaluate((fabricated,), self.index)
        self.assertIs(report.results[0].outcome, Outcome.UNRESOLVED)
        self.assertFalse(report.holds)

    def test_a_fabricated_check_does_not_resolve(self) -> None:
        """The same control for the check resolver, which uses a different index."""
        fabricated = Commitment(
            "Z2",
            EXECUTION,
            "A commitment citing a verification surface that does not exist.",
            Status.DEMONSTRATED,
            (Evidence(EvidenceKind.CHECK, "--no-such-flag"),),
        )
        report = evaluate((fabricated,), self.index)
        self.assertIs(report.results[0].outcome, Outcome.UNRESOLVED)

    def test_an_open_decision_does_not_resolve(self) -> None:
        """DECISION-005 is open, so anything resting on it must fail to resolve.

        This is the lock refusing to let an unaccepted ADR support a
        conformance claim, which is the governance rule made mechanical.
        """
        resting_on_an_open_adr = Commitment(
            "Z3",
            EXECUTION,
            "A commitment resting on an ADR that has not been accepted.",
            Status.DEMONSTRATED,
            (Evidence(EvidenceKind.DECISION, "DECISION-005"),),
        )
        report = evaluate((resting_on_an_open_adr,), self.index)
        self.assertIs(report.results[0].outcome, Outcome.UNRESOLVED)
        self.assertIn("not approved", report.results[0].evidence[0].detail)

    def test_an_approved_decision_resolves(self) -> None:
        """DECISION-001 is approved and is what establishes X3."""
        approved = Commitment(
            "Z4",
            EXECUTION,
            "A commitment resting on an approved ADR.",
            Status.DEMONSTRATED,
            (Evidence(EvidenceKind.DECISION, "DECISION-001"),),
        )
        report = evaluate((approved,), self.index)
        self.assertIs(report.results[0].outcome, Outcome.CONFORMING)

    def test_a_decision_status_stops_at_the_end_of_its_status(self) -> None:
        """Regression: the status run was swallowing the sentence after it.

        ``DECISION-001`` reads "**Status: Approved 2026-08-04.** Recorded
        retrospectively -- the repository ...". Reading to end of line reported
        all of that as the status, which both misquoted the note and dragged
        non-ASCII prose into the artifact.
        """
        self.assertEqual(self.index.decisions["DECISION-001"], "Approved 2026-08-04.")
        self.assertEqual(self.index.decisions["DECISION-005"], "Open. Not accepted.")

    def test_every_recorded_decision_status_is_ascii(self) -> None:
        """Status prose is transcribed from Markdown and must stay printable."""
        for identifier, status in self.index.decisions.items():
            with self.subTest(decision=identifier):
                self.assertTrue(status.isascii())

    def test_no_evidence_is_unexercised_never_conforming(self) -> None:
        """An unchecked commitment must never read as a passing one."""
        uncited = Commitment(
            "Z5",
            EPISTEMIC,
            "A commitment nothing exercises.",
            Status.SPECIFIED,
            (),
        )
        report = evaluate((uncited,), self.index)
        self.assertIs(report.results[0].outcome, Outcome.UNEXERCISED)
        self.assertEqual(report.conforming, ())


class TestLockHolds(unittest.TestCase):
    """The lock, run against this repository as it stands."""

    def setUp(self) -> None:
        self.report = lock(ROOT, COMMITMENTS)

    def test_every_cited_evidence_still_exists(self) -> None:
        """The tripwire. Renaming or deleting cited evidence fails here."""
        broken = {
            result.commitment.commitment_id: [
                item.evidence.name for item in result.evidence if not item.resolved
            ]
            for result in self.report.unresolved
        }
        self.assertEqual(broken, {}, f"cited evidence has gone missing: {broken}")
        self.assertTrue(self.report.holds)

    def test_the_unexercised_set_is_exactly_what_the_freeze_leaves_open(self) -> None:
        """Pinned so that losing coverage is a test failure, not a quiet drift.

        E12 is the one commitment the freeze marks demonstrated while this
        repository cites nothing for it. It is reported as a traceability hole
        rather than hidden, and it is pinned here so that closing it is a
        deliberate act.
        """
        unexercised = {r.commitment.commitment_id for r in self.report.unexercised}
        self.assertEqual(
            unexercised, {"E3", "E4", "E5", "E6", "E7", "E10", "E11", "E12"}
        )

    def test_the_only_unsupported_claim_is_the_one_we_know_about(self) -> None:
        """A commitment marked demonstrated that cites nothing is a finding."""
        holes = {r.commitment.commitment_id for r in self.report.unsupported_claims}
        self.assertEqual(holes, {"E12"})

    def test_every_commitment_is_accounted_for(self) -> None:
        """The three outcomes partition the register with nothing left over."""
        total = (
            len(self.report.conforming)
            + len(self.report.unexercised)
            + len(self.report.unresolved)
        )
        self.assertEqual(total, len(COMMITMENTS))


class TestProjection(unittest.TestCase):
    """The renderer formats the result and decides nothing."""

    def setUp(self) -> None:
        self.report = lock(ROOT, COMMITMENTS)

    def test_rendering_is_deterministic(self) -> None:
        """Commitment X1, applied to the thing that checks X1."""
        self.assertEqual(render(self.report), render(self.report))
        self.assertEqual(
            render(lock(ROOT, COMMITMENTS)), render(lock(ROOT, COMMITMENTS))
        )

    def test_every_commitment_reaches_the_rendered_output(self) -> None:
        """A view that silently drops a commitment would hide a failing one."""
        text = render(self.report)
        for commitment in COMMITMENTS:
            with self.subTest(commitment=commitment.commitment_id):
                self.assertIn(commitment.commitment_id, text)

    def test_the_summary_matches_the_result(self) -> None:
        """The rendered counts are the computed counts, not recounted."""
        data = as_dict(self.report)
        summary = data["summary"]
        self.assertEqual(summary["commitments"], len(COMMITMENTS))
        self.assertEqual(summary["conforming"], len(self.report.conforming))
        self.assertEqual(summary["unexercised"], len(self.report.unexercised))
        self.assertEqual(summary["unresolved"], len(self.report.unresolved))

    def test_the_artifact_carries_no_clock(self) -> None:
        """A timestamp in the artifact would make two identical runs differ."""
        self.assertNotIn(date.today().isoformat(), render(self.report))

    def test_the_artifact_is_ascii(self) -> None:
        """Recorded prose reaches this artifact, and consoles are not all UTF-8.

        Research freeze §9 names locale as one of the ways an integrity
        mechanism ends up working only on the machine that produced it.
        """
        self.assertTrue(render(self.report).isascii())


class TestEngineBoundary(unittest.TestCase):
    """The claim that lets Phase 0 proceed while DECISION-005 is open."""

    def test_conformance_never_imports_the_engine(self) -> None:
        """Reading source is not importing it, and the difference is the point.

        Run in a subprocess because the rest of the suite imports the engine
        for its own reasons, so ``sys.modules`` in this process proves nothing.
        """
        probe = (
            "import sys\n"
            "from pathlib import Path\n"
            "from daale.conformance import COMMITMENTS, lock, render\n"
            "render(lock(Path('.'), COMMITMENTS))\n"
            "roots = {'choir_prototype', 'applications'}\n"
            "leaked = sorted(m for m in sys.modules if m.split('.')[0] in roots)\n"
            "print(','.join(leaked))\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", probe],
            capture_output=True,
            text=True,
            cwd=ROOT,
            check=True,
        )
        self.assertEqual(result.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
