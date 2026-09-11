# Contributing to Athanor

## Philosophy

Specs drive implementation. Spec Kit order: constitution → specify → plan → tasks → implement → converge.

## Rules

1. Epistemic labels: `OBSERVED` / `INFERRED` / `SPECULATIVE` / `NOT_COMPUTABLE`.
2. No efficacy claims. Packet field `efficacy` stays JSON `null`.
3. Enochian/Goetia welcome as **corpus**; no summon UX or authority-seal mint.
4. PD-first. Do not commit copyrighted dumps or full local SoT.
5. Crawl4AI default; paid Firecrawl needs operator yes.
6. Product code: anti-slop-code · production-systems · google-developer-style.
7. Access language only — no phenomenal / sentience claims.
8. Retrieve is live (`athanor retrieve`); train/Hub stay gated.

## PR process

- Link Spec 000 / Spec 001 task id when applicable.
- Keep local `ruff check src tests` and `pytest -q` green. GitHub Actions Validate may fail on account billing even when local checks pass.
- Update `STATUS.md` and `docs/status.md` together (twins) when a lane moves.
