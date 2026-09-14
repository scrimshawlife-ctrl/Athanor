# Private quarantine recovery

Preparation-only support for WF-013 in Spec 003. No source relabeling, gold
promotion, split freeze, training, Hub publication or runtime activation occurs.

```sh
python -m athanor.quarantine --prepared /private/prepared --pack /private/source.zip --output /private/new-recovery
python -m athanor.quarantine --prepared /private/prepared --pack /private/source.zip --output /private/new-recovery --verify
```

Omit `--output` for a read-only summary. Exit 2 means candidate HOLD, not approval;
invalid inputs exit 1. The destination must not already exist when creating a pack.
Destinations inside any Git checkout (including linked worktrees) are rejected,
even if ignored. Keep generated files in private storage outside Git; folder names
are not access controls.
The final output directory and its files use POSIX modes 0700 and 0600,
respectively, at creation (subject to a stricter umask). Parent directories use
normal platform permissions; choose a trusted parent that other users cannot
replace. Existing parent permissions are not changed. On Windows, these modes
do not establish a private ACL: use storage
whose ACL already restricts access to the operator; Windows ACL verification is
outside this command. Verification compares bytes, not access-control policy.

Inputs are a candidate-preparation manifest, features/targets/provenance/quarantine
JSONL and its digest-matching ZIP with atoms_full.jsonl. Every source
atom must supply the eight required string fields in the atom contract, including
epistemic and content_hash; required nonempty values, type/epistemic enums and the
minimum content_hash length are checked. This does not authenticate source claims.
The manifest and ZIP are each parsed from the same captured bytes used for their
recorded digest; replacing their paths afterward cannot substitute other content.
Encrypted, unsupported or malformed DEFLATE members return structured INVALID with exit 1,
without creating an output directory.
Every original quarantined record receives cleaned text, source and cleaned hashes, a removed-line ledger,
original family/reason, provisional topic evidence offsets, and a recovery route.
The output manifest records algorithm and file hashes. Verify compares regenerated
bytes; a changed script requires a new version rather than accepting an old receipt.

Cleaning removes recognized standalone page markers, navigation, social fragments
and ads. Unmatched lines retain their exact whitespace, Unicode and line endings;
navigation prefixes followed by prose are not removed. Images are flagged,
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
