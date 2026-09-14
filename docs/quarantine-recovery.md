# Private quarantine recovery

Preparation-only support for WF-013 in Spec 003. No source relabeling, gold
promotion, split freeze, training, Hub publication or runtime activation occurs.

```sh
python -m athanor.quarantine --prepared /private/prepared --pack /private/source.zip --output /private/new-recovery
python -m athanor.quarantine --prepared /private/prepared --pack /private/source.zip --output /private/new-recovery --verify
```

Omit `--output` for a read-only summary. Exit 2 means candidate HOLD, not approval;
invalid inputs exit 1. The destination must not already exist when creating a pack.
Keep all generated files outside public repositories. Folder names are not access controls.

Inputs are a candidate-preparation manifest, features/targets/provenance/quarantine
JSONL and its digest-matching ZIP with atoms_full.jsonl. Every original quarantined
record receives cleaned text, source and cleaned hashes, a removed-line ledger,
original family/reason, provisional topic evidence offsets, and a recovery route.
The output manifest records algorithm and file hashes. Verify compares regenerated
bytes; a changed script requires a new version rather than accepting an old receipt.

Cleaning removes recognized standalone page markers, navigation, social fragments
and ads, while preserving prose, multilingual text and images. Images are flagged,
not transcribed. Labels use transparent lexical cues: at least two distinct cues
and one qualifying family produce an INFERRED proposal. Ambiguous/missing signal
is NOT_COMPUTABLE. These rules can miss or misclassify material; they are triage,
not independent semantic review or evidence of cultural lineage.

BODY_CANDIDATE also requires agreement with the source family and no higher-priority
quality/rights route. `candidate-features.jsonl` contains text-only projections;
`cleaned.jsonl` is a private audit sidecar and must not be serialized into model
features. All training eligibility stays false, rights unverified and splits
UNASSIGNED. Exact normalized duplicate IDs are linked across all source records;
near-duplicate and complete work/edition grouping remain required before splitting.

Known source-level hold: astro/hba material is not accepted automatically as an
authentic Jyotish anchor. Preserve its original label as provenance, not gold.
Internal/design-only and uncertain rights material remain separate.

Acceptance: synthetic CI checks cleaning preservation/idempotence, catalog false
positives, uncertain labels, source tampering, reproducibility and no overwrite.
Real data and private review decisions are deliberately not committed.

Next: direct semantic adjudication, edition/rights evidence, source re-extraction,
structured relationship validation, then approved instruction-target construction.
This implementation does not complete those steps.
