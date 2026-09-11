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
        assert {"atom_id", "family_id", "excerpt", "license", "epistemic"} <= set(hit)
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
