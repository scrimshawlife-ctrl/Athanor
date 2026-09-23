# Plan — Package 4 Architecture

Status: Skeleton. Advisory.

## Phases
1. Inventory existing (retrieve packet, synthesis, contracts, workflows).
2. Define global architecture (layers: harvest, settle, retrieve, (encoder gated), verification). → architecture.md
3. Acceptance catalog (expand workflow-local ACs to system level). → acceptance-catalog.md
4. Traceability matrix (link REQ → WF → AC → code/tests). → traceability.md
5. Task decomposition (U* items for remaining). → tasks.md
6. Verification strategy (receipts, audits, HERMENEUT integration).

## Dependencies
- All prior specs (000-003).
- Updated retrieve synthesis (basic HERMENEUT).
- Decision register (DEC-00x).

## Risks / NOT_COMPUTABLE
- Full encoder metrics (gated).
- Production scale numbers (DEC-004).

Provenance note as in spec.md.