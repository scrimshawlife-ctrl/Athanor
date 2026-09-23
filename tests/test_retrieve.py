"""Offline lexical retrieve — fixtures only (no ~/.athanor required)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from athanor.entrypoint import main
from athanor.retrieve import build_packet, load_atoms, rank_atoms, retrieve

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "fixtures" / "seed" / "atoms.jsonl"


@pytest.fixture
def seed_atoms():
    return load_atoms(SEED)


@pytest.fixture
def packet_schema():
    pytest.importorskip("jsonschema")
    return json.loads((ROOT / "schemas/athanor_packet.v0.schema.json").read_text(encoding="utf-8"))


def test_seed_has_three_atoms(seed_atoms):
    assert len(seed_atoms) == 3
    families = {a.family_id for a in seed_atoms}
    assert families == {"enochian", "hermetic"}


def test_rank_prefers_enochian_for_calls_query(seed_atoms):
    ranked = rank_atoms("Enochian Calls", seed_atoms, k=3)
    assert ranked
    assert ranked[0][0].family_id == "enochian"
    assert "call" in ranked[0][0].text.lower() or "Call" in ranked[0][0].text


def test_family_filter(seed_atoms):
    ranked = rank_atoms("tablet correspondence", seed_atoms, k=5, family="hermetic")
    assert len(ranked) == 1
    assert ranked[0][0].atom_id == "fixture.hermetic.emerald.01"


def test_retrieve_packet_efficacy_null_and_schema(packet_schema, monkeypatch):
    monkeypatch.setenv("ATHANOR_CORPUS", str(SEED))
    packet = retrieve("Enochian Calls", k=2)
    assert packet["efficacy"] is None
    assert packet["query"] == "Enochian Calls"
    assert len(packet["hits"]) >= 1
    for hit in packet["hits"]:
        base = {"atom_id", "family_id", "excerpt", "license", "epistemic"}
        assert base <= set(hit)
        # Provenance fields now populated when present in corpus (closes deviation)
        if "source_url" in hit:
            assert isinstance(hit.get("source_url"), str)
        if "content_hash" in hit:
            assert isinstance(hit.get("content_hash"), str)
    assert packet["receipts"]  # now has minimal receipt (closes deviation)
    assert packet["receipts"][0]["type"] == "lexical-retrieve"
    for lens in ("historical", "symbolic", "operational"):
        assert packet["synthesis"][lens]["epistemic"] == "INFERRED"

    jsonschema = pytest.importorskip("jsonschema")
    jsonschema.validate(packet, packet_schema)


def test_build_packet_always_null_efficacy(seed_atoms):
    ranked = rank_atoms("Watchtowers", seed_atoms, k=1)
    packet = build_packet("Watchtowers", ranked)
    assert packet["efficacy"] is None


def test_cli_retrieve_uses_fixture(capsys, monkeypatch):
    monkeypatch.delenv("ATHANOR_CORPUS", raising=False)
    code = main(["retrieve", "Enochian Calls", "--k", "2", "--corpus", str(SEED)])
    assert code == 0
    out = capsys.readouterr().out
    packet = json.loads(out)
    assert packet["efficacy"] is None
    assert any(h["family_id"] == "enochian" for h in packet["hits"])


def test_cli_missing_corpus(capsys, monkeypatch, tmp_path):
    missing = tmp_path / "nope.jsonl"
    monkeypatch.setenv("ATHANOR_CORPUS", str(missing))
    code = main(["retrieve", "anything"])
    assert code == 2
    err = capsys.readouterr().err
    assert "corpus not found" in err


def test_athanor_corpus_env(monkeypatch):
    monkeypatch.setenv("ATHANOR_CORPUS", str(SEED))
    packet = retrieve("Emerald Tablet", k=1, family="hermetic")
    assert packet["hits"][0]["atom_id"] == "fixture.hermetic.emerald.01"
    assert packet["efficacy"] is None
    # Provenance surfaced
    assert "source_url" in packet["hits"][0]
    assert packet["receipts"]


def test_three_lens_synthesis_differentiated(monkeypatch):
    """Basic HERMENEUT wiring test: synthesis uses lens_hints/family for differentiation."""
    monkeypatch.setenv("ATHANOR_CORPUS", str(SEED))
    packet = retrieve("Enochian Calls", k=1)
    synth = packet["synthesis"]
    assert "historical" in synth
    assert "symbolic" in synth
    assert "operational" in synth
    # Should contain family-specific or hint-driven text, not pure stub
    hist = synth["historical"]["text"]
    assert "enochian" in hist.lower() or "Retrieved from" in hist
    assert synth["historical"]["epistemic"] == "INFERRED"


def test_tokenless_query_rejected(monkeypatch):
    monkeypatch.setenv("ATHANOR_CORPUS", str(SEED))
    # Pure punctuation (has length but no tokens)
    with pytest.raises(ValueError, match="searchable token"):
        retrieve("!!! ???", k=1)
    # Whitespace-only hits non-empty first (acceptable per strip guard)
    with pytest.raises(ValueError, match="non-empty"):
        retrieve("   ", k=1)


def test_cli_malformed_rows_clean_error(capsys, monkeypatch, tmp_path):
    bad = tmp_path / "bad.jsonl"
    bad.write_text('{"text": "no id"}\n')
    monkeypatch.setenv("ATHANOR_CORPUS", str(bad))
    code = main(["retrieve", "test"])
    assert code == 2
    err = capsys.readouterr().err
    assert "invalid atom" in err or "missing required field" in err
    assert "Traceback" not in err  # no raw tracebacks (REQ-013)


def test_gated_train_eval_readiness_exits_hold():
    """Phase 5: gated skeleton for train eval harness must exit exactly 2 with HOLD (strictly non-activating, mirrors training-readiness.md)."""
    import subprocess
    script = ROOT / "scripts" / "eval_train_readiness.py"
    result = subprocess.run([str(script)], capture_output=True, text=True, check=False)
    assert result.returncode == 2, f"Expected HOLD exit code 2, got {result.returncode}"
    assert "EVAL-TRAIN-HARNESS: HOLD" in result.stdout
    assert "read-only skeleton only" in result.stdout
    assert "no ALLOW_TRAIN" in result.stdout
