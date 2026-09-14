# C-011 — instruction candidates and projection

Every JSONL row has exactly schema_version=athanor.instruction_candidate.v1, row_id (nonblank unique), task (three_lens/classification/correspondence/insufficient_evidence), query (nonblank), sources, answer and split (UNASSIGNED/train/val/test).

Each source has exactly id, text, sha256 and group_id. Text/hash are exact UTF-8 bytes without normalization; IDs/text/groups are nonblank. Source IDs are unique within a row and one source ID cannot denote conflicting text revisions across the input. No source ID, declared group ID or identical content hash may cross split labels. This checks supplied group consistency, not the correctness or completeness of work/edition grouping. A future freeze executor must resolve transitive work identities, mirrors, pairs and near-duplicates before assigning groups.

Answer has exactly historical, symbolic, operational (nonblank strings), citations (unique supplied source IDs), epistemic (OBSERVED/INFERRED/SPECULATIVE/NOT_COMPUTABLE) and efficacy (null). Non-abstaining answers require at least one citation; insufficient_evidence requires NOT_COMPUTABLE. The task tags classify examples; classification/correspondence currently use the same three-lens answer envelope, not Spec 002 typed prediction heads. Per-claim/lens support and semantic entailment are human evaluation obligations not certified by string validation.

No reviewer string or approval flag is accepted in this envelope. A future immutable review sidecar must bind the candidate/source/answer hashes to per-target decisions, reviewer identity, intended use and existing authenticated operator approval. Do not widen this candidate contract into an approval token.

Projection is deterministic by row_id; source order within a prompt is canonical by ID. It contains prompt (system/user messages) and completion (one assistant message with canonical JSON), row_id and split. Source digests, group IDs and future review metadata are not model inputs. The full source-record digest remains in the outer receipt to bind provenance. Output is always CANDIDATE_ONLY, training_authorized=false. JSONL input is bounded; output goes to stdout only. Run `python -m athanor.adapter_data --input PATH` after installing the local package, or with PYTHONPATH=src. Exit 2 denotes candidate-only preparation; exit 1 denotes INVALID input. No GPU/network/model dependency is required.

Raw text may contain malicious instructions; JSON encoding and a fixed system boundary reduce accidental interpolation but do not prove model robustness. Human answer review and actual adversarial model tests remain required. Outputs contain source text and belong in private storage, not Git or public CI logs.

Missing answer targets in the existing 400-row family candidate set must not be synthesized and labeled gold. Reuse source lineage for review proposals, then obtain actual source-grounded answers; do not treat this format change as dataset completion.
