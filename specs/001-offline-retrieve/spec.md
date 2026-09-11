# Spec 001 — Offline lexical retrieve (SHADOW)

**Feature**: Retrieve tradition atoms from local SoT into `athanor.packet.v0`  
**Date**: 2026-09-10  
**Status**: SPECIFY locked · **IMPLEMENT shipped** on main (PR #1)  
**Depends on**: constitution v1.0.0; Spec 000 spine  
**Lane**: SHADOW / advisory  

## Intent

Operators query the frozen local corpus (`~/.athanor/corpus/atoms.jsonl`) offline and receive a labeled three-lens packet with hard-null `efficacy`.

## Problem

Wave 0 harvest produced 319+ atoms with no checkable retrieve surface. Chat LLMs invent citations; Athanor must cite store atoms only.

## Goals

- G1 Stdlib-first lexical rank over atom text (BM25-ish).
- G2 Emit packets validating `schemas/athanor_packet.v0.schema.json` with `efficacy: null`.
- G3 CLI `athanor retrieve` with `--k`, `--family`, `--corpus`.
- G4 CI fixtures so tests pass without operator SoT.
- G5 No summon / efficacy product surface.

## Non-goals

- N1 Embedding backend (optional later; Spec 000 plan flag).
- N2 Generative synthesis beyond stub lens blurbs.
- N3 Train / Hub / encoder heads.
- N4 Rewriting harvest receipts.

## Workflows

Copied from Spec 000 (do not invent):

| Workflow | Owner |
|----------|-------|
| spec-kit | Boof / SCRIBE |
| crawl4ai-scrape | Boof (ingest peer; not this spec’s implement) |
| sigil-forge | HERMENEUT (boundary) |
| access-phenomenal-gate | SHADOW |
| anti-slop-code | PROMETHEUS → build |
| production-systems | PROMETHEUS → build |
| google-developer-style | SCRIBE / build |
| prism-collective | Boof |

**CI:** `.github/workflows/validate.yml` (already live).

## Users

- Operator querying local SoT
- HERMENEUT consuming packets for lens QA

## In scope

- `src/athanor/retrieve.py` + CLI wiring
- Fixture atoms under `fixtures/seed/`
- Quickstart docs

## Out of scope

- Corpus harvest (Spec 000 / ops)
- Encoder train

## Success (OBSERVED)

- [x] PR #1 merged — retrieve on main
- [x] `pytest` includes retrieve tests; efficacy null asserted
- [x] Manual retrieve against Wave 0 SoT returns family hits
- [x] T5 retrieve-time chrome strip (excerpts only; SoT unchanged)

## Risks

| Risk | Mitigation |
|------|------------|
| Nav chrome in sacred-texts SPA pollutes excerpts | T5: `strip_chrome` at excerpt time in `retrieve.py`. Corpus re-harvest optional later. |
| Empty corpus | Clear error / empty hits; CI uses fixtures |
