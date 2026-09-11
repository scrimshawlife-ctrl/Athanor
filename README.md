# Athanor

<p align="center">
  <img src="assets/hero.png" alt="Athanor hero — emerald furnace under golden celestial atlas" width="100%" />
</p>

**Tradition-aware corpus + encoder** for ancient magical and mystical systems.

Named for the alchemical furnace: raw tradition in, structured retrieval gold out.

[![Validate](https://github.com/scrimshawlife-ctrl/Athanor/actions/workflows/validate.yml/badge.svg)](https://github.com/scrimshawlife-ctrl/Athanor/actions/workflows/validate.yml)

| | |
|---|---|
| **Lenses** | Historical · Symbolic · Operational |
| **Honesty** | `OBSERVED` / `INFERRED` / `SPECULATIVE` / `NOT_COMPUTABLE` |
| **Shape** | Encoder + retrieval (Hyperlex-shaped). Not a chatbot that claims power. |
| **Corpus** | PD-first, **extensive** catalog — **includes Enochian as text/history** |
| **Anti** | Efficacy claims · copyright dumps · living-tradition harm · authority-seal *mint* · summon UX · sentience claims |
| **Lane** | SHADOW — retrieve live · train/Hub gated |

The Validate badge may stay red when GitHub Actions billing blocks the workflow even if local `ruff` + `pytest` pass.

## Social preview

GitHub / link-preview card: [`assets/og-social.png`](assets/og-social.png) (1200×630). Distinct from the README hero.

## Atlas

<p align="center">
  <img src="assets/atlas.png" alt="Athanor tradition atlas" width="100%" />
</p>

Navigate traditions: [`docs/atlas/map.md`](docs/atlas/map.md) · [`registry/atlas.json`](registry/atlas.json) · [`registry/families.yaml`](registry/families.yaml)

## Quick links

| Doc | Path |
|-----|------|
| Status | [`STATUS.md`](STATUS.md) |
| Constitution | [`.specify/memory/constitution.md`](.specify/memory/constitution.md) |
| Spec 000 | [`specs/000-athanor-spine/spec.md`](specs/000-athanor-spine/spec.md) |
| Spec 001 retrieve | [`specs/001-offline-retrieve/spec.md`](specs/001-offline-retrieve/spec.md) |
| Operator quickstart | [`docs/quickstart.md`](docs/quickstart.md) |
| Harvest scoreboards | [`wave0`](docs/harvest/wave0-enochian-20260911.md) · [`deepen`](docs/harvest/deepen-20260911.md) |
| Settle policy | [`docs/settle/README.md`](docs/settle/README.md) |
| Adapt (Notion + Orchestra) | [`docs/adapt-notion-orchestra.md`](docs/adapt-notion-orchestra.md) |
| Source manifest | [`docs/source-manifest.md`](docs/source-manifest.md) |
| Dual-use | [`specs/000-athanor-spine/dual-use-gate.md`](specs/000-athanor-spine/dual-use-gate.md) |
| Architecture | [`ARCHITECTURE.md`](ARCHITECTURE.md) |

## Enochian (quick)

**In** the corpus (Dee/Kelley, Calls, PD witnesses). **Out** of the product surface: authority-seal mint, “summon/compel” UX, efficacy scores.

## Install and retrieve

```bash
pip install -e ".[dev,schema]"
athanor --version
athanor doctor
athanor retrieve "Enochian Calls" --k 3
athanor retrieve "Emerald Tablet" --family hermetic --k 5
# CI / no home corpus:
ATHANOR_CORPUS=fixtures/seed/atoms.jsonl athanor retrieve "Enochian Calls" --k 2
```

Local SoT is `~/.athanor/corpus/atoms.jsonl` — **not in git**. Override with `ATHANOR_CORPUS` or `--corpus`.

`athanor retrieve` emits `athanor.packet.v0` JSON. Packet `efficacy` is always JSON `null`. Spec 001 T5 strips sacred-texts SPA chrome at retrieve time (`src/athanor/chrome.py`); stored atoms are not rewritten.

Crawl4AI **0.9.3** is the scrape default. Paid Firecrawl needs an explicit operator yes.

## Peers

Abraxas (rune identity) · Sigil-Forge (construct) · HERMENEUT (read) · Hyperlex (slang encoder sibling) · **Athanor (retrieve live · train gated)**

## License

Code: MIT. Corpus atoms carry their own licenses — see `LICENSE_POLICY.md`.
