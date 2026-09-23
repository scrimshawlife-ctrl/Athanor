# Architecture — Athanor (Package 4 Draft)

Status: Initial text description. Diagrams to follow in later passes. This does not govern or activate.

## High-Level Layers
```
Operator / Notion / Scripts
          |
          v
Harvest (Crawl4AI 0.9.3, PD allowlist) → atoms.jsonl (local ~/.athanor)
          |
          v
Settle / Quarantine / Gold (scripts/shadow/ + admission_approval)
          |
          v
Retrieve (Spec 001 live)
  - load_atoms
  - rank_atoms (BM25-ish stdlib)
  - strip_chrome (retrieve-time)
  - build_packet (provenance + basic 3-lens synthesis)
  - CLI (doctor, retrieve)
          |
          v
(gated) Encoder Prep (Spec 002 P3a specify)
  - adapter_* (data, freeze, overlap, tokens)
  - readiness, quarantine
          |
          v
Verification / Receipts / Audits
  - pytest, ruff, contracts/verify
  - out/audit/
```

## Components
- **Core (shipped)**: src/athanor/{retrieve,chrome,entrypoint}.py
- **Data Model**: Atom (now with source_url, content_hash, lens_hints)
- **Synthesis**: Initial HERMENEUT via _build_lens_synthesis (family + hints driven)
- **Gates**: Fail-closed for train/Hub (no ALLOW_* artifacts in repo)
- **Specs**: 000 spine, 001 retrieve, 002 encoder (specify only), 003 Qwen (separate), 004 architecture (this)

## Non-Goals (per constitution)
- Efficacy claims
- Summon/compel UX
- Full SoT or gold in git
- Production weights without operator authorization

## Next Architecture Work (Package 4)
- Detailed component diagrams (e.g. plantuml or mermaid)
- Data flow for provenance end-to-end
- Integration points for HERMENEUT full contract
- Scalability notes (current in-memory load ok for ~3k-10k atoms)

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base) + 2026-09-22 work.