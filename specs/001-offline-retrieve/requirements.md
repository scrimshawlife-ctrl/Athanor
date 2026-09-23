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

Current deviations status (2026-09-22): 
- Tokenless queries: **ADDRESSED** (retrieve() now raises ValueError for queries with no alphanumeric tokens; ranker guard retained).
- Malformed rows / CLI errors: **ADDRESSED** (load_atoms + from_mapping raise ValueError for missing keys; _cmd_retrieve catches ValueError/TypeError/KeyError/Exception and returns clean exit 2 + stderr, no tracebacks).
- Packets source URL/hash + receipts: **ADDRESSED** (Atom now carries source_url/content_hash; hits include them when present; receipts now carries minimal [{"type": "lexical-retrieve", "epistemic": "INFERRED"}]).
- Lens objects: still generic INFERRED stubs (by design until HERMENEUT wiring; not a deviation for retrieve core).
Maximum k and expanded language/performance support depend on DEC-004.

All core REQ-009/013/011 provenance items now satisfied for v0. See ANALYSIS_REPORT.md for verification.

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base)
