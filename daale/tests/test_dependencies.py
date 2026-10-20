"""Tests for the Phase 3 dependency index.

The load-bearing test here is ``test_values_do_not_change_the_index``. The
index is authorised to exist while the evaluator boundary is held because it
reads *declared structure* and never *asserted content* -- and that claim is
worth an assertion rather than a docstring, because it is the whole reason this
module was allowed to be written.
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any

from daale.execution import build_index, validate_package

ROOT = Path(__file__).resolve().parents[2]


def package(**overrides: Any) -> dict[str, Any]:
    """A package whose references form a small chain and one fan-in.

    ev-001 -> clm-001 -> clm-002, and ev-002 also feeds clm-002, so a change to
    ev-001 reaches two claims and a change to ev-002 reaches one.
    """
    built: dict[str, Any] = {
        "choir_version": "0.1",
        "entities": [{"id": "ent-001", "label": "Orbital"}],
        "claims": [
            {"id": "clm-001", "cites": ["ev-001"], "about": "ent-001"},
            {"id": "clm-002", "cites": ["ev-002"], "supports": "clm-001"},
        ],
        "evidence": [
            {"id": "ev-001", "status": "reported", "value": 42},
            {"id": "ev-002", "status": "estimated", "value": 7},
        ],
        "assumptions": [{"id": "asm-001", "label": "market holds"}],
        "relationships": [{"source": "clm-001", "target": "ent-001"}],
        "uncertainty": {"clm-001": "likely"},
        "metadata": {"packet": "sample"},
    }
    built.update(overrides)
    return built


class TestStructureOnly(unittest.TestCase):
    """The index reads what points where, never what anything says."""

    def test_values_do_not_change_the_index(self) -> None:
        """The authorisation for this module, as an assertion.

        Two packages differing in every value, status, label and free-text
        field -- and in no reference -- must produce identical indexes. If this
        ever fails, the index has started reading content, and content is where
        the evaluator question lives.
        """
        original = build_index(package())
        restated = build_index(
            package(
                entities=[{"id": "ent-001", "label": "COMPLETELY DIFFERENT"}],
                evidence=[
                    {"id": "ev-001", "status": "estimated", "value": -99999},
                    {"id": "ev-002", "status": "asserted", "value": 0},
                ],
                uncertainty={"clm-001": "unlikely"},
                metadata={"packet": "other", "note": "unrelated"},
            )
        )
        self.assertEqual(original._depends_on, restated._depends_on)
        self.assertEqual(original._dependents, restated._dependents)
        self.assertEqual(original.declared, restated.declared)

    def test_a_changed_reference_does_change_the_index(self) -> None:
        """The control. Without it the test above passes on a dead index."""
        moved = package(claims=[{"id": "clm-001", "cites": ["ev-002"]}])
        self.assertNotEqual(
            build_index(package())._depends_on, build_index(moved)._depends_on
        )


class TestEdges(unittest.TestCase):
    """Direct structure, in both directions."""

    def setUp(self) -> None:
        self.index = build_index(package())

    def test_an_object_points_at_what_it_cites(self) -> None:
        self.assertEqual(self.index.depends_on("clm-001"), ("ent-001", "ev-001"))

    def test_the_reverse_relation_is_built(self) -> None:
        self.assertEqual(self.index.dependents_of("ev-001"), ("clm-001",))

    def test_an_unreferenced_object_has_no_dependents(self) -> None:
        self.assertEqual(self.index.dependents_of("asm-001"), ())

    def test_a_relationship_without_an_id_still_creates_an_edge(self) -> None:
        """Relationships carry source and target but no id of their own.

        Dropping them would silently shorten every cone that runs through a
        relationship.
        """
        self.assertIn("ent-001", self.index.depends_on("clm-001"))


class TestAffectedCone(unittest.TestCase):
    """What a change reaches. The plan's §11 mechanism."""

    def setUp(self) -> None:
        self.index = build_index(package())

    def test_the_cone_is_transitive(self) -> None:
        """ev-001 feeds clm-001, which clm-002 supports."""
        self.assertEqual(self.index.affected_cone("ev-001"), ("clm-001", "clm-002"))

    def test_the_cone_excludes_the_changed_object(self) -> None:
        """It is the input to a recomputation, not an output of one."""
        self.assertNotIn("ev-001", self.index.affected_cone("ev-001"))

    def test_a_leaf_change_reaches_nothing(self) -> None:
        self.assertEqual(self.index.affected_cone("clm-002"), ())

    def test_an_unknown_object_reaches_nothing(self) -> None:
        self.assertEqual(self.index.affected_cone("ev-404"), ())

    def test_cone_size_matches_the_cone(self) -> None:
        self.assertEqual(
            self.index.cone_size("ev-001"), len(self.index.affected_cone("ev-001"))
        )

    def test_narrower_evidence_has_a_smaller_cone(self) -> None:
        """The whole point: not every change costs the same to absorb."""
        self.assertGreater(
            self.index.cone_size("ev-001"), self.index.cone_size("ev-002")
        )


class TestIntegrity(unittest.TestCase):
    """Malformed structure is reported, never absorbed and never fatal."""

    def test_a_cycle_terminates_and_is_reported(self) -> None:
        """Circular justification is a finding about the material."""
        looped = package(
            claims=[
                {"id": "clm-001", "cites": ["clm-002"]},
                {"id": "clm-002", "cites": ["clm-001"]},
            ]
        )
        index = build_index(looped)
        self.assertEqual(index.cycles(), ("clm-001", "clm-002"))
        self.assertIn("clm-002", index.affected_cone("clm-001"))

    def test_a_well_formed_package_has_no_cycles(self) -> None:
        self.assertEqual(build_index(package()).cycles(), ())

    def test_a_dangling_reference_is_recorded_not_dropped(self) -> None:
        """The contract gate refuses these; the index still shows the edge.

        Dropping it would understate every cone that runs through it.
        """
        dangling = package(claims=[{"id": "clm-001", "cites": ["ev-404"]}])
        index = build_index(dangling)
        self.assertEqual(index.unknown_references(), (("clm-001", "ev-404"),))
        self.assertIn("clm-001", index.dependents_of("ev-404"))

    def test_a_valid_package_has_no_unknown_references(self) -> None:
        """Consistency with the contract gate, checked rather than assumed."""
        self.assertTrue(validate_package(package()).valid)
        self.assertEqual(build_index(package()).unknown_references(), ())

    def test_an_empty_package_is_an_empty_index(self) -> None:
        index = build_index({})
        self.assertEqual(index.objects, ())
        self.assertEqual(index.cycles(), ())


class TestDeterminism(unittest.TestCase):
    """Commitment X1, applied to the index."""

    def test_the_same_package_builds_the_same_index(self) -> None:
        first, second = build_index(package()), build_index(package())
        self.assertEqual(first._depends_on, second._depends_on)
        self.assertEqual(first._dependents, second._dependents)

    def test_every_result_is_sorted(self) -> None:
        index = build_index(package())
        for object_id in index.objects:
            with self.subTest(object_id=object_id):
                self.assertEqual(
                    list(index.depends_on(object_id)),
                    sorted(index.depends_on(object_id)),
                )
                self.assertEqual(
                    list(index.affected_cone(object_id)),
                    sorted(index.affected_cone(object_id)),
                )

    def test_key_order_in_the_package_does_not_matter(self) -> None:
        """Dictionary insertion order is not part of what was recorded."""
        reordered = dict(reversed(list(package().items())))
        self.assertEqual(
            build_index(package())._depends_on, build_index(reordered)._depends_on
        )


class TestBoundary(unittest.TestCase):
    """The index is structure only, and imports no engine."""

    def test_dependencies_never_imports_the_engine(self) -> None:
        probe = (
            "import sys\n"
            "from daale.execution import build_index\n"
            "build_index({'claims': [{'id': 'c', 'cites': ['e']}]})\n"
            "roots = {'choir_prototype', 'applications'}\n"
            "leaked = sorted(m for m in sys.modules if m.split('.')[0] in roots)\n"
            "print(','.join(leaked))\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", probe],
            capture_output=True,
            text=True,
            cwd=ROOT,
            check=True,
        )
        self.assertEqual(result.stdout.strip(), "")

    def test_the_index_exposes_no_evaluator(self) -> None:
        """The same guard the D-Core carries, for the same reason.

        The evaluator boundary is held by ruling while DECISION-005 has no
        replacement. An index that grew a way to evaluate would settle that by
        implication.
        """
        forbidden = {"evaluate", "reason", "adjudicate", "synthesise", "synthesize"}
        from daale.execution.dependencies import DependencyIndex

        present = forbidden.intersection(dir(DependencyIndex))
        self.assertEqual(present, set(), f"index grew an evaluator: {present}")


if __name__ == "__main__":
    unittest.main()


class TestRealIrShape(unittest.TestCase):
    """The gap between this index and the IR the frozen engine actually emits.

    These assertions pin behaviour that is **wrong**, so that the gap is
    visible in the suite and closing it has to be deliberate. Same treatment
    the unexercised commitments and E12 already get: a defect nobody can see is
    a defect nobody fixes.

    Shape transcribed from
    ``reports/vertical-slice/orbital-series-b/03-ir.json``. Inlined rather than
    read from disk because ``reports/`` is generated output and is not
    committed.
    """

    def real_ir(self) -> dict[str, Any]:
        """One claim, its evidence, its subject, and the relationship between."""
        return {
            "entities": [{"id": "ent-company", "kind": "company", "label": "Orbital"}],
            "claims": [
                {
                    "id": "clm-001",
                    "evidence_ids": ["SRC-AUDIT-FY24"],
                    "subject_id": "ent-company",
                    "predicate": "arr_usd",
                    "uncertainty": "settled",
                    "value": "18000000",
                }
            ],
            "evidence": [
                {
                    "id": "SRC-AUDIT-FY24",
                    "quality": "audited",
                    "source": "Independent audit of FY2024 statements",
                }
            ],
            "assumptions": [{"id": "asm-001", "statement": "Scope covers all subs."}],
            "relationships": [
                {
                    "id": "rel-001",
                    "kind": "supports",
                    "source_id": "SRC-AUDIT-FY24",
                    "target_id": "clm-001",
                }
            ],
            "metadata": {"packet_id": "ORBITAL_SERIES_B"},
        }

    def test_real_references_are_not_seen(self) -> None:
        """evidence_ids, subject_id, source_id and target_id are all missed."""
        index = build_index(self.real_ir())
        self.assertEqual(index.depends_on("clm-001"), ())
        self.assertEqual(index.dependents_of("SRC-AUDIT-FY24"), ())
        self.assertEqual(index.affected_cone("SRC-AUDIT-FY24"), ())

    def test_an_evidence_label_is_misread_as_a_reference(self) -> None:
        """`source` on real evidence is prose, and is invented as an edge."""
        index = build_index(self.real_ir())
        self.assertEqual(
            index.unknown_references(),
            (("SRC-AUDIT-FY24", "Independent audit of FY2024 statements"),),
        )

    def test_real_ir_does_not_pass_the_v0_contract_gate(self) -> None:
        """The finding that matters, and it is not this module's to fix.

        The engine's own output is inadmissible to its own contract gate: no
        `choir_version`, no top-level `uncertainty` section (it is a field on
        each claim), and the misread label above.
        """
        result = validate_package(self.real_ir())
        self.assertFalse(result.valid)
        codes = {violation.code for violation in result.violations}
        self.assertIn("missing-choir-version", codes)
        self.assertIn("missing-section", codes)
        self.assertIn("dangling-reference", codes)
