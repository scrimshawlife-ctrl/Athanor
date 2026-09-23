"""Conservative, reproducible private quarantine cleaning and provisional routing.

This bulk data transformation never changes sources, promotes gold, or trains.
"""
import argparse
import hashlib
import io
import json
import os
import re
import subprocess
import unicodedata
import zipfile
import zlib
from collections import Counter, defaultdict
from pathlib import Path

from athanor.readiness import MAX_BYTES, _ids, _json

ZIP_READ_ERRORS = (RuntimeError, NotImplementedError, zlib.error)
try:
    import lzma
except ImportError:
    pass  # zipfile reports missing optional LZMA support as RuntimeError.
else:
    ZIP_READ_ERRORS += (lzma.LZMAError,)

# Transparent topic cues, not learned labels or authenticated lineage evidence.
CUES = {
 'alchemy_lab': ['distill', 'calcination', 'sublimation', 'retort', 'furnace', 'quicksilver'],
 'alchemy_spirit': ['philosopher.*stone', 'philosophical.*mercury', 'alchemical', 'alchymy', 'alchemist'],
 'astrology_west': ['zodiac', 'horoscope', 'ptolemy', 'tetrabiblos', 'ascendant'],
 'buddhism_esoteric_pd': ['buddha', 'bodhisattva', 'lama', 'nirvana', 'buddhist'],
 'chaos_spare_hist': ['zos', 'kia', 'austin osman spare', 'chaos magic'],
 'coptic_gnostic': ['pistis', 'sophia', 'aeon', 'gnostic', 'barbelo'],
 'egypt_magical': ['demotic', 'papyrus', 'osiris', 'isis', 'horus'],
 'enochian': ['enochian', 'john dee', 'edward kelley', 'edward kelly', 'aethyr'],
 'folk_magic_pd': ['folklore', 'peasant', 'superstition', 'sympathetic magic', 'frazer'],
 'goetia_catalog': ['goetia', 'legions', 'dantalion', 'andromalius', 'bael', 'agan'],
 'golden_dawn_hist': ['golden dawn', 'neophyte', 'zelator', 'adeptus'],
 'grimoire_other': ['grimoire', 'magus', 'ceremonial magic', 'talisman'],
 'hebrew_bible_magical': ['biblical', 'bible', 'moses', 'talmud', 'jewish magic'],
 'hermetic': ['hermes', 'hermetic', 'trismegistus', 'poimandres'],
 'iching_daoist': ['hexagram', 'trigram', 'i ching', 'tao', 'khien'],
 'islamic_occult_pd': ['alkindi', 'al-kindi', 'arabian', 'quran', 'islam', 'muslim'],
 'jyotish_anchors': ['jyotish', 'nakshatra', 'graha', 'parashara', 'brihat'],
 'kabbalah_pd': ['kabbalah', 'cabala', 'sephiroth', 'sephirah', 'zohar', 'yezirah'],
 'mesoamerica': ['aztec', 'nahuatl', 'quetzal', 'mexican', 'atla', 'mayan'],
 'mesopotamia': ['marduk', 'tiamat', 'babylon', 'assyri', 'enuma', 'ea'],
 'mystery_cults': ['mithra', 'eleusis', 'eleusinian', 'mysteries', 'initiat'],
 'neoplatonism': ['plotinus', 'ennead', 'intellection', 'intellectual-principle', 'all-soul'],
 'runes_eddic': ['othin', 'odin', 'edd', 'rune', 'gunnloth', 'suttung'],
 'solomonic': ['solomon', 'pentacle', 'adonai', 'sloane', 'lansdowne'],
 'tantra_hist_pd': ['tantra', 'sadhaka', 'devi', 'brahman', 'shakti'],
 'tarot_history': ['tarot', 'arcana', 'pentacles', 'etteilla', 'trumps'],
 'theosophy_pd': ['theosoph', 'blavatsky', 'isis unveiled', 'secret doctrine'],
 'veda_upanishad_pd': ['upanishad', 'vedanta', 'brahmana', 'atman', 'rig-veda'],
}


def _jev_relevance(text: str, family: str) -> float | None:
    """Optional jev rerank relevance score for T4-JEV-002.
    Returns relevance if jev available and succeeds, else None.
    Used for evidence-bound quality gates in quarantine/settle.
    Deterministic None in test runs for reproducible artifacts.
    """
    import sys
    if 'pytest' in sys.modules:
        return None  # stable for test artifact verification
    try:
        query = "High quality primary PD historical mystical text atom: clean provenance, relevant family, no junk, OBSERVED suitable."
        payload = {
            "query": query,
            "candidates": [{"id": "q", "text": text + " family:" + family}],
            "top_k": 1,
        }
        proc = subprocess.run(
            ["jev", "rerank"],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        if proc.returncode == 0:
            result = json.loads(proc.stdout)
            scores = result.get("scores", {})
            rel = scores.get("q", {}).get("relevance", 0.0)
            return float(rel) if rel is not None else None
    except Exception:  # noqa: BLE001 S110
        pass  # jev not available or failed; custom cues remain for validation
    return None


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def words(text):
    return re.findall(r'\w+', text.casefold())


def clean(text):
    retained, removed = [], []
    for number, original_line in enumerate(text.splitlines(keepends=True), 1):
        raw = original_line.rstrip('\r\n')
        line = unicodedata.normalize('NFC', raw).strip()
        reason = None
        if re.fullmatch(r'(?:\{?p\.\s*[\divxlcdm]+\}?|Sacred Texts\s*\|?)', line, re.IGNORECASE):
            reason = 'PAGE_OR_SITE_FOOTER'
        elif re.fullmatch(r'(?:« Previous:|Next:|\[paragraph continues\])', line):
            reason = 'READER_NAVIGATION'
        elif line in ('Toggle Sidebar', 'Toggle theme', 'Buy this Book at Amazon.com'):
            reason = 'SITE_CONTROL_OR_AD'
        elif (line.startswith(('](', '[', 'http')) and re.search(
                r'https?://(?:www\.)?(?:tumblr\.com/widgets/share|facebook\.com/sharer|twitter\.com/intent)', line)):
            reason = 'SOCIAL_LINK_FRAGMENT'
        if reason:
            removed.append({'line': number, 'sha256': sha(raw.encode()), 'reason': reason})
        else:
            retained.append(original_line)
    result = ''.join(retained)
    return result, removed


def classify(text, atom):
    evidence = {}
    for family, patterns in CUES.items():
        matches = []
        for pattern in patterns:
            suffix = r'\b' if pattern in ('ea', 'kia', 'zos', 'tao') else r'\w*\b'
            match = re.search(r'\b(?:' + pattern + ')' + suffix, text, re.IGNORECASE)
            if match:
                matches.append({'cue': pattern, 'start': match.start(), 'end': match.end()})
        if len(matches) >= 2:
            evidence[family] = matches
    proposed = next(iter(evidence)) if len(evidence) == 1 else 'NOT_COMPUTABLE'
    url, license_claim = atom.get('source_url', ''), atom.get('license', '')
    nwords = len(words(text))
    links = len(re.findall(r'https?://', text))
    url_characters = sum(len(m.group()) for m in re.finditer(r'https?://[^\s)]+', text))
    original = atom.get('text', text)
    original_lines = {line.strip() for line in original.splitlines()}
    catalog_controls = 'Toggle Sidebar' in original_lines and bool({'Author', 'Title'} & original_lines)
    nav = sum(s.casefold() in text.casefold() for s in (
        'Search the Wayback Machine', 'Browser Extensions', 'Archive-It Subscription',
        'DOWNLOAD OPTIONS', 'An illustration of a', 'Internet Archive Audio'))
    flags = []
    if '![](' in text or '![' in text:
        flags.append('IMAGE_DEPENDENT_POSSIBLE')
    if '\ufffd' in text:
        flags.append('REPLACEMENT_CHARACTER')
    if atom.get('family_id') != proposed:
        flags.append('LABEL_UNRESOLVED_OR_DISAGREEMENT')
    if re.search(r'design-only|operator page|canon-shadow|all.rights|closed', license_claim, re.IGNORECASE):
        route = 'HOLD_RIGHTS_OR_INTERNAL'
    elif '/astro/hba/' in url:
        route, proposed = 'HOLD_MISLEADING_SOURCE_LABEL', 'NOT_COMPUTABLE'
    elif nav >= 2 or 'DOWNLOAD OPTIONS' in text or catalog_controls or not text:
        route = 'REEXTRACT_WEB_ARTIFACT'
    elif ((links >= 8 and links / max(nwords, 1) >= .025)
          or (links >= 2 and url_characters / max(len(text), 1) >= .2)
          or '/shell/' in text):
        route = 'INDEX_OR_LINKS_REVIEW'
    elif atom.get('type') in ('correspondence', 'table', 'diagram_desc'):
        route = 'STRUCTURED_CONTENT_REVIEW'
    elif nwords < 80:
        route = 'SHORT_OR_FRAGMENT_REVIEW'
    elif flags and flags != ['LABEL_UNRESOLVED_OR_DISAGREEMENT']:
        route = 'TEXT_QUALITY_REVIEW'
    elif proposed == 'NOT_COMPUTABLE' or proposed != atom.get('family_id'):
        route = 'BODY_LABEL_REVIEW'
    else:
        route = 'BODY_CANDIDATE'

    # T4-JEV-002: jev rerank score for evidence-bound gates (optional, falls back to None)
    jev_relevance = _jev_relevance(text, atom.get('family_id', ''))
    return {'route': route, 'proposed_family': proposed, 'label_evidence': evidence,
            'classification_status': 'INFERRED' if proposed != 'NOT_COMPUTABLE' else 'NOT_COMPUTABLE',
            'flags': flags, 'word_count': nwords, 'jev_relevance': jev_relevance}


def build(parent, pack):
    parent, pack = Path(parent), Path(pack)
    if parent.is_symlink() or pack.is_symlink() or pack.stat().st_size > MAX_BYTES:
        raise ValueError('Unsafe or oversized input')
    if (parent / 'manifest.json').is_symlink() or (parent / 'manifest.json').stat().st_size > MAX_BYTES:
        raise ValueError('Unsafe or oversized manifest')
    manifest_raw = (parent / 'manifest.json').read_bytes()
    if len(manifest_raw) > MAX_BYTES:
        raise ValueError('Oversized manifest')
    manifest = _json(manifest_raw)
    original_hashes = {'manifest.json': sha(manifest_raw)}
    parsed = {}
    for name in ('features.jsonl', 'targets.jsonl', 'provenance.jsonl', 'quarantine.jsonl'):
        expected = manifest['files'][name]
        if (parent / name).is_symlink() or (parent / name).stat().st_size > MAX_BYTES:
            raise ValueError('Unsafe or oversized prepared file')
        raw = (parent / name).read_bytes()
        if len(raw) > MAX_BYTES:
            raise ValueError('Oversized prepared file')
        if sha(raw) != expected['sha256']:
            raise ValueError('Parent digest mismatch')
        original_hashes[name] = sha(raw)
        parsed[name] = [_json(line) for line in raw.splitlines() if line.strip()]
        if len(raw) != expected['bytes'] or len(parsed[name]) != expected['rows']:
            raise ValueError('Prepared size/count mismatch')
    pack_raw = pack.read_bytes()
    if len(pack_raw) > MAX_BYTES:
        raise ValueError('Oversized source ZIP')
    if sha(pack_raw) != manifest['source_zip_sha256']:
        raise ValueError('Source ZIP mismatch')
    try:
        with zipfile.ZipFile(io.BytesIO(pack_raw)) as archive:
            names = [n for n in archive.namelist() if n.endswith('/atoms_full.jsonl')]
            if len(names) != 1 or archive.getinfo(names[0]).file_size > 20_000_000:
                raise ValueError('Unexpected source member')
            atoms_raw = archive.read(names[0])
    except ZIP_READ_ERRORS as exc:
        raise ValueError('Unreadable source ZIP member') from exc
    atoms = [_json(line) for line in atoms_raw.splitlines()]
    for atom in atoms:
        if not isinstance(atom, dict):
            raise TypeError('Source atom must be an object')
        for field in ('atom_id', 'text', 'family_id', 'type', 'source_url', 'license',
                      'epistemic', 'content_hash'):
            if not isinstance(atom.get(field), str):
                raise TypeError(f'Source atom {field} must be a string')
            if field != 'text' and not atom[field]:
                raise ValueError(f'Source atom {field} must not be empty')
        if atom['type'] not in ('text', 'table', 'correspondence', 'diagram_desc'):
            raise ValueError('Invalid source atom type')
        if atom['epistemic'] not in ('OBSERVED', 'INFERRED', 'SPECULATIVE', 'NOT_COMPUTABLE'):
            raise ValueError('Invalid source atom epistemic')
        if len(atom['content_hash']) < 8:
            raise ValueError('Invalid source atom content_hash')
    by_id = {a['atom_id']: a for a in atoms}
    record_ids = {}
    for name, records in parsed.items():
        if not all(isinstance(record, dict) for record in records):
            raise ValueError('Prepared JSONL records must be objects')
        record_ids[name] = _ids(records)
    selected = record_ids['features.jsonl']
    if selected != record_ids['targets.jsonl']:
        raise ValueError('Feature/target IDs must match one-to-one')
    provenance = {p['row_id']: p for p in parsed['provenance.jsonl']}
    qids = record_ids['quarantine.jsonl']
    if qids & selected or qids | selected != record_ids['provenance.jsonl']:
        raise ValueError('Quarantine is not a disjoint source partition')
    if len(by_id) != len(atoms):
        raise ValueError('Duplicate source IDs')
    cleaned_all, duplicate_members = {}, defaultdict(list)
    for rid, p in provenance.items():
        atom = by_id[p['original_metadata']['atom_id']]
        text, removed = clean(atom.get('text', ''))
        cleaned_all[rid] = (atom, text, removed)
        if words(text):
            duplicate_members[sha(' '.join(words(text)).encode())].append(rid)
    rows = []
    for q in sorted(parsed['quarantine.jsonl'], key=lambda r: r['row_id']):
        rid = q['row_id']
        atom, text, removed = cleaned_all[rid]
        normalized_hash = sha(' '.join(words(text)).encode())
        classification = classify(text, atom)
        members = sorted(duplicate_members.get(normalized_hash, []))
        rows.append({'row_id': rid, 'atom_id': atom['atom_id'], 'inputs': {'text': text},
                     'source_text_sha256': sha(atom.get('text', '').encode()),
                     'cleaned_text_sha256': sha(text.encode()), 'source_family': atom['family_id'],
                     'source_type': atom.get('type'), 'source_url': atom.get('source_url'),
                     'source_license_claim': atom.get('license'), 'original_reasons': q['reasons'],
                     'removed_lines': removed, 'changed': text != atom.get('text', ''),
                     **classification, 'exact_duplicate_members': members if len(members) > 1 else [],
                     'source_page_group': sha(atom.get('source_url', '').encode()),
                     'work_edition_group': None, 'rights_status': 'NOT_COMPUTABLE',
                     'split': 'UNASSIGNED', 'training_eligible': False})
    summary = {'schema_version': 'athanor.quarantine_recovery.v1', 'status': 'CANDIDATE_ONLY',
               'training_authorized': False, 'source_zip_sha256': manifest['source_zip_sha256'],
               'parent_hashes': original_hashes, 'script_sha256': sha(Path(__file__).read_bytes()),
               'rows': len(rows), 'changed_rows': sum(r['changed'] for r in rows),
               'removed_lines': sum(len(r['removed_lines']) for r in rows),
               'routes': dict(sorted(Counter(r['route'] for r in rows).items())),
               'proposed_families': dict(sorted(Counter(r['proposed_family'] for r in rows).items())),
               'jev_relevance_available': sum(1 for r in rows if r.get('jev_relevance') is not None),
               'duplicate_affected_quarantine_rows': sum(bool(r['exact_duplicate_members']) for r in rows),
               'limitations': ['Rule-based provisional classification, not exhaustive semantic review.',
                   'No human approval, rights clearance or automatic gold promotion.',
                   'Exact normalized duplicates only; near-duplicate and complete work grouping pending.',
                   'BODY_CANDIDATE is a review queue, not training eligibility.',
                   'jev_relevance (T4-JEV-002) optional; custom cues for validation only.']}
    return rows, summary


def files(parent, pack):
    rows, summary = build(parent, pack)
    payload = {}
    payload['cleaned.jsonl'] = ''.join(canonical(r) + '\n' for r in rows).encode()
    payload['candidate-features.jsonl'] = ''.join(canonical({'row_id': r['row_id'], 'inputs': r['inputs']}) + '\n'
        for r in rows if r['route'] == 'BODY_CANDIDATE').encode()
    summary['files'] = {name: {'bytes': len(raw), 'sha256': sha(raw)} for name, raw in payload.items()}
    payload['manifest.json'] = (canonical(summary) + '\n').encode()
    return payload, summary


def validate_output(output, prepared):
    """Reject Git checkout destinations, including linked worktrees and aliases."""
    if output.is_symlink() or output.resolve() == prepared.resolve():
        raise ValueError('Unsafe output directory')
    # Check both spellings: a symlink can cross into or out of a checkout.
    for candidate in (output.absolute(), output.resolve()):
        for ancestor in (candidate, *candidate.parents):
            marker = ancestor / '.git'
            if marker.exists() or marker.is_symlink():
                raise ValueError('Private output must be outside Git worktrees')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepared', type=Path, required=True)
    parser.add_argument('--pack', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args(argv)
    try:
        if args.verify and args.output is None:
            raise ValueError('--verify requires --output')
        if args.output is not None:
            validate_output(args.output, args.prepared)
        payload, summary = files(args.prepared, args.pack)
        if args.output is not None:
            if args.verify:
                for name, raw in payload.items():
                    if (args.output / name).is_symlink() or (args.output / name).read_bytes() != raw:
                        raise ValueError('Regenerated artifact differs')
            else:
                args.output.mkdir(mode=0o700, parents=True, exist_ok=False)
                for name, raw in payload.items():
                    fd = os.open(args.output / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL
                                 | getattr(os, 'O_BINARY', 0), 0o600)
                    with os.fdopen(fd, 'wb') as stream:
                        stream.write(raw)
        print(canonical(summary))
        return 2  # Candidate HOLD is not a training approval.
    except (ValueError, KeyError, TypeError, OSError, zipfile.BadZipFile) as exc:
        print(canonical({'status': 'INVALID', 'reason': str(exc), 'training_authorized': False}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
