# Acceptance Catalog — Package 4 (Skeleton)

Status: Initial. Workflow-local ACs exist in prior specs; this is the global/system catalog target.

## Global ACs (examples, to be expanded)

| AC-ID | Description | Linked REQ/WF | Verification |
|-------|-------------|---------------|--------------|
| AC-001 | Retrieve never requires network or weights | REQ-008, WF-003 | pytest + doctor |
| AC-003 | Tokenless queries rejected cleanly; malformed rows give stable errors without tracebacks | REQ-009, REQ-013, WF-003 | test_retrieve.py, CLI probes (2026-09-22) |
| AC-011 | Packets include resolvable provenance (source_url, content_hash) and non-empty receipts | REQ-011 | build_packet + tests |
| AC-012 | Three-lens synthesis provided (historical/symbolic/operational) with epistemic labels | REQ-011 | _build_lens_synthesis test |
|| AC-009 | No efficacy claims; genuine historical text preserved | REQ-012 | synthesis + constitution review |
|| AC-001 (harvest) | Source review invariants (rights evidence, HOLD on unclear) | WF-001 | quarantine + admission tests |
|| AC-002 (harvest) | Normalize produces deduped envelopes, records outcomes | WF-002 | harvest scripts + receipts |
|| AC-011 (registry) | Unapproved proposals leave live registry unchanged | WF-011 | registry/ + tests |
|| AC-SIGN-001 | Valid synthetic signature verifies; altered rejects | WF-016 (signed-approval) | test_admission_approval.py |

## Production Verification Targets
- Receipts for every major operation (harvest, settle, retrieve, future train).
- Audit trail for all gated decisions.
- Offline-only enforcement for retrieve.
- HERMENEUT integration points for full lens readings.

See state-machines.md, contracts/ for state and contract ACs.

**Package 4 goal**: Turn workflow-local AC-00x into complete, testable global matrix.

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base) + 2026-09-22 work.