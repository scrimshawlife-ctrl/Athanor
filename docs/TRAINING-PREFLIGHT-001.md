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
