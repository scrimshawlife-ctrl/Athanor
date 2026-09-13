# Data model — Athanor v0

Status: existing v0 sketch followed by the proposed completion model. This does not govern or activate. The current runtime schema is not changed by this file.

## Family
`family_id` (stable string) · wave (0–3) · title · notes · status (`shadow`|`active`)

## Atom
`atom_id` · `family_id` · `type` · `text` · `license` · `source_url` · `epistemic` · `content_hash` · optional `table` / `correspondence` / `diagram_desc` · `lens_hints`

## Receipt
`run_id` · `job_type` (`harvest`|`normalize`|`export`) · `started_at` · `source_urls[]` · `atom_count` · `engine` (`crawl4ai`) · `content_hash`

## Packet
See `schemas/athanor_packet.v0.schema.json`. Hard-null `efficacy`.

## Local SoT paths
- `~/.athanor/corpus/atoms.jsonl`
- `~/.athanor/receipts/*.json`
- Git holds schemas, registry, fixtures, specs — not full corpus dumps.

## Proposed storage and migration model

Use immutable raw-source blobs and a versioned atom envelope, plus append-only source/rights/settlement decisions. [C-001 through C-004](../contracts/README.md) define fields and [domain-model.md](domain-model.md) distinguishes identity from eligibility and epistemic claims.

Keys: atom revision = (atom_id, content_hash); source revision = (source_id, source_sha256); decision_id is unique and references one revision. A changed text hash creates a new revision; no prior GOLD or rights decision is silently carried forward. A decision can supersede another by explicit reference while retaining history. Family IDs resolve against the snapshot's registry hash. Missing work/edition identity remains null with a reason, not an invented title.

Local logical collections: sources, raw blobs, atom envelopes, rights decisions, settlement decisions, snapshots and receipts. Exact directories are implementation choices, not a new canonical home path. Full corpus/gold/quarantine remain local and excluded from git. The fixture corpus is synthetic/sanitized test data, not the source of truth.

Atomic visibility: stage and validate data before publishing an immutable manifest pointer. Readers use a pinned manifest, not a partially written JSONL file. Failed staging retains a recovery journal; reapplication by manifest digest is idempotent. Backups and content/metadata version maps precede any future approved migration. No migration or source rewrite occurs in this patch.

Hash semantics: exact UTF-8 artifact bytes, including newline conventions; source-byte digest and normalized-text digest are distinct fields/identities. Normalization algorithm/version is pinned. Do not recompute historical hashes after normalizing line endings or stripping chrome. Export/migration creates new derived hashes linked to originals. See C-003 for non-self-referential receipt hashing.

Retention, redaction and deletion handling are in [security-privacy-governance.md](security-privacy-governance.md); time periods remain DEC-007. If deletion is required, preserve permitted metadata/tombstone references and record unavailable evidence rather than silently changing historical completion claims.

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base)
