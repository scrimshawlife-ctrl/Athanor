# P3a local exit seal — Spec 002

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

- `scripts/shadow/athanor/apply_gold_p3a.py` — refuses KEEP-as-gold
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
