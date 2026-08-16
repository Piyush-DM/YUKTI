"""The workspace application server.

Serves the workspace UI and a small JSON interface over the case store and the
reasoning engine. Standard library only, following the pattern already
established by ``prototype_risk_rik/server.py`` -- but sharing no code with it,
because that path is legacy under ``DECISION-001`` and this one makes no model
calls.

The interface is deliberately small. Every endpoint corresponds to something a
person does: list the cases, open one, assemble the material, request a
judgment, record a decision. There is no generic resource layer, no filtering,
and no pagination, because nothing in the product needs them yet.

Local development only. No authentication, no multi-user access control, no
concurrency handling beyond what ``ThreadingHTTPServer`` provides by default.
Those are institutional requirements that a real deployment would have to meet,
and pretending otherwise here would be worse than saying so.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from applications.investment.workspace import analysis, diligence
from applications.investment.workspace.cases import (
    Case,
    CaseStore,
    Figure,
    FlaggedConflict,
    LedgerEntry,
    Source,
)

HOST = "127.0.0.1"
PORT = 8770
UI_ROOT = Path(__file__).resolve().parent / "ui"

STORE = CaseStore()


class WorkspaceHandler(SimpleHTTPRequestHandler):
    """Serve the workspace UI and its JSON interface."""

    store = STORE

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(UI_ROOT), **kwargs)

    def log_message(self, format: str, *args: Any) -> None:
        """Keep the console readable; the server is a development tool."""

    def end_headers(self) -> None:
        """Never serve a stale build.

        `SimpleHTTPRequestHandler` revalidates static files with
        `Last-Modified`, and a browser holding `app.js` in memory will keep
        using it — so a last-minute change before a demo can silently show the
        previous build. Verified while building the staged reveal: the browser
        served the old `app.js` until the fetch was forced.

        Demo reliability, not a caching strategy. This server is local
        development only; there is nothing here worth caching.
        """
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self) -> None:
        """Serve JSON reads, or fall through to the static UI."""
        if not self.path.startswith("/api/"):
            super().do_GET()
            return

        try:
            payload = self._route_get()
        except KeyError:
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Case not found."})
            return
        except LookupError:
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Unknown endpoint."})
            return

        self._send_json(HTTPStatus.OK, payload)

    def do_POST(self) -> None:
        """Handle the five things a person can do."""
        segments = self._segments()
        try:
            body = self._read_json()
            if segments == ["api", "cases"]:
                payload = self._open_case(body)
            elif len(segments) == 4 and segments[:2] == ["api", "cases"]:
                payload = self._case_action(segments[2], segments[3], body)
            else:
                raise LookupError(self.path)
        except KeyError:
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Case not found."})
            return
        except LookupError:
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Unknown endpoint."})
            return
        except analysis.MaterialIncomplete as exc:
            self._send_json(HTTPStatus.CONFLICT, {"error": str(exc)})
            return
        except ValueError as exc:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
            return

        self._send_json(HTTPStatus.OK, payload)

    # -- routing -----------------------------------------------------------

    def _segments(self) -> list[str]:
        return [part for part in self.path.split("?")[0].split("/") if part]

    def _route_get(self) -> dict[str, Any]:
        segments = self._segments()
        if segments == ["api", "schedule"]:
            return _schedule_payload()
        if segments == ["api", "reference-material"]:
            return analysis.reference_material()
        if segments == ["api", "cases"]:
            return {"cases": [_case_summary(case) for case in self.store.load_all()]}
        if len(segments) == 3 and segments[:2] == ["api", "cases"]:
            return self._case_detail(segments[2])
        if len(segments) == 4 and segments[:2] == ["api", "cases"]:
            if segments[3] == "report":
                return {"report": analysis.rendered_report(self.store, segments[2])}
        # A superseded judgment reads exactly as it did the day it was reached.
        # This is the route an auditor uses to check an old decision.
        if len(segments) == 5 and segments[:2] == ["api", "cases"]:
            if segments[3] == "judgments":
                return self._case_detail(segments[2], segments[4])
        if len(segments) == 6 and segments[:2] == ["api", "cases"]:
            if segments[3] == "judgments" and segments[5] == "report":
                return {
                    "report": analysis.rendered_report(
                        self.store, segments[2], segments[4]
                    )
                }
        raise LookupError(self.path)

    def _case_action(
        self, case_id: str, action: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        if action == "material":
            self._record_material(case_id, body)
            return self._case_detail(case_id)
        if action == "analysis":
            analysis.request_judgment(self.store, case_id)
            return self._case_detail(case_id)
        if action == "decision":
            self._record_decision(case_id, body)
            return self._case_detail(case_id)
        raise LookupError(action)

    # -- actions -----------------------------------------------------------

    def _open_case(self, body: dict[str, Any]) -> dict[str, Any]:
        case = self.store.open_case(
            company=_text(body, "company"),
            sector=_text(body, "sector"),
            stage=_text(body, "stage"),
            requested_decision=_text(body, "requested_decision"),
            thesis=_text(body, "thesis"),
            owner=_text(body, "owner"),
        )
        return self._case_detail(case.case_id)

    def _record_material(self, case_id: str, body: dict[str, Any]) -> None:
        self.store.record_material(
            case_id,
            sources=tuple(
                Source(
                    label=_text(entry, "label"),
                    origin=_text(entry, "origin"),
                    kind=_text(entry, "kind"),
                )
                for entry in _entries(body, "sources")
            ),
            figures=tuple(
                Figure(
                    metric=_text(entry, "metric"),
                    value=_text(entry, "value"),
                    status=_text(entry, "status"),
                    source_labels=tuple(entry.get("source_labels", [])),
                )
                for entry in _entries(body, "figures")
            ),
            assumptions=tuple(
                str(entry).strip()
                for entry in body.get("assumptions", [])
                if str(entry).strip()
            ),
            flagged_conflicts=tuple(
                FlaggedConflict(
                    metric=_text(entry, "metric"), note=_text(entry, "note")
                )
                for entry in _entries(body, "flagged_conflicts")
            ),
        )

    def _record_decision(self, case_id: str, body: dict[str, Any]) -> None:
        case = self.store.load(case_id)
        if not case.judgments:
            raise ValueError("Request an institutional judgment before deciding.")

        # The decision binds to the judgment in force when it was taken, and
        # keeps pointing there for good. Later analyses supersede that judgment;
        # they never reach back into a decision already recorded against it.
        judgment = analysis.read_judgment(self.store, case)
        self.store.append_ledger_entry(
            case_id,
            LedgerEntry(
                entry_id=f"LEDGER-{len(case.ledger) + 1:03d}",
                judgment_id=judgment.judgment_id,
                decision=_text(body, "decision"),
                decided_by=_text(body, "decided_by"),
                rationale=_text(body, "rationale"),
                recorded_on=_text(body, "recorded_on"),
                judgment_recommendation=judgment.recommendation,
                judgment_confidence=judgment.confidence,
                record_digest=judgment.record_digest,
                material_digest=judgment.material_digest,
                snapshot_id=judgment.snapshot_id,
            ),
        )

    # -- reads -------------------------------------------------------------

    def _case_detail(
        self, case_id: str, judgment_id: str | None = None
    ) -> dict[str, Any]:
        case = self.store.load(case_id)
        payload: dict[str, Any] = {
            "case": asdict(case),
            "title": case.title,
            "status": case.status(),
            "outstanding": [
                asdict(entry)
                for entry in diligence.outstanding(case.recorded_metrics())
            ],
            "judgment": None,
            "ledger_verification": [
                asdict(check)
                | {
                    "resolves": check.resolves,
                    "record_resolves": check.record_resolves,
                    "material_resolves": check.material_resolves,
                }
                for check in analysis.verify_ledger(self.store, case_id)
            ],
        }
        if case.judgments:
            payload["judgment"] = asdict(
                analysis.read_judgment(self.store, case, judgment_id)
            )
        return payload

    # -- transport ---------------------------------------------------------

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if not length:
            return {}
        parsed = json.loads(self.rfile.read(length).decode("utf-8"))
        if not isinstance(parsed, dict):
            raise ValueError("Request body must be a JSON object.")
        return parsed

    def _send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _case_summary(case: Case) -> dict[str, Any]:
    """What the case register shows for one case."""
    return {
        "case_id": case.case_id,
        "title": case.title,
        "company": case.company,
        "sector": case.sector,
        "stage": case.stage,
        "owner": case.owner,
        "opened_on": case.opened_on,
        "requested_decision": case.requested_decision,
        "status": case.status(),
        "decisions": len(case.ledger),
        "judgments": len(case.judgments),
    }


def _schedule_payload() -> dict[str, Any]:
    """The diligence schedule and intake vocabularies, for the intake screens."""
    return {
        "review_areas": list(diligence.REVIEW_AREAS),
        "schedule": [asdict(entry) for entry in diligence.SCHEDULE],
        "source_kinds": [asdict(entry) for entry in diligence.SOURCE_KINDS],
        "figure_statuses": [asdict(entry) for entry in diligence.FIGURE_STATUSES],
    }


def _entries(body: dict[str, Any], key: str) -> list[dict[str, Any]]:
    """Return a required list of objects from the request body."""
    value = body.get(key, [])
    if not isinstance(value, list) or not all(
        isinstance(entry, dict) for entry in value
    ):
        raise ValueError(f"'{key}' must be a list of objects.")
    return value


def _text(source: dict[str, Any], key: str) -> str:
    """Return a string field from the request body, defaulting to empty."""
    value = source.get(key, "")
    if not isinstance(value, str):
        raise ValueError(f"'{key}' must be a string.")
    return value


def main() -> int:
    """Run the workspace server."""
    STORE.root.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((HOST, PORT), WorkspaceHandler)
    print(f"YUKTI workspace running at http://{HOST}:{PORT}/")
    print(f"Case store: {STORE.root}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
