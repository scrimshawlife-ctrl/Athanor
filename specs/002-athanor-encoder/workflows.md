# Workflows 002 — dataset, encoder, evaluation and handoff

Status: proposed specification. This does not govern or activate. Every mutation below remains conditional on existing operator authority and verified inputs.

## WF-004

| Field | Specification |
|---|---|
| Purpose | Apply reviewed settlement decisions with reproducible label provenance. |
| Actors | Proposal generator, label reviewer, operator, settlement executor. |
| Triggers | Batch submitted for review; application requested after exact-scope approval. |
| Preconditions | Atom revisions frozen; rights/label evidence available; proposed and reviewed labels distinguishable. |
| Inputs | Candidate IDs/hashes, proposed labels, exact reviewed target labels, decision IDs, approval reference and expected snapshot digest. |
| Happy path | Validate batch → present evidence and proposed labels → record reviewer decisions → verify approval scope → stage immutable decision records → validate joined outputs → commit the decision manifest → emit receipt. |
| Alternate/failure paths | No approval stays pending; changed hash is STALE; disputed labels or rights remain HOLD; malformed record is rejected; interrupted staging is RECOVERY_REQUIRED without a completed manifest. |
| State transitions | SM-002: PROPOSED → REVIEW_PENDING → APPROVED → APPLYING → APPLIED; staleness/rejection/recovery branches are explicit. |
| Terminal states | APPLIED, REJECTED, CANCELLED for the batch; individual HOLD decisions remain ineligible. |
| Side effects | Versioned decision records and derived views; any future corpus rewrite requires a separately specified migration. |
| Invariants | Heuristic KEEP alone cannot establish GOLD; approval matches exact revisions/labels; prior decisions and receipts remain immutable; reapplication is idempotent. |
| Permissions | Reviewers validate labels; the operator supplies existing promotion authority; executor verifies rather than invents approval. |
| Observability/audit | Batch/decision IDs, actor, reviewed fields, before/after manifest digests, approval reference, counts and failures. |
| Acceptance criteria | AC-004: Unapproved or stale batch cannot apply; repeating an applied batch adds no new decisions; HOLD cannot join into gold; interruption cannot expose a completed GOLD manifest. |
| Dependencies | REQ-014, REQ-015; WF-001/002; C-004 decisions/approval; C-005 snapshot; DEC-001/003. |
| Unresolved items | Existing 400-row review evidence is NOT_COMPUTABLE (DEC-001); authenticated approval verification mechanism remains DEC-003. |

## WF-005

| Field | Specification |
|---|---|
| Purpose | Freeze an eligible, reproducible dataset with leakage-resistant splits. |
| Actors | Dataset maintainer, reviewer, operator for promotion. |
| Triggers | Approved settlement set submitted for dataset preparation. |
| Preconditions | Immutable source/label revisions; declared rights scope, group rules, ratios, seed, tokenizer and registry versions. |
| Inputs | GOLD and KEEP decisions, atom references, pair/negative/wall fixtures, grouping configuration and count/balance requirements. |
| Happy path | Join by atom revision → exclude HOLD/DROP → separate gold/weak → group shared work/edition/source/hash components → assign whole groups deterministically → validate counts/leakage → measure token shares → freeze manifest. |
| Alternate/failure paths | Missing labels mask heads or exclude rows as declared; unresolved grouping blocks freeze; insufficient counts or imbalance records deficits; duplicate gold/weak memberships are rejected; operator must approve any scope reduction. |
| State transitions | SM-004: DRAFT → VALIDATING → FROZEN or REJECTED; changed inputs create a new snapshot. |
| Terminal states | FROZEN or REJECTED for the proposed revision. FROZEN does not mean train-authorized. |
| Side effects | Dataset views, exclusion report, split assignments and manifest; no changes to source corpus. |
| Invariants | No content/work group crosses splits; evaluation is gold-only; weak rows are not test truth; train token-share denominator uses the actual eligible sampled train slice. |
| Permissions | Dataset preparation within scope; promotion/train use remains operator-gated. |
| Observability/audit | Input digests, per-split/class/family counts, grouping version, exclusions, tokenizer revision, token totals and balance result. |
| Acceptance criteria | AC-005: Permuting row order yields identical assignments; same-work mirrors/hash duplicates cannot cross splits; HOLD is excluded; repeated freeze reproduces digest; unsupported family depth is explicitly NOT_COMPUTABLE. |
| Dependencies | REQ-015/016; WF-004; C-005 snapshot/trainrow; dataset-contract.md; DEC-002/005/006. |
| Unresolved items | Current eligible totals, duplicate groups and trained-token balance are NOT_COMPUTABLE; split configuration requires DEC-005. |

## WF-006

| Field | Specification |
|---|---|
| Purpose | Produce a rights-cleared, bounded export without reconstructing excluded works. |
| Actors | Export maintainer, rights reviewer, operator. |
| Triggers | Request for a public companion or approved local handoff subset. |
| Preconditions | Snapshot pinned; export audience/use declared; settlement eligibility and source-level rights reviewed. |
| Inputs | Snapshot, decision references, source/edition grouping, excerpt policy, permitted IDs and destination class. |
| Happy path | Verify eligibility and rights → choose excerpts → enforce per-row and source/work aggregate limits → reject forbidden complete content → validate metadata → emit export manifest and digest. |
| Alternate/failure paths | HOLD/DROP or unclear rights excludes row; missing reception is explicit null/reason and blocks targets requiring that label; short complete Call or reconstructable concatenation is excluded; malformed input fails the job with no complete-export claim. |
| State transitions | SM-003 job lifecycle; export artifact is VERIFIED_LOCAL only after all content and manifest checks. |
| Terminal states | SUCCEEDED with verified local artifact, FAILED, PARTIAL or CANCELLED; none implies PUBLISHED. |
| Side effects | Separate export files and receipt; no source rewrite or upload. |
| Invariants | 500 characters is an upper bound, not rights clearance; no efficacy column; no seal binaries; public excerpt membership is narrower than local corpus membership. |
| Permissions | Existing export/recipient scope required; Hub upload remains WF-010 with exact approval. |
| Observability/audit | Included/excluded IDs and reason codes, rights references, work-level totals, export hash and policy version. |
| Acceptance criteria | AC-006: Allowed license plus HOLD still rejects; full short work is not excused by length; multiple excerpts cannot bypass work policy; missing required rights reference prevents export. |
| Dependencies | REQ-017; WF-004/005; C-008 export; DEC-007/008. |
| Unresolved items | Actual work-level excerpt budget and jurisdiction evidence require DEC-007; current exporter does not implement these eligibility checks. |

## WF-007

| Field | Specification |
|---|---|
| Purpose | Validate encoder tooling behavior on synthetic fixtures before resource-consuming training. |
| Actors | Maintainer, CI runner, reviewer. |
| Triggers | Explicit implementation scope opened for dry-run tooling. |
| Preconditions | Synthetic inputs only; exact config; no model downloads, live corpus or publication side effects. |
| Inputs | Toy train rows, stub model outputs, invalid controls, pinned tool versions and offline policy. |
| Happy path | Validate configuration/contracts → exercise heads and absent-weight fallback → execute synthetic paths → validate receipts → report tooling result. |
| Alternate/failure paths | Invalid config or schema fails; attempted network is denied; unavailable backend returns documented fallback; missing head labels are masked and not fabricated. |
| State transitions | SM-003: VALIDATING → RUNNING → SUCCEEDED/FAILED/CANCELLED. |
| Terminal states | Tooling PASS or failed/cancelled attempt; learned-quality metrics remain NOT_COMPUTABLE. |
| Side effects | Temporary synthetic outputs and receipt only. |
| Invariants | Stub success cannot satisfy E1/E2/E3/E7 model/data evidence; no hidden weight download or live train. |
| Permissions | Implementation authorization is required by current scope; dry-run permission is distinct from real dataset training permission. |
| Observability/audit | Fixture/config hashes, tool versions, test outcomes, network-denial evidence, output schema versions. |
| Acceptance criteria | AC-007: Invalid inference and forced-family OOD controls fail; absent weights preserves lexical availability; synthetic PASS cannot mark trained metrics PASS. |
| Dependencies | REQ-018/023; C-007 encoder, C-009 run/eval; DEC-002/003. |
| Unresolved items | U11-U14 implementation is not completed by this documentation patch; backend choice remains DEC-002. |

## WF-008

| Field | Specification |
|---|---|
| Purpose | Produce an exact model artifact from an authorized frozen snapshot and config. |
| Actors | Operator, training executor. |
| Triggers | Verified training approval for a specified dataset/config/compute scope. |
| Preconditions | WF-005 frozen inputs; WF-007 tooling checks; approved base model/license; sufficient measured resources. |
| Inputs | Snapshot/config/tokenizer/model digests, head masks, seed, resource bounds and approval reference. |
| Happy path | Verify scope and resources → train within bounds → checkpoint → validate artifact readability → hash artifacts → emit training receipt. |
| Alternate/failure paths | Missing/stale approval or resources stays HOLD; OOM or numerical failure stops and records failure; interruption preserves a scoped checkpoint; resume rechecks input identity and approval. |
| State transitions | SM-003; HOLD → VALIDATING only after missing condition changes; RUNNING → PARTIAL/FAILED/CANCELLED or SUCCEEDED. |
| Terminal states | SUCCEEDED artifact production or failed/partial/cancelled attempt; quality and publication remain separate. |
| Side effects | Local checkpoints, weights and receipts within authorized output location. |
| Invariants | No automatic download/spend beyond scope; no weights in git; no claim of learned quality from training completion. |
| Permissions | Existing ALLOW_TRAIN/operator gate scoped to exact inputs; no implied Hub permission. |
| Observability/audit | Input/config/model hashes, environment, seed, resource usage, checkpoint lineage and output digests. |
| Acceptance criteria | AC-008: Wrong snapshot or stale approval blocks start/resume; failed run cannot emit success; artifact digest resolves exact evaluated bytes. |
| Dependencies | REQ-018; WF-005/007; C-004 approval; C-009 run; DEC-002/003/004. |
| Unresolved items | Resource availability and real training output remain NOT_COMPUTABLE. |

## WF-009

| Field | Specification |
|---|---|
| Purpose | Measure exact artifacts against frozen controls and content boundaries. |
| Actors | Evaluation executor, dataset reviewer, ADVERSARY. |
| Triggers | Local artifact or retrieval change submitted for a named gate assessment. |
| Preconditions | Frozen eval inputs/controls, valid reviewed labels, metric definitions/support and exact artifact identity. |
| Inputs | Model/runtime digest, snapshot, E0-E8 definitions, lexical control, wall prompts, historical-positive cases and review rubric. |
| Happy path | Validate evidence scope → run each applicable gate → capture actual outputs → compare to control/rubric → record per-gate status and reviewer evidence. |
| Alternate/failure paths | Missing weights/gold/control/support yields NOT_COMPUTABLE and blocks dependent claims; measured regression is FAIL; interrupted gate is incomplete; fixture existence cannot become behavior PASS. |
| State transitions | SM-003 for job; per-gate result uses PASS/FAIL/NOT_COMPUTABLE with reason and applicability. |
| Terminal states | Completed evaluation receipt or failed/partial attempt; only applicable measured PASS supports its named claim. |
| Side effects | Local evaluation outputs and receipts; no card promotion or publication. |
| Invariants | E7 refers to exact measured train slice/tokenizer; E6 historical positives and E4 harmful packaging are both tested; editing a card never changes evidence. |
| Permissions | Read approved local artifacts; human content review where rubric requires; no publish authority. |
| Observability/audit | Gate ID, metric value, support, control value, dataset/model/config hashes, actual-output references, reviewer and reasons. |
| Acceptance criteria | AC-009: Untrained E2 is NOT_COMPUTABLE with legacy FAIL retained as history; missing E6 blocks Hub; wall fixtures without executed outputs cannot pass; different model hash invalidates reuse. |
| Dependencies | REQ-006/012/019/020/023; WF-005/008 where learned metrics apply; C-009; eval-gates.md; DEC-001/006. |
| Unresolved items | Support minima/rubric choices remain DEC-006; independently verified E7 and learned results remain NOT_COMPUTABLE. |

## WF-010

| Field | Specification |
|---|---|
| Purpose | Publish only an exactly reviewed artifact and an evidence-consistent card. |
| Actors | Operator, ADVERSARY/reviewer, publishing executor. |
| Triggers | Publication request with exact destination and approved artifact manifest. |
| Preconditions | Required gates including E6 PASS; rights/export review; card/slug match; verifiable ALLOW_HUB/operator approval. |
| Inputs | Model/dataset/card hashes, destination, name-gate tier, eval/rights receipts and approval reference. |
| Happy path | Recheck all identities and gates → verify approval scope → upload approved bytes → read back destination identity/digests → record published receipt. |
| Alternate/failure paths | Missing gate, changed bytes/destination or stale approval blocks; partial upload records UPLOAD_PARTIAL and stops; overwrite/cleanup requires authority for that exact remediation. |
| State transitions | SM-005: LOCAL → REVIEW_PENDING → APPROVED → UPLOADING → PUBLISHED; failure/partial branches cannot claim completion. |
| Terminal states | PUBLISHED, REJECTED, CANCELLED or UPLOAD_FAILED for the attempt; UPLOAD_PARTIAL requires reconciliation. |
| Side effects | Only the approved remote artifact/version; no unrelated profile, collection or registry edits. |
| Invariants | Gold-slice balance alone never authorizes Hub; no synthetic quality claims; no implicit training approval. |
| Permissions | Existing explicit operator publication gate; approval references record consent rather than minting authority. |
| Observability/audit | Destination/version, approved/local/remote digests, gate evidence refs, actor, time and partial-upload details. |
| Acceptance criteria | AC-010: Missing E6 or changed card/model blocks; an upload timeout cannot claim PUBLISHED; readback must bind the exact approved bytes. |
| Dependencies | REQ-020/021; WF-006/009; C-004/C-009; existing constitution VIII. |
| Unresolved items | Exact future destination, artifact, authentication and approval are not supplied by this documentation task. |

## WF-012

| Field | Specification |
|---|---|
| Purpose | Transfer an authorized offline pack with reproducible verification and clear limits. |
| Actors | Operator/packager, named recipient, reviewer. |
| Triggers | Request to prepare and deliver a specific offline subset. |
| Preconditions | Recipient, data scope, transfer channel and intended use authorized; secrets and excluded corpus are absent. |
| Inputs | Eligible artifacts, receipts, licenses, scope/approval reference, manifest and reproduction instructions. |
| Happy path | Assemble allowlisted files → verify hashes/scope → include setup and limits → deliver on approved channel → recipient verifies manifest → record acknowledgment. |
| Alternate/failure paths | Missing file/hash mismatch rejects pack; privacy/rights violation excludes content; failed transfer remains undelivered; absent acknowledgment is delivery-unverified, not recipient success. |
| State transitions | SM-006: PREPARING → VERIFIED_LOCAL → DELIVERED → RECIPIENT_VERIFIED; invalid/failed/cancelled branches recorded. |
| Terminal states | RECIPIENT_VERIFIED, REJECTED or CANCELLED; DELIVERED alone is not verified use. |
| Side effects | Local pack and authorized transfer only; no public upload, corpus mutation or recipient training action. |
| Invariants | A local file path is not proof of transfer; pack delivery grants no additional authority; immutable checksums survive transfer. |
| Permissions | Existing operator approval for recipient and exact included data; no unsolicited messaging. |
| Observability/audit | Manifest hash, artifact hashes, destination class, transfer result and recipient verification reference without unnecessary personal data. |
| Acceptance criteria | AC-012: Tampered pack fails; unlisted sensitive file fails scope check; missing acknowledgment leaves recipient verification NOT_COMPUTABLE; reproduction uses pinned inputs. |
| Dependencies | REQ-005/022; WF-006 when excerpts are required; C-010 handoff; DEC-007. |
| Unresolved items | Historical Aaron/other offline packs have not been inspected or delivered by this task; recipient outcome remains NOT_COMPUTABLE. |

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base)
