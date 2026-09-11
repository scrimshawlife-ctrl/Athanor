# Spec 000 — Athanor spine (SHADOW)

**Feature**: Tradition-aware corpus + encoder for ancient magical and mystical systems  
**Date**: 2026-09-10  
**Status**: SPECIFY locked — clarify C1–C12 · plan sealed · tasks filed · checklist · SHADOW (no implement/train)  
**Depends on**: constitution v1.0.0 I–XII  
**Lane**: SHADOW / advisory  
**Remote**: scrimshawlife-ctrl/Athanor  
**Clarify**: `clarify.md` (C1–C12 locked)  

## Intent

Build **Athanor**: an offline-capable knowledge furnace that ingests an **extensive** catalog of ancient and classical magical/mystical systems, indexes them under Historical · Symbolic · Operational lenses, and trains a small **encoder + retrieval** model so operators can query tradition atoms with epistemic honesty.

This is cultural technology and comparative hermetics — not a results-magic engine.

## Problem

1. Mystical corpora are scattered across PD scans, critical editions, and folklore wikis with weak provenance.
2. Chat LLMs blur tradition boundaries, invent citations, and either refuse or roleplay efficacy.
3. Existing Zero State lanes cover construction (Sigil-Forge), reading (HERMENEUT), and identity mint (Abraxas) — none own a **trainable tradition encoder + corpus SoT**.
4. “All systems” without a catalog and license gate becomes copyright theft or shallow skim.
5. Enochian and grimoire material is culturally central; excluding it from the **corpus** would cripple coverage. Including it as a **summon product** would violate Sigil-Forge / dual-use boundaries.

## Goals

- G1 Freeze a tradition **family registry** and atom schema (term / text / table / diagram-desc / correspondence).
- G2 Build an **extensive** PD-first harvest pipeline (Crawl4AI) with receipts and license tags.
- G3 Ship encode + retrieve offline on a frozen local slice before any Hub card.
- G4 Require three-lens packets on primary answers; hard-null efficacy fields.
- G5 Include Enochian, Goetic catalogs, and western grimoire PD as **historical corpus** with product anti-surface for authority-seal / summon UX.
- G6 Keep generative LM as optional later artifact; v0 name “Athanor” means encoder+corpus.
- G7 Operator gates on promote / train / publish (constitution VIII).

## Non-goals

- N1 Chatbot that claims spells work, spirits appear, or initiation is conferred.
- N2 Sigil-Forge authority-seal mint, Enochian tablet “activation” UX, or Goetic command playbooks framed as efficacious.
- N3 Dumping copyrighted modern occult paperbacks or closed initiatory PDFs into git.
- N4 Hard-import Abraxas / Hyperlex / Noema runtimes.
- N5 Phenomenal / sentience claims (constitution VI).
- N6 Auto Hub upload or paid Firecrawl without operator yes.
- N7 Medical, legal, or crisis advice dressed as mysticism.

## Users

- Operator (Danny) — wants a checkable tradition SoT + encoder on personal machine / Spark.
- HERMENEUT — consumes structured packets for three-lens readings.
- SCRIBE — files compact glossaries / taxonomies from settled atoms.
- Reviewer — needs license + dual-use answers before any public card.

## In scope (v0.1 specify)

- Constitution binding (already ratified v1.0.0).
- Tradition family registry (Wave 0–2 lists below).
- Atom + packet schemas (draft under `schemas/`).
- Harvest contract: source allowlist, license field, receipt shape, local SoT path.
- Encoder+retrieval product shape and eval gates (outline; stack in `plan.md`).
- Enochian corpus inclusion rules vs product anti-surface.
- Workflows section (mandatory).

## Out of scope (v0.1)

- Training run and weight files in git.
- Generative fine-tune card.
- Public Hub publish.
- Full OCR pipeline for every archive.org scan (may phase).
- Living-lineage oral material behind paywalls / oaths.

## Workflows

Assigned in this specify. Plan, tasks, and cloud-agent briefs **copy** this list; they do not invent another.

| Workflow | Owner | Role |
|----------|-------|------|
| [spec-kit](sand-workflow:spec-kit) | Boof / SCRIBE | Phase order; Workflows completeness |
| [crawl4ai-scrape](sand-workflow:crawl4ai-scrape) | Boof / INGEST-shaped ops | PD harvest default |
| [sigil-forge](sand-workflow:sigil-forge) | HERMENEUT | Boundary: construction vs corpus; authority-seal stay excluded from *forge* |
| [access-phenomenal-gate](sand-workflow:access-phenomenal-gate) | SHADOW | Card/ops language |
| [anti-slop-code](sand-workflow:anti-slop-code) | FORGE → cloud agent | Product code when implement opens |
| [production-systems](sand-workflow:production-systems) | FORGE → cloud agent | Day-one failure modes on ingest/serve |
| [google-developer-style](sand-workflow:google-developer-style) | SCRIBE / cloud agent | Docs, README, error strings |
| [prism-collective](sand-workflow:prism-collective) | Boof | Epistemic labels; specialist routing |

**CI (when implement opens):** reuse a minimal `validate` + docs workflow pattern from Hyperlex (`pytest` matrix 3.10–3.12, optional MkDocs). Do not invent a second CI philosophy. Name TBD in plan: `.github/workflows/validate.yml`.

**Specialists:** HERMENEUT (tradition map / lens QA) · SCRIBE (artifact file) · FORGE (plan/tasks) · ADVERSARY (dual-use pass before Hub) · SHADOW (honesty / phenomenal gate). No new bot.

## Tradition catalog — extensive corpus

Status of each row is **SPECULATIVE** until a source manifest row is OBSERVED with license tag. Waves are harvest priority, not moral rank.

### Wave 0 — core Western + Enochian spine (first harvest)

| Family id | Scope | PD / open targets (examples) | Notes |
|-----------|-------|------------------------------|-------|
| `hermetic` | Corpus Hermeticum, Asclepius, Emerald Tablet lineages | Mead, Scott, early translations on archive.org / sacred-texts | Three-lens required |
| `alchemy_lab` | Western laboratory alchemy | Ripley, Flamel attributions (careful), Norton, Maier emblems (desc) | Operational = lab metaphor history |
| `alchemy_spirit` | Spiritual / theosophical alchemy overlays | PD Boehme selections, early Rosicrucian PD | Separate from lab family |
| `enochian` | Dee/Kelley tables, Calls / Keys, Liber Loagaeth witnesses, Casaubon *True & Faithful Relation* | PD scans; Casaubon 1659; later Golden Dawn *historical* notes as secondary | **In corpus.** Product anti: no summon UX / authority-seal mint |
| `goetia_catalog` | Ars Goetia spirit lists as historical catalog | Mathers/Crowley PD editions where license clear; earlier MSS witnesses | Catalog + history, not command UX |
| `solomonic` | Greater/Lesser Key lineages, pentacles as diagrams | PD Mathers et al. where clear | Diagram-desc atoms |
| `grimoire_other` | Heptameron, Honorius, Abramelin (PD eds), Picatrix Latin/Arabic PD | archive.org critical where available | Picatrix may need language split |
| `kabbalah_pd` | Sefer Yetzirah, Bahir, early Zohar translations PD | Kaplan is modern — prefer older PD | Living-tradition care |
| `astrology_west` | Ptolemy *Tetrabiblos*, Lilly PD, Firmicus | Cross-link HERMENEUT natal tooling; do not overwrite Jyotish anchors |
| `tarot_history` | Early tarot history, PD decks descriptions, Waite PD text | Images: license per deck | History ≠ fortune UX |
| `runes_eddic` | Eddas, rune poem PD, historical futharks | Abraxas rune *ids* are separate mint | Cite, don’t mint |
| `neoplatonism` | Plotinus, Iamblichus, Proclus PD | Theurgy as historical practice description | |
| `mystery_cults` | Eleusis, Mithraic, Orphic *fragments* | Fragment honesty; NOT_COMPUTABLE when lost | |

### Wave 1 — Mediterranean, Near East, Africa-adjacent PD

| Family id | Scope | Notes |
|-----------|-------|-------|
| `egypt_magical` | PGM (Greek Magical Papyri) translations PD/open, Book of the Dead PD | PGM is central for “ancient magical systems” |
| `mesopotamia` | Maqlû, Šurpu, anti-witchcraft series; Enuma Elish as mythic | Prefer museum/CDLI open |
| `hebrew_bible_magical` | Reception history (not confessional theology dump) | Keep reception-scoped |
| `islamic_occult_pd` | PD Picatrix Arabic/Latin, select occult-scientific PD | Careful modern editions |
| `coptic_gnostic` | Nag Hammadi where translations license allows | |

### Wave 2 — South / East / New World PD shelves

| Family id | Scope | Notes |
|-----------|-------|-------|
| `jyotish_anchors` | Classical Jyotish PD roots; do not overwrite Danny natal registry | HERMENEUT already holds birth data elsewhere |
| `veda_upanishad_pd` | PD Muller et al. where clearly PD | Not a yoga app |
| `tantra_hist_pd` | Historical PD only; living-lineage care | |
| `iching_daoist` | Zhouyi PD, early Daoist alchemy (neidan) PD | |
| `buddhism_esoteric_pd` | Historical Vajrayana descriptions PD; no empowerments | |
| `shinto_onmyodo` | Historical Onmyōdō / yin-yang bureau materials PD | |
| `mesoamerica` | Codices descriptions, open museum notes | Image licenses |
| `andes_amazon` | Only clearly open ethnographic PD; no closed ayahuasca “recipes” as product | Dual-use X |

### Wave 3 — modern reception (secondary, labeled)

| Family id | Scope | Notes |
|-----------|-------|-------|
| `golden_dawn_hist` | Historical GD documents that are PD | Secondary to Wave 0 primaries |
| `theosophy_pd` | Blavatsky PD | High SPECULATIVE contamination risk — label hard |
| `chaos_spare_hist` | Spare / early chaos as *history of method* | Sigil-Forge owns construction |
| `folk_magic_pd` | PD folklore collectors (Folklore Society etc.) | Regional tags |

## Enochian rules (normative)

1. **Ingest** Dee diaries witnesses, angelical Calls, table reconstructions from PD sources, and reputable PD secondary histories.
2. **Atoms** may include: call text, table cell, letter name, historical date, scribal variant.
3. **Lenses:** Historical (Dee/Kelley context), Symbolic (structure of the Calls/tables), Operational (how *historical* practitioners arranged scrying sessions — descriptive).
4. **Forbidden product surfaces:** “generate Enochian conjuration to compel,” authority-seal PNG mint, “activate tablet” buttons, efficacy scores.
5. **Cross-link** Sigil-Forge for any glyph construction; Athanor stores text/structure only.

## Packet sketch (normative intent; schema in plan)

```text
athanor.packet.v0
  query
  hits[]: { atom_id, family_id, lens_scores?, excerpt, license, epistemic }
  synthesis: { historical, symbolic, operational }  # each labeled
  efficacy: null   # HARD NULL always
  receipts[]
```

## Success (v0.1 specify done when)

- [x] Constitution ratified in repo
- [x] This spec reviewed; Wave 0 source manifest started (`docs/source-manifest.md`)
- [x] Schemas drafted (packet + atom)
- [x] `plan.md` + `tasks.md` + `clarify.md` + `checklist.md` + dual-use + data-model
- [ ] Wave 0 manifest ≥8 OBSERVED URLs (T7 — in progress)
- [ ] Operator yes to open implement / first harvest

## Risks

| Risk | Mitigation |
|------|------------|
| Copyright contamination | License field required; PD-first; modern eds default deny |
| Efficacy creep in UX copy | Constitution I; ADVERSARY pass; `efficacy: null` |
| Shallow “all systems” skim | Extensive waves + per-family depth gates before train |
| Enochian moral panic / dual-use | Corpus yes / product anti-surface; no summon UX |
| Spark/train blocked | Same honesty as Hyperlex E2 — label blocked, don’t fake gates |

## Open questions (clarify)

1. Spark vs other box as train home (INFERRED: reuse Hyperlex Spark path).
2. Hub name reservation (`athanor-encoder-*`?).
3. Whether Goetic *images* of seals are ingested as described diagrams only vs image blobs (license).
4. Notion Operator Hub page under Abraxas/AAL 02 Operator — yes/no.
