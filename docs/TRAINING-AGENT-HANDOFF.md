# Training preflight agent handoff

Status: **EXECUTE PREFLIGHT; DO NOT TRAIN**

This file is the explicit handoff for an agent running on the machine that owns the
local Athanor source of truth at `~/.athanor`.

## Objective

Produce truthful, machine-bound evidence for G2-G8. Do not start a pilot or full
training run. Do not promote heuristic labels to GOLD. Do not reinterpret
`local_analysis` rights as `model_training` rights.

## Invariants

1. Local SoT is `~/.athanor`; do not commit corpus text, private review evidence,
   trust files, signatures, keys, or generated private sidecars.
2. Missing evidence is `NOT_COMPUTABLE` and resolves to HOLD.
3. Every receipt must bind the exact candidate manifest. Preserve SHA256 values.
4. All descendants of one source/work/edition/overlap component stay in one split.
5. The untouched TEST partition must remain untouched until baseline/evaluation.
6. JEV/heuristic KEEP is not GOLD.
7. `training_authorized=false` remains true until a separate explicit operator
   authorization is issued after preflight.
8. Stop on any digest mismatch, scope mismatch, overlap, unresolved rights, or
   validation failure. Do not repair evidence by weakening a gate.

## Step 0 — synchronize and validate

```bash
git switch main
git pull --ff-only
python -m pip install -e '.[dev]'
ruff check .
python scripts/validate_semantic_contracts.py
pytest -q
git rev-parse HEAD
```

Expected: all validation green. Record the repo SHA.

## Step 1 — locate/freeze the candidate pack (G2/G4/G5)

Use the existing candidate-pack/freeze workflow documented in
`docs/TRAINING-PREFLIGHT-001.md`. Do not invent source grouping identities. If a
reviewed overlap registry exists, use the pinned registry path, digest, and complete
source bindings.

Run the readiness receipt against the exact candidate pack and preserve its manifest
SHA256. If G2, G4, or G5 is not PASS, stop and resolve that evidence boundary before
rights or GOLD review.

## Step 2 — produce the G3 review queue

Run against the exact local corpus snapshot:

```bash
python -m athanor.training_rights \
  --atoms ~/.athanor/corpus/atoms.jsonl \
  --candidate-manifest-sha256 <CANDIDATE_MANIFEST_SHA256> \
  --output out/training-rights-audit.json
```

Exit 2 is expected for a valid non-authorizing audit. Inspect:
- `candidate_clearable`
- `unresolved`
- host distribution

Do not treat `candidate_clearable` as CLEARED.

## Step 3 — independent model-training rights review (G3)

Create a private review matching
`schemas/training_rights_review.v1.schema.json`.

Required semantics:
- `intended_use` exactly `model_training`
- explicit jurisdiction and reviewer
- exact candidate-manifest binding
- every included source has a stable work/edition identity
- every source decision is `CLEARED`
- evidence hashes resolve to evidence actually reviewed

A source that cannot satisfy this contract stays out/HOLD. Do not reuse the existing
`local_analysis` admission approval as training clearance.

Then:

```bash
python -m athanor.training_rights_review \
  --review /private/training-rights-review.json \
  --repo-sha "$(git rev-parse HEAD)" \
  --output /private/provenance-rights.json
```

## Step 4 — G6 independent GOLD

Do not run retired heuristic GOLD promotion. Build/review the holdout from
content-bound labels only. Reviewer evidence must be independent of the heuristic
that proposed the pair. Bind the review to the candidate manifest and untouched
TEST identities. Until an independent GOLD sidecar exists, G6 remains HOLD.

## Step 5 — G7 untouched baseline

Before any weight update, evaluate the untrained/base system on the untouched TEST
partition. Record the exact repo SHA, candidate/split manifests, evaluator config,
seed, hit@k, corrected nDCG, MRR, per-family results, and available ID/OOD/adversarial
lanes. Preserve misses as zero in nDCG. Do not tune against TEST.

Until this receipt exists, G7 remains HOLD.

## Step 6 — G8 training configuration freeze

Freeze, do not infer, the actual:
- base model ID and immutable revision
- tokenizer ID and immutable revision
- random seed(s)
- sequence length
- optimizer and learning-rate schedule
- batch size / gradient accumulation
- epochs or max steps
- precision
- LoRA/PEFT settings if used
- candidate and split manifest digests
- repository SHA
- relevant runtime/hardware versions

Digest the complete config. Unknown values keep G8 HOLD.

## Step 7 — assemble final preflight receipt

```bash
python -m athanor.training_preflight \
  --pack /path/to/candidate-pack \
  --repo-sha "$(git rev-parse HEAD)" \
  --rights-evidence /private/provenance-rights.json \
  --gold-evidence /private/independent-gold.json \
  --baseline-evidence /private/untrained-baseline.json \
  --config-evidence /private/training-config.json \
  --output out/training-readiness.json
```

Interpretation:
- any HOLD => stop; training remains unauthorized
- `PREFLIGHT_PASS` => evidence prerequisites are satisfied
- `PREFLIGHT_PASS` is **not** permission to train
- require a separate explicit, scoped operator authorization for a bounded pilot

## Return packet

Report back with only:
1. repo SHA
2. candidate manifest SHA256
3. G2-G8 state table
4. unresolved/HOLD reasons
5. paths + SHA256 digests of generated receipts
6. baseline summary if G7 ran
7. proposed immutable training config if G8 was frozen
8. explicit statement: `TRAINING NOT STARTED`

Never include private keys, trust-file contents, corpus text, or copyrighted source
text in the return packet.
