# Athanor specs

Status: SHADOW / advisory specification completion, packages 1-3. This does not govern or activate.

Read [START_HERE](../docs/START_HERE.md) first. The canonical authoring order is:

Constitution/doctrine → Domain model → Requirements → Journeys → Workflows → State machines → Contracts → Data model → Security/privacy/governance → Architecture → Acceptance criteria → Traceability → Tasks → Verification.

Spec Kit's constitution → specify → plan → tasks → implement → converge remains the delivery wrapper. Product workflows belong inside specify, after requirements/journeys and before architecture. Agent skill lists are execution guidance, not behavioral workflow specifications.

| Spec | Path | Status |
|------|------|--------|
| Constitution | `../.specify/memory/constitution.md` | v1.0.0 |
| 000 spine | `000-athanor-spine/` | Historical seal retained; canonical-method completion patch is advisory |
| 001 offline retrieve | `001-offline-retrieve/` | Shipped (PR #1) · T5 chrome (PR #2) |
| 002 encoder + Hub | `002-athanor-encoder/` | Historical P3a local seal reported; gold/eval proof qualifications below; train/Hub gated |

002 may propose Wave 3b family ids. Live `registry/families.yaml` does not change until operator yes.

## Precedence and evidence

The existing constitution controls doctrine and authority. Ratified clarification decisions constrain dependent specs. The linked Athanor Notion Hub supplies operator context; factual discrepancies are recorded in [reconciliation](../out/audit/spec-completion.latest.json), not silently resolved by whichever page is newer. No Abraxas canon or Loop 805 authority is imported into Athanor.

This package specifies target behavior; MUST means required by the proposed completion contract, not already implemented. Existing runtime schemas and code remain unchanged. Historical seals certify their original scope only. They do not certify the fourteen-stage method or current model quality. The [decision register](decisions.md) identifies remaining choices; absence of evidence is NOT_COMPUTABLE.

## Specification map

- [Domain model](000-athanor-spine/domain-model.md)
- Requirements: [000](000-athanor-spine/requirements.md), [001](001-offline-retrieve/requirements.md), [002](002-athanor-encoder/requirements.md)
- [Journeys](journeys.md) → [WF registry](workflows/README.md) → [state machines](state-machines.md)
- [Contracts](contracts/README.md) and [proposed wire schema](contracts/proposed.v1.schema.json)
- Data models: [000](000-athanor-spine/data-model.md), [002](002-athanor-encoder/data-model.md)
- [Security/privacy/governance](000-athanor-spine/security-privacy-governance.md)
- Architecture, full acceptance catalog, traceability, task decomposition, and production verification are packages 4-5, not claimed complete here. Workflow-local acceptance criteria are supplied now to make behavior reviewable.

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base)
