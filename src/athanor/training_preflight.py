"""Generate a fail-closed training-preflight receipt from candidate-pack evidence."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from athanor.readiness import inspect_pack

_SHA_RE = re.compile(r"^[0-9a-f]{40,64}$")


def _evidence_gate(
    evidence: dict[str, Any] | None,
    *,
    expected_kind: str,
    candidate_manifest_sha256: str | None,
    repo_sha: str,
) -> tuple[str, Any, str | None]:
    if evidence is None:
        return "HOLD", "NOT_COMPUTABLE", "EVIDENCE_RECEIPT_REQUIRED"
    if evidence.get("kind") != expected_kind:
        return "HOLD", evidence, "WRONG_EVIDENCE_KIND"
    if evidence.get("status") != "PASS":
        return "HOLD", evidence, "EVIDENCE_STATUS_NOT_PASS"
    if evidence.get("candidate_manifest_sha256") != candidate_manifest_sha256:
        return "HOLD", evidence, "CANDIDATE_MANIFEST_MISMATCH"
    bound_repo_sha = evidence.get("repo_sha")
    if bound_repo_sha is not None and bound_repo_sha != repo_sha:
        return "HOLD", evidence, "REPO_SHA_MISMATCH"
    evidence_sha256 = evidence.get("evidence_sha256")
    if not isinstance(evidence_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", evidence_sha256):
        return "HOLD", evidence, "INVALID_EVIDENCE_DIGEST"
    return "PASS", evidence, None


def receipt_from_audit(
    audit: dict[str, Any],
    repo_sha: str,
    *,
    rights_evidence: dict[str, Any] | None = None,
    gold_evidence: dict[str, Any] | None = None,
    baseline_evidence: dict[str, Any] | None = None,
    config_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
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

    manifest_sha = audit.get("manifest_sha256")
    g3_status, g3_evidence, g3_reason = _evidence_gate(
        rights_evidence,
        expected_kind="provenance_rights",
        candidate_manifest_sha256=manifest_sha,
        repo_sha=repo_sha,
    )
    g6_status, g6_evidence, g6_reason = _evidence_gate(
        gold_evidence,
        expected_kind="independent_gold_holdout",
        candidate_manifest_sha256=manifest_sha,
        repo_sha=repo_sha,
    )
    g7_status, g7_evidence, g7_reason = _evidence_gate(
        baseline_evidence,
        expected_kind="untrained_baseline",
        candidate_manifest_sha256=manifest_sha,
        repo_sha=repo_sha,
    )
    g8_status, g8_evidence, g8_reason = _evidence_gate(
        config_evidence,
        expected_kind="training_config",
        candidate_manifest_sha256=manifest_sha,
        repo_sha=repo_sha,
    )

    gates = {
        "G2_CORPUS_FREEZE": {
            "status": "PASS" if audit.get("manifest_sha256") else "HOLD",
            "evidence": audit.get("manifest_sha256") or "NOT_COMPUTABLE",
        },
        "G3_PROVENANCE_RIGHTS": {
            "status": g3_status,
            "evidence": g3_evidence,
            **({"reason": g3_reason} if g3_reason else {}),
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
            "status": g6_status,
            "evidence": g6_evidence,
            **({"reason": g6_reason} if g6_reason else {}),
        },
        "G7_UNTRAINED_BASELINE": {
            "status": g7_status,
            "evidence": g7_evidence,
            **({"reason": g7_reason} if g7_reason else {}),
        },
        "G8_TRAINING_CONFIG_FREEZE": {
            "status": g8_status,
            "evidence": g8_evidence,
            **({"reason": g8_reason} if g8_reason else {}),
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


def _load_evidence(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"evidence must be a JSON object: {path}")
    return value


def build_receipt(
    pack: Path,
    repo_sha: str,
    *,
    rights_evidence: Path | None = None,
    gold_evidence: Path | None = None,
    baseline_evidence: Path | None = None,
    config_evidence: Path | None = None,
) -> dict[str, Any]:
    return receipt_from_audit(
        inspect_pack(pack),
        repo_sha,
        rights_evidence=_load_evidence(rights_evidence),
        gold_evidence=_load_evidence(gold_evidence),
        baseline_evidence=_load_evidence(baseline_evidence),
        config_evidence=_load_evidence(config_evidence),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", required=True, type=Path)
    parser.add_argument("--repo-sha", required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--rights-evidence", type=Path)
    parser.add_argument("--gold-evidence", type=Path)
    parser.add_argument("--baseline-evidence", type=Path)
    parser.add_argument("--config-evidence", type=Path)
    args = parser.parse_args(argv)

    try:
        receipt = build_receipt(
            args.pack,
            args.repo_sha,
            rights_evidence=args.rights_evidence,
            gold_evidence=args.gold_evidence,
            baseline_evidence=args.baseline_evidence,
            config_evidence=args.config_evidence,
        )
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
