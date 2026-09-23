# Traceability Matrix — Package 4 (Skeleton)

| ID | Requirement | Workflow | Acceptance | Code/Test | Status |
|----|-------------|----------|------------|-----------|--------|
| REQ-008 | Corpus precedence (path > ATHANOR_CORPUS > default) | WF-003 | AC-003 | retrieve.py (default_corpus_path) | PARTIAL (shipped) |
| REQ-009 | Reject blank/tokenless queries | WF-003 | AC-003 | retrieve.py, test_retrieve.py | ADDRESSED 2026-09-22 |
| REQ-010 | Deterministic positive-score hits, stable tie, bounded k | WF-003 | AC-003 | retrieve.py (rank_atoms, _bm25) | PARTIAL (shipped) |
| REQ-011 | Labeled lenses + hard-null efficacy + provenance | WF-003 | AC-003 | retrieve.py (build_packet, _build_lens_synthesis) | ADDRESSED (basic) 2026-09-22 |
| REQ-012 | Genuine historical quotes, decline efficacy | WF-003 | AC-003, AC-009 | retrieve.py (synthesis), constitution | PARTIAL (stubs + design) |
| REQ-013 | Stable CLI errors for malformed | WF-003 | AC-003 | entrypoint.py, retrieve.py | ADDRESSED 2026-09-22 |
| WF-003 | Offline historical retrieval | - | AC-003 | src/athanor/retrieve.py + tests | LIVE + hardened |
| WF-001 | Source/license review | 000 | AC-001 | scripts + quarantine + admission | Historical |
| WF-002 | Harvest and normalize | 000 | AC-002 | scripts/shadow + quarantine | Historical |
| WF-004 | Review and apply settlement | 002 | - | apply_gold_p3a.py | Historical (P3a) |
| WF-005 | Freeze dataset and splits | 002 | - | adapter_freeze.py | Gated prep |
| WF-011 | Family registry proposal/review | 000 | AC-011 | registry/ + scripts | Historical |
| JRN-001 | Researcher wants historical context with checkable citations | WF-003 | - | retrieve packet + provenance | ADDRESSED (basic) |
| JRN-002 | Curator wants questionable source handled responsibly | WF-001,002,004 | - | quarantine + settle | Historical |
| AC-003 | Tokenless/malformed handling + lenses + provenance | REQ-009/011/013, WF-003 | - | retrieve + tests + entrypoint | ADDRESSED 2026-09-22 |
|| AC-001 / AC-002 | Harvest and source review invariants | WF-001/002 | - | quarantine + scripts | Historical |
|| AC-SIGN-001 | Valid synthetic signature verifies; altered rejects | signed-approval-workflow | - | test_admission_approval.py | Shipped |
|| JRN-003 | Dataset reviewer needs reproducible eligible slice | WF-005 | - | adapter_freeze + readiness | Gated prep |
|| JRN-004 | Training operator bounded experimental run | WF-007/008/009 | - | adapter_* + contracts | Gated |
|| ... | Full matrix expansion in Package 4 (pull all REQ/JRN/WF/AC from 000-003 + root) | ... | ... | ... | TODO |

See contracts/README.md, workflows/README.md, 001/requirements.md, and state-machines.md for base definitions.

**Next Package 4 steps**: Expand to all REQ from 000-003, link to AC-*, add code coverage column.

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base) + 2026-09-22 work.