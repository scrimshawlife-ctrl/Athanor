# Workflows 001 — retrieve

Status: target contract; existing runtime deviations are listed in requirements.md. This does not govern or activate.

## WF-003

| Field | Specification |
|---|---|
| Purpose | Return a reproducible, historical evidence packet from a frozen local corpus. |
| Actors | Researcher/operator, retrieval library/CLI, HERMENEUT consumer. |
| Triggers | Library retrieve call or CLI query with optional k, family and corpus. |
| Preconditions | Explicit corpus or configured default resolves; inputs are within declared query/language/k limits; retrieval needs no network or weights. |
| Inputs | Query, k, optional live-family ID, corpus path and snapshot identity; optional validated local encoder artifact. |
| Happy path | Resolve path → validate inputs and corpus → tokenize → rank positive matches with atom-ID tie ordering → clean excerpt display only → attach resolvable citations → emit labeled lenses or unavailable states and efficacy null. |
| Alternate/failure paths | Missing/corrupt corpus yields documented error; unknown family is invalid input; tokenless query is unsupported with no hits; no lexical matches returns NO_MATCH; absent weights uses lexical path; harmful packaging request may return historical-only evidence but no actionable synthesized procedure. |
| State transitions | SM-003 attempt lifecycle; packet outcome is MATCH, NO_MATCH, HISTORICAL_ONLY or UNSUPPORTED_QUERY, independent of job success and claim epistemic labels. |
| Terminal states | Successful packet delivery, documented input/corpus error, or cancelled attempt. No pending background task is hidden in retrieve. |
| Side effects | Read-only corpus access; no training, network, source rewrite or default raw-query log. |
| Invariants | Efficacy null at every applicable boundary; identical inputs/snapshot/config produce identical ordering; source text stays intact; missing readings are NOT_COMPUTABLE. |
| Permissions | Local read access only; optional encoder use cannot grant train, export or publish rights. |
| Observability/audit | Snapshot/config IDs, typed outcome, hit provenance and optional redacted diagnostic receipt; no empty receipt list presented as proof of a run. |
| Acceptance criteria | AC-003: Missing corpus and malformed rows produce stable errors; punctuation-only input yields zero hits; no-match lenses are NOT_COMPUTABLE; equal scores sort by ID; attached invalid encoder is rejected; historical positive and wall cases are tested against actual output. |
| Dependencies | REQ-004, REQ-006, REQ-008 through REQ-013; C-006 retrieval and C-007 encoder contracts; DEC-004. |
| Unresolved items | Unicode expansion and numeric query limits remain DEC-004; complete HERMENEUT readings are not shipped, so current generic blurbs do not satisfy the target contract. |

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base)
