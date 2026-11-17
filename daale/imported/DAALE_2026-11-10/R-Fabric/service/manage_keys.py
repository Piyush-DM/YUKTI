"""Manage clients and their keys. Local to the server; there is no HTTP admin.

    python -m service.manage_keys create-client "Acme Capital"
    python -m service.manage_keys issue-key cl_xxxx --label portal --out secrets/acme.key
    python -m service.manage_keys list
    python -m service.manage_keys revoke key_xxxx
    python -m service.manage_keys disable-client cl_xxxx

A key is shown once, when issued, and only its hash is kept. With --out it is
written to that file instead of the terminal, so it never lands in a
scrollback or a log.
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from .store import Store

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list")
    create = commands.add_parser("create-client")
    create.add_argument("name")
    issue = commands.add_parser("issue-key")
    issue.add_argument("client_id")
    issue.add_argument("--label")
    issue.add_argument("--out", help="write the key to this file instead of printing it")
    revoke = commands.add_parser("revoke")
    revoke.add_argument("key_id")
    disable = commands.add_parser("disable-client")
    disable.add_argument("client_id")
    args = parser.parse_args(argv)

    load_dotenv(ROOT / ".env")
    store = Store(os.getenv("YUKTI_DB_PATH") or ROOT / "data" / "yukti.db")
    try:
        return run(args, store)
    finally:
        store.close()


def run(args, store):
    if args.command == "create-client":
        print(store.create_client(args.name))
    elif args.command == "issue-key":
        try:
            key_id, key = store.issue_key(args.client_id, args.label)
        except KeyError as error:
            print(error, file=sys.stderr)
            return 1
        if args.out:
            out = Path(args.out)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(key + "\n", encoding="utf-8")
            print(f"{key_id} issued; key written to {out}")
        else:
            print(f"{key_id}\nKey (shown once, store it now):\n{key}")
    elif args.command == "revoke":
        if not store.revoke_key(args.key_id):
            print("No active key with that id", file=sys.stderr)
            return 1
        print(f"{args.key_id} revoked")
    elif args.command == "disable-client":
        if not store.disable_client(args.client_id):
            print("No active client with that id", file=sys.stderr)
            return 1
        print(f"{args.client_id} disabled; all its keys stop working")
    elif args.command == "list":
        for row in store.list_keys():
            state = "REVOKED" if row["revoked_at"] else "active"
            print(
                f"{row['key_id']}  {row['client_id']}  {row['client_name']:<24} "
                f"{row['key_prefix']}...  {row['label'] or '-':<12} {state}"
                f"  last used: {row['last_used_at'] or 'never'}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
