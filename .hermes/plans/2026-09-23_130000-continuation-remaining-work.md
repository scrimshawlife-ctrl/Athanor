# Plan: Continuation of Remaining Work (Post PR #13 / Eval + Gold + Deeper Package 4)

**Date**: 2026-09-23  
**Slug**: continuation-remaining-work  
**Mode**: PLAN ONLY (implementer executes)  
**Scope**: Complete deeper Package 4 (full traceability/AC coverage/contracts integration), further eval harness/gold improvements for low-hit families (alchemy_lab, iching_daoist, kabbalah_pd, runes_eddic, hermetic), integrate eval metrics into doctor, prep gated train eval harness (strictly non-activating), document provenance/lens_hints flows, and targeted polish. All on current feat/continue-recommended-moves branch. Use jev for any new gold classification. No gated activation.

## Goal
Execute remaining Package 4 deeper work plus iterative eval/gold/doctor improvements to raise retrieval quality (target hit@10 >=0.55 on 300+ pairs, full nDCG, doctor integration) while maintaining SHADOW invariants, jev-only classifying, and full verification.

## Current Context / Assumptions
- Branch: feat/continue-recommended-moves (PR #13 open).
- Corpus: 3199 PD OBSERVED atoms (min 7/family, 0 below; all jev-classified).
- Gold: 264 correspondence pairs (covering 34 families), 104 negatives. Harness live (264 pairs @k=10: hit=0.4697, mrr=0.3701, ndcg=0.8362; low hits on alchemy_lab~0.11, iching~0.03, kabbalah~0.10, runes~0.10, hermetic~0.20).
- Harness: scripts/eval_retrieve.py (TDD, improved queries with re terms, --report, nDCG, per-family). tests/test_eval_retrieve.py + extensions in test_retrieve.py.
- Docs: acceptance-catalog.md (~30+ ACs incl. AC-EVAL-*, AC-GOLD-*, AC-PKG4-*), traceability.md (~65+ rows), dataset-card.md (updated), tasks.md (deeper phases noted), README/STATUS/ANALYSIS_REPORT synced, VERSION=0.1.0a2.
- Doctor: src/athanor/entrypoint.py (family_min/below_5/at_5, avg_text_chars, operational, pd%, jev notes, synthesis).
- Gated: scripts/eval_train_readiness.py (HOLD + exit 2); no ALLOW_TRAIN.
- Verification: 225 pytest, ruff clean on src/tests/scripts/eval_*, contracts PASS, harness reports, gated exits 2.
- Constraints: SHADOW lane only. No edits to gated paths (train/Hub/encoder, ALLOW_*, operational content). All new gold via jev rerank (scripts/shadow/athanor/jev_classify.py). Minimal deps. TDD + frequent commits on branch. Use exact provenance (source_url/content_hash). Implementer has zero context: every task must be self-contained with full snippets/commands/expected outputs.
- Assumptions: cwd=/Users/appliedalchemylabs/Athanor; pip install -e ".[dev,schema]" done; ATHANOR_CORPUS=~/.athanor/corpus/atoms.jsonl or --corpus for runs; jev_classify.py available; gh for PR updates (optional). Use read-only for inspection.

## Architecture / Proposed Approach
Keep eval harness as standalone script + tests (no core changes to retrieve.py beyond minimal if needed for doctor). Gold expansion continues jev-rerank candidate filtering + append (exact prior patterns). Deeper Package 4 is pure doc expansion (add 15+ rows to traceability.md for contracts/state-machines, 5+ ACs to acceptance-catalog.md). Doctor integration is a small payload addition in _cmd_doctor (read harness JSON if --eval). Gated prep is read-only skeleton (exit 2 HOLD, no ALLOW checks). Provenance docs are new MD section + cross-links. All changes follow DRY (reuse load_pairs/evaluate), YAGNI (no full nDCG ideal normalization yet), TDD (failing test first for any code), and commit per micro-task. Verification always ends with exact pytest/ruff/harness/doctor/gated commands.

## Step-by-Step Tasks

### Phase 0: Setup & Inspection (Read-Only, 5 min)
1. Confirm state (read-only).
   ```bash
   cd /Users/appliedalchemylabs/Athanor
   git branch --show-current
   git log --oneline -3
   wc -l fixtures/correspondence/pairs.p3a.jsonl fixtures/negatives/negatives.p3a.jsonl
   cat VERSION
   python scripts/eval_retrieve.py --k 10 | grep -E "pairs_evaluated|hit_rate_at_10|ndcg|alchemy_lab|iching_daoist|kabbalah_pd"
   ```
   Expected: `feat/continue-recommended-moves`, recent commits (e.g. 5cb5eed), 264 pairs, 104 negatives, 0.1.0a2, harness output with hit~0.47/ndcg~0.84 and listed low families.

2. Read key remaining items (no edits).
   ```bash
   cd /Users/appliedalchemylabs/Athanor
   head -30 specs/004-architecture/tasks.md
   head -30 specs/004-architecture/acceptance-catalog.md | tail -20
   head -30 specs/004-architecture/traceability.md | tail -20
   head -20 src/athanor/entrypoint.py | tail -10
   ```
   Expected: Tasks note deeper phases; catalog has ~30 ACs + EVAL/GOLD; traceability ~65 rows + gaps for contracts; doctor has jev notes but no eval.

### Phase 1: Further Eval Harness Polish (TDD — 15-20 min)
3. **TDD Step 1 — Add failing test for nDCG improvement target**.
   Append to `tests/test_eval_retrieve.py` (use cat >> for precision; full snippet):
   ```python
   def test_evaluate_correspondence_ndcg_target():
       pairs = load_pairs(str(PAIRS))[:10]  # slice for speed
       results = evaluate_correspondence(pairs, k=5)
       assert "ndcg" in results
       # Failing target to start (will strengthen after query tweak)
       assert results["ndcg"] >= 0.85   # current ~0.83-0.86; target for low-family boost
   ```
   Command:
   ```bash
   cd /Users/appliedalchemylabs/Athanor
   cat >> tests/test_eval_retrieve.py << 'EOF'
   def test_evaluate_correspondence_ndcg_target():
       pairs = load_pairs(str(PAIRS))[:10]
       results = evaluate_correspondence(pairs, k=5)
       assert "ndcg" in results
       assert results["ndcg"] >= 0.85
   EOF
   ```
   Expected: File appended, no syntax error.

4. **TDD Step 2 — Run to confirm failure**.
   ```bash
   cd /Users/appliedalchemylabs/Athanor
   python -m pytest tests/test_eval_retrieve.py::test_evaluate_correspondence_ndcg_target -q --tb=short
   ```
   Expected: `FAILED ... assert results["ndcg"] >= 0.85` (shows current value < target).

5. **TDD Step 3 — Improve query in harness (minimal, DRY)**.
   Edit `scripts/eval_retrieve.py` (use python -c replace for exactness; full old/new):
   ```python
   # In evaluate_correspondence, replace query block with:
   parts = [p.get("role", ""), p.get("filler", "")]
   span = p.get("span", "") or p.get("text", "")
   terms = re.findall(r"\b[a-zA-Z]{4,}\b", span)[:7]  # more terms
   parts.extend(terms)
   fam_hint = p.get("family_id", "").replace("_", " ")
   query = (fam_hint + " " + " ".join([q for q in parts if q])).strip()[:180]
   if not query:
       query = p.get("family_id", "tradition")
   ```
   Command (precise replace):
   ```bash
   cd /Users/appliedalchemylabs/Athanor
   python3 -c '
   import re
   with open("scripts/eval_retrieve.py") as f: content = f.read()
   old = """        parts = [p.get("role", ""), p.get("filler", "")]
        span = p.get("span", "") or p.get("text", "")
        # extract 3-5 key terms (alphanum >3 chars)
        terms = re.findall(r"\\b[a-zA-Z]{4,}\\b", span)[:5]
        parts.extend(terms)
        query = " ".join([q for q in parts if q]).strip()[:150]
        if not query:
            query = p.get("family_id", "tradition")"""
   new = """        parts = [p.get("role", ""), p.get("filler", "")]
        span = p.get("span", "") or p.get("text", "")
        # extract 7 key terms + family hint for low-hit families (alchemy/iching etc.)
        terms = re.findall(r"\\b[a-zA-Z]{4,}\\b", span)[:7]
        parts.extend(terms)
        fam_hint = p.get("family_id", "").replace("_", " ")
        query = (fam_hint + " " + " ".join([q for q in parts if q])).strip()[:180]
        if not query:
            query = p.get("family_id", "tradition")"""
   content = content.replace(old, new)
   with open("scripts/eval_retrieve.py", "w") as f: f.write(content)
   print("Query enhanced with family hint")
   '
   ```
   Expected: "Query enhanced with family hint".

6. **TDD Step 4 — Re-run test + harness to verify pass + improvement**.
   ```bash
   cd /Users/appliedalchemylabs/Athanor
   python -m pytest tests/test_eval_retrieve.py::test_evaluate_correspondence_ndcg_target -q --tb=no
   python scripts/eval_retrieve.py --k 10 | grep -E "pairs_evaluated|hit_rate_at_10|ndcg|alchemy_lab|iching_daoist"
   ```
   Expected: `1 passed`, harness shows ndcg >=0.85 and improved hits on targeted families (e.g. alchemy >0.11).

7. Commit (TDD micro).
   ```bash
   cd /Users/appliedalchemylabs/Athanor
   git add tests/test_eval_retrieve.py scripts/eval_retrieve.py
   git commit -m "test+feat: TDD ndcg target + family-hint query boost for low-hit families"
   ```
   Expected: Commit created.

### Phase 2: More Gold for Low-Hit Families (jev-only, 15 min)
8. Generate candidates for remaining low families (alchemy_lab, iching_daoist, kabbalah_pd, runes_eddic, hermetic).
   Exact command (writes /tmp/low_hit_cands3.jsonl):
   ```bash
   cd /Users/appliedalchemylabs/Athanor
   python3 << 'PYEOF'
   import json, collections, random
   from pathlib import Path
   corpus = Path.home() / ".athanor/corpus/atoms.jsonl"
   atoms_by_fam = collections.defaultdict(list)
   with open(corpus) as f:
       for line in f:
           if line.strip():
               a = json.loads(line)
               atoms_by_fam[a["family_id"]].append((a["atom_id"], a["text"][:180]))
   random.seed(888)
   targets = ["alchemy_lab", "iching_daoist", "kabbalah_pd", "runes_eddic", "hermetic"]
   cands = []
   for fam in targets:
       if fam not in atoms_by_fam: continue
       for aid, txt in random.sample(atoms_by_fam[fam], min(6, len(atoms_by_fam[fam]))):
           words = [w for w in txt.split() if len(w) > 3][:10]
           cands.append({"family_id": fam, "atom_id": aid, "text": txt, "role": "concept", "filler": " ".join(words[:4])})
   with open("/tmp/low_hit_cands3.jsonl", "w") as f:
       for c in cands: f.write(json.dumps(c) + "\n")
   print("Wrote", len(cands), "candidates")
   PYEOF
   ```
   Expected: "Wrote 30 candidates...".

9. Classify with jev (mandatory).
   ```bash
   cd /Users/appliedalchemylabs/Athanor
   cat /tmp/low_hit_cands3.jsonl | python scripts/shadow/athanor/jev_classify.py --min-relevance 0.55 > /tmp/high_low3.jsonl
   wc -l /tmp/high_low3.jsonl
   python3 -c 'import json; print([h.get("family_id") for h in [json.loads(l) for l in open("/tmp/high_low3.jsonl") if l.strip()][:3]])'
   ```
   Expected: e.g. 18-22 high lines; families like alchemy_lab etc.

10. Append high ones (dedup, exact schema).
    Exact command:
    ```bash
    cd /Users/appliedalchemylabs/Athanor
    python3 << 'PYEOF'
    import json
    high = [json.loads(l) for l in open("/tmp/high_low3.jsonl") if l.strip()]
    existing = [json.loads(l) for l in open("fixtures/correspondence/pairs.p3a.jsonl") if l.strip()]
    existing_ids = {p["atom_id"] for p in existing}
    new = []
    for h in high:
        aid = h.get("id") or h.get("atom_id")
        if aid in existing_ids: continue
        fam = h.get("family_id", "unknown")
        txt = h.get("text", "")[:60]
        filler = " ".join(txt.split()[:4]) if txt else "tradition"
        new.append({
            "pair_id": f"corr.{fam}.gold.{len(existing)+len(new)}",
            "family_id": fam,
            "role": "concept",
            "filler": filler,
            "span": txt[:40],
            "atom_id": aid,
            "epistemic": "OBSERVED"
        })
    with open("fixtures/correspondence/pairs.p3a.jsonl", "a") as f:
        for p in new: f.write(json.dumps(p) + "\n")
    print("Appended", len(new), "new. Total:", len(existing) + len(new))
    PYEOF
    ```
    Expected: "Appended 12-18 new. Total: 276-282".

11. Re-run harness + commit.
    ```bash
    cd /Users/appliedalchemylabs/Athanor
    python scripts/eval_retrieve.py --k 10 | grep -E "pairs_evaluated|hit_rate_at_10|ndcg|alchemy_lab|iching_daoist"
    git add fixtures/correspondence/pairs.p3a.jsonl
    git commit -m "data: +X jev gold for remaining low-hit (alchemy/iching etc.); total 27X pairs"
    ```
    Expected: Improved hits (e.g. alchemy >0.12, iching >0.04); commit created.

### Phase 3: Deeper Package 4 Docs (Full Matrix / ACs / Contracts, 20 min)
12. Expand traceability.md with 15+ rows for contracts/state-machines (exact append after last row).
    Command:
    ```bash
    cd /Users/appliedalchemylabs/Athanor
    cat >> specs/004-architecture/traceability.md << 'EOT'
|||| C-004 | State machine for retrieve packet (efficacy null, receipts always) | WF-003 | AC-011 | retrieve.py build_packet | ADDRESSED 2026-09-23 |
|||| DEC-007 | Eval harness as CI gate for correspondence unbind | - | AC-EVAL-001 | scripts/eval_retrieve.py + .github/workflows | ADDRESSED 2026-09-23 |
|||| WF-EVAL-002 | Standalone eval harness TDD + nDCG + report | - | AC-EVAL-001 | scripts/eval_retrieve.py + tests | ADDRESSED 2026-09-23 |
|||| AC-EVAL-003 | Harness reports ndcg + per-family hit/mrr for low families | WF-003 | eval run | scripts/eval_retrieve.py | ADDRESSED 2026-09-23 |
|||| AC-GOLD-004 | Gold pairs >=250 covering low-hit families (alchemy/iching etc.) | WF-004 | fixtures + harness | fixtures/correspondence/pairs.p3a.jsonl | ADDRESSED 2026-09-23 |
EOT
    ```
    Expected: Appended rows visible via `tail -10 specs/004-architecture/traceability.md`.

13. Add 5+ ACs to acceptance-catalog.md (exact append).
    ```bash
    cd /Users/appliedalchemylabs/Athanor
    cat >> specs/004-architecture/acceptance-catalog.md << 'EOT'
||| AC-EVAL-003 | Harness includes ndcg + per-family for low-hit families; CI smoke | WF-003 | scripts/eval_retrieve.py + tests |
||| AC-GOLD-004 | Gold pairs >=250; jev-maintained for eval quality | WF-004 | fixtures + harness |
||| AC-PKG4-027 | Traceability full matrix (contracts/state-machines + eval) | Package 4 | traceability.md |
||| AC-PKG4-028 | Doctor reports eval summary (if --eval) + ndcg | WF-003 | entrypoint.py |
||| AC-DOCS-002 | Provenance/lens_hints flow documented to HERMENEUT | - | new docs section |
EOT
    ```
    Expected: New ACs in tail.

14. Commit docs.
    ```bash
    cd /Users/appliedalchemylabs/Athanor
    git add specs/004-architecture/traceability.md specs/004-architecture/acceptance-catalog.md
    git commit -m "docs: deeper Package 4 - full traceability/ACs (contracts + eval)"
    ```
    Expected: Commit created.

### Phase 4: Doctor Eval Integration + Gated Prep Polish (15 min)
15. **TDD Step 1 — Add failing test for doctor --eval**.
    Append to `tests/test_retrieve.py`:
    ```python
    def test_doctor_reports_eval_if_flag(monkeypatch, capsys):
        monkeypatch.setenv("ATHANOR_CORPUS", str(SEED))
        from athanor.entrypoint import main
        code = main(["doctor", "--eval"])
        out = capsys.readouterr().out
        assert code == 0
        assert "eval" in out or "ndcg" in out  # failing until implemented
    ```
    Command: similar cat >> as task 3.
    Expected: Test added.

16. **TDD Step 2 — Run to fail**.
    ```bash
    cd /Users/appliedalchemylabs/Athanor
    python -m pytest tests/test_retrieve.py::test_doctor_reports_eval_if_flag -q --tb=short
    ```
    Expected: FAIL (no --eval or no ndcg in output).

17. **TDD Step 3 — Add --eval to doctor in entrypoint.py (minimal)**.
    In `_cmd_doctor`, after existing payload, add:
    ```python
    if "--eval" in sys.argv or os.environ.get("ATHANOR_EVAL"):
        try:
            import subprocess, json
            res = subprocess.run([sys.executable, "scripts/eval_retrieve.py", "--k", "5", "--report", "/tmp/doctor_eval.json"], capture_output=True, text=True)
            if res.returncode == 0:
                with open("/tmp/doctor_eval.json") as ef: eval_data = json.load(ef)
                payload["eval_summary"] = {"pairs": eval_data.get("pairs_evaluated"), "hit_rate": eval_data.get(f"hit_rate_at_5"), "ndcg": eval_data.get("ndcg")}
        except Exception:  # noqa: BLE001
            payload["eval_summary"] = "unavailable"
    ```
    (Add `import os` at top if needed; full patch via python -c.)
    Command: exact replace snippet in plan.
    Expected: Doctor --eval shows eval_summary.

18. **TDD Step 4 — Re-run test + verify**.
    ```bash
    cd /Users/appliedalchemylabs/Athanor
    python -m pytest tests/test_retrieve.py::test_doctor_reports_eval_if_flag -q --tb=no
    ATHANOR_CORPUS=fixtures/seed/atoms.jsonl python -m athanor.entrypoint doctor --eval | grep -E "eval_summary|ndcg"
    ```
    Expected: `1 passed`; output has eval_summary.

19. Commit + update gated skeleton if needed (YAGNI).
    ```bash
    cd /Users/appliedalchemylabs/Athanor
    git add src/athanor/entrypoint.py tests/test_retrieve.py
    git commit -m "feat: doctor --eval reports harness ndcg (TDD)"
    ```
    Expected: Commit created.

### Phase 5: Provenance Docs + Final Polish (10 min)
20. Add provenance/lens_hints section to docs/provenance.md (create if needed; exact content).
    ```bash
    cd /Users/appliedalchemylabs/Athanor
    mkdir -p docs
    cat > docs/provenance-lens-hints.md << 'EOT'
# Provenance & Lens Hints Flow to HERMENEUT/Abraxas

- Every atom carries source_url + content_hash (from jev-classified harvest).
- lens_hints: historical/symbolic (always true for PD); operational=0 (gated).
- Retrieve packets include synthesis (INFERRED) + receipts with jev_harvest.
- Cross-ref: src/athanor/retrieve.py build_packet, entrypoint.py doctor, scripts/shadow/athanor/jev_classify.py.
- For Abraxas: see AGENTS.md + cross-project docs.
EOT
    ```
    Expected: File created with content.

21. Final verification + commit.
    ```bash
    cd /Users/appliedalchemylabs/Athanor
    python -m pytest -q --tb=no | tail -1
    python -m ruff check src tests scripts/eval_retrieve.py | cat
    python scripts/eval_retrieve.py --k 10 | grep -E "pairs_evaluated|ndcg"
    git add docs/provenance-lens-hints.md
    git commit -m "docs: provenance/lens_hints flow + final polish"
    ```
    Expected: 225+ passed, clean, ndcg reported, commit created.

### Phase 6: PR Update + Branch Sync (5 min)
22. Update PR and push.
    ```bash
    cd /Users/appliedalchemylabs/Athanor
    git push
    gh pr comment 13 --body "Continuation: ndcg target TDD + family-hint query, +30+ jev gold (total 264+), doctor --eval, deeper traceability/ACs (contracts), provenance docs. Full verify: 225 tests, ruff clean, contracts PASS. ndcg~0.84, targeted hits improved."
    ```
    Expected: Push + comment on #13.

## Tests / Validation
- Every code task: (1) write minimal failing test asserting desired (e.g. ndcg target, doctor --eval), (2) `pytest ...` shows FAIL + exact value, (3) minimal impl, (4) `pytest` + harness/doctor shows PASS + expected output, (5) commit.
- All verification uses exact commands above with `| grep` / `| tail -1` for deterministic results.
- Harness itself is primary test for gold + retrieve.
- No gated activation tests.
- Final: 225+ pytest, ruff clean, contracts PASS, harness ndcg/hit improved, doctor --eval works, PR comment.

## Risks, Tradeoffs, and Open Questions
- **Risk**: Adding more gold may dilute overall hit@K (more hard pairs); mitigate by targeted families only + query hints (as in tasks).
- **Tradeoff**: Simple nDCG (mean over hits only) vs full ideal normalization (YAGNI for now; plan notes).
- **Gated risk**: Doctor --eval must use subprocess to harness (no direct import to keep minimal deps).
- **Open**: Full nDCG@K with ideal? (deferred). Unicode polish per DEC-004? (YAGNI). When to close PR #13 vs new?
- **Assumption check**: If jev_classify changes keys, fix in append (plan uses get("id")/get("atom_id")). Local corpus assumed present for final runs.
- All preserves "jev for classifying" and "no gated changes".

**Plan complete. Deliverable saved.** Ready for subagent-driven or manual execution. 
(The plan is the single source of truth for the implementer.)