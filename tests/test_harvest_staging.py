"""Static checks: never import legacy harvesters (imports create directories)."""
import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1] / 'scripts/shadow/athanor'
WRITERS = {
    'wave0_harvest', 'deepen_harvest', 'ingest_priority_a', 'ingest_priority_b',
    'ingest_priority_c', 'ingest_priority_d', 'ingest_priority_d_continue',
    'ingest_priority_e', 'ingest_priority_f_fill2500', 'ingest_priority_f_fill3000',
}


def destination(source):
    tree = ast.parse(source)
    assignments = [n.value for n in ast.walk(tree) if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'ATOMS_PATH'
                           for t in n.targets)]
    assert len(assignments) == 1
    expected = ast.parse('HOME / ".athanor" / "staging" / "legacy-harvest" / '
                         '"candidates.jsonl"', mode='eval').body
    assert ast.dump(assignments[0]) == ast.dump(expected)


def test_all_known_writers_stage_without_importing():
    found = set()
    for path in ROOT.glob('*.py'):
        source = path.read_text(encoding='utf-8')
        if 'ATOMS_PATH =' in source:
            found.add(path.stem)
            destination(source)
    assert found == WRITERS


def test_old_corpus_destination_rejected():
    with pytest.raises(AssertionError):
        destination('ATOMS_PATH = HOME / ".athanor" / "corpus" / "atoms.jsonl"')


def test_continuation_inherits_parent_destination():
    tree = ast.parse((ROOT / 'ingest_priority_b_continue.py').read_text(encoding='utf-8'))
    assert any(isinstance(n, ast.Import) and any(a.name == 'ingest_priority_b'
               and a.asname == 'b' for a in n.names) for n in ast.walk(tree))
    assert not any(isinstance(n, ast.Attribute) and n.attr == 'ATOMS_PATH'
                   and isinstance(n.ctx, ast.Store) for n in ast.walk(tree))
