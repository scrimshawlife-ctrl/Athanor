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


def freeze_candidates(rows, config, overlap_groups=None):
    """Assign connected source/work/hash components, independent of input row order.

    This binds a proposed dataset's bytes and split choices. Human review,
    comprehensive work identities, near-duplicate detection and rights are external.
    Explicit existing splits are rejected to prevent silently moving a held-out set.
    """
    compile_candidates(rows)
    # Optional evidence is an additional identity, never a replacement for work IDs.
    # Values are declared grouping evidence, not authenticated review or authority.
    if overlap_groups is not None:
        source_ids = {s['id'] for row in rows for s in row['sources']}
        if not isinstance(overlap_groups, dict) or set(overlap_groups) != source_ids:
            raise ValueError('Overlap groups must cover exactly all candidate source IDs')
        if any(not isinstance(group, str) or not group.strip() for group in overlap_groups.values()):
            raise ValueError('Overlap group identities must be nonblank strings')
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
            if overlap_groups is not None:
                values.add(('overlap', overlap_groups[source['id']]))
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
    if overlap_groups is not None:
        payload['overlap_groups_sha256'] = digest(canonical(overlap_groups))
        payload['overlap_group_count'] = len(set(overlap_groups.values()))
        payload['unresolved'].append('OVERLAP_EVIDENCE_COMPLETENESS_AND_IDENTITY_REVIEW')
    return {**payload, "freeze_sha256": digest(canonical(payload))}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument('--overlap-groups', type=Path,
                        help='Complete JSON source-ID to reviewed overlap-group mapping; no approval implied')
    parser.add_argument('--overlap-registry', type=Path)
    parser.add_argument('--overlap-registry-sha256')
    parser.add_argument('--source-bindings', type=Path)
    args = parser.parse_args(argv)
    try:
        registry_args = [args.overlap_registry, args.overlap_registry_sha256, args.source_bindings]
        if any(registry_args) and (not all(registry_args) or args.overlap_groups):
            raise ValueError('Registry, digest and bindings required together; raw groups are mutually exclusive')
        for path in (args.input, args.config, *([args.overlap_groups] if args.overlap_groups else []),
                     *([args.source_bindings] if args.source_bindings else [])):
            if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
                raise ValueError("Missing, unsafe or oversized input")
        rows = [_json(line) for line in args.input.read_bytes().splitlines() if line.strip()]
        overlaps = _json(args.overlap_groups.read_bytes()) if args.overlap_groups else None
        if args.overlap_groups and not isinstance(overlaps, dict):
            raise ValueError('Overlap group file must be a JSON object')
        if args.overlap_registry:
            from athanor.adapter_overlap import freeze_with_registry
            result = freeze_with_registry(rows, _json(args.config.read_bytes()), args.overlap_registry,
                                          _json(args.source_bindings.read_bytes()), args.overlap_registry_sha256)
        else:
            result = freeze_candidates(rows, _json(args.config.read_bytes()), overlaps)
    except (ValueError, TypeError, KeyError, OSError, RecursionError) as exc:
        print(json.dumps({"status": "INVALID", "reason": str(exc), "training_authorized": False}))
        return 1
    print(canonical(result))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
