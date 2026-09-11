# Spec 002 — Athanor encoder + Hub card (SHADOW)

**Feature**: Tradition-aware encoder over the Athanor corpus, plus the first legal Hugging Face surface  
**Date**: 2026-09-10  
**Status**: SHADOW specify on main — not implement, not train, not Hub  
**Depends on**: constitution v1.0.0 I–XII; Spec 000 C1–C12; Spec 001 retrieve; Hyperlex Spec 007 as sibling pattern only  

Longform notes in this directory are normative with this index. Constitution I–XII wins on conflict.

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

## Next operator moves

1. Flip or confirm C13–C22 INFERRED rows.
2. Gold-settle a capped Enochian slice plus thin families.
3. Wave 3 deepen before Wave 3b harvest.
4. Do not upload.
