"""Tests for the observability layer.

The observability work is an overlay: it must expose how a decision was reached
without changing what was decided. `TestArchitectureFrozen` is the guard on that
and is the most important class in this file.
"""

from __future__ import annotations

import unittest

from choir_prototype.core.contracts import ConfidenceBand, derive_confidence
from choir_prototype.core.inspection import (
    inspect_all,
    inspect_artifacts,
    inspect_ir,
    inspect_synthesis,
    inspect_trace,
)
from choir_prototype.domains.investment.kernels import all_kernels
from choir_prototype.domains.investment import DOMAIN
from choir_prototype.domains.investment.packets import (
    NORTHWIND_SEED,
    ORBITAL_SERIES_B,
    PACKETS,
)
from choir_prototype.core.pipeline import execute
from choir_prototype.core.replay import record_digest, text_digest, verify
from choir_prototype.core.report import render
from choir_prototype.core.runtime import predicate_coverage
from choir_prototype.core.synthesizer import Recommendation
from choir_prototype.domains.investment.translator import translate


class TestArchitectureFrozen(unittest.TestCase):
    """Claim: observability changed what we can see, not what was decided."""

    def test_recommendations_are_unchanged(self) -> None:
        """The V0 outcomes still hold exactly."""
        _, orbital = execute(ORBITAL_SERIES_B, DOMAIN)
        _, northwind = execute(NORTHWIND_SEED, DOMAIN)
        self.assertIs(orbital.recommendation, Recommendation.PROCEED_WITH_CONDITIONS)
        self.assertIs(northwind.recommendation, Recommendation.INSUFFICIENT_BASIS)

    def test_tallies_are_unchanged(self) -> None:
        """The weighted tally still produces the V0 numbers."""
        _, synthesis = execute(ORBITAL_SERIES_B, DOMAIN)
        self.assertEqual(synthesis.support_weight, 7)
        self.assertEqual(synthesis.oppose_weight, 1)
        self.assertEqual(synthesis.conditional_count, 5)

    def test_confidence_bands_are_unchanged(self) -> None:
        """Each kernel still reaches the band it reached in V0."""
        result, synthesis = execute(ORBITAL_SERIES_B, DOMAIN)
        bands = {
            artifact.kernel_name: artifact.confidence.band
            for artifact in result.artifacts
        }
        self.assertEqual(
            bands,
            {
                "financial_posture": ConfidenceBand.MODERATE,
                "risk_exposure": ConfidenceBand.LOW,
                "market_position": ConfidenceBand.LOW,
                "governance": ConfidenceBand.MODERATE,
            },
        )
        self.assertIs(synthesis.confidence, ConfidenceBand.LOW)

    def test_pipeline_still_has_four_kernels(self) -> None:
        """No kernels were added while improving observability."""
        self.assertEqual(len(all_kernels()), 4)


class TestConfidenceDerivation(unittest.TestCase):
    """Claim: confidence records its own working."""

    def test_every_confidence_carries_a_derivation(self) -> None:
        """No band appears without the rules that produced it."""
        result, _ = execute(ORBITAL_SERIES_B, DOMAIN)
        for artifact in result.artifacts:
            with self.subTest(kernel=artifact.kernel_name):
                self.assertTrue(artifact.confidence.derivation)
                self.assertTrue(
                    artifact.confidence.derivation[-1].startswith("result:")
                )

    def test_derivation_reports_the_band_it_produced(self) -> None:
        """The recorded derivation and the recorded band agree."""
        result, _ = execute(ORBITAL_SERIES_B, DOMAIN)
        for artifact in result.artifacts:
            with self.subTest(kernel=artifact.kernel_name):
                self.assertIn(
                    artifact.confidence.band.value,
                    artifact.confidence.derivation[-1],
                )

    def test_short_circuit_is_visible(self) -> None:
        """A run that stops early says so rather than showing later rules."""
        confidence = derive_confidence(
            [], expected_inputs=4, found_inputs=4, contradiction_count=0
        )
        self.assertTrue(any("stop" in step for step in confidence.derivation))


class TestPredicateCoverage(unittest.TestCase):
    """Claim: the runtime can say which inputs a kernel wanted and missed."""

    def test_reports_missing_predicates_on_a_thin_packet(self) -> None:
        """A thin packet names what was absent, not just a count."""
        ir = translate(NORTHWIND_SEED)
        governance = next(k for k in all_kernels() if k.name == "governance")
        found, missing = predicate_coverage(ir, governance)
        self.assertEqual(found, ())
        self.assertIn("audit_status", missing)

    def test_found_and_missing_partition_the_declared_predicates(self) -> None:
        """Every declared predicate lands in exactly one bucket."""
        ir = translate(ORBITAL_SERIES_B)
        for kernel in all_kernels():
            with self.subTest(kernel=kernel.name):
                found, missing = predicate_coverage(ir, kernel)
                self.assertEqual(sorted((*found, *missing)), sorted(kernel.PREDICATES))


class TestTrace(unittest.TestCase):
    """Claim: the trace shows every stage and what crossed each boundary."""

    def test_covers_all_five_stages(self) -> None:
        """Intake, translation, handoff, kernels and synthesis all appear."""
        result, _ = execute(ORBITAL_SERIES_B, DOMAIN)
        stages = {entry.stage for entry in result.trace}
        self.assertEqual(
            stages,
            {
                "1. packet intake",
                "2. translation",
                "3. handoff",
                "4. kernel execution",
                "5. synthesis",
            },
        )

    def test_records_validation_as_its_own_step(self) -> None:
        """Artifact validation is visible, once per kernel."""
        result, _ = execute(ORBITAL_SERIES_B, DOMAIN)
        validations = [
            entry for entry in result.trace if entry.action == "artifact-validated"
        ]
        self.assertEqual(len(validations), 4)

    def test_records_data_crossing_boundaries(self) -> None:
        """At least one step names its inputs and one names its outputs."""
        result, _ = execute(ORBITAL_SERIES_B, DOMAIN)
        self.assertTrue(any(entry.inputs for entry in result.trace))
        self.assertTrue(any(entry.outputs for entry in result.trace))

    def test_names_the_deciding_rule(self) -> None:
        """The trace says which decision rule produced the recommendation."""
        result, _ = execute(ORBITAL_SERIES_B, DOMAIN)
        notes = [note for entry in result.trace for note in entry.notes]
        self.assertTrue(any("decided by rule R3" in note for note in notes))


class TestSynthesisExplanation(unittest.TestCase):
    """Claim: the synthesizer records how it computed, not just what."""

    def test_tally_lines_reach_the_recorded_totals(self) -> None:
        """The running totals end exactly where the summary says they do."""
        _, synthesis = execute(ORBITAL_SERIES_B, DOMAIN)
        last = synthesis.tally_detail[-1]
        self.assertEqual(last.running_support, synthesis.support_weight)
        self.assertEqual(last.running_oppose, synthesis.oppose_weight)
        self.assertEqual(last.running_conditional, synthesis.conditional_count)

    def test_one_tally_line_per_finding(self) -> None:
        """Nothing is silently excluded from the tally."""
        result, synthesis = execute(ORBITAL_SERIES_B, DOMAIN)
        total_findings = sum(len(a.findings) for a in result.artifacts)
        self.assertEqual(len(synthesis.tally_detail), total_findings)

    def test_records_rules_that_did_not_fire(self) -> None:
        """Rejected rules are recorded, not just the one that fired."""
        _, synthesis = execute(ORBITAL_SERIES_B, DOMAIN)
        self.assertTrue(any(not rule.fired for rule in synthesis.rules_evaluated))

    def test_exactly_one_rule_fires(self) -> None:
        """The decision has a single identifiable cause."""
        for packet in PACKETS.values():
            with self.subTest(packet=packet.id):
                _, synthesis = execute(packet, DOMAIN)
                fired = [r for r in synthesis.rules_evaluated if r.fired]
                self.assertEqual(len(fired), 1)

    def test_evaluation_stops_at_the_firing_rule(self) -> None:
        """Rules after the deciding one are never evaluated."""
        _, synthesis = execute(ORBITAL_SERIES_B, DOMAIN)
        self.assertTrue(synthesis.rules_evaluated[-1].fired)


class TestInspectionViews(unittest.TestCase):
    """Claim: each view renders and shows what a newcomer needs."""

    def test_ir_view_reports_integrity_checks(self) -> None:
        """The IR view surfaces unbacked claims and dangling references."""
        text = inspect_ir(translate(ORBITAL_SERIES_B))
        self.assertIn("INTEGRITY CHECKS", text)
        self.assertIn("claims with no evidence", text)
        self.assertIn("CONTRADICTED", text)

    def test_artifact_view_shows_derivation_and_gaps(self) -> None:
        """The artifact view shows how confidence was derived."""
        result, _ = execute(ORBITAL_SERIES_B, DOMAIN)
        text = inspect_artifacts(result)
        self.assertIn("CONFIDENCE DERIVATION", text)
        self.assertIn("COULD NOT CONCLUDE", text)
        self.assertIn("INPUTS SOUGHT", text)

    def test_artifact_view_names_missing_inputs(self) -> None:
        """On a thin packet the view names what the packet did not supply."""
        result, _ = execute(NORTHWIND_SEED, DOMAIN)
        text = inspect_artifacts(result)
        self.assertIn("MISSING", text)
        self.assertIn("audit_status", text)

    def test_synthesis_view_shows_all_five_steps(self) -> None:
        """The explanation walks tally and rules, not just the answer."""
        _, synthesis = execute(ORBITAL_SERIES_B, DOMAIN)
        text = inspect_synthesis(synthesis)
        for step in ("STEP 1", "STEP 2", "STEP 3", "STEP 4", "STEP 5"):
            with self.subTest(step=step):
                self.assertIn(step, text)
        self.assertIn("FIRED", text)

    def test_synthesis_view_marks_agreement_and_disagreement(self) -> None:
        """A newcomer can see which topics agreed and which did not."""
        _, synthesis = execute(ORBITAL_SERIES_B, DOMAIN)
        text = inspect_synthesis(synthesis)
        self.assertIn("<-- AGREEMENT", text)
        self.assertIn("<-- DISAGREEMENT", text)

    def test_trace_view_groups_by_stage(self) -> None:
        """The trace view is grouped so the pipeline shape is visible."""
        result, _ = execute(ORBITAL_SERIES_B, DOMAIN)
        text = inspect_trace(result)
        self.assertIn("STAGE 1. packet intake", text)
        self.assertIn("STAGE 5. synthesis", text)

    def test_all_views_render_for_both_packets(self) -> None:
        """Nothing crashes on a packet where kernels conclude nothing."""
        for packet in PACKETS.values():
            with self.subTest(packet=packet.id):
                result, synthesis = execute(packet, DOMAIN)
                self.assertTrue(inspect_all(result, synthesis))


class TestReplay(unittest.TestCase):
    """Claim: runs are reproducible and renderers are pure projections."""

    def test_verify_passes_for_both_packets(self) -> None:
        """Every replay check passes."""
        for packet in PACKETS.values():
            with self.subTest(packet=packet.id):
                report = verify(packet, DOMAIN, runs=3)
                self.assertTrue(report.passed, [c.name for c in report.checks])

    def test_record_digest_is_stable(self) -> None:
        """The same packet yields the same record hash."""
        first = record_digest(*execute(ORBITAL_SERIES_B, DOMAIN))
        second = record_digest(*execute(ORBITAL_SERIES_B, DOMAIN))
        self.assertEqual(first, second)

    def test_different_packets_yield_different_digests(self) -> None:
        """The digest actually discriminates between runs."""
        self.assertNotEqual(
            record_digest(*execute(ORBITAL_SERIES_B, DOMAIN)),
            record_digest(*execute(NORTHWIND_SEED, DOMAIN)),
        )

    def test_rendering_is_a_pure_projection(self) -> None:
        """Rendering one record twice gives identical text."""
        result, synthesis = execute(ORBITAL_SERIES_B, DOMAIN)
        self.assertEqual(
            text_digest(render(result, synthesis)),
            text_digest(render(result, synthesis)),
        )

    def test_inspection_is_a_pure_projection(self) -> None:
        """Inspecting one record twice gives identical text."""
        result, synthesis = execute(ORBITAL_SERIES_B, DOMAIN)
        self.assertEqual(
            text_digest(inspect_all(result, synthesis)),
            text_digest(inspect_all(result, synthesis)),
        )


if __name__ == "__main__":
    unittest.main()
