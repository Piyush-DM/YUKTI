import contextlib
import io
import json
import os
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

from fastapi.testclient import TestClient

from daale.client import CompletionRecord, FixtureClient
from daale.pipeline import BASE_KERNELS
from service import manage_keys
from service.app import create_app, load_policies
from service.security import KEY_PREFIX, RateLimiter, hash_key
from service.store import Store

ROOT = Path(__file__).resolve().parents[1]
REAL_SLEEP = time.sleep


def load_json(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def fixture_client():
    outputs = {k.lower(): load_json(f"fixtures/{k.lower()}_output.json") for k in BASE_KERNELS}
    outputs["adversary"] = load_json("fixtures/adversary_output.json")
    return FixtureClient(outputs)


class BlockingClient:
    """Holds every call until released, so a job stays active."""

    def __init__(self):
        self.release = threading.Event()
        self.inner = fixture_client()

    def complete_json(self, purpose, model, messages, schema):
        self.release.wait(10)
        return self.inner.complete_json(purpose, model, messages, schema)


class ServiceTestCase(unittest.TestCase):
    policy_id = "VENDOR-POST-TECH-DD"

    def make(self, client=None, **kwargs):
        self.store = kwargs.pop("store", None) or Store(":memory:")
        app = create_app(
            store=self.store,
            client=client or fixture_client(),
            model_by_kernel={"default": "test-model"},
            policies=load_policies(ROOT / "policies"),
            provider="test",
            **kwargs,
        )
        self.http = TestClient(app)
        self.addCleanup(app.state.executor.shutdown, wait=True, cancel_futures=True)
        return self.http

    def client_with_key(self, name="Acme"):
        client_id = self.store.create_client(name)
        key_id, key = self.store.issue_key(client_id, "portal")
        return client_id, key_id, key

    @staticmethod
    def auth(key):
        return {"Authorization": f"Bearer {key}"}

    def submit(self, key, case=None):
        case = case or load_json("cases/vendor_alpha.json")
        return self.http.post(
            "/v1/judgments", json={"policy_id": self.policy_id, "case": case}, headers=self.auth(key)
        )

    def wait_done(self, key, judgment_id, timeout=10):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            body = self.http.get(f"/v1/judgments/{judgment_id}", headers=self.auth(key)).json()
            if body["status"] in ("completed", "failed"):
                return body
            REAL_SLEEP(0.02)
        self.fail("judgment did not finish")


class AuthenticationTests(ServiceTestCase):
    def setUp(self):
        self.make()
        _, self.key_id, self.key = self.client_with_key()

    def test_health_is_open_and_exposes_no_secret(self):
        body = self.http.get("/v1/health").json()
        self.assertEqual(body["status"], "ok")
        self.assertIn(self.policy_id, body["policies"])
        self.assertNotIn(self.key, json.dumps(body))

    def test_every_other_route_requires_a_key(self):
        for path in ("/v1/judgments", "/v1/cases", "/v1/usage", "/v1/judgments/jdg_x"):
            self.assertEqual(self.http.get(path).status_code, 401, path)
        self.assertEqual(self.http.post("/v1/judgments", json={}).status_code, 401)

    def test_wrong_and_malformed_keys_are_refused(self):
        self.assertEqual(self.http.get("/v1/usage", headers=self.auth(KEY_PREFIX + "nope")).status_code, 401)
        self.assertEqual(self.http.get("/v1/usage", headers={"Authorization": self.key}).status_code, 401)
        self.assertEqual(self.http.get("/v1/usage", headers=self.auth(self.key)).status_code, 200)

    def test_revoking_a_key_stops_it_immediately(self):
        self.assertEqual(self.http.get("/v1/usage", headers=self.auth(self.key)).status_code, 200)
        self.store.revoke_key(self.key_id)
        self.assertEqual(self.http.get("/v1/usage", headers=self.auth(self.key)).status_code, 401)

    def test_disabling_a_client_stops_all_its_keys(self):
        client_id, _, key = self.client_with_key("Other")
        _, second = self.store.issue_key(client_id, "second")
        self.store.disable_client(client_id)
        for each in (key, second):
            self.assertEqual(self.http.get("/v1/usage", headers=self.auth(each)).status_code, 401)

    def test_only_a_hash_of_the_key_is_stored(self):
        dump = json.dumps(self.store._query("SELECT * FROM api_keys"))
        self.assertNotIn(self.key, dump)
        self.assertIn(hash_key(self.key), dump)
        self.assertTrue(self.key.startswith(KEY_PREFIX))

    def test_two_keys_are_independent(self):
        client_id, key_id, first = self.client_with_key("Two")
        _, second = self.store.issue_key(client_id, "second")
        self.assertNotEqual(first, second)
        self.store.revoke_key(key_id)
        self.assertEqual(self.http.get("/v1/usage", headers=self.auth(first)).status_code, 401)
        self.assertEqual(self.http.get("/v1/usage", headers=self.auth(second)).status_code, 200)


class JudgmentTests(ServiceTestCase):
    def setUp(self):
        self.make()
        _, _, self.key = self.client_with_key()

    def test_submit_poll_and_read_the_decision(self):
        response = self.submit(self.key)
        self.assertEqual(response.status_code, 202)
        body = self.wait_done(self.key, response.json()["judgment_id"])
        self.assertEqual(body["status"], "completed")
        self.assertEqual(body["decision"]["policy_state"], "REJECT")
        self.assertFalse(body["degraded"])
        self.assertEqual(body["decision"]["execution_integrity"]["adversary"], "ran")

    def test_audit_record_is_available_once_complete(self):
        jid = self.submit(self.key).json()["judgment_id"]
        self.wait_done(self.key, jid)
        audit = self.http.get(f"/v1/judgments/{jid}/audit", headers=self.auth(self.key)).json()
        self.assertIn("model_calls", audit["trace"])
        self.assertIn("gap_report", audit["trace"])
        self.assertEqual(audit["trace"]["case"]["case_id"], "DD-001")

    def test_usage_counts_calls_and_judgments(self):
        jid = self.submit(self.key).json()["judgment_id"]
        self.wait_done(self.key, jid)
        usage = self.http.get("/v1/usage", headers=self.auth(self.key)).json()
        self.assertEqual(usage["judgments"], 1)
        self.assertEqual(usage["model_calls"], 7)
        self.assertEqual(usage["by_status"], {"completed": 1})

    def test_cases_group_judgments_by_case_id(self):
        first = self.submit(self.key).json()["judgment_id"]
        self.wait_done(self.key, first)
        second = self.submit(self.key).json()["judgment_id"]
        self.wait_done(self.key, second)
        cases = self.http.get("/v1/cases", headers=self.auth(self.key)).json()["cases"]
        self.assertEqual([(c["case_id"], c["judgments"]) for c in cases], [("DD-001", 2)])
        detail = self.http.get("/v1/cases/DD-001", headers=self.auth(self.key)).json()
        self.assertEqual({j["judgment_id"] for j in detail["judgments"]}, {first, second})

    def test_material_sent_inline_becomes_a_case(self):
        material = {
            "case_id": "INLINE-1",
            "decision_stage": "post_technical_due_diligence_approval",
            "decision_question": "Approve the vendor?",
            "claims": [{"claim_id": "C1", "text": "Meets baseline."}, {"claim_id": "C2", "text": "Has support."}],
            "documents": [
                {"text": "Audited revenue grew.", "title": "Financials"},
                {"text": "No SOC 2 report was supplied.", "title": "Security"},
                {"text": "Support is available around the clock.", "title": "Support"},
            ],
        }
        response = self.http.post(
            "/v1/judgments",
            json={"policy_id": self.policy_id, "material": material},
            headers=self.auth(self.key),
        )
        self.assertEqual(response.status_code, 202, response.text)
        body = self.wait_done(self.key, response.json()["judgment_id"])
        self.assertEqual(body["status"], "completed")
        audit = self.http.get(
            f"/v1/judgments/{body['judgment_id']}/audit", headers=self.auth(self.key)
        ).json()["trace"]
        self.assertEqual([e["text"] for e in audit["case"]["evidence"]][1], "No SOC 2 report was supplied.")
        self.assertEqual(len(audit["case"]["evidence"][0]["source"]["content_hash"]), 64)

    def test_bad_requests_are_refused_before_any_model_call(self):
        case = load_json("cases/vendor_alpha.json")
        cases = [
            ({"policy_id": "NOPE", "case": case}, "Unknown policy_id"),
            ({"policy_id": self.policy_id}, "exactly one"),
            ({"policy_id": self.policy_id, "case": case, "material": {}}, "exactly one"),
            ({"policy_id": self.policy_id, "case": {**case, "decision_stage": "other"}}, "decision_stage"),
            ({"policy_id": self.policy_id, "surprise": 1, "case": case}, None),
        ]
        for payload, expect in cases:
            response = self.http.post("/v1/judgments", json=payload, headers=self.auth(self.key))
            self.assertEqual(response.status_code, 422, payload)
            if expect:
                self.assertIn(expect, response.text)
        self.assertEqual(self.http.get("/v1/usage", headers=self.auth(self.key)).json()["judgments"], 0)

    def test_a_client_cannot_make_the_server_read_a_file(self):
        material = {
            "case_id": "X", "decision_stage": "post_technical_due_diligence_approval",
            "decision_question": "q", "claims": [{"claim_id": "C1", "text": "t"}],
            "documents": [{"path": "../../../../etc/passwd"}],
        }
        response = self.http.post(
            "/v1/judgments", json={"policy_id": self.policy_id, "material": material},
            headers=self.auth(self.key),
        )
        self.assertEqual(response.status_code, 422)
        self.assertIn("file paths are not accepted", response.text)


class IsolationTests(ServiceTestCase):
    def setUp(self):
        self.make()
        _, _, self.alice = self.client_with_key("Alice")
        _, _, self.bob = self.client_with_key("Bob")
        self.jid = self.submit(self.alice).json()["judgment_id"]
        self.wait_done(self.alice, self.jid)

    def test_another_client_cannot_see_the_judgment_or_its_audit(self):
        for path in (f"/v1/judgments/{self.jid}", f"/v1/judgments/{self.jid}/audit", "/v1/cases/DD-001"):
            self.assertEqual(self.http.get(path, headers=self.auth(self.bob)).status_code, 404, path)
            self.assertEqual(self.http.get(path, headers=self.auth(self.alice)).status_code, 200, path)

    def test_another_clients_lists_and_usage_are_empty(self):
        self.assertEqual(self.http.get("/v1/judgments", headers=self.auth(self.bob)).json()["judgments"], [])
        self.assertEqual(self.http.get("/v1/cases", headers=self.auth(self.bob)).json()["cases"], [])
        usage = self.http.get("/v1/usage", headers=self.auth(self.bob)).json()
        self.assertEqual((usage["judgments"], usage["total_tokens"]), (0, 0))

    def test_the_same_case_id_does_not_collide_across_clients(self):
        jid_bob = self.submit(self.bob).json()["judgment_id"]
        self.wait_done(self.bob, jid_bob)
        mine = self.http.get("/v1/cases/DD-001", headers=self.auth(self.bob)).json()["judgments"]
        self.assertEqual([j["judgment_id"] for j in mine], [jid_bob])


class LimitTests(ServiceTestCase):
    def test_request_rate_limit_returns_429_with_retry_after(self):
        self.make(rate_per_minute=2)
        _, _, key = self.client_with_key()
        self.assertEqual(self.http.get("/v1/usage", headers=self.auth(key)).status_code, 200)
        self.assertEqual(self.http.get("/v1/usage", headers=self.auth(key)).status_code, 200)
        limited = self.http.get("/v1/usage", headers=self.auth(key))
        self.assertEqual(limited.status_code, 429)
        self.assertGreater(int(limited.headers["Retry-After"]), 0)

    def test_rate_limit_is_per_key(self):
        self.make(rate_per_minute=1)
        _, _, first = self.client_with_key("A")
        _, _, second = self.client_with_key("B")
        self.assertEqual(self.http.get("/v1/usage", headers=self.auth(first)).status_code, 200)
        self.assertEqual(self.http.get("/v1/usage", headers=self.auth(first)).status_code, 429)
        self.assertEqual(self.http.get("/v1/usage", headers=self.auth(second)).status_code, 200)

    def test_limiter_window_expires(self):
        now = [0.0]
        limiter = RateLimiter(1, clock=lambda: now[0])
        self.assertTrue(limiter.allow("k")[0])
        self.assertFalse(limiter.allow("k")[0])
        now[0] = 61
        self.assertTrue(limiter.allow("k")[0])

    def test_active_judgments_per_client_are_capped(self):
        blocker = BlockingClient()
        self.addCleanup(blocker.release.set)
        self.make(client=blocker, max_active_per_client=1)
        _, _, key = self.client_with_key()
        self.assertEqual(self.submit(key).status_code, 202)
        second = self.submit(key)
        self.assertEqual(second.status_code, 429)
        self.assertIn("Retry-After", second.headers)
        blocker.release.set()

    def test_a_judgment_the_daily_model_budget_cannot_finish_is_refused_up_front(self):
        class Budgeted:
            def requests_remaining(self, model=None):
                return 3

            def budget_reset_seconds(self, model=None):
                return 7200

        self.make(client=Budgeted())
        _, _, key = self.client_with_key()
        response = self.submit(key)
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.headers["Retry-After"], "7200")
        self.assertIn("budget", response.text)
        self.assertEqual(self.http.get("/v1/usage", headers=self.auth(key)).json()["judgments"], 0)

    def test_oversized_bodies_are_refused(self):
        self.make(max_body_bytes=200)
        _, _, key = self.client_with_key()
        self.assertEqual(self.submit(key).status_code, 413)


class PersistenceTests(ServiceTestCase):
    def test_results_survive_a_restart_and_interrupted_jobs_are_marked(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "yukti.db"
            self.make(store=Store(path))
            client_id, _, key = self.client_with_key()
            done = self.submit(key).json()["judgment_id"]
            self.wait_done(key, done)
            stuck = self.store.create_judgment(
                client_id, load_json("cases/vendor_alpha.json"), self.policy_id, "m"
            )
            self.store.mark_running(stuck)
            self.store._db.close()

            self.make(store=Store(path))
            self.assertEqual(self.wait_done(key, done)["decision"]["policy_state"], "REJECT")
            interrupted = self.http.get(f"/v1/judgments/{stuck}", headers=self.auth(key)).json()
            self.assertEqual(interrupted["status"], "failed")
            self.assertIn("restart", interrupted["error"])
            self.store._db.close()


class KeyCommandTests(unittest.TestCase):
    def run_cli(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = manage_keys.main(list(argv))
        return code, out.getvalue()

    def test_issue_to_file_keeps_the_key_out_of_the_terminal(self):
        with tempfile.TemporaryDirectory() as directory:
            with mock.patch.dict(os.environ, {"YUKTI_DB_PATH": str(Path(directory) / "k.db")}):
                _, client_id = self.run_cli("create-client", "Acme")
                client_id = client_id.strip()
                out_file = Path(directory) / "secrets" / "acme.key"
                _, printed = self.run_cli("issue-key", client_id, "--label", "portal", "--out", str(out_file))
                key = out_file.read_text(encoding="utf-8").strip()
                self.assertTrue(key.startswith(KEY_PREFIX))
                self.assertNotIn(key, printed)
                _, listing = self.run_cli("list")
                self.assertNotIn(key, listing)
                self.assertIn("active", listing)
                key_id = printed.split()[0]
                code, _ = self.run_cli("revoke", key_id)
                self.assertEqual(code, 0)
                self.assertIn("REVOKED", self.run_cli("list")[1])
                self.assertEqual(self.run_cli("revoke", key_id)[0], 1)


if __name__ == "__main__":
    unittest.main()
