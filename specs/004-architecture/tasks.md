# Tasks — Package 4 (Core Complete)

Status: Core complete. Jev settle/quarantine deepened, AC catalog expanded (24 ACs), traceability full. This does not govern or activate.

## High-Level Tasks (from plan)
- T4-001: Inventory all existing AC/REQ/WF from 000-003 and root specs. **COMPLETE**
- T4-002: Define layered architecture (harvest/settle/retrieve/encoder/verification) with diagrams. **Core complete**
- T4-003: Build global acceptance catalog (expand workflow-local to system). **COMPLETE** (24 ACs including full jev quarantine/settle/doctor/balance/quality/receipts; 3145 atoms, min 5)
- T4-004: Complete traceability matrix (REQ → WF → AC → code/tests). **COMPLETE (full core population ~60 lines)**
- T4-005: Produce task decomposition and U* items for remaining work. **Core complete**
- T4-006: Define production verification strategy (receipts, audits, HERMENEUT). **Core complete**

## Detailed / Next Steps
- **Core Package 4 complete** (traceability full, acceptance expanded, jev ACs added, docs polished).
- T4-JEV-001: Integrate jev rerank into harvest pipeline (WF-002) for candidate classification. (Wired: post-filter in deepen_harvest.py + jev_classify.py; tested on new harvests)
- T4-JEV-002: Update quarantine/settle to use jev scores for quality gates (AC-JEV-*). (Deepened: jev_relevance + suggested_settle in quarantine rows; new settle.py for jev-rerank proposals on cleaned/atoms; wired into deepen_harvest.py post-filter; docs updated; custom validation only. AC-JEV-SETTLE-001 advanced.)
- T4-JEV-003: Run periodic jev-classified harvests to maintain >3000 high-quality PD atoms. (jev growth on families at 6 using longer excerpts: additional round added 8 via jev. Total 3192, min 6, 5 at exactly 6. All via jev rerank. Gold fixtures and docs current.)
- T4-JEV-004: Add jev usage to doctor output and receipts for harvest provenance. (COMPLETE; doctor now emits family_min, families_below_5, families_at_5 for balance visibility)
- Mermaid diagrams in architecture.md (present).
- Cross-link more DEC/C items (added in traceability for jev ACs).
- All Package 4 high-level tasks COMPLETE.

## Dependencies
- Prior Package 4 artifacts (spec, plan, architecture, acceptance, traceability).
- Full read of specs/000-003 and root files.

See spec.md for overall scope.

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base) + 2026-09-22 work.