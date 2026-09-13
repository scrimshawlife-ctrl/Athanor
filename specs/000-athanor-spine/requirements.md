# Requirements 000 — corpus and provenance

Status: proposed target behavior. This does not govern or activate. Each MUST is reviewable, not a claim about current scripts. Stable IDs are globally unique; owner roles already exist.

| ID | Requirement and rationale | Owner | Workflow / acceptance |
|---|---|---|---|
| REQ-001 | MUST separate successful source fetch from rights clearance; unknown rights remain HOLD for promotion/export. Prevent HTTP 200 becoming a license claim. | Operator/reviewer | WF-001 / AC-001 |
| REQ-002 | MUST ingest only reviewed source scope, normalize deterministically, preserve source/content digests and record partial failures. Duplicate content must not create silent repeated atoms. | Ingest executor | WF-002 / AC-002 |
| REQ-003 | MUST preserve existing corpus/registry promotion authority and require approval bound to the exact proposed change. No script may infer approval from its own output. | Operator | WF-011 / AC-011 |
| REQ-004 | MUST retain immutable provenance links from packet to atom revision, source, snapshot and receipt where applicable. Missing links make the affected claim NOT_COMPUTABLE. | Corpus maintainer | WF-002, WF-003 / AC-002, AC-003 |
| REQ-005 | MUST record attempts and terminal outcomes without secrets or default raw-query retention; receipts must validate their declared type. | Executor/reviewer | WF-002, WF-012 / AC-002, AC-012 |
| REQ-006 | MUST keep historical content separate from harmful or efficacious packaging, authority-seal minting, and phenomenal claims. | HERMENEUT/ADVERSARY | WF-003, WF-009 / AC-003, AC-009 |
| REQ-007 | MUST preserve the last valid frozen slice when an optional enricher or a new harvest fails. Fail-open ingest means partial source availability, not open rights or promotion gates. | Corpus maintainer | WF-002 / AC-002 |

Constraints: Python >=3.10; offline analysis; no peer hard imports; existing constitution I-XII. Operational timeouts, volume ceilings, supported scripts/languages, retention durations and rights jurisdictions must be selected explicitly per DEC-004/DEC-007 before making corresponding guarantees.

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base)
