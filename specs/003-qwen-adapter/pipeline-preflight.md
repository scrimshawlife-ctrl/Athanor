# Candidate freeze and runtime inventory

Status: engineering primitives implemented; real training readiness HOLD.
This does not govern or activate. No reviewed dataset, trainer, model load or
training run is claimed by these tools.

## WF-013: candidate-only freeze

Run `python -m athanor.adapter_freeze --input candidates.jsonl --config split.json`.
Both files are private operator inputs, never generated gold. The config is:

```json
{"schema_version":"athanor.split_config.v1","seed":42,"ratios":{"train":0.8,"val":0.1,"test":0.1},"min_rows":{"train":1,"val":1,"test":1},"grouping_revision":"operator-assigned-revision"}
```

These illustrative minima are structural checks, not adequate evaluation support.
Choose and document real support thresholds before freezing approved data.
The algorithm joins transitive components by source ID, work group, exact content
hash and identical task/query. Generic repeated questions conservatively share a
component even across sources. Hash allocation is deterministic, not a promise of
exact split proportions. Missing minima yield REJECTED_SUPPORT; never retry seeds
based on test performance. Existing assigned splits are rejected, not shuffled.

The input digest, grouping revision, seed, component assignments, split/task counts
and projection bind the candidate freeze. Group identities must be complete;
near-duplicate and semantic leakage review remain external. FROZEN_CANDIDATE is
not reviewed, eligible, or authorized. Exit 2 is deliberate HOLD; invalid input is 1.
Trusted source-use/answer-review decisions must bind exact source and answer hashes
before an approved freeze can be issued. No boolean supplied by these tools grants
that authority.

## WF-014: read-only Spark inventory

In the intended Spark environment, from the installed Athanor checkout:

```sh
python -m athanor.adapter_preflight --model-dir /absolute/path/to/local/model
```

Use the actual existing model directory; omit the option if weights are absent.
The command prints JSON to stdout, returns 2 for HOLD, and never downloads weights,
loads a model, changes packages or starts training. It inventories OS/architecture,
Python/package versions, GPU-reported memory/driver and bounded local config.
Revision, weight integrity, backend compatibility and measured training memory
remain unverified. Run it on Spark, not the desktop, for Spark evidence.

Pinned upstream config identifies Qwen3_5ForConditionalGeneration / qwen3_5.
Do not assume an unrelated causal-only recipe is compatible. Verify the actual
local pinned processor and text-only load path before selecting target modules.

`adapter_tokens.completion_tokens` uses the installed tokenizer chat template with
thinking disabled, requires an exact prompt-token prefix, masks every prompt token
and rejects oversized examples rather than truncating. `pad_examples` masks padding
even if its token ID equals EOS. Synthetic tests establish these invariants only;
real Qwen template compatibility is NOT_COMPUTABLE until exercised locally.

## Remaining completion gates

1. Independent answer review, source-use rights and complete work/duplicate IDs.
2. Actual Spark inventory and pinned model/processor integrity evidence.
3. Tested backend lock, real token-boundary tests, language-only modules, bounded
   trainer/checkpoint/resume implementation and measured memory smoke test.
4. Exact run approval, then paired base/adapter evaluation on frozen held-out data.

Provenance: Athanor Spec 003 and synthetic tests/test_adapter_pipeline.py;
upstream pinned config at https://huggingface.co/Qwen/Qwen3.8-27B/raw/1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0/config.json.
