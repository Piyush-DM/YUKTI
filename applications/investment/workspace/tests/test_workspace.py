"""A committee can carry a case from intake to a recorded decision.

The tests that matter most here are the two boundary tests. The workspace's
whole claim is that it is a product *around* the reasoning engine rather than a
second implementation of it:

- ``test_judgment_matches_the_engine_directly`` checks that what the screen
  shows is what the engine concluded, by running the engine independently and
  comparing.
- ``test_case_metadata_does_not_reach_the_engine`` checks the other direction:
  changing who owns a case, or when it was opened, must not move a conclusion.

Everything else is workflow.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from choir_prototype.core.pipeline import execute
from choir_prototype.core.synthesizer import synthesize
from choir_prototype.domains import investment

from applications.investment.vertical_slice.parse import parse_document
from applications.investment.workspace import analysis, diligence
from applications.investment.workspace.cases import (
    CaseStore,
    Figure,
    FlaggedConflict,
    LedgerEntry,
    Source,
)


def reference_tuples() -> tuple[
    tuple[Source, ...], tuple[Figure, ...], tuple[str, ...], tuple[FlaggedConflict, ...]
]:
    """The worked example's material, as the store's entities."""
    material = analysis.reference_material()
    return (
        tuple(Source(**entry) for entry in material["sources"]),
        tuple(
            Figure(
                metric=entry["metric"],
                value=entry["value"],
                status=entry["status"],
                source_labels=tuple(entry["source_labels"]),
            )
            for entry in material["figures"]
        ),
        tuple(material["assumptions"]),
        tuple(FlaggedConflict(**entry) for entry in material["flagged_conflicts"]),
    )


class WorkspaceTestCase(unittest.TestCase):
    """Shared fixture: an empty store in a temporary directory."""

    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.store = CaseStore(Path(self._temporary.name))
        self.addCleanup(self._temporary.cleanup)

    def open_reference_case(self, company: str = "Orbital Logistics") -> str:
        """Open a case and load the worked example's material into it."""
        case = self.store.open_case(
            company=company,
            sector="supply chain software",
            stage="Series B",
            requested_decision="Approve a Series B allocation",
            thesis="Reference case.",
            owner="A. Rao",
            opened_on="2026-08-05",
        )
        sources, figures, assumptions, conflicts = reference_tuples()
        self.store.record_material(
            case.case_id, sources, figures, assumptions, conflicts
        )
        return case.case_id


class TestCaseLifecycle(WorkspaceTestCase):
    """A case moves through the states an institution recognises."""

    def test_a_new_case_starts_as_a_draft(self) -> None:
        """Nothing is claimed about a case before material exists."""
        case = self.store.open_case(
            company="Northwind Instruments",
            sector="laboratory hardware",
            stage="Seed",
            requested_decision="Approve a seed allocation",
            thesis="",
            owner="J. Okafor",
            opened_on="2026-08-05",
        )
        self.assertEqual(case.status(analysed=False), "Draft")

    def test_case_ids_are_readable_and_unique(self) -> None:
        """Two cases for the same company do not collide."""
        first = self.store.open_case(
            "Orbital Logistics", "software", "Series B", "Approve", "", "A. Rao"
        )
        second = self.store.open_case(
            "Orbital Logistics", "software", "Series C", "Approve", "", "A. Rao"
        )
        self.assertEqual(first.case_id, "orbital-logistics")
        self.assertEqual(second.case_id, "orbital-logistics-2")

    def test_opening_a_case_requires_the_committee_facts(self) -> None:
        """A case with no company or no owner is not a case."""
        with self.assertRaises(ValueError):
            self.store.open_case("", "software", "Series B", "Approve", "", "A. Rao")
        with self.assertRaises(ValueError):
            self.store.open_case("Orbital", "software", "Series B", "Approve", "", "")

    def test_status_follows_the_record(self) -> None:
        """Status is derived, so it cannot disagree with what is on file."""
        case_id = self.open_reference_case()
        case = self.store.load(case_id)
        self.assertEqual(case.status(analysed=False), "Material assembled")
        self.assertEqual(case.status(analysed=True), "Analysed")

        self.store.append_ledger_entry(
            case_id,
            LedgerEntry(
                entry_id="LEDGER-001",
                decision="Approved with conditions",
                decided_by="Investment Committee",
                rationale="Conditions accepted.",
                recorded_on="2026-08-05",
                judgment_recommendation="Proceed With Conditions",
                judgment_confidence="Low",
                record_digest="abc",
            ),
        )
        self.assertEqual(self.store.load(case_id).status(analysed=True), "Decided")

    def test_cases_survive_a_restart(self) -> None:
        """A second store over the same directory reads the same cases."""
        case_id = self.open_reference_case()
        reopened = CaseStore(self.store.root).load(case_id)
        self.assertEqual(reopened.case_id, case_id)
        self.assertEqual(len(reopened.figures), 15)


class TestMaterialIntegrity(WorkspaceTestCase):
    """The institution cannot record material it could not defend."""

    def test_a_figure_cannot_cite_a_source_that_is_not_registered(self) -> None:
        """An uncitable figure is what an audit trail exists to prevent."""
        case = self.store.open_case(
            "Orbital", "software", "Series B", "Approve", "", "A. Rao"
        )
        with self.assertRaises(ValueError) as caught:
            self.store.record_material(
                case.case_id,
                sources=(Source("SRC-AUDIT", "FY24 audit", "audit"),),
                figures=(Figure("arr_usd", "1000", "confirmed", ("SRC-GHOST",)),),
                assumptions=(),
                flagged_conflicts=(),
            )
        self.assertIn("SRC-GHOST", str(caught.exception))

    def test_a_figure_must_cite_something(self) -> None:
        """A figure with no source has no standing."""
        case = self.store.open_case(
            "Orbital", "software", "Series B", "Approve", "", "A. Rao"
        )
        with self.assertRaises(ValueError):
            self.store.record_material(
                case.case_id,
                sources=(Source("SRC-AUDIT", "FY24 audit", "audit"),),
                figures=(Figure("arr_usd", "1000", "confirmed", ()),),
                assumptions=(),
                flagged_conflicts=(),
            )

    def test_source_labels_are_unique(self) -> None:
        """Two documents under one reference cannot be told apart later."""
        case = self.store.open_case(
            "Orbital", "software", "Series B", "Approve", "", "A. Rao"
        )
        with self.assertRaises(ValueError):
            self.store.record_material(
                case.case_id,
                sources=(
                    Source("SRC-AUDIT", "FY24 audit", "audit"),
                    Source("SRC-AUDIT", "FY23 audit", "audit"),
                ),
                figures=(),
                assumptions=(),
                flagged_conflicts=(),
            )


class TestDiligenceSchedule(unittest.TestCase):
    """The schedule is the institution's checklist, and it matches the engine."""

    def test_every_scheduled_figure_is_one_the_engine_reads(self) -> None:
        """A figure nobody reads would be busywork asked of a diligence team."""
        engine_predicates: set[str] = set()
        for kernel in investment.DOMAIN.kernels:
            engine_predicates.update(kernel.PREDICATES)
        self.assertEqual(
            {entry.metric for entry in diligence.SCHEDULE}, engine_predicates
        )

    def test_every_engine_area_has_an_institutional_name(self) -> None:
        """No internal component name can reach the screen."""
        for kernel in investment.DOMAIN.kernels:
            with self.subTest(area=kernel.name):
                label = diligence.label_for_review_area(kernel.name)
                self.assertNotEqual(label, kernel.name)
                self.assertIn(label, diligence.REVIEW_AREAS)

    def test_every_engine_topic_has_an_institutional_name(self) -> None:
        """Topics are headings a committee reads, not engine vocabulary."""
        for topic in investment.DOMAIN.topics:
            with self.subTest(topic=topic):
                self.assertNotIn("_", diligence.label_for_topic(topic))

    def test_relabelling_leaves_ordinary_prose_untouched(self) -> None:
        """Text with no internal name passes through byte for byte.

        This is what makes the substitution a relabelling rather than a rewrite:
        the product cannot alter a sentence the engine composed unless that
        sentence names an internal component.
        """
        sentence = (
            "Runway of 15.0 months is adequate but leaves limited room for a "
            "missed quarter."
        )
        self.assertEqual(diligence.institutional_text(sentence), sentence)

    def test_relabelling_replaces_internal_names(self) -> None:
        """Engine-composed prose is stated in the institution's vocabulary."""
        self.assertEqual(
            diligence.institutional_text(
                "weakest contributing kernel is market_position"
            ),
            "weakest contributing review area is Market",
        )

    def test_outstanding_reports_what_is_missing(self) -> None:
        """Gaps are named while they can still be filled."""
        outstanding = diligence.outstanding(frozenset({"arr_usd"}))
        metrics = {entry.metric for entry in outstanding}
        self.assertNotIn("arr_usd", metrics)
        self.assertIn("cash_usd", metrics)
        self.assertEqual(len(outstanding), len(diligence.SCHEDULE) - 1)


class TestJudgment(WorkspaceTestCase):
    """Requesting a judgment produces what the engine concluded, relabelled."""

    def test_material_must_exist_before_analysis(self) -> None:
        """The product refuses rather than analysing an empty case."""
        case = self.store.open_case(
            "Orbital", "software", "Series B", "Approve", "", "A. Rao"
        )
        with self.assertRaises(analysis.MaterialIncomplete):
            analysis.request_judgment(self.store, case.case_id)

    def test_judgment_matches_the_engine_directly(self) -> None:
        """What the screen shows is what the engine concluded.

        The engine is run independently here, from the same material, and the
        product's judgment is compared against it. If the product ever starts
        computing anything of its own, this test fails.
        """
        case_id = self.open_reference_case()
        judgment = analysis.request_judgment(self.store, case_id)

        packet = parse_document(
            json.dumps(analysis.compose_document(self.store.load(case_id))),
            origin="test",
        )
        result, synthesis = execute(packet, investment.DOMAIN)

        self.assertEqual(
            judgment.recommendation, synthesis.recommendation.value.title()
        )
        self.assertEqual(judgment.confidence.lower(), synthesis.confidence.value)
        # Prose is relabelled into institutional vocabulary and not otherwise
        # touched, so the comparison is against the relabelled engine output.
        self.assertEqual(
            judgment.confidence_note,
            diligence.institutional_text(synthesis.confidence_limiting_factor),
        )
        self.assertEqual(
            judgment.rationale,
            tuple(diligence.institutional_text(line) for line in synthesis.rationale),
        )
        self.assertEqual(len(judgment.review_areas), len(result.artifacts))
        self.assertEqual(len(judgment.disagreements), len(synthesis.disagreements))
        self.assertEqual(len(judgment.agreements), len(synthesis.agreements))

    def test_case_metadata_does_not_reach_the_engine(self) -> None:
        """Who owns a case cannot change what the case concludes."""
        first = self.open_reference_case("Orbital Logistics")
        judgment_one = analysis.request_judgment(self.store, first)

        second = self.store.open_case(
            company="Orbital Logistics",
            sector="supply chain software",
            stage="Series B",
            requested_decision="A completely different question",
            thesis="A different thesis entirely.",
            owner="Someone Else",
            opened_on="2030-01-01",
        )
        sources, figures, assumptions, conflicts = reference_tuples()
        self.store.record_material(
            second.case_id, sources, figures, assumptions, conflicts
        )
        judgment_two = analysis.request_judgment(self.store, second.case_id)

        self.assertEqual(judgment_one.recommendation, judgment_two.recommendation)
        self.assertEqual(judgment_one.confidence, judgment_two.confidence)
        # The digest differs only because the case id is the packet id, which is
        # what keeps two cases' artifacts apart on disk.
        self.assertNotEqual(first, second.case_id)

    def test_the_same_material_reproduces_the_same_digest(self) -> None:
        """Re-running a case gives the identical record. Determinism survives."""
        case_id = self.open_reference_case()
        first = analysis.request_judgment(self.store, case_id)
        second = analysis.request_judgment(self.store, case_id)
        self.assertEqual(first.record_digest, second.record_digest)
        self.assertNotEqual(first.record_digest, "")

    def test_no_internal_vocabulary_reaches_the_judgment(self) -> None:
        """A user never reads a kernel name, a claim id, or an artifact label.

        This collects *every* string the judgment can put on a screen, not a
        sample of them. An earlier version checked only the headline fields and
        missed an unresolved question reading "Claim clm-007 ... in the packet",
        which is exactly the kind of leak this test exists to catch.
        """
        case_id = self.open_reference_case()
        judgment = analysis.request_judgment(self.store, case_id)

        visible = " ".join(self.judgment_strings(judgment))
        for internal in ("kernel", "artifact", "translator", "packet", "choirir"):
            with self.subTest(term=internal):
                self.assertNotIn(internal, visible.lower())
        for pattern in ("clm-", "asm-", "rel-", "ent-"):
            with self.subTest(identifier=pattern):
                self.assertNotIn(pattern, visible.lower())

    def test_thin_material_reports_no_internal_vocabulary_either(self) -> None:
        """The declining path renders its own prose and must be checked too."""
        case = self.store.open_case(
            "Northwind Instruments", "lab hardware", "Seed", "Approve", "", "J. Okafor"
        )
        self.store.record_material(
            case.case_id,
            sources=(Source("SRC-FOUNDER", "Founder email summary", "assertion"),),
            figures=(Figure("arr_usd", "400000", "reported", ("SRC-FOUNDER",)),),
            assumptions=(),
            flagged_conflicts=(),
        )
        judgment = analysis.request_judgment(self.store, case.case_id)
        visible = " ".join(self.judgment_strings(judgment)).lower()
        for internal in ("kernel", "packet", "artifact"):
            with self.subTest(term=internal):
                self.assertNotIn(internal, visible)

    @staticmethod
    def judgment_strings(judgment: analysis.Judgment) -> list[str]:
        """Every string this judgment can render, flattened."""
        collected = [
            judgment.recommendation,
            judgment.outcome_guidance,
            judgment.confidence,
            judgment.confidence_note,
            *judgment.rationale,
            *judgment.unresolved_questions,
            *judgment.remaining_uncertainty,
            *judgment.outstanding_schedule_items,
        ]
        for finding in judgment.conditions:
            collected += [finding.stance, finding.topic, finding.statement]
            collected += list(finding.evidence_labels)
        for area in judgment.review_areas:
            collected += [
                area.review_area,
                area.confidence,
                area.confidence_note,
                area.coverage,
                *area.unresolved_questions,
                *area.assumptions,
            ]
            for finding in area.findings:
                collected += [finding.stance, finding.topic, finding.statement]
                collected += list(finding.evidence_labels)
        for view in list(judgment.agreements) + list(judgment.disagreements):
            collected.append(view.topic)
            for area_name, stance, statement in view.positions:
                collected += [area_name, stance, statement]
        return collected

    def test_thin_material_is_reported_as_thin(self) -> None:
        """The product surfaces a declined conclusion rather than manufacturing one."""
        case = self.store.open_case(
            "Northwind Instruments", "lab hardware", "Seed", "Approve", "", "J. Okafor"
        )
        self.store.record_material(
            case.case_id,
            sources=(Source("SRC-FOUNDER", "Founder email summary", "assertion"),),
            figures=(Figure("arr_usd", "400000", "reported", ("SRC-FOUNDER",)),),
            assumptions=("Founder figures are unaudited.",),
            flagged_conflicts=(),
        )
        judgment = analysis.request_judgment(self.store, case.case_id)
        self.assertEqual(judgment.recommendation, "Insufficient Basis")
        self.assertTrue(judgment.outstanding_schedule_items)

    def test_the_audit_trail_is_written_beside_the_case(self) -> None:
        """A judgment can be defended without leaving the case directory."""
        case_id = self.open_reference_case()
        analysis.request_judgment(self.store, case_id)
        directory = self.store.directory(case_id)
        for name in (
            "case.json",
            "01-document.json",
            "05-record.json",
            "06-report.txt",
        ):
            with self.subTest(artifact=name):
                self.assertTrue((directory / name).is_file())

    def test_the_rendered_report_is_available_verbatim(self) -> None:
        """The audit view shows the engine's own report, not a retelling."""
        case_id = self.open_reference_case()
        analysis.request_judgment(self.store, case_id)
        report = analysis.rendered_report(self.store, case_id)
        self.assertIn("INSTITUTIONAL REASONING REPORT", report)


class TestSynthesisBoundary(unittest.TestCase):
    """The product never synthesises. It reads what synthesis produced."""

    def test_workspace_does_not_call_the_synthesizer(self) -> None:
        """A guard on the boundary: only the engine decides.

        ``synthesize`` is imported here purely so this test can name the thing
        the product must not do. The assertion is on the source of the product
        modules themselves.
        """
        self.assertTrue(callable(synthesize))
        product_root = Path(analysis.__file__).parent
        for module in sorted(product_root.glob("*.py")):
            with self.subTest(module=module.name):
                source = module.read_text(encoding="utf-8")
                self.assertNotIn("synthesize(", source)
                self.assertNotIn("derive_confidence", source)


class TestDecisionLedger(WorkspaceTestCase):
    """The committee's decision is recorded against the judgment, not inside it."""

    def test_a_decision_is_appended_and_never_replaces_the_judgment(self) -> None:
        """An override must remain visible as an override."""
        case_id = self.open_reference_case()
        judgment = analysis.request_judgment(self.store, case_id)

        self.store.append_ledger_entry(
            case_id,
            LedgerEntry(
                entry_id="LEDGER-001",
                decision="Declined",
                decided_by="Investment Committee",
                rationale="Concentration risk is outside mandate.",
                recorded_on="2026-08-05",
                judgment_recommendation=judgment.recommendation,
                judgment_confidence=judgment.confidence,
                record_digest=judgment.record_digest,
            ),
        )

        case = self.store.load(case_id)
        self.assertEqual(len(case.ledger), 1)
        entry = case.ledger[0]
        self.assertEqual(entry.decision, "Declined")
        self.assertEqual(entry.judgment_recommendation, "Proceed With Conditions")
        self.assertEqual(entry.record_digest, judgment.record_digest)

    def test_ledger_entries_accumulate(self) -> None:
        """Nothing is deleted; a revisited decision is a second entry."""
        case_id = self.open_reference_case()
        judgment = analysis.request_judgment(self.store, case_id)
        for index in range(2):
            self.store.append_ledger_entry(
                case_id,
                LedgerEntry(
                    entry_id=f"LEDGER-{index + 1:03d}",
                    decision="Deferred pending further diligence",
                    decided_by="Investment Committee",
                    rationale="More material requested.",
                    recorded_on="2026-08-05",
                    judgment_recommendation=judgment.recommendation,
                    judgment_confidence=judgment.confidence,
                    record_digest=judgment.record_digest,
                ),
            )
        self.assertEqual(len(self.store.load(case_id).ledger), 2)


if __name__ == "__main__":
    unittest.main()
