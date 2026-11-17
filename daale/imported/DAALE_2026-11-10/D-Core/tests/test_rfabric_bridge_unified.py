"""The bridge against the unified kernel schema R-Fabric emits today.

``test_rfabric_bridge.py`` builds its trace with the older ``claim_analyses``
analyst shape. R-Fabric kernels now write one ``findings`` list instead, and a
bridge that only read the old shape translated every current trace into claims
that cited no evidence. These tests give it the shape it actually receives.
"""

from __future__ import annotations

import unittest

from daale import rfabric
from daale.execution import validate_package
from daale.tests.test_rfabric_bridge import sample_trace


def unified_trace():
    """sample_trace() with its analyst rewritten as unified ``findings``."""
    trace = sample_trace()
    legacy = trace["provisional_findings"]["analyst"]
    findings = []
    for analysis in legacy["claim_analyses"]:
        for relation in analysis["evidence_relations"]:
            findings.append(
                {
                    "finding_id": f"REL-{analysis['claim_id']}-{relation['evidence_id']}",
                    "finding_type": "EVIDENCE_RELATION",
                    "target_type": "CLAIM",
                    "target_id": analysis["claim_id"],
                    "evidence_ids": [relation["evidence_id"]],
                    "content": relation.get("rationale", "r"),
                    "relation": relation["relation"],
                    "severity": "LOW",
                    "confidence": 0.9,
                }
            )
        for text in analysis.get("uncertainties", []):
            findings.append(
                {
                    "finding_id": f"UNC-{analysis['claim_id']}",
                    "finding_type": "UNCERTAINTY",
                    "target_type": "CLAIM",
                    "target_id": analysis["claim_id"],
                    "evidence_ids": [],
                    "content": text,
                    "severity": "LOW",
                    "confidence": 0.5,
                }
            )
    for index, text in enumerate(legacy.get("assumptions", [])):
        findings.append(
            {
                "finding_id": f"ASM-{index}",
                "finding_type": "ASSUMPTION",
                "target_type": "GENERAL",
                "target_id": "GENERAL",
                "evidence_ids": [],
                "content": text,
                "severity": "LOW",
                "confidence": 0.5,
            }
        )
    trace["provisional_findings"]["analyst"] = {
        "case_id": legacy.get("case_id", trace["case"]["case_id"]),
        "kernel_id": "ANALYST",
        "findings": findings,
        "summary": "s",
        "uncertainties": [],
    }
    return trace


class TestUnifiedSchema(unittest.TestCase):
    def test_claims_cite_the_evidence_the_analyst_related_to_them(self) -> None:
        legacy = rfabric.build_choir_package(sample_trace())
        unified = rfabric.build_choir_package(unified_trace())

        def cites(package):
            return {c["id"]: sorted(c["cites"]) for c in package["claims"]}

        self.assertEqual(cites(unified), cites(legacy))
        self.assertTrue(any(cites(unified).values()), "no claim cites anything")

    def test_relationships_survive_the_translation(self) -> None:
        legacy = rfabric.build_choir_package(sample_trace())
        unified = rfabric.build_choir_package(unified_trace())
        key = lambda r: (r["source"], r["target"], r["relation"])  # noqa: E731
        self.assertEqual(
            sorted(map(key, unified["relationships"])),
            sorted(map(key, legacy["relationships"])),
        )

    def test_assumptions_and_uncertainty_are_carried(self) -> None:
        legacy = rfabric.build_choir_package(sample_trace())
        unified = rfabric.build_choir_package(unified_trace())
        self.assertEqual(unified["assumptions"], legacy["assumptions"])
        self.assertEqual(unified["uncertainty"], legacy["uncertainty"])

    def test_the_unified_package_is_admissible(self) -> None:
        result = validate_package(rfabric.build_choir_package(unified_trace()))
        self.assertTrue(result.valid, result.violations)


if __name__ == "__main__":
    unittest.main()
