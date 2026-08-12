"""Material identity: what a judgment was formed from.

A **Material Snapshot** is the immutable institutional material a judgment rests
on. It exists entirely above CHOIR and DAALE, and nothing here reaches the
engine.

Why this layer exists
---------------------

The reasoning record has a digest, and it proves two runs reached the same
conclusion. It does not prove they read the same material, because the engine
discards distinctions the institution records. Verified before this layer was
built: a figure recorded as ``reported`` and the same figure recorded as
``estimated`` collapse to the same ``Uncertainty.LIKELY`` inside the frozen
translator, produce an identical intermediate representation, and therefore an
identical ``record_digest``.

Two materially different diligence packs, one hash. A committee comparing
digests would conclude they had reviewed the same case.

``material_digest`` closes that. It is computed here, at full institutional
fidelity, over the material exactly as recorded -- including the vocabulary the
engine flattens.

The invariant that makes it work
--------------------------------

**Material identity is finer-grained than reasoning identity.**

    same material  =>  always the same reasoning record
    same record    =>  not necessarily the same material

So a material digest can be relied on where a record digest cannot, and
supersession keys on material: a change to what the institution assembled
creates a new judgment even when the conclusion is unchanged. Institutional
history records deliberation over material, not only changes of mind.

That direction is why the digest is computed over the material **in recorded
order** rather than over a normalised set. Claim identifiers in the engine are
positional, so re-ordering the diligence schedule changes the reasoning record.
A digest that ignored order would be coarser than the record it is supposed to
be finer than, and the invariant above would fail in exactly the case nobody
would think to check.

Scope
-----

Identity, not document management. Sources remain *references* to documents the
institution holds elsewhere; no document is stored, hashed or ingested here. That
boundary is set by ``DECISION-006`` and is deliberate: document storage brings
retention, tenancy and compliance obligations that this phase does not take on.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - import cycle guard only
    from applications.investment.workspace.cases import Case

# Versioning the hashed payload, so the scheme can change without a silent
# collision between digests computed under different rules.
MATERIAL_SCHEME = "yukti-material/1"


@dataclass(frozen=True)
class MaterialSnapshot:
    """One immutable state of a case's institutional material.

    Snapshots are append-only and are never rewritten. A judgment binds to the
    snapshot in force when it was produced, which is what lets a decision made
    months ago still name the material behind it.
    """

    snapshot_id: str
    material_digest: str
    version: int
    recorded_on: str
    case_id: str


def material_payload(case: Case) -> dict[str, Any]:
    """Return the institutional material, at full fidelity, in recorded order.

    Only the four things a judgment is formed from. Case metadata -- owner,
    thesis, requested decision, the date the case was opened -- is deliberately
    excluded: it never reaches the engine, and it must not change material
    identity either, or re-assigning a case would fabricate new material.
    """
    return {
        "scheme": MATERIAL_SCHEME,
        "sources": [asdict(source) for source in case.sources],
        "figures": [asdict(figure) for figure in case.figures],
        "assumptions": list(case.assumptions),
        "flagged_conflicts": [asdict(entry) for entry in case.flagged_conflicts],
    }


def compute_material_digest(case: Case) -> str:
    """Hash the institutional material a judgment would be formed from.

    Full fidelity: the recorded ``status`` and ``kind`` strings are hashed as
    written, not as the engine will later interpret them. That is the whole
    point -- this digest must distinguish material the engine cannot.
    """
    encoded = json.dumps(material_payload(case), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def next_snapshot(
    case: Case, material_digest: str, recorded_on: str
) -> MaterialSnapshot:
    """Build the snapshot that follows this case's existing registry."""
    version = len(case.snapshots) + 1
    return MaterialSnapshot(
        snapshot_id=f"MATERIAL-{version:03d}",
        material_digest=material_digest,
        version=version,
        recorded_on=recorded_on,
        case_id=case.case_id,
    )
