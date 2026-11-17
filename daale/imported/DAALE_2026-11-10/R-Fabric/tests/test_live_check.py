"""The live check must pass only on six of six, and must say why when it does not.

These tests run offline against stubbed clients. They cover the logic that decides pass or fail, so a
checker that always said PASS could not hide behind the opt-in live test.
"""

import contextlib
import io
import tempfile
import unittest
from unittest import mock

import live_check
from daale.client import DaaleModelError
from daale.pipeline import BASE_KERNELS
from tests.test_integrity_rules import StubClient, load


class CheckTests(unittest.TestCase):
    def setUp(self):
        sleeper = mock.patch("daale.pipeline.time.sleep")
        sleeper.start()
        self.addCleanup(sleeper.stop)
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.runs_dir = folder.name

    def run_check(self, base_only=False, **client_args):
        return live_check.check(
            base_only=base_only,
            client=StubClient(**client_args),
            native_json_schema=False,
            model_by_kernel={"default": "m"},
            case=load("cases/vendor_alpha.json"),
            policy=load("policies/vendor_post_technical_dd_v0_1.json"),
            runs_dir=self.runs_dir,
        )

    def test_six_of_six_and_a_clean_adversary_pass(self):
        report = self.run_check()
        self.assertTrue(report.ok, report.problems)
        self.assertEqual(report.succeeded, len(BASE_KERNELS))
        self.assertEqual(report.adversary, "ran")
        self.assertIn("recomputed identically", report.replay)
        self.assertIn("RESULT: PASS", report.render())
        self.assertTrue(report.trace_path)

    def test_every_kernel_is_listed_with_its_attempts(self):
        report = self.run_check()
        self.assertEqual([row.kernel for row in report.rows], BASE_KERNELS)
        self.assertTrue(all(row.attempts == 1 for row in report.rows))
        self.assertTrue(all(row.tokens == 10 for row in report.rows))

    def test_one_failed_kernel_fails_the_check_and_names_it(self):
        report = self.run_check(fail={"contrarian": DaaleModelError("model timed out")})
        self.assertFalse(report.ok)
        self.assertEqual(report.succeeded, len(BASE_KERNELS) - 1)
        failed = [row for row in report.rows if not row.ok]
        self.assertEqual([row.kernel for row in failed], ["CONTRARIAN"])
        self.assertGreater(failed[0].attempts, 1)
        self.assertIn("CONTRARIAN", report.problems[0])
        self.assertIn("model timed out", report.problems[0])
        self.assertIn("RESULT: FAIL", report.render())

    def test_a_failed_adversary_fails_the_check_even_with_six_of_six(self):
        report = self.run_check(fail={"adversary": DaaleModelError("boom")})
        self.assertFalse(report.ok)
        self.assertEqual(report.succeeded, len(BASE_KERNELS))
        self.assertTrue(any("adversary did not run" in problem for problem in report.problems))

    def test_a_decision_that_does_not_replay_fails_the_check(self):
        with mock.patch("live_check.compare", return_value=(True, ["policy_state"])):
            report = self.run_check()
        self.assertFalse(report.ok)
        self.assertIn("DIFFERS in policy_state", report.render())

    def test_the_base_only_check_needs_no_adversary(self):
        report = self.run_check(base_only=True)
        self.assertTrue(report.ok, report.problems)
        self.assertEqual(report.succeeded, len(BASE_KERNELS))
        self.assertEqual(report.trace_path, "")

    def test_the_base_only_check_fails_on_a_failed_kernel(self):
        report = self.run_check(base_only=True, fail={"outsider": DaaleModelError("boom")})
        self.assertFalse(report.ok)
        self.assertEqual([row.kernel for row in report.rows if not row.ok], ["OUTSIDER"])


class CommandTests(unittest.TestCase):
    def run_main(self, report=None, error=None, arguments=()):
        output = io.StringIO()
        with mock.patch("live_check.check", return_value=report, side_effect=error) as check, \
                mock.patch("live_check.load_dotenv"), contextlib.redirect_stdout(output):
            code = live_check.main(list(arguments))
        return code, output.getvalue(), check

    def test_exit_zero_on_a_pass(self):
        rows = [live_check.Row(kernel, True, 1, 10) for kernel in BASE_KERNELS]
        code, output, _ = self.run_main(live_check.Report(rows=rows))
        self.assertEqual(code, 0)
        self.assertIn("PASS", output)

    def test_exit_one_on_a_failure(self):
        rows = [live_check.Row(kernel, kernel != "OUTSIDER", 1) for kernel in BASE_KERNELS]
        report = live_check.Report(rows=rows, problems=["1 of 6 base kernels failed. OUTSIDER: boom"])
        code, output, _ = self.run_main(report)
        self.assertEqual(code, 1)
        self.assertIn("FAIL", output)

    def test_exit_two_when_it_could_not_run(self):
        code, output, _ = self.run_main(error=DaaleModelError("LLM_API_KEY is required"))
        self.assertEqual(code, 2)
        self.assertIn("could not run", output)

    def test_base_only_is_passed_through(self):
        rows = [live_check.Row(kernel, True, 1) for kernel in BASE_KERNELS]
        _, _, check = self.run_main(live_check.Report(rows=rows), arguments=["--base-only"])
        check.assert_called_once_with(base_only=True)


if __name__ == "__main__":
    unittest.main()
