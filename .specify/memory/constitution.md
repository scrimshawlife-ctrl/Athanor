# Project Constitution: Athanor

**Version**: 1.0.0  
**Ratified**: 2026-09-10  
**Last Amended**: 2026-09-10  
**Status**: SHADOW / ADVISORY until operator promotion  
**Remote**: scrimshawlife-ctrl/Athanor  

This constitution gates every later Spec Kit artifact (`specify`, `plan`, `tasks`, `implement`, `converge`).

## Principles

### I. Furnace, not oracle
Athanor turns tradition into **structured, retrievable, labeled knowledge**. It does not claim magical efficacy, manifestation, or spiritual authority. Outputs are cultural-technology readings, never spells that “work.”

### II. Three lenses are mandatory
Every primary claim about a tradition atom must be readable under **Historical**, **Symbolic**, and **Operational** lenses (HERMENEUT contract). Operational means “how practitioners historically structured practice,” not “how to produce supernatural results.”

### III. Epistemic labels are first-class
Every claim is `OBSERVED`, `INFERRED`, `SPECULATIVE`, or `NOT_COMPUTABLE`. Weak harvest labels stay INFERRED until operator settle. Missing sources yield `NOT_COMPUTABLE`, never invented citations.

### IV. Public-domain first, extensive corpus
Wave harvests prefer public-domain and openly licensed primary/secondary sources. Copyrighted modern editions are out unless the operator explicitly clears them. **Extensive** means breadth across traditions and depth within each tradition’s PD shelf — not a shallow Wikipedia skim.

### V. Enochian and grimoire inclusion (corpus) ≠ authority-seal product
**Corpus:** Enochian (Dee/Kelley tables, Calls, related PD editions), Goetic catalogs as historical text, and other grimoire PD material are **in scope** for ingest, encode, and retrieve.  
**Product:** Athanor MUST NOT mint Sigil-Forge authority seals, Enochian/Goetic “summon” UX, or reconstructable ritual-command playbooks framed as efficacious. Sigil-Forge remains the construction lane and keeps its authority-seal exclusions for *glyph forging*. Cross-link, do not merge product surfaces.

### VI. Access ≠ phenomenal
Ops and model cards use **access** language only (Chalmers cut). No phenomenal, sentience, or consciousness claims for the model or for spirits/entities described in corpora.

### VII. Offline-first analyze, fail-open ingest
Baseline encode/retrieve MUST run offline on a frozen local corpus slice. Ingest failures degrade. Analyze never crashes because an optional enricher is missing.

### VIII. Human sovereignty on promotion
Corpus promote, weight publish, Hub upload, tradition-family registry adds, and any spend/scrape beyond Crawl4AI defaults require an operator gate. Specs do not self-promote.

### IX. Peer boundaries (no hard import)
- **Abraxas** — rune identity mint. Athanor may cite rune *ids* after Abraxas mint; MUST NOT mint Abraxas runes.
- **Hyperlex** — slang becoming-culture encoder. Sibling pattern; no Abraxas/Hyperlex hard import.
- **Sigil-Forge** — offline sigil construction. Proposal-only; no efficacy.
- **HERMENEUT** — tradition reading. Owns lens methodology; Athanor implements corpus+model.

### X. Dual-use and living-tradition care
Refuse harmful-intent packaging (harm to persons, non-consensual control). Treat living traditions with care: prefer historical/PD sources; do not scrape closed initiatory material; do not present living practice as a cheat sheet for coercion. Cite safety framing. No operational evasion playbooks.

### XI. Library-first, encoder-first
Ship as a Python package with tests before CLI sugar. Product trunk is an **encoder + retrieval** stack (Hyperlex-shaped). Generative fine-tune is a separate, operator-gated artifact — not the v0 name “Athanor.”

### XII. Crawl4AI default
Public-web harvest uses self-hosted Crawl4AI. Paid Firecrawl only with explicit operator yes after Crawl4AI fails.

## Constraints
- Python ≥ 3.10.
- No weight files or raw copyrighted dumps in git by default (local SoT / LFS / operator machine).
- Receipts for harvest runs; do not rewrite historical receipt hashes.
- Model cards must restate principles I, V, VI.

## Amendment
Operator amends this file, bumps version, restamps Last Amended. Dependent specs re-check I–XII.
