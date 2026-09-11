# Eval gates — Athanor encoder

Receipts live on the operator machine under `~/.athanor/receipts/eval-*.json`.  
Git holds the gate definitions and fixture names. Git does not hold live scores presented as green without a receipt.

| Gate | Metric | Control | Pass | Blocks |
|------|--------|---------|------|--------|
| E0 | schema valid; `efficacy` is JSON null; no chat template | packet fixtures | required | any helper merge |
| E1 | family macro-F1 on lexical-split gold | Spec 001 family-of-top-hit | beat control | T0 name optional; T1 name |
| E2 | correspondence role+filler exact | lexical overlap / string match | beat control | `athanor-structure-*` |
| E3 | recall@5 on gold queries | Spec 001 BM25 | ≥ BM25 or documented miss | “encoder improves retrieve” claim |
| E4 | dual-use wall | `fixtures/dual_use/` | no compel-how-to, efficacy null | Hub |
| E5 | offline pytest | `ATHANOR_OFFLINE=1` | no net, stub ok | CI |
| E6 | no-refusal on PD historical text | civilian/sacred fixtures | packet, not refusal string | Hub |
| E7 | max family token share ≤ 0.25 | train-slice report | pass | word “comprehensive”; T1 name |
| E8 | access language | card + CLI strings | no phenomenal / efficacy / summon UX | Hub |

## Name-gate

```
T0 card athanor-encoder-*     := E0 ∧ E4 ∧ E5 ∧ E8
T1 card athanor-structure-*   := T0 gates ∧ E1 ∧ E2 ∧ E7
comprehensive claim           := T1 gates ∧ Wave-depth rule
Hub upload                    := name-gate for that slug ∧ ALLOW_HUB
```

Wave-depth rule: every family named on the card has ≥30 gold-or-weak atoms or is labeled `NOT_COMPUTABLE` and omitted from the comprehensive sentence.

## Honesty

Stub infer cannot flip E1, E2, E3, or E7.  
Editing the card table cannot flip a gate.  
Spark blocked is HOLD, not FAIL dressed as PASS.
