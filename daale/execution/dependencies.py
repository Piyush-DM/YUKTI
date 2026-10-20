"""The dependency index: what rests on what, and what a change reaches.

Half of Phase 3 of the v0 plan. The plan pairs a dependency index with an
execution planner; the planner is blocked and this is not.

Why this half is not blocked
----------------------------

``DECISION-005`` is invalidated as a governing decision, but no replacement has
been recorded, so the evaluator boundary stands: DAALE still does not decide
whether it evaluates for itself or calls the frozen kernels.

This module needs neither answer. Dependencies in a CHOIR package are
*declared*, not derived -- a claim names the evidence it cites, a relationship
names its source and target. Reading that structure is not evaluating it. The
index never looks at what an object asserts, only at what it points to, and
``test_values_do_not_change_the_index`` proves that mechanically: two packages
differing in every value but in no reference produce identical indexes.

What it is for
--------------

The plan's §11, incremental recomputation: "recomputing only the dependency
cone affected by a changed evidence object". Change one evidence object, and
the cone is what has to be looked at again. Everything outside it provably
cannot have moved, which is what makes an incremental re-run sound rather than
merely faster.

Known limitation -- the reference vocabulary is not the real one
---------------------------------------------------------------

This index reads ``REFERENCE_FIELDS`` from ``contract.py``, and those field
names do not match the intermediate representation the frozen engine actually
emits. Measured against ``reports/vertical-slice/orbital-series-b/03-ir.json``:

* real claims reference by ``evidence_ids`` and ``subject_id``;
* real relationships reference by ``source_id`` and ``target_id``;
* ``source`` on a real evidence object is a human-readable label, not an
  identifier, so reading it as a reference invents five edges that do not
  exist.

The result on real IR is a graph of 10 nodes over 24 declared objects, none of
whose edges are real. The traversal is correct; the vocabulary it traverses is
not.

**Deliberately not fixed here.** The fix belongs in ``contract.py``, which is
committed DAALE v0 code covered by the closure freeze, and correcting it
changes admissibility for every package -- including whether the frozen
engine's own output is admissible at all. That is a ruling, not a patch.

``TestRealIrShape`` pins the current behaviour so the gap stays visible and
closing it is a deliberate act. Finding:
``temp_dump/implementation/blocked/2026-08-22_ir_contract_vocabulary_mismatch.md``

Two graphs, deliberately distinct
---------------------------------

``ReasoningStateStore.dependents_of`` answers a *runtime lineage* question:
which committed objects were derived from this one, recorded as commits
happened. This module answers a *static structure* question: which declared
objects reference this one, read off a package before anything runs.

They are not the same graph and neither substitutes for the other. The parallel
method names are deliberate -- it is the same idea over different subjects --
but a caller must know which subject it is holding.

Determinism
-----------

Commitment X1. Every returned sequence is sorted and the stored maps are built
in sorted order, so no result depends on dictionary insertion. A package with a
reference cycle terminates rather than hanging, and the cycle is reported
rather than silently tolerated: circular justification is a fact about the
material worth surfacing, not a traversal detail to absorb.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from daale.execution.contract import (
    IDENTIFIED_SECTIONS,
    IR_SECTIONS,
    REFERENCE_FIELDS,
)


def _entries(section: Any) -> list[Any]:
    """Return a section's entries, or nothing if it is not a list."""
    return section if isinstance(section, list) else []


def _references(entry: Mapping[str, Any]) -> list[str]:
    """Every identifier one entry points at, in declared field order."""
    found: list[str] = []
    for field_name in REFERENCE_FIELDS:
        value = entry.get(field_name)
        for target in value if isinstance(value, list) else [value]:
            if isinstance(target, str) and target and target not in found:
                found.append(target)
    return found


@dataclass(frozen=True)
class DependencyIndex:
    """Which declared objects rest on which, for one package.

    ``_depends_on`` maps an object to what it points at. ``_dependents`` is
    that relation reversed, built once at construction because the interesting
    question -- what does a change reach -- is always asked in the reverse
    direction.
    """

    declared: frozenset[str]
    _depends_on: dict[str, tuple[str, ...]] = field(default_factory=dict)
    _dependents: dict[str, tuple[str, ...]] = field(default_factory=dict)

    # -- direct edges ------------------------------------------------------

    def depends_on(self, object_id: str) -> tuple[str, ...]:
        """What this object points at directly."""
        return self._depends_on.get(object_id, ())

    def dependents_of(self, object_id: str) -> tuple[str, ...]:
        """What points at this object directly."""
        return self._dependents.get(object_id, ())

    @property
    def objects(self) -> tuple[str, ...]:
        """Every identifier the graph touches, declared or merely referenced."""
        return tuple(sorted(set(self._depends_on) | set(self._dependents)))

    # -- reachability ------------------------------------------------------

    def _reachable(self, object_id: str) -> set[str]:
        """Everything downstream of an object, self included if it is cyclic.

        Self is not seeded into ``seen``, so an object that can reach itself
        ends up in the result. That is what makes cycle detection possible;
        ``affected_cone`` removes it afterwards for its own purposes.
        """
        seen: set[str] = set()
        frontier = [object_id]
        while frontier:
            current = frontier.pop()
            for dependent in self._dependents.get(current, ()):
                if dependent not in seen:
                    seen.add(dependent)
                    frontier.append(dependent)
        return seen

    def affected_cone(self, object_id: str) -> tuple[str, ...]:
        """Everything that would have to be looked at again if this changed.

        Transitive dependents, sorted. The object itself is **excluded**: it is
        the input to a recomputation, not an output of one, and including it
        would make the cone read as "what changed" rather than "what must now
        be rechecked".
        """
        return tuple(sorted(self._reachable(object_id) - {object_id}))

    def cone_size(self, object_id: str) -> int:
        """How far a change to this object reaches. The plan's §12 signal."""
        return len(self.affected_cone(object_id))

    # -- integrity ---------------------------------------------------------

    def unknown_references(self) -> tuple[tuple[str, str], ...]:
        """Every (source, target) pair whose target the package never declares.

        ``contract.validate_package`` reports these as violations and refuses
        the package. The index records them anyway rather than assuming a
        validated input: it is also useful on a package that has not been
        through the gate, and dropping the edge silently would understate every
        cone that runs through it.
        """
        dangling: list[tuple[str, str]] = []
        for source in sorted(self._depends_on):
            for target in self._depends_on[source]:
                if target not in self.declared:
                    dangling.append((source, target))
        return tuple(dangling)

    def cycles(self) -> tuple[str, ...]:
        """Identifiers that lie on a dependency cycle, sorted.

        An object reachable from itself. Reported rather than absorbed: in a
        reasoning package that is circular justification, which is a finding
        about the material rather than a quirk of the traversal.
        """
        return tuple(
            sorted(
                object_id
                for object_id in self.objects
                if object_id in self._reachable(object_id)
            )
        )


def build_index(package: Mapping[str, Any]) -> DependencyIndex:
    """Read declared structure off a package. Evaluates nothing."""
    declared: set[str] = set()
    for name in IDENTIFIED_SECTIONS:
        for entry in _entries(package.get(name)):
            if isinstance(entry, dict) and isinstance(entry.get("id"), str):
                declared.add(entry["id"])

    depends_on: dict[str, list[str]] = {}
    for name in IR_SECTIONS:
        for entry in _entries(package.get(name)):
            if not isinstance(entry, dict):
                continue
            targets = _references(entry)
            if not targets:
                continue
            # An entry with no id of its own -- a relationship, typically --
            # still creates an edge between the things it names, so its
            # references are attributed to the first one rather than dropped.
            identifier = entry.get("id")
            origin = identifier if isinstance(identifier, str) else targets[0]
            bucket = depends_on.setdefault(origin, [])
            for target in targets:
                if target != origin and target not in bucket:
                    bucket.append(target)

    dependents: dict[str, list[str]] = {}
    for source in sorted(depends_on):
        for target in sorted(depends_on[source]):
            dependents.setdefault(target, []).append(source)

    return DependencyIndex(
        declared=frozenset(declared),
        _depends_on={
            key: tuple(sorted(value)) for key, value in sorted(depends_on.items())
        },
        _dependents={
            key: tuple(sorted(value)) for key, value in sorted(dependents.items())
        },
    )
