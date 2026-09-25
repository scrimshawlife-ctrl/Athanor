"""Synthetic candidate checks, including false-approval and tampering controls."""
import hashlib
import json

import pytest

from athanor.readiness import FILES, inspect_pack, main


def pack(root, mutate=None):
    feature = {"row_id": "synthetic", "inputs": {"text": "Synthetic fixture"}}
    target = {"row_id": "synthetic", "targets": {"family_id": "hermetic"},
              "split": "UNASSIGNED", "training_eligible": False}
    records = {FILES[0]: [feature], FILES[1]: [target], FILES[2]: [{}], FILES[3]: []}
    if mutate:
        mutate(records)
    manifest = {"version": "candidate-preparation/1", "repo": "athanor", "files": {}}
    for name, rows in records.items():
        data = "".join(json.dumps(row) + "\n" for row in rows).encode()
        (root / name).write_bytes(data)
        manifest["files"][name] = {"sha256": hashlib.sha256(data).hexdigest(),
                                   "bytes": len(data), "rows": len(rows)}
    (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return manifest


def test_integrity_does_not_authorize_training(tmp_path):
    pack(tmp_path)
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    report = inspect_pack(tmp_path)
    assert report["integrity"] == "PASS"
    assert report["status"] == "HOLD" and report["training_authorized"] is False
    assert report["candidate_rows"] == 1
    assert report["split_counts"] == {"UNASSIGNED": 1}
    assert before == {p.name: p.read_bytes() for p in tmp_path.iterdir()}


def test_forged_approval_does_not_authorize(tmp_path):
    manifest = pack(tmp_path, lambda rows: rows[FILES[1]][0].update(training_eligible=True))
    manifest.update(allow_train=True, allow_hub=True, state="READY", unresolved=[])
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    result = inspect_pack(tmp_path)
    assert result["training_eligible_claims"] == 1
    assert result["training_authorized"] is False and result["status"] == "HOLD"


@pytest.mark.parametrize("mutation", [
    lambda r: r[FILES[0]].append(r[FILES[0]][0]),
    lambda r: r[FILES[1]][0].update(row_id="unmatched"),
    lambda r: r[FILES[0]][0]["inputs"].update(family_id="leaked target"),
    lambda r: r[FILES[0]][0]["inputs"].update(text="  "),
    lambda r: r[FILES[1]][0].update(split="random"),
    lambda r: r[FILES[1]][0].update(training_eligible="false"),
    lambda r: r[FILES[1]][0].update(targets={"family_id": ""}),
    lambda r: r[FILES[1]][0].update(targets={"family_id": float("nan")}),
    lambda r: r[FILES[2]].append([]),
])
def test_invalid_records_even_with_matching_hashes(tmp_path, mutation):
    pack(tmp_path, mutation)
    with pytest.raises((ValueError, TypeError)):
        inspect_pack(tmp_path)


@pytest.mark.parametrize("field,value", [("bytes", 0), ("rows", 7), ("rows", True),
                                         ("sha256", "0" * 64)])
def test_manifest_lies(tmp_path, field, value):
    manifest = pack(tmp_path)
    manifest["files"][FILES[0]][field] = value
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError):
        inspect_pack(tmp_path)


def test_manifest_path_injection(tmp_path):
    manifest = pack(tmp_path)
    manifest["files"]["../outside.jsonl"] = manifest["files"].pop(FILES[0])
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError):
        inspect_pack(tmp_path)


def test_duplicate_json_keys(tmp_path):
    pack(tmp_path)
    (tmp_path / "manifest.json").write_text('{"repo":"athanor","repo":"other"}')
    with pytest.raises(ValueError, match="Duplicate JSON key"):
        inspect_pack(tmp_path)


def test_tamper_and_cli_exit_codes(tmp_path, capsys):
    pack(tmp_path)
    assert main(["--pack", str(tmp_path)]) == 2
    assert json.loads(capsys.readouterr().out)["status"] == "HOLD"
    (tmp_path / FILES[0]).write_text("tampered")
    assert main(["--pack", str(tmp_path)]) == 1
    assert json.loads(capsys.readouterr().out)["status"] == "INVALID"


def test_missing_file(tmp_path):
    pack(tmp_path)
    (tmp_path / FILES[0]).unlink()
    with pytest.raises(ValueError):
        inspect_pack(tmp_path)


def test_complete_split_claim_still_not_authorized(tmp_path):
    def split_rows(records):
        records[FILES[0]] = [{"row_id": s, "inputs": {"text": "Synthetic " + s}}
                             for s in ("train", "validation", "test")]
        records[FILES[1]] = [{"row_id": s, "split": s, "training_eligible": True,
                             "targets": {"family_id": "hermetic"}}
                            for s in ("train", "validation", "test")]
    pack(tmp_path, split_rows)
    result = inspect_pack(tmp_path)
    assert "MISSING_TRAIN_VALIDATION_TEST_PARTITION" not in result["blockers"]
    assert result["training_authorized"] is False and result["status"] == "HOLD"


def test_file_symlink_rejected(tmp_path):
    pack(tmp_path)
    original = tmp_path / FILES[0]
    other = tmp_path / "original.jsonl"
    original.rename(other)
    try:
        original.symlink_to(other)
    except OSError:
        pytest.skip("Host does not permit symlink creation")
    with pytest.raises(ValueError, match="unsafe"):
        inspect_pack(tmp_path)


def test_overflow_number_rejected(tmp_path):
    pack(tmp_path)
    (tmp_path / "manifest.json").write_text('{"number":1e999}')
    with pytest.raises(ValueError, match="Non-finite"):
        inspect_pack(tmp_path)


@pytest.mark.parametrize("filename", ["manifest.json", FILES[0]])
def test_deep_json_returns_structured_invalid(tmp_path, capsys, filename):
    manifest = pack(tmp_path)
    data = ("[" * 100000 + "0" + "]" * 100000).encode()
    (tmp_path / filename).write_bytes(data)
    if filename != "manifest.json":
        manifest["files"][filename] = {"sha256": hashlib.sha256(data).hexdigest(),
                                      "bytes": len(data), "rows": 1}
        (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    assert main(["--pack", str(tmp_path)]) == 1
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "INVALID"
    assert result["reason"] == "JSON nesting exceeds parser limits"



def test_component_leakage_audit_passes_disjoint_components(tmp_path):
    def rows(records):
        names = ("train", "validation", "test")
        records[FILES[0]] = [
            {"row_id": name, "inputs": {"text": "Synthetic " + name}} for name in names
        ]
        records[FILES[1]] = [
            {
                "row_id": name,
                "split": name,
                "training_eligible": False,
                "targets": {"family_id": "hermetic"},
            }
            for name in names
        ]
        records[FILES[2]] = [
            {
                "row_id": name,
                "source_component_id": "component-" + name,
                "content_hash": "hash-" + name,
            }
            for name in names
        ]

    pack(tmp_path, rows)
    report = inspect_pack(tmp_path)
    assert report["leakage_audit"]["status"] == "PASS"
    assert report["leakage_audit"]["component_overlap_count"] == 0
    assert "WORK_EDITION_GROUPING_AND_LEAKAGE_PROOF" not in report["blockers"]


def test_component_leakage_audit_blocks_cross_split_component(tmp_path):
    def rows(records):
        names = ("train", "validation", "test")
        records[FILES[0]] = [
            {"row_id": name, "inputs": {"text": "Synthetic " + name}} for name in names
        ]
        records[FILES[1]] = [
            {
                "row_id": name,
                "split": name,
                "training_eligible": False,
                "targets": {"family_id": "hermetic"},
            }
            for name in names
        ]
        records[FILES[2]] = [
            {
                "row_id": name,
                "source_component_id": "shared" if name != "test" else "test-only",
                "content_hash": "hash-" + name,
            }
            for name in names
        ]

    pack(tmp_path, rows)
    report = inspect_pack(tmp_path)
    assert report["leakage_audit"]["status"] == "FAIL"
    assert report["leakage_audit"]["component_overlap_count"] == 1
    assert "WORK_EDITION_GROUPING_AND_LEAKAGE_PROOF" in report["blockers"]


def test_component_leakage_audit_is_not_computable_without_component_ids(tmp_path):
    def rows(records):
        records[FILES[2]] = [{"row_id": "synthetic", "content_hash": "hash-only"}]

    pack(tmp_path, rows)
    report = inspect_pack(tmp_path)
    assert report["leakage_audit"]["status"] == "NOT_COMPUTABLE"
    assert report["leakage_audit"]["missing_source_components"] == 1
    assert "WORK_EDITION_GROUPING_AND_LEAKAGE_PROOF" in report["blockers"]
