"""Ground truth is derived from the frozen pipeline, not hand-written.

These tests check that ``ground_truth.build_ground_truth`` reflects the live
pipeline (recommendation, confidence, fired rule, tally), that its tally is
internally consistent, that it is deterministic, and that the document it emits
round-trips through the real vertical-slice parser.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from choir_prototype.core.synthesizer import Recommendation
from choir_prototype.domains.investment.packets import ORBITAL_SERIES_B

from applications.investment.vertical_slice.parse import parse_document
from experiments.rubric_reproduction import ground_truth

_REPO_ROOT = Path(__file__).resolve().parents[3]
_COMMITTED_DOCUMENT = (
    _REPO_ROOT
    / "applications"
    / "investment"
    / "vertical_slice"
    / "documents"
    / "orbital-series-b.json"
)


class TestGroundTruthReflectsThePipeline(unittest.TestCase):
    """Claim: the ground-truth file is the frozen pipeline's own output."""

    def test_orbital_headline_result(self) -> None:
        view = ground_truth.build_ground_truth("orbital-series-b")["comparison_view"]
        self.assertEqual(view["recommendation"], "proceed with conditions")
        self.assertEqual(view["confidence"], "low")
        self.assertEqual(view["fired_rule"], "R3 proceed-with-conditions")
        self.assertEqual(view["tally"], {"support": 7, "oppose": 1, "conditional": 5})
        self.assertEqual(
            sorted(view["usable_kernels"]),
            ["financial_posture", "governance", "market_position", "risk_exposure"],
        )
        self.assertEqual(view["agreements"], ["capital_efficiency"])
        self.assertEqual(view["disagreements"], ["revenue_quality"])

    def test_northwind_declines(self) -> None:
        view = ground_truth.build_ground_truth("northwind-seed")["comparison_view"]
        self.assertEqual(view["recommendation"], "insufficient basis")
        self.assertEqual(view["confidence"], "insufficient")
        self.assertEqual(view["fired_rule"], "R1 insufficient-basis")

    def test_recommendation_is_in_the_live_vocabulary(self) -> None:
        allowed = {member.value for member in Recommendation}
        for packet_id in ground_truth.PACKETS:
            view = ground_truth.build_ground_truth(packet_id)["comparison_view"]
            self.assertIn(view["recommendation"], allowed)

    def test_tally_is_internally_consistent(self) -> None:
        """Re-derive the tally from the artifacts and the band-weight table."""
        weights = ground_truth.live_constants()["band_weight"]
        band_weight = {name.lower(): value for name, value in weights.items()}
        for packet_id in ground_truth.PACKETS:
            record = ground_truth.build_ground_truth(packet_id)["record"]
            support = oppose = conditional = 0
            for artifact in record["artifacts"]:
                weight = band_weight[artifact["confidence"]["band"]]
                for finding in artifact["findings"]:
                    stance = finding["stance"]
                    if stance == "supports":
                        support += weight
                    elif stance == "opposes":
                        oppose += weight
                    elif stance == "conditional":
                        conditional += 1
            synthesis = record["synthesis"]
            self.assertEqual(support, synthesis["support_weight"], packet_id)
            self.assertEqual(oppose, synthesis["oppose_weight"], packet_id)
            self.assertEqual(conditional, synthesis["conditional_count"], packet_id)

    def test_deterministic(self) -> None:
        first = ground_truth.build_ground_truth("orbital-series-b")
        second = ground_truth.build_ground_truth("orbital-series-b")
        self.assertEqual(first["record"], second["record"])
        self.assertEqual(first["record_digest"], second["record_digest"])
        self.assertEqual(first["source_fingerprint"], second["source_fingerprint"])

    def test_ir_known_ids_cover_every_addressable_kind(self) -> None:
        ids = set(ground_truth.build_ground_truth("orbital-series-b")["ir_known_ids"])
        self.assertIn("ent-company", ids)
        self.assertIn("ent-market", ids)
        self.assertIn("clm-001", ids)
        self.assertIn("SRC-AUDIT-FY24", ids)
        self.assertIn("asm-001", ids)
        self.assertTrue(any(value.startswith("rel-") for value in ids))


class TestDocumentSerialisation(unittest.TestCase):
    """Claim: the document handed to the control is the real packet, serialised."""

    def test_round_trips_through_the_vertical_slice_parser(self) -> None:
        document = ground_truth.packet_to_document(ORBITAL_SERIES_B)
        reparsed = parse_document(json.dumps(document), origin="test")
        self.assertEqual(reparsed, ORBITAL_SERIES_B)

    def test_matches_the_committed_sample_document(self) -> None:
        document = ground_truth.packet_to_document(ORBITAL_SERIES_B)
        committed = json.loads(_COMMITTED_DOCUMENT.read_text(encoding="utf-8"))
        self.assertEqual(document, committed)


class TestGroundTruthFiles(unittest.TestCase):
    """Claim: ``write_all`` produces one valid JSON file per packet."""

    def test_write_all_creates_files(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            out_dir = Path(raw)
            written = ground_truth.write_all(out_dir)
            names = {path.name for path in written}
            self.assertIn("orbital-series-b.json", names)
            self.assertIn("northwind-seed.json", names)
            self.assertIn("orbital-series-b__document.json", names)
            for path in written:
                json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
