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
| WF-001 | Source/license review | 000 | - | scripts + quarantine | Historical |
| ... | Full matrix expansion in Package 4 | ... | ... | ... | TODO |

See contracts/README.md, workflows/README.md, 001/requirements.md, and state-machines.md for base definitions.

**Next Package 4 steps**: Expand to all REQ from 000-003, link to AC-*, add code coverage column.

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base) + 2026-09-22 work.