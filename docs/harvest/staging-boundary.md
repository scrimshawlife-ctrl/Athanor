# Legacy harvest staging boundary

Legacy harvest scripts now default to `~/.athanor/staging/legacy-harvest/candidates.jsonl`,
not `~/.athanor/corpus/atoms.jsonl`. This implements a staging boundary, not review
authentication or promotion. Existing corpus and historical receipts are unchanged.

Ten writer modules and `ingest_priority_b_continue.py` (through its parent import)
share this candidate destination. Duplicate checks, counts and adjacent backups in
these scripts now describe staging only. Existing corpus totals are not included:
old fill targets and historical progress claims must not be interpreted as current
reviewed-corpus targets. No harvest was run to verify this change.

Do not point retrieval or training at this staging file. A license claim in a
harvest plan is not clearance. Before corpus admission, WF-001/WF-002 and C-001/C-002
require use-scoped rights, exact content/source binding and review evidence. Those
advisory contracts are not an implemented authenticated admission service. Unknown
rights/review remains HOLD / NOT_COMPUTABLE; no promotion command is supplied here.

This default-path change is not an OS security boundary: symlinks, manually edited
paths or external writers are not prevented. Existing retrieval readers remain
compatible and do not certify rights. Historical scraping prompts that say append
directly to the corpus are superseded by this staging rule for new harvests.

Provenance: local writer inventory and static regression tests. This does not govern
or activate training, publishing or corpus promotion.
