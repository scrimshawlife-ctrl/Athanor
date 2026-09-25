"""Convert reviewed training-rights evidence into a G3 sidecar; never performs legal review."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from athanor.readiness import MAX_BYTES, _json

_SHA = re.compile(r"^[0-9a-f]{64}$")


def _hash(value: object) -> str:
    if not isinstance(value, str) or not _SHA.fullmatch(value):
        raise ValueError("lowercase SHA256 required")
    return value


def settle_training_rights(review: dict, *, repo_sha: str | None = None) -> dict:
    """Validate complete reviewer attestations for the exact candidate manifest."""
    expected = {
        "schema",
        "candidate_manifest_sha256",
        "intended_use",
        "jurisdiction",
        "reviewer",
        "review_evidence_sha256",
        "sources",
    }
    if not isinstance(review, dict) or set(review) != expected:
        raise ValueError("unexpected training-rights review fields")
    if review["schema"] != "athanor.training_rights_review.v1":
        raise ValueError("unsupported training-rights review schema")
    manifest = _hash(review["candidate_manifest_sha256"])
    if review["intended_use"] != "model_training":
        raise ValueError("rights review must explicitly cover model_training")
    for field in ("jurisdiction", "reviewer"):
        if not isinstance(review[field], str) or not review[field].strip():
            raise ValueError(f"{field} required")
    refs = review["review_evidence_sha256"]
    if not isinstance(refs, list) or not refs or len(refs) != len(set(refs)):
        raise ValueError("distinct review evidence references required")
    for ref in refs:
        _hash(ref)

    sources = review["sources"]
    if not isinstance(sources, list) or not sources:
        raise ValueError("source decisions required")
    seen = set()
    for source in sources:
        if not isinstance(source, dict) or set(source) != {
            "source_id", "work_edition_id", "source_url", "license_basis",
            "decision", "evidence_sha256",
        }:
            raise ValueError("unexpected source decision fields")
        sid = source["source_id"]
        if not isinstance(sid, str) or not sid.strip() or sid in seen:
            raise ValueError("unique source_id required")
        seen.add(sid)
        for field in ("work_edition_id", "source_url", "license_basis"):
            if not isinstance(source[field], str) or not source[field].strip():
                raise ValueError(f"{field} required")
        if source["decision"] != "CLEARED":
            raise ValueError("all sources must be CLEARED for G3 PASS")
        evidence = source["evidence_sha256"]
        if not isinstance(evidence, list) or not evidence or len(evidence) != len(set(evidence)):
            raise ValueError("distinct source evidence references required")
        for ref in evidence:
            _hash(ref)

    canonical_review = json.dumps(review, sort_keys=True, separators=(",", ":")).encode()
    evidence_sha = hashlib.sha256(canonical_review).hexdigest()
    sidecar = {
        "kind": "provenance_rights",
        "status": "PASS",
        "candidate_manifest_sha256": manifest,
        "evidence_sha256": evidence_sha,
    }
    if repo_sha is not None:
        if not isinstance(repo_sha, str) or not re.fullmatch(r"[0-9a-f]{40,64}", repo_sha):
            raise ValueError("valid repo SHA required")
        sidecar["repo_sha"] = repo_sha
    return sidecar


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review", required=True, type=Path)
    parser.add_argument("--repo-sha")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.review.is_symlink() or not args.review.is_file() or args.review.stat().st_size > MAX_BYTES:
            raise ValueError("unsafe or oversized review input")
        sidecar = settle_training_rights(_json(args.review.read_bytes()), repo_sha=args.repo_sha)
    except (ValueError, TypeError, KeyError, OSError, RecursionError) as exc:
        print(json.dumps({"status": "HOLD", "training_authorized": False, "reason": str(exc)}))
        return 2
    payload = json.dumps(sidecar, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
