# Plan 000 — Athanor spine

**Status:** HARDENED (PROMETHEUS draft folded 2026-09-10 PT) · P2 retrieve **shipped** (PR #1) · harvest Wave 0 GO  
**Spec:** `spec.md` (Workflows SoT — copy only; do not invent)  
**Lane:** SHADOW / advisory · Harvest+retrieve open · **No train / no Hub** until operator yes  
**Remote:** scrimshawlife-ctrl/Athanor

Stack and how live here. What/why stay in `spec.md`. Constitution I–XII bind.

---

## Workflows

Product workflows are [WF-001, WF-002 and WF-011](workflows.md), with [WF-003](../001-offline-retrieve/workflows.md) for retrieval. The following historical skill list supports their execution; it does not substitute for purpose, triggers, failure paths and acceptance criteria. Architecture revision is package 4; this plan's old future-tense instructions are historical where contradicted by shipped Spec 001.

## Execution skills (copied from spec)

| Workflow | Owner | Role |
|----------|-------|------|
| [spec-kit](sand-workflow:spec-kit) | Boof / SCRIBE | Phase order; Workflows completeness |
| [crawl4ai-scrape](sand-workflow:crawl4ai-scrape) | Boof / INGEST-shaped ops | PD harvest default |
| [sigil-forge](sand-workflow:sigil-forge) | HERMENEUT | Boundary: construction vs corpus; authority-seal stay excluded from *forge* |
| [access-phenomenal-gate](sand-workflow:access-phenomenal-gate) | SHADOW | Card/ops language |
| [anti-slop-code](sand-workflow:anti-slop-code) | PROMETHEUS → cloud agent | Product code when implement opens |
| [production-systems](sand-workflow:production-systems) | PROMETHEUS → cloud agent | Day-one failure modes on ingest/serve |
| [google-developer-style](sand-workflow:google-developer-style) | SCRIBE / cloud agent | Docs, README, error strings |
| [prism-collective](sand-workflow:prism-collective) | Boof | Epistemic labels; specialist routing |

**CI (when implement opens):** `.github/workflows/validate.yml` — Hyperlex-shaped `pytest` matrix Python 3.10–3.12 + optional MkDocs. Do not invent a second CI philosophy.

**Specialists:** HERMENEUT · SCRIBE · PROMETHEUS · ADVERSARY · SHADOW. **No new bot.**

**Cloud-agent briefs (when implement opens):** copy this Workflows table; require **active node + exit condition** (Procedural Graphs steal — topology evolves only on validation).

---

## CONTRACT

Offline-capable **encoder + retrieval** over an extensive PD-first tradition corpus. Three-lens packets. `efficacy: null` always. Enochian/Goetic **in corpus**; **no** summon / authority-seal product surface.

---

## COMPONENTS

| ID | Component | Notes |
|----|-----------|-------|
| C1 | Local SoT | `~/.athanor/corpus/` JSONL atoms + receipts (Hyperlex park pattern). Not full dumps in git. |
| C2 | Family registry | `family_id` from Wave 0–3; atom types `text` \| `table` \| `correspondence` \| `diagram_desc` |
| C3 | Ingest | Crawl4AI allowlist → normalize → license tag → receipt → candidate store |
| C4 | Index | Lexical **required**; embedding **optional** (see stack defaults) |
| C5 | Encoder | T0/T1 small encoder + family heads; Spark path; name `athanor-encoder-*` only after eval gate |
| C6 | Packet | `schemas/athanor_packet.v0.schema.json` — hard-null `efficacy` |
| C7 | Boundaries | Sigil-Forge construction; Abraxas rune cite-not-mint; Hyperlex sibling no hard-import |

---

## DATA FLOW

```
allowlisted URL
  → crawl4ai-scrape
  → normalize + license tag
  → receipt (immutable hash)
  → candidate atom store (~/.athanor)
  → frozen slice
  → lexical (+ optional embed) index
  → retrieve
  → athanor.packet.v0 (three-lens synthesis, efficacy null)
```

Fail-open ingest (constitution VII). Analyze never requires live net.

---

## STACK DEFAULTS (resolved — INFERRED until implement yes)

| Decision | Default | Label |
|----------|---------|-------|
| Embedding backend | **stdlib-first lexical** (BM25/TF-IDF class) on freeze; optional `sentence-transformers` only behind operator flag | INFERRED (simplest offline) |
| Encoder ceilings | Mirror Hyperlex T0/T1 param bands when implement opens; do not invent a third scale ladder | INFERRED |
| CI workflow file | `.github/workflows/validate.yml` | OBSERVED (spec already named) |
| Train home | Spark / operator box — same honesty as Hyperlex E2 if blocked | SPECULATIVE until clarify |
| Hub name | `athanor-encoder-*` reserved in docs only; no upload | INFERRED |

---

## BOUNDARIES / NON-GOALS (this plan)

- No train run, weight files in git, Hub publish, or generative LM card in v0.1
- No Firecrawl paid unless Danny yes after Crawl4AI fails
- No Sigil-Forge authority-seal / summon UX / efficacy scores
- No Abraxas/Hyperlex/Noema hard import
- No new specialist bot

---

## FAILURE MODES

| Failure | Day-one behavior |
|---------|------------------|
| License unclear | Atom stays candidate; no promote |
| Crawl4AI miss | Receipt FAILED; no invented excerpt |
| Missing PD shelf | Family `NOT_COMPUTABLE` depth; no fake coverage |
| Efficacy creep in copy | ADVERSARY + constitution I; schema rejects non-null efficacy |
| Spark blocked | Label blocked; do not fake eval green |
| Enochian product slip | Anti-surface checklist in tasks; fail CI string scan when implement opens |

---

## PHASES (active node → exit)

| Phase | Active node | Exit condition (validation) |
|-------|-------------|-----------------------------|
| **P0 Manifest** | Wave 0 source rows OBSERVED | `docs/source-manifest.md` has ≥1 licensed URL per Wave 0 family **or** explicit NOT_COMPUTABLE |
| **P1 Ingest** | Crawl4AI tap + receipts | One dry-run receipt chain on allowlisted PD URL; license field required |
| **P2 Retrieve** | Offline lexical retrieve on seed slice | Query → packet validates against `athanor.packet.v0`; `efficacy === null` |
| **P3 Encoder shadow** | Train scripts only (no weights in git) | Script dry-run on toy slice; no Hub name claim |
| **P4 Eval + dual-use** | Eval gates + ADVERSARY | Dual-use PASS recorded; three-lens present on fixture answers |
| **P5 Train gate** | Operator yes | Explicit Danny yes before Spark train; else HOLD |

Topology does **not** jump P0→P5 without exit evidence (Procedural Graphs).

---

## TESTS (when implement opens)

- Schema: packet with non-null `efficacy` **rejected**
- Ingest: receipt hash stable; re-run does not rewrite history
- Retrieve: offline on frozen slice; missing enricher does not crash
- Boundary: string/fixture tests that summon / authority-seal UX paths are absent
- Workflows: `tasks.md` / PR body copy the Workflows table above

---

## MINIMUM IMPLEMENTATION (first operator yes)

1. Package skeleton + `validate.yml` + schemas already in repo  
2. P0 manifest file + P1 ingest CLI shape (Crawl4AI)  
3. P2 offline retrieve returning valid packets  

**Not** in minimum: encoder train, Hub, generative card.

---

## FUTURE EXPANSION

- Optional embedding backend  
- T0/T1 encoder on Spark  
- Wave 1–3 harvest after Wave 0 depth gate  
- Generative fine-tune as **separate** gated artifact  

---

## OPEN CLARIFY (from spec — do not invent answers)

1. Spark vs other box as train home  
2. Hub name reservation confirm  
3. Goetic seal images: diagram_desc only vs blobs  
4. Notion Operator Hub page yes/no  

---

## Historical next moves (superseded by completion package sequence)

1. Operator review this plan + `tasks.md`  
2. Start P0 manifest (ops) — still no train  
3. Hold implement until Danny yes on first harvest / code  

Current next work: [specification completion map](../README.md) and [decision register](../decisions.md). This does not govern or activate.

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base)
