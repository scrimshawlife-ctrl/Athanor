"""Tests for fail-closed training-rights triage."""

from athanor.training_rights import audit_training_rights

MANIFEST = "a" * 64


def _atom(aid, license_claim, url="https://archive.org/details/example"):
    return {
        "atom_id": aid,
        "license": license_claim,
        "source_url": url,
    }


def test_public_domain_claim_is_candidate_not_clearance():
    report = audit_training_rights([_atom("a1", "public-domain (1659)")], candidate_manifest_sha256=MANIFEST)
    assert report["counts"]["candidate_clearable"] == 1
    assert report["training_rights_cleared"] is False
    assert report["training_authorized"] is False
    assert report["status"] == "REVIEW_REQUIRED"


def test_unknown_license_is_explicitly_unresolved():
    report = audit_training_rights([_atom("a1", "unknown")], candidate_manifest_sha256=MANIFEST)
    assert report["counts"]["unresolved"] == 1
    assert report["unresolved"][0]["atom_id"] == "a1"


def test_modern_or_ambiguous_claim_does_not_clear_by_nonempty_string():
    report = audit_training_rights([_atom("a1", "publisher claim")], candidate_manifest_sha256=MANIFEST)
    assert report["counts"]["unresolved"] == 1


def test_evidence_digest_is_deterministic():
    atoms = [_atom("b", "CC0"), _atom("a", "public domain")]
    first = audit_training_rights(atoms, candidate_manifest_sha256=MANIFEST)
    second = audit_training_rights(atoms, candidate_manifest_sha256=MANIFEST)
    assert first["evidence_sha256"] == second["evidence_sha256"]
