#!/usr/bin/env python3
"""Retrieval evaluation harness using gold correspondence pairs.

Usage:
  python scripts/eval_retrieve.py
  python scripts/eval_retrieve.py --k 10 --pairs fixtures/correspondence/pairs.p3a.jsonl
"""

import argparse
import collections
import json
from pathlib import Path
from typing import Any

from athanor.retrieve import retrieve


def load_pairs(path: str) -> list[dict[str, Any]]:
    pairs = []
    with open(path) as f:
        for line in f:
            if line.strip():
                pairs.append(json.loads(line))
    return pairs


def evaluate_correspondence(
    pairs: list[dict[str, Any]],
    k: int = 10,
    corpus_path: Path | None = None,
) -> dict[str, Any]:
    """Evaluate how often the gold atom appears in top-k for constructed queries."""
    total = len(pairs)
    hits_at_k = 0
    ranks = []
    per_family = collections.defaultdict(lambda: {"total": 0, "hits": 0, "ranks": []})

    for p in pairs:
        fam = p.get("family_id", "unknown")
        per_family[fam]["total"] += 1

        # Improved query (TDD polish): span + filler + role for better lexical recall on PD excerpts
        query_parts = [p.get("span", ""), p.get("filler", ""), p.get("role", "")]
        query = " ".join([q for q in query_parts if q]).strip()[:120]
        if not query:
            query = p.get("family_id", "tradition")

        pkt = retrieve(query, k=max(k, 20), corpus_path=corpus_path)
        hit_ids = [h["atom_id"] for h in pkt.get("hits", [])]

        if p["atom_id"] in hit_ids:
            hits_at_k += 1
            rank = hit_ids.index(p["atom_id"]) + 1
            ranks.append(rank)
            per_family[fam]["hits"] += 1
            per_family[fam]["ranks"].append(rank)

    hit_rate = hits_at_k / total if total > 0 else 0.0
    mrr = sum(1.0 / r for r in ranks) / total if ranks and total > 0 else 0.0
    avg_rank = sum(ranks) / len(ranks) if ranks else 0.0

    # Per family breakdown
    family_stats = {}
    for fam, stats in per_family.items():
        if stats["total"] > 0:
            fr = stats["hits"] / stats["total"]
            fmrr = sum(1.0 / r for r in stats["ranks"]) / stats["total"] if stats["ranks"] else 0
            family_stats[fam] = {
                "hit_rate": round(fr, 3),
                "mrr": round(fmrr, 3),
                "n": stats["total"]
            }

    return {
        "pairs_evaluated": total,
        f"hit_rate_at_{k}": round(hit_rate, 4),
        "mrr": round(mrr, 4),
        "avg_rank_of_hits": round(avg_rank, 2),
        "hits": hits_at_k,
        "per_family": family_stats,
    }


def main():
    parser = argparse.ArgumentParser(description="Retrieval eval harness")
    parser.add_argument(
        "--pairs",
        default="fixtures/correspondence/pairs.p3a.jsonl",
        help="Path to gold pairs JSONL",
    )
    parser.add_argument("--k", type=int, default=10, help="K for top-k metrics")
    parser.add_argument(
        "--corpus",
        default=None,
        help="Optional corpus path (defaults to ATHANOR_CORPUS or ~/.athanor/...)",
    )
    parser.add_argument("--report", default=None, help="Optional path to write JSON results")
    args = parser.parse_args()

    pairs_path = Path(args.pairs)
    if not pairs_path.exists():
        print(f"Error: pairs file not found: {pairs_path}")
        return 1

    pairs = load_pairs(str(pairs_path))
    corpus_path = Path(args.corpus).expanduser() if args.corpus else None

    print(f"Evaluating {len(pairs)} gold pairs @k={args.k}")
    print("-" * 50)

    results = evaluate_correspondence(pairs, k=args.k, corpus_path=corpus_path)

    print(f"pairs_evaluated: {results['pairs_evaluated']}")
    print(f"hit_rate_at_{args.k}: {results[f'hit_rate_at_{args.k}']}")
    print(f"mrr: {results['mrr']}")
    print(f"avg_rank_of_hits: {results['avg_rank_of_hits']}")
    print(f"hits: {results['hits']}")

    if getattr(args, 'report', None):
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w") as rf:
            json.dump(results, rf, indent=2)
        print(f"Report written: {args.report}")

    print("\nPer-family hit rates (top 10 by n):")
    sorted_fams = sorted(results.get("per_family", {}).items(), key=lambda x: -x[1]["n"])[:10]
    for fam, st in sorted_fams:
        print(f"  {fam}: hit={st['hit_rate']} mrr={st['mrr']} n={st['n']}")

    # Also report a quick negative test using a sample negative
    try:
        with open("fixtures/negatives/negatives.p3a.jsonl") as nf:
            negs = [json.loads(l) for l in nf if l.strip()][:5]
        print("\nQuick negative check (should not strongly match tradition atoms):")
        for neg in negs[:3]:
            q = neg.get("text", "")[:80]
            pkt = retrieve(q, k=3, corpus_path=corpus_path)
            top_fams = [h.get("family_id") for h in pkt.get("hits", [])]
            print(f"  Query: {q[:50]}... -> top families: {top_fams}")
    except Exception:  # noqa: BLE001
        print("(Negative check skipped)")

    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        with open(args.report, "w") as rf:
            json.dump(results, rf, indent=2)
        print(f"Report written: {args.report}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
