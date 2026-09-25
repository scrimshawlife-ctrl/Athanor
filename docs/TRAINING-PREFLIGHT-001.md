# TRAINING-PREFLIGHT-001

**Goal:** Establish a reproducible, leakage-resistant evidence boundary that can truthfully answer whether Athanor is ready for a pilot training run.

**Status:** IN_PROGRESS · training remains HOLD until every required gate has machine-verifiable evidence.

## Assumptions

- Current corpus volume is sufficient for preflight; additional harvesting is not a prerequisite.
- Existing retrieval scores are baseline observations, not proof of generalization.
- Derived rows from the same source component must not cross TRAIN/DEV/TEST boundaries.
- JEV acceptance is candidate evidence and MUST NOT be treated as independently reviewed GOLD.

## Gate chain

1. **G0 Repository hygiene** — no accidental/debris files in the training surface.
2. **G1 Validation** — Ruff, contract verification, and pytest pass on Python 3.10, 3.11, and 3.12.
3. **G2 Corpus freeze** — exact corpus inputs and hashes are recorded.
4. **G3 Provenance/rights** — source and reception/rights evidence is complete for admitted rows.
5. **G4 Component split** — split by contamination-relevant source component, never by derived row alone.
6. **G5 Leakage audit** — exact and near-duplicate/source-family overlap across splits is measured and blocking violations are zero.
7. **G6 GOLD holdout** — final evaluation contains independently reviewed, content-bound decisions; JEV-only candidates remain distinct.
8. **G7 Baseline** — evaluate the untrained system on the untouched frozen TEST split and preserve the receipt.
9. **G8 Training config freeze** — model/base weights, tokenizer, seed, hyperparameters, code SHA, dataset SHA, and environment are pinned.
10. **G9 Pilot** — bounded pilot training only after G0-G8 PASS.
11. **G10 Post-train evaluation** — compare pilot to G7 on the same untouched TEST receipt before authorizing a full run.

## State model

`HOLD -> PREFLIGHT_PASS -> PILOT_AUTHORIZED -> PILOT_EVALUATED -> FULL_TRAIN_ELIGIBLE`

No gate may infer a later state. Missing evidence is `NOT_COMPUTABLE`, which resolves to `HOLD` for authorization.

## Required readiness receipt

A future `training-readiness.json` MUST be generated from evidence rather than hard-coded prose and include:

- repository SHA
- corpus/dataset manifest SHA256
- split manifest SHA256
- source-component overlap counts
- duplicate/near-duplicate audit results
- provenance/rights summary
- GOLD review counts and reviewer/approval references
- baseline metrics by lane and family
- validation matrix for supported Python versions
- training configuration digest
- gate results G0-G10
- final state and blocking reasons

## Acceptance

Training remains **HOLD** until G0-G8 are PASS. A high retrieval score alone cannot satisfy G5-G8.


## Executable receipt

Generate the current fail-closed G2-G8 receipt from a candidate pack:

```bash
python -m athanor.training_preflight \
  --pack /path/to/candidate-pack \
  --repo-sha "$(git rev-parse HEAD)" \
  --output out/training-readiness.json
```

Exit codes:

- `0`: all represented G2-G8 gates PASS (this still does not authorize training).
- `2`: valid evidence, but one or more gates remain HOLD.
- `1`: invalid or unsafe evidence input.

The current receipt intentionally keeps G3, G6, G7, and G8 on HOLD until authenticated rights review, independent content-bound GOLD review, an untouched-test baseline receipt, and a pinned training configuration are supplied by later contracts.


## G3/G6/G7/G8 evidence binding

The receipt generator accepts four optional private evidence sidecars:

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

Each sidecar must identify the expected evidence kind, report PASS, bind the exact candidate manifest SHA256, and carry a SHA256 evidence digest. A repo SHA may also be supplied; if present it must match the evaluated checkout. Wrong-kind, stale-manifest, stale-repo, non-PASS, or malformed evidence remains HOLD.

The generic envelope is `schemas/training_preflight_evidence.v1.schema.json`. This envelope proves binding only. It does not prove that a rights reviewer, GOLD reviewer, baseline harness, or training configuration is substantively correct. Those producers remain separate workflows.

Even when G2-G8 all PASS, the generated receipt keeps `training_authorized=false`. Pilot execution still requires a separate, explicit, scoped operator authorization after preflight.


## G3 rights-audit producer

Before any training-rights approval is possible, triage the exact corpus atom snapshot:

```bash
python -m athanor.training_rights \
  --atoms ~/.athanor/corpus/atoms.jsonl \
  --candidate-manifest-sha256 <64-hex-candidate-manifest> \
  --output out/training-rights-audit.json
```

This command is deliberately non-authorizing and exits 2 for a valid audit. It treats recognizable public-domain/open-license strings only as `candidate_clearable`; all other claims are explicit unresolved rows. It never converts a nonempty `license` field, an allowlisted host, or a public-domain-looking string into G3 PASS.

The resulting audit is the queue for work/edition/source evidence review. A later authenticated review may produce the `provenance_rights` PASS sidecar consumed by `athanor.training_preflight`; this triage report cannot be used as that sidecar because its evidence kind/status intentionally differ.


## G3 model-training rights settlement

The existing corpus-admission approval covers `local_analysis` only and MUST NOT be reused as model-training clearance.

After `athanor.training_rights` produces the review queue, an independent reviewer resolves the exact work/edition/source evidence into `athanor.training_rights_review.v1`. Every included source must be explicitly `CLEARED` for `intended_use=model_training`, with evidence digests and a candidate-manifest binding.

Convert a completed review into the G3 sidecar:

```bash
python -m athanor.training_rights_review \
  --review /private/training-rights-review.json \
  --repo-sha "$(git rev-parse HEAD)" \
  --output /private/provenance-rights.json
```

Any HOLD source, missing evidence, wrong use scope, stale manifest, or malformed review fails closed. This converter validates the review contract; it does not perform or substitute for legal review.
