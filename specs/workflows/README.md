# Product workflow registry

Status: advisory target specification. This does not govern or activate. IDs are stable and never reused; superseding a workflow preserves its ID and records its revision.

| ID | Purpose | Owning specification | Journey |
|---|---|---|---|
| WF-001 | Source and license review | [000 workflows](../000-athanor-spine/workflows.md#wf-001) | JRN-002 |
| WF-002 | Harvest and normalize | [000 workflows](../000-athanor-spine/workflows.md#wf-002) | JRN-002 |
| WF-003 | Offline historical retrieval | [001 workflows](../001-offline-retrieve/workflows.md#wf-003) | JRN-001 |
| WF-004 | Review and apply settlement | [002 workflows](../002-athanor-encoder/workflows.md#wf-004) | JRN-002 |
| WF-005 | Freeze dataset and splits | [002 workflows](../002-athanor-encoder/workflows.md#wf-005) | JRN-003 |
| WF-006 | Sanitize export | [002 workflows](../002-athanor-encoder/workflows.md#wf-006) | JRN-005 |
| WF-007 | Synthetic encoder tooling check | [002 workflows](../002-athanor-encoder/workflows.md#wf-007) | JRN-004 |
| WF-008 | Authorized training | [002 workflows](../002-athanor-encoder/workflows.md#wf-008) | JRN-004 |
| WF-009 | Evaluate exact artifacts | [002 workflows](../002-athanor-encoder/workflows.md#wf-009) | JRN-004, JRN-005 |
| WF-010 | Reviewed publication | [002 workflows](../002-athanor-encoder/workflows.md#wf-010) | JRN-005 |
| WF-011 | Family registry proposal/review | [000 workflows](../000-athanor-spine/workflows.md#wf-011) | JRN-006 |
| WF-012 | Offline verification and handoff | [002 workflows](../002-athanor-encoder/workflows.md#wf-012) | JRN-006 |

Every workflow must explicitly state Purpose, Actors, Triggers, Preconditions, Inputs, Happy path, Alternate/failure paths, State transitions, Terminal states, Side effects, Invariants, Permissions, Observability/audit, Acceptance criteria, Dependencies, and Unresolved items. Requirements link to workflows; architecture and tasks reference them rather than inventing independent behavior. Existing agent/skill lists remain execution guidance.

WF-local AC-001 through AC-012 are initial acceptance bundles, not a claim of a completed global acceptance/test matrix. [State machines](../state-machines.md), [contracts](../contracts/README.md), and [decisions](../decisions.md) supply shared definitions.

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base)
