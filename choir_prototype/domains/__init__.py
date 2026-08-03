"""Domain layer (L2).

Each module here supplies one domain: packets, a translator, kernels, and a
topic vocabulary, bound together as a ``Domain``. Domains import from the core;
the core never imports from here. ``audit.py`` check A1 enforces that direction.

``investment`` is a package only because it predates this layering; the other
three are single files, which is the shape a new domain should take. Adding a
domain means adding one file and one line in ``REGISTRY``.

``engineering`` is the hold-out: it was written after the core was frozen and
hashed, as a control on whether the decoupling generalises.
"""

from __future__ import annotations

from choir_prototype.core.domain import Domain
from choir_prototype.domains import engineering, investment, law, medicine

REGISTRY: dict[str, Domain] = {
    investment.DOMAIN.name: investment.DOMAIN,
    law.DOMAIN.name: law.DOMAIN,
    medicine.DOMAIN.name: medicine.DOMAIN,
    engineering.DOMAIN.name: engineering.DOMAIN,
}

# Domains used while decoupling the core, versus the one held back as a control.
DEVELOPMENT_SET = ("investment", "law", "medicine")
HOLD_OUT = ("engineering",)


def find_packet(packet_id: str) -> tuple[Domain, object] | None:
    """Locate a packet by id across every domain."""
    for domain in REGISTRY.values():
        packet = domain.packet(packet_id)
        if packet is not None:
            return domain, packet
    return None


def all_packets() -> list[tuple[Domain, object]]:
    """Every packet in every domain, in registry order."""
    return [
        (domain, packet)
        for domain in REGISTRY.values()
        for packet in domain.packets.values()
    ]
