"""Tests for the V0.1 architecture freeze.

The freeze is a tripwire. These tests are what make it fire.

``TestFreezeIntact`` is the one that matters: if it fails, something in the
frozen architecture moved. That is not automatically wrong -- V0.2 is expected
to change things -- but it should be a deliberate act with a version bump
attached, not a surprise.
"""

from __future__ import annotations

import unittest

from choir_prototype.freeze import (
    FROZEN_MANIFEST,
    FROZEN_TREE_DIGEST,
    STATUS,
    VERSION,
    current_state,
    frozen_files,
    tree_digest,
    verify_freeze,
)


class TestFreezeIntact(unittest.TestCase):
    """Claim: the frozen architecture has not moved."""

    def test_tree_digest_matches_the_pin(self) -> None:
        """One value identifies the whole frozen state."""
        self.assertEqual(tree_digest(), FROZEN_TREE_DIGEST)

    def test_nothing_changed_added_or_removed(self) -> None:
        """Every pinned file is present and identical."""
        report = verify_freeze()
        self.assertTrue(
            report.intact,
            {
                "changed": report.changed,
                "added": report.added,
                "removed": report.removed,
            },
        )

    def test_every_file_is_pinned(self) -> None:
        """No file in the package escapes the freeze."""
        present = {item.path for item in current_state()}
        self.assertEqual(present, set(FROZEN_MANIFEST))


class TestFreezeMechanism(unittest.TestCase):
    """Claim: the freeze detects real changes and ignores cosmetic ones."""

    def test_python_modules_are_pinned_by_syntax_tree(self) -> None:
        """Formatting must not trip the freeze; code changes must."""
        python_states = [item for item in current_state() if item.path.endswith(".py")]
        self.assertTrue(python_states)
        for item in python_states:
            with self.subTest(path=item.path):
                self.assertEqual(item.kind, "ast")

    def test_non_python_files_are_pinned_by_content(self) -> None:
        """Documentation is pinned exactly, since it has no syntax tree."""
        others = [item for item in current_state() if not item.path.endswith(".py")]
        for item in others:
            with self.subTest(path=item.path):
                self.assertEqual(item.kind, "bytes")

    def test_caches_are_excluded(self) -> None:
        """Bytecode caches are not part of the architecture."""
        for path in frozen_files():
            with self.subTest(path=path.name):
                self.assertNotIn("__pycache__", path.parts)

    def test_tree_digest_is_sensitive_to_any_file(self) -> None:
        """Changing any single digest changes the tree digest."""
        states = current_state()
        baseline = tree_digest(states)
        for index in range(min(3, len(states))):
            mutated = list(states)
            original = mutated[index]
            mutated[index] = type(original)(
                path=original.path, digest="0" * 64, kind=original.kind
            )
            with self.subTest(path=original.path):
                self.assertNotEqual(tree_digest(tuple(mutated)), baseline)


class TestFreezeRecord(unittest.TestCase):
    """Claim: the freeze is documented, not just enforced."""

    def test_version_and_status_are_declared(self) -> None:
        """The package knows it is frozen and at what version."""
        self.assertEqual(VERSION, "0.1")
        self.assertEqual(STATUS, "FROZEN")

    def test_freeze_record_exists_and_names_the_limits(self) -> None:
        """FROZEN.md records what V0.1 did not establish, not only what it did."""
        from pathlib import Path

        record = Path(__file__).resolve().parents[1] / "FROZEN.md"
        self.assertTrue(record.is_file())
        text = record.read_text(encoding="utf-8")
        for expected in (
            "does **not** establish",
            "No defeat typing",
            "V0.2",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, text)


if __name__ == "__main__":
    unittest.main()
