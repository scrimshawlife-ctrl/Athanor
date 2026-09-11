"""CLI entry (SHADOW stub)."""

from __future__ import annotations

import argparse
import json
import sys

from athanor import __version__


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="athanor", description="Athanor tradition furnace (SHADOW)")
    parser.add_argument("--version", action="store_true", help="Print version and exit")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("doctor", help="Environment / schema smoke")
    args = parser.parse_args(argv)

    if args.version or args.cmd is None:
        print(__version__)
        return 0

    if args.cmd == "doctor":
        payload = {
            "ok": True,
            "version": __version__,
            "lane": "SHADOW",
            "efficacy": None,
            "note": "Ingest/retrieve not shipped yet — Spec Kit spine only.",
        }
        json.dump(payload, sys.stdout, indent=2)
        print()
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
