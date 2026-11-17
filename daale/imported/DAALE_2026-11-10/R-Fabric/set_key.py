"""Put the model provider's API key into .env without it appearing on screen or in a command line.

    python set_key.py

Run it in a terminal window. The key is read with a hidden prompt and written to the
LLM_API_KEY line of .env (created from .env.example if there is none). It is never printed.
Run it again any time to replace the key.
"""

import getpass
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
KEY_NAME = "LLM_API_KEY"


def clean(raw):
    """Strip pasting debris from a key and refuse anything that cannot be one."""
    key = (raw or "").strip().strip("'\"").strip()
    if not key:
        raise ValueError("nothing was entered")
    if any(char.isspace() for char in key):
        raise ValueError("a key has no spaces or line breaks; paste only the key")
    if len(key) < 20:
        raise ValueError("that is too short to be an API key")
    return key


def set_key(env_path, key, template_path=None):
    """Write ``LLM_API_KEY=<key>`` into the file, replacing an existing line. Returns the path."""
    env_path = Path(env_path)
    # Read bytes: text mode would turn a Windows file's \r\n into \n before it can be
    # detected. utf-8-sig drops a BOM (Notepad adds one), which python-dotenv would
    # otherwise glue onto the first variable name.
    if env_path.exists():
        text = env_path.read_bytes().decode("utf-8-sig")
    elif template_path is not None and Path(template_path).exists():
        text = Path(template_path).read_bytes().decode("utf-8-sig")
    else:
        text = ""
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines()
    replacement = f"{KEY_NAME}={key}"

    active = [i for i, line in enumerate(lines) if line.lstrip().startswith(f"{KEY_NAME}=")]
    if active:
        for index in active:
            lines[index] = replacement
    else:
        commented = [
            i for i, line in enumerate(lines)
            if line.strip().replace(" ", "").startswith(f"#{KEY_NAME}=")
        ]
        if commented:
            lines[commented[0]] = replacement
        else:
            lines.append(replacement)

    descriptor, temporary = tempfile.mkstemp(dir=env_path.parent, prefix=".env.", suffix=".tmp")
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(newline.join(lines) + newline)
        os.replace(temporary, env_path)
    except BaseException:
        if os.path.exists(temporary):
            os.unlink(temporary)
        raise
    return env_path


def configured_provider(env_path):
    """The DAALE_LIVE_PROVIDER named in the file, defaulting like the engine does."""
    try:
        for line in Path(env_path).read_text(encoding="utf-8").splitlines():
            name, separator, value = line.partition("=")
            if separator and name.strip() == "DAALE_LIVE_PROVIDER":
                return value.strip().strip("'\"").lower()
    except OSError:
        pass
    return "openrouter"


def main():
    if not sys.stdin.isatty():
        print("Run this in a terminal window: input cannot be hidden here, so nothing was asked.")
        return 2
    try:
        key = clean(getpass.getpass("Paste the API key (nothing will show), then press Enter: "))
    except ValueError as error:
        print(f"Not saved: {error}.")
        return 1

    path = set_key(ROOT / ".env", key, ROOT / ".env.example")
    print(f"Saved {KEY_NAME} ({len(key)} characters) in {path}. The key itself was not printed.")
    provider = configured_provider(path)
    if provider != "generic":
        print(f"Note: DAALE_LIVE_PROVIDER is '{provider}'; {KEY_NAME} is only used when it is 'generic'.")
    print("Next:  python preflight.py   then   python check_provider.py --list")
    return 0


if __name__ == "__main__":
    sys.exit(main())
