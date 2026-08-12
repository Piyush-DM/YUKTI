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

from applications.investment.workspace.material import (
    MaterialSnapshot,
    compute_material_digest,
    next_snapshot,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_STORE_ROOT = REPOSITORY_ROOT / "reports" / "workspace"

CASE_FILE = "case.json"
JUDGMENTS_DIRECTORY = "judgments"

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
class JudgmentRecord:
    """One analysis of this case, kept for as long as the case exists.

    Judgments are **superseded, never replaced.** A later analysis marks this
    one superseded and takes its place as current; this one keeps its
    identifier, its digest, and its artifacts on disk forever, because a
    decision recorded against it must stay verifiable after the material has
    moved on.

    ``superseded_by`` is the id of the judgment that replaced this one, or the
    empty string while this is the current judgment.
    """

    judgment_id: str
    record_digest: str
    recorded_on: str
    superseded_by: str = ""
    # What the judgment was formed from. ``record_digest`` proves two judgments
    # reasoned identically; these prove they read the same material, which is a
    # separate and stronger claim. See material.py.
    material_digest: str = ""
    snapshot_id: str = ""

    @property
    def is_current(self) -> bool:
        """True while no later analysis has replaced this one."""
        return not self.superseded_by


@dataclass(frozen=True)
class LedgerEntry:
    """One decision the institution recorded against an analysis.

    The judgment is what the analysis concluded; the decision is what the
    institution chose to do about it. They are stored separately and on purpose:
    a committee that overrides a recommendation is the most important thing the
    ledger can record, and collapsing the two would erase it.

    ``judgment_id`` binds the decision to the exact analysis it was taken
    against. That binding is permanent. Re-analysing the case creates a new
    judgment and leaves this one — and therefore this decision — untouched and
    still resolvable.
    """

    entry_id: str
    judgment_id: str
    decision: str
    decided_by: str
    rationale: str
    recorded_on: str
    judgment_recommendation: str
    judgment_confidence: str
    record_digest: str
    # Recorded on the decision as well as on the judgment, so verification does
    # not depend on the judgment record still being intact to check the
    # material. A decision should be able to state, by itself, what it rested on.
    material_digest: str = ""
    snapshot_id: str = ""


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
    snapshots: tuple[MaterialSnapshot, ...] = ()
    judgments: tuple[JudgmentRecord, ...] = ()
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

    def current_snapshot(self) -> MaterialSnapshot | None:
        """The material in force, or None before any material was recorded."""
        return self.snapshots[-1] if self.snapshots else None

    def snapshot(self, snapshot_id: str) -> MaterialSnapshot | None:
        """Look up any material state this case has ever held."""
        for record in self.snapshots:
            if record.snapshot_id == snapshot_id:
                return record
        return None

    def current_judgment(self) -> JudgmentRecord | None:
        """The judgment in force, or None if the case has never been analysed."""
        return self.judgments[-1] if self.judgments else None

    def judgment(self, judgment_id: str) -> JudgmentRecord | None:
        """Look up any judgment this case has ever reached, current or not."""
        for record in self.judgments:
            if record.judgment_id == judgment_id:
                return record
        return None

    def status(self) -> str:
        """Derive the case status from the record.

        Every input is on the case itself, so status cannot disagree with what
        is on file. The judgment history is part of the case now, which is why
        this no longer has to be told whether an analysis exists.
        """
        if self.ledger:
            return STATUS_DECIDED
        if self.judgments:
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
        recorded_on: str | None = None,
    ) -> Case:
        """Replace the case material wholesale and snapshot it if it changed.

        Whole-record replacement rather than per-item editing: the diligence
        pack is assembled and then submitted, and a half-applied set of figures
        is not a state the institution should be able to reach.

        A snapshot is appended whenever the material digest moves, whether or
        not anyone runs an analysis afterwards. The registry is a record of what
        the institution assembled and when -- deliberation over material, not
        only the states that happened to be analysed.
        """
        case = self.load(case_id)
        _validate_material(sources, figures)
        updated = replace(
            case,
            sources=sources,
            figures=figures,
            assumptions=assumptions,
            flagged_conflicts=flagged_conflicts,
        )

        digest = compute_material_digest(updated)
        current = updated.current_snapshot()
        if current is None or current.material_digest != digest:
            snapshot = next_snapshot(
                updated, digest, recorded_on or date.today().isoformat()
            )
            updated = replace(updated, snapshots=updated.snapshots + (snapshot,))

        return self.save(updated)

    def judgments_directory(self, case_id: str) -> Path:
        """Where every judgment this case has ever reached is kept."""
        return self.directory(case_id) / JUDGMENTS_DIRECTORY

    def judgment_directory(self, case_id: str, judgment_id: str) -> Path:
        """Where one judgment's artifacts live. Written once, never rewritten."""
        return self.judgments_directory(case_id) / judgment_id

    def append_judgment(
        self, case_id: str, record_digest: str, recorded_on: str
    ) -> tuple[Case, JudgmentRecord]:
        """Record a new judgment, superseding the current one.

        **Keyed on material, not on reasoning.** A change to what the
        institution assembled creates a new judgment even when the conclusion is
        unchanged, because institutional history records deliberation over
        material rather than only changes of mind.

        Returns the existing judgment unchanged only when the material is
        byte-identical -- which, the engine being deterministic, also means the
        reasoning is. Recording that twice would put an event in the record that
        never happened.

        Keying on ``record_digest`` here would be wrong and was the earlier
        behaviour: two materially different diligence packs can produce one
        reasoning record, so a real material change could pass unrecorded.

        The previous judgment is marked superseded and otherwise left alone. Its
        artifacts stay on disk and any decision citing it keeps resolving.
        """
        case = self.load(case_id)
        snapshot = case.current_snapshot()
        material_digest = snapshot.material_digest if snapshot else ""
        snapshot_id = snapshot.snapshot_id if snapshot else ""

        current = case.current_judgment()
        if current is not None and current.material_digest == material_digest:
            return case, current

        judgment_id = f"JUDGMENT-{len(case.judgments) + 1:03d}"
        superseded = tuple(
            replace(record, superseded_by=judgment_id) if record.is_current else record
            for record in case.judgments
        )
        record = JudgmentRecord(
            judgment_id=judgment_id,
            record_digest=record_digest,
            recorded_on=recorded_on,
            material_digest=material_digest,
            snapshot_id=snapshot_id,
        )
        return self.save(replace(case, judgments=superseded + (record,))), record

    def append_ledger_entry(self, case_id: str, entry: LedgerEntry) -> Case:
        """Add a decision to the case's ledger. Entries are never removed."""
        case = self.load(case_id)
        if case.judgment(entry.judgment_id) is None:
            raise ValueError(
                f"Decision cites judgment '{entry.judgment_id}', which this case "
                "has never reached. A decision must bind to a real judgment."
            )
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
        snapshots=tuple(
            MaterialSnapshot(
                snapshot_id=entry["snapshot_id"],
                material_digest=entry["material_digest"],
                version=entry["version"],
                recorded_on=entry["recorded_on"],
                case_id=entry["case_id"],
            )
            for entry in raw.get("snapshots", [])
        ),
        judgments=tuple(
            JudgmentRecord(
                judgment_id=entry["judgment_id"],
                record_digest=entry["record_digest"],
                recorded_on=entry["recorded_on"],
                superseded_by=entry.get("superseded_by", ""),
                material_digest=entry.get("material_digest", ""),
                snapshot_id=entry.get("snapshot_id", ""),
            )
            for entry in raw.get("judgments", [])
        ),
        ledger=tuple(
            LedgerEntry(
                entry_id=entry["entry_id"],
                judgment_id=entry.get("judgment_id", ""),
                decision=entry["decision"],
                decided_by=entry["decided_by"],
                rationale=entry["rationale"],
                recorded_on=entry["recorded_on"],
                judgment_recommendation=entry["judgment_recommendation"],
                judgment_confidence=entry["judgment_confidence"],
                record_digest=entry["record_digest"],
                material_digest=entry.get("material_digest", ""),
                snapshot_id=entry.get("snapshot_id", ""),
            )
            for entry in raw.get("ledger", [])
        ),
    )
