# Operational Lens Track — Gated Planning Document

**Status**: GATED (SHADOW lane only — historical PD corpus does not contain operational content)

## Rationale

Current corpus is 100% historical primary sources. `lens_hints.operational` is deliberately 0 across all 3156 atoms.

Operational content would include:
- Practical instructions
- Modern ritual adaptations
- Efficacy-oriented descriptions
- Contemporary practitioner notes

These are intentionally excluded to maintain strict provenance and avoid unsubstantiated claims.

## Proposed Gated Path (if ever activated)

1. **Separate Corpus Slice**
   - New corpus path or tag: `operational/` or `modern_pd_cleared/`
   - All entries must pass additional review (rights, modern sourcing, operator sign-off)

2. **Jev Classification**
   - Use `jev_classify.py` with a specialized prompt for "operational suitability"
   - Min-relevance threshold higher (e.g. 0.7)
   - Must include explicit "This is practical guidance only — no efficacy guaranteed" disclaimer in text

3. **Schema Extension**
   - Add optional `operational_safety` field or `practice_note` 
   - Update `lens_hints` to allow `operational: true` only on this track

4. **Quarantine / Settle**
   - New quarantine rules in `quarantine.py` for operational atoms (stronger human review required)
   - `settle.py` must flag operational proposals for explicit operator approval

5. **Doctor & Receipts**
   - `athanor doctor` must report separate "operational_atoms" count
   - Receipts must carry `operational: true` flag

6. **Evaluation**
   - Separate gold fixtures for operational queries
   - Strict "no efficacy" tests in `test_retrieve.py`

## Current Mitigations

- Synthesis stubs in `retrieve.py` explicitly state: "Athanor returns historical/textual context only — no practice instructions, efficacy scores, or summon UX."
- All atoms carry `epistemic: OBSERVED` with historical focus.
- AC-009 and related enforce "No efficacy claims".

## Decision Criteria for Activation

- Clear operator need demonstrated
- Modern sources with explicit rights clearance
- Additional governance (e.g. signed approval per WF-016)
- Updated acceptance catalog entries (new AC-OPERATIONAL-*)

**Until then**: All work stays in historical lane. Operational remains 0.

---

*Generated during execution of quality recommendations. Any future operational atoms would still route through jev for classification.*