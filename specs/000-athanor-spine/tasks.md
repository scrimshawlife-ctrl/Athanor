# Tasks 000 — Athanor spine

**Workflows on every implement task:** anti-slop-code · production-systems · google-developer-style · crawl4ai-scrape · access-phenomenal-gate · spec-kit · prism-collective  

**Status:** Spec Kit complete when Setup + Foundational docs tasks are done in-repo; code phases wait for operator implement yes.

## Setup

- [x] T1 Create private repo `scrimshawlife-ctrl/Athanor`
- [x] T2 Constitution v1.0.0
- [x] T3 Spec 000 + Workflows section
- [x] T4 Clarify locks C1–C12
- [x] T5 Plan sealed
- [x] T6 Checklist pass (this seal)
- [x] T7 Wave 0 rows in `docs/source-manifest.md` with OBSERVED URLs (min 8)

## Foundational (docs / schema — no train)

- [x] T8 Freeze `schemas/athanor_packet.v0.schema.json` fields + examples
- [x] T9 Add `schemas/athanor_atom.v0.schema.json`
- [x] T10 Add `registry/families.yaml` for Wave 0–3 ids from spec
- [x] T11 Dual-use gate doc (`dual-use-gate.md`)
- [x] T12 Data model doc (`data-model.md`)
- [x] T13 README operator quickstart (offline retrieve stub described; no fake CLI yet)

## User story A — Manifest & harvest ready

- [x] T14 Allowlist file `config/source_allowlist.yaml` from manifest
- [ ] T15 Receipt schema + example harvest receipt
- [ ] T16 Ingest design note: Crawl4AI → atom JSONL (implement later)

## User story B — Offline retrieve

- [ ] T17 Lexical retrieve design on frozen seed fixtures (`fixtures/seed/`)
- [ ] T18 Packet golden fixtures (efficacy null asserted)
- [x] T19 Dual-use negative fixtures (summon/efficacy language must refuse or strip)

## User story C — Encoder shadow (gated)

- [ ] T20 Shadow dir sketch `scripts/shadow/athanor/` (docs only until implement yes)
- [ ] T21 Eval gates doc: family accuracy, lens coverage, dual-use wall, no-efficacy
- [ ] T22 Spark / `ALLOW_TRAIN` honesty note (fail-closed like Hyperlex E2)

## Polish

- [ ] T23 ADVERSARY dual-use review before any Hub card (not before Spec seal)
- [ ] T24 Optional Notion Operator Hub page
- [ ] T25 Converge pass after first implement PR

## Explicitly not tasks yet

Implement ingest code · train · Hub upload · generative LoRA · paid Firecrawl.
