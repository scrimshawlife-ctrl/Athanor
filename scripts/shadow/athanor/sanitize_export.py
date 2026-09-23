#!/usr/bin/env python3
"""Sanitize Athanor atoms for offline / companion export (SHADOW).

Dataset-contract rules:
  - text_excerpt ≤ 500 characters
  - required fields: atom_id, family_id, license, source_url, epistemic,
    content_hash, reception_layer
  - drop licenses in {unknown, hold, closed-initiatory, all-rights}
  - no efficacy column
  - no full-page dumps (excerpt capped)

Fail-closed: does NOT upload to Hub. Hub requires ALLOW_HUB (absent).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

EXCERPT_CAP = 500
DROP_LICENSE_EXACT = frozenset(
    {"unknown", "hold", "closed-initiatory", "all-rights"}
)
DROP_LICENSE_SUBSTR = ("closed-initiatory", "all-rights")
REQUIRED = (
    "atom_id",
    "family_id",
    "license",
    "source_url",
    "epistemic",
    "content_hash",
    "reception_layer",
)


def _license_drop(license_val: str | None) -> bool:
    lic = (license_val or "").strip().lower()
    if not lic:
        return True
    if lic in DROP_LICENSE_EXACT:
        return True
    if lic.startswith("hold"):
        return True
    for sub in DROP_LICENSE_SUBSTR:
        if sub in lic:
            return True
    return bool(lic == "unknown" or lic.startswith("unknown"))


def _excerpt(text: str | None, cap: int = EXCERPT_CAP) -> str:
    raw = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    # collapse extreme whitespace but keep readable prose
    collapsed = " ".join(raw.split())
    if len(collapsed) <= cap:
        return collapsed
    return collapsed[: cap - 1].rstrip() + "…"


def sanitize_row(atom: dict) -> dict | None:
    if _license_drop(atom.get("license")):
        return None
    reception = atom.get("reception_layer")
    if not reception:
        # legacy harvest rows may omit; contract requires the field
        reception = "unspecified"
    text = atom.get("text")
    if text is None:
        return None
    # drop seal binaries / non-text
    if atom.get("type") in ("image", "seal", "binary"):
        return None
    row = {
        "atom_id": atom["atom_id"],
        "family_id": atom["family_id"],
        "license": atom.get("license"),
        "source_url": atom.get("source_url"),
        "epistemic": atom.get("epistemic"),
        "content_hash": atom.get("content_hash"),
        "reception_layer": reception,
        "text_excerpt": _excerpt(text),
    }
    for k in REQUIRED:
        if row.get(k) in (None, ""):
            return None
    # never include efficacy
    assert "efficacy" not in row
    return row


def load_id_filter(path: Path | None) -> set[str] | None:
    if path is None:
        return None
    ids: set[str] = set()
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            aid = obj.get("atom_id")
            if aid:
                ids.add(aid)
    return ids


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--atoms",
        type=Path,
        default=Path.home() / ".athanor/corpus/atoms.jsonl",
        help="Source of truth atoms JSONL (not committed to git)",
    )
    p.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Output sanitized JSONL path",
    )
    p.add_argument(
        "--only-ids-from",
        type=Path,
        default=None,
        help="Optional JSONL with atom_id fields to include (e.g. gold.jsonl)",
    )
    p.add_argument(
        "--epistemic",
        default=None,
        help="Optional epistemic filter (e.g. OBSERVED)",
    )
    args = p.parse_args(argv)

    if not args.atoms.is_file():
        print(f"FAIL: atoms not found: {args.atoms}", file=sys.stderr)
        return 2

    id_filter = load_id_filter(args.only_ids_from)
    kept = 0
    dropped_license = 0
    dropped_filter = 0
    dropped_other = 0
    args.out.parent.mkdir(parents=True, exist_ok=True)

    with args.atoms.open(encoding="utf-8") as src, args.out.open(
        "w", encoding="utf-8"
    ) as dst:
        for line in src:
            line = line.strip()
            if not line:
                continue
            atom = json.loads(line)
            if id_filter is not None and atom.get("atom_id") not in id_filter:
                dropped_filter += 1
                continue
            if args.epistemic and atom.get("epistemic") != args.epistemic:
                dropped_filter += 1
                continue
            if _license_drop(atom.get("license")):
                dropped_license += 1
                continue
            row = sanitize_row(atom)
            if row is None:
                dropped_other += 1
                continue
            dst.write(json.dumps(row, ensure_ascii=False) + "\n")
            kept += 1

    digest = hashlib.sha256(args.out.read_bytes()).hexdigest()
    summary = {
        "out": str(args.out),
        "kept": kept,
        "dropped_license": dropped_license,
        "dropped_filter": dropped_filter,
        "dropped_other": dropped_other,
        "excerpt_cap": EXCERPT_CAP,
        "sha256": digest,
        "hub": "NOT_UPLOADED",
        "allow_hub": False,
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
