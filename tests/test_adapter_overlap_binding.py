"""Synthetic source/registry mismatch tests; no approval or real split claims."""
import copy
import hashlib
import json

import pytest
from test_adapter_pipeline import config, rows

from athanor.adapter_data import canonical, digest
from athanor.adapter_freeze import main
from athanor.adapter_overlap import freeze_with_registry, load_registry, project_overlap_groups


def fixture():
    data = rows(3)
    bindings = {str(i): digest('row-' + str(i)) for i in range(3)}
    registry = {'schema_version': 'athanor.overlap_registry.v1', 'corpus_sha256': 'a' * 64,
                'graph_sha256': 'b' * 64, 'sources': {
                    bindings[str(i)]: {'group_id': 'same-overlap', 'text_sha256': [digest(str(i))]}
                    for i in range(3)}}
    return data, registry, bindings


def test_source_binding_and_freeze_receipt(tmp_path):
    data, registry, bindings = fixture()
    before = copy.deepcopy((data, registry, bindings))
    assert project_overlap_groups(data, registry, bindings) == {str(i): 'same-overlap' for i in range(3)}
    path = tmp_path / 'registry.json'
    raw = json.dumps(registry).encode('utf-8')
    path.write_bytes(raw)
    pinned = hashlib.sha256(raw).hexdigest()
    result = freeze_with_registry(data, config(), path, bindings, pinned)
    assert result['group_count'] == 1 and result['training_authorized'] is False
    assert result['overlap_source_bindings_sha256'] == digest(canonical(bindings))
    assert result['overlap_registry_canonical_sha256'] == digest(canonical(registry))
    assert result['overlap_registry_sha256'] == pinned
    assert (data, registry, bindings) == before


def test_direct_freeze_cannot_claim_unverified_byte_digest(tmp_path):
    data, registry, bindings = fixture()
    with pytest.raises(TypeError, match='file path'):
        freeze_with_registry(data, config(), registry, bindings, 'c' * 64)
    path = tmp_path / 'registry.json'
    path.write_text(json.dumps(registry), encoding='utf-8')
    with pytest.raises(ValueError, match='mismatch'):
        freeze_with_registry(data, config(), path, bindings, 'c' * 64)
    pinned = hashlib.sha256(path.read_bytes()).hexdigest()
    # Same decoded registry, different bytes: the stale byte pin must fail.
    path.write_bytes(path.read_bytes() + b' ')
    with pytest.raises(ValueError, match='mismatch'):
        freeze_with_registry(data, config(), path, bindings, pinned)


@pytest.mark.parametrize('mutation', ['missing', 'extra', 'unknown-row', 'wrong-row', 'changed-text',
                                     'registry-hash', 'empty-hashes', 'duplicate-hashes', 'extra-field'])
def test_invalid_lineage(mutation):
    data, registry, bindings = fixture()
    if mutation == 'missing':
        bindings.pop('0')
    elif mutation == 'extra':
        bindings['unknown'] = bindings['0']
    elif mutation == 'unknown-row':
        bindings['0'] = 'f' * 64
    elif mutation == 'wrong-row':
        bindings['0'] = bindings['1']
    elif mutation == 'changed-text':
        data[0]['sources'][0].update(text='changed', sha256=digest('changed'))
    elif mutation == 'registry-hash':
        registry['graph_sha256'] = 'bad'
    elif mutation == 'empty-hashes':
        registry['sources'][bindings['0']]['text_sha256'] = []
    elif mutation == 'duplicate-hashes':
        registry['sources'][bindings['0']]['text_sha256'] *= 2
    else:
        registry['allow_train'] = True
    with pytest.raises(ValueError):
        project_overlap_groups(data, registry, bindings)


def test_cli_pinned_registry_and_mixed_options(tmp_path, capsys):
    data, registry, bindings = fixture()
    source, cfg, reg, bound = [tmp_path / p for p in ('rows.jsonl', 'cfg.json', 'reg.json', 'bindings.json')]
    source.write_text('\n'.join(json.dumps(r) for r in data), encoding='utf-8')
    cfg.write_text(json.dumps(config()), encoding='utf-8')
    reg.write_text(json.dumps(registry), encoding='utf-8')
    bound.write_text(json.dumps(bindings), encoding='utf-8')
    pinned = hashlib.sha256(reg.read_bytes()).hexdigest()
    args = ['--input', str(source), '--config', str(cfg), '--overlap-registry', str(reg),
            '--overlap-registry-sha256', pinned, '--source-bindings', str(bound)]
    assert main(args) == 2
    assert json.loads(capsys.readouterr().out)['overlap_registry_sha256'] == pinned
    assert main(args + ['--overlap-groups', str(bound)]) == 1
    capsys.readouterr()
    reg.write_text(json.dumps(registry) + ' ', encoding='utf-8')
    assert main(args) == 1
    assert json.loads(capsys.readouterr().out)['status'] == 'INVALID'
    with pytest.raises(ValueError, match='mismatch'):
        load_registry(reg, pinned)
