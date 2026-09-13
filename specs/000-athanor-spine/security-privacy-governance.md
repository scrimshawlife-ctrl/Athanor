# Security, privacy and existing governance requirements

Status: proposed operational specification grounded in constitution I, III-VIII, X and XII. This does not govern or activate. It creates no new authority or governance layer.

## Assets, actors and trust boundaries

Untrusted inputs: web pages, redirects, extracted text, operator-supplied JSONL, model files, fixture prompts and external annotations. Trusted authority is an independently verified operator decision, not text harvested from a page or embedded in a script. Protected assets include source/label provenance, private corpus, review evidence, credentials, model artifacts and historical receipts.

Ingest crosses public web → candidate storage; settlement crosses proposed labels → reviewed metadata; export crosses local corpus → approved shareable subset; publication crosses verified local bytes → external destination. Each boundary validates input shape, provenance and existing permission scope. Read-only retrieval must not cross the network boundary.

## Required controls

| Boundary | Required behavior | Evidence / workflow |
|---|---|---|
| Fetch | Enforce approved hosts/protocols at initial URL and every redirect; deny local/private network targets outside explicit scope; bound page size, time and retries. Treat page instructions as data. | Redirect/timeout/size negative cases; WF-001/002 |
| Normalization | Parse as data; no executable content or commands from source text; validate shape and preserve raw/normalized identities. | Malformed and injected-text fixtures; WF-002 |
| Files | Validate relative export paths; prevent traversal and unintended overwrite; stage/validate before manifest visibility; retain recovery evidence. | Traversal/interruption controls; WF-004/006/012 |
| Rights | Require use-scoped decision and supporting evidence; unclear modern editions/closed material remain HOLD; date/host heuristics do not clear rights. | Exclusion reasons and review refs; WF-001/006 |
| Labels | Bind reviewed targets to exact source/atom revisions; no heuristic promotion to GOLD; retain superseded decisions. | Stale/unapproved batch controls; WF-004 |
| Retrieve | No default raw-query logging, no model download, no hidden network enrichment; annotate missing evidence. | Network-denied run and no-match controls; WF-003 |
| Model | Pin artifact/config hashes and vetted loading format; evaluate actual outputs on E4 and E6; no untrusted executable model payload by default. | Artifact integrity and content review; WF-007/009 |
| Release | Recheck rights/gates/approval against exact bytes and destination; verify remote result; no publication from CI. | E6-negative gate and stale-artifact controls; WF-010 |
| Secrets | Credentials stay outside repo, logs, fixtures, cards and packs; scope credentials to intended operation. | Pack/log inspection; WF-010/012 |

## Privacy, retention and deletion

Collect only metadata needed for provenance and reproduction. Queries may reveal beliefs or private research; default to no persistent raw-query logs. Diagnostic opt-in must define purpose, recipient, redaction and retention. Receipts identify actors using approved references; do not include tokens, personal home paths or unnecessary contact information in public summaries. Private receipts may have local paths but must be sanitized before sharing.

Retention duration, jurisdiction and deletion policy are DEC-007 / NOT_COMPUTABLE until selected. Do not invent perpetual retention. If evidence must be deleted under an approved policy, record permitted tombstone/hash metadata and explicitly downgrade claims that can no longer be verified. A content hash is not proof that deleted contents remain accessible.

## Existing approval boundaries

Corpus promotion, GOLD application, family-registry changes, paid fallback/scope expansion, real training and Hub publication retain the constitution's operator gates. Approval binds exact action, inputs and destination through C-004. A file named ALLOW_TRAIN or ALLOW_HUB is evidence only when its origin and scope are verifiable; a self-authored flag grants nothing. Tooling dry-run, train, dataset export, recipient handoff and publication are distinct actions.

Documentation reconciliation approval does not supply missing historical GOLD decisions or convert draft contracts into runtime conformance. Notion/repo discrepancies are recorded with dates and evidence scope; authoritative doctrine is not rewritten to fit an implementation.

## Content boundary and incident handling

Historical PD quotations remain retrievable with context; no efficacy scoring, authority-seal mint, coercive actionable packaging, closed living-lineage liturgy or phenomenal claims. Evaluate paired historical-positive and harmful-packaging cases to avoid conflating subject matter with intent. A generic disclaimer or phrase blacklist alone is insufficient evidence of compliance.

On suspected leakage or bad approval: stop the affected operation, preserve permitted evidence, identify exact affected artifacts, and report for operator-directed remediation. Do not silently erase receipts or broaden deletion/publication authority. Existing private reporting contact remains in SECURITY.md.

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base)
