"""Run run_daale.py with a profile laid over .env.

    python run_profile.py profiles/test_google.env --live --case cases/vendor_gamma.json

A profile holds only non-secret settings (which models run which kernels, fallbacks). The key stays in .env,
which run_daale.py still loads; anything a profile sets wins over .env. Everything after the profile path is
passed to run_daale.py unchanged.
"""

import os
import sys
from pathlib import Path

from dotenv import dotenv_values

if len(sys.argv) < 2:
    raise SystemExit(__doc__)

profile = Path(sys.argv[1])
if not profile.is_file():
    raise SystemExit(f"profile not found: {profile}")
for name, value in dotenv_values(profile).items():
    if any(word in name.upper() for word in ("KEY", "TOKEN", "SECRET", "PASSWORD")) and "MAX" not in name.upper():
        raise SystemExit(f"{name}: a profile must not hold secrets; keep them in .env")
    os.environ[name] = value or ""

sys.argv = ["run_daale.py", *sys.argv[2:]]
import run_daale  # noqa: E402  (after the environment is set)

raise SystemExit(run_daale.main())
