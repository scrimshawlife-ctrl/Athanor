#!/usr/bin/env python3
"""
Batch JEV Harvester — fetches PD content from Gutenberg, extracts candidates,
runs JEV rerank, appends approved atoms, generates pairs for target family.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from html import unescape
from collections import defaultdict

# Gutenberg ID configs for families at floor 31
FAMILY_CONFIGS = {
    "theosophy_pd": {
        "gutenberg_ids": ["60852", "54488", "17009", "6687", "8578", "55618", "54824"],
        "keywords": ["theosophy", "blavatsky", "secret doctrine", "is unveiled", "cosmic", "karma", "reincarnation", "masters", "adept", "esoteric", "occult", "spiritual", "evolution", "root race", "manvantara"]
    },
    "buddhism_esoteric_pd": {
        "gutenberg_ids": ["15255", "6507", "5286", "16841", "16842"],
        "keywords": ["buddhism", "dharma", "sutra", "tibet", "vajrayana", "mantra", "mandala", "bodhisattva", "nirvana", "meditation", "tantra", "lama", "dalai", "samsara"]
    },
    "golden_dawn_hist": {
        "gutenberg_ids": ["47865", "45736", "38579"],
        "keywords": ["golden dawn", "macgregor", "westcott", "waite", "crowley", "mathers", "rosicrucian", "hermetic", "qabalah", "tarot", "enochian", "ritual", "grade", "adeptus"]
    },
    "jyotish_anchors": {
        "gutenberg_ids": ["40918", "25455", "40723"],
        "keywords": ["jyotish", "astrology", "vedic", "hindu", "planet", "nakshatra", "dasha", "bhava", "rasi", "graha", "yoga", "kundali", "horoscope", "predict"]
    },
    "alchemy_spirit": {
        "gutenberg_ids": ["48385", "41520", "41521", "38429"],
        "keywords": ["alchemy", "hermetic", "philosopher stone", "elixir", "transmutation", "mercury", "sulfur", "salt", "vessel", "furnace", "opus", "magnum", "rubedo", "albedo", "nigredo"]
    },
    "goetia_catalog": {
        "gutenberg_ids": ["72679"],  # Already used for grimoire_other
        "keywords": ["goetia", "solomon", "spirit", "seal", "demon", "invocation", "evocation", "conjuration", "pentacle", "triangle", "circle", "sigil", "king", "prince", "duke"]
    },
    "coptic_gnostic": {
        "gutenberg_ids": ["45360", "31836", "28232"],
        "keywords": ["gnostic", "coptic", "nag hammadi", "valentinus", "basilides", "simon magus", "pistis sophia", "archon", "aeon", "pleroma", "demiurge", "sophia", "yaldabaoth"]
    },
    "veda_upanishad_pd": {
        "gutenberg_ids": ["3030", "3059", "3064", "3068", "3072"],
        "keywords": ["upaniṣad", "upanishad", "veda", "brahman", "atman", "om", "karma", "moksha", "dharma", "yoga", "vedanta", "self", "absolute", "consciousness"]
    },
    "mesoamerica": {
        "gutenberg_ids": ["12827", "13067", "34343"],
        "keywords": ["aztec", "maya", "mexica", "quetzalcoatl", "tzolkin", "calendar", "codex", "nahuatl", "teotihuacan", "tenochtitlan", "sacrifice", "pyramid", "god", "ritual"]
    },
    "runes_eddic": {
        "gutenberg_ids": ["57642", "2627", "4747"],
        "keywords": ["rune", "eddic", "poetic edda", "prose edda", "snorri", "odin", "thor", "freya", "loki", "valhalla", "yggdrasil", "ragnarok", "nidhogg", "mimir", "huginn", "muninn"]
    },
    "arbatel": {
        "gutenberg_ids": ["47583"],  # May need esoteric archives
        "keywords": ["arbatel", "olympic spirit", "arbatel of magic", "phul", "hagith", "och", "ophiel", "bethor", "phaleg", "arathon", "seal", "character"]
    },
    "andes_amazon": {
        "gutenberg_ids": ["17607", "10794", "17123"],
        "keywords": ["andes", "inca", "peru", "amazon", "shaman", "ayahuasca", "curandero", "pachamama", "inti", "villac umu", "cuzco", "machu picchu", "quipu"]
    },
    "astrology_west": {
        "gutenberg_ids": ["25074", "47120", "47121"],
        "keywords": ["astrology", "horoscope", "zodiac", "planet", "house", "aspect", "transit", "progression", "natal", "chart", "ascendant", "midheaven", "dignity", "exaltation"]
    },
    "tarot_history": {
        "gutenberg_ids": ["10403", "43117"],
        "keywords": ["tarot", "major arcana", "minor arcana", "trump", "fool", "magician", "high priestess", "empress", "emperor", "hierophant", "lovers", "chariot", "strength", "hermit"]
    },
    "chaos_spare_hist": {
        "gutenberg_ids": ["47584", "47585"],
        "keywords": ["chaos magic", "austin spare", "sigil", "gnosis", "servitor", "ego", "belief", "paradigm", "meta", "chaosphere", "peter carroll", "ray sherwin"]
    },
    "mesopotamia": {
        "gutenberg_ids": ["17170", "2951", "40215"],
        "keywords": ["sumer", "babylon", "akkad", "gilgamesh", "enuma elish", "ishtar", "marduk", "enlil", "ea", "cuneiform", "tablet", "ziggurat", "priest", "temple", "ritual"]
    },
    "shinto_onmyodo": {
        "gutenberg_ids": ["46823", "40216"],
        "keywords": ["shinto", "onmyodo", "kami", "shrine", "matsuri", "ofuda", "onmyoji", "abeno seimei", "divination", "omikuji", "yorishiro", "heaven", "earth", "spirit"]
    }
}

def fetch_gutenberg(gid):
    """Fetch Gutenberg HTML and extract text."""
    url = f"https://www.gutenberg.org/files/{gid}/{gid}-h/{gid}-h.htm"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        
        # Extract text
        text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.I)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        text = unescape(text)
        text = re.sub(r"\s+", " ", text).strip()
        
        if len(text) < 1000:
            return None
        return text
    except Exception as e:
        print(f"  Failed to fetch {gid}: {e}", file=sys.stderr)
        return None

def chunk_text(text, family, source_url, min_len=400, max_len=1400, overlap=100):
    """Split text into overlapping chunks with keywords."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    current = ""
    for s in sentences:
        current += " " + s
        if len(current) > max_len:
            clean = re.sub(r"\s+", " ", current).strip()[:max_len]
            if len(clean) >= min_len:
                chunks.append(clean)
            current = current[-overlap:] if overlap > 0 else ""
    
    # Filter for family-relevant chunks
    keywords = FAMILY_CONFIGS.get(family, {}).get("keywords", [])
    filtered = []
    for c in chunks:
        if any(kw.lower() in c.lower() for kw in keywords):
            filtered.append({
                "text": c,
                "family_id": family,
                "source_url": source_url,
                "provenance": "OBSERVED primary PD",
                "content_hash": hashlib.sha256(c.encode()).hexdigest()[:12]
            })
    return filtered

def run_jev(candidates, min_relevance=0.5):
    """Run JEV rerank on candidates."""
    if not candidates:
        return []
    
    # Add deterministic IDs
    for c in candidates:
        if "id" not in c:
            c["id"] = c.get("content_hash", hashlib.sha256(c["text"].encode()).hexdigest()[:12])
    
    payload = {
        "query": "High quality primary PD historical mystical text atom: clean provenance, relevant family, no junk, OBSERVED suitable.",
        "candidates": [{"id": c["id"], "text": c["text"] + " family:" + c["family_id"]} for c in candidates],
        "top_k": len(candidates)
    }
    
    try:
        proc = subprocess.run(["jev", "rerank"], input=json.dumps(payload), 
                            capture_output=True, text=True, timeout=60)
        if proc.returncode != 0:
            print(f"  JEV failed: {proc.stderr}", file=sys.stderr)
            return []
        result = json.loads(proc.stdout)
        selected = set(result.get("selected_ids", []))
        scores = result.get("scores", {})
        
        approved = []
        for c in candidates:
            cid = c["id"]
            if cid in selected and scores.get(cid, {}).get("relevance", 0) >= min_relevance:
                approved.append(c)
        return approved
    except Exception as e:
        print(f"  JEV error: {e}", file=sys.stderr)
        return []

def append_atoms(atoms, atoms_path):
    """Append atoms to corpus."""
    with open(atoms_path, "a") as f:
        for a in atoms:
            f.write(json.dumps(a) + "\n")
    return len(atoms)

def gen_pairs_for_family(family, atoms_path, pairs_path):
    """Generate pairs for new atoms of this family only."""
    # Load existing atom_ids with pairs
    existing = set()
    if os.path.exists(pairs_path):
        with open(pairs_path) as f:
            for line in f:
                p = json.loads(line)
                if p.get("family_id") == family:
                    existing.add(p.get("atom_id"))
    
    # Find new atoms
    new_atoms = []
    with open(atoms_path) as f:
        for line in f:
            a = json.loads(line)
            if a.get("family_id") == family and a.get("atom_id") not in existing:
                new_atoms.append(a)
    
    if not new_atoms:
        return 0
    
    ROLES = ["planet", "element", "symbol", "concept", "text", "letter", "practice"]
    new_pairs = []
    for i, atom in enumerate(new_atoms):
        role = ROLES[i % len(ROLES)]
        pair = {
            "pair_id": f"corr.{family}.{role}.{hashlib.sha256((family+"."+role+"."+atom.get("atom_id","")).encode()).hexdigest()[:6]}"." + role + "." + atom.get(\"atom_id\", \"\")).encode()).hexdigest()[:6]}".{role}.{atom.get("atom_id","")}'.encode()).hexdigest()[:6]}",
            "family_id": family,
            "role": role,
            "filler": " ".join(atom.get("text","").split()[:10]),
            "span": " ".join(atom.get("text","").split()[10:20]) if len(atom.get("text","").split()) > 10 else atom.get("text","")[:50],
            "atom_id": atom.get("atom_id"),
            "epistemic": "OBSERVED"
        }
        new_pairs.append(pair)
    
    with open(pairs_path, "a") as f:
        for p in new_pairs:
            f.write(json.dumps(p) + "\n")
    
    return len(new_pairs)

def harvest_family(family, min_relevance=0.5):
    """Full harvest pipeline for one family."""
    config = FAMILY_CONFIGS.get(family, {})
    gutenberg_ids = config.get("gutenberg_ids", [])
    
    if not gutenberg_ids:
        print(f"  No Gutenberg IDs configured for {family}")
        return 0, 0
    
    all_candidates = []
    for gid in gutenberg_ids:
        print(f"  Fetching {gid}...")
        text = fetch_gutenberg(gid)
        if text:
            source_url = f"https://www.gutenberg.org/files/{gid}/{gid}-h/{gid}-h.htm"
            cands = chunk_text(text, family, source_url)
            all_candidates.extend(cands)
            print(f"    {len(cands)} candidates")
        time.sleep(1)
    
    print(f"  Total candidates: {len(all_candidates)}")
    if not all_candidates:
        return 0, 0
    
    approved = run_jev(all_candidates, min_relevance)
    print(f"  JEV approved: {len(approved)}")
    
    if not approved:
        return 0, 0
    
    atoms_path = os.path.expanduser("~/.athanor/corpus/atoms.jsonl")
    pairs_path = "fixtures/correspondence/pairs.p3a.jsonl"
    
    atoms_added = append_atoms(approved, atoms_path)
    pairs_added = gen_pairs_for_family(family, atoms_path, pairs_path)
    
    return atoms_added, pairs_added

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", required=True)
    parser.add_argument("--min-relevance", type=float, default=0.5)
    args = parser.parse_args()
    
    if args.family not in FAMILY_CONFIGS:
        print(f"Unknown family: {args.family}")
        sys.exit(1)
    
    print(f"=== Harvesting {args.family} ===")
    atoms, pairs = harvest_family(args.family, args.min_relevance)
    print(f"=== {args.family} complete: +{atoms} atoms, +{pairs} pairs ===")

if __name__ == "__main__":
    main()