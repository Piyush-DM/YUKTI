"""A daily request budget that survives restarts.

A key capped at, say, 20 requests a day cannot afford a judgment that starts and
runs out half way: the requests it spent are gone and it produced nothing. This
counts every request the engine sends (retries included, since the provider
counts them too), stores the count on disk, and lets the pipeline refuse to
start a judgment it cannot finish.

The day rolls over at midnight Pacific time, which is when Google resets its
daily quotas. If the timezone database is unavailable, fixed UTC-8 is used.

    python -m daale.budget status [--model MODEL]
    python -m daale.budget set 17 [--model MODEL]   # requests already used today

Budgets are per model; MODEL defaults to DAALE_DEFAULT_MODEL.
"""

import argparse
import json
import os
import sys
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parents[1] / "data" / "request_budget.json"


class BudgetExhausted(RuntimeError):
    """The daily request budget is used up. Retrying before the reset is pointless."""

    quota_exhausted = True


def _pacific(moment):
    try:
        from zoneinfo import ZoneInfo

        return moment.astimezone(ZoneInfo("America/Los_Angeles"))
    except Exception:  # noqa: BLE001 - no tz database on this machine
        return moment.astimezone(timezone(timedelta(hours=-8)))


class RequestBudget:
    def __init__(self, daily_limit, path=None, clock=lambda: datetime.now(timezone.utc)):
        if daily_limit < 1:
            raise ValueError("daily request limit must be at least 1")
        self.daily_limit = daily_limit
        self.path = Path(path) if path else DEFAULT_PATH
        self._clock = clock
        self._lock = threading.Lock()

    # -- state ----------------------------------------------------------------

    def _today(self):
        return _pacific(self._clock()).date().isoformat()

    def _read(self):
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if data.get("date") == self._today():
                return int(data.get("count", 0))
        except (FileNotFoundError, ValueError):
            pass
        return 0

    def _write(self, count):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix(".tmp")
        temp.write_text(json.dumps({"date": self._today(), "count": count}), encoding="utf-8")
        os.replace(temp, self.path)

    # -- use ------------------------------------------------------------------

    def used(self):
        with self._lock:
            return self._read()

    def remaining(self):
        return max(0, self.daily_limit - self.used())

    def seconds_until_reset(self):
        now = _pacific(self._clock())
        midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        return int((midnight - now).total_seconds()) + 1

    def _exhausted(self):
        return BudgetExhausted(
            f"daily request budget of {self.daily_limit} is used up; "
            f"it resets in about {self.seconds_until_reset() // 3600}h "
            f"{self.seconds_until_reset() % 3600 // 60}m (midnight Pacific)"
        )

    def check(self):
        with self._lock:
            if self._read() >= self.daily_limit:
                raise self._exhausted()

    def take(self):
        """Count one request, or raise if there is none left."""
        with self._lock:
            count = self._read()
            if count >= self.daily_limit:
                raise self._exhausted()
            self._write(count + 1)

    def set_used(self, count):
        with self._lock:
            self._write(max(0, count))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    status = commands.add_parser("status")
    status.add_argument("--model")
    setter = commands.add_parser("set")
    setter.add_argument("used", type=int, help="requests already used today")
    setter.add_argument("--model")
    args = parser.parse_args(argv)

    try:
        from dotenv import load_dotenv

        load_dotenv(DEFAULT_PATH.parents[1] / ".env")
    except ImportError:
        pass
    from .providers import pacers_from_env

    model = args.model or os.getenv("DAALE_DEFAULT_MODEL", "").strip()
    pacer = pacers_from_env(os.environ).for_model(model) if model else None
    budget = pacer.budget if pacer is not None else None
    if budget is None:
        print(f"No daily limit is configured for model {model!r} (see LLM_LIMITS in .env)", file=sys.stderr)
        return 1
    if args.command == "set":
        budget.set_used(args.used)
    print(
        f"{model}: used {budget.used()} of {budget.daily_limit} today (Pacific); "
        f"{budget.remaining()} left; resets in {budget.seconds_until_reset() // 3600}h "
        f"{budget.seconds_until_reset() % 3600 // 60}m"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
