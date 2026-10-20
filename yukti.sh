#!/bin/sh
# Start YUKTI on macOS or Linux.
#
#   ./yukti.sh
#
# Finds a Python for you: the repository's own virtual environment if one has
# been created, then python3, then python.
set -e
cd "$(dirname "$0")"

if [ -x ".venv/bin/python" ]; then
    exec .venv/bin/python yukti.py "$@"
fi

if command -v python3 >/dev/null 2>&1; then
    exec python3 yukti.py "$@"
fi

exec python yukti.py "$@"
