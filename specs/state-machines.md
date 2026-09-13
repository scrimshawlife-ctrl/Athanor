# State machines — proposed behavior

Status: advisory contract. This does not govern or activate. These describe existing review/promotion boundaries and proposed execution behavior; they do not grant capabilities. A disallowed transition must fail with a reason and preserve the previous durable state.

## SM-001 — source review (WF-001)

| From | Event / guard | To | Durable effect |
|---|---|---|---|
| CANDIDATE | Reviewer starts on exact source revision | UNDER_REVIEW | Record source hash and intended use |
| UNDER_REVIEW | Rights evidence sufficient for declared use | CLEARED | Scoped decision and reviewer evidence |
| UNDER_REVIEW | Evidence absent/ambiguous or source unavailable | HOLD | Reason; no use authorization |
| UNDER_REVIEW | Excluded material or denied use | DENIED | Rejection evidence |
| HOLD | New evidence submitted | UNDER_REVIEW | New review event; old evidence retained |
| CLEARED/DENIED | Source or scope changes | CANDIDATE (new revision) | Prior decision remains immutable |

CLEARED and DENIED are terminal per revision. Expired or superseded clearance cannot be reused as current permission.

## SM-002 — reviewed application (WF-004, WF-011)

| From | Event / guard | To | Durable effect |
|---|---|---|---|
| PROPOSED | Exact manifest submitted | REVIEW_PENDING | Manifest hash and proposed decisions |
| REVIEW_PENDING | Existing operator authority approves exact scope | APPROVED | Verifiable approval reference |
| REVIEW_PENDING | Reviewer rejects | REJECTED | Reason; no application |
| APPROVED | Inputs, approval and target still match | APPLYING | Stage versioned outputs |
| APPROVED/APPLYING | Input hash or approved scope differs | STALE | Stop; do not expose completed output |
| APPLYING | Validation and commit of manifest succeeds | APPLIED | Output digest and receipt |
| APPLYING | Interruption or partial durable write | RECOVERY_REQUIRED | Recovery journal; incomplete output marker |
| RECOVERY_REQUIRED | Reconcile journal; same approval still valid | APPLYING | Idempotent resume |
| STALE | Revised manifest submitted | REVIEW_PENDING | New approval required |
| PROPOSED/REVIEW_PENDING/APPROVED/STALE/RECOVERY_REQUIRED | Authorized cancellation with staged-output reconciliation | CANCELLED | Preserve history; invalidate staged completion |

APPLIED, REJECTED and CANCELLED are terminal for a batch. Reapplication of the same applied digest returns the existing result. An atom's KEEP/HOLD/DROP/GOLD disposition is a separate versioned decision; it is not this batch state. GOLD changes neither historical truth nor license scope.

## SM-003 — bounded job (WF-002, WF-003, WF-006 through WF-009)

| From | Event / guard | To | Durable effect |
|---|---|---|---|
| PLANNED | Start requested | VALIDATING | Run ID, config/input references |
| VALIDATING | Missing authority, resource or prerequisite | HOLD | Missing condition; no execution |
| HOLD | Missing condition changes | VALIDATING | Recheck all inputs, not just one flag |
| VALIDATING | Valid inputs and required authority | RUNNING | Start time and execution identity |
| VALIDATING | Invalid inputs | FAILED | Typed validation reason |
| RUNNING | All required outputs verified | SUCCEEDED | Complete manifest and receipt |
| RUNNING | Some sources/steps finish, others fail | PARTIAL | Completed and failed items enumerated |
| RUNNING | No valid completion | FAILED | Error and recoverable outputs noted |
| PLANNED/VALIDATING/HOLD/RUNNING | Cancellation | CANCELLED | Checkpoints/staging reconciled |

SUCCEEDED/PARTIAL/FAILED/CANCELLED terminate an attempt. Retry uses a new run ID with parent_run_id and revalidates authority. Ingest partial success may preserve candidate rows; no partial job may masquerade as a complete frozen dataset or release. Retrieving NO_MATCH can be a successful job with unavailable claims. Metric PASS/FAIL/NOT_COMPUTABLE is independent of job success.

## SM-004 — snapshot (WF-005)

| From | Event / guard | To | Durable effect |
|---|---|---|---|
| DRAFT | Declared rows/config submitted | VALIDATING | Input manifest identity |
| VALIDATING | Eligibility, grouping, split and counts validate | FROZEN | Immutable manifest and digests |
| VALIDATING | Invalid/missing mandatory input | REJECTED | Exclusions and reasons |
| FROZEN | Any row, label, grouping, tokenizer or policy change | DRAFT (new ID) | Old snapshot remains usable under its original scope |

FROZEN/REJECTED terminate a snapshot revision. A frozen dataset with a measured failing balance gate may exist as a research artifact only if marked ineligible for the affected claim; it cannot be silently presented as train-ready. Train approval remains separate.

## SM-005 — publication (WF-010)

| From | Event / guard | To | Durable effect |
|---|---|---|---|
| LOCAL | Exact artifact/card/destination submitted | REVIEW_PENDING | Proposed release manifest |
| REVIEW_PENDING | Required gates, rights and operator approval valid | APPROVED | Bound approval and evidence |
| REVIEW_PENDING | Review fails | REJECTED | Reasons |
| APPROVED | Identities and permissions rechecked | UPLOADING | Upload attempt ID |
| UPLOADING | Remote bytes/version verified | PUBLISHED | Destination and remote digest evidence |
| UPLOADING | Incomplete remote state | UPLOAD_PARTIAL | Known remote objects and reconciliation needed |
| UPLOADING | Upload fails without partial remote artifact | UPLOAD_FAILED | Failure receipt |
| UPLOAD_PARTIAL | Exact remediation authorized and reconciled | REVIEW_PENDING | Revised attempt manifest |
| LOCAL/REVIEW_PENDING/APPROVED | Cancel before upload | CANCELLED | No upload |

PUBLISHED/REJECTED/UPLOAD_FAILED/CANCELLED terminate an attempt. Cancellation during upload requires recording any remote objects; it cannot erase the partial-state obligation. Deletion, overwrites and publication reversal require their own existing authority.

## SM-006 — offline handoff (WF-012)

PREPARING → VERIFIED_LOCAL only when manifest and scope checks pass; VERIFIED_LOCAL → DELIVERED only with transfer evidence; DELIVERED → RECIPIENT_VERIFIED only with recipient hash verification. Invalid scope/hash → REJECTED. Cancelled preparation/transfer → CANCELLED with any partial delivery recorded. Missing acknowledgment leaves DELIVERED, not RECIPIENT_VERIFIED. New artifact bytes require a new pack ID and verification.

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base)
