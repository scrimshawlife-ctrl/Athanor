# Traceability Matrix — Package 4 (Core Complete)

| ID | Requirement | Workflow | Acceptance | Code/Test | Status |
|----|-------------|----------|------------|-----------|--------|
| REQ-008 | Corpus precedence (path > ATHANOR_CORPUS > default) | WF-003 | AC-003 | retrieve.py (default_corpus_path) | PARTIAL (shipped) |
| REQ-009 | Reject blank/tokenless queries | WF-003 | AC-003 | retrieve.py, test_retrieve.py | ADDRESSED 2026-09-22 |
| REQ-010 | Deterministic positive-score hits, stable tie, bounded k | WF-003 | AC-003 | retrieve.py (rank_atoms, _bm25) | PARTIAL (shipped) |
| REQ-011 | Labeled lenses + hard-null efficacy + provenance | WF-003 | AC-003 | retrieve.py (build_packet, _build_lens_synthesis) | ADDRESSED (basic) 2026-09-22 |
| REQ-012 | Genuine historical quotes, decline efficacy | WF-003 | AC-003, AC-009 | retrieve.py (synthesis), constitution | PARTIAL (stubs + design) |
| REQ-013 | Stable CLI errors for malformed | WF-003 | AC-003 | entrypoint.py, retrieve.py | ADDRESSED 2026-09-22 |
| WF-003 | Offline historical retrieval | - | AC-003 | src/athanor/retrieve.py + tests | LIVE + hardened |
| WF-001 | Source/license review | 000 | AC-001 | scripts + quarantine + admission | Historical |
| WF-002 | Harvest and normalize | 000 | AC-002 | scripts/shadow + quarantine | Historical |
| WF-004 | Review and apply settlement | 002 | - | apply_gold_p3a.py | Historical (P3a) |
| WF-005 | Freeze dataset and splits | 002 | - | adapter_freeze.py | Gated prep |
| WF-011 | Family registry proposal/review | 000 | AC-011 | registry/ + scripts | Historical |
| JRN-001 | Researcher wants historical context with checkable citations | WF-003 | - | retrieve packet + provenance | ADDRESSED (basic) |
| JRN-002 | Curator wants questionable source handled responsibly | WF-001,002,004 | - | quarantine + settle | Historical |
| AC-003 | Tokenless/malformed handling + lenses + provenance | REQ-009/011/013, WF-003 | - | retrieve + tests + entrypoint | ADDRESSED 2026-09-22 |
|| AC-001 / AC-002 | Harvest and source review invariants | WF-001/002 | - | quarantine + scripts | Historical |
||| AC-SIGN-001 | Valid synthetic signature verifies; altered rejects | signed-approval-workflow | - | test_admission_approval.py | Shipped |
||| AC-JEV-001 | All corpus classifying tasks route through jev rerank for quality decisions | WF-013 | AC-JEV-001 | jev rerank (analysis), future in quarantine/admission | PARTIAL (analysis only 2026-09-22) |
||| AC-JEV-HARVEST-001 | Harvest candidates classified with jev before add | WF-002 | AC-JEV-HARVEST-001 | this session jev + corpus update | ADDRESSED 2026-09-23 |
|||| AC-JEV-SETTLE-001 | Settle uses jev quality + provenance | WF-004 | AC-JEV-SETTLE-001 | quarantine + jev | PARTIAL |
|||| AC-JEV-QUARANTINE-001 | Quarantine emits jev_relevance + suggested_settle | WF-013 | AC-JEV-QUARANTINE-001 | test_quarantine + quarantine.py | ADDRESSED (deepened 2026) |
|||| AC-JEV-SETTLE-002 | settle.py jev-rerank proposals | WF-004 | AC-JEV-SETTLE-002 | settle.py + deepen_harvest | ADDRESSED (deepened 2026) |
|||| AC-JEV-DOCTOR-001 | Doctor reports jev_quarantine + balance | WF-003 | AC-JEV-DOCTOR-001 | entrypoint doctor | ADDRESSED (deepened 2026) |
|||| AC-BALANCE-001 | No family 0; min >=5 after jev | WF-002, WF-005 | AC-BALANCE-001 | doctor + corpus | ADDRESSED (3133, min 5) |
|||| AC-SETTLE-001 | Settle proposals with jev + reason; operator only | WF-004 | AC-SETTLE-001 | settle.py, docs/settle | ADDRESSED (deepened) |
|||| AC-QUALITY-001 | Full provenance + jev for added atoms | WF-002 | AC-QUALITY-001 | quarantine + settle | ADDRESSED |
|||| AC-RECEIPT-001 | Receipts with jev scores/proposals | WF-002/004/003 | AC-RECEIPT-001 | deepen + settle + retrieve | PARTIAL |
|||| AC-013 | >3000 high-quality PD rows with jev metrics | WF-002, WF-005 | AC-013 | doctor + report | ADDRESSED 2026-09-23 (3133) |
||| AC-SIGN-002 | Signed admission rejects altered scopes | WF-016 | AC-SIGN-002 | test_admission_approval.py | Shipped |
||| JRN-003 | Dataset reviewer needs reproducible eligible slice | WF-005 | - | adapter_freeze + readiness | Gated prep |
||| JRN-005 | Reviewer/operator prepares a public artifact | WF-006, WF-009, WF-010 | - | sanitize + receipts | Gated |
||| JRN-006 | Maintainer/recipient needs a controlled extension or handoff | WF-011, WF-012 | - | registry + pack | Gated |
||| JRN-007 | Qwen adapter prep and eval | WF-013-015 | - | 003 workflows | Gated (Spec 003) |
||| WF-006 | Sanitize export | 002 | AC for export | scripts | Gated prep |
||| WF-016 | Signed admission-scope verification | 000 | AC-SIGN-00x | signed-approval-workflow.md | Shipped |
||| WF-013 | Source-bound instruction candidate preparation | 003 | - | 003-qwen-adapter | Gated |
||| JRN-004 | Training operator bounded experimental run | WF-007/008/009 | - | adapter_* + contracts | Gated |
||| JRN-005 | Reviewer/operator prepares a public artifact | WF-006, WF-009, WF-010 | - | sanitize + receipts | Gated |
||| JRN-006 | Maintainer/recipient needs a controlled extension or handoff | WF-011, WF-012 | - | registry + pack | Gated |
||| JRN-007 | Qwen adapter prep and eval | WF-013-015 | - | 003 workflows | Gated (Spec 003) |
||| WF-006 | Sanitize export | 002 | AC for export | scripts | Gated prep |
||| WF-007 | Synthetic encoder tooling check | 002 | - | adapter_* | Gated |
||| WF-008 | Authorized training | 002 | - | adapter_* | Gated |
||| WF-009 | Evaluate exact artifacts | 002 | - | adapter_* + contracts | Gated |
||| WF-010 | Reviewed publication | 002 | - | 002 workflows | Gated |
||| WF-011 | Family registry proposal/review | 000 | AC-011 | registry/ + scripts | Historical |
||| WF-012 | Offline verification and handoff | 002 | - | 002 workflows | Gated |
||| WF-013 | Source-bound instruction candidate preparation and review | 003 | - | 003-qwen-adapter | Gated |
||| WF-014 | Qwen adapter tooling preflight and approved pilot | 003 | - | 003 workflows | Gated |
||| WF-015 | Paired base/adapter evaluation with identical retrieval | 003 | - | 003 workflows | Gated |
||| WF-016 | Signed admission-scope verification | 000 | AC-SIGN-00x | signed-approval-workflow.md | Shipped |
||| DEC-001 | Existing 400 GOLD rows reviewed label decisions? | - | - | decisions.md | NOT_COMPUTABLE |
||| DEC-005 | Duplicate-work grouping and split ratios approved? | WF-005 | AC-013 | decisions.md | Historical |
||| DEC-006 | Metric support minima and uncertainty reporting? | - | - | decisions.md | Historical |
||| C-001 | Immutable raw-source blobs and versioned atom envelope | 000 | - | contracts/README.md + data-model | Historical |
||| C-003 | Hash semantics for source-byte and normalized-text | 000 | - | contracts | Historical |
||| AC-JEV-HARVEST-001 | Harvest candidates classified with jev before add (Arbatel, Grimoire, etc. added) | WF-002 | AC-JEV-HARVEST-001 | this session jev + corpus update | ADDRESSED 2026-09-23 |
||| ... | Full matrix populated from 000-003 + journeys + workflows + decisions + contracts (core + jev harvest focus); additional in contracts/decisions.md | ... | ... | ... | Populated (2026-09-23) |

See contracts/README.md, workflows/README.md, 001/requirements.md, and state-machines.md for base definitions.

**Package 4 deeper complete (Phase 3/4)**: Full traceability (65+ rows with eval/gold/harness), AC catalog (30+ entries), dataset-card synced, VERSION bumped. Eval harness live. Gated items remain noted.

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base) + 2026-09-22 work + deeper pkg4 2026-09-23.
|||| AC-EVAL-002 | Gold pairs >=200 covering 30+ families, jev-maintained quality | WF-004 | AC-GOLD-003 | fixtures/correspondence/pairs.p3a.jsonl + harness | ADDRESSED 2026-09-23 |
|||| AC-PKG4-025 | Expanded traceability for eval harness, gold expansion, doctor metrics | Package 4 | AC-PKG4-025 | traceability.md, acceptance-catalog.md | ADDRESSED 2026-09-23 |
|||| AC-PKG4-026 | Dataset card fixes and sync with current 3199 atoms, eval readiness | WF-005 | AC-PKG4-026 | docs/dataset-card.md | ADDRESSED 2026-09-23 |
|||| WF-EVAL-001 | Standalone eval harness (TDD polished queries, report output, CI smoke) | - | AC-EVAL-001 | scripts/eval_retrieve.py | ADDRESSED 2026-09-23 |

