# Data model extension — encoder v0

Status: v0 intent plus proposed completion model below. This does not govern or activate. Training rows are not inserted into the closed atom schema.

Inherits `specs/000-athanor-spine/data-model.md`.

Existing `athanor.atom.v0` stays closed. Encoder training rows are a view: `athanor.atom.trainrow.v0`.

Required view fields: atom_id, family_id, type, text, license, source_url, epistemic, content_hash, reception_layer, settle, split.

Correspondence pair view: `athanor.correspondence.pair.v0` (pair_id, family_id, role, filler, span, atom_id, epistemic).

Encoder inference schema: `schemas/athanor_encoder_inference.v0.schema.json`.
Attaches optionally on `athanor.packet.v0` under key `encoder`.

Receipt job_type gains gold_settle / sanitize_export / train / eval.

Local paths:
- `~/.athanor/corpus/atoms.jsonl`
- `~/.athanor/settle/gold.jsonl`
- `~/.athanor/exports/sanitize-*.jsonl`
- `~/.athanor/receipts/*.json`
- `~/.athanor/weights/` (never git)

## Proposed joins, labels and splits

Join atom revisions to rights and settlement decisions by ID plus digest, not atom_id alone. GOLD and weak KEEP views are disjoint: remove gold revisions from KEEP train membership. HOLD/DROP cannot enter either. The report's 2,597 INFERRED atoms is not equivalent to 2,424 reported non-gold KEEP rows. Independently observed current eligibility remains NOT_COMPUTABLE.

Train rows carry supervision, split, group_id, reviewed labels and loss_mask. family_id resolves to a pinned registry; wave is derived. Missing lens/reception/correspondence targets are masked. Validation/test labels require per-target GOLD evidence. Synthetic negatives test OOD handling, not historical truth; wall prompts are eval-only. Correspondence pairs bind exact source atom/hash and reviewed role/filler/span.

Canonical reception values: primary_witness, pd_translation, historical_commentary, modern_reception. Legacy period_translation and primary_pd require explicit reviewed mapping (DEC-008); missing metadata uses null/reason in an envelope and is excluded where the train/export contract requires a label. Never emit an unrecognized unspecified string.

Freeze grouping by connected components of known work, edition, normalized source and duplicate content. Keep all linked rows/pairs in one split; grouping propagates transitively. Missing identity that prevents leakage checks blocks the relevant freeze claim. Record ratios, seed, algorithm, canonicalizer, tokenizer revision and exclusion report. Recompute token balance on the actual sampled train slice; gold-only balance is separately named.

Schemas/contracts: [C-005 through C-010](../contracts/README.md). Version negotiation preserves v0 readers; migration and producer enforcement are future implementation work. Stored original atoms, historical receipts and current runtime schemas remain unchanged.

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base)
