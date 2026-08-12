"""CHOIR contract validation: is this package admissible at all?

The first responsibility the v0 plan gives the D-Core is "CHOIR version and
contract validation". This module is that gate, and nothing more. It answers a
structural question -- does this package have the shape CHOIR commits to -- and
never an interpretive one.

What the contract is
--------------------

Commitment **A2**, transcribed: "The IR shape: entities, claims, evidence,
assumptions, relationships, uncertainty, metadata." That list is frozen, so it
is the contract, and it is stated here in exactly those terms. The register in
``daale/conformance/commitments.py`` holds the same statement, and
``test_the_contract_sections_match_commitment_a2`` keeps the two from drifting
apart.

Two further checks follow from commitments rather than from taste:

* **Identifier uniqueness.** Two objects sharing an identifier make every
  downstream citation ambiguous.
* **Referential integrity.** Commitment **X4** -- "kernels cite only
  identifiers present in the IR" -- is unenforceable if the IR itself cites
  identifiers that are not in it. Checking it at the input boundary is the
  same property applied one step earlier.

What this is not
----------------

It is not semantic validation, and it does not evaluate anything. A package can
pass this gate and still be reasoning nobody should act on; that judgement
belongs to CHOIR, and reaching it requires the evaluator this phase does not
have. Violations are returned as data rather than raised, because a caller
usually wants all of them at once and a trace wants to record each.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

# Commitment A2, verbatim in content and order.
IR_SECTIONS: tuple[str, ...] = (
    "entities",
    "claims",
    "evidence",
    "assumptions",
    "relationships",
    "uncertainty",
    "metadata",
)

# Sections whose entries carry identifiers other objects may cite.
IDENTIFIED_SECTIONS: tuple[str, ...] = (
    "entities",
    "claims",
    "evidence",
    "assumptions",
)

# Fields by which one object refers to another. Checked wherever they appear.
REFERENCE_FIELDS: tuple[str, ...] = ("cites", "source", "target", "supports", "about")

MISSING_SECTION = "missing-section"
MISSING_VERSION = "missing-choir-version"
DUPLICATE_IDENTIFIER = "duplicate-identifier"
DANGLING_REFERENCE = "dangling-reference"
MALFORMED_SECTION = "malformed-section"


@dataclass(frozen=True)
class ContractViolation:
    """One reason a package is not admissible."""

    code: str
    subject: str
    detail: str


@dataclass(frozen=True)
class ContractResult:
    """The outcome of validating one package against the CHOIR contract."""

    violations: tuple[ContractViolation, ...]

    @property
    def valid(self) -> bool:
        """A package is admissible only when nothing is wrong with it."""
        return not self.violations


def _entries(section: Any) -> Sequence[Any]:
    """Return a section's entries, or an empty sequence if it is not a list."""
    return section if isinstance(section, list) else ()


def _collect_identifiers(
    package: Mapping[str, Any], violations: list[ContractViolation]
) -> set[str]:
    """Gather every declared identifier, reporting any declared twice."""
    seen: set[str] = set()
    for name in IDENTIFIED_SECTIONS:
        for entry in _entries(package.get(name)):
            if not isinstance(entry, dict):
                continue
            identifier = entry.get("id")
            if not isinstance(identifier, str):
                continue
            if identifier in seen:
                violations.append(
                    ContractViolation(
                        DUPLICATE_IDENTIFIER,
                        identifier,
                        f"declared more than once; second occurrence in '{name}'",
                    )
                )
            seen.add(identifier)
    return seen


def _check_references(
    package: Mapping[str, Any],
    declared: set[str],
    violations: list[ContractViolation],
) -> None:
    """Report any reference to an identifier the package does not declare."""
    for name in IR_SECTIONS:
        for entry in _entries(package.get(name)):
            if not isinstance(entry, dict):
                continue
            subject = entry.get("id")
            subject_name = subject if isinstance(subject, str) else f"<{name} entry>"
            for field_name in REFERENCE_FIELDS:
                value = entry.get(field_name)
                targets = value if isinstance(value, list) else [value]
                for target in targets:
                    if isinstance(target, str) and target not in declared:
                        violations.append(
                            ContractViolation(
                                DANGLING_REFERENCE,
                                subject_name,
                                f"'{field_name}' cites '{target}', "
                                "which the package does not declare",
                            )
                        )


def validate_package(package: Mapping[str, Any]) -> ContractResult:
    """Validate a CHOIR package against the frozen A2 shape.

    Structural only. Every violation is reported rather than the first one
    raising, because a caller fixing a package wants the whole list.
    """
    violations: list[ContractViolation] = []

    version = package.get("choir_version")
    if not isinstance(version, str) or not version.strip():
        violations.append(
            ContractViolation(
                MISSING_VERSION,
                "package",
                "no 'choir_version' declared; the contract cannot be selected",
            )
        )

    for name in IR_SECTIONS:
        if name not in package:
            violations.append(
                ContractViolation(MISSING_SECTION, name, "required by commitment A2")
            )
        elif name in IDENTIFIED_SECTIONS and not isinstance(package[name], list):
            violations.append(
                ContractViolation(
                    MALFORMED_SECTION,
                    name,
                    f"expected a list of objects, found {type(package[name]).__name__}",
                )
            )

    declared = _collect_identifiers(package, violations)
    _check_references(package, declared, violations)

    return ContractResult(tuple(violations))
