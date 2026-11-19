"""Versioned, evidence-bound R-Fabric context used by D-Core arbitration.

The public R-Fabric decision packet stores one status per claim, while the
internal contradiction check also needs the evidence behind that status. This
small adapter schema keeps those concerns explicit without changing the
decision packet that R-Fabric records or replays.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass


ARBITRATION_PACKET_SCHEMA = "rfabric-arbitration/1.0"
CLAIM_STATES = frozenset({"SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE", "UNKNOWN"})
REQUIREMENT_STATES = frozenset({"SATISFIED", "NOT_SATISFIED", "UNKNOWN"})


class ArbitrationPacketError(ValueError):
    """The R-Fabric trace cannot be translated without losing evidence authority."""


@dataclass(frozen=True)
class EvidenceBoundStatus:
    """One final claim or requirement status and the exact evidence IDs it cites."""

    object_id: str
    status: str
    evidence_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.object_id, str) or not self.object_id:
            raise ArbitrationPacketError("arbitration status needs a non-empty object_id")
        if not isinstance(self.status, str) or not self.status:
            raise ArbitrationPacketError(f"{self.object_id}: arbitration status must be a string")
        if any(not isinstance(item, str) or not item for item in self.evidence_ids):
            raise ArbitrationPacketError(f"{self.object_id}: evidence IDs must be non-empty strings")
        if len(set(self.evidence_ids)) != len(self.evidence_ids):
            raise ArbitrationPacketError(f"{self.object_id}: duplicate evidence IDs")


@dataclass(frozen=True)
class RFabricArbitrationPacket:
    """The bounded, versioned cross-package input to the D-Core contradiction check."""

    schema_version: str
    decision_packet_sha256: str
    claims: tuple[EvidenceBoundStatus, ...]
    requirements: tuple[EvidenceBoundStatus, ...]

    def __post_init__(self) -> None:
        if self.schema_version != ARBITRATION_PACKET_SCHEMA:
            raise ArbitrationPacketError(
                f"unsupported arbitration packet schema: {self.schema_version!r}"
            )
        if (
            len(self.decision_packet_sha256) != 64
            or any(char not in "0123456789abcdef" for char in self.decision_packet_sha256)
        ):
            raise ArbitrationPacketError("decision_packet_sha256 must be a lowercase SHA-256 digest")
        for label, entries, allowed in (
            ("claim", self.claims, CLAIM_STATES),
            ("requirement", self.requirements, REQUIREMENT_STATES),
        ):
            ids = [item.object_id for item in entries]
            if len(ids) != len(set(ids)):
                raise ArbitrationPacketError(f"duplicate {label} IDs in arbitration packet")
            for item in entries:
                if item.status not in allowed:
                    raise ArbitrationPacketError(
                        f"{label} {item.object_id}: unsupported status {item.status!r}"
                    )


def decision_packet_digest(payload) -> str:
    """Hash the exact JSON decision packet the arbitration context supplements."""
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


__all__ = [
    "ARBITRATION_PACKET_SCHEMA",
    "ArbitrationPacketError",
    "decision_packet_digest",
    "EvidenceBoundStatus",
    "RFabricArbitrationPacket",
]
