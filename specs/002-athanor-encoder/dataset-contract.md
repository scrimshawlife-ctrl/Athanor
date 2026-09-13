# Dataset contract — Athanor encoder

**Status:** SHADOW specify  
**SoT:** `~/.athanor/corpus/atoms.jsonl` (not git, not Hub)  
**Public cousin:** `athanor-atoms-sanitize-*` excerpts only

Completion target: [WF-004/005/006](workflows.md), [C-004/C-005/C-008](../contracts/README.md), and [data model](data-model.md) define eligibility, rights, split and reconstruction semantics. Current exporter behavior is not contract conformance. This does not govern or activate.

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

Target refinement: group connected work/edition/canonical-source/content-hash identities before split assignment; mirrored pages must not cross splits. Record canonicalizer/grouping revisions, ratios and seed. Unknown identities that prevent leakage checks remain unresolved. Weak rows are train-only; validation/test truth requires reviewed GOLD labels.

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

Eligibility requires both settlement and use-scoped rights clearance. HOLD/DROP cannot export even when license is public-domain. Evaluate full-work boundaries and aggregate excerpts by work/edition; the character limit does not permit a complete short Call. Missing required reception metadata excludes public training rows; legacy mappings require review, not unspecified defaults.

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

Reported P3a candidate rows: 400 gold + 2424 non-gold KEEP = 2824, subject to independent eligibility verification (NOT_COMPUTABLE here). The committed 63 pairs and 80 negatives are below the T1 thresholds by 137 and 120 respectively. Raw corpus count is not eligible train-row count; thresholds apply after exclusions, grouping and task-specific labeling.

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base)
