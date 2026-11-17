"""Opt-in live test: all six base kernels succeed against the real model.

Skipped unless DAALE_LIVE=1, because it makes real model calls and takes several minutes:

    $env:DAALE_LIVE = '1'; python -m pytest tests/test_live_six_kernels.py -q

It needs the key in .env. For the full judgment including the adversary, run `python live_check.py`.
"""

import os
import unittest

from dotenv import load_dotenv

import live_check


@unittest.skipUnless(os.environ.get("DAALE_LIVE") == "1", "set DAALE_LIVE=1 to make real model calls")
class LiveSixKernelTests(unittest.TestCase):
    def test_all_six_base_kernels_succeed(self):
        load_dotenv(live_check.ROOT / ".env")
        report = live_check.check(base_only=True)
        self.assertTrue(report.ok, "\n" + report.render())
        self.assertEqual(report.succeeded, 6)


if __name__ == "__main__":
    unittest.main()
