# Athanor

<p align="center">
  <img src="assets/hero.png" alt="Athanor hero — emerald furnace under golden celestial atlas" width="100%" />
</p>

**Tradition-aware corpus + encoder** for ancient magical and mystical systems.

Specification completion: start at [docs/START_HERE.md](docs/START_HERE.md). Packages 1-3 are an advisory target, not runtime changes. Corpus/GOLD/E7 values below are historical operator-machine reports; independent validity is NOT_COMPUTABLE without their underlying evidence. Committed P3a fixtures are 63 pairs, 80 negatives and 55 wall prompts; fixture availability does not prove wall behavior. See [current eval evidence scope](specs/002-athanor-encoder/eval-gates.md).

Named for the alchemical furnace: raw tradition in, structured retrieval gold out.
Hyperlex-shaped sibling — **encoder + retrieval**, not a chatbot that claims power.

[![Validate](https://github.com/scrimshawlife-ctrl/Athanor/actions/workflows/validate.yml/badge.svg)](https://github.com/scrimshawlife-ctrl/Athanor/actions/workflows/validate.yml)

| | |
|---|---|
| **Owns** | tradition families · PD harvest · offline lexical retrieve · Spec 002 encoder specify |
| **Lenses** | Historical · Symbolic · Operational |
| **Honesty** | `OBSERVED` / `INFERRED` / `SPECULATIVE` / `NOT_COMPUTABLE` |
| **Shape** | Spec 001 retrieve **live**. Spec 002 encoder/Hub **gated**. Not a summon UX. |
| **Corpus** | PD-first, extensive catalog — **includes Enochian as text/history** |
| **Anti** | Efficacy claims · copyright dumps · living-tradition harm · authority-seal *mint* · summon UX · sentience / phenomenal claims |
| **Lane** | SHADOW — retrieve live · train/Hub gated |
| **Version** | see [`VERSION`](VERSION) (`0.1.0a0`) |

The Validate badge may stay red when GitHub Actions billing blocks the workflow even if local `ruff` + `pytest` pass. Local tests are the bar.

## What ships / what does not

| Ships now | Does **not** ship |
|-----------|-------------------|
| Offline lexical `athanor retrieve` → `athanor.packet.v0` | Trained encoder weights / Hub upload |
| Spec 001 T5 chrome strip at retrieve time | Efficacy scores (packet `efficacy` is always JSON `null`) |
| Spec 002 P3a **specify** exit (gold/fixtures sealed) | `ALLOW_TRAIN` / `ALLOW_HUB` artifacts |
| Dual-use wall fixtures (≥55 prompts) | Summon / compel product surface |
| Atlas + family registry | Full SoT / gold JSONL in git |

## Current state (OBSERVED 2026-09-23 PT)

Snapshot for operators. Full receipts live in [`STATUS.md`](STATUS.md).

|| Area | State |
|------|-------|
|| Spec Kit spine (000) | Sealed |
|| Spec 001 retrieve | Live on main · T5 chrome strip landed |
|| Spec 002 encoder | **P3a specify exit sealed** · implement/train still gated |
|| Local SoT | `~/.athanor/corpus/atoms.jsonl` — **3184** atoms (jev-classified PD, min 5, 15 families at 5) |
|| Quality | All classifying via jev rerank; `docs/dataset-card.md` (7.8/10 best-practices); gold fixtures 70 pairs / 84 negatives |
|| P3a remainder | **70** correspondence pairs · **84** negatives · **55** dual-use |
|| Package 4 | Core complete (24 ACs, full traceability, jev settle/quarantine/doctor) |
| Harvest | Wave 0–1 + A–E + F fill3000 · Crawl4AI **0.9.3** |
| Hub / train | **Blocked** · Aaron pack local-only |
| Wave 3b / Enochian flood | Ask-first HOLD |

## Social preview

GitHub / link-preview card: [`assets/og-social.png`](assets/og-social.png) (and `.jpg` for Settings paste). Distinct from the README hero.
Settings → Social preview is manual (no API/MCP write).

## Atlas

<p align="center">
  <img src="assets/atlas.png" alt="Athanor tradition atlas" width="100%" />
</p>

Navigate traditions: [`docs/atlas/map.md`](docs/atlas/map.md) · [`registry/atlas.json`](registry/atlas.json) · [`registry/families.yaml`](registry/families.yaml)

## Pipeline

```
PD allowlist → Crawl4AI 0.9.3 → atom JSONL (~/.athanor/corpus/)
                              → receipts + harvest scoreboards
                              → lexical retrieve (+ optional embed later)
                              → athanor.packet.v0 (efficacy: null)
                              → optional encoder T0/T1 (Spark, gated)
```

Normative plan: [`ARCHITECTURE.md`](ARCHITECTURE.md) · [`specs/000-athanor-spine/plan.md`](specs/000-athanor-spine/plan.md).
No hard import of Abraxas or Hyperlex runtimes.

## Specs

| Spec | Role | Path |
|------|------|------|
| 000 spine | Constitution / plan / dual-use | [`specs/000-athanor-spine/`](specs/000-athanor-spine/) |
| 001 retrieve | Offline lexical retrieve + T5 chrome | [`specs/001-offline-retrieve/`](specs/001-offline-retrieve/) |
| 002 encoder | Dataset · gold · Hub card · P3a exit | [`specs/002-athanor-encoder/`](specs/002-athanor-encoder/) · [`p3a-exit.md`](specs/002-athanor-encoder/p3a-exit.md) |

## Quick links

| Doc | Path |
|-----|------|
| Status | [`STATUS.md`](STATUS.md) |
| Operator quickstart | [`docs/quickstart.md`](docs/quickstart.md) |
| Constitution | [`.specify/memory/constitution.md`](.specify/memory/constitution.md) |
| Source manifest | [`docs/source-manifest.md`](docs/source-manifest.md) |
| Harvest scoreboards | [`wave0`](docs/harvest/wave0-enochian-20260911.md) · [`deepen`](docs/harvest/deepen-20260911.md) · [`A`](docs/harvest/ingest-priority-a-20260911.md)–[`F`](docs/harvest/ingest-priority-f-fill3000-20260911.md) |
| Settle policy | [`docs/settle/README.md`](docs/settle/README.md) · [`gold-p3a`](docs/settle/gold-p3a-001-20260911.md) · [`p3a-remainder`](docs/settle/p3a-remainder-20260911.md) |
| Adapt (Notion + Orchestra) | [`docs/adapt-notion-orchestra.md`](docs/adapt-notion-orchestra.md) |
| Dual-use gate | [`specs/000-athanor-spine/dual-use-gate.md`](specs/000-athanor-spine/dual-use-gate.md) |
| Architecture | [`ARCHITECTURE.md`](ARCHITECTURE.md) |
| Agents | [`AGENTS.md`](AGENTS.md) |
| License policy | [`LICENSE_POLICY.md`](LICENSE_POLICY.md) |
| Docs index | [`docs/index.md`](docs/index.md) |

## Install and retrieve

```bash
pip install -e ".[dev,schema]"
athanor --version
athanor doctor
athanor retrieve "Enochian Calls" --k 3
athanor retrieve "Emerald Tablet" --family hermetic --k 5
# CI / no home corpus:
ATHANOR_CORPUS=fixtures/seed/atoms.jsonl athanor retrieve "Enochian Calls" --k 2
pytest -q
```

Local SoT is `~/.athanor/corpus/atoms.jsonl` — **not in git**. Override with `ATHANOR_CORPUS` or `--corpus`.

`athanor retrieve` emits `athanor.packet.v0` JSON. Packet `efficacy` is always JSON `null`. Synthesis lenses are stubbed `INFERRED` until HERMENEUT wiring.

Spec 001 T5 strips sacred-texts SPA chrome at retrieve time (`src/athanor/chrome.py`). Stored atoms are **not** rewritten by retrieve.

Crawl4AI **0.9.3** is the scrape default. Paid Firecrawl needs an explicit operator yes.

## Corpus, settle, and fixtures

| Layer | Where | In git? |
|-------|-------|---------|
| Local SoT | `~/.athanor/corpus/atoms.jsonl` | **No** |
| Gold / KEEP / quarantine | `~/.athanor/settle/` · `~/.athanor/quarantine/` | **No** |
| Seed fixtures (CI smoke) | `fixtures/seed/` | Yes |
| P3a correspondence / negatives / dual-use | `fixtures/correspondence/` · `fixtures/negatives/` · `fixtures/dual_use/` | Yes (counts only; no full SoT) |
| Sanitize export | `scripts/shadow/athanor/sanitize_export.py` | Yes — excerpt ≤500; no Hub |

Settle rules (short): heuristic KEEP stays **INFERRED** until gold settle; chrome/stub DROP may be quarantined locally; modern sacred-texts Rowe/Achadian `/book/` essays **HOLD** without an operator license call. Details: [`docs/settle/README.md`](docs/settle/README.md).

## Spec 002 encoder (gated)

P3a **specify** exit is sealed — see [`specs/002-athanor-encoder/p3a-exit.md`](specs/002-athanor-encoder/p3a-exit.md).

| Gate | State |
|------|-------|
| E0 lexical retrieve / packet smoke | **PASS** |
| E2 correspondence unbind | **FAIL** until train eval harness |
| E7 gold family balance | **PASS** (max share ~0.067 ≤ 0.25) |
| U11–U14 implement / train scripts | Unchecked — no `ALLOW_TRAIN` |
| U18–U19 Hub / train artifacts | Unchecked — no `ALLOW_HUB` |
| Hugging Face upload | Forbidden without `ALLOW_HUB` |

Aaron offline pack (when built) stays under `/workspace/athanor-harvest/` on the operator machine — **not** Hub-published from this repo.

## Repo map

```
assets/          hero, atlas, OG social
src/athanor/     retrieve, chrome, CLI entry
fixtures/        seed + P3a eval slices (not full SoT)
scripts/shadow/athanor/   harvest / settle / sanitize helpers
specs/           Spec Kit 000–002
registry/        atlas + families
docs/            quickstart, harvest, settle, atlas
~/.athanor/      local SoT, receipts, settle (machine-local)
```

## Enochian (quick)

**In** the corpus (Dee/Kelley, Calls, PD witnesses). **Out** of the product surface: authority-seal mint, “summon/compel” UX, efficacy scores.
Enochian gold batches stay capped; flood harvests are ask-first.

## Fail-closed gates

Do **not** without an explicit Danny/operator yes:

- Commit `atoms.jsonl`, gold dumps, or quarantine into git
- Set `ALLOW_TRAIN` / `ALLOW_HUB` or publish to Hugging Face
- Paid Firecrawl cloud (Crawl4AI is default)
- Wave 3b live registry merge / Enochian flood
- Efficacy, summon, or phenomenal product claims

## Peers

Abraxas (rune identity) · Sigil-Forge (construct) · HERMENEUT (read) · Hyperlex (slang encoder sibling) · Semion (sign triad) · Yggdrasil (route classifier) · **Athanor (tradition retrieve live · train gated)**

## Agents

Boof (PRISM) orchestrates. FORGE / PROMETHEUS plan. HERMENEUT lens QA. SCRIBE files artifacts. SHADOW honesty. ADVERSARY dual-use before Hub.
Do not spawn a fifth growth bot or a new mystical specialist — route to existing seats. See [`AGENTS.md`](AGENTS.md).

## License

Code: MIT. Corpus atoms carry their own licenses — see [`LICENSE_POLICY.md`](LICENSE_POLICY.md).

This does not govern or activate.

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base)
