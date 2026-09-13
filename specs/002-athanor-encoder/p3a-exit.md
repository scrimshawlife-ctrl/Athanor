# P3a local exit seal — Spec 002

## Current evidence qualification

This is the historical operator-machine report, not an independent certification of the fourteen-stage method. At review base fd84c708, committed fixtures are independently countable: 63 pairs, 80 negatives, 55 wall prompts. The local corpus, exact label-review evidence and E7 reports are not available in this checkout: independent GOLD validity, current eligible row counts and E7 reproduction are NOT_COMPUTABLE. The 2597 INFERRED atoms must not all be called KEEP; this report separately lists 2424 non-gold KEEP rows.

The original seal and counts below remain historical. Scripts/fixtures and a reported seal do not prove actual model wall behavior, trained metrics or runtime contract conformance. See [eval-gates.md](eval-gates.md) and [DEC-001](../decisions.md). This does not govern or activate.

**Date:** 2026-09-11 PT  
**Operator:** Danny / Boof (executor on shared box)  
**Lane:** SHADOW specify — train/Hub still fail-closed  

## Sealed counts (OBSERVED)

| artifact | target (P3a) | achieved | path |
|----------|-------------:|---------:|------|
| gold classify | 400 across ≥12 families | **400** / 27 families | `~/.athanor/settle/gold.jsonl` (batch `gold-p3a-001`) |
| correspondence pairs | ≥40 | **63** | `~/.athanor/settle/correspondence_pairs.jsonl` · `fixtures/correspondence/pairs.p3a.jsonl` |
| negatives | ≥80 | **80** | `~/.athanor/settle/negatives.jsonl` · `fixtures/negatives/negatives.p3a.jsonl` |
| dual-use wall | ≥20 (P3a) / ≥50 (T1 prep) | **55** | `~/.athanor/settle/dual_use_wall.jsonl` · `fixtures/dual_use/wall.p3a.jsonl` |
| local SoT atoms | fill3000 | **2997** after DROP | `~/.athanor/corpus/atoms.jsonl` (**not in git**) |
| KEEP weak (INFERRED) | optional | **2824** settle rows / **2424** non-gold | `~/.athanor/settle/keep.jsonl` |

## E7

| slice | max family token share | result |
|-------|-----------------------:|:------:|
| 400 gold | **~0.0674** | **PASS** (≤0.25) |
| gold+KEEP candidate | ~0.1384 | PASS |

Receipt/report: `~/.athanor/settle/balance-report-p3a-20260911T081248Z.{md,json}` · receipt `~/.athanor/receipts/p3a-remainder-20260911T081248Z.json` · gold receipt `gold-settle-p3a-20260911T080756Z.json`.

## Eval honesty

- **E0** lexical retrieve / packet smoke: **PASS** (Spec 001 live + local pytest).
- **E2** correspondence unbind: **FAIL** until train eval harness (pairs exist; encoder not trained).
- **E7** gold slice: **PASS**.

## Scripts sealed for specify

- `scripts/shadow/athanor/apply_gold_p3a.py` — historical selection/application helper; reviewed GOLD evidence is NOT_COMPUTABLE. The earlier description "refuses KEEP-as-gold" is not supported by the selection logic.
- `scripts/shadow/athanor/sanitize_export.py` — excerpt ≤500; required contract fields; no Hub

## Gated remainder (unchecked)

| item | gate |
|------|------|
| U11–U14 implement / train scripts | no `ALLOW_TRAIN` · no Spark train run |
| U18 ADVERSARY Hub pass | no `ALLOW_HUB` |
| U19 `ALLOW_TRAIN` / `ALLOW_HUB` artifacts | fail-closed absent |
| Wave 3b live registry merge | HOLD (proposal only) |
| Hugging Face upload | forbidden without `ALLOW_HUB` |
| atoms.jsonl in git | forbidden |

## Aaron offline pack pointer

Local (not Hub): `/workspace/athanor-harvest/aaron-train-pack-20260911/`  
Zip: `/workspace/athanor-harvest/athanor-train-pack-aaron-20260911.zip`  
Audience: Aaron Godbout (Zero State co-founder). Contact via Danny. Notion publish is parent-owned.

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base)
