# Ingest Priority A — consolidated scoreboard

- run_id: `ingest-priority-a-consolidated-20260911T063614Z`
- component_runs: ingest-priority-a-20260911T063120Z-e094a0b6, ingest-priority-a-20260911T063251Z-2434935f, ingest-priority-a-20260911T063433Z-812681b7
- job_type: harvest | engine: crawl4ai 0.9.3 (+ urllib static mirror)
- timestamp_utc: 2026-09-11T06:36:14.802718+00:00
- pages_ok: **73** | pages_fail: **0**
- atoms_written: **385** | atoms_skipped_dupe: 0
- before_total: **1178** → after_total: **1563**
- receipt: `/home/box/.athanor/receipts/ingest-priority-a-consolidated-20260911T063614Z.json`
- script: `/workspace/Athanor/scripts/shadow/athanor/ingest_priority_a.py`
- chrome_strip: yes | allowlist respected | no Firecrawl | no Wave 3b | no Enochian flood
- balance: max family share of NEW = 14.3% (limit 25%)

## Priority A family deltas

| family_id | before | after | delta | session_new | % of NEW |
|---|---:|---:|---:|---:|---:|
| `alchemy_spirit` | 0 | 55 | +55 | 55 | 14.3% |
| `grimoire_other` | 0 | 55 | +55 | 55 | 14.3% |
| `tarot_history` | 0 | 55 | +55 | 55 | 14.3% |
| `mystery_cults` | 0 | 55 | +55 | 55 | 14.3% |
| `solomonic` | 5 | 60 | +55 | 55 | 14.3% |
| `kabbalah_pd` | 16 | 71 | +55 | 55 | 14.3% |
| `runes_eddic` | 16 | 71 | +55 | 55 | 14.3% |

## All families (after)

| family_id | before | after | delta |
|---|---:|---:|---:|
| `enochian` | 513 | 513 | +0 |
| `mesopotamia` | 146 | 146 | +0 |
| `egypt_magical` | 97 | 97 | +0 |
| `astrology_west` | 79 | 79 | +0 |
| `coptic_gnostic` | 76 | 76 | +0 |
| `kabbalah_pd` | 16 | 71 | +55 |
| `runes_eddic` | 16 | 71 | +55 |
| `hermetic` | 68 | 68 | +0 |
| `solomonic` | 5 | 60 | +55 |
| `alchemy_spirit` | 0 | 55 | +55 |
| `grimoire_other` | 0 | 55 | +55 |
| `mystery_cults` | 0 | 55 | +55 |
| `tarot_history` | 0 | 55 | +55 |
| `hebrew_bible_magical` | 53 | 53 | +0 |
| `alchemy_lab` | 34 | 34 | +0 |
| `goetia_catalog` | 29 | 29 | +0 |
| `neoplatonism` | 28 | 28 | +0 |
| `iching_daoist` | 11 | 11 | +0 |
| `chaos_spare_hist` | 7 | 7 | +0 |

## HOLD (with reason)

- {"url_pattern": "sacred-texts.com/book/", "reason": "HOLD Rowe/Achadian modern /book/ essays"}
- {"family_id": "enochian", "reason": "HOLD — skip Enochian this run (prefer no flood)"}
- {"family_id": "alchemy_spirit", "reason": "balance pause >25% of NEW atoms"}
- {"family_id": "solomonic", "reason": "balance pause >25% of NEW atoms"}
- {"family_id": "grimoire_other", "reason": "balance pause >25% of NEW atoms"}
- {"family_id": "tarot_history", "reason": "balance pause >25% of NEW atoms"}
- {"family_id": "mystery_cults", "reason": "balance pause >25% of NEW atoms"}
- {"family_id": "kabbalah_pd", "reason": "balance pause >25% of NEW atoms"}
- {"family_id": "runes_eddic", "reason": "balance pause >25% of NEW atoms"}
- {"family_id": "thelema_pd", "note": "PROPOSAL ONLY — do not harvest this run"}
- {"family_id": "wicca_hist", "note": "PROPOSAL ONLY — do not harvest this run"}
- {"url": "https://archive.sacred-texts.com/grim/moses7/m701.htm", "reason": "DROP SPA/chrome-only after strip_chrome"}

## FAILED

- (none)

## INFERRED license notes

- All Priority A atoms stamped license=public-domain (INFERRED from sacred-texts PD edition claims).
- Waite Pictorial Key 1911: PD-US via sacred-texts tarot/pkt.
- Key of Solomon Mathers 1888: public-domain period translation.
- Cumont Mysteries of Mithra / Taylor Eleusinian: public-domain historical commentary.
- Sepher Yetzirah / Cabala / Jewish Mysticism chapters: public-domain.
- Poetic Edda (incl. Havamal) / related Norse PD translations: public-domain.
- Alchemy spirit/process texts (Hermetic Arcanum, Turba, Paracelsus, Ripley Bosom Book, etc.): public-domain; distinct from alchemy_lab emerald.
- Grimoire_other via BCM Arbatel/Heptameron sections, Moses books, Magus, Abramelin historical chapters: public-domain.

## Propose (never GOLD)

- KEEP: ['alchemy_spirit', 'grimoire_other', 'tarot_history', 'mystery_cults', 'solomonic', 'kabbalah_pd', 'runes_eddic']
- HOLD: Wave 3b (thelema_pd, wicca_hist); Rowe/Achadian `/book/` modern essays
- DROP: SPA chrome-only after strip; HTTP 404 pages

## Sample atom_ids

- `alchemy_spirit:dfceaffe70bd29c1`
- `alchemy_spirit:06e839dc6624e4db`
- `alchemy_spirit:1be6e8967188b4b2`
- `alchemy_spirit:a97819dd7fff0197`
- `alchemy_spirit:41d97261b74d0726`
- `alchemy_spirit:668de4f9bbdb989a`
- `alchemy_spirit:aa341f942b940b6c`
- `alchemy_spirit:fa098473a9190c6e`
- `alchemy_spirit:cc89ce91dce86e2a`
- `alchemy_spirit:419fa750488a0531`

