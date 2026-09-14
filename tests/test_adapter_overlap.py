"""Synthetic-only overlap integration; no private corpus or real split assignment."""
import copy
import json

import pytest
from test_adapter_pipeline import config, rows

from athanor.adapter_data import canonical, digest
from athanor.adapter_freeze import freeze_candidates, main


def test_overlap_unions_preserve_work_links_and_inputs():
    data = rows(3)
    data[2]['sources'][0]['group_id'] = data[1]['sources'][0]['group_id']
    before = copy.deepcopy(data)
    mapping = {'0': 'overlap-a', '1': 'overlap-a', '2': 'overlap-b'}
    result = freeze_candidates(data, config(), mapping)
    assert result['group_count'] == 1
    assert len(set(result['groups'].values())) == 1
    assert result['status'] == 'REJECTED_SUPPORT'
    assert result['training_authorized'] is False
    assert result['projection']['training_authorized'] is False
    assert result['overlap_groups_sha256'] == digest(canonical(mapping))
    assert data == before
    assert result == freeze_candidates(list(reversed(data)), config(), dict(reversed(list(mapping.items()))))


@pytest.mark.parametrize('mapping', [[], {}, {'0': 'a'}, {'0': 'a', '1': 'b', '2': 'c', 'x': 'd'},
                                     {'0': '', '1': 'b', '2': 'c'},
                                     {'0': ' ', '1': 'b', '2': 'c'},
                                     {'0': True, '1': 'b', '2': 'c'}])
def test_invalid_overlap_evidence(mapping):
    with pytest.raises(ValueError, match='Overlap'):
        freeze_candidates(rows(3), config(), mapping)


def test_omission_preserves_legacy_receipt_and_existing_holdout_rejected():
    data = rows(3)
    assert freeze_candidates(data, config()) == freeze_candidates(data, config(), None)
    assert 'overlap_groups_sha256' not in freeze_candidates(data, config())
    data[0]['split'] = 'test'
    with pytest.raises(ValueError, match='held-out'):
        freeze_candidates(data, config(), {'0': 'a', '1': 'a', '2': 'b'})


def test_cli_overlap_receipt_and_malformed_files(tmp_path, capsys):
    source, cfg, overlap = [tmp_path / name for name in ('rows.jsonl', 'config.json', 'overlap.json')]
    source.write_text('\n'.join(json.dumps(r) for r in rows(3)), encoding='utf-8')
    cfg.write_text(json.dumps(config()), encoding='utf-8')
    overlap.write_text(json.dumps({'0': 'a', '1': 'a', '2': 'a'}), encoding='utf-8')
    args = ['--input', str(source), '--config', str(cfg), '--overlap-groups', str(overlap)]
    assert main(args) == 2
    result = json.loads(capsys.readouterr().out)
    assert result['group_count'] == 1 and result['training_authorized'] is False
    for text in ('null', '[]', '{"0":"a","0":"b","1":"a","2":"a"}'):
        overlap.write_text(text, encoding='utf-8')
        assert main(args) == 1
        assert json.loads(capsys.readouterr().out)['status'] == 'INVALID'
