# Spec 002 — Athanor encoder + Hub card (SHADOW)

**Feature**: Tradition-aware encoder over the Athanor corpus, plus the first legal Hugging Face surface  
**Date**: 2026-09-10  
**Status**: Historical P3a local specify seal reported; canonical-method packages 1-3 are advisory. Encoder implementation, train and Hub remain gated.
**Depends on**: constitution v1.0.0 I–XII; Spec 000 C1–C12; Spec 001 retrieve; Hyperlex Spec 007 as sibling pattern only  

Longform notes in this directory share the precedence and evidence qualifications in [specs/README.md](../README.md). Constitution I–XII wins on conflict. Proposed v1 contracts are targets, not changes to shipped schemas.

## Workflows

[WF-004 through WF-010 and WF-012](workflows.md) define dataset, encoder, release and handoff behavior. Read [requirements](requirements.md) and [journeys](../journeys.md) first, then [state machines](../state-machines.md), [contracts](../contracts/README.md) and data-model.md before architecture.

## Intent

Athanor already harvests and retrieves. Spec 002 defines the learned furnace: a small encoder that binds family, lens, reception layer, and correspondence structure. v0 Hub name means encoder + sanitized dataset. A generative LoRA is a later gated artifact with a different card name.

## Product shape

| Tier | Name allowed | Gate |
|------|--------------|------|
| T0 MiniLM-class encoder + linear heads | `athanor-encoder-*` | E0 E4 E5 E8 |
| T1 ModernBERT-base-class + unbind | `athanor-structure-*` | T0 + E1 E2 E7 |
| T2 decoder LoRA | `athanor-read-*-lora` | operator generate yes |
| Chat 7B | never under Athanor | constitution XI |

Heads: family, wave, atom_type, lens_route, reception_layer, correspondence unbind.  
Forbidden heads: efficacy, manifestation, spirit-present, refusal-on-PD-text, phenomenal.

Packet: `athanor.encoder.inference.v0` optional block on retrieve packets. `efficacy` JSON null. No chat template.

## Contemporary

Wave 3 deepen first (`golden_dawn_hist`, `theosophy_pd`, `chaos_spare_hist`, `folk_magic_pd`).  
Wave 3b is proposal-only: `registry/families.wave3b.proposed.yaml`.  
Reception layer required. Living-lineage internals out. Post-1928 HOLD default.

## Name collision

Do not use `Athanor-DPO` or `Atanor-4B`. Those Hub slugs are unrelated projects.

## Sibling files (normative)

| File | Owns |
|------|------|
| `clarify.md` | C13–C28 |
| `plan.md` | phases P3a–P6 |
| `tasks.md` | U1–U19 |
| `dataset-contract.md` | gold/weak/neg/wall/sanitize |
| `gold-settle.md` | KEEP ≠ gold |
| `eval-gates.md` | E0–E8 |
| `dual-use-addendum.md` | encoder/Hub wall |
| `contemporary-wave.md` | Wave 3 / 3b fences |
| `data-model.md` | trainrow views |
| `hardware.md` | Spark honesty |
| `ingest-design.md` | harvest → settle → train |
| `hf-package/README.md` | card shape |
| `hf-package/PROFILE.md` | Hub profile copy |
| `checklist.md` | specify completeness |

## Historical next operator moves (original specify snapshot)

1. Flip or confirm C13–C22 INFERRED rows.
2. Gold-settle a capped Enochian slice plus thin families.
3. Wave 3 deepen before Wave 3b harvest.
4. Do not upload.

Current completion work follows the [specification map](../README.md). The historical 400 GOLD and E7 claims require the qualifications in p3a-exit.md; their independent validity is NOT_COMPUTABLE here. This does not govern or activate.

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base)
