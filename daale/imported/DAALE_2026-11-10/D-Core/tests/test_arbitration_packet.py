"""Regression tests for the versioned R-Fabric/D-Core arbitration packet."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from daale.execution.arbitration import _has_internal_contradiction
from daale.execution.arbitration_packet import (
    ARBITRATION_PACKET_SCHEMA,
    ArbitrationPacketError,
    EvidenceBoundStatus,
    RFabricArbitrationPacket,
    decision_packet_digest,
)
from daale.execution.commit import Candidate
from daale import rfabric
from daale.rfabric import build_arbitration_packet, build_candidate


FIXTURE = Path(__file__).parent / "fixtures" / "rfabric_stress_run3_packet.json"


class TestRFabricArbitrationPacket(unittest.TestCase):
    def test_actual_stress_run3_packet_is_admitted_without_a_type_crash(self) -> None:
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        trace = fixture["trace"]
        packet = build_arbitration_packet(trace)

        self.assertEqual(fixture["source_trace"]["run_id"], trace["run"]["run_id"])
        self.assertEqual(packet.schema_version, ARBITRATION_PACKET_SCHEMA)
        claim = next(item for item in packet.claims if item.object_id == "C2")
        self.assertEqual(claim.status, "CONTRADICTED")
        self.assertTrue(claim.evidence_ids)

        candidate = build_candidate(trace, "exec-stress-run3", _EmptyStore())
        conflict, detail = _has_internal_contradiction(candidate)
        self.assertTrue(conflict)
        self.assertIn("C2", detail)
        self.assertIn("R1", detail)
        self.assertIn("E17", detail)

        # The actual packet contains the same-evidence contradiction. It must be
        # rejected by arbitration, not crash and not pass to the commit gate.
        admission = rfabric.admit(trace)
        self.assertEqual(admission.outcome.state.value, "rejected")

    def test_same_evidence_contradiction_still_fails_the_existing_check(self) -> None:
        packet = RFabricArbitrationPacket(
            schema_version=ARBITRATION_PACKET_SCHEMA,
            decision_packet_sha256=decision_packet_digest(
                {"provisional_claim_statuses": {"C2": "CONTRADICTED"}}
            ),
            claims=(EvidenceBoundStatus("C2", "CONTRADICTED", ("E6", "E7")),),
            requirements=(EvidenceBoundStatus("R3", "SATISFIED", ("E7",)),),
        )
        candidate = Candidate(
            candidate_id="cnd-overlap",
            execution_id="exec-overlap",
            object_id="obj-overlap",
            payload={"provisional_claim_statuses": {"C2": "CONTRADICTED"}},
            provenance=("C2", "E6", "E7"),
            read_versions={},
            origin="rfabric",
            arbitration_packet=packet,
        )

        conflict, detail = _has_internal_contradiction(candidate)
        self.assertTrue(conflict)
        self.assertIn("C2", detail)
        self.assertIn("R3", detail)
        self.assertIn("E7", detail)

    def test_missing_evidence_context_fails_closed_for_a_contradicted_claim(self) -> None:
        candidate = Candidate(
            candidate_id="cnd-missing-context",
            execution_id="exec-missing-context",
            object_id="obj-missing-context",
            payload={"provisional_claim_statuses": {"C2": "CONTRADICTED"}},
            provenance=("C2",),
            read_versions={},
            origin="rfabric",
        )
        conflict, detail = _has_internal_contradiction(candidate)
        self.assertTrue(conflict)
        self.assertIn("packet is required", detail)

    def test_context_is_bound_to_the_exact_candidate_decision_packet(self) -> None:
        packet = RFabricArbitrationPacket(
            schema_version=ARBITRATION_PACKET_SCHEMA,
            decision_packet_sha256=decision_packet_digest(
                {"provisional_claim_statuses": {"C2": "CONTRADICTED"}}
            ),
            claims=(EvidenceBoundStatus("C2", "CONTRADICTED", ("E6",)),),
            requirements=(),
        )
        candidate = Candidate(
            candidate_id="cnd-tampered",
            execution_id="exec-tampered",
            object_id="obj-tampered",
            payload={"provisional_claim_statuses": {"C2": "SUPPORTED"}},
            provenance=("C2", "E6"),
            read_versions={},
            origin="rfabric",
            arbitration_packet=packet,
        )

        conflict, detail = _has_internal_contradiction(candidate)
        self.assertTrue(conflict)
        self.assertIn("digest does not match", detail)

    def test_duplicate_ids_and_invalid_statuses_are_rejected_by_the_schema(self) -> None:
        with self.assertRaisesRegex(ArbitrationPacketError, "duplicate claim IDs"):
            RFabricArbitrationPacket(
                schema_version=ARBITRATION_PACKET_SCHEMA,
                decision_packet_sha256="0" * 64,
                claims=(
                    EvidenceBoundStatus("C1", "SUPPORTED", ("E1",)),
                    EvidenceBoundStatus("C1", "CONTRADICTED", ("E2",)),
                ),
                requirements=(),
            )
        with self.assertRaisesRegex(ArbitrationPacketError, "unsupported status"):
            RFabricArbitrationPacket(
                schema_version=ARBITRATION_PACKET_SCHEMA,
                decision_packet_sha256="0" * 64,
                claims=(EvidenceBoundStatus("C1", "SATISFIED", ("E1",)),),
                requirements=(),
            )


class _EmptyStore:
    def current_version(self, object_id):
        return None


if __name__ == "__main__":
    unittest.main()
