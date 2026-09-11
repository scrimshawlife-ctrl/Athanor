# Ingest Priority B — consolidated scoreboard (correspondence / table)

- run_id: `ingest-priority-b-consolidated-20260911T064621Z`
- component_runs: ingest-priority-b-20260911T064148Z-4e8c866f, ingest-priority-b-20260911T064428Z-fb0854b4
- job_type: harvest | priority: **B** | engine: crawl4ai 0.9.3 (+ urllib static mirror)
- timestamp_utc: 2026-09-11T06:46:21.378667+00:00
- pages_ok: **60** | pages_fail: **0**
- atoms_written: **113** | atoms_skipped_dupe: 25 | quality_skips: 76
- before_total: **1563** → after_total: **1676**
- types: `{'table': 23, 'correspondence': 90}`
- kinds: `{'letter-watchtower': 18, 'hexagram-judgment': 22, 'planet-metal': 33, 'planet-day-hour': 16, 'element-direction': 3, 'tarot-suit-element': 15, 'sephirah-path': 6}`
- receipt: `/home/box/.athanor/receipts/ingest-priority-b-consolidated-20260911T064621Z.json`
- backup: `/home/box/.athanor/corpus/atoms.pre-ingest-b-20260911T064023Z.jsonl`
- script: `/workspace/Athanor/scripts/shadow/athanor/ingest_priority_b.py`
- chrome_strip: yes | allowlist respected | no Firecrawl | no Wave 3b | no Enochian flood | no efficacy | no Hub
- balance: max family share of NEW = 21.2% (limit 25%)

## Priority B family deltas

| family_id | before | after | delta | session_new | % of NEW |
|---|---:|---:|---:|---:|---:|
| `kabbalah_pd` | 71 | 95 | +24 | 24 | 21.2% |
| `iching_daoist` | 11 | 33 | +22 | 22 | 19.5% |
| `hermetic` | 68 | 90 | +22 | 22 | 19.5% |
| `astrology_west` | 79 | 95 | +16 | 16 | 14.2% |
| `tarot_history` | 55 | 70 | +15 | 15 | 13.3% |
| `alchemy_spirit` | 55 | 69 | +14 | 14 | 12.4% |
| `runes_eddic` | 71 | 71 | +0 | 0 | 0.0% |
| `enochian` | 513 | 513 | +0 | 0 | 0.0% |

## Correspondence kinds

- `planet-metal`: 33
- `hexagram-judgment`: 22
- `letter-watchtower`: 18
- `planet-day-hour`: 16
- `tarot-suit-element`: 15
- `sephirah-path`: 6
- `element-direction`: 3

## All families (after)

| family_id | before | after | delta |
|---|---:|---:|---:|
| `enochian` | 513 | 513 | +0 |
| `mesopotamia` | 146 | 146 | +0 |
| `egypt_magical` | 97 | 97 | +0 |
| `astrology_west` | 79 | 95 | +16 |
| `kabbalah_pd` | 71 | 95 | +24 |
| `hermetic` | 68 | 90 | +22 |
| `coptic_gnostic` | 76 | 76 | +0 |
| `runes_eddic` | 71 | 71 | +0 |
| `tarot_history` | 55 | 70 | +15 |
| `alchemy_spirit` | 55 | 69 | +14 |
| `solomonic` | 60 | 60 | +0 |
| `grimoire_other` | 55 | 55 | +0 |
| `mystery_cults` | 55 | 55 | +0 |
| `hebrew_bible_magical` | 53 | 53 | +0 |
| `alchemy_lab` | 34 | 34 | +0 |
| `iching_daoist` | 11 | 33 | +22 |
| `goetia_catalog` | 29 | 29 | +0 |
| `neoplatonism` | 28 | 28 | +0 |
| `chaos_spare_hist` | 7 | 7 | +0 |

## HOLD (with reason)

- {"url_pattern": "sacred-texts.com/book/", "reason": "HOLD Rowe/Achadian modern /book/ essays"}
- {"family_id": "enochian", "reason": "HOLD — prefer Hebrew/kabbalah letter tables over Enochian watchtower ritual; skip Enochian this run"}
- {"family_id": "runes_eddic", "reason": "HOLD — no clean PD rune correspondence table in allowlisted set this run (poem text already Priority A)"}
- {"family_id": "thelema_pd", "note": "PROPOSAL ONLY — Wave 3b; do not harvest"}
- {"family_id": "wicca_hist", "note": "PROPOSAL ONLY — Wave 3b; do not harvest"}
- {"family_id": "iching_daoist", "reason": "balance pause >25% of NEW atoms"}
- {"family_id": "hermetic", "reason": "balance pause >25% of NEW atoms"}
- {"family_id": "astrology_west", "reason": "balance pause >25% of NEW atoms"}
- {"family_id": "tarot_history", "reason": "balance pause >25% of NEW atoms"}
- {"reason": "continue-pass rebalance for underfilled kinds (hexagram/sephirah/magus scales)"}
- {"family_id": "kabbalah_pd", "reason": "balance pause >25% of NEW atoms"}
- {"reason": "below TARGET_MIN 40 (got 39) — quality gate preferred over flood"}

## FAILED

- (none)

## INFERRED license notes

- Sepher Yetzirah / Cabala (Pick 1913) / Kabbalah Unveiled chapters: public-domain letter & sephirah tables (INFERRED).
- I Ching Legge SBE vol.16 hexagram judgments: public-domain.
- Barrett Magus (Agrippa-derived) scales, planetary tables, elements: public-domain on sacred-texts.
- Key of Solomon Mathers days/hours: public-domain period translation.
- Ptolemy Tetrabiblos PD chapters: public-domain.
- Waite Pictorial Key 1911 + Mathers Tarot: public-domain suit/element historical.
- Paracelsus / alchemy spirit metal-planet process: public-domain.

## Propose (never GOLD)

- KEEP: ['alchemy_spirit', 'astrology_west', 'hermetic', 'iching_daoist', 'kabbalah_pd', 'tarot_history']
- HOLD: Enochian watchtower ritual (prefer Hebrew letter tables); runes_eddic (no clean PD correspondence table this run); Wave 3b; Rowe `/book/`; element-direction still thin (3)
- DROP: SPA chrome-only after strip; HTTP 404

## Sample atom_ids

- `kabbalah_pd:73eb00803613e7e1`
- `kabbalah_pd:04667415dbb30fd3`
- `kabbalah_pd:85ae0fa8de3fec89`
- `kabbalah_pd:db3c6be7e2661f7b`
- `kabbalah_pd:85819b08230966eb`
- `kabbalah_pd:b192e135355b18bd`
- `kabbalah_pd:64eaecb207d85afd`
- `kabbalah_pd:e64d9912902c4965`
- `kabbalah_pd:7efc7c17e475317b`
- `kabbalah_pd:5f7064cb88d48652`
- `kabbalah_pd:597e07fcd7829a65`
- `kabbalah_pd:b7ec60e28b3d9c7b`

