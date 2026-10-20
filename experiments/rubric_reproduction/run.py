"""Orchestrate the offline half of the experiment, then stop.

This regenerates ground truth from the frozen pipeline and assembles the L-lo
control prompts. It does **not** call any language model and does **not** run the
comparison (there are no responses yet). It stops at:

    prompts generated; awaiting external model responses.

After that line, a human collects model responses into
``experiments/rubric_reproduction/responses/`` (record shape per
``prompts/OUTPUT_SCHEMA.json``) and runs ``compare.py`` per response.

Run: ``python -m experiments.rubric_reproduction.run``
"""

from __future__ import annotations

from experiments.rubric_reproduction import build_prompt, ground_truth

STOP_LINE = "prompts generated; awaiting external model responses."


def main() -> int:
    """Regenerate ground truth and prompts, then stop before any model call."""
    print("Regenerating ground truth from the frozen choir_prototype pipeline...")
    ground_truth_paths = ground_truth.write_all()
    for path in ground_truth_paths:
        print(f"  wrote {path}")

    print("\nAssembling L-lo control prompts...")
    prompt_paths = build_prompt.write_all()
    for path in prompt_paths:
        print(f"  wrote {path}")

    print()
    print(STOP_LINE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
