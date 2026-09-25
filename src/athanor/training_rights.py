"""Audit candidate-source rights claims for training preflight; read-only and non-authorizing."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

from athanor.readiness import MAX_BYTES, _json

_DENY_LICENSES = {"", "unknown", "hold", "denied", "not_computable", "not-computable", "none", "null"}
_TRAINING_TERMS = (
    "public domain",
    "public-domain",
    "pd ",
    "cc0",
    "cc-by",
    "cc by",
    "creative commons",
)


def _license_candidate(value: object) -> bool:
    if not isinstance(value, str) or value.strip().casefold() in _DENY_LICENSES:
        return False
    folded = value.strip().casefold()
    return any(term in folded for term in _TRAINING_TERMS)


def audit_training_rights(atoms: list[dict], *, candidate_manifest_sha256: str) -> dict:
    """Classify source/license claims without converting claims into legal clearance."""
    if not isinstance(candidate_manifest_sha256, str) or len(candidate_manifest_sha256) != 64:
        raise ValueError("candidate manifest SHA256 required")
    int(candidate_manifest_sha256, 16)
    if not atoms:
        raise ValueError("atoms required")

    counts = Counter()
    hosts = Counter()
    unresolved = []
    seen = set()
    for atom in atoms:
        if not isinstance(atom, dict):
            raise TypeError("atom must be an object")
        aid = atom.get("atom_id")
        if not isinstance(aid, str) or not aid or aid in seen:
            raise ValueError("unique atom_id required")
        seen.add(aid)
        license_claim = atom.get("license")
        source_url = atom.get("source_url")
        if not isinstance(source_url, str) or not source_url.strip():
            raise ValueError("source_url required")
        host = (urlparse(source_url).hostname or "").casefold()
        hosts[host or "INVALID_HOST"] += 1
        if _license_candidate(license_claim):
            counts["candidate_clearable"] += 1
        else:
            counts["unresolved"] += 1
            unresolved.append(
                {
                    "atom_id": aid,
                    "host": host or "INVALID_HOST",
                    "license_claim": license_claim,
                }
            )

    report = {
        "schema": "athanor.training_rights_audit.v1",
        "status": "REVIEW_REQUIRED",
        "candidate_manifest_sha256": candidate_manifest_sha256,
        "atom_count": len(atoms),
        "counts": dict(sorted(counts.items())),
        "hosts": dict(sorted(hosts.items())),
        "unresolved": sorted(unresolved, key=lambda row: row["atom_id"]),
        "training_rights_cleared": False,
        "training_authorized": False,
        "scope": (
            "License-string triage only. Public-domain/open claims remain claims until "
            "work/edition/source evidence is independently reviewed for training use."
        ),
    }
    report["evidence_sha256"] = hashlib.sha256(
        json.dumps(report, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--atoms", required=True, type=Path)
    parser.add_argument("--candidate-manifest-sha256", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.atoms.is_symlink() or not args.atoms.is_file() or args.atoms.stat().st_size > MAX_BYTES:
            raise ValueError("unsafe or oversized atoms input")
        atoms = [_json(line) for line in args.atoms.read_bytes().splitlines() if line.strip()]
        report = audit_training_rights(
            atoms, candidate_manifest_sha256=args.candidate_manifest_sha256
        )
    except (ValueError, TypeError, KeyError, OSError, RecursionError) as exc:
        print(json.dumps({"status": "INVALID", "training_authorized": False, "reason": str(exc)}))
        return 1
    payload = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
