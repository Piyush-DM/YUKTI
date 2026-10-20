"""The L-lo prompt is assembled offline and does not leak the answer.

Also asserts that no module in the scaffold imports a network client -- the
experiment must not be able to call a model.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from experiments.rubric_reproduction import build_prompt, ground_truth

_SCAFFOLD = Path(__file__).resolve().parents[1]
_MODULES = ["ground_truth.py", "build_prompt.py", "compare.py", "run.py"]
_NETWORK_IMPORT_RE = re.compile(
    r"^\s*(?:import|from)\s+"
    r"(openai|anthropic|requests|httpx|aiohttp|urllib|socket|http|websockets)\b",
    re.MULTILINE,
)

_RECOMMENDATION_PHRASES = [
    "proceed with conditions",
    "insufficient basis",
    "contested",
    "decline",
    "proceed",
]


class TestPromptContent(unittest.TestCase):
    """Claim: the prompt carries the rubric, the packet, the id map and schema."""

    def setUp(self) -> None:
        self.prompt = build_prompt.build("orbital-series-b")
        self.rubric = build_prompt.RUBRIC_PATH.read_text(encoding="utf-8")

    def test_contains_the_rubric_verbatim(self) -> None:
        self.assertIn(self.rubric.strip(), self.prompt)

    def test_contains_packet_data(self) -> None:
        for needle in (
            "Orbital Logistics Inc.",
            '"value": "18000000"',
            "SRC-AUDIT-FY24",
            "net_revenue_retention_pct",
            "Customer reference calls describe contraction",
        ):
            self.assertIn(needle, self.prompt, needle)

    def test_contains_the_id_map(self) -> None:
        self.assertIn("clm-001  arr_usd", self.prompt)
        self.assertIn("clm-015  reporting_cadence", self.prompt)
        self.assertIn("ent-market", self.prompt)
        self.assertIn("asm-002", self.prompt)

    def test_contains_the_output_schema(self) -> None:
        self.assertIn(build_prompt.OUTPUT_SCHEMA.strip(), self.prompt)
        self.assertIn('"recommendation":', self.prompt)

    def test_is_deterministic(self) -> None:
        self.assertEqual(self.prompt, build_prompt.build("orbital-series-b"))

    def test_does_not_leak_the_ground_truth_answer(self) -> None:
        """The packet-specific part of the prompt states no recommendation.

        Recommendation phrases legitimately appear inside the rubric (the R1..R6
        table) and the output schema (the enum). They must not appear anywhere
        else -- e.g. next to the packet, as an answer.
        """
        remainder = self.prompt
        for chunk in (
            build_prompt.PREAMBLE,
            self.rubric,
            build_prompt.OUTPUT_SCHEMA,
        ):
            remainder = remainder.replace(chunk, "")
        lowered = remainder.lower()
        for phrase in _RECOMMENDATION_PHRASES:
            self.assertNotIn(phrase, lowered, phrase)

        view = ground_truth.build_ground_truth("orbital-series-b")["comparison_view"]
        self.assertNotIn(view["confidence_limiting_factor"], self.prompt)

    def test_covers_both_packets(self) -> None:
        for packet_id in ground_truth.PACKETS:
            self.assertTrue(build_prompt.build(packet_id).strip())


class TestOffline(unittest.TestCase):
    """Claim: nothing in the scaffold can reach a network or a model."""

    def test_no_module_imports_a_network_client(self) -> None:
        for name in _MODULES:
            source = (_SCAFFOLD / name).read_text(encoding="utf-8")
            hits = _NETWORK_IMPORT_RE.findall(source)
            self.assertEqual(hits, [], f"{name} imports {hits}")

    def test_write_all_writes_only_prompt_files(self) -> None:
        written = build_prompt.write_all()
        self.assertTrue(written)
        for path in written:
            self.assertEqual(path.parent, build_prompt.PROMPTS_DIR)
            self.assertTrue(path.suffix in (".txt", ".json"))


if __name__ == "__main__":
    unittest.main()
