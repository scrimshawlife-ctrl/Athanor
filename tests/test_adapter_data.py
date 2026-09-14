"""Synthetic-only source-grounding envelope controls; no learned quality claims."""
import copy
import json

import pytest

from athanor.adapter_data import compile_candidates, digest, main


def example():
    return {"schema_version": "athanor.instruction_candidate.v1", "row_id": "synthetic",
            "task": "three_lens", "query": "Describe the synthetic record", "split": "UNASSIGNED",
            "sources": [{"id": "s1", "text": "Synthetic example only.",
                         "sha256": digest("Synthetic example only."), "group_id": "work1"}],
            "answer": {"historical": "A synthetic example.", "symbolic": "NOT_COMPUTABLE",
                       "operational": "NOT_COMPUTABLE", "epistemic": "INFERRED",
                       "citations": ["s1"], "efficacy": None}}


def test_projection_is_candidate_not_authority():
    row = example()
    before = copy.deepcopy(row)
    result = compile_candidates([row])
    assert row == before
    assert result["status"] == "CANDIDATE_ONLY" and result["training_authorized"] is False
    prompt = result["rows"][0]["prompt"]
    assert [m["role"] for m in prompt] == ["system", "user"]
    assert set(json.loads(prompt[1]["content"])["sources"][0]) == {"id", "text"}
    assert result["rows"][0]["completion"][0]["role"] == "assistant"


@pytest.mark.parametrize("mutate", [
    lambda r: r.update(allow_train=True),
    lambda r: r["answer"].update(efficacy=0.5),
    lambda r: r["answer"].update(citations=["invented"]),
    lambda r: r["answer"].update(citations=[]),
    lambda r: r["sources"][0].update(sha256="0" * 64),
    lambda r: r["sources"][0].update(group_id=""),
    lambda r: r.update(task="insufficient_evidence"),
    lambda r: r.update(query=" "),
    lambda r: r["answer"].update(epistemic="GOLD"),
    lambda r: r["answer"].update(citations=["s1", "s1"]),
])
def test_negative_controls(mutate):
    row = example()
    mutate(row)
    with pytest.raises((ValueError, TypeError)):
        compile_candidates([row])


def test_abstention_without_sources():
    row = example()
    row.update(task="insufficient_evidence", sources=[])
    row["answer"].update(epistemic="NOT_COMPUTABLE", citations=[])
    assert compile_candidates([row])["status"] == "CANDIDATE_ONLY"


@pytest.mark.parametrize("identity", ["source", "group", "content"])
def test_cross_split_leakage(identity):
    a, b = example(), example()
    a["split"], b["split"], b["row_id"] = "train", "test", "other"
    if identity != "source":
        b["sources"][0]["id"] = "s2"
        b["answer"]["citations"] = ["s2"]
    if identity == "content":
        b["sources"][0]["group_id"] = "other-work"
    with pytest.raises(ValueError, match="crosses splits"):
        compile_candidates([a, b])


def test_determinism_duplicate_and_source_revision():
    a, b = example(), example()
    b["row_id"] = "second"
    assert compile_candidates([a, b]) == compile_candidates([b, a])
    with pytest.raises(ValueError, match="Duplicate instruction"):
        compile_candidates([a, a])
    b["sources"][0].update(text="Changed", sha256=digest("Changed"))
    with pytest.raises(ValueError, match="Conflicting revisions"):
        compile_candidates([a, b])


def test_cli(tmp_path, capsys):
    path = tmp_path / "synthetic.jsonl"
    path.write_text(json.dumps(example()), encoding="utf-8")
    assert main(["--input", str(path)]) == 2
    assert json.loads(capsys.readouterr().out)["status"] == "CANDIDATE_ONLY"
    path.write_text("[" * 10000 + "0" + "]" * 10000, encoding="utf-8")
    assert main(["--input", str(path)]) == 1
    assert json.loads(capsys.readouterr().out)["status"] == "INVALID"
