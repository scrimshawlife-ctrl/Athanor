"""Conservative, reproducible private quarantine cleaning and provisional routing.

This bulk data transformation never changes sources, promotes gold, or trains.
"""
import argparse
import hashlib
import json
import re
import unicodedata
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

from athanor.readiness import MAX_BYTES, _json

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


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def words(text):
    return re.findall(r'\w+', text.casefold())


def clean(text):
    retained, removed = [], []
    for number, raw in enumerate(text.splitlines(), 1):
        line = unicodedata.normalize('NFC', raw).strip()
        reason = None
        if re.fullmatch(r'(?:\{?p\.\s*[\divxlcdm]+\}?|Sacred Texts\s*\|?)', line, re.IGNORECASE):
            reason = 'PAGE_OR_SITE_FOOTER'
        elif re.match(r'^(?:« Previous:|Next:|\[paragraph continues\]$)', line):
            reason = 'READER_NAVIGATION'
        elif line in ('Toggle Sidebar', 'Toggle theme', 'Buy this Book at Amazon.com'):
            reason = 'SITE_CONTROL_OR_AD'
        elif (line.startswith(('](', '[', 'http')) and re.search(
                r'https?://(?:www\.)?(?:tumblr\.com/widgets/share|facebook\.com/sharer|twitter\.com/intent)', line)):
            reason = 'SOCIAL_LINK_FRAGMENT'
        if reason:
            removed.append({'line': number, 'sha256': sha(raw.encode()), 'reason': reason})
        else:
            retained.append(line)
    result = re.sub(r'\n{3,}', '\n\n', '\n'.join(retained)).strip()
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
    catalog_controls = 'Toggle Sidebar' in original and ('\nAuthor\n' in original or '\nTitle\n' in original)
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
    return {'route': route, 'proposed_family': proposed, 'label_evidence': evidence,
            'classification_status': 'INFERRED' if proposed != 'NOT_COMPUTABLE' else 'NOT_COMPUTABLE',
            'flags': flags, 'word_count': nwords}


def build(parent, pack):
    parent, pack = Path(parent), Path(pack)
    if parent.is_symlink() or pack.is_symlink() or pack.stat().st_size > MAX_BYTES:
        raise ValueError('Unsafe or oversized input')
    if (parent / 'manifest.json').is_symlink() or (parent / 'manifest.json').stat().st_size > MAX_BYTES:
        raise ValueError('Unsafe or oversized manifest')
    manifest = _json((parent / 'manifest.json').read_bytes())
    original_hashes = {'manifest.json': sha((parent / 'manifest.json').read_bytes())}
    parsed = {}
    for name in ('features.jsonl', 'targets.jsonl', 'provenance.jsonl', 'quarantine.jsonl'):
        expected = manifest['files'][name]
        if (parent / name).is_symlink() or (parent / name).stat().st_size > MAX_BYTES:
            raise ValueError('Unsafe or oversized prepared file')
        raw = (parent / name).read_bytes()
        if sha(raw) != expected['sha256']:
            raise ValueError('Parent digest mismatch')
        original_hashes[name] = sha(raw)
        parsed[name] = [_json(line) for line in raw.splitlines() if line.strip()]
        if len(raw) != expected['bytes'] or len(parsed[name]) != expected['rows']:
            raise ValueError('Prepared size/count mismatch')
    if sha(pack.read_bytes()) != manifest['source_zip_sha256']:
        raise ValueError('Source ZIP mismatch')
    with zipfile.ZipFile(pack) as archive:
        names = [n for n in archive.namelist() if n.endswith('/atoms_full.jsonl')]
        if len(names) != 1 or archive.getinfo(names[0]).file_size > 20_000_000:
            raise ValueError('Unexpected source member')
        atoms = [_json(line) for line in archive.read(names[0]).splitlines()]
    by_id = {a['atom_id']: a for a in atoms}
    provenance = {p['row_id']: p for p in parsed['provenance.jsonl']}
    qids = [r['row_id'] for r in parsed['quarantine.jsonl']]
    selected = {r['row_id'] for r in parsed['features.jsonl']}
    if (set(qids) & selected or set(qids) | selected != set(provenance)
            or len(provenance) != len(parsed['provenance.jsonl'])):
        raise ValueError('Quarantine is not a disjoint source partition')
    if len(by_id) != len(atoms) or len(set(qids)) != len(qids):
        raise ValueError('Duplicate source/quarantine IDs')
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
               'duplicate_affected_quarantine_rows': sum(bool(r['exact_duplicate_members']) for r in rows),
               'limitations': ['Rule-based provisional classification, not exhaustive semantic review.',
                   'No human approval, rights clearance or automatic gold promotion.',
                   'Exact normalized duplicates only; near-duplicate and complete work grouping pending.',
                   'BODY_CANDIDATE is a review queue, not training eligibility.']}
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
        payload, summary = files(args.prepared, args.pack)
        if args.output is not None:
            if args.output.is_symlink() or args.output.resolve() == args.prepared.resolve():
                raise ValueError('Unsafe output directory')
            if args.verify:
                for name, raw in payload.items():
                    if (args.output / name).is_symlink() or (args.output / name).read_bytes() != raw:
                        raise ValueError('Regenerated artifact differs')
            else:
                args.output.mkdir(parents=True, exist_ok=False)
                for name, raw in payload.items():
                    with (args.output / name).open('xb') as stream:
                        stream.write(raw)
        print(canonical(summary))
        return 2  # Candidate HOLD is not a training approval.
    except (ValueError, KeyError, TypeError, OSError, zipfile.BadZipFile) as exc:
        print(canonical({'status': 'INVALID', 'reason': str(exc), 'training_authorized': False}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
