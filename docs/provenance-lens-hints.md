# Provenance & Lens Hints Flow to HERMENEUT/Abraxas

- Every atom carries source_url + content_hash (from jev-classified harvest).
- lens_hints: historical/symbolic (always true for PD); operational=0 (gated).
- Retrieve packets include synthesis (INFERRED) + receipts with jev_harvest.
- Cross-ref: src/athanor/retrieve.py build_packet, entrypoint.py doctor, scripts/shadow/athanor/jev_classify.py.
- For Abraxas: see AGENTS.md + cross-project docs.
