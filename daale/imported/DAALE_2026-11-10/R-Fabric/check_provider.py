"""Check the configured provider with at most two small requests. Prints no secrets.

    python check_provider.py            # list Gemma model ids, then one tiny JSON call
    python check_provider.py --list     # only list models, make no completion

Reads the same `.env` as run_daale.py. Works for DAALE_LIVE_PROVIDER=openrouter
and generic. The completion uses DAALE_DEFAULT_MODEL and a one-line prompt;
it sends no case material.
"""

import argparse
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent


def endpoints():
    provider = os.getenv("DAALE_LIVE_PROVIDER", "openrouter").strip().lower()
    if provider == "openrouter":
        return provider, "https://openrouter.ai/api/v1", os.getenv("OPENROUTER_API_KEY", "")
    if provider == "generic":
        return provider, (os.getenv("LLM_BASE_URL") or "").rstrip("/"), os.getenv("LLM_API_KEY", "")
    sys.exit(f"check_provider supports openrouter and generic, not {provider!r}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true", help="only list models")
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    provider, base, key = endpoints()
    if not base:
        sys.exit("No base URL: set LLM_BASE_URL in .env")
    if not key:
        sys.exit("No API key in .env for this provider")
    if not base.startswith("https://") and "localhost" not in base and "127.0.0.1" not in base:
        sys.exit("Refusing to send a key over plain http")

    headers = {"Authorization": f"Bearer {key}"}
    print(f"provider: {provider}  endpoint: {base}")

    response = requests.get(f"{base}/models", headers=headers, timeout=60)
    if not response.ok:
        print(f"model list: HTTP {response.status_code} {response.text[:300]}")
    else:
        data = response.json()
        items = data.get("data") or data.get("models") or []
        ids = sorted(str(item.get("id") or item.get("name")) for item in items)
        gemma = [i for i in ids if "gemma" in i.lower()]
        print(f"model list: {len(ids)} models, {len(gemma)} mention gemma")
        for model_id in gemma:
            print(f"  {model_id}")

    if args.list:
        return 0

    model = os.getenv("DAALE_DEFAULT_MODEL", "").strip()
    if not model:
        sys.exit("Set DAALE_DEFAULT_MODEL in .env (use an id printed above) to test a completion")

    payload = {
        "model": model,
        "temperature": 0,
        "max_tokens": 60,
        "messages": [{"role": "user", "content": 'Reply with exactly this JSON and nothing else: {"ok": true}'}],
    }
    response = requests.post(f"{base}/chat/completions", headers=headers, json=payload, timeout=120)
    print(f"completion: HTTP {response.status_code}")
    if response.ok:
        body = response.json()
        print("  served model:", body.get("model"))
        print("  usage:", body.get("usage"))
        print("  reply:", (body["choices"][0]["message"].get("content") or "")[:200])
    else:
        print("  ", response.text[:400])
    return 0 if response.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
