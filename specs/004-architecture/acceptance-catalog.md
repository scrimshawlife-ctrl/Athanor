# Acceptance Catalog — Package 4 (Skeleton)

Status: Core global catalog expanded (includes jev harvest/settle ACs). Workflow-local ACs from prior specs incorporated. This does not govern or activate.

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
||| AC-JEV-001 | All corpus classifying tasks (settle, quarantine, epistemic/family/gold balance, data quality) route through jev rerank (or equivalent) for evidence-bound decisions; custom logic only for validation | WF-013 (quarantine/settle) | jev rerank runs + tests (analysis 2026-09-22); future integration |
||| AC-JEV-HARVEST-001 | All new harvest candidates classified with jev rerank before quarantine; only HIGH relevance PD-primary chunks added as OBSERVED atoms | WF-002 | jev rerank + corpus doctor (this session) |
||| AC-JEV-SETTLE-001 | Settle decisions use jev-classified quality scores + provenance; HOLD for low relevance or disputed PD | WF-004 | quarantine + jev logs |
||| AC-013 | Corpus size and quality tracked with jev-classified metrics; >3000 high-quality PD rows maintained | WF-002, WF-005 | doctor + ANALYSIS_REPORT |
||| AC-SIGN-002 | Signed admission rejects altered or untrusted scopes | WF-016 | test_admission_approval.py |

## Production Verification Targets
- Receipts for every major operation (harvest, settle, retrieve, future train).
- Audit trail for all gated decisions.
- Offline-only enforcement for retrieve.
- HERMENEUT integration points for full lens readings.

See state-machines.md, contracts/ for state and contract ACs.

**Package 4 goal**: Turn workflow-local AC-00x into complete, testable global matrix.

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base) + 2026-09-22 work.