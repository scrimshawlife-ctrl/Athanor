# Clarify 002 — Athanor encoder + Hub

**Date**: 2026-09-10 PT  
**Status**: PROVISIONAL LOCK for specify seal. Operator may flip any INFERRED row before P5.  
**Depends on**: Spec 000 C1–C12 (not re-opened)

| # | Question | Decision | Epistemic |
|---|----------|----------|-----------|
| C13 | Hub namespace v0 | Personal `scrimshawlife-ctrl`. AAL org later when the org is OBSERVED. Collection name `athanor`. | INFERRED (Hyperlex twin) |
| C14 | Reserved Hub slugs | `athanor-encoder-*`, `athanor-structure-*`, `athanor-atoms-sanitize-*`, `athanor-read-*-lora`. Never `Athanor-DPO` or `Atanor-4B`. | OBSERVED collisions + INFERRED reserve |
| C15 | Wave 3b families | Specified as **proposal** in `registry/families.wave3b.proposed.yaml`. Not merged into live `registry/families.yaml` until operator yes (constitution VIII). Harvest HOLD until merge. | LOCKED process / SPECULATIVE ids |
| C16 | Contemporary default | Post-1928 copyright HOLD unless operator license call. Living-lineage internals out. Reception layer tag required. | LOCKED (C12 parallel) |
| C17 | T0 trunk | MiniLM-class or ≤40M public encoder. Cheapest offline path. | INFERRED |
| C18 | T1 trunk | ModernBERT-base class (~149M), Hyperlex 007 twin. Name `athanor-structure-*` only after E2+E7. | INFERRED |
| C19 | T2 generate | Out of v0 implement. Separate card name if ever opened. | LOCKED (000 C2) |
| C20 | Sanitize Enochian | Public dataset may hold **excerpts** ≤ 500 characters per atom plus license + hash + URL. No full Call, no full Casaubon page. | INFERRED pending operator flip |
| C21 | Seal images | Still `diagram_desc` only (000 C7). No binary seals on Hub. | LOCKED |
| C22 | Train home | T1 on DGX Spark. T0 dry-run may use local GPU. Spark blocked → HOLD, no fake green. | INFERRED (000 C5) |
| C23 | Gold vs KEEP | KEEP harvest remains INFERRED. Gold requires explicit operator settle export. | LOCKED (settle policy) |
| C24 | Family cap | Train token share per `family_id` ≤ 0.25. E7 name-gate. | LOCKED |
| C25 | Efficacy head | Forbidden. Packet and card `efficacy` JSON null. | LOCKED (000 C11) |
| C26 | Chat template | Forbidden on infer. No assistant string. | LOCKED |
| C27 | Upload | `ALLOW_HUB` file or explicit operator yes. Not CI. | LOCKED (VIII) |
| C28 | Spec 000 task drift | T17–T18 treated OBSERVED-done via Spec 001 ship. Encoder work lives in 002, not as silent 000 reopen. | OBSERVED |

Open (do not invent): AAL org slug spelling; exact MiniLM checkpoint id; whether T0 is skipped if Spark is free this cycle.
