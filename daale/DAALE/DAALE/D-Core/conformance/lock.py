"""The conformance lock: resolve every cited commitment evidence, or fail.

Phase 0 of the DAALE execution plan is "map each frozen CHOIR commitment to
executable contract + test." ``commitments.py`` is the map. This module is what
makes it executable: it resolves every citation against the repository and
reports, per commitment, whether the evidence the freeze relies on actually
exists.

What it catches
---------------

A conformance lock is a tripwire, in the same sense ``FROZEN.md`` uses the word.
It does not re-run the reasoning -- ``--replay`` and the prototype's own suite
already do that, and duplicating them would create a second answer to the same
question. It catches the failure those checks cannot see: **a frozen commitment
whose evidence has quietly stopped existing.** Delete or rename
``TestKernelIndependence`` and every test still passes, ``--frozen`` still
reports INTACT, and commitment A3 silently loses the only thing that
demonstrated it. The lock fails.

It also makes the second failure visible without failing: a commitment the
freeze marks **demonstrated** while citing nothing. That is a hole in the
traceability chain rather than a broken link, so it is reported as a finding.

How resolution works, and why it reads rather than imports
----------------------------------------------------------

Evidence is resolved by parsing source files into syntax trees and collecting
declared names and string constants. Nothing is imported and nothing is
executed. That is deliberate on two counts:

* It is how the freeze itself works. ``freeze.py`` pins Python modules by
  normalised syntax tree rather than by bytes, so the mechanism is already
  idiomatic here.
* It keeps the lock free of any dependency on the engine, which is what allows
  it to be built while ``DECISION-005`` is open. Asserted by
  ``test_conformance_never_imports_the_engine``.

Determinism
-----------

No clock, no randomness, no dictionary-order dependence. Commitments are
reported in the order the freeze states them; resolved names are compared
against frozen sets. The same repository produces byte-identical output, which
is commitment X1 applied to the thing that checks X1.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from daale.conformance.commitments import (
    Commitment,
    Evidence,
    EvidenceKind,
    Status,
)

# The subject of conformance for v0.1: the only executable CHOIR in the tree.
# Named as a path, read as text, never imported.
SUBJECT_DIRECTORY = "choir_prototype"

# Where approved architecture decisions live.
DECISION_DIRECTORY = Path("docs") / "architecture"


class Outcome(Enum):
    """What the lock concluded about one commitment.

    ``UNEXERCISED`` is not a softer ``CONFORMING``. A commitment with no
    evidence has not been checked, and the report says so rather than letting
    an unchecked commitment read as a passing one.
    """

    CONFORMING = "conforming"
    UNEXERCISED = "unexercised"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True)
class EvidenceIndex:
    """Every name the repository declares, and every decision it has recorded.

    ``names`` holds declared classes and functions. ``literals`` holds string
    constants, which is where CLI flags and replay check names live.
    ``decisions`` maps a decision identifier to its recorded status line.
    """

    names: frozenset[str]
    literals: frozenset[str]
    decisions: dict[str, str]


@dataclass(frozen=True)
class EvidenceResult:
    """One citation, and whether it resolved."""

    evidence: Evidence
    resolved: bool
    detail: str


@dataclass(frozen=True)
class CommitmentResult:
    """One commitment, its outcome, and every citation behind it."""

    commitment: Commitment
    outcome: Outcome
    evidence: tuple[EvidenceResult, ...]

    @property
    def unsupported_claim(self) -> bool:
        """True when the freeze claims demonstration but cites nothing.

        A hole in the traceability chain rather than a broken link. Reported,
        not fatal -- the commitment may well be demonstrated somewhere that
        nobody wrote down, and asserting otherwise would overstate what the
        lock knows.
        """
        return (
            self.commitment.status is Status.DEMONSTRATED
            and self.outcome is Outcome.UNEXERCISED
        )


@dataclass(frozen=True)
class ConformanceReport:
    """The result of locking a commitment register against a repository."""

    results: tuple[CommitmentResult, ...]

    @property
    def unresolved(self) -> tuple[CommitmentResult, ...]:
        """Commitments citing evidence that no longer exists."""
        return tuple(r for r in self.results if r.outcome is Outcome.UNRESOLVED)

    @property
    def unexercised(self) -> tuple[CommitmentResult, ...]:
        """Commitments with no evidence cited at all."""
        return tuple(r for r in self.results if r.outcome is Outcome.UNEXERCISED)

    @property
    def conforming(self) -> tuple[CommitmentResult, ...]:
        """Commitments whose every citation resolved."""
        return tuple(r for r in self.results if r.outcome is Outcome.CONFORMING)

    @property
    def unsupported_claims(self) -> tuple[CommitmentResult, ...]:
        """Commitments marked demonstrated that cite nothing."""
        return tuple(r for r in self.results if r.unsupported_claim)

    @property
    def holds(self) -> bool:
        """The lock holds when no cited evidence has gone missing."""
        return not self.unresolved


def _collect_from_source(source: str, names: set[str], literals: set[str]) -> None:
    """Collect declared names and string constants from one parsed module."""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            literals.add(node.value)


# Typographic characters that reach this layer from Markdown decision notes.
# Normalised so the rendered artifact stays ASCII on every console that reads
# it. The research freeze §9 names this failure mode directly: an integrity
# mechanism that only works on the machine that produced it has not been
# institutionalised, and locale is one of the ways that happens.
_ASCII_SUBSTITUTIONS = {
    "‐": "-",
    "‑": "-",
    "‒": "-",
    "–": "-",
    "—": "-",
    "‘": "'",
    "’": "'",
    "“": '"',
    "”": '"',
    "…": "...",
    " ": " ",
}


def to_ascii(text: str) -> str:
    """Normalise recorded prose to ASCII by mechanical substitution.

    Total and reversible in meaning: only typographic variants are mapped to
    their ASCII equivalents, and anything still outside ASCII is dropped rather
    than guessed at. Nothing here changes what a status says.
    """
    for source, replacement in _ASCII_SUBSTITUTIONS.items():
        text = text.replace(source, replacement)
    return text.encode("ascii", "ignore").decode("ascii")


def _read_decisions(directory: Path) -> dict[str, str]:
    """Map each decision note to its recorded status line.

    The identifier comes from the filename, which is the stable part. The
    status is the first declared one, truncated at the end of its bold run --
    without that truncation the following sentence is swallowed too, and a note
    reading "Approved ... Recorded retrospectively" reports both as its status.
    A note with no status line resolves to an empty string and therefore never
    counts as approved.
    """
    decisions: dict[str, str] = {}
    if not directory.is_dir():
        return decisions

    for path in sorted(directory.glob("DECISION-*.md")):
        identifier = path.stem.split("_", 1)[0]
        status = ""
        for line in path.read_text(encoding="utf-8").splitlines():
            if "Status:" in line:
                declared = line.split("Status:", 1)[1]
                status = to_ascii(declared.split("**", 1)[0].strip())
                break
        decisions[identifier] = status

    return decisions


def build_evidence_index(root: Path) -> EvidenceIndex:
    """Index every name, literal and decision the repository declares.

    Reads source; imports nothing. A file that will not parse is skipped rather
    than raising, because an unparseable file elsewhere in the tree is not a
    conformance failure and should not masquerade as one.
    """
    names: set[str] = set()
    literals: set[str] = set()

    subject = root / SUBJECT_DIRECTORY
    for path in sorted(subject.rglob("*.py")):
        try:
            _collect_from_source(path.read_text(encoding="utf-8"), names, literals)
        except (OSError, SyntaxError, UnicodeDecodeError):
            continue

    return EvidenceIndex(
        names=frozenset(names),
        literals=frozenset(literals),
        decisions=_read_decisions(root / DECISION_DIRECTORY),
    )


def _resolve(evidence: Evidence, index: EvidenceIndex) -> EvidenceResult:
    """Resolve one citation against the index."""
    if evidence.kind is EvidenceKind.TEST:
        found = evidence.name in index.names
        detail = "declared in the subject" if found else "no such test declared"
        return EvidenceResult(evidence, found, detail)

    if evidence.kind is EvidenceKind.CHECK:
        found = evidence.name in index.literals
        detail = "named in the subject" if found else "no such check named"
        return EvidenceResult(evidence, found, detail)

    status = index.decisions.get(evidence.name)
    if status is None:
        return EvidenceResult(evidence, False, "no such decision note")
    if "Approved" not in status:
        return EvidenceResult(evidence, False, f"not approved ({status})")
    return EvidenceResult(evidence, True, status)


def evaluate(
    commitments: tuple[Commitment, ...], index: EvidenceIndex
) -> ConformanceReport:
    """Lock a commitment register against an indexed repository."""
    results: list[CommitmentResult] = []

    for commitment in commitments:
        resolved = tuple(_resolve(item, index) for item in commitment.evidence)

        if not resolved:
            outcome = Outcome.UNEXERCISED
        elif all(item.resolved for item in resolved):
            outcome = Outcome.CONFORMING
        else:
            outcome = Outcome.UNRESOLVED

        results.append(CommitmentResult(commitment, outcome, resolved))

    return ConformanceReport(tuple(results))


def lock(root: Path, commitments: tuple[Commitment, ...]) -> ConformanceReport:
    """Index the repository and evaluate the register against it."""
    return evaluate(commitments, build_evidence_index(root))
