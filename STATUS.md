# Athanor STATUS

**Lane:** SHADOW  
**Version:** see `VERSION`  
**Remote:** https://github.com/scrimshawlife-ctrl/Athanor  

| Area | State |
|------|-------|
| Spec Kit spine (000) | Sealed |
| Hero + atlas art | Shipped under `assets/` |
| Package | `athanor` CLI `doctor` / `retrieve` / `--version` |
| CI | `.github/workflows/validate.yml` |
| Wave 0 harvest | **GO** — Crawl4AI 0.9.3 · **319** atoms · local SoT only |
| Hub / train | Blocked |

## Wave 0 harvest (OBSERVED 2026-09-10 PT)

- SoT: `~/.athanor/corpus/atoms.jsonl` (not in git)
- Receipt: `~/.athanor/receipts/wave0-enochian-20260911T044756Z-95149c51.json`
- Scoreboard copy: `/workspace/athanor-harvest/wave0-enochian-20260911-045309.md`
- Engine: crawl4ai 0.9.3 · pages_ok 37 · failures 2 (I Ching classic paths 404; recovered via `/book/the-i-ching`)
- Epistemic: all atoms **INFERRED** until operator settle

| family_id | n |
|-----------|---|
| enochian | 128 |
| hermetic | 56 |
| alchemy_lab | 32 |
| goetia_catalog | 32 |
| egypt_magical | 30 |
| runes_eddic | 15 |
| kabbalah_pd | 13 |
| iching_daoist | 13 |
| **total** | **319** |

Next: operator settle gold · train still gated. Offline retrieve: shipped on `feat/offline-retrieve`.

## Notion + Orchestra adapt (OBSERVED 2026-09-10 PT)

- Source: Historical Proto-Systems Integration Layer + Hermes Orchestra references
- Receipt: `adapt-notion-orchestra-20260911T050713Z`
- **+68** atoms → corpus total **387** (local SoT)
- Doc: `docs/adapt-notion-orchestra.md`

## Deepen + Wave 1 harvest (OBSERVED 2026-09-10 PT)

- Receipt: `deepen-20260911T051038Z-14f21ac2`
- Net **+840** atoms → corpus total **1227** (0 failures, 162 dupe skips)
- Casaubon IA deepen + 15 sacred-texts Enochian /book/ + Wave 1 (mesopotamia, egypt dmp, Pistis Sophia, Tetrabiblos, Plotinus, hebrew-bible-magical)
- Scoreboard: `docs/harvest/deepen-20260911.md`
- Script: `scripts/shadow/athanor/deepen_harvest.py`
- SoT remains local: `~/.athanor/corpus/atoms.jsonl` (not in git)
