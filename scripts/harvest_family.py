#!/usr/bin/env python3
"""
Harvest a family: fetch PD sources → chunk → JEV rerank → append atoms → gen pairs.
Single command per family. JEV-only constraint enforced.
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

# Family configurations: supports multiple source types
FAMILY_CONFIGS = {
    "runes_eddic": {
        "sources": [
            {"type": "sacred_texts", "url": "https://www.sacred-texts.com/neu/poe/poe00.htm"},
            {"type": "sacred_texts", "url": "https://www.sacred-texts.com/neu/poe/poe01.htm"},
            {"type": "sacred_texts", "url": "https://www.sacred-texts.com/neu/poe/poe02.htm"},
            {"type": "gutenberg", "id": "57642"},
            {"type": "gutenberg", "id": "2627"},
            {"type": "gutenberg", "id": "4747"},
        ],
        "keywords": ["rune", "eddic", "poetic edda", "prose edda", "snorri", "odin", "thor", "freya", "loki", "valhalla", "yggdrasil", "ragnarok", "nidhogg", "mimir", "huginn", "muninn", "stanza", "verse", "skald"],
        "jev_query": "Primary source Edda stanza, Old Norse mythology, poetic kennings, skaldic verse, OBSERVED suitable.",
        "min_relevance": 0.3
    },
    "arbatel": {
        "sources": [
            {"type": "gutenberg", "id": "47583"},
            {"type": "sacred_texts", "url": "https://www.esotericarchives.com/arbatel/arbatel.htm"},
        ],
        "keywords": ["arbatel", "olympic spirit", "phul", "hagith", "och", "ophiel", "bethor", "phaleg", "arathon", "seal", "character", "magic"],
        "jev_query": "Primary source Arbatel of Magic, Olympic spirits, ceremonial magic, OBSERVED suitable.",
        "min_relevance": 0.5
    },
    "golden_dawn_hist": {
        "sources": [
            {"type": "gutenberg", "id": "47865"},
            {"type": "gutenberg", "id": "45736"},
            {"type": "gutenberg", "id": "38579"},
            {"type": "sacred_texts", "url": "https://www.sacred-texts.com/oto/gd.htm"},
        ],
        "keywords": ["golden dawn", "macgregor", "westcott", "waite", "crowley", "mathers", "rosicrucian", "hermetic", "qabalah", "tarot", "enochian", "ritual", "grade", "adeptus"],
        "jev_query": "Primary source Golden Dawn history, Hermetic Order, ceremonial magic, OBSERVED suitable.",
        "min_relevance": 0.5
    },
    "jyotish_anchors": {
        "sources": [
            {"type": "gutenberg", "id": "40918"},
            {"type": "gutenberg", "id": "25455"},
            {"type": "gutenberg", "id": "40723"},
        ],
        "keywords": ["jyotish", "astrology", "vedic", "hindu", "planet", "nakshatra", "dasha", "bhava", "rasi", "graha", "yoga", "kundali", "horoscope"],
        "jev_query": "Primary source Vedic astrology (Jyotish), planetary positions, nakshatras, dashas, OBSERVED suitable.",
        "min_relevance": 0.5
    },
    "andes_amazon": {
        "sources": [
            {"type": "gutenberg", "id": "17607"},
            {"type": "gutenberg", "id": "10794"},
            {"type": "gutenberg", "id": "17123"},
        ],
        "keywords": ["andes", "inca", "peru", "amazon", "shaman", "ayahuasca", "curandero", "pachamama", "inti", "villac umu", "cuzco", "machu picchu", "quipu"],
        "jev_query": "Primary source Andean/Amazonian spirituality, shamanism, ayahuasca, Inca cosmology, OBSERVED suitable.",
        "min_relevance": 0.5
    },
    "astrology_west": {
        "sources": [
            {"type": "gutenberg", "id": "25074"},
            {"type": "gutenberg", "id": "47120"},
            {"type": "gutenberg", "id": "47121"},
        ],
        "keywords": ["astrology", "horoscope", "zodiac", "planet", "house", "aspect", "transit", "progression", "natal", "chart", "ascendant", "midheaven", "dignity", "exaltation"],
        "jev_query": "Primary source Western astrology, natal charts, planetary aspects, houses, OBSERVED suitable.",
        "min_relevance": 0.5
    },
    "tarot_history": {
        "sources": [
            {"type": "gutenberg", "id": "10403"},
            {"type": "gutenberg", "id": "43117"},
            {"type": "sacred_texts", "url": "https://www.sacred-texts.com/tarot/pkt/pkt00.htm"},
        ],
        "keywords": ["tarot", "major arcana", "minor arcana", "trump", "fool", "magician", "high priestess", "empress", "emperor", "hierophant", "lovers", "chariot", "strength", "hermit"],
        "jev_query": "Primary source Tarot history, Major Arcana symbolism, card meanings, OBSERVED suitable.",
        "min_relevance": 0.5
    },
    "chaos_spare_hist": {
        "sources": [
            {"type": "gutenberg", "id": "47584"},
            {"type": "gutenberg", "id": "47585"},
            {"type": "sacred_texts", "url": "https://www.esotericarchives.com/spare/spare.htm"},
        ],
        "keywords": ["chaos magic", "austin spare", "sigil", "gnosis", "servitor", "ego", "belief", "paradigm", "meta", "chaosphere", "peter carroll", "ray sherwin"],
        "jev_query": "Primary source Chaos magic, Austin Spare, sigil craft, gnosis, OBSERVED suitable.",
        "min_relevance": 0.5
    },
    "mesopotamia": {
        "sources": [
            {"type": "gutenberg", "id": "17170"},
            {"type": "gutenberg", "id": "2951"},
            {"type": "gutenberg", "id": "40215"},
            {"type": "sacred_texts", "url": "https://www.sacred-texts.com/ane/sum/sum00.htm"},
        ],
        "keywords": ["sumer", "babylon", "akkad", "gilgamesh", "enuma elish", "ishtar", "marduk", "enlil", "ea", "cuneiform", "tablet", "ziggurat", "priest", "temple"],
        "jev_query": "Primary source Mesopotamian mythology, Gilgamesh, Enuma Elish, cuneiform tablets, OBSERVED suitable.",
        "min_relevance": 0.5
    },
    "alchemy_spirit": {
        "sources": [
            {"type": "gutenberg", "id": "48385"},
            {"type": "gutenberg", "id": "41520"},
            {"type": "gutenberg", "id": "41521"},
            {"type": "gutenberg", "id": "38429"},
            {"type": "sacred_texts", "url": "https://www.sacred-texts.com/alchemy/ha/ha00.htm"},
        ],
        "keywords": ["alchemy", "hermetic", "philosopher stone", "elixir", "transmutation", "mercury", "sulfur", "salt", "vessel", "furnace", "opus", "magnum", "rubedo", "albedo", "nigredo"],
        "jev_query": "Primary source alchemical texts, transmutation, philosopher's stone, hermetic philosophy, OBSERVED suitable.",
        "min_relevance": 0.5
    },
    "goetia_catalog": {
        "sources": [
            {"type": "gutenberg", "id": "72679"},
            {"type": "sacred_texts", "url": "https://www.sacred-texts.com/grim/lks/lks00.htm"},
        ],
        "keywords": ["goetia", "solomon", "spirit", "seal", "demon", "invocation", "evocation", "conjuration", "pentacle", "triangle", "circle", "sigil", "king", "prince", "duke"],
        "jev_query": "Primary source Goetia/Lesser Key of Solomon, spirit seals, invocations, OBSERVED suitable.",
        "min_relevance": 0.5
    },
    "coptic_gnostic": {
        "sources": [
            {"type": "gutenberg", "id": "45360"},
            {"type": "gutenberg", "id": "31836"},
            {"type": "gutenberg", "id": "28232"},
            {"type": "sacred_texts", "url": "https://www.sacred-texts.com/chr/gnostic.htm"},
        ],
        "keywords": ["gnostic", "coptic", "nag hammadi", "valentinus", "basilides", "simon magus", "pistis sophia", "archon", "aeon", "pleroma", "demiurge", "sophia", "yaldabaoth"],
        "jev_query": "Primary source Gnostic/Coptic texts, Nag Hammadi, Pistis Sophia, aeons, archons, OBSERVED suitable.",
        "min_relevance": 0.5
    },
    "veda_upanishad_pd": {
        "sources": [
            {"type": "gutenberg", "id": "3030"},
            {"type": "gutenberg", "id": "3059"},
            {"type": "gutenberg", "id": "3064"},
            {"type": "gutenberg", "id": "3068"},
            {"type": "gutenberg", "id": "3072"},
        ],
        "keywords": ["upaniṣad", "upanishad", "veda", "brahman", "atman", "om", "karma", "moksha", "dharma", "yoga", "vedanta", "self", "absolute", "consciousness"],
        "jev_query": "Primary source Upanishad/Vedic texts, Brahman, Atman, Vedanta philosophy, OBSERVED suitable.",
        "min_relevance": 0.5
    },
    "mesoamerica": {
        "sources": [
            {"type": "gutenberg", "id": "12827"},
            {"type": "gutenberg", "id": "13067"},
            {"type": "gutenberg", "id": "34343"},
            {"type": "sacred_texts", "url": "https://www.sacred-texts.com/latin/pop/pop00.htm"},
        ],
        "keywords": ["aztec", "maya", "mexica", "quetzalcoatl", "tzolkin", "calendar", "codex", "nahuatl", "teotihuacan", "tenochtitlan", "sacrifice", "pyramid", "god", "ritual"],
        "jev_query": "Primary source Mesoamerican/Aztec/Maya cosmology, calendars, deities, rituals, OBSERVED suitable.",
        "min_relevance": 0.5
    },
    "shinto_onmyodo": {
        "sources": [
            {"type": "gutenberg", "id": "46823"},
            {"type": "gutenberg", "id": "40216"},
            {"type": "sacred_texts", "url": "https://www.sacred-texts.com/shi/kj/kj00.htm"},
        ],
        "keywords": ["shinto", "onmyodo", "kami", "shrine", "matsuri", "ofuda", "onmyoji", "abeno seimei", "divination", "omikuji", "yorishiro"],
        "jev_query": "Primary source Shinto/Onmyodo texts, kami, divination, onmyoji practices, OBSERVED suitable.",
        "min_relevance": 0.5
    }
}

DEFAULT_QUERY = "High quality primary PD historical mystical text atom: clean provenance, relevant family, no junk, OBSERVED suitable."

def fetch_gutenberg(gid):
    url = f"https://www.gutenberg.org/files/{gid}/{gid}-h/{gid}-h.htm"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.I)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        text = unescape(text)
        text = re.sub(r"\s+", " ", text).strip()
        return text if len(text) > 1000 else None
    except Exception as e:
        print(f"  Failed {gid}: {e}", file=sys.stderr)
        return None

def chunk_text(text, family, source_url, min_len=300, max_len=1400):
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    current = ""
    for s in sentences:
        current += " " + s
        if len(current) > max_len:
            clean = re.sub(r"\s+", " ", current).strip()[:max_len]
            if len(clean) >= min_len:
                chunks.append(clean)
            current = ""
    config = FAMILY_CONFIGS.get(family, {})
    keywords = config.get("keywords", [])
    filtered = []
    for c in chunks:
        if any(kw.lower() in c.lower() for kw in keywords):
            filtered.append({
                "text": c, "family_id": family, "source_url": source_url,
                "provenance": "OBSERVED primary PD",
                "content_hash": hashlib.sha256(c.encode()).hexdigest()[:12]
            })
    return filtered

def run_jev(candidates, family):
    if not candidates:
        return []
    for c in candidates:
        if "id" not in c:
            c["id"] = c.get("content_hash", hashlib.sha256(c["text"].encode()).hexdigest()[:12])
    config = FAMILY_CONFIGS.get(family, {})
    query = config.get("jev_query", DEFAULT_QUERY)
    payload = {
        "query": query,
        "candidates": [{"id": c["id"], "text": c["text"] + " family:" + c["family_id"]} for c in candidates],
        "top_k": len(candidates)
    }
    try:
        proc = subprocess.run(["jev", "rerank"], input=json.dumps(payload), capture_output=True, text=True, timeout=60)
        if proc.returncode != 0:
            print(f"  JEV failed: {proc.stderr}", file=sys.stderr)
            return []
        result = json.loads(proc.stdout)
        selected = set(result.get("selected_ids", []))
        scores = result.get("scores", {})
        approved = [c for c in candidates if c["id"] in selected and scores.get(c["id"], {}).get("relevance", 0) >= 0.5]
        return approved
    except Exception as e:
        print(f"  JEV error: {e}", file=sys.stderr)
        return []

def append_atoms(atoms, atoms_path):
    with open(atoms_path, "a") as f:
        for a in atoms:
            f.write(json.dumps(a) + "\n")
    return len(atoms)

def gen_pairs_for_family(family, atoms_path, pairs_path):
    existing = set()
    if os.path.exists(pairs_path):
        with open(pairs_path) as f:
            for line in f:
                p = json.loads(line)
                if p.get("family_id") == family:
                    existing.add(p.get("atom_id"))
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
            "pair_id": f"corr.{family}.{role}.{hashlib.sha256((family + '.' + role + '.' + atom.get('atom_id','')).encode()).hexdigest()[:6]}",
            "family_id": family, "role": role,
            "filler": " ".join(atom.get("text","").split()[:10]),
            "span": " ".join(atom.get("text","").split()[10:20]) if len(atom.get("text","").split()) > 10 else atom.get("text","")[:50],
            "atom_id": atom.get("atom_id"), "epistemic": "OBSERVED"
        }
        new_pairs.append(pair)
    with open(pairs_path, "a") as f:
        for p in new_pairs:
            f.write(json.dumps(p) + "\n")
    return len(new_pairs)

def harvest_family(family):
    config = FAMILY_CONFIGS.get(family)
    if not config:
        print(f"Unknown family: {family}", file=sys.stderr)
        return 0, 0
    gutenberg_ids = config.get("gutenberg_ids", [])
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
    approved = run_jev(all_candidates, family)
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
    parser.add_argument("--family", required=True, choices=list(FAMILY_CONFIGS.keys()))
    args = parser.parse_args()
    print(f"=== Harvesting {args.family} ===")
    atoms, pairs = harvest_family(args.family)
    print(f"=== {args.family} complete: +{atoms} atoms, +{pairs} pairs ===")

if __name__ == "__main__":
    main()