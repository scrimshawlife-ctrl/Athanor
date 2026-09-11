# Ingest Priority C — consolidated scoreboard (islamic_occult_pd)

- run_id: `ingest-priority-c-consolidated-20260911T070459Z`
- component_runs: ingest-priority-c-20260911T070348Z-fa64c845, ingest-priority-c-20260911T070416Z-5f1d275c
- job_type: harvest | priority: **C** | engine: crawl4ai 0.9.3 (+ urllib + local Gutenberg)
- timestamp_utc: 2026-09-11T07:04:59.573792+00:00
- pages_ok: **15** | pages_fail: **0**
- atoms_written: **88** | atoms_skipped_dupe: 22 | quality_skips: 42
- before_total: **1676** → after_total: **1764**
- `islamic_occult_pd`: **0 → 88** (delta +88)
- types: `{'text': 78, 'correspondence': 10}`
- kinds: `{'picatrix-reception': 9, 'arabic-occult-science': 21, 'arabic-astrology-transmission': 28, 'arabic-philosophy-occult': 20, 'talisman-historical': 10}`
- receipt: `/home/box/.athanor/receipts/ingest-priority-c-consolidated-20260911T070459Z.json`
- backup: `/home/box/.athanor/corpus/atoms.pre-ingest-c-20260911T070202Z.jsonl`
- script: `/workspace/Athanor/scripts/shadow/athanor/ingest_priority_c.py`
- chrome_strip: yes | allowlist respected | no Firecrawl | no Wave 3b | no Enochian | no efficacy | no Hub

## Priority C family delta

| family_id | before | after | delta | % of NEW |
|---|---:|---:|---:|---:|
| `islamic_occult_pd` | 0 | 88 | +88 | 100.0% |

## Correspondence / topic kinds

- `arabic-astrology-transmission`: 28
- `arabic-occult-science`: 21
- `arabic-philosophy-occult`: 20
- `talisman-historical`: 10
- `picatrix-reception`: 9

## Sources (PD)

- Thorndike 1923 *History of Magic…* vol1 ch28 Arabic occult science; ch30 Gerbert/Arabic astrology (Gutenberg 67792)
- Thorndike 1923 vol2 ch38 Arabic astrology translators; ch66 Picatrix (Gutenberg 67330)
- de Boer *History of Philosophy in Islam* — Brethren of Basra / Kindi / natural philosophy (sacred-texts)
- O'Leary *Arabic Thought…* — transmission leaves (sacred-texts)
- Pavitt *Book of Talismans* (1914) — Arab/Islamic-historical leaves only

## HOLD (with reason)

- {"url": "https://archive.org/details/goal-of-the-wise-english", "reason": "HOLD — 2022 Abdullah Hashem English Goal of the Wise (copyrighted modern)"}
- {"url": "https://archive.org/details/the-picatrix-the-goal-of-the-wise-by-hashem-atallah", "reason": "HOLD — Hashem Atallah modern English Picatrix translation (copyright-unclear/modern)"}
- {"url": "https://archive.org/details/christopher-warnock-the-complete-picatrix", "reason": "HOLD — Warnock/Greer modern Complete Picatrix (post-1928 copyright)"}
- {"url": "https://archive.org/details/picatrix_20190508", "reason": "HOLD — anonymous English picatrix upload; no PD year/creator; likely modern translation"}
- {"url": "https://archive.org/details/picatrix_202012", "reason": "HOLD — Alfonso X Picatrix concordance (Hispanic Seminary); stamped CC-BY-ND (not cc-by/pd) + modern editorial layer; OCR also unusable"}
- {"url": "https://archive.org/details/picatrix-ghayat-al-hakim-al-majriti", "reason": "HOLD — Arabic Ghayat al-Hakim upload; no clear PD edition year/license (may be Ritter or modern print)"}
- {"family_id": "enochian", "reason": "HOLD — out of Priority C scope"}
- {"note": "Wave 3b families — PROPOSAL ONLY; do not harvest", "family_ids": ["thelema_pd", "wicca_hist"]}
- {"reason": "below TARGET_MIN 40 (got 22) — quality gate preferred over flood"}

## FAILED

- (none)

## INFERRED license notes

- Thorndike, A History of Magic and Experimental Science vols 1–2 (1923): PD-US (pub. 1923 → PD 2019); Gutenberg 67792/67330 (INFERRED).
- Thorndike ch.66 Picatrix: historical commentary on Latin Picatrix tradition — used in lieu of copyrighted modern English translations (INFERRED).
- de Boer, History of Philosophy in Islam (1903 Eng.): public-domain sacred-texts (INFERRED).
- O'Leary, Arabic Thought and Its Place in History (1922): public-domain sacred-texts (INFERRED).
- Pavitt, Book of Talismans (1914): public-domain; only Arab/Islamic-historical leaves kept (INFERRED).
- Modern Picatrix English (Warnock/Greer, Atallah, Hashem 2022): HOLD copyright — not harvested.
- archive.org Alfonso X Picatrix concordance: HOLD CC-BY-ND + modern editorial; Arabic Ghayat upload: HOLD license-unclear.

## Sample atom_ids

- `islamic_occult_pd:3ad2eae2b497a101`
- `islamic_occult_pd:97435689825730f3`
- `islamic_occult_pd:f31dfe342059e33d`
- `islamic_occult_pd:16b37b02669ba6f5`
- `islamic_occult_pd:6588fd051e2b9362`
- `islamic_occult_pd:7332bd45dde43dec`
- `islamic_occult_pd:d24ffdf2acc0891b`
- `islamic_occult_pd:3dc54056d7d8deac`
- `islamic_occult_pd:d73ca1a35df46a61`
- `islamic_occult_pd:8d7c30860c289155`
- `islamic_occult_pd:6da34aa84c55c015`
- `islamic_occult_pd:eba5360436ef9973`
- `islamic_occult_pd:bf919936e7731146`
- `islamic_occult_pd:61b3347f76103639`

## Propose (never GOLD)

- KEEP: islamic_occult_pd (88 NEW; Thorndike Picatrix + Arabic occult-scientific PD + sacred-texts Islamic scientific)
- HOLD: modern English Picatrix (Warnock/Greer/Atallah/Hashem 2022); Alfonso X concordance CC-BY-ND; Arabic Ghayat upload license-unclear; Wave 3b; Enochian
- DROP: SPA chrome-only after strip; HTTP failures (none this run)

