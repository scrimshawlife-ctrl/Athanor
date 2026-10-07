# Athanor Training Continuation — Corrected Execution Receipt

## 1. OBSERVED Run 001 Findings

| Artifact | Status | Verification |
|----------|--------|--------------|
| Training config | RECOVERED | `configs/nemotron-training-final.yaml` |
| Training log | RECOVERED | `~/Athanor/training.log` (112K chars, 4 concatenated runs) |
| Merge log | RECOVERED | `~/Athanor/merge.log` |
| Eval results | RECOVERED | `eval_results.json` |
| Adapter artifacts | RECOVERED | `lora-out-nemotron/adapter_model.safetensors` (336MB) |
| Merged model | RECOVERED | `merged-nemotron-ath/model.safetensors` (5.4GB) |
| Corpus manifest | RECOVERED | `out/training-readiness-delphi.json` |
| Preflight evidence | RECOVERED | All G2-G8 PASS at `8a3ca40` |
| Commit SHA | CONFIRMED | `d8206d6` (Run 001 completion) |
| Environment | CONFIRMED | GB10 / Delphi / torch 2.15.0.dev |

### Verification note — 2026-10-07 (from `~/Athanor` on macOS)

Status above records what was recovered from the training host (`GB10 / Delphi`). Re-checked against this
clone, because a receipt is a claim and a claim needs re-measuring when the machine changes:

| Artifact | Claimed | Present in this clone |
|---|---|---|
| `configs/nemotron-training-final.yaml` | RECOVERED | **yes** |
| `eval_results.json` | RECOVERED | **yes** |
| `training.log` | RECOVERED | no |
| `merge.log` | RECOVERED | no |
| `lora-out-nemotron/adapter_model.safetensors` (336MB) | RECOVERED | **no** |
| `merged-nemotron-ath/model.safetensors` (5.4GB) | RECOVERED | **no** |
| `out/training-readiness-delphi.json` | RECOVERED | no |

`git ls-files | grep -c safetensors` → **0**. The two weight files — the only artifacts that would let any of
this be loaded for inference — are not here, and never were in version control.

The repository's own tooling already says so, and said so before this note: `python -m athanor.adapter_preflight`
→ `{"status": "HOLD", "weights_verified": false, "training_authorized": false}`, and pointed at
`t1_bias_corrected_adapter` → `{"status": "INVALID", "reason": "Missing, unsafe or oversized model config"}`.
`specs/003-qwen-adapter/model-lock.json` records `"weight_downloaded": false`.

**Consequence for anything consuming this engine:** no adapter can be loaded here, so no inference path in
Abraxas may claim one. Engines route model inference through `abraxas.evidence.adapters.model_agnostic` and
report `model-agnostic/offline-deterministic` when no endpoint is configured. Custom inference stays a later
capability until weights exist somewhere a consumer can reach.

**Independent recomputation of derived values:**
- Trainable params: 83,886,080 / 8,114,147,328 = **1.0338%** ✅
- Final eval loss: 5.282 (trainer) / 5.2843 (merged, 100 samples) ✅
- Base loss: 5.2886 (100 samples) ✅
- Delta: -0.0044 loss / -0.86 ppl ✅

---

## 2. Run 001 Behavioral Change Assessment

**VERDICT: MARGINAL DOMAIN ADAPTATION — NOT SUFFICIENT FOR CAPABILITY CLAIM**

- Statistical: -0.083% loss improvement (negligible)
- Qualitative: Family-conditioned generation observed (Græ Runen, sephiroth, Fehu)
- But: Hallucinations present (non-standard terminology)
- **Cannot claim meaningful Athanor capability acquisition from loss delta alone**

---

## 3. Training Curve Diagnosis

**NOT_COMPUTABLE — INSUFFICIENT TELEMETRY**

| Metric | Status |
|--------|--------|
| Training loss trajectory | NOT COMPUTABLE (never logged) |
| Intermediate eval loss | NOT COMPUTABLE (only step-0 eval visible) |
| Convergence/plateau | NOT COMPUTABLE (no intermediate data) |
| Exact optimizer steps | NOT COMPUTABLE (no trainer_state.json) |
| Epochs completed | NOT COMPUTABLE (final eval reports epoch=0) |

**Previous "PLATEAUED (C)" conclusion WITHDRAWN.** Absence of measured improvement ≠ evidence of plateau.

---

## 4. Masking/Objective Verdict

**CORRECT** — `train_on_inputs: false` with completion format correctly masks `Family: {family}\nText: ` prefix. Only target corpus content contributes to loss. Padding and special tokens handled via standard HF -100 masking. No discrepancy between intended and implemented objective.

---

## 5. Anomalies Discovered (Evidence-Classified)

| Severity | Anomaly | Classification |
|----------|---------|----------------|
| HIGH | No checkpoint dirs found | OBSERVED |
| HIGH | Training loss not logged | OBSERVED |
| MEDIUM | Intermediate evals missing (expected at steps 50,100,150,200,250) | OBSERVED |
| MEDIUM | Final eval metadata epoch=0 | OBSERVED |
| LOW | OOM warning during final eval | OBSERVED |
| MEDIUM | Checkpoint saving failed (config has save_steps=50) | INFERRED |
| LOW | 4 concatenated runs in single log | OBSERVED |
| NOT_COMPUTABLE | Why checkpoints failed | Root cause unknown |
| NOT_COMPUTABLE | Why training loss not logged | Root cause unknown |
| NOT_COMPUTABLE | Why epoch=0 in eval | Root cause unknown |

---

## 6. Run 002 Hypothesis (Corrected)

**VARIABLE**: Training budget (optimizer steps 288→96, epochs 3→1, warmup 20→7)

**JUSTIFICATION**: 
1. Run 001 final eval: 5.2843 vs base 5.2886 = -0.0044 delta
2. **Training trajectory NOT_COMPUTABLE** — cannot determine if 288 steps were necessary
3. **Observability failure** — Run 001 produced no intermediate telemetry
4. Run 002 must fix observability while testing budget hypothesis

**HYPOTHESIS**: Reducing training budget from 288 to ~96 optimizer steps (preserving scheduler geometry: 6.94% warmup fraction) achieves **equivalent final evaluation performance** while providing **full trajectory observability**.

---

## 7. Primary Variable & Thresholds

| Metric | Promotion Threshold | Failure Threshold |
|--------|---------------------|-------------------|
| eval_loss (step 96) | ≤ 5.285 | > 5.290 |
| eval_ppl vs base | ≤ +0.5% | > +1% |
| qualitative preservation | no degradation | visible degradation |
| observability | complete (training loss, LR, checkpoints, trainer_state.json) | any missing |
| wall_time | ≤ 20 min | > 30 min |

---

## 8. Files Created/Changed (All Synced to Delphi)

| File | Purpose |
|------|---------|
| `RUN-001-manifest.json` | **CORRECTED** — evidence-classified baseline receipt |
| `RUN-001-diagnostic-report.md` | **CORRECTED** — full diagnostic with evidence tags |
| `configs/nemotron-training-run002.yaml` | **CORRECTED** — warmup=7, logging_steps=5, save/eval_steps=24, seed=42 |
| `RUN-002-preregistration.yaml` | **CORRECTED** — single variable, derived params, CONFIG_DIGEST set |
| `EXECUTION-RECEIPT.md` | **THIS FILE** |

---

## 9. Tests Executed

| Test Suite | Result |
|------------|--------|
| pytest tests/ | 231 passed, 3 skipped |
| Preflight gates (G2-G8) | PASS (independent) |
| Corpus integrity | PASS |
| Leakage audit | PASS |
| Rights audit | PASS |
| Base vs merged eval | PASS (100 samples) |
| Adapter merge | PASS (5.4GB model) |
| Inference smoke test | PASS (8 prompts) |
| Run 002 config validation | PASS (Axolotl load_cfg successful) |

---

## 10. Training Status

**TRAINING_READY** — Run 002 fully configured, preregistered, artifacts persisted, config validated, tests passing.

### Dry-Validation Complete ✅

1. Corrected Run 002 config parses without error ✅
2. Logging/checkpoint configs syntactically valid for Axolotl v0.19.0 ✅
3. Output dir unique (`lora-out-nemotron-run002`) ✅
4. Seed parameter supported (seed=42 confirmed in parsed config) ✅

---

## 11. Exact Next Safe Action

**AWAITING OPERATOR AUTHORIZATION** to execute Run 002 on Delphi (GB10).

When authorized, execute:

```bash
ssh delphi "HF_HUB_ENABLE_HF_TRANSFER=1 tmux new-session -d -s run002 'export PATH=~/.local/bin:\$PATH && ~/.local/bin/axolotl train ~/Athanor/configs/nemotron-training-run002.yaml 2>&1 | tee ~/run002.log'"
```

Then monitor: `ssh delphi "tail -f ~/run002.log"`

---

**Run 001 is now an immutable experimental control.** All evidence preserved at commit `d8206d6`. Run 002 will be a controlled single-variable intervention with preregistered promotion criteria and full observability.