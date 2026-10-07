# Roadmap — Athanor

Tradition-aware corpus and encoder for historical magical and mystical systems. Public-domain-first,
read through three lenses, and **no efficacy claims** — the corpus is the artifact.

Three words are used in one sense each, and they are not interchangeable:

- **shipped** — merged, and something runs it.
- **in progress** — being worked on now.
- **not planned** — deliberately not being built, with the reason given.

Anything that would require a claim this repository cannot evidence is listed as not planned rather than
deferred, because a roadmap that quietly carries an unmet promise is worse than a short one.

_Last reviewed: 2026-10-07._

## Shipped

- Corpus with provenance discipline and a PD-first sourcing rule.
- Three-lens encoder with the bias-corrected adapter **specified** (spec `003`).
- `adapter_preflight`: a read-only runtime inventory that never downloads, loads weights, or trains.
- `pair_id` generation repaired; every tracked module parses.

## In progress

- Nothing that requires weights. The repair work on the corpus and tooling.

## Next

- A runnable training environment, if one is ever provisioned — see "not planned" for what that would take.
- Bringing the sealed-run artifacts into `STATUS.md`, per this repository's own convention.

## Not planned

- **Claiming a trained adapter.** `specs/003-qwen-adapter/model-lock.json` records
  `"weight_downloaded": false` and `MODEL_REVISION_SELECTED_ENVIRONMENT_NOT_COMPUTABLE`; `adapter_preflight`
  reports the adapter `INVALID` and the machine `HOLD`. No weight file exists in this repository or on the
  machine this was last reviewed from, so no model result can be claimed.
- **Efficacy claims** of any kind.
