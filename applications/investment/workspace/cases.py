"""Cases: the institution's unit of work, and where it is kept.

A case is one decision the institution has to make. It accumulates the material
a committee needs — a source register, a diligence schedule, stated assumptions,
and conflicts the team has flagged — and it keeps the judgments and decisions
made against that material.

Storage is one JSON file per case under ``reports/workspace/<case-id>/``, beside
the engine artifacts for that case's analyses. There is no database: the
material is small, the file is readable by a human without tooling, and the
`reports/` tree is already established as generated output that is not
committed. A store that can be inspected with a text editor is worth more here
than one that scales.

Case identifiers are slugs derived from the company name, so a directory listing
is legible and a URL says what it points at. They are assigned deterministically
— same company, same empty store, same id — and never reused.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, replace
from datetime import date
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_STORE_ROOT = REPOSITORY_ROOT / "reports" / "workspace"

CASE_FILE = "case.json"

# What the institution has done with the case so far. Status is derived from
# the record rather than set by hand, so it cannot drift from reality.
STATUS_DRAFT = "Draft"
STATUS_MATERIAL_ASSEMBLED = "Material assembled"
STATUS_ANALYSED = "Analysed"
STATUS_DECIDED = "Decided"


@dataclass(frozen=True)
class Source:
    """One document in the case's source register."""

    label: str
    origin: str
    kind: str


@dataclass(frozen=True)
class Figure:
    """One recorded figure from the diligence schedule, and what backs it."""

    metric: str
    value: str
    status: str
    source_labels: tuple[str, ...]


@dataclass(frozen=True)
class FlaggedConflict:
    """A conflict the diligence team found between the case's own sources."""

    metric: str
    note: str


@dataclass(frozen=True)
class LedgerEntry:
    """One decision the institution recorded against an analysis.

    The judgment is what the analysis concluded; the decision is what the
    institution chose to do about it. They are stored separately and on purpose:
    a committee that overrides a recommendation is the most important thing the
    ledger can record, and collapsing the two would erase it.
    """

    entry_id: str
    decision: str
    decided_by: str
    rationale: str
    recorded_on: str
    judgment_recommendation: str
    judgment_confidence: str
    record_digest: str


@dataclass(frozen=True)
class Case:
    """One institutional decision, with everything assembled against it."""

    case_id: str
    company: str
    sector: str
    stage: str
    requested_decision: str
    thesis: str
    owner: str
    opened_on: str
    sources: tuple[Source, ...] = ()
    figures: tuple[Figure, ...] = ()
    assumptions: tuple[str, ...] = ()
    flagged_conflicts: tuple[FlaggedConflict, ...] = ()
    ledger: tuple[LedgerEntry, ...] = ()

    @property
    def title(self) -> str:
        """How the case is named everywhere it is listed."""
        return f"{self.company} -- {self.stage}"

    def recorded_metrics(self) -> frozenset[str]:
        """Which schedule metrics this case has a figure for."""
        return frozenset(figure.metric for figure in self.figures)

    def has_material(self) -> bool:
        """True once there is something to analyse."""
        return bool(self.sources) and bool(self.figures)

    def status(self, analysed: bool) -> str:
        """Derive the case status from the record.

        ``analysed`` is passed in rather than stored, because whether an
        analysis exists is a fact about the artifacts on disk and duplicating it
        onto the case would create a second answer that can go stale.
        """
        if self.ledger:
            return STATUS_DECIDED
        if analysed:
            return STATUS_ANALYSED
        if self.has_material():
            return STATUS_MATERIAL_ASSEMBLED
        return STATUS_DRAFT


class CaseStore:
    """Reads and writes cases as JSON files under one root directory."""

    def __init__(self, root: Path = DEFAULT_STORE_ROOT) -> None:
        self.root = root

    def directory(self, case_id: str) -> Path:
        """Return the directory holding one case and its analysis artifacts."""
        return self.root / case_id

    def exists(self, case_id: str) -> bool:
        """True when a case with this id has been written."""
        return (self.directory(case_id) / CASE_FILE).is_file()

    def list_ids(self) -> tuple[str, ...]:
        """Every case id, sorted, so listings do not depend on filesystem order."""
        if not self.root.is_dir():
            return ()
        return tuple(
            sorted(
                path.name
                for path in self.root.iterdir()
                if (path / CASE_FILE).is_file()
            )
        )

    def load(self, case_id: str) -> Case:
        """Read one case. Raises ``KeyError`` if it does not exist."""
        path = self.directory(case_id) / CASE_FILE
        if not path.is_file():
            raise KeyError(case_id)
        return _case_from_dict(json.loads(path.read_text(encoding="utf-8")))

    def load_all(self) -> tuple[Case, ...]:
        """Every case, in id order."""
        return tuple(self.load(case_id) for case_id in self.list_ids())

    def save(self, case: Case) -> Case:
        """Write one case, creating its directory if needed."""
        directory = self.directory(case.case_id)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / CASE_FILE).write_text(
            json.dumps(asdict(case), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        return case

    def open_case(
        self,
        company: str,
        sector: str,
        stage: str,
        requested_decision: str,
        thesis: str,
        owner: str,
        opened_on: str | None = None,
    ) -> Case:
        """Open a new case and write it.

        ``opened_on`` is the only value here that comes from outside the
        request. It is institutional metadata and never reaches the reasoning
        engine, so it cannot affect what a case concludes.
        """
        company = _required(company, "Company")
        case = Case(
            case_id=self._allocate_id(company),
            company=company,
            sector=_required(sector, "Sector"),
            stage=_required(stage, "Stage"),
            requested_decision=_required(requested_decision, "Requested decision"),
            thesis=thesis.strip(),
            owner=_required(owner, "Owner"),
            opened_on=opened_on or date.today().isoformat(),
        )
        return self.save(case)

    def record_material(
        self,
        case_id: str,
        sources: tuple[Source, ...],
        figures: tuple[Figure, ...],
        assumptions: tuple[str, ...],
        flagged_conflicts: tuple[FlaggedConflict, ...],
    ) -> Case:
        """Replace the case material wholesale.

        Whole-record replacement rather than per-item editing: the diligence
        pack is assembled and then submitted, and a half-applied set of figures
        is not a state the institution should be able to reach.
        """
        case = self.load(case_id)
        _validate_material(sources, figures)
        return self.save(
            replace(
                case,
                sources=sources,
                figures=figures,
                assumptions=assumptions,
                flagged_conflicts=flagged_conflicts,
            )
        )

    def append_ledger_entry(self, case_id: str, entry: LedgerEntry) -> Case:
        """Add a decision to the case's ledger. Entries are never removed."""
        case = self.load(case_id)
        return self.save(replace(case, ledger=case.ledger + (entry,)))

    def _allocate_id(self, company: str) -> str:
        """Derive an unused slug from the company name."""
        base = _slug(company) or "case"
        if not self.exists(base):
            return base
        suffix = 2
        while self.exists(f"{base}-{suffix}"):
            suffix += 1
        return f"{base}-{suffix}"


def _slug(text: str) -> str:
    """Reduce text to a lowercase, hyphen-separated identifier."""
    lowered = re.sub(r"[^a-z0-9]+", "-", text.lower())
    return lowered.strip("-")


def _required(value: str, field_name: str) -> str:
    """Return a trimmed required field, or fail naming it as the user sees it."""
    trimmed = value.strip()
    if not trimmed:
        raise ValueError(f"{field_name} is required.")
    return trimmed


def _validate_material(
    sources: tuple[Source, ...], figures: tuple[Figure, ...]
) -> None:
    """Reject material the institution could not defend.

    Only two rules, both institutional rather than technical: a source register
    cannot list the same document twice under one label, and a figure cannot
    cite a source the register does not contain. The second is the important
    one -- an uncitable figure is exactly the thing an audit trail exists to
    prevent.
    """
    labels: set[str] = set()
    for source in sources:
        if not source.label.strip():
            raise ValueError("Every source needs a reference label.")
        if source.label in labels:
            raise ValueError(f"Source label '{source.label}' is used twice.")
        labels.add(source.label)

    for figure in figures:
        if not figure.value.strip():
            raise ValueError(f"Figure '{figure.metric}' has no value.")
        if not figure.source_labels:
            raise ValueError(f"Figure '{figure.metric}' cites no source.")
        for label in figure.source_labels:
            if label not in labels:
                raise ValueError(
                    f"Figure '{figure.metric}' cites source '{label}', "
                    "which is not in the source register."
                )


def _case_from_dict(raw: dict[str, Any]) -> Case:
    """Rebuild a case from its stored form."""
    return Case(
        case_id=raw["case_id"],
        company=raw["company"],
        sector=raw["sector"],
        stage=raw["stage"],
        requested_decision=raw["requested_decision"],
        thesis=raw["thesis"],
        owner=raw["owner"],
        opened_on=raw["opened_on"],
        sources=tuple(Source(**entry) for entry in raw.get("sources", [])),
        figures=tuple(
            Figure(
                metric=entry["metric"],
                value=entry["value"],
                status=entry["status"],
                source_labels=tuple(entry["source_labels"]),
            )
            for entry in raw.get("figures", [])
        ),
        assumptions=tuple(raw.get("assumptions", [])),
        flagged_conflicts=tuple(
            FlaggedConflict(**entry) for entry in raw.get("flagged_conflicts", [])
        ),
        ledger=tuple(LedgerEntry(**entry) for entry in raw.get("ledger", [])),
    )
