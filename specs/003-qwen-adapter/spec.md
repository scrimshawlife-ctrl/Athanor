# Spec 003 — source-grounded Qwen adapter

Status: implementation preparation authorized by the operator's Qwen selection and continuation. No real-data training, download/spend, production activation or publication is authorized by this specification. Existing constitution remains unchanged. This is the separate generative artifact anticipated by constitution XI and Spec 002 T2, not a replacement for the encoder or lexical packet.

## Constitution and domain

Maintain historical/symbolic/operational distinctions, source citations, uncertainty and efficacy=null. Operational means historical arrangement, not supernatural instructions. Preserve living-tradition and harmful-intent boundaries. No authority seal or phenomenal claim. Spec 001 retrieval stays independently usable; Spec 002 T0/T1 gates do not certify this adapter.

Entities: immutable source revision; instruction candidate; reviewed instruction decision; grouped split snapshot; base/processor/template lock; adapter run; paired baseline evaluation. A valid candidate is not reviewed gold. A model repository revision is not a local artifact-integrity or hardware-compatibility receipt.

## Requirements

- RQ-003-01: Text-only Qwen3.8-27B adapter in a separate namespace; no image/video training in this scope.
- RQ-003-02: Bind every supplied source text to its SHA-256 and a reviewed work-group identity. Reject stale references and source/group/content identities crossing splits.
- RQ-003-03: Model-facing projection contains task/query/source text plus the fixed system instruction; answers are separate assistant completions. Never feed label/rights/approval sidecars into prompts.
- RQ-003-04: Review answer entailment, factual citations, uncertainty, rights and source-instruction handling before any row becomes eligible. Model-generated answers remain proposals, not gold.
- RQ-003-05: Pin model, processor, chat template, framework, kernels, LoRA modules, quantization and run configuration before training. No main/latest reference at runtime.
- RQ-003-06: Train only reviewed assistant completions with verified token masks. Reject empty supervised spans or truncation that removes citations/answer structure. Begin with packing disabled; enable only after boundary tests.
- RQ-003-07: Compare base+retrieval and adapter+identical retrieval using frozen evidence and held-out groups. Training loss and schema validity cannot substitute for quality or safety measurements.

## Journeys

JRN-007: Maintainer supplies source-bound candidate answers → deterministic validation/projection → human review and frozen split → exact pilot approval → paired baseline evaluation → separate publication decision. Invalid input returns an explicit failure; absent evidence remains HOLD, not retry-until-PASS.

## Workflow before architecture

See [WF-013 through WF-015](workflows.md). They refine existing WF-004/005/008/009 without changing authority.

## State machines and contracts

SM-007 candidate: DRAFT → VALIDATING → CANDIDATE_ONLY or INVALID. Future reviewed transitions: CANDIDATE_ONLY → REVIEW_PENDING → REVIEWED → FROZEN; stale source/answer decisions return to REVIEW_PENDING, rejected rows remain excluded. Current compiler implements only validation/projection, not review or freeze.

Run lifecycle reuses SM-003. Exact local weights are prerequisites for baseline or adapter evaluation, not proof of a successful run. Model preparation HOLD does not authorize a download.

C-011 instruction_candidate.v1 is documented by [data-contract.md](data-contract.md) and enforced for candidate syntax by src/athanor/adapter_data.py. The exported envelope's status is always CANDIDATE_ONLY and training_authorized=false. CLI writes JSON to stdout only; callers must not mistake exit 2 for training failure or success. INVALID exits 1. No trainer consumes this envelope automatically.

## Security, privacy and governance

Source text is untrusted data, never an executable instruction. Prompt separation is not sufficient prompt-injection protection: adversarial source fixtures and actual model-output review remain required. Never commit private instruction/source packs or raw copyrighted source content. Review training-use and sharing-use rights separately. Keep provenance sidecars out of model features. Reviewed decisions must bind source/answer hashes and scope through the existing selected verifier; a user-edited boolean is not authentication.

## Architecture and model selection

The operator selected Qwen3.8-27B, rather than Nemotron, for this adapter. [model-lock.json](model-lock.json) records the full upstream repository revision observed via git ls-remote. Model-card metadata describes a 27B causal vision-language model; this scope uses only text. No weights were downloaded. The processor is to resolve from the same revision; its local bytes/template still need hashing and inspection.

Flow: private instruction candidates → candidate validator/projection → independent review/rights decision join → approved grouped freeze → pinned processor and completion-mask tests → exact approved LoRA pilot → paired base/adapter evaluation. Existing lexical retrieval supplies the same context for both evaluated systems.

TRL/Transformers/PEFT is a candidate integration path, not a verified dependency lock. NeMo is an alternative framework; NVIDIA's Spark recipe demonstrating Qwen3-8B does not establish Qwen3.8-27B support. Do not copy its architecture-specific recipe or substitute a Flash-Next/MoE model. Exact supported model class, language-only load path, target modules, dtype and Spark kernels must be tested before selecting backend or quantization. LoRA versus QLoRA is unresolved until measured compatibility/memory evidence; no RAM fit is inferred from parameter count or inference success.

Use the pinned model's native template when the processor is available; do not transplant Hyperlex prompts or an unrelated model's template. Initial examples are single-turn prompt/completion with final JSON answers, not generated chain-of-thought targets. The proposed trainer uses completion-only loss after testing exact token boundaries. No training script is claimed implemented by candidate tooling.

## Acceptance, traceability and tasks

| Requirement | Workflow | Acceptance / implementation evidence |
|---|---|---|
| RQ-003-01/05 | WF-014 | Selected model/revision recorded; local processor/backend/resource tests remain NOT_COMPUTABLE |
| RQ-003-02/03 | WF-013 | Candidate tests reject stale hashes, invented citations and declared cross-split identities; permutation produces identical output |
| RQ-003-04 | WF-013 | Candidate component freeze and support report tested; trusted review/rights joins remain pending |
| RQ-003-06 | WF-014 | Synthetic completion-mask/truncation tests pass; actual pinned processor and trainer remain unverified |
| RQ-003-07 | WF-015 | Actual paired outputs, support and reviewer evidence required; not implemented |

- [x] A1 Record Qwen model-family decision and observed immutable repository revision.
- [x] A2 Implement candidate syntax/projection checks and synthetic negative controls.
- [ ] A3 Produce independently reviewed source-bound instruction answers and rights decisions.
- [ ] A4 Implement trusted review joins and deterministic work-level dataset freeze with support report.
- [ ] A5 Inspect Spark and local artifacts; choose tested backend/environment lock, modules and resource limits.
- [ ] A6 Implement processor/template mask tests and bounded trainer/checkpoint/resume behavior.
- [ ] A7 Freeze baseline protocol and execute paired evaluation after separate training approval.

Partial implementation for A4/A5/A6: [pipeline-preflight.md](pipeline-preflight.md).
Candidate splitting, token-mask primitives and runtime inventory do not complete
those tasks or waive their external evidence requirements.

Verification: existing pytest and semantic-contract CI plus new adapter candidate tests. Synthetic PASS proves tooling only. No full model training, adapter weights, learned metrics or Notion parity is claimed.

## Sources and unresolved decisions

- https://huggingface.co/Qwen/Qwen3.8-27B — model identity/type and published license claim.
- https://huggingface.co/docs/trl/v0.29.0/en/sft_trainer — prompt/completion masking capability, not an environment recommendation or compatibility proof.
- https://build.nvidia.com/spark/nemo-fine-tune/instructions — Spark fine-tuning examples; different model than this selection.

Unresolved: exact rights/review evidence; supported family/language/task coverage; train/validation/test group assignment; per-task support and acceptance thresholds; local tokenizer/template hashes; backend and quantization; real Spark resources; exact run approval. These remain NOT_COMPUTABLE, not default values.

Provenance: operator Qwen selection in this task, Athanor PR #9 base a58160c9cdf0c5cce7d18814a8b3c08e62c09797, upstream full revision in model-lock.json and linked primary documentation. No Abraxas Loop/Sprint authority applies.
