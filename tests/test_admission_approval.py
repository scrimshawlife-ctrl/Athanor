"""Ephemeral synthetic keys only; never use these tests as real review evidence."""
import copy
import hashlib
import json
from datetime import datetime, timezone

import pytest

pytest.importorskip('cryptography')
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from athanor.admission_approval import DOMAIN, main, verify

NOW = datetime(2026, 9, 14, 12, tzinfo=timezone.utc)


def fixture():
    key = Ed25519PrivateKey.generate()
    atom = {'atom_id': 'synthetic-1', 'family_id': 'hermetic', 'type': 'text',
            'text': 'Synthetic only.', 'source_url': 'https://example.invalid/synthetic',
            'license': 'CC0-fixture', 'epistemic': 'INFERRED',
            'content_hash': hashlib.sha256(b'Synthetic only.').hexdigest()}
    candidates = (json.dumps(atom) + '\n').encode()
    trust = {'schema_version': 'athanor.operator_trust.v1', 'operator': 'synthetic-operator',
             'public_key_hex': key.public_key().public_bytes_raw().hex(),
             'revoked_approval_ids': []}
    manifest = {'schema_version': 'athanor.corpus_admission_approval.v1',
                'approval_id': 'synthetic-approval', 'operator': 'synthetic-operator',
                'action': 'admit_local_retrieval', 'target': 'athanor.local_retrieval_corpus',
                'approved_at': '2026-09-14T00:00:00Z', 'expires_at': '2026-09-15T00:00:00Z',
                'candidates_sha256': hashlib.sha256(candidates).hexdigest(),
                'decisions': [{'atom_id': atom['atom_id'], 'content_hash': atom['content_hash'],
                    'rights': {'outcome': 'CLEARED', 'intended_use': 'local_analysis',
                               'jurisdiction': 'synthetic', 'reviewer': 'synthetic-reviewer',
                               'evidence_sha256': ['1' * 64]},
                    'review': {'decision': 'KEEP', 'reviewer': 'synthetic-reviewer',
                               'evidence_sha256': ['2' * 64]}}]}
    return key, candidates, trust, manifest


def signed(key, candidates, trust, manifest):
    raw = json.dumps(manifest).encode()
    return verify(raw, key.sign(DOMAIN + raw), candidates, trust, now=NOW)


def test_valid_scope_stays_read_only():
    key, candidates, trust, manifest = fixture()
    before = copy.deepcopy(manifest)
    result = signed(key, candidates, trust, manifest)
    assert result['status'] == 'SIGNED_SCOPE_VERIFIED'
    assert result['atom_count'] == 1 and manifest == before
    assert result['admission_enabled'] is result['training_authorized'] is False
    assert result['corpus_mutated'] is False


@pytest.mark.parametrize('mutation', [
    lambda m: m.update(action='train'),
    lambda m: m.update(target='different-corpus'),
    lambda m: m.update(operator='someone-else'),
    lambda m: m.update(expires_at='2026-09-14T12:00:00Z'),
    lambda m: m.update(approved_at='2026-09-15T00:00:00Z'),
    lambda m: m.update(decisions=[]),
    lambda m: m['decisions'][0].update(content_hash='0' * 64),
    lambda m: m['decisions'][0]['rights'].update(outcome='HOLD'),
    lambda m: m['decisions'][0]['rights'].update(intended_use='export'),
    lambda m: m['decisions'][0]['rights'].update(evidence_sha256=[]),
    lambda m: m['decisions'][0]['rights'].update(jurisdiction='NOT_COMPUTABLE'),
    lambda m: m['decisions'][0]['review'].update(reviewer=''),
    lambda m: m['decisions'][0]['review'].update(decision='HOLD'),
    lambda m: m['decisions'][0]['review'].update(evidence_sha256=[]),
    lambda m: m.update(public_key_hex='0' * 64),
])
def test_even_valid_signature_cannot_override_constraints(mutation):
    key, candidates, trust, manifest = fixture()
    mutation(manifest)
    with pytest.raises(ValueError):
        signed(key, candidates, trust, manifest)


def test_signature_tamper_wrong_key_domain_and_revocation():
    key, candidates, trust, manifest = fixture()
    raw = json.dumps(manifest).encode()
    signature = key.sign(DOMAIN + raw)
    for data, sig in [(raw + b' ', signature), (raw, b'0' * 64),
                      (raw, key.sign(raw)),
                      (raw, Ed25519PrivateKey.generate().sign(DOMAIN + raw))]:
        with pytest.raises(ValueError, match='signature'):
            verify(data, sig, candidates, trust, now=NOW)
    trust['revoked_approval_ids'] = [manifest['approval_id']]
    with pytest.raises(ValueError, match='revoked'):
        signed(key, candidates, trust, manifest)


def test_changed_bytes_and_duplicate_json_rejected():
    key, candidates, trust, manifest = fixture()
    with pytest.raises(ValueError, match='changed'):
        signed(key, candidates + b'\n', trust, manifest)
    raw = b'{"approval_id":"a","approval_id":"b"}'
    with pytest.raises(ValueError, match='Duplicate'):
        verify(raw, key.sign(DOMAIN + raw), candidates, trust, now=NOW)


@pytest.mark.parametrize('field,value', [('license', 'NOT_COMPUTABLE'),
    ('license', 'unknown'), ('content_hash', '0' * 64), ('table', []),
    ('lens_hints', {'historical': 'true'})])
def test_signed_bad_atom_rejected(field, value):
    key, candidates, trust, manifest = fixture()
    atom = json.loads(candidates)
    atom[field] = value
    candidates = json.dumps(atom).encode()
    manifest['candidates_sha256'] = hashlib.sha256(candidates).hexdigest()
    with pytest.raises(ValueError):
        signed(key, candidates, trust, manifest)


def test_cli_missing_trust_holds_without_writes(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr('athanor.admission_approval.Path.home', lambda: tmp_path)
    assert main(['--manifest', 'missing', '--signature', 'missing',
                 '--candidates', 'missing']) == 2
    assert json.loads(capsys.readouterr().out)['status'] == 'HOLD'
    assert list(tmp_path.iterdir()) == []


def test_cli_verifies_without_mutation(tmp_path, monkeypatch, capsys):
    key, candidates, trust, manifest = fixture()
    manifest['approved_at'] = '2020-01-01T00:00:00Z'
    manifest['expires_at'] = '2099-01-01T00:00:00Z'
    raw = json.dumps(manifest).encode()
    (tmp_path / '.athanor').mkdir()
    (tmp_path / '.athanor/operator-trust.json').write_text(json.dumps(trust))
    for name, data in [('manifest', raw), ('signature', key.sign(DOMAIN + raw)),
                       ('candidates', candidates)]:
        (tmp_path / name).write_bytes(data)
    monkeypatch.setattr('athanor.admission_approval.Path.home', lambda: tmp_path)
    before = {str(p): p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    assert main(['--manifest', str(tmp_path / 'manifest'),
                 '--signature', str(tmp_path / 'signature'),
                 '--candidates', str(tmp_path / 'candidates')]) == 0
    output = capsys.readouterr().out
    assert json.loads(output)['admission_enabled'] is False
    assert 'Synthetic only.' not in output
    assert before == {str(p): p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
