# Plan 000 — Athanor spine (DRAFT)

**Status:** DRAFT — FORGE to harden  
**Spec:** `spec.md`  
**Stack stays here; what/why stays in spec.**

## Architecture (proposed)

1. **Local SoT** — `~/.athanor/corpus/` JSONL atoms + receipts (not full dumps in git; Hyperlex park pattern).
2. **Ingest** — Crawl4AI allowlisted sources → normalize → license tag → receipt → candidate store.
3. **Registry** — `family_id` + atom types (`text`, `table`, `correspondence`, `diagram_desc`).
4. **Index** — lexical + embedding index over frozen slice; offline retrieve.
5. **Encoder (T0/T1)** — small base encoder + tradition/family heads; Spark train path mirrored from Hyperlex lessons; name `athanor-encoder-*` only after eval gate.
6. **Packet** — `athanor.packet.v0` with hard-null `efficacy`.

## Non-stack constraints (from spec Workflows)

anti-slop-code · production-systems · google-developer-style · crawl4ai-scrape · access-phenomenal-gate · spec-kit · prism-collective · sigil-forge boundary

## Phases (task seeds)

- P0 Manifest: fill Wave 0 URLs + licenses OBSERVED
- P1 Ingest tap + receipts
- P2 Offline retrieve on seed slice
- P3 Encoder shadow scripts
- P4 Eval gates + ADVERSARY dual-use
- P5 Operator train yes (Spark)

## Open for FORGE

- Exact embedding backend (stdlib-first vs optional)
- Param ceilings (mirror Hyperlex T0/T1?)
- CI workflow filename confirm
