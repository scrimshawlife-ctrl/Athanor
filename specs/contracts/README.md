# Contracts — completion target

Status: advisory v1 design. This does not govern or activate. [proposed.v1.schema.json](proposed.v1.schema.json) is a review schema under specs, not a replacement for runtime schemas. Its named $defs define wire shapes; semantic checks below require implementation and evidence in packages 4-5. JSON validity alone never establishes rights, human approval, label quality, or a passing gate.

## C-001 — source and license decision

Source identity records source_id, canonical URL, observed_at, source_sha256, work_id and edition_id where known. Null work/edition identity requires a reason and blocks cross-source split claims until grouping is resolved. URL normalization records its version; preserve the original requested URL and final observed URL in the receipt.

LicenseDecision fields: decision_id, source_id, content_hash, intended_use (ingest/local_analysis/export), outcome (CLEARED/HOLD/DENIED), reviewer, evidence_refs, jurisdiction and decided_at. CLEARED needs nonempty evidence, identified jurisdiction/scope and exact source or edition binding. A host allowlist, HTTP success, age heuristic or license string is insufficient. Revisions supersede but never overwrite decisions. See WF-001.

## C-002 — stored atom envelope and legacy boundary

The proposed atom_envelope contains schema_version, atom (a projection conforming to the existing closed v0 atom schema), source_ref, harvest_receipt_ref, reception_layer, reception_reason, and settlement_refs. Provenance sidecars are not injected into the closed v0 object. Envelope and legacy source bytes have separate digests.

Existing harvested rows may contain extra metadata and therefore not conform to the declared v0 schema. A future migration must: retain the original blob and hash; derive the canonical atom projection; move metadata into the envelope; validate both projection and envelope; emit a migration receipt; and switch readers only after approved compatibility verification. This patch performs no migration. Unknown legacy fields are retained in the original blob, not silently dropped. See [data model](../000-athanor-spine/data-model.md).

## C-003 — receipt

Each receipt requires schema_version, run_id, workflow_id, job_type, status, started_at, finished_at, engine, config_hash, inputs, outputs, counts, errors and epistemic. References carry identity, sha256 and optional authorized location. job_type covers harvest, normalize, settlement, freeze, sanitize_export, tooling_check, train, eval, publish, handoff and registry_review. A receipt for PARTIAL/FAILED/CANCELLED must enumerate errors or cancellation reason; SUCCEEDED must identify required outputs.

Hash algorithm is SHA-256 of exact artifact bytes. started_at/finished_at are UTC RFC3339 instants, with finish >= start. Persist a receipt only after terminal state. A separate run journal tracks nonterminal states. Compute a receipt digest from its final bytes in a manifest outside the receipt; do not insert a self-referential hash. Old receipts are immutable; a correction references the original receipt and explains the correction. Existing scripts emit incompatible variants; do not relabel them v1 without validation.

## C-004 — settlement and approval reference

A settlement decision binds decision_id, atom_id, content_hash, decision, reviewed_targets, label_evidence_refs, reviewer, approval_ref and decided_at. KEEP/HOLD/DROP may be proposals; a GOLD decision requires nonempty reviewed targets, supporting evidence and verifiable operator approval. Reviewed target values are explicit; the decision is not blanket validation of all possible claims. The reviewed_targets object permits family_id, atom_type, lens_route, reception_layer and correspondence only. Missing targets remain unreviewed/masked.

Approval reference fields: approval_id, operator, action, scope_hash, target, evidence_ref and approved_at; expires_at and revoked_at are optional. scope_hash binds a manifest of exact atom/label revisions, registry diff, training inputs, export pack or release destination as applicable. Approval evidence is checked through a trusted mechanism (DEC-003), not accepted because a JSON file contains an operator name. It records existing consent and is not an authorization token or new governance layer.

The existing GOLD script's hard-coded operator phrase and heuristic selection are not sufficient evidence under this target contract. Historical approval validity stays NOT_COMPUTABLE until the scope is reconciled; no historical receipt is erased.

## C-005 — train rows, fixtures and snapshots

Train row: atom envelope reference plus family_id, atom_type, reception_layer, settlement_decision_ref, supervision (gold/weak), split (train/validation/test), group_id, labels and loss_mask. GOLD claims must link reviewed target evidence; a loss_mask enables only available labels. Wave derives from the pinned registry. Weak rows may enter train only, never validation/test truth. HOLD/DROP are rejected. A row must not exist in both gold and weak partitions.

Correspondence: pair_id, family_id, role, filler, span, atom reference/hash, epistemic, settlement reference for reviewed pairs. role/filler/span must be supported by the source; string presence alone does not establish the relation. Existing 60 OBSERVED fixture rows have not been independently validated against local source atoms in this review. Negatives: unique neg_id, theme, text, provenance/license and expected OOD outcome; fictional content is explicitly a fixture. Wall: prompt_id, query, expected disposition, forbidden behavior rubric and positive historical controls. Do not use expected output as evidence of actual model behavior.

Snapshot requires snapshot_id, row_manifest ref, registry/config/tokenizer revisions, grouping_version, seed, split_ratios, split_counts, per-family counts, train_token_total, train_family_tokens, exclusion_manifest ref and evidence_refs. group_id is a connected component of shared work/edition/canonical source and content hashes; conservative grouping prevents mirror leakage. Unknown grouping remains unresolved, not randomly split. Sort group IDs and assign with the declared deterministic algorithm/config; ratios must sum to one. Same inputs/config produce the same assignments. Changing any input creates a new snapshot, never a mutated old one.

E7 = max(train_family_tokens[f]) / train_token_total after exclusion and sampling, using the actual model tokenizer revision. Empty denominator is NOT_COMPUTABLE. Count each eligible training token exactly once. Report gold-only balance separately; it is not train-slice E7. Dataset minimums remain in dataset-contract.md; unsupported families are identified explicitly rather than silently removed from a claim.

## C-006 — retrieval API, errors and packet

Path precedence: explicit corpus argument > ATHANOR_CORPUS > home default. Library target errors: InvalidQuery, InvalidFamily, InvalidK, CorpusUnavailable, CorpusInvalid and ContractViolation. CLI target mapping: valid packet including NO_MATCH exits 0; invalid/unsupported input and unusable corpus exit 2 with stable error code on stderr; internal contract violation exits 1. No partial JSON success packet or traceback for an expected user-input error. These are target names, not existing exported classes.

Tokenless input yields UNSUPPORTED_QUERY and zero hits; CLI emits the structured error rather than a success packet. Valid supported input with no positive match yields NO_MATCH, empty hits and NOT_COMPUTABLE lenses with reasons. Unknown family is InvalidFamily, distinct from an existing family with no matches. k must be an integer >=1 and <= an explicitly selected limit (DEC-004). Ranking configuration is pinned; ties use atom_id ascending. Excerpt budget must count Unicode code points including ellipses; source text is never rewritten by display cleanup.

The separate `athanor.error.v1` envelope requires schema_version, code, nonempty reason and exit_code. Codes are UNSUPPORTED_QUERY, InvalidQuery, InvalidFamily, InvalidK, CorpusUnavailable, CorpusInvalid and ContractViolation. ContractViolation exits 1; other listed errors exit 2. Errors contain no snapshot_ref, hits or synthesis, and go to stderr; zero hits means retrieval was not performed, not an empty success packet. Packet outcomes are MATCH, NO_MATCH and HISTORICAL_ONLY only. This is advisory wire design, not an implemented CLI change.

Proposed packet: schema_version, query, outcome, snapshot_ref, hits, synthesis, efficacy and optional encoder/diagnostic_receipt_ref. Each hit includes atom_id, family_id, excerpt, license_decision_ref, source_url, content_hash and epistemic. Every lens requires epistemic, text, evidence_refs and reason; unavailable lens has text null and nonempty reason with NOT_COMPUTABLE. Empty lens objects are invalid. No source attribution is invented when the source is absent. Historical quotation and generated interpretive claims carry separate labels.

## C-007 — encoder output

Proposed output records exact model_ref, snapshot_ref, outcome (classified/out_of_domain/unavailable), family_id nullable, family_confidence nullable, lens_route, reception_layer nullable, unbind nullable, epistemic, reason and efficacy null. classified requires known family_id and bounded confidence; OOD/unavailable requires null family/confidence with reason. Confidence describes a prediction, not historical truth. Missing model uses lexical fallback and unavailable status, never synthetic scores. No chat_template, efficacy score, phenomenal head or forecast permission is permitted. The optional packet encoder uses this schema directly rather than accepting arbitrary extra properties.

## C-008 — sanitized export

Each row includes atom_id, family_id, text_excerpt (<=500 Unicode code points), source_url, content_hash, reception_layer, epistemic, settlement_decision_ref and license_decision_ref. Export context supplies approved audience/use, snapshot and work-level excerpt policy. No efficacy field, binary seal, HOLD/DROP row or unsupported rights state. Exact allowlisted use clearance is required; a blacklist of a few license strings is insufficient.

The exporter must check full-work boundaries and aggregate excerpts across a work/edition: a complete short Call or multiple chunks reconstructing a prohibited work fails regardless of per-row length. Unknown work boundary/rights produces exclusion with NOT_COMPUTABLE, not approval. Required reception labels missing after reviewed migration exclude the row; no unspecified string is invented. Stage outputs, validate all included rows and aggregate policy, then finalize manifest. Partial files cannot be mistaken for a complete export. Failure reasons distinguish rights, settlement, metadata, reconstruction and encoding.

## C-009 — run, evaluation and release evidence

Training config pins checkpoint, tokenizer, library revisions, heads/label masks, seeds, hyperparameters, snapshot and resource envelope. Resume binds identical relevant inputs and checkpoint ancestry. Runtime/resource choices remain DEC-002/004; this contract supplies required fields, not guessed values.

Eval result records gate_id, status (PASS/FAIL/NOT_COMPUTABLE), applicability, metric_name, value nullable, control_value nullable, support, artifact_ref, snapshot_ref, config_hash, output_refs, reviewer and reason. NOT_COMPUTABLE includes missing artifact/evidence/denominator/definition; FAIL means an executed valid assessment missed its criterion. Non-applicable gates are marked explicitly and cannot satisfy a required gate. E4/E6 need actual-output references and content review; counts alone cannot pass them. E5 requires enforced network denial evidence, not only an environment variable.

Executed E1/E2/E3/E7 results require a frozen dataset snapshot reference. E0 schema checks, E4 wall fixtures, E5 offline tests, E6 historical-positive fixtures and E8 card/CLI assessments may use snapshot_ref=null when no dataset snapshot is involved; their exact tested inputs remain bound by artifact_ref, config_hash and output_refs. All PASS/FAIL results still require applicable status, a measured value, positive support, artifact and output evidence. Unknown gate IDs are rejected by the existing E0-E8 enum until their evidence scope is specified. Missing required evidence remains NOT_COMPUTABLE; never invent a snapshot merely to satisfy a schema.

Executed E1/E2/E3 comparison results additionally require non-null control_value; zero is a valid measured control. NOT_COMPUTABLE results and non-comparison gates may retain null. Every executed PASS/FAIL requires a nonblank reviewer. A null encoder model_ref forces outcome=unavailable, never an out_of_domain classification.

Review regression check: `python specs/contracts/verify_review.py` (requires jsonschema). It tests positive and negative cases, both PASS and FAIL paths, comparison controls, missing-model behavior, nonblank reviewers, and WF-003 error-envelope consistency. Two mutation controls reproduce the comparison and missing-model defects when their constraints are removed. It needs no Git history and ignores unrelated tracked/untracked changes. One-off patch-scope and whitespace audits run separately at review time; this checker does not certify real gate outcomes or patch scope.

See eval-gates.md for the single prerequisite matrix. A release manifest binds model/dataset/card bytes, destination, exact approved scope, applicable gates and rights evidence. Receipt must include remote identity/readback evidence before PUBLISHED. The historical T0/T1 names do not prove those artifacts exist.

## C-010 — offline handoff

Pack manifest: pack_id, intended_recipient_ref, intended_use, scope/approval_ref, artifact list with relative paths/digests/licenses, excluded-data statement, reproduction instructions and verification command references. Paths must be relative, non-traversing and unique. Include only approved files; do not default to copying the full home corpus. Local manifest validation proves VERIFIED_LOCAL; transfer evidence proves DELIVERED; recipient digest acknowledgment proves RECIPIENT_VERIFIED. Pack possession is not authority to train or publish.

## Compatibility and implementation status

Existing v0 consumers remain unchanged. Implement v1 via explicit opt-in/version negotiation and a documented migration, not by silently changing responses under an old schema ID. Packages 4-5 must add producer/consumer semantic tests, complete JSON Schemas for remaining reference/config manifests, migration/rollback checks, and the global traceability/test matrix. The included wire schema concretizes high-risk atom, approval, settlement, packet, encoder, export, receipt and eval boundaries now; it does not claim full runtime conformance or full corpus validation.

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base)
