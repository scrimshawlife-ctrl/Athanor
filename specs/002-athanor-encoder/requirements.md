# Requirements 002 — settlement, encoder and release

Status: proposed target behavior. This does not govern or activate. Operator approval to prepare this package is not evidence of historical label review.

| ID | Requirement and rationale | Owner | Workflow / acceptance |
|---|---|---|---|
| REQ-014 | MUST separate heuristic proposals from reviewed GOLD decisions bound to atom hash, reviewed target labels, reviewer and approval reference. | Operator/reviewer | WF-004 / AC-004 |
| REQ-015 | MUST exclude HOLD/DROP from train/export; KEEP remains weak; gold and weak must be disjoint after joining by atom revision. | Dataset maintainer | WF-004, WF-005 / AC-004, AC-005 |
| REQ-016 | MUST freeze provenance, eligible rows, duplicate groups, deterministic splits and measured balance before training. | Dataset reviewer | WF-005 / AC-005 |
| REQ-017 | MUST sanitize only scope-cleared eligible rows; enforce excerpt and work-level reconstruction restrictions, canonical reception labels and artifact digests. | Export maintainer | WF-006 / AC-006 |
| REQ-018 | MUST use explicit model/tokenizer/config revisions and approval scoped to the training snapshot; missing authority or resources remains HOLD. | Training operator | WF-007, WF-008 / AC-007, AC-008 |
| REQ-019 | MUST evaluate exact artifacts against frozen controls; unexecuted, unsupported and absent-evidence metrics remain NOT_COMPUTABLE. | Evaluation reviewer | WF-009 / AC-009 |
| REQ-020 | MUST apply the single name/release prerequisite matrix, including the existing E6 Hub requirement, and validate actual outputs on wall and historical-positive cases. | ADVERSARY/operator | WF-009, WF-010 / AC-009, AC-010 |
| REQ-021 | MUST bind approved publication to exact artifact bytes, destination, card, license and evaluation; failed/partial uploads cannot claim PUBLISHED. | Publishing operator | WF-010 / AC-010 |
| REQ-022 | MUST hand off only scope-authorized files with a manifest, checksums, reproduction instructions and recipient validation; delivery never grants train/publish authority. | Operator/recipient | WF-012 / AC-012 |
| REQ-023 | MUST represent out-of-domain and unavailable head results explicitly; do not invent family labels or infer truth from confidence. | Model maintainer | WF-007, WF-009 / AC-007, AC-009 |

Dataset count floors remain those in [dataset-contract](dataset-contract.md). Model, tokenizer, support minima, split configuration, approval verification and rights/retention choices remain explicit dependencies in [decisions](../decisions.md). No training metrics or hardware capacity are fabricated.

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base)
