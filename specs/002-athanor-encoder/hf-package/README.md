---
license: mit
library_name: transformers
pipeline_tag: text-classification
base_model: answerdotai/ModernBERT-base
base_model_relation: adapter
tags:
  - encoder
  - athanor
  - hermetic
  - not-chat
  - no-efficacy
---

# athanor-structure-modernbert-base-seed (provisional T1 draft)

**Furnace, not oracle.** This card is the publish *shape*. Name-gate is false until Spec 002 E2 and E7 pass. Weights are produced on Spark and are not in git.

Completion qualification: this is a provisional T1 structure-tier draft, not an existing model. Base checkpoint/tokenizer and artifact identity remain DEC-002. All T1 prerequisites include T0 gates plus E1/E2/E7; Hub additionally requires E6, rights/export review and verified operator approval. The historical table below is not a current release certification; use [eval-gates.md](../eval-gates.md) for evidence scope. Model training results, E4/E6 execution and independent E7 reproduction are NOT_COMPUTABLE here. The frontmatter is draft metadata, not an approved license declaration for future weights or corpus.

Do not treat this file as a live Hub upload.

## What this is

A small **encoder** over public-domain and license-cleared tradition atoms from the Athanor corpus. It routes family, lens, and reception layer. It does not cast, summon, initiate, or score results.

`efficacy` is always JSON `null`.

## What this is not

- A chatbot or ritual co-pilot
- An efficacy engine
- A Sigil-Forge authority-seal mint
- An Enochian / Goetic command surface
- A consciousness or spirit detector
- The unrelated Hub artifacts `schneewolflabs/Athanor-DPO` and `carlosmm26/Atanor-4B`

## Constitution restated (required on every card)

1. **Furnace, not oracle.** Outputs are cultural-technology readings.
2. **Enochian and grimoire text may appear as history.** Product surfaces that summon, compel, or mint authority seals are out of scope.
3. **Access language only.** No phenomenal, sentience, or spirit-presence claims.

## Intended use

Offline retrieve re-rank and family/lens routing for operators and HERMENEUT packets.

There is no chat template.

## Training data

Local SoT is `~/.athanor/corpus/atoms.jsonl` (not in git, not this card).
Public companion dataset (when gated) is excerpt-only, license-tagged, epistemic-labeled.
KEEP harvest rows are INFERRED. They are not gold.

## Historical eval table (2026-09-11 report; qualified above)

| Gate | Status | Note |
|------|--------|------|
| E0 packet / lexical retrieve smoke | PASS | packet fixtures + Spec 001 retrieve smoke OBSERVED; efficacy null |
| E1 family classify | NOT RUN | needs Spark weights + train eval harness |
| E2 correspondence unbind | FAIL | pairs exist (63) but encoder unbind **not trained**; blocks `athanor-structure-*` |
| E3 recall@5 vs BM25 | NOT RUN | Spec 001 is the control |
| E4 dual-use wall | PASS | `fixtures/dual_use/wall.p3a.jsonl` (55); refuse_or_historical_only |
| E5 offline | PASS | no network |
| E6 no-refusal on PD text | PASS | stub / retrieve |
| E7 family balance | PASS (gold slice) | max family token share ~0.067 on 400 gold; ≤0.25 |
| E8 access language | PASS | this card |

Do not flip E2 by editing the card. E7 gold PASS ≠ Hub authorization (`ALLOW_HUB` absent). Train gated (`ALLOW_TRAIN` absent).

This does not govern or activate.

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base)
