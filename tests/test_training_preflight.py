"""Tests for deterministic training-preflight receipt generation."""

import pytest

from athanor.training_preflight import receipt_from_audit

REPO_SHA = "a" * 40


def _audit(leakage_status="PASS", split_counts=None):
    return {
        "integrity": "PASS",
        "manifest_sha256": "b" * 64,
        "candidate_rows": 30,
        "split_counts": split_counts
        or {"train": 20, "validation": 5, "test": 5},
        "leakage_audit": {
            "status": leakage_status,
            "component_overlap_count": 0 if leakage_status == "PASS" else 1,
            "content_hash_overlap_count": 0,
        },
    }


def test_receipt_passes_only_gates_supported_by_current_evidence():
    receipt = receipt_from_audit(_audit(), REPO_SHA)
    assert receipt["gates"]["G2_CORPUS_FREEZE"]["status"] == "PASS"
    assert receipt["gates"]["G4_COMPONENT_SPLIT"]["status"] == "PASS"
    assert receipt["gates"]["G5_LEAKAGE_AUDIT"]["status"] == "PASS"
    assert receipt["gates"]["G3_PROVENANCE_RIGHTS"]["status"] == "HOLD"
    assert receipt["gates"]["G6_GOLD_HOLDOUT"]["status"] == "HOLD"
    assert receipt["state"] == "HOLD"
    assert receipt["training_authorized"] is False


def test_leakage_failure_blocks_component_split_and_leakage_gates():
    receipt = receipt_from_audit(_audit("FAIL"), REPO_SHA)
    assert receipt["gates"]["G4_COMPONENT_SPLIT"]["status"] == "HOLD"
    assert receipt["gates"]["G5_LEAKAGE_AUDIT"]["status"] == "HOLD"
    assert "G5_LEAKAGE_AUDIT" in receipt["blocking_gates"]


def test_missing_partition_blocks_component_split():
    receipt = receipt_from_audit(_audit(split_counts={"train": 25, "test": 5}), REPO_SHA)
    assert receipt["gates"]["G4_COMPONENT_SPLIT"]["status"] == "HOLD"
    assert receipt["gates"]["G5_LEAKAGE_AUDIT"]["status"] == "PASS"


@pytest.mark.parametrize("repo_sha", ["", "xyz", "A" * 40, "a" * 39])
def test_invalid_repo_sha_rejected(repo_sha):
    with pytest.raises(ValueError, match="repo_sha"):
        receipt_from_audit(_audit(), repo_sha)


def test_failed_integrity_rejected():
    audit = _audit()
    audit["integrity"] = "FAIL"
    with pytest.raises(ValueError, match="integrity"):
        receipt_from_audit(audit, REPO_SHA)



def _evidence(kind, manifest="b" * 64, repo_sha=REPO_SHA):
    return {
        "kind": kind,
        "status": "PASS",
        "candidate_manifest_sha256": manifest,
        "repo_sha": repo_sha,
        "evidence_sha256": "c" * 64,
    }


def test_explicit_bound_evidence_can_satisfy_g3_g6_g7_g8():
    receipt = receipt_from_audit(
        _audit(),
        REPO_SHA,
        rights_evidence=_evidence("provenance_rights"),
        gold_evidence=_evidence("independent_gold_holdout"),
        baseline_evidence=_evidence("untrained_baseline"),
        config_evidence=_evidence("training_config"),
    )
    assert receipt["state"] == "PREFLIGHT_PASS"
    assert receipt["blocking_gates"] == []
    assert receipt["training_authorized"] is False


def test_evidence_for_different_candidate_manifest_is_rejected():
    receipt = receipt_from_audit(
        _audit(),
        REPO_SHA,
        rights_evidence=_evidence("provenance_rights", manifest="d" * 64),
    )
    gate = receipt["gates"]["G3_PROVENANCE_RIGHTS"]
    assert gate["status"] == "HOLD"
    assert gate["reason"] == "CANDIDATE_MANIFEST_MISMATCH"


def test_wrong_evidence_kind_cannot_satisfy_gate():
    receipt = receipt_from_audit(
        _audit(),
        REPO_SHA,
        gold_evidence=_evidence("provenance_rights"),
    )
    gate = receipt["gates"]["G6_GOLD_HOLDOUT"]
    assert gate["status"] == "HOLD"
    assert gate["reason"] == "WRONG_EVIDENCE_KIND"


def test_evidence_repo_sha_mismatch_is_rejected():
    receipt = receipt_from_audit(
        _audit(),
        REPO_SHA,
        config_evidence=_evidence("training_config", repo_sha="d" * 40),
    )
    gate = receipt["gates"]["G8_TRAINING_CONFIG_FREEZE"]
    assert gate["status"] == "HOLD"
    assert gate["reason"] == "REPO_SHA_MISMATCH"
