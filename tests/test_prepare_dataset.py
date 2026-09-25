from pathlib import Path

import pytest

from athanor.dataset import prepare_dataset


def test_prepare_dataset_produces_manifest_and_exits_hold(tmp_path: Path):
    # minimal gold + weak input
    gold = tmp_path / "gold.jsonl"
    gold.write_text('{"row_id":"g1","family_id":"test","split":"UNASSIGNED"}\n')
    weak = tmp_path / "weak.jsonl"
    weak.write_text('')
    manifest_path = tmp_path / "manifest.json"
    with pytest.raises(SystemExit) as exc:
        prepare_dataset(gold, weak, manifest_path, ratios={"train":0.8,"eval":0.2}, seed=42)
    assert exc.value.code == 2
    assert not manifest_path.exists()  # HOLD, no freeze
