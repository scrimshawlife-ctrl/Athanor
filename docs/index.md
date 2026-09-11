# Athanor

<p align="center">
  <img src="../assets/hero.png" alt="Athanor hero — emerald furnace under golden celestial atlas" width="100%" />
</p>

**Tradition-aware corpus + encoder** for ancient magical and mystical systems.

Named for the alchemical furnace: raw tradition in, structured retrieval gold out.

| | |
|---|---|
| **Lenses** | Historical · Symbolic · Operational |
| **Honesty** | `OBSERVED` / `INFERRED` / `SPECULATIVE` / `NOT_COMPUTABLE` |
| **Shape** | Encoder + retrieval (Hyperlex-shaped). Not a chatbot that claims power. |
| **Corpus** | PD-first, **extensive** catalog — **includes Enochian as text/history** |
| **Anti** | Efficacy claims · copyright dumps · living-tradition harm · authority-seal *mint* · summon UX · sentience claims |
| **Lane** | SHADOW — retrieve live · train/Hub gated |

GitHub Actions Validate may stay red on account billing even when local `ruff` + `pytest` pass.

## Atlas

<p align="center">
  <img src="../assets/atlas.png" alt="Athanor tradition atlas" width="100%" />
</p>

Navigate traditions: [map](atlas/map.md) · [atlas.json](../registry/atlas.json) · [families.yaml](../registry/families.yaml)

## Operator docs

| Doc | Path |
|-----|------|
| Status | [status.md](status.md) (twin of repo-root `STATUS.md`) |
| Quickstart | [quickstart.md](quickstart.md) |
| Wave 0 harvest | [harvest/wave0-enochian-20260911.md](harvest/wave0-enochian-20260911.md) |
| Deepen harvest | [harvest/deepen-20260911.md](harvest/deepen-20260911.md) |
| Ingest A–E | [A](harvest/ingest-priority-a-20260911.md) · [B](harvest/ingest-priority-b-20260911.md) · [C](harvest/ingest-priority-c-20260911.md) · [D](harvest/ingest-priority-d-20260911.md) · [E](harvest/ingest-priority-e-20260911.md) |
| Settle KEEP / DROP / HOLD | [settle/README.md](settle/README.md) |
| P3a settle cards | [settle-pack-3000](settle/settle-pack-20260911-3000.md) · [gold](settle/gold-p3a-001-20260911.md) · [remainder](settle/p3a-remainder-20260911.md) |
| Fill3000 scoreboard | [harvest/ingest-priority-f-fill3000-20260911.md](harvest/ingest-priority-f-fill3000-20260911.md) |
| Adapt (Notion + Orchestra) | [adapt-notion-orchestra.md](adapt-notion-orchestra.md) |
| Source manifest | [source-manifest.md](source-manifest.md) |
| Architecture | [architecture.md](architecture.md) |
| Spec 000 | [../specs/000-athanor-spine/spec.md](../specs/000-athanor-spine/spec.md) |
| Spec 001 retrieve | [../specs/001-offline-retrieve/spec.md](../specs/001-offline-retrieve/spec.md) |

## Enochian (quick)

**In** the corpus (Dee/Kelley, Calls, PD witnesses). **Out** of the product surface: authority-seal mint, “summon/compel” UX, efficacy scores.

## Retrieve

See [quickstart.md](quickstart.md). Default SoT is `~/.athanor/corpus/atoms.jsonl` (not in git). Packet `efficacy` is always JSON `null`. Spec 001 T5 strips sacred-texts SPA chrome at retrieve time; stored atoms are not rewritten.

## Peers

Abraxas (rune identity) · Sigil-Forge (construct) · HERMENEUT (read) · Hyperlex (slang encoder sibling) · **Athanor (retrieve live · train gated)**
