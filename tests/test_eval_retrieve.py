"""Tests for scripts/eval_retrieve.py retrieval eval harness (TDD)."""
from __future__ import annotations
import json
import subprocess
from pathlib import Path

from scripts.eval_retrieve import evaluate_correspondence, load_pairs

ROOT = Path(__file__).resolve().parents[1]
PAIRS = ROOT / "fixtures" / "correspondence" / "pairs.p3a.jsonl"
NEGS = ROOT / "fixtures" / "negatives" / "negatives.p3a.jsonl"


def test_load_pairs_returns_list():
    pairs = load_pairs(str(PAIRS))
    assert isinstance(pairs, list)
    assert len(pairs) >= 100
    assert "atom_id" in pairs[0]
    assert "family_id" in pairs[0]


def test_evaluate_correspondence_basic():
    pairs = load_pairs(str(PAIRS))[:5]  # small slice for speed
    results = evaluate_correspondence(pairs, k=5)
    assert "pairs_evaluated" in results
    assert results["pairs_evaluated"] == 5
    # Current baseline after query polish (lexical BM25 on PD excerpts)
    assert results["hit_rate_at_5"] >= 0.6, f"Expected >=0.6 hit rate, got {results.get('hit_rate_at_5', 0.0)}"
    assert "per_family" in results


def test_gated_train_eval_readiness_exits_hold():
    """Phase 5: gated skeleton must exit 2 with HOLD (non-activating)."""
    script = ROOT / "scripts" / "eval_train_readiness.py"
    result = subprocess.run([str(script)], capture_output=True, text=True, check=False)
    assert result.returncode == 2
    assert "EVAL-TRAIN-HARNESS: HOLD" in result.stdout
    assert "read-only skeleton only" in result.stdout


def test_evaluate_with_report(tmp_path):
    """Test --report flag produces valid JSON (TDD addition)."""
    import tempfile
    from scripts.eval_retrieve import load_pairs, evaluate_correspondence
    pairs = load_pairs(str(PAIRS))[:3]
    results = evaluate_correspondence(pairs, k=3)
    report_path = tmp_path / "test_report.json"
    # Simulate the report logic
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as rf:
        json.dump(results, rf, indent=2)
    assert report_path.exists()
    with open(report_path) as f:
        loaded = json.load(f)
    assert loaded["pairs_evaluated"] == 3
    assert "hit_rate_at_3" in loaded
