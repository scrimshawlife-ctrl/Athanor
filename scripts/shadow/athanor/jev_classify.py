#!/usr/bin/env python3
"""
Jev classify helper for Athanor harvests (T4-JEV-001 start).
Takes candidate jsonl (id, text, family), runs jev rerank, outputs high quality atoms.
Usage: cat candidates.jsonl | python jev_classify.py --min-relevance 0.7 > high.jsonl
Requires jev CLI in PATH.
"""
import sys, json, subprocess, argparse, hashlib

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-relevance", type=float, default=0.65)
    parser.add_argument("--query", default="High quality primary PD historical mystical text atom: clean provenance, relevant family, no junk, OBSERVED suitable.")
    args = parser.parse_args()

    candidates = [json.loads(line) for line in sys.stdin if line.strip()]
    if not candidates:
        return

    payload = {
        "query": args.query,
        "candidates": [{"id": c.get("id", c.get("atom_id")), "text": c["text"] + " family:" + c.get("family", c.get("family_id",""))} for c in candidates],
        "top_k": len(candidates)
    }

    try:
        proc = subprocess.run(["jev", "rerank"], input=json.dumps(payload), capture_output=True, text=True, timeout=30)
        if proc.returncode != 0:
            print("jev failed", proc.stderr, file=sys.stderr)
            return
        result = json.loads(proc.stdout)
        selected = set(result.get("selected_ids", []))
        scores = result.get("scores", {})
    except Exception as e:
        print("jev error", e, file=sys.stderr)
        return

    for c in candidates:
        cid = c.get("id", c.get("atom_id"))
        if cid in selected and scores.get(cid, {}).get("relevance", 0) >= args.min_relevance:
            # output as atom
            text = c["text"]
            atom = {
                "atom_id": c.get("atom_id", f"pd.{c.get('family','unk')}.{hashlib.sha256(text.encode()).hexdigest()[:8]}"),
                "family_id": c.get("family", c.get("family_id")),
                "type": "text",
                "text": text,
                "license": c.get("license", "public-domain"),
                "source_url": c.get("source_url", "researched"),
                "epistemic": "OBSERVED",
                "content_hash": hashlib.sha256(text.encode()).hexdigest()[:16],
                "lens_hints": {"historical": True, "symbolic": True, "operational": False}
            }
            print(json.dumps(atom))

if __name__ == "__main__":
    main()
