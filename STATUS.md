# Athanor STATUS

**Lane:** SHADOW — retrieve live · train/Hub gated  
**Version:** see `VERSION`  
**Remote:** https://github.com/scrimshawlife-ctrl/Athanor  

| Area | State |
|------|-------|
| Spec Kit spine (000) | Sealed |
| Spec 001 retrieve | Live on main (PR #1) · T5 chrome strip (PR #2 / `83c3ef2`) |
| Hero + atlas art | Shipped under `assets/` |
| Package | `athanor` CLI `doctor` / `retrieve` / `--version` |
| CI | `.github/workflows/validate.yml` — local ruff+pytest is the bar; Actions may fail on account billing |
| Harvest | Wave 0–1 + ATHANOR-INGEST A–E on local SoT · Crawl4AI 0.9.3 |
| Local SoT | `~/.athanor/corpus/atoms.jsonl` — **2374** after A–E (not in git) |
| Hub / train | Blocked |

## Wave 0 harvest (OBSERVED 2026-09-10 PT)

- SoT: `~/.athanor/corpus/atoms.jsonl` (not in git)
- Receipt: `~/.athanor/receipts/wave0-enochian-20260911T044756Z-95149c51.json`
- Scoreboard copy: [`docs/harvest/wave0-enochian-20260911.md`](docs/harvest/wave0-enochian-20260911.md)
- Engine: crawl4ai 0.9.3 · pages_ok 37 · failures 2 (I Ching classic paths 404; recovered via `/book/the-i-ching`)
- Epistemic: harvest atoms **INFERRED** until operator gold settle

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

## Notion + Orchestra adapt (OBSERVED 2026-09-10 PT)

- Source: Historical Proto-Systems Integration Layer + Hermes Orchestra references
- Receipt: `adapt-notion-orchestra-20260911T050713Z`
- **+68** atoms → corpus total **387** (local SoT)
- Doc: [`docs/adapt-notion-orchestra.md`](docs/adapt-notion-orchestra.md)

## Deepen + Wave 1 harvest (OBSERVED 2026-09-10 PT)

- Receipt: `deepen-20260911T051038Z-14f21ac2`
- Net **+840** atoms → corpus total **1227** (0 failures, 162 dupe skips)
- Casaubon IA deepen + 15 sacred-texts Enochian `/book/` + Wave 1 (mesopotamia, egypt dmp, Pistis Sophia, Tetrabiblos, Plotinus, hebrew-bible-magical)
- Scoreboard: [`docs/harvest/deepen-20260911.md`](docs/harvest/deepen-20260911.md)
- Script: `scripts/shadow/athanor/deepen_harvest.py`
- SoT remains local: `~/.athanor/corpus/atoms.jsonl` (not in git)
- No Firecrawl

## Settle DROP (OBSERVED operator machine)

- After deepen, local SoT was **1227**. After settle DROP, **1178** remain (**49** quarantined locally).
- JSONL and quarantine files are **not in git**. Family-level post-settle counts are not published here.
- Heuristic KEEP stays **INFERRED** until an explicit gold settle. KEEP is not OBSERVED gold.
- Modern sacred-texts `/book/` Rowe/Achadian essays: **HOLD** — not PD gold without an operator license call.
- Policy: [`docs/settle/README.md`](docs/settle/README.md)

## ATHANOR-INGEST Priorities A–E (OBSERVED 2026-09-11 PT)

Local SoT after settle DROP (**1178**) then A→E harvests. Atoms stay under `~/.athanor` — **not in git**. Crawl4AI **0.9.3**. No paid Firecrawl. Heuristic KEEP remains **INFERRED** (not gold). Wave **3b** families are proposal-only (not harvested). Train / Hub still gated.

| Priority | Net +atoms | Corpus after | Scripts |
|----------|-----------:|-------------:|---------|
| A thin families | +385 | 1563 | `scripts/shadow/athanor/ingest_priority_a.py` |
| B tables / correspondence | +113 | 1676 | `ingest_priority_b.py` (+ `_continue`) |
| C `islamic_occult_pd` | +88 | 1764 | `ingest_priority_c.py` |
| D Wave 2 PD | +395 | 2159 | `ingest_priority_d.py` (+ `_continue`) |
| E Wave 3 reception | +215 | **2374** | `ingest_priority_e.py` |
| **A–E total** | **+1196** | **2374** | |

Scoreboards (repo copies; receipts stay local under `~/.athanor/receipts/`):

- [`docs/harvest/ingest-priority-a-20260911.md`](docs/harvest/ingest-priority-a-20260911.md)
- [`docs/harvest/ingest-priority-b-20260911.md`](docs/harvest/ingest-priority-b-20260911.md)
- [`docs/harvest/ingest-priority-c-20260911.md`](docs/harvest/ingest-priority-c-20260911.md)
- [`docs/harvest/ingest-priority-d-20260911.md`](docs/harvest/ingest-priority-d-20260911.md)
- [`docs/harvest/ingest-priority-e-20260911.md`](docs/harvest/ingest-priority-e-20260911.md)

### Family counts (local SoT, OBSERVED 2026-09-11 PT)

| family_id | n |
|-----------|--:|
| enochian | 513 |
| mesopotamia | 146 |
| iching_daoist | 104 |
| egypt_magical | 97 |
| kabbalah_pd | 95 |
| astrology_west | 95 |
| hermetic | 90 |
| islamic_occult_pd | 88 |
| tantra_hist_pd | 78 |
| coptic_gnostic | 76 |
| runes_eddic | 71 |
| tarot_history | 70 |
| veda_upanishad_pd | 70 |
| alchemy_spirit | 69 |
| mesoamerica | 67 |
| golden_dawn_hist | 65 |
| theosophy_pd | 65 |
| folk_magic_pd | 65 |
| solomonic | 60 |
| buddhism_esoteric_pd | 59 |
| grimoire_other | 55 |
| mystery_cults | 55 |
| hebrew_bible_magical | 53 |
| jyotish_anchors | 50 |
| alchemy_lab | 34 |
| goetia_catalog | 29 |
| neoplatonism | 28 |
| chaos_spare_hist | 27 |
| **total** | **2374** |

**HOLD:** modern Picatrix English; modern sacred-texts `/book/` Rowe/Achadian essays (license call). **STOP** before Wave 3b / Enochian flood unless operator asks.

## Spec 001 T5 excerpt chrome (retrieve-time)

- Sacred-texts SPA nav (`[Categories]`, Toggle Sidebar, USB shop, breadcrumbs) is stripped **when building retrieve excerpts**, not by rewriting `~/.athanor` SoT.
- Helper: `athanor.chrome.strip_chrome` (stdlib; reusable by a later harvest pass).
- Landed as PR #2 / `83c3ef2`. Corpus re-harvest remains optional if operators want clean stored `text`.
- Packet `efficacy` stays JSON `null`. Train / Hub still gated.
