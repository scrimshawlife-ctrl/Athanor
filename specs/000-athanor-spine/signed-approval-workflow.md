# WF-016: read-only signed admission-scope verification

This does not govern or activate. Implementation is a verifier, not admission.

| Field | Specification |
|---|---|
| Purpose | Authenticate an operator attestation bound to exact candidate bytes before any future admission workflow. |
| Actors | Operator controls signing/trust; verifier executor reads evidence. |
| Triggers | Explicit local verification request. |
| Preconditions | Operator provisions public trust separately; private key stays outside agent access; approval and underlying evidence reviewed by operator. |
| Inputs | Candidate JSONL, exact manifest bytes, detached signature, fixed operator trust file, current UTC clock. |
| Happy path | Bounded reads, verify domain-separated Ed25519 signature, validate time/revocation/scope, hash candidate bytes, validate atoms and content-bound decisions, return SIGNED_SCOPE_VERIFIED. |
| Alternate/failure paths | Missing trust/dependency, invalid input, tampering, expiry/revocation, unresolved rights/review or changed bytes returns HOLD; CLI exit 2. |
| State transitions | REQUESTED -> VERIFYING -> SIGNED_SCOPE_VERIFIED or HOLD. Neither state enters an admitted/training state. |
| Terminal states | SIGNED_SCOPE_VERIFIED (exit 0), HOLD (exit 2). |
| Side effects | Console report only; no signer, trust provisioning, journal mutation, corpus writes or network calls. |
| Invariants | No submitted key establishes trust; signature binds metadata and exact candidate bytes; KEEP is not GOLD; all reports keep admission_enabled/training_authorized false. |
| Permissions | Existing operator authority only. File ownership, execution environment and signing control are external trust prerequisites, not provided by this verifier. |
| Observability/audit | Success reports approval ID, manifest/candidate hashes and row count; failures report HOLD and reason; raw content and signatures are not logged. |
| Acceptance criteria | AC-SIGN-001 valid synthetic signature verifies; AC-SIGN-002 altered scope/bytes/signature or unknown key rejects; AC-SIGN-003 absent evidence/HOLD rejects even when signed; AC-SIGN-004 missing trust causes no writes. |
| Dependencies | DEC-003, C-001/C-004, WF-001, staging boundary, cryptography approval extra, tests/test_admission_approval.py. |
| Unresolved items | Real key setup, independent review, evidence truth, revocation freshness, secure writer and replay/atomicity controls. Real-data readiness NOT_COMPUTABLE. |

Traceability: all AC-SIGN criteria are exercised by test_admission_approval.py;
Run `python -m pytest tests/test_admission_approval.py -q` for the synthetic
acceptance suite. Next task is a separately reviewed admission transaction,
not a direct append based on a cached verification result.
