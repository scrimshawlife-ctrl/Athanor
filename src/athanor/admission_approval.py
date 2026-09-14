"""Read-only, exact-byte signed approval verification. Never admits or signs data."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from athanor.readiness import _json

DOMAIN = b'athanor.corpus-admission-approval.v1\x00'
LIMIT = 16 * 1024 * 1024


def _shape(value, keys):
    if not isinstance(value, dict) or set(value) != set(keys.split()):
        raise ValueError('Unexpected object fields')


def _text(value):
    if not isinstance(value, str) or not value.strip() or value == 'NOT_COMPUTABLE':
        raise ValueError('Missing resolved evidence or identity')
    return value


def _hash(value):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
        raise ValueError('Expected lowercase SHA256')
    return value


def _date(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ', value):
        raise ValueError('Expected UTC timestamp at second precision')
    return datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)


def _refs(values):
    if not isinstance(values, list) or not values or len(values) > 100:
        raise ValueError('Evidence references required')
    if len({_hash(v) for v in values}) != len(values):
        raise ValueError('Duplicate evidence references')


def verify(manifest_bytes, signature, candidate_bytes, trust, *, now=None):
    """Trust must come from operator-controlled configuration, never the submission.

    Signature authenticates an operator attestation, not the truth of its evidence.
    This result is not an admission token; a future writer must reverify exact bytes.
    """
    for data, limit in ((manifest_bytes, 1024 * 1024), (candidate_bytes, LIMIT)):
        if not isinstance(data, bytes) or not 0 < len(data) <= limit:
            raise ValueError('Missing or oversized input')
    if not isinstance(signature, bytes) or len(signature) != 64:
        raise ValueError('Expected raw 64-byte Ed25519 signature')
    _shape(trust, 'schema_version operator public_key_hex revoked_approval_ids')
    if trust['schema_version'] != 'athanor.operator_trust.v1':
        raise ValueError('Unknown trust configuration')
    _text(trust['operator'])
    _hash(trust['public_key_hex'])  # Raw Ed25519 public key is 32 bytes, hex encoded.
    revoked = trust['revoked_approval_ids']
    if not isinstance(revoked, list) or any(not isinstance(v, str) or not v for v in revoked):
        raise ValueError('Invalid revocation configuration')
    try:
        from cryptography.exceptions import InvalidSignature, UnsupportedAlgorithm
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    except ImportError as exc:
        raise ValueError('Install the approval extra; verification unavailable') from exc
    try:
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(trust['public_key_hex'])).verify(
            signature, DOMAIN + manifest_bytes)
    except InvalidSignature as exc:
        raise ValueError('Invalid operator signature') from exc
    except UnsupportedAlgorithm as exc:
        raise ValueError('Ed25519 verification unavailable on this backend') from exc
    m = _json(manifest_bytes)
    _shape(m, 'schema_version approval_id operator action target approved_at expires_at '
           'candidates_sha256 decisions')
    if (m['schema_version'] != 'athanor.corpus_admission_approval.v1'
            or m['action'] != 'admit_local_retrieval'
            or m['target'] != 'athanor.local_retrieval_corpus'
            or m['operator'] != trust['operator']):
        raise ValueError('Approval scope mismatch')
    if _text(m['approval_id']) in revoked:
        raise ValueError('Approval revoked')
    now = now if now is not None else datetime.now(timezone.utc)
    if now.tzinfo is None or not _date(m['approved_at']) <= now < _date(m['expires_at']):
        raise ValueError('Approval is not currently valid')
    if _hash(m['candidates_sha256']) != hashlib.sha256(candidate_bytes).hexdigest():
        raise ValueError('Candidate bytes changed')
    rows = [_json(line) for line in candidate_bytes.splitlines() if line.strip()]
    if not rows or len(rows) > 10000:
        raise ValueError('Invalid candidate count')
    by_id = {}
    for atom in rows:
        if not isinstance(atom, dict):
            raise TypeError('Atom must be an object')
        required = {'atom_id', 'family_id', 'type', 'text', 'license', 'source_url',
                    'epistemic', 'content_hash'}
        if not required <= set(atom) or set(atom) - required - {
                'lens_hints', 'table', 'correspondence', 'diagram_desc'}:
            raise ValueError('Unexpected atom fields')
        for field in ('atom_id', 'family_id', 'text', 'license', 'source_url'):
            _text(atom[field])
        if atom['license'].strip().casefold() in {'unknown', 'hold', 'denied', 'not_computable'}:
            raise ValueError('Unresolved license')
        for field in ('table', 'correspondence'):
            if field in atom and not isinstance(atom[field], dict):
                raise ValueError('Structured atom content must be an object')
        if 'diagram_desc' in atom and not isinstance(atom['diagram_desc'], str):
            raise ValueError('Diagram description must be text')
        if 'lens_hints' in atom:
            hints = atom['lens_hints']
            if not isinstance(hints, dict) or any(
                    key in {'historical', 'symbolic', 'operational'} and type(value) is not bool
                    for key, value in hints.items()):
                raise ValueError('Invalid lens hints')
        if atom['atom_id'] in by_id:
            raise ValueError('Duplicate atom ID')
        if atom['type'] not in {'text', 'table', 'correspondence', 'diagram_desc'}:
            raise ValueError('Unknown atom type')
        if atom['epistemic'] not in {'OBSERVED', 'INFERRED', 'SPECULATIVE', 'NOT_COMPUTABLE'}:
            raise ValueError('Unknown epistemic label')
        if _hash(atom['content_hash']) != hashlib.sha256(atom['text'].encode('utf-8')).hexdigest():
            raise ValueError('Stale atom text digest')
        by_id[atom['atom_id']] = atom
    decisions = m['decisions']
    if not isinstance(decisions, list) or len(decisions) != len(rows):
        raise ValueError('Review decisions must cover every atom')
    seen = set()
    for decision in decisions:
        _shape(decision, 'atom_id content_hash rights review')
        aid = _text(decision['atom_id'])
        if aid not in by_id or aid in seen or decision['content_hash'] != by_id[aid]['content_hash']:
            raise ValueError('Review binding mismatch')
        seen.add(aid)
        rights, review = decision['rights'], decision['review']
        _shape(rights, 'outcome intended_use jurisdiction reviewer evidence_sha256')
        if rights['outcome'] != 'CLEARED' or rights['intended_use'] != 'local_analysis':
            raise ValueError('Rights are not cleared for local analysis')
        _text(rights['jurisdiction'])
        _text(rights['reviewer'])
        _refs(rights['evidence_sha256'])
        _shape(review, 'decision reviewer evidence_sha256')
        if review['decision'] != 'KEEP':
            raise ValueError('Content review is not KEEP')
        _text(review['reviewer'])
        _refs(review['evidence_sha256'])
    return {'status': 'SIGNED_SCOPE_VERIFIED', 'approval_id': m['approval_id'],
            'manifest_sha256': hashlib.sha256(manifest_bytes).hexdigest(),
            'candidates_sha256': m['candidates_sha256'], 'atom_count': len(rows),
            'corpus_mutated': False, 'admission_enabled': False, 'training_authorized': False,
            'evidence_truth': 'NOT_COMPUTABLE', 'gold_certification': 'NOT_COMPUTABLE'}


def _read(path, limit):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError('Expected regular non-symlink input')
    with path.open('rb') as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError('Input exceeds size limit')
    return data


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--signature', required=True, type=Path)
    parser.add_argument('--candidates', required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        # No CLI/environment override: trust is not submitted with candidate data.
        trust = _json(_read(Path.home() / '.athanor/operator-trust.json', 65536))
        result = verify(_read(args.manifest, 1024 * 1024), _read(args.signature, 64),
                        _read(args.candidates, LIMIT), trust)
    except (ValueError, TypeError, KeyError, OSError, RecursionError) as exc:
        result = {'status': 'HOLD', 'reason': str(exc), 'admission_enabled': False,
                  'training_authorized': False, 'corpus_mutated': False}
        print(json.dumps(result))
        return 2
    print(json.dumps(result))
    return 0  # Successful verification only; no writer is exposed.


if __name__ == '__main__':
    raise SystemExit(main())
