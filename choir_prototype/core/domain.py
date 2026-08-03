"""The extension point a domain plugs into.

A domain supplies four things and nothing else:

- **packets**   the input material, in whatever shape that domain uses
- **translate** a function mapping one of those packets to the CHOIR IR
- **kernels**   independent readers of that IR
- **topics**    the vocabulary its kernels use to label findings

The core knows this shape. It does not know any particular domain, and no module
under ``core/`` imports anything under ``domains/``. That direction is checked
mechanically by ``audit.py`` (check A1), because a layering rule nobody verifies
is a layering rule that has already been broken.

Everything downstream of ``translate`` -- runtime, synthesizer, confidence,
conflict detection, report, inspection, replay -- is shared. A domain cannot
override any of it, which is what makes agreement across domains meaningful
rather than a coincidence of configuration.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from choir_prototype.core.contracts import Kernel
from choir_prototype.core.ir import ChoirIR


@dataclass(frozen=True)
class PacketSummary:
    """What the pipeline needs to know about a packet it cannot read.

    Packets are domain-shaped: an investment packet has data points and source
    documents, a clinical packet has observations and guidelines. The core never
    touches those fields. It asks the domain to describe the packet instead, so
    no packet shape is baked into the pipeline.
    """

    packet_id: str
    title: str
    record_count: int
    notes: tuple[str, ...]


@dataclass(frozen=True)
class Domain:
    """One domain's binding into the shared pipeline."""

    name: str
    description: str
    translate: Callable[[Any], ChoirIR]
    describe: Callable[[Any], PacketSummary]
    kernels: tuple[Kernel, ...]
    topics: tuple[str, ...]
    packets: dict[str, Any]

    def packet(self, packet_id: str) -> Any | None:
        """Return a packet by id, or None."""
        return self.packets.get(packet_id)

    def declared_topics(self) -> tuple[str, ...]:
        """Topics this domain's kernels are expected to emit, sorted."""
        return tuple(sorted(self.topics))
