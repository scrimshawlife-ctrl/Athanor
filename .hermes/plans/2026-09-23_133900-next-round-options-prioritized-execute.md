# Plan: All Next Round Options by Priority + Execute (Athanor Corpus Quality)

**Date**: 2026-09-23  
**Slug**: next-round-options-prioritized-execute  
**Context**: Athanor esoteric PD corpus improvement (SHADOW lane, jev-only)

## Goal
Execute the highest-priority next round of Athanor pretrain corpus improvement: raise minimum gold pair family size from 12, deepen alchemy coverage, expand OOD negatives, enhance eval harness/doctor metrics, and complete full verification while preserving jev-only classification on primary PD OBSERVED sources with long coherent excerpts.

## Current Context / Assumptions
- Corpus state (read-only inspection): 3758 atoms, 1307 gold pairs (fixtures/correspondence/pairs.p3a.jsonl), 250 negatives (fixtures/negatives/negatives.p3a.jsonl), min pair family size = 12 (shinto_onmyodo:12; next: mesopotamia:13, grimoire_other:14, tarot_history:14, history_magic:14, golden_dawn_hist:15, grimoire:15, mesoamerica:15), alchemy_lab:309 pairs, mean excerpt 339.7 chars, long (>400ch) 14.9%.
- All classification/selection/harvest must use jev rerank exclusively (`scripts/shadow/athanor/jev_classify.py --min-relevance 0.5` fallback; 0.55 preferred). No custom logic for adds.
- Primary public-domain OBSERVED sources only (sacred-texts.com, archive.org, gutenberg.org, wikisource.org, newtonproject.ox.ac.uk). Firecrawl (export FIRECRAWL_API_KEY=...) or web_extract fallback.
- Longer excerpts (450-1400+ chars) prioritized for pretrain signal.
- Retrieval harness: `scripts/eval_retrieve.py --k 10` (per-family hit/ndcg, low callouts, OOD negative spillover).
- Doctor: `python -m athanor doctor --eval` or direct entrypoint (src/athanor/entrypoint.py).
- Full verification required every round: `python -m pytest -q --tb=no | tail -1` (must be 227 passed), `python -m ruff check src tests scripts/eval_retrieve.py`, `python specs/contracts/verify_review.py`.
- Branch: feat/continue-recommended-moves (PR #13 active). Commits use exact messages with counts/SHAs/metrics.
- No changes to gated paths (train, Hub, encoder weights, ALLOW_*).
- TDD for any code changes: write failing test first, run to confirm failure, implement minimally, run to pass.
- DRY/YAGNI: reuse existing extract/jev/add patterns; extend only where needed.

Assumptions for implementer:
- Working dir = /Users/appliedalchemylabs/Athanor
- Python 3 + required packages (pytest, ruff) available.
- jev CLI in PATH for classification.
- ~/.athanor/corpus/atoms.jsonl is the live corpus.
- All adds append to pairs.p3a.jsonl and atoms.jsonl with provenance (source_url, content_hash, epistemic=OBSERVED).
- If jev returns 0 high-relevance, hold (do not add low-quality data).

## Architecture / Proposed Approach
Prioritize rounds by impact on min pair family size + retrieval metrics (hit@10, ndcg, per-family) while expanding gold OOD for harness robustness. Use jev rerank as the sole gate for every candidate. Run targeted firecrawl/web_extract for fresh long PD excerpts on lowest families first, then alchemy. Extend harness/doctor only for observability of the current bottleneck (shinto + near-min families). Every round ends with exact verification commands + git add/commit (no push in this plan unless specified). Follow TDD for any harness/doctor changes.

Option prioritization (highest first):
1. Balance lowest pair families (shinto_onmyodo to >=15, then mesopotamia/grimoire/etc.) + alchemy deepen.
2. Expand gold negatives to 300+ with OOD diversity.
3. Further harness/doctor enhancements (more per-family sampling, dynamic thresholds).
4. Fresh source discovery + quality review round (firecrawl for new PD).
5. Full re-eval harness + docs sync + doctor validation.

This plan details execution of Option 1 (highest priority) as the "execute" round, with notes on how to chain to Option 2+.

## Step-by-Step Tasks (Option 1 - Highest Priority Round: Low Family Balance + Alchemy)

**Task 1: Inspect current state (read-only, 2 min)**
- Exact command (run in /Users/appliedalchemylabs/Athanor):
  ```
  python3 -c '
  import json, collections, os, statistics
  atoms = [json.loads(l) for l in open(os.path.expanduser("~/.athanor/corpus/atoms.jsonl")) if l.strip()]
  pairs = [json.loads(l) for l in open("fixtures/correspondence/pairs.p3a.jsonl") if l.strip()]
  fam_p = collections.Counter(p.get("family_id") for p in pairs)
  lengths = [len(a.get("text","")) for a in atoms]
  negs = len([l for l in open("fixtures/negatives/negatives.p3a.jsonl") if l.strip()])
  print("Atoms:", len(atoms), "Pairs:", len(pairs), "Negs:", negs)
  print("Min pair fam:", min(fam_p.values()))
  print("Lowest <=15:", sorted([(f,c) for f,c in fam_p.items() if c <=15], key=lambda x:x[1]))
  print("Alchemy_lab:", fam_p.get("alchemy_lab",0))
  print("shinto_onmyodo:", fam_p.get("shinto_onmyodo",0))
  print("Mean len:", round(statistics.mean(lengths),1), "Long%:", round(100*len([l for l in lengths if l>400])/len(lengths),1))
  '
  ```
- Expected output (example; capture exact):
  ```
  Atoms: 3758 Pairs: 1307 Negs: 250
  Min pair fam: 12
  Lowest <=15: [('shinto_onmyodo', 12), ('mesopotamia', 13), ...]
  Alchemy_lab: 309
  shinto_onmyodo: 12
  Mean len: 339.7 Long%: 14.9
  ```
- Verification: Copy output to plan notes. Do not mutate.

**Task 2: Update harness boosts if needed for new targets (TDD - 5 min)**
- Read current boosts (read-only):
  ```
  head -80 scripts/eval_retrieve.py | grep -A 20 "boosts ="
  ```
- Write failing test first (edit tests/test_eval_retrieve.py):
  Use exact patch or append. Add this test at end:
  ```python
  def test_evaluate_correspondence_shinto_boost_present():
      # TDD: verify shinto boost keywords exist for low family targeting
      with open("scripts/eval_retrieve.py") as f:
          content = f.read()
      assert "shinto_onmyodo" in content and "kami" in content, "shinto boost keywords missing"
      assert "mesopotamia" not in content or "gilgamesh" in content.lower()  # optional
  ```
- Run to verify failure:
  ```
  python -m pytest tests/test_eval_retrieve.py::test_evaluate_correspondence_shinto_boost_present -q --tb=short
  ```
- Expected before fix: FAIL (if keywords missing in this run; adjust).
- Then minimally implement (only if test fails): use read_file + targeted edit to add to boosts dict in scripts/eval_retrieve.py:
  ```python
  boosts = {
      "iching_daoist": ["hexagram", "trigram", "qian", "kun", "yi", "change"],
      "alchemy_lab": ["stone", "elixir", "hermetic", "philosopher", "sulphur", "gold"],
      "kabbalah_pd": ["sephiroth", "yetzirah", "zohar", "tree", "emanation", "sefirot"],
      "shinto_onmyodo": ["kami", "shinto", "kojiki", "onmyodo", "yin", "yang", "divination", "spirit", "ritual", "omikuji"],
      "hebrew_bible_magical": ["sephir", "razim", "raziel", "angels", "demons", "grimoire", "mysteries"],
      "mesopotamia": ["gilgamesh", "enki", "enuma", "elish", "babylon", "mesopotamia"],
      "grimoire": ["grimorium", "verum", "grand", "grimoire", "solomon", "pact"],
  }.get(fam, [])
  ```
- Re-run test:
  ```
  python -m pytest tests/test_eval_retrieve.py::test_evaluate_correspondence_shinto_boost_present -q --tb=no
  ```
- Expected: 1 passed.
- Run full relevant test:
  ```
  python -m pytest tests/test_eval_retrieve.py -q --tb=no | tail -1
  ```
- Expected: 227 passed (or current total).
- Commit (non-mutating in plan description): `git add tests/test_eval_retrieve.py scripts/eval_retrieve.py && git commit -m "test+harness: TDD shinto/meso/grimoire boosts for low family round"`

**Task 3: Discover and scrape fresh PD sources for lowest families + alchemy (read-only commands only, 5-10 min)**
- Export key (if using firecrawl):
  ```
  export FIRECRAWL_API_KEY=fc-...   # use actual; or skip for web_extract
  ```
- Search commands:
  ```
  firecrawl search "Kojiki full English Basil Hall Chamberlain public domain" --limit 3
  firecrawl search "Epic of Gilgamesh full text Langdon or Kovacs public domain" --limit 2
  firecrawl search "Grimorium Verum full English public domain sacred-texts" --limit 2
  firecrawl search "Agrippa Three Books of Occult Philosophy full text PD chapter" --limit 2
  firecrawl search "Hermetic Museum Waite full text PD sophic hydrolith" --limit 2
  ```
- Expected: URLs printed (sacred-texts.com/shi/kj, gutenberg.org/ebooks/18897, sacred-texts.com/grim, archive.org, etc.).
- Scrape 2-3 key pages (long text):
  ```
  firecrawl scrape "https://sacred-texts.com/shi/kj/index.htm" -o /tmp/kojiki_next.txt && wc -c /tmp/kojiki_next.txt
  firecrawl scrape "https://www.gutenberg.org/ebooks/18897" -o /tmp/gilgamesh_next.txt && wc -c /tmp/gilgamesh_next.txt
  firecrawl scrape "https://sacred-texts.com/grim/bcm/bcm20.htm" -o /tmp/grimorium_next.txt && wc -c /tmp/grimorium_next.txt
  firecrawl scrape "https://archive.org/stream/cu31924028928236/cu31924028928236_djvu.txt" -o /tmp/agrippa_next.txt && wc -c /tmp/agrippa_next.txt
  firecrawl scrape "https://sacred-texts.com/alc/hm1/hm101.htm" -o /tmp/hermetic_next.txt && wc -c /tmp/hermetic_next.txt
  ```
- Expected output example: "27900 /tmp/kojiki_next.txt" (sizes >8k chars preferred).

**Task 4: Extract long coherent excerpts (python one-liner style, 5 min)**
- Run extraction for each (exact script; saves /tmp/*_cands.jsonl):
  ```
  python3 << 'PYEOF'
  import json, re, hashlib
  def extract(text, family, source, minl=450, maxl=1400):
      text = re.sub(r'\s+', ' ', text)
      sents = re.split(r'(?<=[.!?])\s+', text)
      cur, ps = "", []
      for s in sents:
          if len(cur) + len(s) > maxl and len(cur) >= minl:
              ps.append(cur.strip()); cur = s
          else: cur += " " + s
      if len(cur) >= minl: ps.append(cur.strip())
      cands = []
      for p in ps[:80]:
          if len(p) < minl: continue
          cands.append({"family_id": family, "text": p[:maxl], "source_url": source, "content_hash": hashlib.sha256(p.encode()).hexdigest()[:16], "epistemic": "OBSERVED", "license": "PD", "role": "excerpt", "filler": ""})
      with open(f"/tmp/{family}_cands.jsonl", "w") as f:
          for c in cands: f.write(json.dumps(c)+"\n")
      print(f"Extracted {len(cands)} for {family}")
  with open("/tmp/kojiki_next.txt") as f: extract(f.read(), "shinto_onmyodo", "https://sacred-texts.com/shi/kj/index.htm")
  with open("/tmp/gilgamesh_next.txt") as f: extract(f.read(), "mesopotamia", "https://www.gutenberg.org/ebooks/18897")
  with open("/tmp/grimorium_next.txt") as f: extract(f.read(), "grimoire", "https://sacred-texts.com/grim/bcm/bcm20.htm")
  with open("/tmp/agrippa_next.txt") as f: extract(f.read(), "alchemy_lab", "https://archive.org/details/cu31924028928236", minl=500)
  with open("/tmp/hermetic_next.txt") as f: extract(f.read(), "alchemy_lab", "https://sacred-texts.com/alc/hm1/hm101.htm")
  PYEOF
  ```
- Expected: "Extracted 13 for shinto_onmyodo" etc. (numbers vary; capture).

**Task 5: Classify with jev (strict, 5 min)**
- For each family (try 0.55 first):
  ```
  cat /tmp/shinto_onmyodo_cands.jsonl | python scripts/shadow/athanor/jev_classify.py --min-relevance 0.55 > /tmp/high_shinto.jsonl && wc -l /tmp/high_shinto.jsonl
  cat /tmp/mesopotamia_cands.jsonl | python scripts/shadow/athanor/jev_classify.py --min-relevance 0.55 > /tmp/high_meso.jsonl && wc -l /tmp/high_meso.jsonl
  cat /tmp/grimoire_cands.jsonl | python scripts/shadow/athanor/jev_classify.py --min-relevance 0.55 > /tmp/high_grimoire.jsonl && wc -l /tmp/high_grimoire.jsonl
  cat /tmp/alchemy_lab_cands.jsonl | python scripts/shadow/athanor/jev_classify.py --min-relevance 0.55 > /tmp/high_alch.jsonl && wc -l /tmp/high_alch.jsonl
  ```
- If 0 lines: fallback (do not add if still 0):
  ```
  cat /tmp/shinto_onmyodo_cands.jsonl | python scripts/shadow/athanor/jev_classify.py --min-relevance 0.5 > /tmp/high_shinto.jsonl && wc -l /tmp/high_shinto.jsonl
  ```
- Expected on success: "N /tmp/high_*.jsonl" where N>0. On 0: "0 /tmp/high_*.jsonl" — log and skip add for that source (quality gate).

**Task 6: Add high-relevance atoms + gold pairs (if any high; 5 min)**
- Exact adder (only run if wc showed >0):
  ```
  python3 << 'PYEOF'
  import json, hashlib, time
  from pathlib import Path
  atoms_path = Path.home() / ".athanor/corpus/atoms.jsonl"
  pairs_path = Path("fixtures/correspondence/pairs.p3a.jsonl")
  for fam, highf in [("shinto_onmyodo", "/tmp/high_shinto.jsonl"), ("mesopotamia", "/tmp/high_meso.jsonl"), ("grimoire", "/tmp/high_grimoire.jsonl"), ("alchemy_lab", "/tmp/high_alch.jsonl")]:
      if not Path(highf).exists(): continue
      highs = [json.loads(l) for l in open(highf) if l.strip()]
      if not highs: continue
      existing_atoms = set()
      if atoms_path.exists():
          for l in open(atoms_path): 
              try: existing_atoms.add(json.loads(l)["atom_id"])
              except: pass
      added_a = added_p = 0
      with open(atoms_path, "a") as af, open(pairs_path, "a") as pf:
          for h in highs:
              aid = h.get("atom_id", f"pd.{fam}.{hashlib.sha256(h['text'].encode()).hexdigest()[:8]}")
              if aid in existing_atoms: continue
              atom = {"atom_id": aid, "family_id": fam, "text": h["text"], "source_url": h["source_url"], "content_hash": h["content_hash"], "epistemic": "OBSERVED", "license": "PD", "lens_hints": {"historical": True, "symbolic": True}}
              af.write(json.dumps(atom) + "\n")
              added_a += 1
              pair = {"pair_id": f"corr.{fam}.text.{int(time.time()*1000)%100000}", "family_id": fam, "role": "text", "filler": "PD excerpt", "span": h["text"][:100], "atom_id": aid, "epistemic": "OBSERVED"}
              pf.write(json.dumps(pair) + "\n")
              added_p += 1
      print(f"Added {added_a} atoms + {added_p} pairs for {fam}")
  print("New totals check:")
  print("Atoms:", sum(1 for _ in open(atoms_path)))
  print("Pairs:", sum(1 for _ in open(pairs_path)))
  PYEOF
  ```
- Expected (example on success): "Added 12 atoms + 12 pairs for shinto_onmyodo" etc. "New totals check: Atoms: 3770 Pairs: 1319"

**Task 7: Expand gold negatives (bite-sized, 3 min)**
- Append 10-15 new OOD (exact):
  ```
  python3 << 'PYEOF'
  import json
  negs_path = "fixtures/negatives/negatives.p3a.jsonl"
  existing = [json.loads(l) for l in open(negs_path) if l.strip()]
  new = [
      {"neg_id": f"neg.round2.{i}", "theme": t, "text": txt, "epistemic": "OBSERVED", "license": "CC0-fixture", "source": "fixture"}
      for i, (t, txt) in enumerate([
          ("tech_cloud", "Cloud computing provides scalable infrastructure for modern applications."),
          ("news_science", "Particle accelerators reveal fundamental properties of matter."),
          ("product_finance", "Banking apps enable instant transfers between accounts."),
          ("news_edu", "Libraries digitize rare books for public access."),
          ("slop_health", "Daily walks improve cardiovascular health and mood."),
          ("news_law", "Courts interpret contracts using established precedent."),
          ("tech_robotics", "Robots assemble cars on automated factory lines."),
          ("news_env", "National parks preserve wilderness areas for future generations."),
          ("product_ent", "Video games use physics engines for realistic movement."),
          ("news_politics", "Parliaments debate budgets and legislation annually."),
          ("tech_network", "Fiber optic cables transmit data at high speeds."),
          ("news_sport", "Teams analyze statistics to improve player performance."),
          ("product_travel", "Booking sites compare prices across airlines and hotels."),
          ("news_food", "Farmers markets sell locally grown produce directly to consumers."),
          ("slop_auto", "Modern cars include safety features like automatic braking."),
      ])
  ]
  added = 0
  with open(negs_path, "a") as f:
      for n in new:
          if not any(e.get("neg_id") == n["neg_id"] for e in existing):
              f.write(json.dumps(n) + "\n")
              added += 1
  print(f"Added {added} negatives. Total now ~{len(existing)+added}")
  PYEOF
  ```
- Expected: "Added 15 negatives. Total now ~265"

**Task 8: Re-evaluate harness (read-only run, capture output)**
- Command:
  ```
  python scripts/eval_retrieve.py --k 10 2>&1 | grep -E "pairs_evaluated|hit_rate_at_10|ndcg|alchemy_lab|shinto_onmyodo|Low/near-min|Negative trad-family" | head -15
  ```
- Expected (post adds): lines with updated numbers, e.g. "pairs_evaluated: 1319", "alchemy_lab: hit=0.33...", "Low/near-min pair families (n<=15, min=13): ...", "Negative trad-family spillover: 1/6 (target low)".

**Task 9: Full verification + docs sync (TDD style for any doc change)**
- Run:
  ```
  python -m pytest -q --tb=no | tail -1
  python -m ruff check src tests scripts/eval_retrieve.py | cat
  python specs/contracts/verify_review.py | cat
  ```
- Expected: "227 passed in X.XXs", "All checks passed!", "REVIEW_CONTRACTS_PASS ..."
- Update docs/dataset-card.md (minimal, via read + targeted):
  - Use python -c re.sub for counts (exact):
    ```
    python3 -c '
    import re, json, collections, os, statistics
    atoms = [json.loads(l) for l in open(os.path.expanduser("~/.athanor/corpus/atoms.jsonl")) if l.strip()]
    pairs = [json.loads(l) for l in open("fixtures/correspondence/pairs.p3a.jsonl") if l.strip()]
    fam_p = collections.Counter(p.get("family_id") for p in pairs)
    lengths = [len(a.get("text","")) for a in atoms]
    negs = len([l for l in open("fixtures/negatives/negatives.p3a.jsonl") if l.strip()])
    with open("docs/dataset-card.md") as f: c = f.read()
    c = re.sub(r"Atoms: \d+", f"Atoms: {len(atoms)}", c)
    c = re.sub(r"Pairs: \d+", f"Pairs: {len(pairs)}", c)
    c = re.sub(r"Negatives: \d+", f"Negatives: {negs}", c)
    c = re.sub(r"alchemy_lab pairs: \d+", f"alchemy_lab pairs: {fam_p.get(\"alchemy_lab\",0)}", c)
    with open("docs/dataset-card.md", "w") as f: f.write(c)
    print("Docs updated: Atoms", len(atoms), "Pairs", len(pairs), "Negs", negs)
    '
    ```
- Re-verify docs change with grep or python.
- Commit: `git add fixtures/negatives/negatives.p3a.jsonl docs/dataset-card.md src/athanor/entrypoint.py scripts/eval_retrieve.py tests/test_eval_retrieve.py ~/.athanor/corpus/atoms.jsonl fixtures/correspondence/pairs.p3a.jsonl 2>/dev/null || git add ... && git commit -m "data: +X jev for shinto/meso/grimoire/alchemy (shinto now 15+). +15 neg (~265). Harness/doctor tweaks. Full verify PASS."`

**Task 10: PR comment + snapshot (final)**
- Command:
  ```
  gh pr comment 13 --body "Round 1 (priority low balance + alchemy): [exact counts from above]. Min pair now 13+. Full verify PASS."
  python3 -c '...'  # repeat stats print
  git log --oneline -1
  ```
- Expected: Comment URL + updated stats + commit SHA.

## Option 2+ (Lower Priority - Chain After Option 1)
- Repeat Tasks 3-10 but target "more alchemy" sources + "negatives to 300".
- For harness: add per_family_ndcg_sample expansion in entrypoint.py (TDD first in test).
- Source discovery: new searches for "Bardo Thodol", "Popol Vuh", "Upanishads full" if still low families.
- Exact command for Option 2 start: same firecrawl searches but with "more alchemy PD Basil Valentine Triumphal Chariot".

## Tests / Validation
- Every code change: TDD cycle documented above (failing test run → implement → passing run).
- Per round end: exact 3 verification commands + expected strings ("227 passed", "All checks passed!", "REVIEW_CONTRACTS_PASS").
- Harness run: capture grep output showing per-family and low callouts.
- No commit without the 3 verify lines in log.
- If jev high==0: log and skip; do not mutate corpus.

## Risks, Tradeoffs, and Open Questions
- Risk: jev returns 0 high on good PD (seen in prior rounds) → tradeoff: hold quality vs. force lower threshold (plan: hold, document).
- Risk: eval timeout on full 1300+ pairs → use --k 5 or slice for intermediate; full only at verify.
- Tradeoff: longer excerpts improve signal but reduce atom count per page.
- Open: exact min target after this round (15? 20?); whether to add "shinto" to doctor low threshold in entrypoint.py (current <=12).
- Open: best new sources if sacred-texts exhausted (arxiv secondary only, never add).
- Always: preserve "jev rerank mandatory" and "primary PD OBSERVED" invariants.

**End of plan. Implementer: follow tasks in order, capture every expected output before proceeding.**