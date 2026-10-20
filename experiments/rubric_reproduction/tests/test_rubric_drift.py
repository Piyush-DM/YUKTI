"""Detect drift between ``rubric.md`` and the live frozen source.

What this guards: every numeric constant, enum member, predicate list, topic
label, the kernel dispatch order, the market-metric routing, and the emitted
finding catalogue.

What it does NOT guard (documented in ``rubric.md`` Section I): operator
direction, branch order, and the exact text of statement / derivation / rationale
strings. Those must be diffed against the source files by a human.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from choir_prototype.core.pipeline import execute
from choir_prototype.core.replay import _canonical, record_digest, text_digest
from choir_prototype.core.synthesizer import Recommendation
from choir_prototype.domains.investment import DOMAIN
from choir_prototype.domains.investment.kernels import all_kernels

from experiments.rubric_reproduction import ground_truth

RUBRIC_PATH = Path(__file__).resolve().parents[1] / "rubric.md"

_BLOCK_RE = re.compile(
    r"<!-- BEGIN rubric-machine-block -->\s*```json\n(.*?)\n```\s*"
    r"<!-- END rubric-machine-block -->",
    re.DOTALL,
)

_KNOWN_RULE_NAMES = {
    "R1 insufficient-basis",
    "R2 live-disagreement",
    "R3 proceed-with-conditions",
    "R4 proceed",
    "R5 decline",
    "R6 balanced-fallback",
}


def _machine_block() -> dict:
    match = _BLOCK_RE.search(RUBRIC_PATH.read_text(encoding="utf-8"))
    if match is None:
        raise AssertionError("rubric.md is missing its rubric-machine-block")
    return json.loads(match.group(1))


class TestRubricDrift(unittest.TestCase):
    """Claim: the rubric's constants still match the frozen implementation."""

    def setUp(self) -> None:
        self.block = _machine_block()

    def test_constants_equal_live_source(self) -> None:
        """The machine block's ``constants`` equal ``ground_truth.live_constants()``."""
        self.assertEqual(self.block["constants"], ground_truth.live_constants())

    def test_kernel_dispatch_order(self) -> None:
        """The declared dispatch order matches ``all_kernels()``."""
        self.assertEqual(
            self.block["kernel_dispatch_order"],
            [kernel.name for kernel in all_kernels()],
        )

    def test_market_metrics_route_to_the_market_entity(self) -> None:
        """Exactly the declared market metrics attach to ``ent-market``."""
        ir = DOMAIN.translate(DOMAIN.packet("orbital-series-b"))
        market = set(self.block["market_metrics"])
        for claim in ir.claims:
            expected = "ent-market" if claim.predicate in market else "ent-company"
            self.assertEqual(claim.subject_id, expected, claim.predicate)

    def test_finding_catalogue_matches_a_live_run(self) -> None:
        """Every ``(kernel, finding_id, topic)`` the pipeline emits is declared."""
        emitted = set()
        for packet in ground_truth.PACKETS.values():
            result, _ = execute(packet, DOMAIN)
            for artifact in result.artifacts:
                for finding in artifact.findings:
                    emitted.add((artifact.kernel_name, finding.id, finding.topic))
        declared = {
            (row["kernel"], row["finding_id"], row["topic"])
            for row in self.block["finding_catalogue"]
        }
        self.assertEqual(emitted, declared)

    def test_recommendation_vocabulary(self) -> None:
        """The declared recommendation values match the live enum, in order."""
        self.assertEqual(
            self.block["constants"]["synthesis"]["recommendations"],
            [member.value for member in Recommendation],
        )

    def test_known_rule_names_are_the_six_decision_rules(self) -> None:
        """A guard on the R1..R6 names the comparison keys on."""
        run = ground_truth.build_ground_truth("orbital-series-b")
        names = {rule["name"] for rule in run["record"]["synthesis"]["rules_evaluated"]}
        self.assertTrue(names <= _KNOWN_RULE_NAMES, names)

    def test_canonical_helpers_are_importable(self) -> None:
        """The experiment depends on these frozen-package callables staying put."""
        for helper in (_canonical, record_digest, text_digest):
            self.assertTrue(callable(helper))


if __name__ == "__main__":
    unittest.main()
