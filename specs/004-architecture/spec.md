# Architecture — Package 4

Status: Initial skeleton. This does not govern or activate.

Architecture, full acceptance catalog, traceability, task decomposition, and production verification (per specs/README.md). Builds on packages 1-3 (spine, retrieve live, encoder specify).

## Scope
- Full architecture for the retrieve + (gated) encoder system.
- Acceptance criteria catalog (global, not just workflow-local).
- Traceability matrix (requirements → workflows → tests → code).
- Task decomposition for remaining implementation.
- Verification strategy beyond current local pytest/ruff.

## Precedence
Follows constitution, domain model, requirements (000/001/002), journeys, workflows, state machines, contracts, data model, security/privacy/governance.

See root specs/ for shared artifacts.

## Key Deliverables (target)
- Architecture diagram(s) and description. (architecture.md started)
- Complete acceptance criteria (AC-*) catalog. (acceptance-catalog.md started)
- Traceability matrix (CSV or MD). (traceability.md expanded)
- Updated task lists with package 4 items.
- Production verification plan (including receipts, audits).

Current artifacts in this dir:
- spec.md
- plan.md
- architecture.md (draft)
- acceptance-catalog.md (skeleton)
- traceability.md (populated examples)
- tasks.md (decomposition skeleton)

## Current State (OBSERVED)
- Retrieve (Spec 001) live with recent hardening (tokenless rejection, provenance, clean errors).
- 219 tests.
- Basic three-lens synthesis wired (initial HERMENEUT).
- Gated paths remain fail-closed.

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base) + 2026-09-22 work.