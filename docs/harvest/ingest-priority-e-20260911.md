# Ingest Priority E scoreboard — Wave 3 PD reception

- run_id: `ingest-priority-e-20260911T072836Z-5be6409f`
- job_type: harvest | priority: **E** | engine: crawl4ai 0.9.3 (+ urllib + Gutenberg cache)
- timestamp_utc: 2026-09-11T07:29:41.416032+00:00
- pages_ok: **26** | pages_fail: **0**
- atoms_written: **215** | dupes: 11 | quality_skips: 96
- before_total: **2159** → after_total: **2374**
- types: `{'text': 215}`
- kinds: `{'westcott-historic-lecture': 5, 'mathers-kabbalah-unveiled-hist': 40, 'waite-bcm-historical-survey': 20, 'blavatsky-isis-unveiled': 28, 'blavatsky-secret-doctrine': 28, 'leadbeater-textbook-theosophy': 9, 'frazer-golden-bough-folk': 45, 'grimm-folk-tradition-prose': 20, 'spare-focus-of-life': 12, 'spare-anathema-of-zos': 8}`
- receipt: `/home/box/.athanor/receipts/ingest-priority-e-20260911T072836Z-5be6409f.json`
- backup: `/home/box/.athanor/corpus/atoms.pre-ingest-e-20260911T072836Z.jsonl`
- script: `/workspace/Athanor/scripts/shadow/athanor/ingest_priority_e.py`
- chrome_strip: yes | allowlist respected | no Firecrawl | no Wave 3b | no Enochian | no efficacy | no Hub | STOP after E

## Priority E family deltas

| family_id | before | after | delta | % of NEW |
|---|---:|---:|---:|---:|
| `golden_dawn_hist` | 0 | 65 | +65 | 30.2% |
| `theosophy_pd` | 0 | 65 | +65 | 30.2% |
| `folk_magic_pd` | 0 | 65 | +65 | 30.2% |
| `chaos_spare_hist` | 7 | 27 | +20 | 9.3% |

## Sources used

- sacred-texts: Westcott Historic Lecture (G.D.)
- sacred-texts: Mathers Kabbalah Unveiled (1887) historical leaves
- sacred-texts: Waite Book of Ceremonial Magic historical survey (conjuration HOLD)
- sacred-texts: Blavatsky Isis Unveiled + Secret Doctrine
- Gutenberg #55618: Blavatsky Key to Theosophy
- sacred-texts: Leadbeater Textbook of Theosophy (1912); Steiner Theosophy (1910)
- sacred-texts: Frazer Golden Bough folk-magic anthropological leaves
- sacred-texts: Grimm Household Tales tradition-prose folk motifs
- sacred-texts: Spare Focus of Life (1921) + Anathema of Zos (1927) PD-US only

## HOLD (with reason)

- {"url": "https://sacred-texts.com/eso/ (Regardie / modern GD manuals)", "reason": "HOLD — Israel Regardie Golden Dawn materials remain copyright; not harvested"}
- {"url": "https://sacred-texts.com/eso/chaos/zos.txt", "reason": "HOLD — Kenneth Grant Cults of the Shadow excerpt (copyright)"}
- {"url": "https://sacred-texts.com/eso/chaos/sparezia.txt", "reason": "HOLD — modern secondary commentary (1993 Usenet), not clear PD Spare primary"}
- {"url": "https://sacred-texts.com/eso/chaos/chaosdef.htm", "reason": "HOLD — modern Defining Chaos; chaos_late_hist / Wave 3b-adjacent"}
- {"url": "https://sacred-texts.com/eso/chaos/monastic.txt", "reason": "HOLD — modern Chaos Monasticism; not historical Spare PD"}
- {"note": "TOPY materials — HOLD (modern; chaos_late_hist / Wave 3b-adjacent)", "paths": ["/eso/topy/topybook.txt", "/eso/topy/topymani.htm", "/eso/topy/black.htm", "/eso/topy/topyfaq.txt"]}
- {"note": "PA Dutch Pow-Wows / Long Lost Friend operational charm leaves — HOLD efficacy framing", "paths": ["/ame/pow/pow003.htm", "/ame/pow/pow012.htm", "/ame/pow/pow016.htm"]}
- {"note": "Waite Book of Ceremonial Magic conjuration/demon catalog leaves — HOLD summon/efficacy", "paths": ["/grim/bcm/bcm51.htm", "/grim/bcm/bcm61.htm", "/grim/bcm/bcm63.htm"]}
- {"family_id": "enochian", "reason": "HOLD — Priority F = no new Enochian; out of Priority E scope"}
- {"note": "Wave 3b families — PROPOSAL ONLY; do not harvest", "family_ids": ["thelema_pd", "wicca_hist", "spiritualism_pd", "new_thought_pd", "ceremonial_revival_hist", "neopagan_recon_hist", "atr_open_hist", "chaos_late_hist"]}
- {"note": "Spare UK copyright life+70 (d.1956) may still apply in UK until end-2026; harvested only as PD-US published ≤1927 with INFERRED license note"}
- {"family_id": "golden_dawn_hist", "reason": "NOTE share 30.2% of NEW exceeds 25% soft balance"}
- {"family_id": "theosophy_pd", "reason": "NOTE share 30.2% of NEW exceeds 25% soft balance"}
- {"family_id": "folk_magic_pd", "reason": "NOTE share 30.2% of NEW exceeds 25% soft balance"}

## FAILED

- (none)

## INFERRED license notes

- Westcott Historic Lecture (G.D.): public-domain sacred-texts (INFERRED).
- Mathers Kabbalah Unveiled (1887): public-domain GD historical reception (INFERRED).
- Waite Book of Ceremonial Magic (1911): PD historical survey leaves only; conjuration/demon leaves HOLD (INFERRED).
- Regardie Golden Dawn corpus: HOLD copyright.
- Blavatsky Isis Unveiled (1877) + Secret Doctrine (1888): public-domain (INFERRED).
- Blavatsky Key to Theosophy: Gutenberg #55618 public-domain (INFERRED).
- Leadbeater Textbook of Theosophy (1912): public-domain (INFERRED).
- Steiner Theosophy tr. Shields (1910): public-domain (INFERRED).
- Frazer Golden Bough PD leaves: anthropological folk-magic reception (INFERRED).
- Grimm Household Tales PD English: tradition-prose folk motifs (INFERRED).
- PA Dutch Pow-Wows / Hohman Long Lost Friend: HOLD efficacy/charm operational leaves.
- Spare Focus of Life (1921) + Anathema of Zos (1927): PD-US (INFERRED); UK life+70 may apply until end-2026.
- Kenneth Grant Cults of the Shadow Spare excerpt (zos.txt): HOLD copyright.
- Modern chaos commentary / TOPY / Defining Chaos / Monasticism: HOLD (chaos_late / Wave 3b).
- Wave 3b families: PROPOSAL ONLY — not harvested.
- Enochian: HOLD — Priority F = no new Enochian.

## Sample atom_ids

- `golden_dawn_hist:80af8dc256a02850`
- `golden_dawn_hist:9b63d9c3c70c23fa`
- `golden_dawn_hist:23b871cfcc74b844`
- `golden_dawn_hist:0120d32c03f78a12`
- `golden_dawn_hist:bb2a12389ae2ae48`
- `golden_dawn_hist:ae91f7ef1e9f44f2`
- `golden_dawn_hist:f6de590763a008d4`
- `golden_dawn_hist:b0ab83ebea511b44`
- `golden_dawn_hist:2bd2f5005f328ebb`
- `golden_dawn_hist:1da7d132a285743a`
- `golden_dawn_hist:603803a8bf56df8f`
- `golden_dawn_hist:8ef4bb76b0823aae`
- `golden_dawn_hist:bc381ac3eb2934fe`
- `golden_dawn_hist:9088515a3e51fc23`
- `golden_dawn_hist:c4a9dc62d336bac8`
- `golden_dawn_hist:a609884b4c18879e`
- `golden_dawn_hist:c3452975aec701cd`
- `golden_dawn_hist:dcd34cfc857195c6`
- `golden_dawn_hist:1908e9d9bcad1f97`
- `golden_dawn_hist:83767ca97b21159f`

## Propose (never GOLD)

- KEEP: golden_dawn_hist, theosophy_pd, folk_magic_pd, chaos_spare_hist
- HOLD: Regardie GD; Grant Cults of the Shadow; modern Spare commentary; TOPY/chaos_late; Pow-Wow efficacy charms; Waite conjuration leaves; Wave 3b; Enochian/Priority F; Spare UK term caveat
- DROP: SPA chrome-only after strip; HTTP failures; efficacy-framed chunks

## STOP

- Priority E complete for this run. Do **not** start Wave 3b. Priority F = no new Enochian.


## Post-run notes

- Gutenberg #55618 Key to Theosophy was cached under `cache-e/` but not ingested: `theosophy_pd` already hit soft-cap 65 from Isis Unveiled + Secret Doctrine + Leadbeater.
- Steiner Theosophy leaves planned but not reached (family soft-cap).
- Balance NOTE: empty families each ~30.2% of NEW because `chaos_spare_hist` carefully capped at +20; soft-cap notes recorded in receipt HOLD.
- STOP: no Wave 3b started; Priority F = no new Enochian.
