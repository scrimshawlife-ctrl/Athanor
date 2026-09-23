# Training readiness: candidate integrity is not approval

Status: bounded safety remediation on top of main be1ebc9820a2b3a1c7f0596010ac08bab978086e. No training or publication authority is granted.

## Implemented

- The historical apply_gold_p3a.py entry point is retired. It exits 2 with HOLD without reading or writing the corpus, settle lists or receipts. Historical outputs are not rewritten. Heuristic KEEP cannot become reviewed GOLD through this helper.
- `python -m athanor.readiness --pack PATH` audits an existing Athanor candidate-preparation/1 directory, read-only. Install the local package or set PYTHONPATH=src before running from a checkout.
- The candidate auditor verifies the exact four file names, bytes, digests, row counts, nonempty unique feature/target ID correspondence, text-only feature boundaries, and basic target/split types. It rejects duplicate JSON keys, nonfinite numbers, unsafe file paths and symlinks.
- CI installs the contract format dependencies and executes the shared semantic regression suite, alongside runtime and candidate-audit tests.

Exit 1 means invalid/unreadable input. Exit 2 means candidate audit completed but training remains HOLD. This command has no READY path: candidate-preparation/1 carries no authenticated label, rights or operator approval chain. Editing allow_train, state or training_eligible cannot grant authority. The report calls such fields claims and independently verified eligible count remains NOT_COMPUTABLE. Extra local files are not included in the audit and this is not a complete handoff-directory allowlist inspection.

File integrity and unique row IDs do not establish label correctness, rights, corpus completeness, source/work deduplication, train/test independence or GPU compatibility. Nonempty text is not a cleanliness or tokenizer-fit test. The command does not freeze splits, mutate data, run models, download weights or publish.

## Remaining work and exact dependencies

The operator subsequently selected Qwen3.8-27B for the separate generative adapter lane: [Spec 003](../specs/003-qwen-adapter/spec.md). The T0/T1 encoder decisions below remain relevant only to Spec 002; do not block Qwen candidate preparation on choosing MiniLM. `python -m athanor.adapter_data --input PATH` validates and projects source-bound instruction candidates, never training-ready examples. Actual processor/backend/hardware checks and reviewed answers are still required.

| Step | Existing workflow / decision | Required outcome and next implementation |
|---|---|---|
| Reviewed labels | WF-004; DEC-001/003 | Supply per-target reviewer decisions bound to exact atom hashes and a selected trusted approval verification mechanism; implement a new settlement executor. Never restore the heuristic mutator. |
| Rights / reception | WF-005/006; DEC-007/008 | Reviewed use-specific rights and reception mappings; replace sanitize_export.py's license exclusions and unspecified fallback with decision joins and work-level protection. |
| Dataset freeze | WF-005; DEC-005 | Select ratios, seed and grouping rules; implement prepare_dataset.py with transitive work/edition/source/hash groups, gold-only evaluation, weak train-only membership and deterministic manifests. |
| Evaluation coverage | WF-009; DEC-006 | Choose support minima and uncertainty protocol; review thin-family examples, source-bound pairs and held-out queries. Do not fill missing labels with predictions. |
| Model and resources | WF-007/008; DEC-002/004 | Select immutable backbone/tokenizer revisions and supported tier/languages/resource envelope; then implement train_encoder.py/infer_encoder.py and backend dependencies. |
| Tooling | WF-007/009 | Synthetic offline tests, head masks, failure receipts, resume identity and missing-weight lexical fallback; implement the real metric/control harness, not constant PASS fixtures. |
| Real training | WF-008 | Frozen eligible snapshot + tooling evidence + selected resources + exact scoped operator approval. Bounded pilot before any scaling. |

Full architecture/acceptance/traceability remains packages 4–5. Do not check U11–U14 complete merely because candidate auditing is available. E1–E3 remain NOT_COMPUTABLE without exact trained artifacts and measured controls. E7 must measure the actual sampled train tokens, not historical gold balance. Hub remains separately gated.

## Validation mapping

### Explicit overlap evidence during candidate freeze

`python -m athanor.adapter_freeze --input CANDIDATES --config CONFIG --overlap-groups MAPPING`
accepts a JSON object mapping every candidate source ID to a nonblank overlap-group ID.
The mapping must cover exactly the source IDs present, not instruction-row IDs. It adds
grouping identities without replacing declared work/source/content identities; links
combine transitively. The receipt binds the mapping's canonical SHA256 and group count.
The command remains candidate-only with exit2, even when support minima pass.

The mapping is caller-supplied evidence, not authenticated authority. The stronger
binding path uses `--overlap-registry REGISTRY --overlap-registry-sha256 SHA256
--source-bindings BINDINGS` instead of `--overlap-groups`. All three arguments are
required together. BINDINGS maps every candidate source ID to a corpus row ID.
The registry maps corpus rows to overlap groups and allowed original/derivative text
hashes. The CLI and direct `freeze_with_registry` API verify the pinned registry bytes, complete source mapping and actual
candidate text hashes, then uses the additional grouping identities. The receipt
binds registry bytes, canonical registry contents and source bindings. Registry
authenticity and completeness still require review; choosing a digest is not approval.
The direct API accepts a registry file path, not an in-memory registry plus an
unverified digest. It loads and checks the bytes inside the receipt-producing call;
`project_overlap_groups` remains available for unpinned in-memory projection without
claiming a verified registry byte hash.
The private registry has been generated from verified evidence, but no real instruction
candidate set has been frozen through this path. Omitting both overlap options
preserves prior grouping behavior and does not prove absence of overlaps.
Do not replace work/edition grouping with passage overlap groups or treat a consistent
split as rights clearance. Explicit existing held-out splits still cannot be reassigned.

`tests/test_adapter_overlap.py` verifies combined/transitive work and overlap grouping,
determinism, source preservation, evidence hashes, missing/unknown mappings, malformed
JSON/null, existing holdouts and candidate-only CLI results. Synthetic tests do not
establish real-corpus completeness or training readiness.
`tests/test_adapter_overlap_binding.py` also covers direct-API rejection of fabricated
byte pins and stale pins after byte-only changes that leave decoded JSON unchanged.

REQ-014/015 and WF-004 invariant KEEP != GOLD: tests/test_gold_retired.py verifies HOLD, nonzero exit, unchanged corpus bytes and no new files. This is regression prevention, not completion of settlement.

WF-005 preflight: tests/test_readiness.py covers tampering, counterfeit metadata, duplicate/unmatched row IDs, target leakage into features, invalid labels/splits, empty text, forged authorization, and distinct INVALID/HOLD exits. Full WF-005 acceptance still requires a future frozen dataset builder.

C-005/C-009 semantics: specs/contracts/verify_review.py runs in CI. It validates contracts, not actual trained gate outcomes.

Provenance: Athanor main be1ebc9820a2b3a1c7f0596010ac08bab978086e, candidate-preparation/1 format and local synthetic regression checks. No Abraxas Loop or Sprint authority applies.

## Gated eval_train_readiness skeleton (Phase 5)
`scripts/eval_train_readiness.py` is a strict HOLD skeleton (exit 2 immediately with "EVAL-TRAIN-HARNESS: HOLD" message). It never enables training, imports no training code, checks no ALLOW_* flags, and references this document + eval-gates.md. Tested via `test_gated_train_eval_readiness_exits_hold` in test_retrieve.py. Mirrors the candidate auditor's fail-closed pattern. No activation path present.
