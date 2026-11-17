"""Replay: the policy decision of a completed run can be recomputed from the findings its trace recorded.

DECISION-005, condition 2. Model calls are not replayed; they are what was recorded.
"""

import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from daale.client import DaaleModelError
from daale.pipeline import DaalePipeline
from daale.replay import compare, main
from tests.test_integrity_rules import StubClient, approve_everything, load


class ReplayTests(unittest.TestCase):
    def setUp(self):
        self.case = load("cases/vendor_alpha.json")
        self.policy = load("policies/vendor_post_technical_dd_v0_1.json")
        sleeper = mock.patch("daale.pipeline.time.sleep")
        sleeper.start()
        self.addCleanup(sleeper.stop)

    def run_trace(self, **client_args):
        pipeline = DaalePipeline(client=StubClient(**client_args), model_by_kernel={"default": "m"})
        return pipeline.run(self.case, self.policy).trace

    def test_a_completed_run_replays_identically(self):
        self.assertEqual(compare(self.run_trace()), (True, []))

    def test_a_blocked_advance_replays_identically(self):
        trace = self.run_trace(rewrite=approve_everything, fail={"contrarian": DaaleModelError("boom")})
        self.assertEqual(trace["decision_packet"]["triggered_rule"]["rule_id"], "INCOMPLETE-RUN-ADVANCE-BLOCKED")
        self.assertEqual(compare(trace), (True, []))

    def test_a_contested_requirement_replays_identically(self):
        def one_dissenter(purpose, output):
            output = approve_everything(purpose, output)
            if purpose == "historian":
                for finding in output["findings"]:
                    if finding["finding_type"] == "REQUIREMENT_ASSESSMENT" and finding["target_id"] == "R3":
                        finding["status"] = "NOT_SATISFIED"
            return output

        trace = self.run_trace(rewrite=one_dissenter)
        self.assertEqual(trace["decision_packet"]["policy_state"], "HOLD")
        self.assertEqual(compare(trace), (True, []))

    def test_a_trace_replays_after_a_round_trip_through_json(self):
        trace = json.loads(json.dumps(self.run_trace()))
        self.assertEqual(compare(trace), (True, []))

    def test_changing_a_recorded_finding_is_caught(self):
        tampered = copy.deepcopy(self.run_trace())
        for finding in tampered["provisional_findings"]["analyst"]["findings"]:
            if finding["finding_type"] == "REQUIREMENT_ASSESSMENT" and finding["target_id"] == "R1":
                finding["status"] = "SATISFIED"
        replayable, differences = compare(tampered)
        self.assertTrue(replayable)
        self.assertIn("requirement_summary", differences)

    def test_a_refused_run_is_reported_as_not_replayable(self):
        trace = self.run_trace(fail={"adversary": DaaleModelError("boom")})
        self.assertEqual(compare(trace), (False, []))


class ReplayCommandTests(unittest.TestCase):
    def run_main(self, trace):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "trace.json"
            path.write_text(json.dumps(trace), encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = main([str(path)])
        return code, output.getvalue()

    def setUp(self):
        sleeper = mock.patch("daale.pipeline.time.sleep")
        sleeper.start()
        self.addCleanup(sleeper.stop)
        self.pipeline = DaalePipeline(client=StubClient(), model_by_kernel={"default": "m"})
        self.trace = self.pipeline.run(
            load("cases/vendor_alpha.json"), load("policies/vendor_post_technical_dd_v0_1.json")
        ).trace

    def test_it_says_ok_and_exits_zero_when_the_decision_matches(self):
        code, output = self.run_main(self.trace)
        self.assertEqual(code, 0)
        self.assertIn("REPLAY OK", output)

    def test_it_names_the_fields_that_differ_and_exits_one(self):
        tampered = copy.deepcopy(self.trace)
        tampered["decision_packet"]["policy_state"] = "ADVANCE"
        code, output = self.run_main(tampered)
        self.assertEqual(code, 1)
        self.assertIn("policy_state", output)

    def test_it_needs_exactly_one_argument(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main([]), 2)


if __name__ == "__main__":
    unittest.main()
