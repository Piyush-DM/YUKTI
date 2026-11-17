"""Smoke tests for the DAALE ontology scaffold.

These tests protect repository stability without defining ontology behavior.
They verify that existing ontology module boundaries remain importable and
documented while implementation awaits approved specifications.
"""

import importlib
import unittest


ONTOLOGY_MODULES = (
    "daale.ontology",
    "daale.ontology.base",
    "daale.ontology.confidence",
    "daale.ontology.contradiction",
    "daale.ontology.decision",
    "daale.ontology.evidence",
    "daale.ontology.proposal",
    "daale.ontology.relationships",
)


class OntologyScaffoldTests(unittest.TestCase):
    """Stability checks for current DAALE ontology module boundaries."""

    def test_ontology_modules_are_importable(self) -> None:
        """Existing ontology scaffold modules should import cleanly."""
        for module_name in ONTOLOGY_MODULES:
            with self.subTest(module_name=module_name):
                module = importlib.import_module(module_name)
                self.assertIsNotNone(module)

    def test_ontology_modules_are_documented(self) -> None:
        """Existing ontology scaffold modules should explain their status."""
        for module_name in ONTOLOGY_MODULES:
            with self.subTest(module_name=module_name):
                module = importlib.import_module(module_name)
                self.assertTrue((module.__doc__ or "").strip())


if __name__ == "__main__":
    unittest.main()
