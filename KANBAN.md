# Kanban — Athanor

Board state as measured, not as remembered. Every item below was true on the date at the bottom.

| | Backlog | In progress | Blocked | Done |
|---|---|---|---|---|
| **Count** | 2 | 0 | 3 | 4 |

**Blocked** matters more than the other columns: an item sits there when it is waiting on something this
repository cannot supply, and the blocker is named rather than implied.

_Last reviewed: 2026-10-07._

## Backlog

- Bring the 10 sealed-run artifacts into `STATUS.md`, per this repository's own convention.
- Widen corpus coverage for the traditions the three-lens encoder already handles.

## In progress

- Nothing. The corpus and tooling are in a repaired, consistent state.

## Blocked

| Item | Blocked on | Evidence |
|---|---|---|
| Train the bias-corrected adapter | A provisioned training environment | `specs/003-qwen-adapter/model-lock.json`: `weight_downloaded: false`, `allow_train: false`, `MODEL_REVISION_SELECTED_ENVIRONMENT_NOT_COMPUTABLE` |
| Publish any model result | Trained weights | `adapter_preflight` → `HOLD`; pointed at the adapter → `INVALID`. No weight file exists in this repository or in this clone. |
| Verify the adapter's base model | Agreement on which base this adapter belongs to | `adapter_config.json` names `nvidia/Llama-3.1-Nemotron-Nano-8B-v1`; spec `003` pins `Qwen/Qwen3.8-27B` |

## Done

- `pair_id` generation repaired — byte-identical to `scripts/harvest_family.py`'s, confirmed against generated
  data and a tracked fixture.
- Every tracked `.py` parses.
- `adapter_preflight` (read-only; never downloads, loads weights, or trains).
- `EXECUTION-RECEIPT.md` re-measured against this clone: 2 of 7 claimed artifacts present, both weight files
  absent. The receipt carries a verification note rather than an edited history.
