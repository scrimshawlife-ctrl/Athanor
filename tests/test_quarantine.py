"""Synthetic-only recovery fixtures; private data never required by CI."""
import json
import os
import stat
import zipfile

import pytest

from athanor.quarantine import build, canonical, classify, clean, main, sha


def fixture(tmp_path):
    parent = tmp_path / 'prepared'
    parent.mkdir()
    atom = {'atom_id': 'synthetic', 'text': 'Marduk and Tiamat. ' * 50,
            'family_id': 'mesopotamia', 'type': 'text', 'source_url': 'https://example.org',
            'license': 'synthetic-only', 'epistemic': 'INFERRED', 'content_hash': 'synthetic-hash'}
    pack = tmp_path / 'synthetic.zip'
    with zipfile.ZipFile(pack, 'w') as archive:
        archive.writestr('pack/atoms_full.jsonl', canonical(atom) + '\n')
    records = {'features.jsonl': [], 'targets.jsonl': [],
               'provenance.jsonl': [{'row_id': 'r', 'original_metadata': {'atom_id': 'synthetic'}}],
               'quarantine.jsonl': [{'row_id': 'r', 'reasons': ['WEAK_NOT_GOLD']}]}
    manifest = {'source_zip_sha256': sha(pack.read_bytes()), 'files': {}}
    for name, rows in records.items():
        raw = ''.join(canonical(r) + '\n' for r in rows).encode()
        (parent / name).write_bytes(raw)
        manifest['files'][name] = {'sha256': sha(raw), 'bytes': len(raw), 'rows': len(rows)}
    (parent / 'manifest.json').write_text(canonical(manifest), encoding='utf-8')
    return parent, pack


def test_cleaning_controls():
    text, removed = clean('p. 12\nHistorical claim remains.\nSacred Texts |')
    assert text == 'Historical claim remains.\n' and len(removed) == 2
    assert clean(text)[0] == text
    assert clean('A prose URL https://example.org remains.')[0].endswith('remains.')
    assert clean('![](https://example.org/glyph.jpg)')[0].startswith('![](')


def test_preserve_prose_and_whitespace():
    text = '  Verse  \r\nNext: This doctrine was revised...\r\n\r\n\r\n« Previous: substantive prose\n\te\u0301  \n'
    assert clean(text) == (text, [])
    assert clean('Next:\nBody\n« Previous:\n[paragraph continues]\n')[0] == 'Body\n'


@pytest.mark.parametrize('linked', [False, True])
def test_no_private_output_in_checkout(tmp_path, capsys, linked):
    parent, pack = fixture(tmp_path)
    checkout = tmp_path / 'checkout'
    checkout.mkdir()
    marker = checkout / '.git'
    if linked:
        marker.write_text('gitdir: elsewhere')
    else:
        marker.mkdir()
    out = checkout / 'nested' / 'private-output'
    assert main(['--prepared', str(parent), '--pack', str(pack), '--output', str(out)]) == 1
    assert not out.exists()
    assert json.loads(capsys.readouterr().out)['status'] == 'INVALID'


@pytest.mark.parametrize('field,value', [('text', None), ('text', []), ('text', 3),
    ('atom_id', {}), ('family_id', False), ('source_url', []), ('license', None), ('type', 7),
    ('epistemic', None), ('content_hash', []), ('license', ''), ('source_url', ''),
    ('type', 'unknown'), ('epistemic', 'APPROVED'), ('content_hash', 'short')])
def test_invalid_atom_types(tmp_path, capsys, field, value):
    parent, pack = fixture(tmp_path)
    with zipfile.ZipFile(pack) as archive:
        atom = json.loads(archive.read('pack/atoms_full.jsonl'))
    atom[field] = value
    with zipfile.ZipFile(pack, 'w') as archive:
        archive.writestr('pack/atoms_full.jsonl', canonical(atom) + '\n')
    manifest = json.loads((parent / 'manifest.json').read_bytes())
    manifest['source_zip_sha256'] = sha(pack.read_bytes())
    (parent / 'manifest.json').write_text(canonical(manifest))
    assert main(['--prepared', str(parent), '--pack', str(pack)]) == 1
    result = json.loads(capsys.readouterr().out)
    assert result['status'] == 'INVALID' and field in result['reason']


def test_routing_controls():
    atom = {'family_id': 'mesopotamia', 'type': 'text', 'source_url': '', 'license': 'PD'}
    assert classify('Marduk Tiamat ' * 50, atom)['route'] == 'BODY_CANDIDATE'
    assert classify('Uninformative.', atom)['proposed_family'] == 'NOT_COMPUTABLE'
    catalog = 'Toggle Sidebar\nTitle\nMarduk Tiamat ' * 50
    assert classify(catalog, {**atom, 'text': catalog})['route'] == 'REEXTRACT_WEB_ARTIFACT'
    assert classify('Marduk Tiamat ' * 50, {**atom, 'license': 'design-only'})['route'] == 'HOLD_RIGHTS_OR_INTERNAL'
    assert classify('Marduk Tiamat ' * 50, {**atom, 'source_url': '/astro/hba/x'})['route'] == 'HOLD_MISLEADING_SOURCE_LABEL'
    assert classify('Marduk earth early ' * 50, atom)['proposed_family'] == 'NOT_COMPUTABLE'


@pytest.mark.parametrize('newline', ['\n', '\r\n', '\r'])
@pytest.mark.parametrize('heading', ['Title', 'Author'])
def test_catalog_logical_lines(newline, heading):
    original = newline.join([heading, 'Toggle Sidebar', 'Marduk Tiamat ' * 50])
    atom = {'text': original, 'family_id': 'mesopotamia', 'type': 'text'}
    assert classify(clean(original)[0], atom)['route'] == 'REEXTRACT_WEB_ARTIFACT'
    prose = newline.join(['Title of a chapter', 'Toggle Sidebar is mentioned in prose',
                          'Marduk Tiamat ' * 50])
    assert classify(prose, {**atom, 'text': prose})['route'] == 'BODY_CANDIDATE'


@pytest.mark.parametrize('field', ['atom_id', 'family_id', 'text', 'type', 'license',
                                   'source_url', 'epistemic', 'content_hash'])
def test_missing_required_atom_field(tmp_path, capsys, field):
    parent, pack = fixture(tmp_path)
    with zipfile.ZipFile(pack) as archive:
        atom = json.loads(archive.read('pack/atoms_full.jsonl'))
    del atom[field]
    with zipfile.ZipFile(pack, 'w') as archive:
        archive.writestr('pack/atoms_full.jsonl', canonical(atom) + '\n')
    manifest = json.loads((parent / 'manifest.json').read_bytes())
    manifest['source_zip_sha256'] = sha(pack.read_bytes())
    (parent / 'manifest.json').write_text(canonical(manifest))
    out = tmp_path / 'rejected'
    assert main(['--prepared', str(parent), '--pack', str(pack), '--output', str(out)]) == 1
    assert not out.exists()
    assert field in json.loads(capsys.readouterr().out)['reason']


@pytest.mark.skipif(os.name != 'posix', reason='POSIX access-mode enforcement')
@pytest.mark.parametrize('mask', [0o000, 0o022])
def test_private_creation_modes(tmp_path, capsys, mask):
    parent, pack = fixture(tmp_path)
    out = tmp_path / 'nested' / 'private-output'
    previous = os.umask(mask)
    try:
        assert main(['--prepared', str(parent), '--pack', str(pack), '--output', str(out)]) == 2
    finally:
        os.umask(previous)
    assert stat.S_IMODE(out.stat().st_mode) == 0o700
    for path in out.iterdir():
        assert stat.S_IMODE(path.stat().st_mode) == 0o600
    capsys.readouterr()


def test_build_verify_and_no_overwrite(tmp_path, capsys):
    parent, pack = fixture(tmp_path)
    before = {p.name: p.read_bytes() for p in parent.iterdir()}
    out = tmp_path / 'private-output'
    args = ['--prepared', str(parent), '--pack', str(pack), '--output', str(out)]
    assert main(args) == 2
    rows = [json.loads(line) for line in (out / 'cleaned.jsonl').read_text().splitlines()]
    assert len(rows) == 1 and rows[0]['training_eligible'] is False
    assert main(args + ['--verify']) == 2
    assert main(args) == 1
    assert before == {p.name: p.read_bytes() for p in parent.iterdir()}
    (out / 'cleaned.jsonl').write_text('tampered')
    assert main(args + ['--verify']) == 1
    capsys.readouterr()


def test_source_tampering(tmp_path):
    parent, pack = fixture(tmp_path)
    (parent / 'quarantine.jsonl').write_text('{}')
    with pytest.raises(ValueError, match='digest'):
        build(parent, pack)
