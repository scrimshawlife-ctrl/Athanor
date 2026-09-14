"""Deterministic whole-component candidate split freeze; never promotes review status."""
from __future__ import annotations

import argparse
import copy
import json
import math
from collections import Counter
from pathlib import Path

from athanor.adapter_data import canonical, compile_candidates, digest
from athanor.readiness import MAX_BYTES, _json


def freeze_candidates(rows, config):
    """Assign connected source/work/hash components, independent of input row order.

    This binds a proposed dataset's bytes and split choices. Human review,
    comprehensive work identities, near-duplicate detection and rights are external.
    Explicit existing splits are rejected to prevent silently moving a held-out set.
    """
    compile_candidates(rows)
    if any(row["split"] != "UNASSIGNED" for row in rows):
        raise ValueError("Freeze requires UNASSIGNED candidates; preserve existing held-out splits")
    expected = {"schema_version", "seed", "ratios", "min_rows", "grouping_revision"}
    if not isinstance(config, dict) or set(config) != expected:
        raise ValueError("Unexpected freeze config")
    if config["schema_version"] != "athanor.split_config.v1":
        raise ValueError("Unknown split config version")
    if type(config["seed"]) is not int or not isinstance(config["grouping_revision"], str):
        raise ValueError("Explicit integer seed and grouping revision required")
    if not config["grouping_revision"].strip():
        raise ValueError("Grouping revision is blank")
    ratios, minima = config["ratios"], config["min_rows"]
    if not isinstance(ratios, dict) or not isinstance(minima, dict):
        raise TypeError("Ratios and minima must be objects")
    if set(ratios) != {"train", "val", "test"} or set(minima) != set(ratios):
        raise ValueError("Explicit train/val/test ratios and minima required")
    if any(type(v) not in (float, int) or not math.isfinite(v) or not 0 < v < 1
           for v in ratios.values()):
        raise ValueError("Every split ratio must be a positive finite proportion below one")
    if not math.isclose(math.fsum(ratios.values()), 1, rel_tol=0, abs_tol=1e-12):
        raise ValueError("Ratios must sum to one")
    if any(type(v) is not int or v < 1 for v in minima.values()):
        raise ValueError("Each split requires an explicit positive minimum row count")
    parent = {row["row_id"]: row["row_id"] for row in rows}

    def root(key):
        while parent[key] != key:
            parent[key] = parent[parent[key]]
            key = parent[key]
        return key

    def union(a, b):
        a, b = sorted((root(a), root(b)))
        parent[b] = a

    owner, identities = {}, {}
    for row in rows:
        rid = row["row_id"]
        values = {("prompt", digest(canonical({"query": row["query"], "task": row["task"]})))}
        for source in row["sources"]:
            values.update({("id", source["id"]), ("work", source["group_id"]),
                           ("content", source["sha256"])})
        identities[rid] = values
        for value in values:
            if value in owner:
                union(rid, owner[value])
            else:
                owner[value] = rid
    components = {}
    for rid in sorted(parent):
        components.setdefault(root(rid), []).append(rid)
    assignment, group_refs = {}, {}
    for members in components.values():
        keys = sorted(set().union(*(identities[rid] for rid in members)))
        group_hash = digest(canonical(keys))
        bucket = int(digest(canonical([config["seed"], group_hash])), 16) / (1 << 256)
        split = ("train" if bucket < ratios["train"] else "val"
                 if bucket < ratios["train"] + ratios["val"] else "test")
        for rid in members:
            assignment[rid], group_refs[rid] = split, group_hash
    frozen = copy.deepcopy(sorted(rows, key=lambda row: row["row_id"]))
    counts, task_counts = Counter(), {key: Counter() for key in ratios}
    for row in frozen:
        row["split"] = assignment[row["row_id"]]
        counts[row["split"]] += 1
        task_counts[row["split"]][row["task"]] += 1
    projection = compile_candidates(frozen)
    deficits = {key: max(0, minima[key] - counts[key]) for key in sorted(minima)}
    status = "FROZEN_CANDIDATE" if not any(deficits.values()) else "REJECTED_SUPPORT"
    payload = {"schema_version": "athanor.candidate_freeze.v1", "status": status,
               "training_authorized": False, "config": config,
               "input_sha256": digest(canonical(sorted(rows, key=lambda row: row["row_id"]))),
               "groups": dict(sorted(group_refs.items())), "group_count": len(components),
               "split_counts": {key: counts[key] for key in sorted(ratios)},
               "task_counts": {key: dict(sorted(task_counts[key].items())) for key in sorted(ratios)},
               "support_deficits": deficits, "projection": projection,
               "unresolved": ["REVIEWED_ANSWERS", "RIGHTS", "COMPLETE_WORK_IDENTITIES",
                              "NEAR_DUPLICATE_REVIEW", "PER_TASK_EVAL_SUPPORT", "TRAIN_APPROVAL"]}
    return {**payload, "freeze_sha256": digest(canonical(payload))}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        for path in (args.input, args.config):
            if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
                raise ValueError("Missing, unsafe or oversized input")
        rows = [_json(line) for line in args.input.read_bytes().splitlines() if line.strip()]
        result = freeze_candidates(rows, _json(args.config.read_bytes()))
    except (ValueError, TypeError, KeyError, OSError, RecursionError) as exc:
        print(json.dumps({"status": "INVALID", "reason": str(exc), "training_authorized": False}))
        return 1
    print(canonical(result))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
