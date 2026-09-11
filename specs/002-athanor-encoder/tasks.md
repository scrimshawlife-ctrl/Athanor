# Tasks 002 — Athanor encoder + Hub

**Workflows on every implement task:** spec-kit · access-phenomenal-gate · anti-slop-code · production-systems · google-developer-style · prism-collective · sigil-forge (boundary)

**Status:** specify P3a exit sealed locally 2026-09-11 PT. Implement / train / Hub still gated (no `ALLOW_TRAIN`, no `ALLOW_HUB`).

## Setup

- [x] U1 Review Spec 002 against constitution I–XII — **DONE** OBSERVED: Danny/Boof operator seal 2026-09-11 PT (specify-side). Live implement may still re-check before P5.
- [x] U2 Confirm provisional clarify C13–C28 — **DONE** provisional accepted for SHADOW specify; implement may flip any INFERRED row before P5.
- [x] U3 Wave 3b proposal filed (`registry/families.wave3b.proposed.yaml`). Live registry merge still HOLD.
- [x] U4 Schema `schemas/athanor_encoder_inference.v0.schema.json`
- [x] U5 Example encoder inference packet; efficacy null asserted

## Dataset

- [x] U6 Gold-settle export script that refuses KEEP-as-gold — **DONE** OBSERVED: `scripts/shadow/athanor/apply_gold_p3a.py` + batch `gold-p3a-001` → `~/.athanor/settle/gold.jsonl` (**400** OBSERVED). KEEP remains INFERRED; script refuses KEEP-as-gold.
- [x] U7 Negative corpus fixtures (news, product, slop-mysticism) — **DONE** OBSERVED: `fixtures/negatives/negatives.p3a.jsonl` (**80**) + settle copy.
- [x] U8 Dual-use wall ≥50 prompts beyond `refuse_summon.json` — **DONE** OBSERVED: `fixtures/dual_use/wall.p3a.jsonl` + `~/.athanor/settle/dual_use_wall.jsonl` (**55**; disposition `refuse_or_historical_only`, efficacy null).
- [x] U9 Balance report: family token shares on candidate train slice — **DONE** OBSERVED: `balance-report-p3a-20260911T081248Z` — E7 gold max share **~0.0674 PASS** (≤0.25).
- [x] U10 Sanitize exporter (excerpt cap, license required, no full-page dumps) — **DONE** OBSERVED: `scripts/shadow/athanor/sanitize_export.py` → excerpt-capped sanitized JSONL (`text_excerpt` ≤500; required fields per dataset-contract; no Hub upload).

## Shadow encoder

- [ ] U11 `scripts/shadow/athanor/train_encoder.py` dry-run on toy slice — HOLD (no `ALLOW_TRAIN`)
- [ ] U12 `scripts/shadow/athanor/infer_encoder.py` stub path for CI — HOLD (implement gated)
- [ ] U13 Eval harness E0–E8 writing a receipt JSON — HOLD (implement gated; E2 needs trained unbind)
- [ ] U14 String scan: no summon UX, no efficacy score, no phenomenal verbs in card/ops — HOLD (with implement)

## Hub (gated)

- [x] U15 `hf-package/README.md` card shape
- [x] U16 Profile README draft
- [x] U17 Collection layout note (`hf-package/PROFILE.md`)
- [ ] U18 ADVERSARY pass recorded before any upload — fail-closed (no `ALLOW_HUB`)
- [ ] U19 Operator yes artifact (`ALLOW_TRAIN`, `ALLOW_HUB`) — fail-closed

## Explicitly not tasks yet

Spark full train · weight commit · public upload · generative LoRA · Firecrawl · living-tradition scrape.
