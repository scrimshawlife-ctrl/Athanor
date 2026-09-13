# Gold settle protocol

Evidence qualification: the historical apply_gold_p3a.py selects heuristic KEEP candidates and stamps OBSERVED. That does not by itself prove reviewed target labels. The existing 400-row GOLD validity is NOT_COMPUTABLE pending DEC-001; historical reports are retained.

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

A script may propose KEEP vs DROP. It may not independently decide or stamp GOLD. The proposed [WF-004](workflows.md) permits an executor to apply exact reviewed decisions only after verifying existing operator approval and input hashes; it cannot turn its own heuristic selection into review evidence.
No gold.jsonl in git.

Target decision/approval fields: [C-004](../contracts/README.md). This documentation does not validate historical approvals, alter the source corpus, or grant promotion authority. This does not govern or activate.

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base)
