# Signed approval verification (read-only)

This implements the selected local-signature direction for DEC-003, not corpus
admission. It does not govern or activate. No signing key, trust configuration,
corpus writer, training permission or real approval was provisioned.

See [WF-016](../../specs/000-athanor-spine/signed-approval-workflow.md) for workflow
fields, acceptance criteria and unresolved dependencies.

Install the `approval` extra. Run `python -m athanor.admission_approval --manifest
MANIFEST --signature SIGNATURE --candidates CANDIDATES` as one command. Exit 0 means
only SIGNED_SCOPE_VERIFIED; exit 2 means HOLD. Both keep admission_enabled,
training_authorized and corpus_mutated false. Never interpret exit 0 as promotion.

## Trust and signing

The CLI reads only `~/.athanor/operator-trust.json` for trust. There is no submitted
key, key-discovery request, trust-file CLI argument, or signer built into this tool.
Its exact fields are schema_version=`athanor.operator_trust.v1`, operator, a
32-byte Ed25519 public key encoded as 64 lowercase hex characters in public_key_hex,
and revoked_approval_ids (an explicit list, possibly empty). The operator must
configure and protect this separately; absent or invalid configuration yields HOLD.

Keep the private key outside this repository, dataset packs and agent access. The
operator-controlled signing process signs the exact bytes of the prefix
`athanor.corpus-admission-approval.v1` followed by one NUL byte and then the exact
manifest bytes. Signature file is raw 64-byte Ed25519, not base64. Whitespace edits
to the signed manifest invalidate it. The library uses cryptography's Ed25519
verification, not custom cryptography:
https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ed25519/

## Manifest wire shape

Exact fields: schema_version=`athanor.corpus_admission_approval.v1`, approval_id,
operator, action=`admit_local_retrieval`, target=`athanor.local_retrieval_corpus`,
approved_at, expires_at, candidates_sha256, decisions. Timestamps are UTC
YYYY-MM-DDTHH:MM:SSZ; approved_at <= current clock < expires_at is required.
Revoked approval IDs fail even if signature and time are valid. Rotating/removing
the configured public key invalidates approvals from the prior key.

candidates_sha256 binds the entire candidate JSONL byte stream, including IDs,
labels, source URLs, license claims, order and whitespace. Each atom also requires
SHA256 of exact UTF-8 text. Decisions cover every atom once, binding atom_id and
content_hash. Each contains:

- rights: outcome=CLEARED, intended_use=local_analysis, jurisdiction, reviewer,
  evidence_sha256 (nonempty distinct lowercase SHA256 list).
- review: decision=KEEP, reviewer, evidence_sha256 (same reference constraints).

These are the operator's signed attestations corresponding to C-001/C-004, not
proof of legal truth or reviewer independence. Evidence references must be resolved
and reviewed by the operator before signing; this verifier does not fetch evidence
or certify its contents. NOT_COMPUTABLE/unknown license, absent decisions, invalid
references, HOLD decisions and changed content fail. KEEP is not GOLD, and local
analysis clearance is not export or training clearance.

## Limits and threat boundary

Manifest <=1 MiB; candidates <=16 MiB and 10,000 rows; trust <=64 KiB. Reads are
bounded; duplicate JSON keys/nonfinite values are rejected. No manifest path is
followed. The CLI rejects leaf symlinks. This is not a sandbox against a compromised
operator OS, changed home resolution, parent-directory junctions, replaced trust
configuration or modified verifier code. Protect the account, trust file, clock
and private key externally. Revocation-list freshness depends on the operator.

A future writer must reverify the exact bytes at use time, recheck evidence and
revocation, enforce atomic/non-overwriting admission and record replay state.
This verifier neither consumes approval IDs nor issues reusable admission tokens;
repeated read-only verification is permitted. Do not attach it to legacy append
loops or copy extracted atoms manually on the strength of its success status.

## Verification

Synthetic tests create ephemeral keys in memory, test valid signatures and negative
controls (tampering, other keys/domains, expiry/revocation, wrong scope, changed
bytes, unresolved evidence, bad atoms). They do not establish real dataset rights.
Private held packages remain separate and unapproved by these tests.

Provenance: operator accepted local signed-manifest implementation on 2026-09-14;
local synthetic tests. Independent security review and real trust setup remain pending.
