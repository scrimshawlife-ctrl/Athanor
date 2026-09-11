# Ingest design note (000 T16 + 002 train view)

Harvest remains Crawl4AI → normalize → license tag → receipt → `~/.athanor/corpus/atoms.jsonl`.

Encoder does not scrape. Encoder reads settle exports.

```
atoms.jsonl
  → gold_settle (operator)
  → gold.jsonl + keep.jsonl
  → split by source_url / content_hash
  → optional sanitize_export (Hub)
  → train_encoder (Spark, gated)
```

Reuse `athanor.chrome.strip_chrome` on stored text only in a future harvest pass.
Refuse atoms without license and source_url.
Stamp reception_layer at harvest time for Wave 3 / proposed 3b.
Idempotent on content_hash. Receipts are append-only.
Paid Firecrawl still requires operator yes after Crawl4AI fails.
