# Ingest Priority F scoreboard — fill3000

- run_id: `ingest-priority-f-fill3000-20260911T075202Z-bfc3931b`
- job_type: harvest | priority: **F** | goal: **fill3000** | engine: crawl4ai 0.9.3 (+ urllib)
- timestamp_utc: 2026-09-11T07:59:36.429986+00:00
- pages_ok: **180** | pages_fail: **0**
- atoms_written: **626** | dupes: 49 | quality_skips: 122
- before_total: **2374** → after_total: **3000** (target ≥3000)
- types: `{'text': 567, 'correspondence': 59}`
- kinds: `{'plotinus-enneads': 60, 'goetia-spirit-catalog': 55, 'alchemy-lab-process': 55, 'hindu-zodiac-anchor': 4, 'jewish-magic-superstition': 55, 'grimoire-other-hist': 50, 'mithra-eleusis': 50, 'buddhist-esoteric-description': 50, 'greater-key-hist': 45, 'arabic-philosophy-occult': 45, 'upanishad-sbe': 45, 'tantra-historical': 40, 'maya-chilam-balam': 40, 'frazer-golden-bough': 32}`
- receipt: `/home/box/.athanor/receipts/ingest-priority-f-fill3000-20260911T075202Z-bfc3931b.json`
- backup: `/home/box/.athanor/corpus/atoms.pre-ingest-f-20260911T075202Z.jsonl`

## Per-family NEW

| family_id | before | after | delta | % of NEW |
|---|---:|---:|---:|---:|
| neoplatonism | 28 | 88 | **60** | 9.6% |
| goetia_catalog | 29 | 84 | **55** | 8.8% |
| alchemy_lab | 34 | 89 | **55** | 8.8% |
| jyotish_anchors | 50 | 54 | **4** | 0.6% |
| hebrew_bible_magical | 53 | 108 | **55** | 8.8% |
| grimoire_other | 55 | 105 | **50** | 8.0% |
| mystery_cults | 55 | 105 | **50** | 8.0% |
| buddhism_esoteric_pd | 59 | 109 | **50** | 8.0% |
| solomonic | 60 | 105 | **45** | 7.2% |
| islamic_occult_pd | 88 | 133 | **45** | 7.2% |
| veda_upanishad_pd | 70 | 115 | **45** | 7.2% |
| tantra_hist_pd | 78 | 118 | **40** | 6.4% |
| mesoamerica | 67 | 107 | **40** | 6.4% |
| folk_magic_pd | 65 | 97 | **32** | 5.1% |
| theosophy_pd | 65 | 65 | **0** | 0.0% |
| golden_dawn_hist | 65 | 65 | **0** | 0.0% |

## HOLD / DROP notes (proposals only — no settle)

- {'url_pattern': 'sacred-texts.com/book/', 'reason': 'HOLD Rowe/Achadian modern /book/ essays'}
- {'family_id': 'enochian', 'reason': 'HOLD — no new Enochian harvest (overweight)'}
- {'note': 'Wave 3b families — PROPOSAL ONLY; do not harvest', 'family_ids': ['thelema_pd', 'wicca_hist', 'spiritualism_pd', 'new_thought_pd', 'ceremonial_revival_hist', 'neopagan_recon_hist', 'atr_open_hist', 'chaos_late_hist']}
- {'url': 'https://sacred-texts.com/astro/hba/hba16.htm', 'reason': 'HOLD/DROP — efficacy/results framing'}
- {'url': 'https://sacred-texts.com/bud/ettt/index.htm', 'reason': 'HOLD — Musés 1961 copyright / practice manuals'}
- {'note': 'goetia conjuration/summon UX leaves — HOLD; catalog description only', 'paths': ['/grim/lks/lks28.htm', '/grim/lks/lks29.htm', '/grim/lks/lks30.htm', '/grim/bcm/bcm51.htm', '/grim/bcm/bcm61.htm', '/grim/bcm/bcm63.htm']}
- {'note': 'PA Dutch operational charm leaves — HOLD efficacy', 'paths': ['/ame/pow/pow003.htm', '/ame/pow/pow012.htm', '/ame/pow/pow016.htm']}
- {'note': 'tantra ritual-formation leaves — HOLD living practice frames', 'paths': ['/tantra/maha/maha05.htm', '/tantra/maha/maha06.htm', '/tantra/maha/maha07.htm', '/tantra/maha/maha09.htm', '/tantra/maha/maha10.htm', '/tantra/maha/maha11.htm', '/tantra/maha/maha13.htm', '/tantra/maha/maha14.htm']}
- {'reason': 'stop — corpus>=3000 or NEW>=850'}

## FAILED (sample)


## Hard locks honored

- no Firecrawl / no Enochian flood / no Wave 3b harvest / no HF upload / no git-commit atoms
- Crawl4AI 0.9.3 from Hyperlex venv; UA `AthanorCorpusBot/0.2`; ≤1 req / 2.1s / host; robots.txt
- chrome strip via `athanor.chrome.strip_chrome`; epistemic=INFERRED; efficacy=null
- balance soft-cap ≤25% NEW; family soft_cap=60

