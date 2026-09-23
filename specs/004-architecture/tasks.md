# Tasks — Package 4 (Skeleton)

Status: Initial decomposition. This does not govern or activate.

## High-Level Tasks (from plan)
- T4-001: Inventory all existing AC/REQ/WF from 000-003 and root specs.
- T4-002: Define layered architecture (harvest/settle/retrieve/encoder/verification) with diagrams.
- T4-003: Build global acceptance catalog (expand workflow-local to system).
- T4-004: Complete traceability matrix (REQ → WF → AC → code/tests).
- T4-005: Produce task decomposition and U* items for remaining work.
- T4-006: Define production verification strategy (receipts, audits, HERMENEUT).

## Detailed / Next Steps
- Expand traceability to 50+ rows (pull from journeys.md, state-machines.md, contracts).
- Add mermaid/plantuml diagrams to architecture.md.
- Map all JRN-00x to ACs.
- Define ACs for gated paths (even if not implemented).
- Cross-link to 001/002/003 requirements.
- Add section for DEC-00x dependencies.
- T4-JEV-001: Integrate jev rerank into harvest pipeline (WF-002) for candidate classification.
- T4-JEV-002: Update quarantine/settle to use jev scores for quality gates (AC-JEV-*).
- T4-JEV-003: Run periodic jev-classified harvests to maintain >3000 high-quality PD atoms.
- T4-JEV-004: Add jev usage to doctor output and receipts for harvest provenance.

## Dependencies
- Prior Package 4 artifacts (spec, plan, architecture, acceptance, traceability).
- Full read of specs/000-003 and root files.

See spec.md for overall scope.

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base) + 2026-09-22 work.