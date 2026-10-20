"""Assemble the L-lo control prompt. Makes no model call.

The L-lo ("rubric-executor") control receives exactly what the frozen pipeline
"has" and nothing more:

1. a neutral preamble instructing mechanical application of the rules, with no
   outside knowledge and no invented identifiers;
2. ``rubric.md`` verbatim -- the transcription of ``kernels.py`` / ``contracts.py``
   / ``synthesizer.py`` / the citation rule;
3. the deterministic id map for the packet (entity, evidence, claim and
   assumption ids), because forming those ids is translation, which the frozen
   ``translator.py`` performs with "no reasoning" -- handing the model the id map
   removes a numbering confound without doing any of its analysis for it;
4. the input packet, in the ``yukti-investment-document/0.1`` shape;
5. the required output JSON schema.

This module reads ``rubric.md`` and builds each packet document in memory via
``ground_truth.packet_to_document``. It imports no model client and opens no
socket.

Run: ``python -m experiments.rubric_reproduction.build_prompt``
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from experiments.rubric_reproduction import ground_truth

HERE = Path(__file__).resolve().parent
RUBRIC_PATH = HERE / "rubric.md"
PROMPTS_DIR = HERE / "prompts"

VARIANT = "L-lo"

PREAMBLE = """\
You are executing a fixed, deterministic analytical procedure. It is written out
in full below, transcribed from a reference implementation. Your task is to apply
it exactly as specified and report the result.

Rules:

- Use ONLY the information in the INPUT PACKET below. Do not use any outside
  knowledge about the company, the sector, comparable transactions, or base
  rates. If a rule needs a value the packet does not contain, follow the rule's
  stated behaviour for a missing value.
- Do not invent any identifier. Every id you cite must appear in the ID MAP or
  the INPUT PACKET below.
- Apply the numeric thresholds and the branch order exactly as written. Do not
  substitute your own judgement for a threshold comparison.
- Produce the confidence bands by the stated derivation rules only. Do not assign
  a confidence value directly.
- Return exactly one JSON object matching the REQUIRED OUTPUT schema, with no
  prose, commentary, or markdown fences outside the object.
"""

OUTPUT_SCHEMA = """\
{
  "artifacts": [
    {
      "kernel_name": "<financial_posture | risk_exposure | market_position | governance>",
      "findings": [
        {
          "id": "<finding id from the rubric's finding catalogue>",
          "topic": "<topic from the rubric's topic list>",
          "stance": "<supports | opposes | conditional | neutral>",
          "statement": "<the statement text the rule specifies>",
          "claim_ids": ["clm-0NN", "..."],
          "evidence_ids": ["SRC-...", "..."]
        }
      ],
      "evidence_references": ["SRC-...", "..."],
      "confidence": {
        "band": "<high | moderate | low | insufficient>",
        "limiting_factor": "<the limiting-factor string the rule specifies>",
        "evidence_floor": "<audited | reported | estimated | asserted | none>",
        "coverage": "<found>/<expected> expected inputs present",
        "contradictions": <integer>,
        "derivation": ["rule 0: ...", "rule 1: ...", "..."]
      },
      "assumptions": ["...", "..."],
      "unresolved_questions": ["...", "..."]
    }
  ],
  "synthesis": {
    "recommendation": "<proceed | proceed with conditions | decline | contested | insufficient basis>",
    "confidence": "<high | moderate | low | insufficient>",
    "confidence_limiting_factor": "<string>",
    "support_weight": <integer>,
    "oppose_weight": <integer>,
    "conditional_count": <integer>,
    "usable_kernels": ["<kernel name>", "..."],
    "agreements": [{"topic": "<topic>"}],
    "disagreements": [{"topic": "<topic>"}],
    "rules_evaluated": [{"name": "R1 insufficient-basis", "fired": false}, "..."],
    "remaining_uncertainty": ["[kernel] ...", "..."],
    "rationale": ["...", "..."]
  }
}
"""


def _id_map(document: dict[str, Any]) -> str:
    """The deterministic id map the translator would produce for this document."""
    lines = [
        "Entities:",
        "  ent-company   (every metric except the three market metrics below)",
        "  ent-market    (tam_usd, market_growth_pct, competitor_count)",
        "",
        "Evidence ids (one per source; cite these exactly):",
    ]
    for source in document["sources"]:
        lines.append(f"  {source['label']:<16} {source['origin']} ({source['kind']})")
    lines.append("")
    lines.append("Claim ids (one per data point, in packet order):")
    for index, point in enumerate(document["data_points"], start=1):
        lines.append(f"  clm-{index:03d}  {point['metric']}")
    lines.append("")
    lines.append("Assumption ids (one per stated assumption, in packet order):")
    for index, _ in enumerate(document["stated_assumptions"], start=1):
        lines.append(f"  asm-{index:03d}")
    return "\n".join(lines)


def build(
    packet_id: str,
    variant: str = VARIANT,
    document: dict[str, Any] | None = None,
) -> str:
    """Return the full L-lo prompt string for one packet. No model call."""
    if variant != VARIANT:
        raise ValueError(f"only the {VARIANT!r} variant is defined in this scaffold")
    if document is None:
        document = ground_truth.packet_to_document(ground_truth.PACKETS[packet_id])

    rubric = RUBRIC_PATH.read_text(encoding="utf-8")
    sections = [
        PREAMBLE,
        "=" * 78,
        "RUBRIC (verbatim transcription of the frozen implementation)",
        "=" * 78,
        rubric,
        "=" * 78,
        "ID MAP (use these identifiers exactly; do not invent others)",
        "=" * 78,
        _id_map(document),
        "=" * 78,
        "INPUT PACKET (this is all the information available)",
        "=" * 78,
        json.dumps(document, indent=2),
        "=" * 78,
        "REQUIRED OUTPUT",
        "=" * 78,
        OUTPUT_SCHEMA,
    ]
    return "\n".join(sections) + "\n"


def write_all(out_dir: Path = PROMPTS_DIR) -> list[Path]:
    """Write one L-lo prompt per packet plus the shared schema. Returns paths."""
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for packet_id in ground_truth.PACKETS:
        prompt = build(packet_id)
        path = out_dir / f"{packet_id}__{VARIANT}.txt"
        path.write_text(prompt, encoding="utf-8")
        written.append(path)
    schema_path = out_dir / "OUTPUT_SCHEMA.json"
    schema_path.write_text(OUTPUT_SCHEMA, encoding="utf-8")
    written.append(schema_path)
    return written


def main() -> int:
    """Regenerate every L-lo prompt."""
    written = write_all()
    for path in written:
        print(f"written: {path.relative_to(HERE.parent.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
