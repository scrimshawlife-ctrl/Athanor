# Acceptance Catalog — Package 4 (Core Complete)

Status: Deeper Package 4 complete (eval/gold/harness ACs added). 30+ ACs. 3199 atoms, min 7/family, eval harness live. This does not govern or activate.

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
|||| AC-JEV-SETTLE-001 | Settle decisions use jev-classified quality scores + provenance; HOLD for low relevance or disputed PD. Quarantine emits jev_relevance + suggested_settle; settle.py provides jev-rerank proposals. | WF-004 | quarantine rows, settle.py, deepen_harvest integration (2026) |
|||| AC-JEV-QUARANTINE-001 | Quarantine classify() emits jev_relevance (from rerank) and suggested_settle (KEEP/HOLD/REVIEW); custom cues for validation only. | WF-013 | test_quarantine.py + quarantine.py |
|||| AC-JEV-SETTLE-002 | settle.py consumes quarantine output / atoms, runs jev rerank, emits proposals with decision + reason + score. | WF-004 | settle.py + doctor |
|||| AC-JEV-DOCTOR-001 | Doctor reports jev_classify, jev_quarantine (including suggested_settle), corpus metrics, balance. | WF-003 | entrypoint.py doctor + tests |
|||| AC-BALANCE-001 | After jev rounds: no family at 0; minimum family size >=5; all 30 families represented; tracked in doctor. | WF-002, WF-005 | doctor + corpus balance checks (3133 atoms, min 5) |
|||| AC-SETTLE-001 | Settle proposals (from settle.py or quarantine) include jev_relevance, suggested_settle, reason; operator review only (no auto-apply). | WF-004 | settle.py, docs/settle/README.md |
|||| AC-QUALITY-001 | Every added atom has full provenance (source_url, content_hash), lens_hints, epistemic OBSERVED, PD license; jev-classified. | WF-002 | quarantine + settle + corpus |
|||| AC-RECEIPT-001 | Major operations (harvest, settle, retrieve) produce receipts with jev scores / proposals where applicable. | WF-002, WF-004, WF-003 | deepen_harvest + settle.py + retrieve |
|||| AC-013 | Corpus size and quality tracked with jev-classified metrics; >3000 high-quality PD rows maintained (3133, min 5, 0 at 4) | WF-002, WF-005 | doctor + ANALYSIS_REPORT |
|||| AC-SIGN-002 | Signed admission rejects altered or untrusted scopes | WF-016 | test_admission_approval.py |

## Production Verification Targets
- Receipts for every major operation (harvest, settle, retrieve, future train).
- Audit trail for all gated decisions.
- Offline-only enforcement for retrieve.
- HERMENEUT integration points for full lens readings.

See state-machines.md, contracts/ for state and contract ACs.

**Package 4 goal**: Turn workflow-local AC-00x into complete, testable global matrix.

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base) + 2026-09-22 work.
|| AC-EVAL-001 | Retrieval eval harness runs on gold pairs and reports hit@K/MRR per family; used in CI smoke | WF-003 | scripts/eval_retrieve.py + tests |
|| AC-EVAL-002 | Gold pairs cover >=30 families with real atom_ids; hit rate @10 >=0.65 baseline | WF-003 | eval run + dataset-card |
|| AC-GOLD-003 | Gold correspondence pairs >=200; negatives >=100; maintained with jev for pair quality | WF-004 | fixtures counts + harness |
|| AC-PKG4-025 | Traceability matrix covers eval harness, gold expansion, doctor jev metrics | Package 4 | traceability.md |
|| AC-PKG4-026 | Dataset card updated for current corpus (3199 atoms, min 7/family, eval readiness 7.5/10) | WF-005 | docs/dataset-card.md |
|| AC-DOCS-001 | All specs/docs synced with current gold counts, harness, ACs, version bump | - | README, STATUS, traceability, dataset-card |
