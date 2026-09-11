# Ingest Priority D — consolidated scoreboard (Wave 2 PD families)

- run_id: `ingest-priority-d-consolidated-20260911T072054Z`
- component_runs: ingest-priority-d-20260911T071431Z-85e3c235, ingest-priority-d-20260911T071525Z-0ecdd12c, ingest-priority-d-20260911T071937Z-6817aecc
- job_type: harvest | priority: **D** | engine: crawl4ai 0.9.3 (+ urllib + Met OA API)
- timestamp_utc: 2026-09-11T07:20:54.593631+00:00
- pages_ok: **103** | pages_fail: **3**
- atoms_written: **395** | atoms_skipped_dupe: 29 | quality_skips: 38
- before_total: **1764** → after_total: **2159**
- types: `{'text': 265, 'correspondence': 116, 'diagram_desc': 14}`
- kinds: `{'upanishad-sbe': 60, 'hindu-zodiac-anchor': 50, 'tantra-historical': 58, 'buddhist-esoteric-description': 59, 'hexagram-judgment': 66, 'aztec-hymn': 25, 'rigveda-hymn': 10, 'daoist-pd': 5, 'maya-chilam-balam': 28, 'met-oa-object': 14, 'tantra-shakti-historical': 20}`
- receipt: `/home/box/.athanor/receipts/ingest-priority-d-consolidated-20260911T072054Z.json`
- backup: `/home/box/.athanor/corpus/atoms.pre-ingest-d-20260911T071431Z.jsonl`
- script: `/workspace/Athanor/scripts/shadow/athanor/ingest_priority_d.py`
- chrome_strip: yes | allowlist respected | no Firecrawl | no Wave 3b | no Enochian | no efficacy | no Hub

## Priority D family deltas

| family_id | before | after | delta | % of NEW |
|---|---:|---:|---:|---:|
| `veda_upanishad_pd` | 0 | 70 | +70 | 17.7% |
| `jyotish_anchors` | 0 | 50 | +50 | 12.7% |
| `tantra_hist_pd` | 0 | 78 | +78 | 19.7% |
| `buddhism_esoteric_pd` | 0 | 59 | +59 | 14.9% |
| `iching_daoist` | 33 | 104 | +71 | 18.0% |
| `mesoamerica` | 0 | 67 | +67 | 17.0% |

## Sources (PD)

- Müller Upanishads SBE1/15 + Griffith Rig-Veda hymn leaves (sacred-texts)
- Hindu Book of Astrology 1902 zodiac anchors (efficacy ch HOLD)
- Avalon/Woodroffe Mahanirvana preface + Shakti and Shâkta ch.1 (historical; ritual-formation HOLD)
- Schlagintweit Buddhism in Tibet 1863 Mahayana/mysticism description; SBE49/Lotus doctrinal
- Legge I Ching intros + hexagrams ic23–31 + Taoist PD title leaves
- Brinton Rig Veda Americanus 1890; Roys Chilam Balam 1933 (non-renewal claim)
- Met Open Access Mesoamerican object metadata (CC0)

## HOLD (with reason)

- {"url": "https://sacred-texts.com/bud/ettt/index.htm", "reason": "HOLD — Musés 1961 Esoteric Teachings of the Tibetan Tantra (post-1928 copyright; practice manuals)"}
- {"url": "https://sacred-texts.com/nam/maya/ybac/index.htm", "reason": "HOLD — Gates 1937 Yucatan Before and After the Conquest; renewal-era English translation, no clear non-renewal receipt here"}
- {"url": "https://sacred-texts.com/nam/maya/mhw/index.htm", "reason": "HOLD — Thompson 1950 Maya Hieroglyphic Writing; renewal-era, copyright-unclear for harvest"}
- {"url": "https://sacred-texts.com/astro/hba/hba16.htm", "reason": "HOLD/DROP — HBA 'Rules for Attaining Health, Wealth And Happiness' (efficacy/results framing)"}
- {"note": "tantra ritual-formation leaves (maha05–07, 09–11, 13–14) — HOLD living/operational initiatory practice frames", "paths": ["/tantra/maha/maha05.htm", "/tantra/maha/maha06.htm", "/tantra/maha/maha07.htm", "/tantra/maha/maha09.htm", "/tantra/maha/maha10.htm", "/tantra/maha/maha11.htm", "/tantra/maha/maha13.htm", "/tantra/maha/maha14.htm"]}
- {"host": "www.britishmuseum.org", "reason": "HOLD — BM object pages errored/unstable this run (HTTP 520); prefer Met OA + sacred-texts PD"}
- {"family_id": "enochian", "reason": "HOLD — out of Priority D scope; no Enochian flood"}
- {"note": "Wave 3b families — PROPOSAL ONLY; do not harvest", "family_ids": ["thelema_pd", "wicca_hist"]}
- {"url": "https://collectionapi.metmuseum.org/public/collection/v1/objects/329077", "reason": "DROP — non-Mesoamerican / false-positive Met hit"}
- {"reason": "continue script crashed after atom writes on MET_OBJECT_IDS NameError; atoms kept"}
- {"url": "https://sacred-texts.com/bud/ettt/index.htm", "reason": "HOLD — Musés 1961 Esoteric Teachings of the Tibetan Tantra (copyright + practice manuals)"}
- {"url": "https://sacred-texts.com/nam/maya/ybac/index.htm", "reason": "HOLD — Gates 1937 Yucatan; renewal-era English translation"}
- {"url": "https://sacred-texts.com/nam/maya/mhw/index.htm", "reason": "HOLD — Thompson 1950 Maya Hieroglyphic Writing; copyright-unclear"}
- {"url": "https://sacred-texts.com/astro/hba/hba16.htm", "reason": "HOLD — HBA efficacy chapter"}
- {"note": "tantra ritual-formation leaves maha05–07,09–11,13–14 HOLD (operational initiatory)"}
- {"host": "www.britishmuseum.org", "reason": "HOLD — BM object pages HTTP 520 / unstable"}
- {"family_id": "enochian", "reason": "HOLD — out of Priority D scope"}
- {"note": "Wave 3b PROPOSAL ONLY", "family_ids": ["thelema_pd", "wicca_hist"]}
- {"note": "iching deepen: hexagrams ic32–ic64 still open for later PD deepen"}
- {"note": "tantra: maha00 preface filled early budget; sas02+ / htg deepen still open"}

## FAILED

- https://archive.sacred-texts.com/hin/rigveda/rv02112.htm: HTTP 404 (status=404)
- https://archive.sacred-texts.com/tao/sbe39/sbe3902.htm: HTTP 404 (status=404)
- https://archive.sacred-texts.com/tao/sbe39/sbe3903.htm: HTTP 404 (status=404)

## INFERRED license notes

- Max Müller Upanishads SBE 1/15 (1879/1884): public-domain (INFERRED).
- Griffith Rig Veda (1896): public-domain (INFERRED).
- Bhakti Seva Hindu Book of Astrology (1902): public-domain; efficacy ch HOLD (INFERRED).
- Avalon/Woodroffe Mahanirvana preface + Shakti and Shâkta ch.1 historical: PD; ritual-formation HOLD (INFERRED).
- Schlagintweit Buddhism in Tibet (1863): PD historical description (INFERRED).
- SBE49 / Lotus Sutra Kern: PD doctrinal description (INFERRED).
- Legge I Ching intros + hexagrams ic23–31: PD deepen (INFERRED).
- Brinton Rig Veda Americanus (1890): PD (INFERRED).
- Roys Chilam Balam (1933): sacred-texts non-renewal PD claim (INFERRED).
- Gates Yucatan 1937 + Thompson MHW 1950 + Musés ETTT 1961: HOLD.
- Met Open Access PD object metadata: CC0 (INFERRED via isPublicDomain).
- British Museum: HOLD fetch errors.

## Sample atom_ids

- `veda_upanishad_pd:0e093479bc65b1a6`
- `jyotish_anchors:5cbc385d919ff9ba`
- `tantra_hist_pd:b2e642f657e67849`
- `buddhism_esoteric_pd:91f4becae4d80a19`
- `iching_daoist:18858bcd81169e59`
- `mesoamerica:b0d794085f810adc`
- `veda_upanishad_pd:1d1355cdbc7a163b`
- `veda_upanishad_pd:7490e3e3308e2046`
- `veda_upanishad_pd:b21c1ea354e1aad2`
- `veda_upanishad_pd:1a7ed489b7d53e0f`
- `veda_upanishad_pd:76cbf0ec6503a2b6`
- `veda_upanishad_pd:d5b57e8f6663e47d`
- `veda_upanishad_pd:b4c0ac97f88aad5d`
- `jyotish_anchors:071842858a6925de`
- `tantra_hist_pd:eeb18ed48964e07f`
- `tantra_hist_pd:ff41d76c041176f6`
- `buddhism_esoteric_pd:6237ae862b6658e3`
- `buddhism_esoteric_pd:8a25f55dc0052e8f`

## Propose (never GOLD)

- KEEP: veda_upanishad_pd (70), jyotish_anchors (50), tantra_hist_pd (78), buddhism_esoteric_pd (59), iching_daoist (+71), mesoamerica (67)
- HOLD: ETTT Musés 1961; Gates Yucatan 1937; Thompson MHW 1950; Mahanirvana ritual-formation; HBA efficacy; BM pages; Wave 3b; Enochian; further iching ic32+ / sas deepen
- DROP: SPA chrome-only; non-Meso Met false positives; HTTP 404 leaves

