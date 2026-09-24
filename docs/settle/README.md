# Settle policy

Operator settle classifies harvested atoms before any gold epistemic label. Local SoT is `~/.athanor/corpus/atoms.jsonl` (not in git). Quarantine files stay on the operator machine.

| Decision | Meaning |
|----------|---------|
| **KEEP** | Atom remains in local SoT. Heuristic KEEP stays **INFERRED** until an explicit gold settle. KEEP is not OBSERVED gold. |
| **DROP** | Reject (chrome/stub or other). May be quarantined locally. Not committed. |
| **HOLD** | Deferred. Do not treat as PD gold. |

## HOLD: Rowe / Achadian `/book/` essays

Modern sacred-texts `/book/` Rowe / Achadian essays stay **HOLD**. They are not PD gold without an explicit operator license call.

## Observed local SoT (operator machine)

After deepen the local corpus was **1227** atoms. After settle DROP, **1178** remain and **49** were quarantined. Family-level post-settle counts are not published. Do not commit `atoms.jsonl` or quarantine files.

## Retrieve-time chrome (not a settle rewrite)

Spec 001 T5 (`src/athanor/chrome.py`) strips sacred-texts SPA nav when building retrieve excerpts. It does **not** rewrite stored atoms. A later harvest pass may reuse `strip_chrome` if operators want clean stored `text`.

## Gates

- Crawl4AI 0.9.3 is the scrape default. Paid Firecrawl needs an operator yes.
- Train / Hub stay gated.
- Packet `efficacy` stays JSON `null`. No summon UX.

## Jev-deepened settle (T4-JEV-002)

Settle decisions route through jev rerank for evidence-bound quality.
- Quarantine rows now include `jev_relevance` (from rerank) and `suggested_settle` (KEEP/HOLD/REVIEW based on threshold + flags).
- `scripts/shadow/athanor/settle.py` consumes cleaned.jsonl (or atoms), re-ranks with jev, proposes final decisions.
- High jev (>=0.75) + BODY_CANDIDATE + no flags -> suggested KEEP.
- Low jev (<0.4) or problematic routes -> HOLD.
- Operator reviews proposals; custom cues only for validation.
- Run: `cat ~/.athanor/quarantine/.../cleaned.jsonl | python scripts/shadow/athanor/settle.py --min-relevance 0.6 > proposals.jsonl`
- Deepen harvest also emits `.settle_proposals.jsonl` for new atoms.

All classifying (including settle) uses jev rerank.
