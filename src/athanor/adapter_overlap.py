"""Bind candidate source bytes to declared, hash-pinned overlap registry evidence."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

from athanor.adapter_data import canonical, compile_candidates, digest
from athanor.readiness import MAX_BYTES, _json


def _hash(value):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None


def load_registry(path, expected_sha256):
    if not isinstance(path, Path):
        raise TypeError('Registry must be supplied as a file path')
    if not _hash(expected_sha256):
        raise ValueError('Explicit registry SHA256 required')
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError('Unsafe registry file')
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise ValueError('Registry SHA256 mismatch')
    return _json(raw)


def project_overlap_groups(rows, registry, bindings):
    compile_candidates(rows)
    if not isinstance(registry, dict) or set(registry) != {
            'schema_version', 'corpus_sha256', 'graph_sha256', 'sources'}:
        raise ValueError('Unexpected overlap registry')
    if registry['schema_version'] != 'athanor.overlap_registry.v1':
        raise ValueError('Unsupported overlap registry')
    if not all(_hash(registry[k]) for k in ('corpus_sha256', 'graph_sha256')):
        raise ValueError('Invalid registry provenance digest')
    sources = registry['sources']
    if not isinstance(sources, dict) or not sources:
        raise ValueError('Registry sources required')
    for rid, record in sources.items():
        if not _hash(rid) or not isinstance(record, dict) or set(record) != {'group_id', 'text_sha256'}:
            raise ValueError('Invalid registry row')
        hashes = record['text_sha256']
        if (not isinstance(record['group_id'], str) or not record['group_id'].strip()
                or not isinstance(hashes, list) or not hashes or not all(_hash(h) for h in hashes)
                or len(hashes) != len(set(hashes))):
            raise ValueError('Invalid registry group or text digests')
    used = {source['id']: source for row in rows for source in row['sources']}
    if not isinstance(bindings, dict) or set(bindings) != set(used):
        raise ValueError('Explicit bindings must cover every candidate source ID')
    mapping = {}
    for sid, source in used.items():
        rid = bindings[sid]
        if not isinstance(rid, str) or rid not in sources:
            raise ValueError('Unknown bound corpus row')
        if source['sha256'] not in sources[rid]['text_sha256']:
            raise ValueError('Candidate text not bound to selected corpus row')
        mapping[sid] = sources[rid]['group_id']
    return mapping


def freeze_with_registry(rows, config, registry_path, bindings, registry_sha256):
    """Verify pinned file bytes inside the receipt-producing boundary.

    Use project_overlap_groups for unpinned in-memory projection; it produces
    no receipt claiming that a supplied byte digest was verified.
    """
    from athanor.adapter_freeze import freeze_candidates
    registry = load_registry(registry_path, registry_sha256)
    result = freeze_candidates(rows, config, project_overlap_groups(rows, registry, bindings))
    result.pop('freeze_sha256')
    result['overlap_registry_sha256'] = registry_sha256
    result['overlap_registry_canonical_sha256'] = digest(canonical(registry))
    result['overlap_source_bindings_sha256'] = digest(canonical(bindings))
    result['unresolved'].append('REGISTRY_AUTHENTICITY_AND_COVERAGE_REVIEW')
    result['freeze_sha256'] = digest(canonical(result))
    return result
