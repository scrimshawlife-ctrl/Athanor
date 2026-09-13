# Workflows 000 — source, harvest and registry

Status: proposed behavior under existing constitution I-XII. This does not govern or activate.

## WF-001

| Field | Specification |
|---|---|
| Purpose | Establish source identity and a use-scoped rights decision before promotion or export. |
| Actors | Curator, source reviewer, operator. |
| Triggers | Candidate source submitted or an existing source/edition changes. |
| Preconditions | Candidate URL and intended use recorded; no assumption that a host-wide license covers every edition. |
| Inputs | Source URL, work/edition metadata when available, fetch digest, rights evidence, intended use, existing decision revision. |
| Happy path | Observe source → identify edition → inspect rights evidence → record CLEARED scope and reviewer → hand approved source to WF-002. |
| Alternate/failure paths | Unreachable source records unavailable observation; mixed or unclear rights yields HOLD; prohibited material yields DENIED; changed content invalidates old scope pending review. |
| State transitions | SM-001: CANDIDATE → UNDER_REVIEW → CLEARED, HOLD or DENIED; changed content creates a new review revision. |
| Terminal states | CLEARED or DENIED for a review revision; HOLD is unresolved and cannot authorize use. |
| Side effects | Source and license-decision records only; no automatic corpus promotion. |
| Invariants | HTTP 200 is not license evidence; ancient work age is not edition clearance; unknown facts stay NOT_COMPUTABLE. |
| Permissions | Reviewer records evidence; existing operator gate controls promotion and additional scrape/spend scope. |
| Observability/audit | Decision ID, source/content digest, intended use, evidence references, actor, timestamp and reason. |
| Acceptance criteria | AC-001: Given HTTP success without rights evidence, decision remains HOLD; given evidence for one edition, another edition is not cleared; revised bytes require renewed review. |
| Dependencies | REQ-001; C-001 source/license contract; existing source manifest; DEC-007. |
| Unresolved items | Specific export jurisdictions and legacy rights evidence: DEC-007 / NOT_COMPUTABLE where absent. |

## WF-002

| Field | Specification |
|---|---|
| Purpose | Produce provenance-preserving candidate atoms while containing source failures. |
| Actors | Ingest executor, curator, operator when existing gates require approval. |
| Triggers | Authorized harvest request against reviewed source scope. |
| Preconditions | Allowed destinations and use scope checked; timeout/size/retry bounds supplied; last valid frozen slice remains available. |
| Inputs | WF-001 decisions, source list, engine/normalizer revisions, existing hashes, run config and approval reference if required. |
| Happy path | Verify scope → fetch bounded pages → normalize → calculate hashes → deduplicate → validate candidate envelopes → record outcomes → hand candidates to WF-004. |
| Alternate/failure paths | Timeout/404/parser failure records per-source reason and continues eligible sources; unauthorized redirect or uncertain rights is held; duplicates record skips; interruption preserves completed candidates and a PARTIAL or CANCELLED receipt. |
| State transitions | SM-003: PLANNED → VALIDATING → RUNNING → SUCCEEDED or PARTIAL/FAILED/CANCELLED; candidates do not become GOLD. |
| Terminal states | SUCCEEDED, PARTIAL, FAILED, CANCELLED for the attempt. A retry has a new run ID linked to its parent. |
| Side effects | Candidate storage and receipts; no rewrite of existing frozen snapshots or historical receipt hashes. |
| Invariants | Every candidate has source/digest; identical content is not duplicated; failure cannot relax rights, authority or promotion checks. |
| Permissions | Crawl4AI within approved scope; paid fallback, additional scope and promotion retain existing operator gates. |
| Observability/audit | Attempted URLs, engine/config revision, success/failure/duplicate counts, input/output digests and candidate manifest. Secrets are excluded. |
| Acceptance criteria | AC-002: A mixed success/timeout batch records both outcomes; rerunning identical source bytes adds no duplicates; disallowed redirect is held; previous frozen retrieve remains usable. |
| Dependencies | REQ-002, REQ-004, REQ-005, REQ-007; WF-001; C-002 atom and C-003 receipt contracts. |
| Unresolved items | Production timeout/volume/retry values need measured selection under DEC-004; no capacity claim is made. |

## WF-011

| Field | Specification |
|---|---|
| Purpose | Review a family addition or revision without silently changing live classification meaning. |
| Actors | Proposer, tradition reviewer, operator, registry maintainer. |
| Triggers | New family proposal or documented correction to an existing family. |
| Preconditions | Current registry revision pinned; proposal explains scope, overlap, sources and migration effects. |
| Inputs | Proposed ID/title/wave, inclusion/exclusion examples, evidence references, affected labels and exact proposed diff. |
| Happy path | Check unique ID and semantic overlap → reviewer examines examples → operator approves exact diff → maintainer applies versioned registry change → record downstream revalidation needs. |
| Alternate/failure paths | Duplicate ID, unclear distinction or insufficient sources returns proposal for revision; missing approval remains pending; changed diff makes approval stale. |
| State transitions | SM-002 proposal/review/apply lifecycle, scoped to registry revision rather than atom labels. |
| Terminal states | APPLIED, REJECTED, CANCELLED; STALE and REVIEW_PENDING cannot alter the live registry. |
| Side effects | Only the explicitly approved registry revision and an audit receipt; no retroactive silent relabeling. |
| Invariants | Family IDs never reused; proposed Wave 3b entries remain proposals until approved; registry existence is not comprehensive coverage. |
| Permissions | Constitution VIII's operator gate remains mandatory; reviewers and agents cannot self-promote. |
| Observability/audit | Base/new registry hashes, proposal ID, approval evidence, changed IDs and affected dataset/model references. |
| Acceptance criteria | AC-011: Unapproved proposals leave live registry unchanged; a changed diff rejects old approval; pinned older snapshots retain their original family definitions. |
| Dependencies | REQ-003; C-004 approval scope; C-005 snapshot provenance; existing registry/families.yaml. |
| Unresolved items | Existing Wave 3b proposals remain unresolved; this workflow neither approves them nor creates new governance. |

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base)
