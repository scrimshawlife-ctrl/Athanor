"""Read-only candidate integrity audit, never a training authorization oracle."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

FILES = ("features.jsonl", "targets.jsonl", "provenance.jsonl", "quarantine.jsonl")
MAX_BYTES = 256 * 1024 * 1024


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _constant(value):
    raise ValueError(f"Non-finite JSON number: {value}")


def _json(data):
    def number(value):
        parsed = float(value)
        if not math.isfinite(parsed):
            raise ValueError("Non-finite JSON number")
        return parsed
    return json.loads(data, object_pairs_hook=_object, parse_constant=_constant, parse_float=number)


def _read(root, name):
    path = root / name  # Fixed names only; never consume a manifest-provided path.
    if path.is_symlink() or not path.is_file() or path.resolve().parent != root.resolve():
        raise ValueError(f"Missing or unsafe file: {name}")
    if path.stat().st_size > MAX_BYTES:
        raise ValueError(f"Audit size limit exceeded: {name}")
    return path.read_bytes()


def _ids(rows):
    ids = set()
    for row in rows:
        key = row.get("row_id")
        if not isinstance(key, str) or not key.strip() or key in ids:
            raise ValueError("Missing or duplicate row_id")
        ids.add(key)
    return ids


def inspect_pack(root: Path) -> dict:
    """Verify candidate-preparation/1; even edited approval claims remain untrusted."""
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Pack root must be a real directory")
    raw_manifest = _read(root, "manifest.json")
    manifest = _json(raw_manifest)
    if not isinstance(manifest, dict) or manifest.get("repo") != "athanor":
        raise ValueError("Expected Athanor manifest")
    if manifest.get("version") != "candidate-preparation/1":
        raise ValueError("Unsupported candidate version")
    entries = manifest.get("files")
    if not isinstance(entries, dict) or set(entries) != set(FILES):
        raise ValueError("Expected exactly four candidate file entries")
    files = {}
    for name in FILES:
        metadata = entries[name]
        if not isinstance(metadata, dict):
            raise TypeError("Invalid file metadata")
        data = _read(root, name)
        if hashlib.sha256(data).hexdigest() != metadata.get("sha256"):
            raise ValueError(f"Digest mismatch: {name}")
        if type(metadata.get("bytes")) is not int or metadata["bytes"] != len(data):
            raise ValueError(f"Byte count mismatch: {name}")
        rows = [_json(line) for line in data.splitlines() if line.strip()]
        if not all(isinstance(row, dict) for row in rows):
            raise ValueError("JSONL records must be objects")
        if type(metadata.get("rows")) is not int or metadata["rows"] != len(rows):
            raise ValueError(f"Row count mismatch: {name}")
        files[name] = rows
    features, targets = files[FILES[0]], files[FILES[1]]
    if not features or _ids(features) != _ids(targets):
        raise ValueError("Nonempty feature/target IDs must match one-to-one")
    for row in features:
        inputs = row.get("inputs")
        if set(row) != {"row_id", "inputs"} or not isinstance(inputs, dict):
            raise ValueError("Unexpected feature envelope")
        if set(inputs) != {"text"} or not isinstance(inputs["text"], str):
            raise ValueError("Model inputs must contain text only")
        if not inputs["text"].strip():
            raise ValueError("Empty model input")
    splits, families, heads = Counter(), Counter(), Counter()
    eligible = 0
    for row in targets:
        labels, split = row.get("targets"), row.get("split")
        if not isinstance(labels, dict) or not isinstance(labels.get("family_id"), str):
            raise TypeError("Missing family target")
        if not labels["family_id"].strip():
            raise ValueError("Blank family target")
        if split not in {"UNASSIGNED", "train", "val", "validation", "test"}:
            raise ValueError("Unknown split")
        if type(row.get("training_eligible")) is not bool:
            raise ValueError("Eligibility claim must be boolean")
        splits[split] += 1
        families[labels["family_id"]] += 1
        heads.update(labels.keys())
        eligible += row["training_eligible"]
    blockers = ["INDEPENDENT_LABEL_REVIEW", "USE_SCOPED_RIGHTS_REVIEW",
                "WORK_EDITION_GROUPING_AND_LEAKAGE_PROOF", "MODEL_TOKENIZER_CONFIG_PIN",
                "EVALUATION_SUPPORT_PROTOCOL", "TRAINER_AND_EVALUATOR_IMPLEMENTATION",
                "RESOURCE_PREFLIGHT", "SCOPED_OPERATOR_TRAIN_APPROVAL"]
    if splits["UNASSIGNED"]:
        blockers.append("UNASSIGNED_SPLITS")
    if not (splits["train"] and splits["test"] and (splits["val"] or splits["validation"])):
        blockers.append("MISSING_TRAIN_VALIDATION_TEST_PARTITION")
    return {
        "schema_version": "athanor.candidate_audit.v1", "status": "HOLD",
        "integrity": "PASS", "training_authorized": False,
        "manifest_sha256": hashlib.sha256(raw_manifest).hexdigest(),
        "files_verified": len(FILES), "candidate_rows": len(targets),
        "provenance_rows": len(files["provenance.jsonl"]),
        "quarantine_rows": len(files["quarantine.jsonl"]),
        "split_counts": dict(sorted(splits.items())),
        "family_counts": dict(sorted(families.items())),
        "target_field_counts": dict(sorted(heads.items())),
        "training_eligible_claims": eligible,
        "independently_verified_eligible_rows": "NOT_COMPUTABLE", "blockers": blockers,
        "scope": "Candidate storage and joins only; no review authentication or content adjudication",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        result = inspect_pack(args.pack)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"status": "INVALID", "training_authorized": False, "reason": str(exc)}))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 2  # This candidate format cannot establish training readiness.


if __name__ == "__main__":
    raise SystemExit(main())
