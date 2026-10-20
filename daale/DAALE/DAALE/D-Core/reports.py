"""Report path utilities for Prototype-001 infrastructure.

These utilities prepare directories and path names only. They do not generate
report content.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class ReportPaths:
    """Paths reserved for a single dated report output."""

    root: Path
    date_directory: Path
    report_markdown: Path
    metadata_json: Path


def build_report_paths(
    reports_root: Path, report_date: date | None = None
) -> ReportPaths:
    """Return the expected report paths without creating report files."""
    selected_date = report_date or date.today()
    root = reports_root.resolve()
    date_directory = root / selected_date.isoformat()

    return ReportPaths(
        root=root,
        date_directory=date_directory,
        report_markdown=date_directory / "report.md",
        metadata_json=date_directory / "metadata.json",
    )


def ensure_reports_root(reports_root: Path) -> Path:
    """Create the reports root directory if it does not exist."""
    root = reports_root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def prepare_report_directory(
    reports_root: Path, report_date: date | None = None
) -> ReportPaths:
    """Create the dated report directory without writing report files."""
    paths = build_report_paths(ensure_reports_root(reports_root), report_date)
    paths.date_directory.mkdir(parents=True, exist_ok=True)
    return paths


def verify_reports_root_writable(reports_root: Path) -> tuple[bool, str]:
    """Check whether the reports root can be created and written to."""
    try:
        root = ensure_reports_root(reports_root)
        probe = root / ".write-test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
    except OSError as exc:
        return False, str(exc)

    return True, f"Writable reports directory: {root}"
