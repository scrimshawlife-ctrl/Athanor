# Contributing

## The rules that matter here

- **Public-domain-first sourcing.** A source that cannot be shown to be PD is not admitted.
- **Three lenses, no efficacy claims.** The corpus is read through the lenses; whether any of it *works* is
  not a claim this repository makes, in either direction.
- **Never claim a model result.** No trained weights exist here: `specs/003-qwen-adapter/model-lock.json`
  records `weight_downloaded: false`, and `adapter_preflight` reports the adapter `INVALID`. Run
  `python -m athanor.adapter_preflight` before asserting anything about the runtime.
- **`pair_id` is derived, not invented.** It must stay byte-identical to `scripts/harvest_family.py`'s.
- **Nothing downloads, loads weights, or trains** without an explicit authorization flag.
