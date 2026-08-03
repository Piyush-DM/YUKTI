"""Local HTTP bridge for the prototype Risk RIK UI integration.

This is a development-only server for the investment prototype. It is not a
production API and does not define DAALE runtime architecture.
"""

from __future__ import annotations

from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
import json

from pydantic import ValidationError

from applications.investment.prototype_risk_rik.contracts import (
    RiskRikExecutionError,
    RiskRikExecutionRequest,
)
from applications.investment.prototype_risk_rik.executor import execute_risk_rik
from applications.investment.prototype_risk_rik.provider import (
    ProviderConfigurationError,
    configured_adapter_from_environment,
    provider_status_from_environment,
)


HOST = "127.0.0.1"
PORT = 8765
UI_ROOT = Path(__file__).resolve().parents[1] / "prototype-ui"


class PrototypeRiskRikHandler(SimpleHTTPRequestHandler):
    """Serve the static UI and prototype Risk RIK execution endpoint."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(UI_ROOT), **kwargs)

    def do_POST(self) -> None:
        """Handle prototype execution requests."""
        if self.path != "/prototype-risk-rik/execute":
            self.send_error(HTTPStatus.NOT_FOUND, "Unknown prototype endpoint")
            return

        try:
            request = RiskRikExecutionRequest.model_validate(self._read_json())
            adapter = configured_adapter_from_environment()
            artifact = execute_risk_rik(request, adapter)
        except ValidationError as exc:
            self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"ok": False, "error": f"Invalid request: {exc}"},
            )
            return
        except ProviderConfigurationError as exc:
            self._send_json(
                HTTPStatus.PRECONDITION_REQUIRED,
                {"ok": False, "error": str(exc)},
            )
            return
        except RiskRikExecutionError as exc:
            self._send_json(
                HTTPStatus.BAD_GATEWAY,
                {"ok": False, "error": str(exc)},
            )
            return

        self._send_json(
            HTTPStatus.OK,
            {
                "ok": True,
                "provider": provider_status_from_environment().__dict__,
                "artifact": artifact.model_dump(mode="json"),
            },
        )

    def do_GET(self) -> None:
        """Serve provider status or static prototype UI files."""
        if self.path == "/prototype-risk-rik/provider":
            self._send_json(
                HTTPStatus.OK,
                {"ok": True, "provider": provider_status_from_environment().__dict__},
            )
            return

        super().do_GET()

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        data = self.rfile.read(length)
        parsed = json.loads(data.decode("utf-8"))
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


def main() -> int:
    """Run the local prototype server."""
    server = ThreadingHTTPServer((HOST, PORT), PrototypeRiskRikHandler)
    print(f"Serving YUKTI investment prototype at http://{HOST}:{PORT}/")
    print("Prototype endpoint: POST /prototype-risk-rik/execute")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
