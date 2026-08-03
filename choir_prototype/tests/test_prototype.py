"""Tests for the CHOIR prototype.

These test the claims the prototype exists to demonstrate, not incidental
behaviour. Each test names the thesis claim it defends.
"""

from __future__ import annotations

import unittest

from choir_prototype.core.contracts import (
    Artifact,
    ConfidenceBand,
    Finding,
    Stance,
    derive_confidence,
)
from choir_prototype.core.ir import EvidenceQuality
from choir_prototype.domains.investment.kernels import (
    FinancialPostureKernel,
    all_kernels,
)
from choir_prototype.domains.investment import DOMAIN
from choir_prototype.domains.investment.packets import NORTHWIND_SEED, ORBITAL_SERIES_B
from choir_prototype.core.pipeline import execute
from choir_prototype.core.report import render
from choir_prototype.core.runtime import ArtifactValidationError, validate_artifact
from choir_prototype.core.synthesizer import Recommendation
from choir_prototype.domains.investment.translator import translate


class TestDeterminism(unittest.TestCase):
    """Claim: the same packet produces the same output on every run."""

    def test_report_is_byte_identical_across_runs(self) -> None:
        """Two independent executions render identical reports."""
        first = render(*execute(ORBITAL_SERIES_B, DOMAIN))
        second = render(*execute(ORBITAL_SERIES_B, DOMAIN))
        self.assertEqual(first, second)

    def test_both_packets_are_deterministic(self) -> None:
        """Determinism is not specific to one packet."""
        for packet in (ORBITAL_SERIES_B, NORTHWIND_SEED):
            with self.subTest(packet=packet.id):
                self.assertEqual(
                    render(*execute(packet, DOMAIN)), render(*execute(packet, DOMAIN))
                )


class TestTranslator(unittest.TestCase):
    """Claim: the translator maps, it does not reason."""

    def test_produces_ir_covering_every_data_point(self) -> None:
        """Every packet data point becomes exactly one claim."""
        ir = translate(ORBITAL_SERIES_B)
        self.assertEqual(len(ir.claims), len(ORBITAL_SERIES_B.data_points))
        self.assertEqual(len(ir.evidence), len(ORBITAL_SERIES_B.sources))

    def test_records_flagged_conflict_as_contradiction(self) -> None:
        """A conflict noted in the packet survives translation as a relationship."""
        ir = translate(ORBITAL_SERIES_B)
        contradicted = ir.contradicted_claim_ids()
        self.assertEqual(len(contradicted), 1)
        claim = ir.claim(next(iter(contradicted)))
        self.assertIsNotNone(claim)
        assert claim is not None
        self.assertEqual(claim.predicate, "net_revenue_retention_pct")

    def test_carries_no_stance_or_confidence(self) -> None:
        """The IR contains no judgement -- no stances, no confidence, no findings."""
        ir = translate(ORBITAL_SERIES_B)
        for claim in ir.claims:
            self.assertFalse(hasattr(claim, "stance"))
            self.assertFalse(hasattr(claim, "confidence"))


class TestKernelIndependence(unittest.TestCase):
    """Claim: kernels reason independently and cannot observe one another."""

    def test_kernel_result_does_not_depend_on_other_kernels(self) -> None:
        """A kernel run alone produces the same artifact as one run in the set."""
        ir = translate(ORBITAL_SERIES_B)
        alone = FinancialPostureKernel().run(ir)
        in_set = next(
            kernel.run(ir)
            for kernel in all_kernels()
            if kernel.name == "financial_posture"
        )
        self.assertEqual(alone, in_set)

    def test_kernel_result_does_not_depend_on_dispatch_order(self) -> None:
        """Reversing dispatch order changes no artifact."""
        ir = translate(ORBITAL_SERIES_B)
        forward = {k.name: k.run(ir) for k in all_kernels()}
        backward = {k.name: k.run(ir) for k in reversed(all_kernels())}
        self.assertEqual(forward, backward)


class TestArtifactValidation(unittest.TestCase):
    """Claim: the runtime rejects artifacts that are not grounded in the IR."""

    def setUp(self) -> None:
        """Build an IR to validate against."""
        self.ir = translate(ORBITAL_SERIES_B)
        self.confidence = derive_confidence(
            evidence=self.ir.evidence,
            expected_inputs=1,
            found_inputs=1,
            contradiction_count=0,
        )

    def test_rejects_fabricated_citation(self) -> None:
        """A finding citing an id that is not in the IR is refused."""
        artifact = Artifact(
            kernel_name="rogue",
            findings=(
                Finding(
                    id="rogue-1",
                    topic="growth",
                    stance=Stance.SUPPORTS,
                    statement="Invented.",
                    claim_ids=("clm-999",),
                ),
            ),
            evidence_references=(),
            confidence=self.confidence,
            assumptions=(),
            unresolved_questions=(),
        )
        with self.assertRaises(ArtifactValidationError):
            validate_artifact(artifact, self.ir)

    def test_rejects_silent_kernel(self) -> None:
        """A kernel must produce findings or unresolved questions."""
        artifact = Artifact(
            kernel_name="silent",
            findings=(),
            evidence_references=(),
            confidence=self.confidence,
            assumptions=(),
            unresolved_questions=(),
        )
        with self.assertRaises(ArtifactValidationError):
            validate_artifact(artifact, self.ir)

    def test_accepts_kernel_that_only_reports_uncertainty(self) -> None:
        """Saying 'I could not tell' is a valid artifact."""
        artifact = Artifact(
            kernel_name="honest",
            findings=(),
            evidence_references=(),
            confidence=self.confidence,
            assumptions=(),
            unresolved_questions=("Nothing in the packet addressed this.",),
        )
        validate_artifact(artifact, self.ir)


class TestDerivedConfidence(unittest.TestCase):
    """Claim: confidence is derived from structure, never authored."""

    def test_no_evidence_yields_insufficient(self) -> None:
        """Findings with no evidence behind them cannot be confident."""
        confidence = derive_confidence([], 4, 4, 0)
        self.assertIs(confidence.band, ConfidenceBand.INSUFFICIENT)

    def test_low_coverage_yields_insufficient(self) -> None:
        """Good evidence does not rescue a kernel that saw almost nothing."""
        ir = translate(ORBITAL_SERIES_B)
        audited = [
            item for item in ir.evidence if item.quality is EvidenceQuality.AUDITED
        ]
        confidence = derive_confidence(
            audited, expected_inputs=5, found_inputs=1, contradiction_count=0
        )
        self.assertIs(confidence.band, ConfidenceBand.INSUFFICIENT)
        self.assertIn("coverage", confidence.limiting_factor)

    def test_weakest_evidence_sets_the_ceiling(self) -> None:
        """One asserted source drags a set of audited sources down."""
        ir = translate(ORBITAL_SERIES_B)
        strong = derive_confidence(
            [item for item in ir.evidence if item.quality is EvidenceQuality.AUDITED],
            expected_inputs=1,
            found_inputs=1,
            contradiction_count=0,
        )
        mixed = derive_confidence(ir.evidence, 1, 1, 0)
        self.assertIs(strong.band, ConfidenceBand.HIGH)
        self.assertIs(mixed.band, ConfidenceBand.LOW)

    def test_always_names_a_limiting_factor(self) -> None:
        """Every derived confidence says what is holding it back."""
        ir = translate(ORBITAL_SERIES_B)
        for artifact in execute(ORBITAL_SERIES_B, DOMAIN)[0].artifacts:
            with self.subTest(kernel=artifact.kernel_name):
                self.assertTrue(artifact.confidence.limiting_factor)
        self.assertTrue(derive_confidence(ir.evidence, 1, 1, 0).limiting_factor)


class TestSynthesis(unittest.TestCase):
    """Claim: synthesis reports agreement and disagreement honestly."""

    def test_detects_cross_kernel_agreement(self) -> None:
        """Two independent kernels reaching the same stance is recorded."""
        _, synthesis = execute(ORBITAL_SERIES_B, DOMAIN)
        topics = {view.topic for view in synthesis.agreements}
        self.assertIn("capital_efficiency", topics)

    def test_detects_cross_kernel_disagreement(self) -> None:
        """Opposing stances on one topic are surfaced, not averaged away."""
        _, synthesis = execute(ORBITAL_SERIES_B, DOMAIN)
        topics = {view.topic for view in synthesis.disagreements}
        self.assertIn("revenue_quality", topics)

    def test_disagreement_is_not_hidden_by_the_recommendation(self) -> None:
        """A reached recommendation still reports the live disagreement."""
        _, synthesis = execute(ORBITAL_SERIES_B, DOMAIN)
        self.assertIs(synthesis.recommendation, Recommendation.PROCEED_WITH_CONDITIONS)
        self.assertTrue(synthesis.disagreements)

    def test_thin_packet_declines_to_conclude(self) -> None:
        """Too few usable kernels yields INSUFFICIENT_BASIS, not a guess."""
        _, synthesis = execute(NORTHWIND_SEED, DOMAIN)
        self.assertIs(synthesis.recommendation, Recommendation.INSUFFICIENT_BASIS)
        self.assertIs(synthesis.confidence, ConfidenceBand.INSUFFICIENT)

    def test_confidence_is_the_minimum_not_the_average(self) -> None:
        """Institutional confidence tracks the weakest contributing kernel."""
        result, synthesis = execute(ORBITAL_SERIES_B, DOMAIN)
        usable = [
            artifact.confidence.band
            for artifact in result.artifacts
            if artifact.confidence.band is not ConfidenceBand.INSUFFICIENT
        ]
        self.assertIn(ConfidenceBand.MODERATE, usable)
        self.assertIs(synthesis.confidence, ConfidenceBand.LOW)


class TestReport(unittest.TestCase):
    """Claim: the report exposes every stage and stays explainable."""

    def test_contains_every_required_section(self) -> None:
        """The report carries all sections the deliverable specifies."""
        text = render(*execute(ORBITAL_SERIES_B, DOMAIN))
        for section in (
            "TRANSLATION INTO THE INTERMEDIATE REPRESENTATION",
            "RECOMMENDATION",
            "CONFIDENCE",
            "KERNEL FINDINGS",
            "AGREEMENTS",
            "DISAGREEMENTS",
            "REMAINING UNCERTAINTY",
            "SUPPORTING EVIDENCE",
            "EXECUTION TRACE",
        ):
            with self.subTest(section=section):
                self.assertIn(section, text)

    def test_trace_covers_every_pipeline_stage(self) -> None:
        """Translator, runtime and synthesizer all appear in the trace.

        Kernels also appear as components in their own right, so this asserts
        containment rather than equality.
        """
        result, _ = execute(ORBITAL_SERIES_B, DOMAIN)
        components = {entry.component for entry in result.trace}
        self.assertTrue({"translator", "runtime", "synthesizer"} <= components)

    def test_trace_steps_are_contiguous(self) -> None:
        """Trace steps are numbered 1..n with no gaps."""
        result, _ = execute(ORBITAL_SERIES_B, DOMAIN)
        self.assertEqual(
            [entry.step for entry in result.trace],
            list(range(1, len(result.trace) + 1)),
        )


if __name__ == "__main__":
    unittest.main()
