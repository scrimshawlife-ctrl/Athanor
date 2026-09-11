import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def packet_schema():
    pytest.importorskip("jsonschema")
    return json.loads((ROOT / "schemas/athanor_packet.v0.schema.json").read_text(encoding="utf-8"))


def test_example_packet_valid(packet_schema):
    jsonschema = pytest.importorskip("jsonschema")
    example = json.loads((ROOT / "schemas/athanor_packet.v0.example.json").read_text(encoding="utf-8"))
    jsonschema.validate(example, packet_schema)
    assert example["efficacy"] is None


def test_dual_use_fixture_exists():
    path = ROOT / "fixtures/dual_use/refuse_summon.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["expect"]["efficacy"] is None
