"""Tests for the domain-independence claim.

These are the executable form of the experiment defined in
``choir/research/phase-5-generalization/domain_independence.md`` section 6.

The claim under test:

    The same IR, runtime, confidence model, conflict model and decision
    procedure serve four unrelated domains, with zero changes to the core.

Each test names the part of the claim it defends. ``TestHoldOut`` is the one
that matters most: law and medicine were the development set, so a fix could
have been tuned to them. Engineering was written afterwards.
"""

from __future__ import annotations

import unittest

from choir_prototype.audit import (
    CORE_MANIFEST,
    check_execution,
    check_hold_out,
    check_import_direction,
    check_rule_identity,
    check_shared_machinery,
    check_vocabulary_isolation,
    portability_score,
    run_audit,
)
from choir_prototype.core.contracts import ConfidenceBand
from choir_prototype.core.ir import ChoirIR
from choir_prototype.core.pipeline import execute
from choir_prototype.core.replay import record_digest, verify
from choir_prototype.core.report import render
from choir_prototype.core.synthesizer import Recommendation
from choir_prototype.domains import DEVELOPMENT_SET, HOLD_OUT, REGISTRY, all_packets

# Digests captured before the core/domain split. If the refactor had changed
# any decision, these would move.
V0_DIGESTS = {
    "orbital-series-b": (
        "580a5b279f18a7f13b71e5d36c226bf044d738b1b53d5c53ef32d03792154445"
    ),
    "northwind-seed": (
        "fc4e69083af1977251f224fe4019694389a80fe11d60a1a1263fcc785022ab6f"
    ),
}


class TestBehaviourPreserved(unittest.TestCase):
    """Claim: the layering refactor changed structure, not results."""

    def test_investment_digests_match_pre_split_baseline(self) -> None:
        """The V0 investment runs still produce byte-identical records."""
        investment = REGISTRY["investment"]
        for packet_id, expected in V0_DIGESTS.items():
            with self.subTest(packet=packet_id):
                packet = investment.packet(packet_id)
                self.assertIsNotNone(packet)
                self.assertEqual(record_digest(*execute(packet, investment)), expected)


class TestLayering(unittest.TestCase):
    """Claim: the core does not know any domain exists."""

    def test_core_never_imports_a_domain(self) -> None:
        """A1: dependencies point from domains to core, never the reverse."""
        check = check_import_direction()
        self.assertTrue(check.passed, check.rows)

    def test_core_code_contains_no_domain_vocabulary(self) -> None:
        """A2: no domain term appears in core identifiers or runtime strings."""
        check = check_vocabulary_isolation()
        self.assertTrue(check.passed, check.rows)

    def test_no_domain_defines_its_own_reasoning_machinery(self) -> None:
        """A4: domains supply inputs and kernels, never their own synthesizer."""
        check = check_shared_machinery()
        self.assertTrue(check.passed, check.rows)


class TestAllDomainsExecute(unittest.TestCase):
    """Claim: every domain runs end to end on shared code."""

    def test_every_packet_executes(self) -> None:
        """A3: no domain fails on the shared pipeline."""
        check = check_execution()
        self.assertTrue(check.passed, check.rows)

    def test_every_domain_produces_an_ir(self) -> None:
        """Translation succeeds for every packet in every domain."""
        for domain, packet in all_packets():
            with self.subTest(domain=domain.name):
                ir = domain.translate(packet)
                self.assertIsInstance(ir, ChoirIR)
                self.assertTrue(ir.claims)
                self.assertEqual(ir.metadata.domain, domain.name)

    def test_every_domain_produces_one_artifact_per_kernel(self) -> None:
        """The runtime dispatches every kernel a domain registers."""
        for domain, packet in all_packets():
            with self.subTest(domain=domain.name):
                result, _ = execute(packet, domain)
                self.assertEqual(len(result.artifacts), len(domain.kernels))

    def test_every_domain_renders_a_report(self) -> None:
        """The shared renderer handles every domain without special-casing."""
        for domain, packet in all_packets():
            with self.subTest(domain=domain.name):
                self.assertIn("RECOMMENDATION", render(*execute(packet, domain)))


class TestSharedReasoning(unittest.TestCase):
    """Claim: the reasoning is structural, not tuned per domain."""

    def test_one_rule_ordering_serves_every_domain(self) -> None:
        """A6: every run is adjudicated from the same ordered rule set."""
        check = check_rule_identity()
        self.assertTrue(check.passed, check.rows)

    def test_every_decision_rule_is_exercised_somewhere(self) -> None:
        """All five rules fire across the corpus -- none is domain-specific."""
        fired: set[str] = set()
        for domain, packet in all_packets():
            _, synthesis = execute(packet, domain)
            fired.update(rule.name for rule in synthesis.rules_evaluated if rule.fired)
        self.assertEqual(len(fired), 5, sorted(fired))

    def test_outcomes_differ_across_domains(self) -> None:
        """The same rules produce different answers from different structure."""
        outcomes = {
            execute(packet, domain)[1].recommendation
            for domain, packet in all_packets()
        }
        self.assertTrue(
            {
                Recommendation.PROCEED,
                Recommendation.PROCEED_WITH_CONDITIONS,
                Recommendation.DECLINE,
                Recommendation.CONTESTED,
                Recommendation.INSUFFICIENT_BASIS,
            }
            <= outcomes,
            sorted(item.name for item in outcomes),
        )

    def test_insufficient_basis_reached_in_more_than_one_domain(self) -> None:
        """Declining to conclude is not an investment-specific behaviour."""
        declining = {
            domain.name
            for domain, packet in all_packets()
            if execute(packet, domain)[1].recommendation
            is Recommendation.INSUFFICIENT_BASIS
        }
        self.assertGreaterEqual(len(declining), 2, declining)

    def test_confidence_is_derived_in_every_domain(self) -> None:
        """No domain may author a confidence value."""
        for domain, packet in all_packets():
            result, _ = execute(packet, domain)
            for artifact in result.artifacts:
                with self.subTest(domain=domain.name, kernel=artifact.kernel_name):
                    self.assertTrue(artifact.confidence.limiting_factor)
                    self.assertTrue(artifact.confidence.derivation)

    def test_weakest_kernel_caps_confidence_in_every_domain(self) -> None:
        """The minimum-not-average rule is not investment-specific."""
        for domain, packet in all_packets():
            result, synthesis = execute(packet, domain)
            usable = [
                artifact.confidence.band
                for artifact in result.artifacts
                if artifact.confidence.band is not ConfidenceBand.INSUFFICIENT
            ]
            if len(usable) < 2:
                continue
            with self.subTest(domain=domain.name):
                weights = [band.weight for band in usable]
                self.assertEqual(synthesis.confidence.weight, min(weights))


class TestHoldOut(unittest.TestCase):
    """Claim: the decoupling generalises, rather than fitting two examples."""

    def test_core_matches_the_manifest_pinned_before_the_hold_out(self) -> None:
        """A5/A7: adding the hold-out domain changed no core file."""
        check = check_hold_out()
        self.assertTrue(check.passed, check.rows)

    def test_hold_out_is_not_in_the_development_set(self) -> None:
        """The control was genuinely held back."""
        self.assertTrue(HOLD_OUT)
        self.assertFalse(set(HOLD_OUT) & set(DEVELOPMENT_SET))

    def test_hold_out_domain_is_registered_and_runs(self) -> None:
        """The control is a real domain, not a stub."""
        for name in HOLD_OUT:
            domain = REGISTRY[name]
            with self.subTest(domain=name):
                self.assertGreaterEqual(len(domain.kernels), 2)
                self.assertTrue(domain.packets)
                for packet in domain.packets.values():
                    result, synthesis = execute(packet, domain)
                    self.assertTrue(result.artifacts)
                    self.assertTrue(synthesis.rationale)

    def test_manifest_covers_every_core_module(self) -> None:
        """No core file escapes the hash pin."""
        from choir_prototype.audit import _core_files

        self.assertEqual({path.name for path in _core_files()}, set(CORE_MANIFEST))


class TestPortabilityMetric(unittest.TestCase):
    """Claim: the metric from domain_independence.md section 6 is satisfied."""

    def test_zero_core_changes(self) -> None:
        """The target is core_changes == 0."""
        core_changes, _, _ = portability_score()
        self.assertEqual(core_changes, 0)

    def test_portability_is_one(self) -> None:
        """portability = 1 - core_changes / total."""
        _, _, portability = portability_score()
        self.assertEqual(portability, 1.0)

    def test_full_audit_passes(self) -> None:
        """Every check A1-A7 passes."""
        failures = [check.id for check in run_audit() if not check.passed]
        self.assertEqual(failures, [])


class TestDeterminismAcrossDomains(unittest.TestCase):
    """Claim: reproducibility is a property of the core, not of one domain."""

    def test_every_domain_replays_identically(self) -> None:
        """Replay verification passes for every packet in every domain."""
        for domain, packet in all_packets():
            with self.subTest(domain=domain.name):
                report = verify(packet, domain, runs=2)
                self.assertTrue(
                    report.passed, [c.name for c in report.checks if not c.passed]
                )

    def test_digests_discriminate_across_domains(self) -> None:
        """Different domains produce different records."""
        digests = {
            record_digest(*execute(packet, domain)) for domain, packet in all_packets()
        }
        self.assertEqual(len(digests), len(all_packets()))


if __name__ == "__main__":
    unittest.main()
