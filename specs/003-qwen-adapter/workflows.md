# Adapter workflows — proposed behavior, bounded current implementation

## WF-013

| Field | Specification |
|---|---|
| Purpose | Prepare source-bound instruction candidates, then review and freeze eligible examples. |
| Actors | Maintainer, label/rights reviewer, operator, dataset executor. |
| Triggers | Authorized candidate preparation request; separately reviewed freeze request. |
| Preconditions | Source text and identities available; declared use; review is distinct from generation. |
| Inputs | C-011 records, exact source hashes, task tags; future reviewed decisions and grouping configuration. |
| Happy path | Validate syntax/hashes/citations → project prompts/completions → independently review answers/rights → join exact decision revisions → group works transitively → freeze splits and receipt. |
| Alternate/failure paths | Malformed/stale/invented citation returns INVALID; unknown rights/entailment stays CANDIDATE_ONLY/HOLD; insufficient sources require explicit abstention; interrupted freeze cannot emit a completed manifest. |
| State transitions | SM-007 DRAFT → VALIDATING → CANDIDATE_ONLY/INVALID; future REVIEW_PENDING → REVIEWED → FROZEN. |
| Terminal states | INVALID or CANDIDATE_ONLY for current compiler; FROZEN/REJECTED for future reviewed freeze. |
| Side effects | Current compiler emits stdout only; future approved freeze writes immutable private outputs. |
| Invariants | No heuristic/generative label becomes gold; no known source/group/content crosses splits; metadata excluded from model features; candidate bytes are not approval. |
| Permissions | Candidate preparation within current scope; review/promotion under existing operator authority. |
| Observability/audit | Input/projection hashes, row IDs/splits, exact failure reason; future decision/exclusion/support receipts. |
| Acceptance criteria | AC-013: reordered rows produce identical projection; stale hashes/invented citations/declared leakage reject; all compiler successes stay CANDIDATE_ONLY. Semantic review and actual freeze require additional evidence. |
| Dependencies | RQ-003-02/03/04; WF-004/005/006; C-011; DEC-001/003/005/006/007. |
| Unresolved items | Source-group correctness, reviewed answers/rights and authenticated review joins remain NOT_COMPUTABLE. |

## WF-014

| Field | Specification |
|---|---|
| Purpose | Validate exact Qwen tooling, then execute only an approved bounded adapter pilot. |
| Actors | Maintainer, Spark operator, training executor. |
| Triggers | Local artifact/resource preflight request; separate exact-input training approval. |
| Preconditions | Model/processor/backend pinned; approved local artifacts; synthetic mask tests; frozen reviewed dataset before real run. |
| Inputs | Model lock, local file hashes, environment, resource limits, training config, frozen snapshot and approval reference. |
| Happy path | Inspect environment → verify artifact/class compatibility → check template/masks/truncation offline → check LoRA modules/resources → verify run approval → bounded pilot → checkpoint/hash receipt. |
| Alternate/failure paths | Missing artifacts/resources stays HOLD; unsupported kernels/empty supervised tokens fail preflight; OOM/nonfinite loss records FAILED/PARTIAL; resume requires identical relevant inputs and scope. |
| State transitions | SM-003 HOLD → VALIDATING → RUNNING → SUCCEEDED/FAILED/PARTIAL/CANCELLED. |
| Terminal states | Verified tooling or model artifact; never automatic quality PASS or publication. |
| Side effects | Preflight reads; approved pilot writes only scoped local checkpoints/receipts. No implicit downloads. |
| Invariants | No source/prompt/padding loss; no truncated empty answers; no fabricated compatibility; no implicit model publication; no weights in Git. |
| Permissions | Hardware inspection/local fixture checks within scope; real data/GPU training and new downloads require exact scope. |
| Observability/audit | Hardware/software versions, artifact/template/config hashes, supervised token counts, peak memory, loss failures and checkpoint lineage. |
| Acceptance criteria | AC-014: mismatch blocks start/resume; prompt/padding labels are -100; completions retain supervised tokens; failed run cannot emit success. |
| Dependencies | RQ-003-01/05/06; WF-007/008/013; C-009; model-lock.json. |
| Unresolved items | Local weights/template/backend/Spark compatibility, resource budgets and trainer are NOT_COMPUTABLE or unimplemented. |

## WF-015

| Field | Specification |
|---|---|
| Purpose | Compare the exact adapter against unmodified Qwen with identical retrieved evidence. |
| Actors | Evaluation executor, domain reviewer, ADVERSARY. |
| Triggers | Frozen protocol and approved local baseline/adapter artifacts available. |
| Preconditions | Independent held-out groups, support minima, decoding/config lock and per-task acceptance criteria selected before tuning. |
| Inputs | Base/adapter hashes, identical retrieval snapshots/prompts, reference answers, wall and historical-positive fixtures. |
| Happy path | Execute paired systems → retain actual outputs → score factual citation/answer support, format, abstention and task accuracy → review harmful and historical-positive behavior → record comparisons and limitations. |
| Alternate/failure paths | Missing output/support becomes NOT_COMPUTABLE; measured regression is FAIL; contaminated holdout invalidates claim; truncated/incomplete generation recorded, not discarded silently. |
| State transitions | SM-003 job plus PASS/FAIL/NOT_COMPUTABLE per applicable metric. |
| Terminal states | Completed comparison or explicit failed/partial evaluation, not publication. |
| Side effects | Private outputs and review receipts; no card/Hub promotion. |
| Invariants | Identical evidence and decoding policy for paired comparisons; separate task-stratum reporting; no selection on test set; model losses do not prove usefulness. |
| Permissions | Approved local evaluation only; later artifact/card publication requires existing operator gate. |
| Observability/audit | Input/output identities, per-task support, exact scorer/rubric, uncertainty, latency/memory, reviewers and exclusions. |
| Acceptance criteria | AC-015: no claims from absent outputs; fabricated citations count as errors; meaningful improvement and no unacceptable safety/historical-positive regression under preregistered thresholds. |
| Dependencies | RQ-003-07; WF-009/013/014; E4/E6/E8 intent retained but encoder E1/E2 are not automatically inherited. |
| Unresolved items | Numeric support/quality margins, rubric, real baseline/adapter outputs and evaluation harness remain unresolved. |
