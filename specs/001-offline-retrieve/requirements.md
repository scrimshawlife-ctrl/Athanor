# Requirements 001 — offline retrieval

Status: proposed target contract extending shipped behavior. This does not govern or activate.

| ID | Requirement and rationale | Owner | Workflow / acceptance |
|---|---|---|---|
| REQ-008 | MUST resolve corpus precedence as explicit path > ATHANOR_CORPUS > documented home default; retrieval must not require network or weights. | Retrieve maintainer | WF-003 / AC-003 |
| REQ-009 | MUST reject blank/tokenless queries without arbitrary hits; distinguish invalid family, unavailable corpus and valid no-match. Unsupported language behavior must be explicit. | Retrieve maintainer | WF-003 / AC-003 |
| REQ-010 | MUST return deterministic positive-score hits with stable tie order, bounded k and excerpt semantics; source bytes remain unchanged. | Retrieve maintainer | WF-003 / AC-003 |
| REQ-011 | MUST return labeled lenses or explicit NOT_COMPUTABLE lens entries, hard-null efficacy and resolvable hit provenance; attached encoder blocks must independently validate. | HERMENEUT/maintainer | WF-003 / AC-003 |
| REQ-012 | MUST keep genuine historical quotations available while declining efficacy/compulsion packaging; a generic disclaimer alone is not behavioral proof. | ADVERSARY | WF-003, WF-009 / AC-003, AC-009 |
| REQ-013 | MUST provide stable library exceptions and CLI outcomes for malformed JSONL, non-object rows, missing fields and unavailable paths, without uncaught tracebacks in normal CLI errors. | Retrieve maintainer | WF-003 / AC-003 |

Current deviations: ASCII tokenizer produces tokenless inputs; ranker returns arbitrary zero-score hits for those inputs; malformed row errors are not all caught by CLI; packets omit source URL/hash and contain empty receipts; current lens objects are generic INFERRED stubs. These remain implementation tasks, not fixed by this document. Maximum k and expanded language/performance support depend on DEC-004.

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base)
