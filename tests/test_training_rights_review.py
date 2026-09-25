"""Tests for G3 model-training rights settlement."""

import pytest

from athanor.training_rights_review import settle_training_rights

MANIFEST = "a" * 64


def _review():
    return {
        "schema": "athanor.training_rights_review.v1",
        "candidate_manifest_sha256": MANIFEST,
        "intended_use": "model_training",
        "jurisdiction": "US",
        "reviewer": "independent-reviewer",
        "review_evidence_sha256": ["b" * 64],
        "sources": [
            {
                "source_id": "source-1",
                "work_edition_id": "work-edition-1",
                "source_url": "https://archive.org/details/example",
                "license_basis": "reviewed public-domain edition",
                "decision": "CLEARED",
                "evidence_sha256": ["c" * 64],
            }
        ],
    }


def test_complete_model_training_review_produces_g3_sidecar():
    sidecar = settle_training_rights(_review(), repo_sha="d" * 40)
    assert sidecar["kind"] == "provenance_rights"
    assert sidecar["status"] == "PASS"
    assert sidecar["candidate_manifest_sha256"] == MANIFEST
    assert sidecar["repo_sha"] == "d" * 40


def test_local_analysis_scope_cannot_clear_training():
    review = _review()
    review["intended_use"] = "local_analysis"
    with pytest.raises(ValueError, match="model_training"):
        settle_training_rights(review)


def test_any_held_source_blocks_g3():
    review = _review()
    review["sources"][0]["decision"] = "HOLD"
    with pytest.raises(ValueError, match="CLEARED"):
        settle_training_rights(review)


def test_missing_source_evidence_blocks_g3():
    review = _review()
    review["sources"][0]["evidence_sha256"] = []
    with pytest.raises(ValueError, match="source evidence"):
        settle_training_rights(review)
