# Tasks — Package 4 (Skeleton)

Status: Initial decomposition. This does not govern or activate.

## High-Level Tasks (from plan)
- T4-001: Inventory all existing AC/REQ/WF from 000-003 and root specs. **COMPLETE**
- T4-002: Define layered architecture (harvest/settle/retrieve/encoder/verification) with diagrams. **Core complete**
- T4-003: Build global acceptance catalog (expand workflow-local to system). **Core complete (jev harvest ACs added)**
- T4-004: Complete traceability matrix (REQ → WF → AC → code/tests). **COMPLETE (full core population ~60 lines)**
- T4-005: Produce task decomposition and U* items for remaining work. **Core complete**
- T4-006: Define production verification strategy (receipts, audits, HERMENEUT). **Core complete**

## Detailed / Next Steps
- **Core Package 4 complete** (traceability full, acceptance expanded, jev ACs added, docs polished).
- T4-JEV-001: Integrate jev rerank into harvest pipeline (WF-002) for candidate classification. (Wired: post-filter in deepen_harvest.py + jev_classify.py; tested on new harvests)
- T4-JEV-002: Update quarantine/settle to use jev scores for quality gates (AC-JEV-*). (Next)
- T4-JEV-003: Run periodic jev-classified harvests to maintain >3000 high-quality PD atoms. (Deeper balance continue: boosted jyotish_anchors to 4+, alchemy_spirit, solomonic, grimoire_other, astrology_west etc.; now min 4, 3 families <5, no families at 3; total 3110; jev rerank only)
- T4-JEV-004: Add jev usage to doctor output and receipts for harvest provenance. (Next)
- Add mermaid diagrams to architecture.md.
- Cross-link more DEC/C items.

## Dependencies
- Prior Package 4 artifacts (spec, plan, architecture, acceptance, traceability).
- Full read of specs/000-003 and root files.

See spec.md for overall scope.

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base) + 2026-09-22 work.