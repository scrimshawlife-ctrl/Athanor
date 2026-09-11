# Data model — Athanor v0

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
