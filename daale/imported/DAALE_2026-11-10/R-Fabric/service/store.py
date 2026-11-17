"""SQLite persistence: clients, hashed keys, and judgments.

Every read of judgment data takes the caller's ``client_id`` and filters on it.
There is deliberately no function that fetches a judgment by id alone, so a
route cannot forget the ownership check.
"""

import json
import secrets
import sqlite3
import threading
from collections import namedtuple
from datetime import datetime, timezone
from pathlib import Path

from .security import display_prefix, generate_key, hash_key

Identity = namedtuple("Identity", "client_id key_id")

SCHEMA = """
CREATE TABLE IF NOT EXISTS clients (
    client_id   TEXT PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,
    created_at  TEXT NOT NULL,
    disabled_at TEXT
);
CREATE TABLE IF NOT EXISTS api_keys (
    key_id       TEXT PRIMARY KEY,
    client_id    TEXT NOT NULL REFERENCES clients(client_id),
    key_hash     TEXT NOT NULL UNIQUE,
    key_prefix   TEXT NOT NULL,
    label        TEXT,
    created_at   TEXT NOT NULL,
    revoked_at   TEXT,
    last_used_at TEXT
);
CREATE TABLE IF NOT EXISTS judgments (
    judgment_id  TEXT PRIMARY KEY,
    client_id    TEXT NOT NULL REFERENCES clients(client_id),
    case_id      TEXT NOT NULL,
    policy_id    TEXT NOT NULL,
    status       TEXT NOT NULL,
    created_at   TEXT NOT NULL,
    started_at   TEXT,
    finished_at  TEXT,
    model        TEXT,
    request_json TEXT NOT NULL,
    decision_json TEXT,
    trace_json   TEXT,
    error        TEXT,
    model_calls  INTEGER NOT NULL DEFAULT 0,
    total_tokens INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS judgments_by_client ON judgments (client_id, created_at);
CREATE INDEX IF NOT EXISTS judgments_by_case ON judgments (client_id, case_id);
"""

ACTIVE = ("queued", "running")


def _now():
    return datetime.now(timezone.utc).isoformat()


def _json(value):
    return None if value is None else json.dumps(value, ensure_ascii=False)


class Store:
    def __init__(self, path):
        if str(path) != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(str(path), check_same_thread=False, isolation_level=None)
        self._db.row_factory = sqlite3.Row
        self._lock = threading.RLock()
        with self._lock:
            self._db.execute("PRAGMA foreign_keys = ON")
            self._db.execute("PRAGMA journal_mode = WAL")
            self._db.executescript(SCHEMA)

    def close(self):
        with self._lock:
            self._db.close()

    def _query(self, sql, params=()):
        with self._lock:
            return [dict(row) for row in self._db.execute(sql, params)]

    def _exec(self, sql, params=()):
        with self._lock:
            return self._db.execute(sql, params).rowcount

    # -- clients and keys (managed from the command line, never over HTTP) --

    def create_client(self, name):
        client_id = "cl_" + secrets.token_hex(6)
        self._exec(
            "INSERT INTO clients (client_id, name, created_at) VALUES (?, ?, ?)",
            (client_id, name, _now()),
        )
        return client_id

    def client_exists(self, client_id):
        return bool(self._query("SELECT 1 FROM clients WHERE client_id = ?", (client_id,)))

    def issue_key(self, client_id, label=None):
        """Create a key. The plaintext is returned once and never stored."""
        if not self.client_exists(client_id):
            raise KeyError(f"unknown client {client_id}")
        key = generate_key()
        key_id = "key_" + secrets.token_hex(5)
        self._exec(
            "INSERT INTO api_keys (key_id, client_id, key_hash, key_prefix, label, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (key_id, client_id, hash_key(key), display_prefix(key), label, _now()),
        )
        return key_id, key

    def revoke_key(self, key_id):
        return self._exec(
            "UPDATE api_keys SET revoked_at = ? WHERE key_id = ? AND revoked_at IS NULL",
            (_now(), key_id),
        ) == 1

    def disable_client(self, client_id):
        return self._exec(
            "UPDATE clients SET disabled_at = ? WHERE client_id = ? AND disabled_at IS NULL",
            (_now(), client_id),
        ) == 1

    def list_keys(self):
        return self._query(
            "SELECT k.key_id, k.client_id, c.name AS client_name, k.key_prefix, k.label, "
            "k.created_at, k.revoked_at, k.last_used_at "
            "FROM api_keys k JOIN clients c USING (client_id) ORDER BY k.created_at"
        )

    def authenticate(self, key):
        """The identity behind a key, or None if unknown, revoked or disabled."""
        rows = self._query(
            "SELECT k.key_id, k.client_id FROM api_keys k "
            "JOIN clients c ON c.client_id = k.client_id "
            "WHERE k.key_hash = ? AND k.revoked_at IS NULL AND c.disabled_at IS NULL",
            (hash_key(key),),
        )
        if not rows:
            return None
        self._exec("UPDATE api_keys SET last_used_at = ? WHERE key_id = ?", (_now(), rows[0]["key_id"]))
        return Identity(rows[0]["client_id"], rows[0]["key_id"])

    # -- judgments ---------------------------------------------------------

    def create_judgment(self, client_id, case, policy_id, model):
        judgment_id = "jdg_" + secrets.token_hex(10)
        self._exec(
            "INSERT INTO judgments (judgment_id, client_id, case_id, policy_id, status, "
            "created_at, model, request_json) VALUES (?, ?, ?, ?, 'queued', ?, ?, ?)",
            (judgment_id, client_id, case["case_id"], policy_id, _now(), model, _json(case)),
        )
        return judgment_id

    def count_active(self, client_id):
        return self._query(
            "SELECT COUNT(*) AS n FROM judgments WHERE client_id = ? AND status IN ('queued','running')",
            (client_id,),
        )[0]["n"]

    def mark_running(self, judgment_id):
        self._exec(
            "UPDATE judgments SET status = 'running', started_at = ? WHERE judgment_id = ?",
            (_now(), judgment_id),
        )

    def mark_completed(self, judgment_id, decision, trace, model_calls, total_tokens):
        self._exec(
            "UPDATE judgments SET status = 'completed', finished_at = ?, decision_json = ?, "
            "trace_json = ?, model_calls = ?, total_tokens = ? WHERE judgment_id = ?",
            (_now(), _json(decision), _json(trace), model_calls, total_tokens, judgment_id),
        )

    def mark_failed(self, judgment_id, error):
        self._exec(
            "UPDATE judgments SET status = 'failed', finished_at = ?, error = ? WHERE judgment_id = ?",
            (_now(), error[:500], judgment_id),
        )

    def mark_interrupted(self):
        """Jobs left active by a restart will never finish; say so."""
        return self._exec(
            "UPDATE judgments SET status = 'failed', finished_at = ?, "
            "error = 'interrupted by a service restart; submit again' "
            "WHERE status IN ('queued','running')",
            (_now(),),
        )

    _SUMMARY = (
        "judgment_id, case_id, policy_id, status, created_at, started_at, finished_at, "
        "model, error, model_calls, total_tokens"
    )

    @staticmethod
    def _inflate(row, with_trace=False):
        decision = json.loads(row.pop("decision_json")) if row.get("decision_json") else None
        trace = row.pop("trace_json", None)
        row.pop("request_json", None)
        row["decision"] = decision
        if with_trace:
            row["trace"] = json.loads(trace) if trace else None
        return row

    def get_judgment(self, client_id, judgment_id, with_trace=False):
        rows = self._query(
            f"SELECT {self._SUMMARY}, decision_json, trace_json FROM judgments "
            "WHERE client_id = ? AND judgment_id = ?",
            (client_id, judgment_id),
        )
        return self._inflate(rows[0], with_trace) if rows else None

    def list_judgments(self, client_id, case_id=None, limit=50):
        sql = f"SELECT {self._SUMMARY}, decision_json FROM judgments WHERE client_id = ?"
        params = [client_id]
        if case_id is not None:
            sql += " AND case_id = ?"
            params.append(case_id)
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        return [self._inflate(row) for row in self._query(sql, params)]

    def list_cases(self, client_id):
        return self._query(
            "SELECT case_id, COUNT(*) AS judgments, MAX(created_at) AS last_submitted "
            "FROM judgments WHERE client_id = ? GROUP BY case_id ORDER BY last_submitted DESC",
            (client_id,),
        )

    def usage(self, client_id):
        totals = self._query(
            "SELECT COUNT(*) AS judgments, COALESCE(SUM(model_calls),0) AS model_calls, "
            "COALESCE(SUM(total_tokens),0) AS total_tokens, MIN(created_at) AS since "
            "FROM judgments WHERE client_id = ?",
            (client_id,),
        )[0]
        by_status = {
            row["status"]: row["n"]
            for row in self._query(
                "SELECT status, COUNT(*) AS n FROM judgments WHERE client_id = ? GROUP BY status",
                (client_id,),
            )
        }
        totals["by_status"] = by_status
        return totals
