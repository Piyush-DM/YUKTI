"""The freeze boundary between reading and reasoning.

    source material                    -- may vary: prose, phrasing, noise
          |
    reader  (keyword or model)         -- may vary: the model especially
          |
    EvidenceRecord   ========= FREEZE =========
          |
    deterministic engine               -- must NOT vary given a fixed record
          |
    verdict

An :class:`EvidenceRecord` is exactly what one reader made of one block of
prose: the sources it recognised and the figures it proposed, each carrying the
passage it was read from. It is canonically ordered and hashable.

Its ``digest`` covers only what actually reaches the engine -- metric, value,
status, citation, and the source register. It excludes the quote, the reader's
name and the timestamp, mirroring the product, where ``material_digest``
already excludes provenance (see ``workspace/material.py`` and
``IntakeRecord``). A figure typed by hand and the same figure lifted from a
memo are the same evidence and must hash alike.

That makes two kinds of variance separable and separately measurable:

* **reading variance** -- two reader runs produce EvidenceRecords with
  different digests. Normal and expected for the model. This is where the
  confidence-band flip observed on memo 2 actually lives.
* **reasoning variance** -- one EvidenceRecord, replayed through the engine
  more than once, produces different engine records. This must never happen,
  and :meth:`EvidenceRecord.replay_is_stable` asserts it does not.

Nothing here makes a verdict reproducible by pinning the verdict. The
reproducible object is the evidence; the engine is already deterministic over
it. If it ever is not, that difference is the finding.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone

REPOSITORY_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from applications.investment.workspace import analysis, assistant, intake  # noqa: E402
from applications.investment.workspace.cases import (  # noqa: E402
    CaseStore,
    Figure,
    Source,
)
from applications.investment.workspace.diligence import SCHEDULE  # noqa: E402

KEYWORD_READER = "keyword"
MODEL_READER = "model"

_SCHEDULE_ORDER = {item.metric: index for index, item in enumerate(SCHEDULE)}


@dataclass(frozen=True, order=True)
class FrozenSource:
    """One recognised source, exactly as it will enter the register."""

    label: str
    origin: str
    kind: str


@dataclass(frozen=True)
class FrozenFigure:
    """One proposed figure. ``quote`` and ``basis`` are provenance only."""

    metric: str
    value: str
    status: str
    source_label: str
    quote: str
    basis: str


@dataclass(frozen=True)
class ReplayCheck:
    """The result of replaying one frozen record through the engine N times."""

    evidence_digest: str
    times: int
    record_digests: frozenset[str]
    verdicts: frozenset[tuple[str, str, int, int, int]]

    @property
    def stable(self) -> bool:
        """True when every replay produced the identical engine record."""
        return len(self.record_digests) == 1 and len(self.verdicts) == 1

    @property
    def verdict(self) -> tuple[str, str, int, int, int]:
        """The single verdict every replay reached. Raises if they disagreed."""
        if len(self.verdicts) != 1:
            raise ValueError(f"replays disagreed: {sorted(self.verdicts)}")
        return next(iter(self.verdicts))


@dataclass(frozen=True)
class EvidenceRecord:
    """What one reader made of one memo. The freeze boundary."""

    reader: str
    memo: str
    read_at: str
    sources: tuple[FrozenSource, ...]
    figures: tuple[FrozenFigure, ...]
    unattributed: tuple[FrozenFigure, ...]

    # -- canonical ordering ------------------------------------------------

    def _ordered_sources(self) -> tuple[FrozenSource, ...]:
        return tuple(sorted(self.sources))

    def _ordered_figures(self) -> tuple[FrozenFigure, ...]:
        return tuple(
            sorted(
                self.figures,
                key=lambda f: (_SCHEDULE_ORDER.get(f.metric, 99), f.metric),
            )
        )

    def engine_input(self) -> dict[str, object]:
        """Exactly what will reach the engine, and nothing else."""
        return {
            "sources": [
                {"label": s.label, "origin": s.origin, "kind": s.kind}
                for s in self._ordered_sources()
            ],
            "figures": [
                {
                    "metric": f.metric,
                    "value": f.value,
                    "status": f.status,
                    "source_label": f.source_label,
                }
                for f in self._ordered_figures()
            ],
        }

    @property
    def digest(self) -> str:
        """SHA-256 over the engine input. Provenance and timing excluded."""
        blob = json.dumps(
            self.engine_input(), sort_keys=True, separators=(",", ":")
        )
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    # -- persistence -----------------------------------------------------

    def to_json(self) -> str:
        payload = {
            "reader": self.reader,
            "memo": self.memo,
            "read_at": self.read_at,
            "evidence_digest": self.digest,
            "sources": [
                {"label": s.label, "origin": s.origin, "kind": s.kind}
                for s in self._ordered_sources()
            ],
            "figures": [
                {
                    "metric": f.metric,
                    "value": f.value,
                    "status": f.status,
                    "source_label": f.source_label,
                    "quote": f.quote,
                    "basis": f.basis,
                }
                for f in self._ordered_figures()
            ],
            "unattributed": [
                {
                    "metric": f.metric,
                    "value": f.value,
                    "status": f.status,
                    "quote": f.quote,
                    "basis": f.basis,
                }
                for f in sorted(self.unattributed, key=lambda f: f.metric)
            ],
        }
        return json.dumps(payload, indent=2, sort_keys=True) + "\n"

    @classmethod
    def from_json(cls, blob: str) -> EvidenceRecord:
        raw = json.loads(blob)
        return cls(
            reader=raw["reader"],
            memo=raw["memo"],
            read_at=raw.get("read_at", ""),
            sources=tuple(
                FrozenSource(s["label"], s["origin"], s["kind"])
                for s in raw.get("sources", [])
            ),
            figures=tuple(
                FrozenFigure(
                    f["metric"],
                    f["value"],
                    f["status"],
                    f["source_label"],
                    f.get("quote", ""),
                    f.get("basis", ""),
                )
                for f in raw.get("figures", [])
            ),
            unattributed=tuple(
                FrozenFigure(
                    f["metric"],
                    f["value"],
                    f["status"],
                    "",
                    f.get("quote", ""),
                    f.get("basis", ""),
                )
                for f in raw.get("unattributed", [])
            ),
        )

    # -- replay --------------------------------------------------------

    def replay(
        self, root: pathlib.Path, *, recorded_on: str = "2026-09-07"
    ) -> analysis.Judgment:
        """Feed this frozen record through the engine. No prose is consulted.

        Builds a throwaway case from the record alone and runs the engine
        exactly as the product does -- ``record_material`` then
        ``request_judgment`` -- so anything this proves, the product inherits.
        """
        store = CaseStore(root)
        case = store.open_case(
            company=self.memo,
            sector="experiment",
            stage="Series B",
            requested_decision="Approve",
            thesis="",
            owner="replay",
            opened_on=recorded_on,
        )
        store.record_material(
            case.case_id,
            tuple(
                Source(s.label, s.origin, s.kind) for s in self._ordered_sources()
            ),
            tuple(
                Figure(f.metric, f.value, f.status, (f.source_label,))
                for f in self._ordered_figures()
            ),
            (),
            (),
            recorded_on=recorded_on,
        )
        return analysis.request_judgment(
            store, case.case_id, recorded_on=recorded_on
        )

    def replay_is_stable(
        self, *, times: int = 5, persist_root: pathlib.Path | None = None
    ) -> ReplayCheck:
        """Replay N times from THIS record and report whether the engine moved.

        When ``persist_root`` is given, the first replay runs against that
        directory instead of a discarded temp one, so the judgment it produces
        -- the case file, ``05-record.json``, the rest of the stage trail --
        survives on disk for audit, the same way ``orbital-series-b`` and
        ``meridian-robotics`` do. The remaining replays still run in temp
        directories; they exist only to confirm the engine reaches the same
        digest again, not to be kept.
        """
        digests: set[str] = set()
        verdicts: set[tuple[str, str, int, int, int]] = set()
        for index in range(times):
            if index == 0 and persist_root is not None:
                persist_root.mkdir(parents=True, exist_ok=True)
                judgment = self.replay(persist_root)
            else:
                with tempfile.TemporaryDirectory() as directory:
                    judgment = self.replay(pathlib.Path(directory))
            digests.add(judgment.record_digest)
            verdicts.add(
                (
                    judgment.recommendation,
                    judgment.confidence,
                    len(judgment.conditions),
                    len(judgment.disagreements),
                    len(judgment.outstanding_schedule_items),
                )
            )
        return ReplayCheck(
            evidence_digest=self.digest,
            times=times,
            record_digests=frozenset(digests),
            verdicts=frozenset(verdicts),
        )


def read_evidence(memo: str, text: str, *, reader: str) -> EvidenceRecord:
    """Read one memo into a frozen evidence record with the chosen reader.

    Source recognition is always the deterministic keyword pass -- the source
    vocabulary is small and closed, and keeping it fixed isolates the variable
    under study to the figure read. With ``reader="model"`` the figures come
    from the language model; otherwise from the keyword reader.
    """
    recognised = intake.read(text).sources
    as_sources = tuple(
        Source(s.label, s.origin, s.kind) for s in recognised
    )

    if reader == MODEL_READER:
        proposed = assistant.propose(text, as_sources)
        reader_name = assistant.status()["model"]
    else:
        proposed = intake.propose(text, as_sources)
        reader_name = KEYWORD_READER

    attributed: list[FrozenFigure] = []
    unattributed: list[FrozenFigure] = []
    for figure in proposed:
        row = FrozenFigure(
            metric=figure.metric,
            value=figure.value,
            status=figure.status,
            source_label=figure.source_label,
            quote=figure.span.quote,
            basis=figure.basis,
        )
        (attributed if figure.source_label else unattributed).append(row)

    return EvidenceRecord(
        reader=reader_name,
        memo=memo,
        read_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        sources=tuple(
            FrozenSource(s.label, s.origin, s.kind) for s in recognised
        ),
        figures=tuple(attributed),
        unattributed=tuple(unattributed),
    )


@dataclass(frozen=True)
class ReadingVariance:
    """How many distinct evidence records one reader produced for one memo."""

    memo: str
    reader: str
    runs: int
    records: tuple[EvidenceRecord, ...]

    @property
    def digests(self) -> tuple[str, ...]:
        return tuple(record.digest for record in self.records)

    @property
    def distinct(self) -> int:
        return len(set(self.digests))

    @property
    def stable(self) -> bool:
        return self.distinct == 1

    def differences(self) -> list[str]:
        """A per-metric account of where the distinct records disagree."""
        groups: dict[str, EvidenceRecord] = {}
        for record in self.records:
            groups.setdefault(record.digest, record)
        if len(groups) < 2:
            return []

        metrics: set[str] = set()
        per_digest: dict[str, dict[str, str]] = {}
        for digest, record in groups.items():
            mapped = {
                f.metric: f"{f.value}/{f.status}/{f.source_label or '-'}"
                for f in record.figures
            }
            per_digest[digest] = mapped
            metrics |= set(mapped)

        lines: list[str] = []
        for metric in sorted(metrics, key=lambda m: _SCHEDULE_ORDER.get(m, 99)):
            seen = {mapped.get(metric, "(absent)") for mapped in per_digest.values()}
            if len(seen) > 1:
                rendering = "  |  ".join(
                    f"{digest[:8]}={per_digest[digest].get(metric, '(absent)')}"
                    for digest in per_digest
                )
                lines.append(f"{metric}: {rendering}")
        return lines


def reading_variance(
    memo: str, text: str, *, reader: str, runs: int
) -> ReadingVariance:
    """Read one memo N times with one reader and collect the evidence records."""
    records = tuple(
        read_evidence(memo, text, reader=reader) for _ in range(runs)
    )
    return ReadingVariance(memo=memo, reader=reader, runs=runs, records=records)


__all__ = [
    "EvidenceRecord",
    "FrozenFigure",
    "FrozenSource",
    "KEYWORD_READER",
    "MODEL_READER",
    "ReadingVariance",
    "ReplayCheck",
    "read_evidence",
    "reading_variance",
]
