# Athanor operator quickstart

Retrieve is live. Train and Hub stay gated.

## Install

```bash
pip install -e ".[dev,schema]"
athanor --version
athanor doctor
```

## Retrieve

Default corpus is `~/.athanor/corpus/atoms.jsonl` (local SoT, not in git). Override with `ATHANOR_CORPUS` or `--corpus`.

```bash
athanor retrieve "Enochian Calls" --k 3
athanor retrieve "Emerald Tablet" --family hermetic --k 5
# CI / no home corpus:
ATHANOR_CORPUS=fixtures/seed/atoms.jsonl athanor retrieve "Enochian Calls" --k 2
```

Output is `athanor.packet.v0` JSON. `efficacy` is always JSON `null`. Synthesis lenses are stubbed INFERRED until HERMENEUT wiring.

Retrieve excerpts run Spec 001 T5 `strip_chrome` (`src/athanor/chrome.py`). Sacred-texts SPA nav is stripped at retrieve time. Stored atoms are not rewritten.

## Operator notes

1. Read the [constitution](../.specify/memory/constitution.md), [Spec 000](../specs/000-athanor-spine/spec.md), and [Spec 001](../specs/001-offline-retrieve/spec.md).
2. Fill [`source-manifest.md`](source-manifest.md) before any harvest.
3. Crawl4AI 0.9.3 is the scrape default. No paid Firecrawl without an operator yes.
4. Settle: heuristic KEEP stays INFERRED until gold settle; chrome/stub DROP may be quarantined locally; Rowe/Achadian `/book/` essays HOLD. See [`settle/README.md`](settle/README.md).
5. Enochian text is welcome; summon UX is not. Never expect efficacy scores.
6. Do not commit corpus dumps, quarantine files, or train without an operator gate.
