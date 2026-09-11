# Plan 000 — Athanor spine

**Status**: SEALED for Spec Kit (implement still gated)  
**Spec**: `spec.md`  
**Clarify**: `clarify.md`  
**Workflows** (copied from specify — do not replace):

| Workflow | Owner |
|----------|-------|
| spec-kit | Boof / SCRIBE |
| crawl4ai-scrape | Boof / ingest ops |
| sigil-forge | HERMENEUT (boundary only) |
| access-phenomenal-gate | SHADOW |
| anti-slop-code | FORGE → cloud / build sub |
| production-systems | FORGE → cloud / build sub |
| google-developer-style | SCRIBE / cloud |
| prism-collective | Boof |

CI when implement opens: `.github/workflows/validate.yml` (pytest 3.10–3.12 + ruff; optional MkDocs). Hyperlex-shaped; no second CI philosophy.

## Architecture

```
sources (PD allowlist)
    → Crawl4AI harvest + receipt
    → normalize → atom JSONL (local SoT ~/.athanor/corpus/)
    → family registry
    → lexical index + embedding index (frozen slice)
    → retrieve → athanor.packet.v0 (efficacy: null)
    → optional T0/T1 encoder heads (Spark, operator-gated)
```

### Components

1. **Family registry** — YAML/JSON under `registry/families.yaml` listing Wave 0–3 `family_id`s from spec. Code loads; human amends.
2. **Atom store** — append-only JSONL: `atom_id`, `family_id`, `type` (`text`|`table`|`correspondence`|`diagram_desc`), `text`, `license`, `source_url`, `epistemic`, `lens_hints`, `content_hash`.
3. **Receipts** — harvest run JSON under `~/.athanor/receipts/`; never rewrite historical hashes.
4. **Ingest CLI** — `athanor ingest …` (SHADOW under `scripts/shadow/` until promote).
5. **Retrieve CLI** — `athanor retrieve "query"` → packet JSON offline.
6. **Encoder (later)** — T0 baseline encoder ≤40M; T1 structure ≤150M; names `athanor-encoder-*` only after eval. Mirror Hyperlex honesty on Spark/`ALLOW_TRAIN`.
7. **Packet schema** — `schemas/athanor_packet.v0.schema.json` (already stubbed; freeze fields in implement).

### Stack (normative for implement)

| Layer | Choice |
|-------|--------|
| Language | Python ≥ 3.10 |
| Package layout | `src/athanor/` library-first; SHADOW scripts until promote |
| Harvest | Crawl4AI (collective default) |
| Embeddings (v0) | Optional dependency; lexical BM25/stdlib rank must work offline with `ATHANOR_OFFLINE=1` |
| Train (later) | Spark; not required for Spec 000 “complete” |
| Tests | pytest; dual-use fixture wall; packet schema validation |

### Param ceilings (encoder card, when opened)

| Tier | Params | When |
|------|--------|------|
| T0 | 22–40M | after seed corpus freeze + retrieve smoke |
| T1 | 60–150M | after family/lens eval gate |
| Gen LoRA | separate artifact | only with operator yes — not “Athanor” v0 |

### Production-systems day-one (ingest/serve)

Timeouts + backoff on harvest · idempotent ingest keys · secrets not in git · health on retrieve CLI exit codes · structured logs · rollback = prior SoT snapshot · no unbounded crawl without allowlist.

### Anti-slop (when code lands)

Cyclomatic/cognitive bounds per anti-slop-code · no `any` escape hatches on trusted paths · 100% coverage on shipped slice · unknown only at untrusted parse then narrow.

## Non-goals (plan-level)

No chat UI · no Hub auto-publish · no Abraxas mint · no Sigil-Forge forge merge · no efficacy head.

## Success for this plan

Plan answers *how* without redefining *what*. Tasks below are executable without inventing new workflows.
