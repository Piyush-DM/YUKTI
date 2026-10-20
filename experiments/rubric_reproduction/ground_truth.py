"""Derive ground truth from the frozen ``choir_prototype`` implementation.

Nothing here transcribes an expected value by hand. The ground truth for each
packet is produced by importing the frozen package and running its own pipeline:

    execute(packet, DOMAIN) -> (RunResult, Synthesis)

The record is then reduced with the frozen package's own canonical form
(``choir_prototype.core.replay._canonical`` -- the exact reduction its record
digest is computed over, imported here for the same reason
``applications/investment/vertical_slice/run.py`` imports it: a second copy would
be a second answer to the same question). ``build_comparison_view`` from
``compare`` extracts the scored fields, so ground truth and any response are
reduced by identical code.

``live_constants()`` reads the numeric constants, enum members and predicate
lists straight from the live modules. ``rubric.md`` carries a copy of the same
structure; ``tests/test_rubric_drift.py`` asserts the two are equal, so a change
to a threshold in ``kernels.py`` (or a band weight in ``contracts.py``, etc.)
fails a test until ``rubric.md`` is updated to match.

Run: ``python -m experiments.rubric_reproduction.ground_truth``
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from choir_prototype.core.pipeline import execute
from choir_prototype.core.replay import _canonical, record_digest, text_digest
from choir_prototype.core.report import render
from choir_prototype.domains.investment import DOMAIN
from choir_prototype.domains.investment.packets import (
    NORTHWIND_SEED,
    ORBITAL_SERIES_B,
    InvestmentPacket,
)

from experiments.rubric_reproduction import compare

HERE = Path(__file__).resolve().parent
GROUND_TRUTH_DIR = HERE / "ground_truth"

DOCUMENT_VERSION = "yukti-investment-document/0.1"

# The two synthetic investment packets that ship in the frozen prototype. There
# are no others in the investment domain.
PACKETS: dict[str, InvestmentPacket] = {
    ORBITAL_SERIES_B.id: ORBITAL_SERIES_B,
    NORTHWIND_SEED.id: NORTHWIND_SEED,
}

_THRESHOLD_NAMES = [
    "STRONG_GROWTH_PCT",
    "WEAK_GROWTH_PCT",
    "HEALTHY_MARGIN_PCT",
    "WEAK_MARGIN_PCT",
    "COMFORTABLE_RUNWAY_MONTHS",
    "TIGHT_RUNWAY_MONTHS",
    "CONCENTRATION_ALERT_PCT",
    "CONCENTRATION_SEVERE_PCT",
    "HEALTHY_NRR_PCT",
    "WEAK_NRR_PCT",
    "HIGH_CHURN_PCT",
    "EFFICIENT_BURN_RATIO",
    "UNSUSTAINABLE_BURN_RATIO",
    "LARGE_TAM_USD",
    "STRONG_MARKET_GROWTH_PCT",
    "CROWDED_COMPETITOR_COUNT",
    "FOUNDER_CONTROL_ALERT_PCT",
    "MINIMUM_INDEPENDENT_SEATS",
]


def live_constants() -> dict[str, Any]:
    """Read the rubric's numeric constants straight from the live source modules.

    The single place the experiment reads these symbols. Both the ground-truth
    ``source_fingerprint`` and the rubric-drift test compare against this.
    """
    from choir_prototype.core import contracts as contracts_mod
    from choir_prototype.core.ir import _EVIDENCE_RANK
    from choir_prototype.core.synthesizer import (
        DOMINANCE_MARGIN,
        MINIMUM_USABLE_KERNELS,
        Recommendation,
    )
    from choir_prototype.domains.investment import kernels as kernels_mod
    from choir_prototype.domains.investment import translator as translator_mod

    kernel_classes = (
        kernels_mod.FinancialPostureKernel,
        kernels_mod.RiskExposureKernel,
        kernels_mod.MarketPositionKernel,
        kernels_mod.GovernanceKernel,
    )
    kernel_specs = {
        cls.name: {
            "predicates": list(cls.PREDICATES),
            "expected_inputs": len(cls.PREDICATES),
        }
        for cls in kernel_classes
    }

    return {
        "translator": {
            "TRANSLATOR_NAME": translator_mod.TRANSLATOR_NAME,
            "IR_VERSION": translator_mod.IR_VERSION,
            "kind_to_quality": {
                key: value.name
                for key, value in translator_mod._KIND_TO_QUALITY.items()
            },
            "kind_to_quality_default": "ASSERTED",
            "status_to_uncertainty": {
                key: value.name
                for key, value in translator_mod._STATUS_TO_UNCERTAINTY.items()
            },
            "status_to_uncertainty_default": "UNKNOWN",
        },
        "evidence_quality_rank": {
            member.name: rank for member, rank in _EVIDENCE_RANK.items()
        },
        "confidence": {
            "MINIMUM_COVERAGE": contracts_mod.MINIMUM_COVERAGE,
            "quality_rank_to_band": {
                str(rank): band.name
                for rank, band in contracts_mod._QUALITY_RANK_TO_BAND.items()
            },
            "band_order_strong_to_weak": [
                band.name for band in contracts_mod._ORDERED_BANDS
            ],
        },
        "band_weight": {
            band.name: weight for band, weight in contracts_mod._BAND_WEIGHT.items()
        },
        "synthesis": {
            "MINIMUM_USABLE_KERNELS": MINIMUM_USABLE_KERNELS,
            "DOMINANCE_MARGIN": DOMINANCE_MARGIN,
            "recommendations": [member.value for member in Recommendation],
        },
        "kernels": kernel_specs,
        "thresholds": {name: getattr(kernels_mod, name) for name in _THRESHOLD_NAMES},
        "topics": list(kernels_mod.TOPICS),
    }


def packet_to_document(packet: InvestmentPacket) -> dict[str, Any]:
    """Serialise a packet into the ``yukti-investment-document/0.1`` shape.

    This is the same shape ``applications/investment/vertical_slice`` parses. It
    is produced from the frozen packet object, not copied from a file, so it
    cannot drift from the packet the pipeline actually reasons over.
    """
    return {
        "document_version": DOCUMENT_VERSION,
        "id": packet.id,
        "title": packet.title,
        "company_name": packet.company_name,
        "sector": packet.sector,
        "stage": packet.stage,
        "sources": [
            {"label": source.label, "origin": source.origin, "kind": source.kind}
            for source in packet.sources
        ],
        "data_points": [
            {
                "metric": point.metric,
                "value": point.value,
                "source_labels": list(point.source_labels),
                "status": point.status,
            }
            for point in packet.data_points
        ],
        "stated_assumptions": list(packet.stated_assumptions),
        "noted_conflicts": [
            {"metric": conflict.metric, "note": conflict.note}
            for conflict in packet.noted_conflicts
        ],
    }


def _ir_known_ids(ir_record: dict[str, Any]) -> list[str]:
    """Every addressable id in a canonical IR record (the X4 allow-list)."""
    ids: set[str] = set()
    for section in ("entities", "claims", "evidence", "assumptions", "relationships"):
        for item in ir_record.get(section, []):
            if isinstance(item, dict) and "id" in item:
                ids.add(item["id"])
    return sorted(ids)


def build_ground_truth(packet_id: str) -> dict[str, Any]:
    """Run the frozen pipeline for one packet and assemble its ground-truth record."""
    packet = PACKETS[packet_id]
    result, synthesis = execute(packet, DOMAIN)

    record = {
        "ir": _canonical(result.ir),
        "artifacts": _canonical(result.artifacts),
        "synthesis": _canonical(synthesis),
        "trace": _canonical(result.trace),
    }
    report_text = render(result, synthesis)
    constants = live_constants()

    return {
        "experiment": "rubric_reproduction",
        "packet_id": packet_id,
        "generated_by": "experiments/rubric_reproduction/ground_truth.py",
        "note": (
            "Derived by running choir_prototype's own pipeline. No expected value "
            "is hand-written here."
        ),
        "source_fingerprint": hashlib.sha256(
            json.dumps(constants, sort_keys=True).encode("utf-8")
        ).hexdigest(),
        "record_digest": record_digest(result, synthesis),
        "report_digest": text_digest(report_text),
        "report_text": report_text,
        "ir_known_ids": _ir_known_ids(record["ir"]),
        "record": record,
        "comparison_view": compare.build_comparison_view(record),
        "document": packet_to_document(packet),
    }


def write_all(out_dir: Path = GROUND_TRUTH_DIR) -> list[Path]:
    """Write a ground-truth file per packet. Returns the paths written."""
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for packet_id in PACKETS:
        payload = build_ground_truth(packet_id)
        path = out_dir / f"{packet_id}.json"
        path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        written.append(path)
        document_path = out_dir / f"{packet_id}__document.json"
        document_path.write_text(
            json.dumps(payload["document"], indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        written.append(document_path)
    return written


def main() -> int:
    """Regenerate every ground-truth file."""
    written = write_all()
    for path in written:
        print(f"written: {path.relative_to(HERE.parent.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
