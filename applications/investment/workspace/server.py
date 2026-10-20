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

import argparse
import json
import threading
import webbrowser
from dataclasses import asdict
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from applications.investment.workspace import (
    analysis,
    assistant,
    diligence,
    explain,
    intake,
)
from applications.investment.workspace.cases import (
    Case,
    CaseStore,
    Figure,
    FlaggedConflict,
    IntakeRecord,
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
            elif segments == ["api", "worked-example"]:
                payload = self._open_worked_example()
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
        if action == "read":
            return self._read_prose(case_id, body)
        if action == "accept":
            self._accept_intake(case_id, body)
            return self._case_detail(case_id)
        if action == "ask":
            return self._ask(case_id, body)
        raise LookupError(action)

    def _read_prose(self, case_id: str, body: dict[str, Any]) -> dict[str, Any]:
        """Read pasted prose and return proposals. Changes nothing.

        A read, expressed as a POST because the text travels in the body. The
        case is untouched: these are suggestions until someone accepts them.
        """
        case = self.store.load(case_id)
        text = _text(body, "text")
        reading = intake.read(text, case.sources)
        read_by = "reader"

        # The model reads messier prose than the keyword reader does. It is
        # tried second and only replaces the figures, never the governance: its
        # proposals are the same Proposal objects, still unconfirmed, still
        # carrying a span that had to be found verbatim in the text.
        if assistant.enabled():
            attributable = case.sources + tuple(
                Source(label=item.label, origin=item.origin, kind=item.kind)
                for item in reading.sources
            )
            try:
                proposed = assistant.propose(text, attributable)
            except assistant.AssistantUnavailable as exc:
                read_by = f"reader (the model was unavailable: {exc})"
            else:
                if proposed:
                    reading = intake.Reading(sources=reading.sources, figures=proposed)
                    read_by = "model"

        return {
            "text": text,
            "read_by": read_by,
            "sources": [asdict(source) for source in reading.sources],
            "proposals": [
                asdict(proposal) | {"needs_attention": proposal.needs_attention}
                for proposal in reading.figures
            ],
            "unmatched": [
                asdict(item)
                for item in diligence.outstanding(
                    frozenset(proposal.metric for proposal in reading.figures)
                )
            ],
        }

    def _accept_intake(self, case_id: str, body: dict[str, Any]) -> None:
        """Fold the readings a person confirmed into the case material.

        Sources the reader confirmed are registered first, because a figure may
        not cite a source that is not in the register -- the one rule the
        product enforces purely for the audit trail.
        """
        confirmed_sources = tuple(
            Source(
                label=_text(entry, "label"),
                origin=_text(entry, "origin"),
                kind=_text(entry, "kind"),
            )
            for entry in _entries(body, "sources")
        )
        if confirmed_sources:
            case = self.store.load(case_id)
            have = {source.label for source in case.sources}
            self.store.record_material(
                case_id,
                sources=case.sources
                + tuple(item for item in confirmed_sources if item.label not in have),
                figures=case.figures,
                assumptions=case.assumptions,
                flagged_conflicts=case.flagged_conflicts,
            )

        accepted = tuple(
            IntakeRecord(
                record_id="",
                metric=_text(entry, "metric"),
                value=_text(entry, "value"),
                status=_text(entry, "status"),
                source_label=_text(entry, "source_label"),
                quote=_text(entry, "quote"),
                basis=_text(entry, "basis"),
                recorded_on=_text(entry, "recorded_on"),
                edited=bool(entry.get("edited", False)),
            )
            for entry in _entries(body, "accepted")
        )
        if not accepted and not confirmed_sources:
            raise ValueError("Nothing was accepted.")
        if accepted:
            self.store.accept_intake(case_id, accepted)

    def _ask(self, case_id: str, body: dict[str, Any]) -> dict[str, Any]:
        """Answer a question about this case from its record."""
        case = self.store.load(case_id)
        judgment = analysis.read_judgment(self.store, case) if case.judgments else None
        question = _text(body, "question")

        # Compute first, phrase second. The deterministic answer is the answer;
        # the model only changes its wording, and is checked afterwards for
        # figures the record does not contain.
        reply = explain.answer(question, case, judgment)
        text = reply.text
        phrased_by = "record"
        note = ""

        extract = json.dumps(asdict(judgment) if judgment else {}, indent=1)[:12000]

        if assistant.enabled():
            try:
                if reply.understood:
                    # A recognised question already has an answer. The model
                    # only puts the record's answer into better words.
                    phrased = assistant.phrase(question, case, reply.text, extract)
                else:
                    # Anything else: an ordinary conversation, grounded in the
                    # record rather than refused for not matching a phrasing.
                    phrased = assistant.converse(question, case, extract)
                text = phrased.text
                phrased_by = "model" if phrased.model_used else "record"
                note = phrased.note
            except assistant.AssistantUnavailable as exc:
                note = f"the model was unavailable: {exc}"

        return {
            "answer": text,
            "record_sources": list(reply.sources),
            "understood": reply.understood,
            "phrased_by": phrased_by,
            "note": note,
            "suggestions": list(explain.suggestions(case, judgment)),
        }

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

    def _open_worked_example(self) -> dict[str, Any]:
        """Open a case already carrying the worked example's material.

        The one action the register offers when it is empty. It leaves the case
        at *Material assembled*, so the reader still performs the two steps that
        matter: requesting the judgment and recording the decision.
        """
        case = analysis.open_worked_example(self.store)
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
            "suggestions": [],
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
        judgment = None
        if case.judgments:
            judgment = analysis.read_judgment(self.store, case, judgment_id)
            payload["judgment"] = asdict(judgment)
        payload["suggestions"] = list(explain.suggestions(case, judgment))
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
        "assistant": assistant.status(),
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


# ASCII only. A Windows console runs a legacy codepage by default and renders an
# em dash as a replacement character, which is a poor first impression from the
# one screen that tells a new reader what to do.
BANNER = """\
  YUKTI - Investment Committee Workspace

  Open:        {url}
  Case store:  {store}

  What to do, in order:
    1. Open a case, or load the worked example from the empty register.
    2. Material  - register the sources, then record figures against them.
    3. Judgment  - request one. The engine reads only the material.
    4. Decision  - record what the committee chose. Audit keeps the receipt.

  Stop with Ctrl-C. Local development only: no accounts, no access control.
"""


def main(argv: list[str] | None = None) -> int:
    """Run the workspace server.

    Opens a browser by default. Someone handed this application should not have
    to read a port off a console to use it, and the port is the only thing the
    console said that they needed.
    """
    parser = argparse.ArgumentParser(
        prog="yukti",
        description="Run the YUKTI investment committee workspace.",
    )
    parser.add_argument("--host", default=HOST, help=f"default: {HOST}")
    parser.add_argument("--port", type=int, default=PORT, help=f"default: {PORT}")
    parser.add_argument(
        "--no-browser", action="store_true", help="do not open a browser"
    )
    parser.add_argument(
        "--check-assist",
        action="store_true",
        help="check the optional language model wiring and exit",
    )
    args = parser.parse_args(argv)

    if args.check_assist:
        print(assistant.check())
        return 0

    STORE.root.mkdir(parents=True, exist_ok=True)
    try:
        server = ThreadingHTTPServer((args.host, args.port), WorkspaceHandler)
    except OSError as exc:
        print(f"Could not start on {args.host}:{args.port} — {exc}")
        print("Something else may be using the port. Try: --port 8771")
        return 1

    url = f"http://{args.host}:{args.port}/"
    print(BANNER.format(url=url, store=STORE.root))

    if not args.no_browser:
        # Slightly delayed so the first request cannot race the serve loop, and
        # swallowed on failure: a machine with no browser should still get a
        # working server, not a traceback under the instructions.
        def open_browser() -> None:
            try:
                webbrowser.open(url)
            except Exception:
                pass

        threading.Timer(0.5, open_browser).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
