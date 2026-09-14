"""Synthetic invariants, not evidence of Qwen or Spark compatibility."""
import copy
import json

import pytest
from test_adapter_data import example

from athanor.adapter_data import digest
from athanor.adapter_freeze import freeze_candidates
from athanor.adapter_preflight import inspect_model, inventory
from athanor.adapter_tokens import completion_tokens, pad_examples


def config():
    return {"schema_version": "athanor.split_config.v1", "seed": 42,
            "ratios": {"train": .6, "val": .2, "test": .2},
            "min_rows": {"train": 1, "val": 1, "test": 1}, "grouping_revision": "synthetic-v1"}


def rows(count=100):
    output = []
    for i in range(count):
        row = example()
        row.update(row_id=str(i), query=f"Synthetic query {i}")
        row["sources"][0].update(id=str(i), group_id=str(i), text=str(i), sha256=digest(str(i)))
        row["answer"]["citations"] = [str(i)]
        output.append(row)
    return output


def test_freeze_deterministic_and_nonmutating():
    data = rows()
    before = copy.deepcopy(data)
    result = freeze_candidates(data, config())
    assert result == freeze_candidates(list(reversed(data)), config())
    assert data == before
    assert result["status"] == "FROZEN_CANDIDATE"
    assert result["training_authorized"] is False
    assert sum(result["split_counts"].values()) == 100


def test_transitive_components():
    data = rows(3)
    data[1]["sources"].append(copy.deepcopy(data[0]["sources"][0]))
    data[2]["sources"].append(copy.deepcopy(data[1]["sources"][0]))
    result = freeze_candidates(data, config())
    assert result["group_count"] == 1
    assert len(set(result["groups"].values())) == 1
    assert result["status"] == "REJECTED_SUPPORT"


def test_freeze_rejects_existing_holdout_and_bad_ratios():
    data = rows(1)
    data[0]["split"] = "test"
    with pytest.raises(ValueError, match="held-out"):
        freeze_candidates(data, config())
    data[0]["split"] = "UNASSIGNED"
    bad = config()
    bad["ratios"]["train"] = float("nan")
    with pytest.raises(ValueError):
        freeze_candidates(data, bad)


class SyntheticTokenizer:
    def apply_chat_template(self, messages, **kwargs):
        assert kwargs["enable_thinking"] is False
        return [1, 2, 3] if len(messages) == 2 else [1, 2, 3, 4, 5]


def token_args():
    return [{"role": "system", "content": "s"}, {"role": "user", "content": "u"}], [
        {"role": "assistant", "content": "a"}]


def test_completion_mask_and_padding():
    row = completion_tokens(SyntheticTokenizer(), *token_args(), max_length=5)
    assert row["labels"] == [-100, -100, -100, 4, 5]
    shorter = {key: value[:-1] for key, value in row.items()}
    padded = pad_examples([row, shorter], pad_token_id=5)
    assert padded["labels"][0][-1] == 5
    assert padded["labels"][1][-1] == -100
    assert padded["attention_mask"][1][-1] == 0


def test_truncation_and_bad_template_fail_closed():
    with pytest.raises(ValueError, match="truncation"):
        completion_tokens(SyntheticTokenizer(), *token_args(), max_length=4)

    class BadTemplate(SyntheticTokenizer):
        def apply_chat_template(self, messages, **kwargs):
            return [7] if len(messages) == 2 else [8, 9]

    with pytest.raises(ValueError, match="prefix"):
        completion_tokens(BadTemplate(), *token_args(), max_length=5)
    with pytest.raises(ValueError):
        completion_tokens(SyntheticTokenizer(), [None], [None], max_length=5)


def test_preflight_is_inventory_not_authority(tmp_path, monkeypatch):
    monkeypatch.setattr("athanor.adapter_preflight.shutil.which", lambda _: None)
    result = inventory()
    assert result["status"] == "HOLD" and result["training_authorized"] is False
    assert result["gpu"]["status"] == "NOT_COMPUTABLE"
    with pytest.raises(ValueError):
        inspect_model(tmp_path)
    (tmp_path / "config.json").write_text(json.dumps({"architectures": ["Synthetic"]}))
    model = inspect_model(tmp_path)
    assert model["architecture"] == ["Synthetic"]
    assert model["revision_verified"] is False and model["weights_verified"] is False
