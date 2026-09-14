"""Retired helper must not create gold or rewrite an operator corpus."""
import json
import os
import subprocess
import sys
from pathlib import Path


def test_legacy_gold_helper_has_no_mutation(tmp_path):
    corpus = tmp_path / ".athanor" / "corpus"
    corpus.mkdir(parents=True)
    atoms = corpus / "atoms.jsonl"
    original = b'{"atom_id":"synthetic","epistemic":"INFERRED"}\n'
    atoms.write_bytes(original)
    before = sorted(str(p.relative_to(tmp_path)) for p in tmp_path.rglob("*"))
    helper = Path(__file__).resolve().parents[1] / "scripts/shadow/athanor/apply_gold_p3a.py"
    result = subprocess.run([sys.executable, str(helper)], cwd=tmp_path,
                            env={**os.environ, "HOME": str(tmp_path), "USERPROFILE": str(tmp_path)},
                            capture_output=True, text=True, check=False)
    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert report["reason"] == "HEURISTIC_GOLD_PROMOTION_RETIRED"
    assert report["corpus_mutated"] is False
    assert atoms.read_bytes() == original
    assert before == sorted(str(p.relative_to(tmp_path)) for p in tmp_path.rglob("*"))
