"""Generate a fail-closed training-preflight receipt from candidate-pack evidence."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from athanor.readiness import inspect_pack

_SHA_RE = re.compile(r"^[0-9a-f]{40,64}$")


def receipt_from_audit(audit: dict[str, Any], repo_sha: str) -> dict[str, Any]:
    """Map read-only candidate evidence to deterministic G2-G8 gate states."""
    if not _SHA_RE.fullmatch(repo_sha):
        raise ValueError("repo_sha must be a 40-64 character lowercase hex digest")
    if audit.get("integrity") != "PASS":
        raise ValueError("candidate audit integrity must PASS")

    split_counts = audit.get("split_counts") or {}
    partition_ok = bool(
        split_counts.get("train")
        and split_counts.get("test")
        and (split_counts.get("val") or split_counts.get("validation"))
    )
    leakage = audit.get("leakage_audit") or {}
    leakage_ok = leakage.get("status") == "PASS"

    gates = {
        "G2_CORPUS_FREEZE": {
            "status": "PASS" if audit.get("manifest_sha256") else "HOLD",
            "evidence": audit.get("manifest_sha256") or "NOT_COMPUTABLE",
        },
        "G3_PROVENANCE_RIGHTS": {
            "status": "HOLD",
            "evidence": "NOT_COMPUTABLE",
            "reason": "AUTHENTICATED_USE_SCOPED_RIGHTS_REVIEW_REQUIRED",
        },
        "G4_COMPONENT_SPLIT": {
            "status": "PASS" if partition_ok and leakage_ok else "HOLD",
            "evidence": {
                "split_counts": split_counts,
                "leakage_status": leakage.get("status", "NOT_COMPUTABLE"),
            },
        },
        "G5_LEAKAGE_AUDIT": {
            "status": "PASS" if leakage_ok else "HOLD",
            "evidence": leakage,
        },
        "G6_GOLD_HOLDOUT": {
            "status": "HOLD",
            "evidence": "NOT_COMPUTABLE",
            "reason": "INDEPENDENT_CONTENT_BOUND_LABEL_REVIEW_REQUIRED",
        },
        "G7_UNTRAINED_BASELINE": {
            "status": "HOLD",
            "evidence": "NOT_COMPUTABLE",
            "reason": "UNTOUCHED_TEST_BASELINE_RECEIPT_REQUIRED",
        },
        "G8_TRAINING_CONFIG_FREEZE": {
            "status": "HOLD",
            "evidence": "NOT_COMPUTABLE",
            "reason": "MODEL_TOKENIZER_SEED_HYPERPARAMETER_PIN_REQUIRED",
        },
    }
    blockers = [gate for gate, result in gates.items() if result["status"] != "PASS"]

    return {
        "schema": "athanor.training_preflight.v1",
        "repo_sha": repo_sha,
        "candidate_manifest_sha256": audit.get("manifest_sha256"),
        "candidate_rows": audit.get("candidate_rows"),
        "gates": gates,
        "blocking_gates": blockers,
        "state": "HOLD" if blockers else "PREFLIGHT_PASS",
        "training_authorized": False,
        "scope": "Read-only evidence receipt; never authorizes training.",
    }


def build_receipt(pack: Path, repo_sha: str) -> dict[str, Any]:
    return receipt_from_audit(inspect_pack(pack), repo_sha)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", required=True, type=Path)
    parser.add_argument("--repo-sha", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    try:
        receipt = build_receipt(args.pack, args.repo_sha)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"state": "INVALID", "training_authorized": False, "reason": str(exc)}))
        return 1

    payload = json.dumps(receipt, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if receipt["state"] == "PREFLIGHT_PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
