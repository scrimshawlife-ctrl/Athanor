# Gold settle protocol

Harvest KEEP is not gold. This protocol is the only path from local SoT to OBSERVED train labels.

## Inputs

- `~/.athanor/corpus/atoms.jsonl`
- `docs/settle/README.md` decisions
- operator yes per batch (constitution VIII)

## Decisions per atom

| Decision | Epistemic after | Train |
|----------|-----------------|-------|
| GOLD | OBSERVED | gold split |
| KEEP | INFERRED | weak only |
| HOLD | INFERRED | excluded |
| DROP | n/a | excluded / quarantine |

## Batch rules

- Work by `family_id` then `source_url`.
- Enochian GOLD is capped so that after sampling the family cannot exceed the 0.25 token share on the eventual train slice.
- HOLD remains the default for Rowe/Achadian `/book/` essays and any post-1928 page without a license call.
- Chrome-heavy atoms DROP or re-harvest. Retrieve-time strip is not a settle rewrite.
- Correspondence pairs GOLD only when role and filler are explicit in the excerpt.

## Outputs (local)

- `~/.athanor/settle/gold.jsonl`
- `~/.athanor/settle/keep.jsonl`
- `~/.athanor/settle/hold.jsonl`
- receipt `job_type=gold_settle` with counts by family

## Honesty

A script may propose KEEP vs DROP. It may not stamp GOLD.  
No gold.jsonl in git.
