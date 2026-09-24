#!/usr/bin/env python3
"""
Generate pairs for NEW atoms of a specific family only.
Appends to existing pairs.p3a.jsonl - does NOT regenerate all pairs.
"""
import argparse
import hashlib
import json
import os

ROLES = ["planet", "element", "symbol", "concept", "text", "letter", "practice"]

def generate_pair_id(family, role, atom_id):
    seed = f"{family}.{role}.{atom_id}"
    return f"corr.{family}.{role}.{hashlib.sha256(seed.encode()).hexdigest()[:6]}"

def generate_filler(text, max_len=200):
    words = text.split()
    return " ".join(words[:max_len // 5])

def generate_span(text, max_len=200):
    words = text.split()
    if len(words) <= max_len // 5:
        return text[:max_len]
    mid = len(words) // 2
    return " ".join(words[mid:mid + max_len // 5])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", required=True, help="Family ID to generate pairs for")
    parser.add_argument("--atoms", default=os.path.expanduser("~/.athanor/corpus/atoms.jsonl"))
    parser.add_argument("--pairs", default="fixtures/correspondence/pairs.p3a.jsonl")
    parser.add_argument("--start-index", type=int, default=0, help="Skip first N atoms (for existing pairs)")
    args = parser.parse_args()

    # Load existing pair atom_ids for this family to avoid duplicates
    existing_atom_ids = set()
    if os.path.exists(args.pairs):
        with open(args.pairs) as f:
            for line in f:
                line = line.strip()
                if line:
                    p = json.loads(line)
                    if p.get("family_id") == args.family:
                        existing_atom_ids.add(p.get("atom_id"))

    print(f"Existing atoms with pairs for {args.family}: {len(existing_atom_ids)}")

    # Load new atoms for this family
    new_atoms = []
    with open(args.atoms) as f:
        for line in f:
            line = line.strip()
            if line:
                a = json.loads(line)
                if a.get("family_id") == args.family and a.get("atom_id") not in existing_atom_ids:
                    new_atoms.append(a)

    print(f"New atoms to pair for {args.family}: {len(new_atoms)}")

    if not new_atoms:
        print("No new atoms to process")
        return

    # Sort for determinism
    new_atoms.sort(key=lambda a: a.get("atom_id", ""))

    # Generate pairs
    new_pairs = []
    for i, atom in enumerate(new_atoms):
        role = ROLES[i % len(ROLES)]
        pair = {
            "pair_id": generate_pair_id(args.family, role, atom.get("atom_id", "")),
            "family_id": args.family,
            "role": role,
            "filler": generate_filler(atom.get("text", "")),
            "span": generate_span(atom.get("text", "")),
            "atom_id": atom.get("atom_id", f"pd.{args.family}.{hashlib.sha256(atom.get('text','').encode()).hexdigest()[:8]}"),
            "epistemic": "OBSERVED"
        }
        new_pairs.append(pair)

    # Append to existing pairs file
    with open(args.pairs, "a") as f:
        for p in new_pairs:
            f.write(json.dumps(p) + "\n")

    print(f"Appended {len(new_pairs)} new pairs for {args.family}")

    # Verify total
    from collections import Counter
    fam_counts = Counter()
    with open(args.pairs) as f:
        for line in f:
            line = line.strip()
            if line:
                p = json.loads(line)
                fam_counts[p.get("family_id")] += 1
    print(f"Total pairs for {args.family}: {fam_counts.get(args.family, 0)}")

if __name__ == "__main__":
    main()