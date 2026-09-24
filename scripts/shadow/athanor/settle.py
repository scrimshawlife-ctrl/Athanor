#!/usr/bin/env python3
"""
Settle helper for Athanor (T4-JEV-002 deepened).
Reads quarantine cleaned.jsonl (with jev_relevance + suggested_settle),
applies jev rerank for additional evidence-bound scoring on settle candidates,
proposes final decisions (KEEP/DROP/HOLD) for operator review.
Usage: cat cleaned.jsonl | python settle.py --min-relevance 0.6 > settle_proposals.jsonl

All classifying via jev rerank + custom validation only.
"""

import argparse
import json
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-relevance", type=float, default=0.6)
    parser.add_argument("--query", default="Settle decision for PD historical mystical text: high quality, clean provenance, relevant to family, suitable for OBSERVED or INFERRED keep.")
    args = parser.parse_args()

    rows = [json.loads(line) for line in sys.stdin if line.strip()]
    if not rows:
        return

    # Prepare for jev rerank on settle candidates (those with jev or suggested)
    candidates = []
    for r in rows:
        text = r.get('inputs', {}).get('text', r.get('text', ''))
        fid = r.get('source_family', r.get('proposed_family', 'unknown'))
        suggested = r.get('suggested_settle', 'REVIEW')
        jev = r.get('jev_relevance', 0) or 0
        candidates.append({
            "id": r.get('atom_id', r.get('row_id')),
            "text": text[:2000] + f" family:{fid} suggested:{suggested} jev:{jev:.2f}",
            "row": r
        })

    if not candidates:
        return

    payload = {
        "query": args.query,
        "candidates": [{"id": c["id"], "text": c["text"]} for c in candidates],
        "top_k": len(candidates)
    }

    proposals = []
    try:
        proc = subprocess.run(
            ["jev", "rerank"],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if proc.returncode == 0:
            result = json.loads(proc.stdout)
            scores = result.get("scores", {})
            selected = set(result.get("selected_ids", []))
        else:
            scores = {}
            selected = set()
    except Exception as e:  # noqa: BLE001
        print(f"jev settle error: {e}", file=sys.stderr)
        scores = {}
        selected = set()

    for c in candidates:
        cid = c["id"]
        r = c["row"]
        jev_score = scores.get(cid, {}).get("relevance", r.get('jev_relevance', 0) or 0)
        base_suggested = r.get('suggested_settle', 'REVIEW')

        # Deepened decision: jev primary for evidence, custom for validation
        if jev_score >= args.min_relevance and cid in selected and base_suggested == 'KEEP':
            decision = 'KEEP'
            reason = f"high jev {jev_score:.2f} + suggested KEEP"
        elif jev_score < 0.4 or base_suggested == 'HOLD':
            decision = 'HOLD'
            reason = f"low jev {jev_score:.2f} or suggested HOLD"
        else:
            decision = 'REVIEW'
            reason = f"jev {jev_score:.2f} + suggested {base_suggested}"

        prop = {
            "atom_id": cid,
            "source_family": r.get('source_family'),
            "jev_relevance": jev_score,
            "base_suggested": base_suggested,
            "settle_decision": decision,
            "reason": reason,
            "route": r.get('route'),
            "flags": r.get('flags', []),
            "source_url": r.get('source_url')
        }
        proposals.append(prop)
        print(json.dumps(prop, ensure_ascii=False))

    # Summary to stderr
    decisions = {}
    for p in proposals:
        d = p['settle_decision']
        decisions[d] = decisions.get(d, 0) + 1
    print(f"\nSettle proposals: {decisions}", file=sys.stderr)


if __name__ == "__main__":
    main()