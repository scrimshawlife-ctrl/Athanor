# Dataset contract — Athanor encoder

**Status:** SHADOW specify  
**SoT:** `~/.athanor/corpus/atoms.jsonl` (not git, not Hub)  
**Public cousin:** `athanor-atoms-sanitize-*` excerpts only

## Classes

| Class | Who labels | May train T0 | May name-gate T1 | May publish Hub |
|-------|------------|--------------|------------------|-----------------|
| gold | operator settle | yes | yes | excerpt if license clear |
| weak KEEP | harvest heuristic | yes, capped | no, not sole | excerpt if license clear |
| HOLD | settle | no | no | no |
| DROP / quarantine | settle | no | no | no |
| negative | fixtures + operator | yes | yes | yes |
| dual-use wall | fixtures | eval only | eval only | prompts ok, not as tradition atoms |
| modern_reception | harvest + tag | yes, separate stratum | yes as reception, never as primary | excerpt if license clear |

## Split rule

Split by `source_url` host-path prefix and `content_hash`.  
All atoms from the same sacred-texts `/book/` leaf stay in one split.  
No lemma-level leak required; page-level leak is the defect to prevent.

## Minimum counts

### Plan implement (P3a exit)

- 400 gold classify rows across ≥12 families
- 40 correspondence unbind pairs
- 80 negatives
- 20 dual-use wall prompts
- Balance report written even if E7 fails

### T1 name-gate

- 3000 gold+weak classify rows
- ≥12 families with ≥30 rows each or family marked `NOT_COMPUTABLE` and dropped from the “comprehensive” claim
- 200 correspondence pairs
- 200 negatives
- 50 dual-use wall items
- per-family token share ≤ 0.25
- reception stratum present if Wave 3/3b rows are in train

## Sanitize exporter rules

- `text_excerpt` ≤ 500 characters
- required fields: `atom_id`, `family_id`, `license`, `source_url`, `epistemic`, `content_hash`, `reception_layer`
- drop rows with license in `{unknown, hold, closed-initiatory, all-rights}`
- drop full-page dumps, table dumps larger than 500 chars, seal binaries
- Enochian Calls: excerpt + pointer, never a concatenated Keys file
- `efficacy` column absent

## Negatives (required themes)

- news / weather / sports
- software docs
- ecommerce product copy
- AI-slop “manifest your abundance” clichés
- invented citations and fake grimoire titles

## Correspondence pair shape

```json
{
  "pair_id": "corr.planet.lead",
  "family_id": "alchemy_lab",
  "role": "planet",
  "filler": "Saturn",
  "span": "lead",
  "atom_id": "alchemy_lab:example",
  "epistemic": "INFERRED"
}
```

Gold pairs require operator settle. Weak pairs may bootstrap T0 only.
