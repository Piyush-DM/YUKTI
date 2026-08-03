"""The investment domain.

Everything investment-specific lives under this package: the packet shape, the
translator that maps it to the IR, and the four kernels that read that IR.

Nothing in ``choir_prototype/core/`` imports anything from here. That is checked
mechanically by ``audit.py`` (check A1).
"""

from __future__ import annotations

from choir_prototype.core.domain import Domain, PacketSummary
from choir_prototype.domains.investment.kernels import TOPICS, all_kernels
from choir_prototype.domains.investment.packets import PACKETS, InvestmentPacket
from choir_prototype.domains.investment.translator import translate


def describe(packet: InvestmentPacket) -> PacketSummary:
    """Tell the pipeline what it needs to know about an investment packet.

    The pipeline never reads packet fields itself, so this is the only place
    that knows an investment packet has sources, data points and conflicts.
    """
    return PacketSummary(
        packet_id=packet.id,
        title=packet.title,
        record_count=len(packet.data_points),
        notes=(
            f"{len(packet.sources)} source document(s)",
            f"{len(packet.data_points)} data point(s)",
            f"{len(packet.stated_assumptions)} stated assumption(s)",
            f"{len(packet.noted_conflicts)} flagged conflict(s)",
        ),
    )


DOMAIN = Domain(
    name="investment",
    description="Venture investment assessment from a diligence packet",
    translate=translate,
    describe=describe,
    kernels=all_kernels(),
    topics=TOPICS,
    packets=dict(PACKETS),
)
