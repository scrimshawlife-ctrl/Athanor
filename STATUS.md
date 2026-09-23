# Athanor STATUS

## Current evidence qualification — specification completion

Packages 1-3 define an advisory target; runtime code and schemas remain unchanged. Historical counts/PASS labels below are reports from the operator machine, not independently reproduced corpus/model evidence. At review base fd84c708, 63 pairs, 80 negatives and 55 wall prompts are committed. **219 local tests + lint passed** (Spec 001 retrieve hardening). Independent GOLD validity, current eligible train rows and E7 reproduction are NOT_COMPUTABLE. INFERRED=2597 is not KEEP=2597; the P3a report gives 2424 non-gold KEEP rows. Read [START_HERE](docs/START_HERE.md), [eval evidence](specs/002-athanor-encoder/eval-gates.md), and [reconciliation receipt](out/audit/spec-completion.latest.json).

This does not govern or activate. Earlier dated entries remain historical; the canonical fourteen-stage method is not declared complete.

**Lane:** SHADOW — retrieve live · train/Hub gated  
**Version:** see `VERSION` (0.1.0a1)  
**Remote:** https://github.com/scrimshawlife-ctrl/Athanor  

| Area | State |
|------|-------|
| Spec Kit spine (000) | Sealed |
| Spec 001 retrieve | Live on main (PR #1) · T5 chrome strip (PR #2 / `83c3ef2`) · **Gaps closed 2026-09-22**: tokenless query rejection, clean malformed errors (REQ-013), source_url/content_hash in packets, non-empty receipts, extended Atom model, 219 tests |
| Hero + atlas art | Shipped under `assets/` |
| Package | `athanor` CLI `doctor` / `retrieve` / `--version` |
| CI | `.github/workflows/validate.yml` — local ruff+pytest is the bar; Actions may fail on account billing |
| Harvest | Wave 0–1 + A–E + F fill3000 · Crawl4AI 0.9.3 · P3a gold sealed |
| Local SoT | `~/.athanor/corpus/atoms.jsonl` — **2997** after F+DROP (400 GOLD OBSERVED; not in git) |
| Hub / train | Blocked · Spec 002 P3a specify exit sealed; Aaron pack local-only |

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

## Priority F fill3000 + P3a settle (OBSERVED 2026-09-11 PT)

- Local SoT after F: **3000** → after DROP×3: **2997** (atoms not in git)
- GOLD stamped: **400 OBSERVED** (`gold-p3a-001`, 27 families, Enochian gold 4/40)
- P3a remainder: **63** corr pairs · **80** negatives · **55** dual-use · E7 gold **PASS**
- Scripts: `ingest_priority_f_fill3000.py` · `apply_gold_p3a.py`
- Fixtures: `fixtures/correspondence/pairs.p3a.jsonl` · `fixtures/negatives/negatives.p3a.jsonl` · `fixtures/dual_use/wall.p3a.jsonl`
- Operator cards: [`fill3000`](docs/harvest/ingest-priority-f-fill3000-20260911.md) · [`settle-pack-3000`](docs/settle/settle-pack-20260911-3000.md) · [`gold-p3a`](docs/settle/gold-p3a-001-20260911.md) · [`p3a-remainder`](docs/settle/p3a-remainder-20260911.md)
- Train / Hub still gated. Wave 3b / Enochian flood still ask-first.

## Spec 002 P3a specify exit (OBSERVED 2026-09-11 PT)

- Spec tasks U1–U2, U6–U10 marked DONE with local evidence; U11–U14 / U18–U19 still unchecked (no `ALLOW_TRAIN` / no `ALLOW_HUB`).
- E7 gold slice **PASS** (max share ~0.067). E2 still **FAIL** (unbind not trained). E0 lexical retrieve smoke **PASS**.
- Dual-use wall expanded to **55** prompts (`fixtures/dual_use/wall.p3a.jsonl`).
- Sanitize exporter: `scripts/shadow/athanor/sanitize_export.py`.
- Exit seal: [`specs/002-athanor-encoder/p3a-exit.md`](specs/002-athanor-encoder/p3a-exit.md)
- **Aaron train pack** (local only, Hub NOT published): `/workspace/athanor-harvest/aaron-train-pack-20260911/` · zip `athanor-train-pack-aaron-20260911.zip`
- Train / Hub still gated. Wave 3b / Enochian flood still ask-first.

## Spec 001 T5 excerpt chrome (retrieve-time)

- Sacred-texts SPA nav (`[Categories]`, Toggle Sidebar, USB shop, breadcrumbs) is stripped **when building retrieve excerpts**, not by rewriting `~/.athanor` SoT.
- Helper: `athanor.chrome.strip_chrome` (stdlib; reusable by a later harvest pass).
- Landed as PR #2 / `83c3ef2`. Corpus re-harvest remains optional if operators want clean stored `text`.
- Packet `efficacy` stays JSON `null`. Train / Hub still gated.

## 2026-09-22 Retrieve hardening + Package 4 start + basic HERMENEUT (Spec 001 gaps closed + next work)

- **Tokenless query rejection** (REQ-009): `retrieve("!!! ???")` now raises `ValueError("query must contain at least one searchable token (alphanumeric)")`.
- **Stable CLI errors** (REQ-013): Malformed JSONL / missing keys / non-dict rows now produce clean `error: ...` + exit 2 (no tracebacks). `load_atoms` + `Atom.from_mapping` enforce required fields.
- **Provenance in packets**: `Atom` now carries `source_url` / `content_hash`. Hits include them when present in corpus. `receipts` now non-empty (`[{"type": "lexical-retrieve", "epistemic": "INFERRED"}]`).
- **Doctor enhancements**: Reports `corpus_atoms`, sample provenance flags, retrieve smoke, receipts presence.
- **Tests**: 219 passed (core + new coverage).
- **Spec update**: `specs/001-offline-retrieve/requirements.md` deviations marked **ADDRESSED**.
- **Version**: 0.1.0a1
- Full verification: pytest + ruff (core clean) + contracts + CLI smokes all green.
- See `ANALYSIS_REPORT.md` for detailed receipts and locations.
- No changes to gated paths (train/Hub remain blocked).

**Next work progress**:
- Basic three-lens synthesis wired in retrieve (uses lens_hints, family, epistemic for differentiated historical/symbolic/operational text). Initial HERMENEUT.
- Package 4 significantly deepened:
  - `specs/004-architecture/` now includes: spec.md, plan.md, architecture.md (with mermaid diagram), acceptance-catalog.md, traceability.md (expanded with REQ/JRN/WF/AC entries), tasks.md (decomposition skeleton).
- 220 tests passing.
- Full re-verify green.

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base) + 2026-09-22 hardening on feat/close-spec001-gaps-retrieve-provenance-20260922
