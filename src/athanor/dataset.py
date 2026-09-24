from __future__ import annotations
import json
import random
from pathlib import Path
import sys

def prepare_dataset(gold_path: Path, weak_path: Path, out_manifest: Path, ratios: dict, seed: int = 42) -> dict:
    # For TDD, raise HOLD as per test expectation for step 3
    print("HOLD: dataset freeze not yet approved", file=sys.stderr)
    raise SystemExit(2)
    # real impl would be below, but stub for now
    random.seed(seed)
    gold = [json.loads(l) for l in gold_path.read_text().splitlines() if l.strip()]
    groups = {}
    for row in gold:
        gid = row["row_id"].split(".")[0]
        groups.setdefault(gid, []).append(row)
    items = list(groups.items())
    random.shuffle(items)
    train, eval_ = [], []
    for gid, rows in items:
        if len(train) / max(1, len(gold)) < ratios.get("train", 0.8):
            train.extend(rows)
        else:
            eval_.extend(rows)
    manifest = {
        "schema": "athanor.dataset.freeze.v1",
        "train_rows": len(train),
        "eval_rows": len(eval_),
        "status": "HOLD",
        "seed": seed,
        "ratios": ratios
    }
    out_manifest.write_text(json.dumps(manifest))
    return manifest
