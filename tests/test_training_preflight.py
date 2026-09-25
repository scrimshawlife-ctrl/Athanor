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
