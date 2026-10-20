"""Hashing and audit-trace persistence for DAALE runs."""

import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path


def stable_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def hash_value(value):
    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()


def new_run_identity():
    now = datetime.now(timezone.utc)
    return {
        "run_id": f"run-{uuid.uuid4().hex}",
        "timestamp": now.isoformat(),
        "filename_timestamp": now.strftime("%Y%m%dT%H%M%S%fZ"),
    }


def _safe_filename_part(value):
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", value)
    return safe.strip("._-") or "unnamed"


def write_trace(trace, runs_directory):
    directory = Path(runs_directory)
    directory.mkdir(parents=True, exist_ok=True)

    case_id = _safe_filename_part(trace["case"]["case_id"])
    stamp = trace["run"]["filename_timestamp"]
    short_run_id = trace["run"]["run_id"].split("-", 1)[1][:12]
    path = directory / f"{case_id}-{stamp}-{short_run_id}.json"
    path.write_text(json.dumps(trace, indent=2, ensure_ascii=False), encoding="utf-8")
    return path

