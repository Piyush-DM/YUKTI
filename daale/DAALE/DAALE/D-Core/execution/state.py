"""The Reasoning State Store: versioned state, with one writer.

The v0 plan §6 gives the store six areas and one access rule: "The D-Core
receives canonical write authority; workers operate on immutable snapshots or
isolated working state." The critical invariant it states elsewhere is blunter
-- "R-Fabric can propose; D-Core alone can commit."

This module implements that rule as behaviour rather than as convention. A
canonical write requires an ``ExecutionLease``, the store issues no leases
itself, and a lease that does not match the open execution is refused. The
D-Core is the only component in this package that holds one.

Python cannot make a method genuinely unreachable, and pretending otherwise
would be theatre. What it can do is make an unauthorised write *fail loudly and
leave a record*, which is the property an audit actually needs.

The six areas
-------------

===================  =======================================================
Canonical objects    Current CHOIR-valid objects and their versions.
Provenance           Source lineage for every derived result.
Dependencies         Which objects depend on which earlier objects.
Execution events     Held by ``ExecutionTrace``; the store references it.
Candidate workspace  Non-canonical proposals awaiting validation.
Historical snapshots Prior canonical states, for timeline and replay.
===================  =======================================================

Versioning and staleness
------------------------

Every canonical object carries a version that increases on each commit. A
candidate declares the versions it read. If any of them has moved by the time
it reaches the gate, the candidate raced another writer and is stale -- it is
refused rather than silently overwriting. That is the "stale candidate commits"
risk the plan names, and the control it names for it.

Snapshots are immutable and append-only, following ``DECISION-004``: history is
never rewritten, so a snapshot taken during an execution stays readable
afterwards regardless of what the canonical state does next.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


class UnauthorizedWrite(RuntimeError):
    """A canonical write was attempted without a lease for the open execution."""


class StaleWrite(RuntimeError):
    """A canonical write was attempted against inputs that have since moved."""


@dataclass(frozen=True)
class ExecutionLease:
    """Canonical write authority for one execution.

    Issued by the D-Core and by nothing else. Holding one is what distinguishes
    a component that may commit from one that may only propose.
    """

    execution_id: str


@dataclass(frozen=True)
class CanonicalObject:
    """One committed object, at one version, with its lineage attached.

    Provenance travels with the object rather than in a side table, because the
    plan's acceptance criteria require every committed result to trace back to
    its inputs, and a lineage that can be dropped independently of the thing it
    describes will eventually be.
    """

    object_id: str
    version: int
    execution_id: str
    payload: Mapping[str, Any]
    provenance: tuple[str, ...]


@dataclass(frozen=True)
class Snapshot:
    """An immutable view of canonical state at one point in an execution."""

    snapshot_id: str
    execution_id: str
    objects: tuple[CanonicalObject, ...]


@dataclass
class ReasoningStateStore:
    """Versioned reasoning state. Readable by anyone, writable under lease."""

    _open_execution_id: str | None = None
    _canonical: dict[str, CanonicalObject] = field(default_factory=dict)
    _dependencies: dict[str, tuple[str, ...]] = field(default_factory=dict)
    _candidates: list[str] = field(default_factory=list)
    _snapshots: list[Snapshot] = field(default_factory=list)

    # -- lifecycle ---------------------------------------------------------

    def open_execution(self, execution_id: str) -> ExecutionLease:
        """Open an execution and return its lease.

        Called by the D-Core. Opening a second execution while one is open
        would allow two writers, which is the nondeterminism the plan's
        "canonical commit serialization" control exists to prevent.
        """
        if self._open_execution_id is not None:
            raise UnauthorizedWrite(
                f"execution {self._open_execution_id} is already open; "
                "canonical commits are serialised"
            )
        self._open_execution_id = execution_id
        return ExecutionLease(execution_id)

    def close_execution(self, lease: ExecutionLease) -> None:
        """Close the open execution. Further commits require a new lease."""
        self._require_authority(lease)
        self._open_execution_id = None

    # -- reads -------------------------------------------------------------

    def canonical(self, object_id: str) -> CanonicalObject | None:
        """Return the current canonical object, or None if there is not one."""
        return self._canonical.get(object_id)

    def current_version(self, object_id: str) -> int | None:
        """Return the current version of an object, or None if it is absent."""
        existing = self._canonical.get(object_id)
        return None if existing is None else existing.version

    def provenance_of(self, object_id: str) -> tuple[str, ...]:
        """Return the inputs a committed object was derived from."""
        existing = self._canonical.get(object_id)
        return () if existing is None else existing.provenance

    def dependents_of(self, object_id: str) -> tuple[str, ...]:
        """Return the objects that were derived from this one."""
        return self._dependencies.get(object_id, ())

    @property
    def candidates_seen(self) -> tuple[str, ...]:
        """Every candidate the workspace has been shown, in order."""
        return tuple(self._candidates)

    @property
    def snapshots(self) -> tuple[Snapshot, ...]:
        """Every snapshot taken, oldest first. Append-only."""
        return tuple(self._snapshots)

    # -- writes ------------------------------------------------------------

    def propose(self, candidate_id: str) -> None:
        """Record that a candidate entered the workspace. No lease required.

        Proposing is deliberately unprivileged: the whole point of the
        candidate protocol is that anything may propose and only the gate
        decides. Nothing here becomes canonical.
        """
        self._candidates.append(candidate_id)

    def commit(
        self,
        lease: ExecutionLease,
        object_id: str,
        payload: Mapping[str, Any],
        provenance: tuple[str, ...],
        read_versions: Mapping[str, int],
    ) -> CanonicalObject:
        """Commit one object to canonical state under lease.

        ``read_versions`` is what the writer believed when it computed the
        payload. If canonical state has moved underneath it, the write is
        refused rather than applied -- the optimistic-concurrency guard the
        plan names at the commit gate.
        """
        self._require_authority(lease)
        self._require_fresh(read_versions)

        existing = self._canonical.get(object_id)
        committed = CanonicalObject(
            object_id=object_id,
            version=1 if existing is None else existing.version + 1,
            execution_id=lease.execution_id,
            payload=dict(payload),
            provenance=provenance,
        )
        self._canonical[object_id] = committed

        for source in provenance:
            existing_dependents = self._dependencies.get(source, ())
            if object_id not in existing_dependents:
                self._dependencies[source] = existing_dependents + (object_id,)

        return committed

    def take_snapshot(self, lease: ExecutionLease) -> Snapshot:
        """Freeze current canonical state as an immutable historical snapshot."""
        self._require_authority(lease)
        snapshot = Snapshot(
            snapshot_id=f"SNAPSHOT-{len(self._snapshots) + 1:03d}",
            execution_id=lease.execution_id,
            objects=tuple(self._canonical[key] for key in sorted(self._canonical)),
        )
        self._snapshots.append(snapshot)
        return snapshot

    # -- guards ------------------------------------------------------------

    def _require_authority(self, lease: ExecutionLease) -> None:
        """Refuse any write that is not under the open execution's lease."""
        if self._open_execution_id is None:
            raise UnauthorizedWrite("no execution is open; nothing may commit")
        if lease.execution_id != self._open_execution_id:
            raise UnauthorizedWrite(
                f"lease for {lease.execution_id} does not match the open "
                f"execution {self._open_execution_id}"
            )

    def _require_fresh(self, read_versions: Mapping[str, int]) -> None:
        """Refuse a write whose inputs have moved since they were read."""
        for object_id, seen in read_versions.items():
            current = self.current_version(object_id)
            if current != seen:
                raise StaleWrite(
                    f"'{object_id}' was read at version {seen} but is now "
                    f"{'absent' if current is None else f'version {current}'}"
                )
