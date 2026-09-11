# Data model extension — encoder v0

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
