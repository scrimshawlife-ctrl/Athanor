# Plan 002 — Athanor encoder + Hub

**Status:** Historical architecture draft; P3a local seal reported. Behavioral completion package is advisory; architecture closure belongs to package 4.
**Lane:** SHADOW · **No train / no Hub** until operator yes  
**Pattern:** twin Hyperlex Spec 007. Do not hard-import Hyperlex.

## Workflows

Use [WF-004 through WF-010 and WF-012](workflows.md). [Requirements](requirements.md), [journeys](../journeys.md), [state machines](../state-machines.md) and [contracts](../contracts/README.md) precede architecture. Agent skill assignments remain execution guidance, not product workflow definitions.

## CONTRACT

Learned encoder over settled + weak tradition atoms. Three-lens routing. Correspondence unbind on T1. `efficacy: null`. Contemporary systems as reception history. Hub card is encoder + sanitized excerpts.

## COMPONENTS

| ID | Component | Notes |
|----|-----------|-------|
| C1 | Gold settle export | From local SoT; KEEP ≠ gold |
| C2 | Sanitize export | Excerpt + license + family + hash; Hub-safe |
| C3 | Shadow train | `scripts/shadow/athanor/train_encoder.py` dry-run first |
| C4 | Heads | family, wave, atom_type, lens_route, reception_layer, unbind |
| C5 | Infer helper | stub in CI; Spark weights local |
| C6 | HF package | `specs/002-athanor-encoder/hf-package/` card shape only |
| C7 | Balance sampler | E7: no family > 25% tokens |

## DATA FLOW

```
~/.athanor/corpus/atoms.jsonl
  → gold settle filter (operator)
  → splits by content_hash / source_url
  → sanitize excerpts (Hub subset)
  → train on Spark (gated)
  → eval E0–E8
  → name-gate
  → operator yes
  → huggingface-cli upload
```

Lexical retrieve (Spec 001) remains the offline path if weights missing.

## PHASES

| Phase | Active node | Exit |
|-------|-------------|------|
| P3a Dataset freeze | gold+weak+neg+wall counts | numbers in a receipt, not a vibe |
| P3b Shadow train script | dry-run on toy slice | no weights in git |
| P4 Pre-train validation | tooling/schema/offline checks; eval protocol fixed | learned E1–E3 remain NOT_COMPUTABLE without trained weights |
| P5 Train gate | Danny yes | Spark run or HOLD |
| P5 post-train evaluation | exact trained artifact assessed by WF-009 | applicable E0–E8 recorded; missing evidence blocks claims |
| P6 Hub | Danny yes + name-gate | card matches eval table |

Do not jump P3a → P6.

## STACK DEFAULTS (INFERRED until implement yes)

| Decision | Default |
|----------|---------|
| T0 trunk | MiniLM-L6-v2 class or smaller — cheapest offline |
| T1 trunk | ModernBERT-base class (Hyperlex twin) |
| Train box | DGX Spark; T0-only may use local GPU if operator says so |
| Hub user | `scrimshawlife-ctrl` until AAL org OBSERVED |
| Dataset name | `athanor-atoms-sanitize-v0` |
| Model name | `athanor-encoder-modernbert-base-seed` until E2 |

## Historical next moves (superseded by completion map)

1. Operator lock clarify Q1–Q5 in spec 002.
2. Wave 3b family yes/HOLD.
3. Gold-settle pass on local 1178 (KEEP is not gold).
4. Do not upload.

This does not govern or activate. Existing P-phase IDs are retained; the clarified dependency order prevents a claim that learned evaluation happened before training. Backend, split and metric-support decisions remain in [decisions.md](../decisions.md).

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base)
