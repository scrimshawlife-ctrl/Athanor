# Domain model — Athanor

Status: proposed specification, not runtime conformance. This does not govern or activate.

## Entities and relationships

| Concept | Identity and meaning | Relationships / exclusions |
|---|---|---|
| Work | Stable work_id for a textual/cultural work; attribution may be uncertain | Has editions/witnesses; shared mirrors do not create new works |
| Edition / Witness | edition_id plus language, translation, attribution, publication metadata and supporting references | Belongs to a work; a modern translation does not inherit an ancient work's rights status |
| Source | source_id and normalized URL; a fetch is a dated observation of bytes | Resolves an edition when known; HTTP success is not license clearance |
| LicenseDecision | Versioned rights decision and scope: ingest, local use, or export | Targets exact source/content or reviewed edition; records reviewer and evidence; HOLD excludes promotion/export |
| Atom | Stable atom_id and exact content digest for a text/table/correspondence/diagram description | Belongs to a source and proposed family; immutable content identity is separate from revisable labels |
| Family | Existing registry ID and version; wave is harvest priority | Registry membership is not quality, coverage, rights, or approval; proposals are not live families |
| Claim | Assertion text, lens, epistemic label, evidence references and scope | OBSERVED text occurrence does not establish the truth of the quoted historical belief |
| Lens | Historical, symbolic, or operational reading of evidence | Operational describes historical arrangement; missing reading is explicitly unavailable, never an invented explanation |
| SettleDecision | Candidate/KEEP/HOLD/DROP/GOLD judgment for an atom hash and named label targets | GOLD requires reviewed target labels; license clearance is separately required; superseding decisions preserve history |
| Snapshot | Immutable manifest of eligible atom revisions, label decisions, split assignments, tokenizer/config revisions | A corpus count is not a frozen dataset; changes produce a new snapshot_id |
| Receipt | Terminal record of an attempted workflow with input/output hashes and status | A path or prose PASS is not validated receipt contents; failed/partial jobs retain outcomes |
| ModelArtifact | Artifact hash, model/tokenizer revisions, config and training snapshot | Weight availability, evaluation success, name eligibility and publication are separate facts |
| Packet | Query outcome plus evidence-bound hits and labeled lenses, optional validated encoder output | A hit can be a historical quotation without becoming a practice instruction; efficacy is always null |

## Independent dimensions

- Source observation: a source returned bytes at a time, with a digest.
- Label review: a reviewer validated specified family/type/lens/reception/correspondence labels against those bytes.
- Settlement eligibility: KEEP/GOLD may be considered for training; HOLD/DROP may not.
- Rights clearance: an explicit decision covers the proposed use; a permissive string alone does not.
- Epistemic status: OBSERVED / INFERRED / SPECULATIVE / NOT_COMPUTABLE applies to a named claim. Synthetic fixture existence can be OBSERVED while its fictional text is not a historical fact.
- Processing state: success/failure/pending is independent of epistemic status and authority.

## Invariants

One content revision cannot silently inherit another revision's review. Weak labels never acquire GOLD solely through host reputation, text length, balance sampling, or successful execution. The source URL plus digest and snapshot must make each hit resolvable even if the remote page later changes. Changing labels must not rewrite old content hashes or historical receipts. No receipt, card, or schema grants an executor authority.

## Head semantics

Family is a label from the pinned live registry; wave is derived from that registry, not independently inferred. Atom type describes representation. Lens route is a multi-label routing decision, not a completed three-lens reading. Reception layer distinguishes primary_witness, pd_translation, historical_commentary, and modern_reception. A correspondence identifies role, filler, quoted span, and source atom revision. Missing head labels are masked, not filled from family stereotypes. Out-of-domain classification is a separate outcome with null family, never a forced family prediction.

Provenance: Notion Sprint 001 Hub [not inspected; Athanor Hub inspected] + Loop 805 Slice N/A + Hash: fd84c7085579f3e7a560b38fc554a4f832fa9c10 (review base)
