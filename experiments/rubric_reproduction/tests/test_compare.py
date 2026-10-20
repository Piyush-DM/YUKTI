"""The comparison engine is deterministic, network-free, and grades as designed.

A perfect response reproduces; a supports<->opposes stance flip diverges; a
one-band slip is partial; a fabricated citation is an X4 divergence; a different
recommendation is a tier-1 divergence.
"""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from experiments.rubric_reproduction import compare, ground_truth


def _ground_truth_payload(packet_id: str = "orbital-series-b") -> dict:
    return ground_truth.build_ground_truth(packet_id)


def _write(tmp: Path, name: str, payload: dict) -> Path:
    path = tmp / name
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


class TestComparison(unittest.TestCase):
    """Claim: ``compare`` grades a response against ground truth as designed."""

    def setUp(self) -> None:
        self.payload = _ground_truth_payload()
        self.record = self.payload["record"]

    def _run(self, response_record: dict) -> dict:
        with tempfile.TemporaryDirectory() as raw:
            tmp = Path(raw)
            gt_path = _write(tmp, "gt.json", self.payload)
            resp_path = _write(tmp, "resp.json", {"record": response_record})
            return compare.compare_files(gt_path, resp_path)

    def test_identical_response_reproduces(self) -> None:
        result = self._run(copy.deepcopy(self.record))
        self.assertEqual(result["verdict"], "Reproduces")
        self.assertEqual(result["x4_violations"], [])
        for tier in result["per_field"].values():
            for field, verdict in tier.items():
                self.assertEqual(verdict, "match", field)

    def test_stance_flip_diverges(self) -> None:
        record = copy.deepcopy(self.record)
        for artifact in record["artifacts"]:
            for finding in artifact["findings"]:
                if finding["stance"] == "supports":
                    finding["stance"] = "opposes"
                    break
            else:
                continue
            break
        result = self._run(record)
        self.assertEqual(result["per_field"]["tier2"]["findings"], "divergence")
        self.assertEqual(result["verdict"], "Diverges")

    def test_one_band_slip_is_partial(self) -> None:
        record = copy.deepcopy(self.record)
        for artifact in record["artifacts"]:
            if artifact["confidence"]["band"] == "moderate":
                artifact["confidence"]["band"] = "low"
                break
        result = self._run(record)
        self.assertEqual(result["per_field"]["tier2"]["kernel_bands"], "partial")

    def test_fabricated_citation_is_an_x4_divergence(self) -> None:
        record = copy.deepcopy(self.record)
        record["artifacts"][0]["findings"][0]["claim_ids"] = ["clm-999"]
        result = self._run(record)
        self.assertIn("clm-999", result["x4_violations"])
        self.assertEqual(result["verdict"], "Diverges")

    def test_different_recommendation_is_a_tier1_divergence(self) -> None:
        record = copy.deepcopy(self.record)
        record["synthesis"]["recommendation"] = "decline"
        result = self._run(record)
        self.assertEqual(result["per_field"]["tier1"]["recommendation"], "divergence")
        self.assertEqual(result["verdict"], "Diverges")

    def test_comparison_is_deterministic(self) -> None:
        record = copy.deepcopy(self.record)
        first = self._run(record)
        second = self._run(copy.deepcopy(record))
        # Drop the input-path fields, which differ per temp directory.
        for result in (first, second):
            result.pop("ground_truth", None)
            result.pop("response", None)
        self.assertEqual(first, second)

    def test_build_comparison_view_has_every_scored_field(self) -> None:
        view = compare.build_comparison_view(self.record)
        for field in compare.TIER1_FIELDS + compare.TIER2_FIELDS + compare.TIER3_FIELDS:
            self.assertIn(field, view, field)


if __name__ == "__main__":
    unittest.main()
