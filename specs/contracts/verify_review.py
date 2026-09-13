"""Reusable advisory contract regressions; no Git history, runtime or network needed."""
import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from validation import is_valid_contract

ROOT = Path(__file__).resolve().parents[2]
REL = "specs/contracts/proposed.v1.schema.json"
schema = json.loads((ROOT / REL).read_text(encoding="utf-8"))
Draft202012Validator.check_schema(schema)
v = Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER)
H = "a" * 64
ref = {"id": "synthetic", "sha256": H}
lens = {"epistemic": "NOT_COMPUTABLE", "text": None, "evidence_refs": [], "reason": "synthetic unavailable evidence"}
packet = {"schema_version": "athanor.packet.v1", "query": "synthetic", "outcome": "NO_MATCH", "snapshot_ref": ref, "hits": [], "synthesis": {k: copy.deepcopy(lens) for k in ("historical", "symbolic", "operational")}, "efficacy": None}
error = {"schema_version": "athanor.error.v1", "code": "UNSUPPORTED_QUERY", "reason": "No supported tokens", "exit_code": 2}
source = {"schema_version": "athanor.source.v1", "source_id": "s", "source_url": "https://example.invalid/synthetic", "observed_at": "2026-09-13T00:00:00Z", "source_sha256": H, "work_id": "w", "edition_id": "e", "identity_reason": None, "canonicalizer_version": "synthetic-v1"}
evaluation = {"schema_version": "athanor.eval_result.v1", "gate_id": "E5", "status": "PASS", "applicability": "applicable", "metric_name": "synthetic offline test count", "value": 1, "control_value": None, "support": 1, "artifact_ref": ref, "snapshot_ref": None, "config_hash": H, "output_refs": [ref], "reviewer": "synthetic", "reason": "synthetic executed evidence"}
positive = [packet, source]
negative = []
def changed(obj, **kw):
    result = copy.deepcopy(obj)
    result.update(kw)
    return result

def gate_case(gate, status, **kw):
    value, control = (0.5, 0.25) if status == 'PASS' else (0.25, 0.5)
    if gate == 'E7':
        value, control = (0.25 if status == 'PASS' else 0.5), None
    fields = {'gate_id': gate, 'status': status, 'value': value, 'control_value': control}
    fields.update(kw)
    return changed(evaluation, **fields)

# Unsupported queries are errors, not packets with a fake snapshot.
bad_packet = changed(packet, outcome="UNSUPPORTED_QUERY", query="!!!")
negative.append(bad_packet)
for code in schema["$defs"]["error"]["properties"]["code"]["enum"]:
    exit_code = 1 if code == "ContractViolation" else 2
    positive.append(changed(error, code=code, exit_code=exit_code))
    negative.append(changed(error, code=code, exit_code=2 if exit_code == 1 else 1))
negative.extend([changed(error, snapshot_ref=ref), changed(error, hits=[]), changed(error, reason=""), changed(error, reason="   ")])

# Every unresolved identity needs a meaningful reason; resolved identities may omit the explanation via null.
bad_source = changed(source, work_id=None, identity_reason=None)
for missing in ({"work_id": None}, {"edition_id": None}, {"work_id": None, "edition_id": None}):
    positive.append(changed(source, **missing, identity_reason="Identity unavailable in synthetic source"))
    for reason in (None, "", "   "):
        negative.append(changed(source, **missing, identity_reason=reason))
    item = changed(source, **missing)
    del item["identity_reason"]
    negative.append(item)

# Non-dataset checks may lack a snapshot, never all evidence.
for gate in ("E0", "E4", "E5", "E6", "E8"):
    for status in ("PASS", "FAIL"):
        case = gate_case(gate, status)
        positive.extend([case, changed(case, snapshot_ref=ref)])
        negative.extend([changed(case, artifact_ref=None), changed(case, output_refs=[]), changed(case, support=0), changed(case, value=None)])
for gate in ("E1", "E2", "E3", "E7"):
    for status in ("PASS", "FAIL"):
        case = gate_case(gate, status)
        negative.append(case)
        positive.append(changed(case, snapshot_ref=ref))
negative.extend([changed(evaluation, gate_id="FUTURE_GATE"), changed(evaluation, gate_id="FUTURE_GATE", snapshot_ref=ref)])
positive.append(changed(evaluation, gate_id="E1", status="NOT_COMPUTABLE", value=None, support=0, artifact_ref=None, output_refs=[], reviewer=None, reason="Dataset absent"))

# Every executed gate needs an attributable reviewer, including content-review gates.
for gate in ("E0", "E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8"):
    for status in ("PASS", "FAIL"):
        case = gate_case(gate, status, snapshot_ref=ref)
        positive.append(case)
        for reviewer in (None, "", "   "):
            negative.append(changed(case, reviewer=reviewer))
        missing = changed(case)
        del missing["reviewer"]
        negative.append(missing)

# Executed comparison gates cannot omit their control; zero remains legitimate.
for gate in ("E1", "E2", "E3"):
    for status in ("PASS", "FAIL"):
        case = gate_case(gate, status, snapshot_ref=ref, control_value=None)
        negative.append(case)
        positive.extend([gate_case(gate, status, snapshot_ref=ref),
                         changed(case, value=0.5 if status == 'PASS' else 0, control_value=0 if status == 'PASS' or gate != 'E3' else 0.5)])
        for invalid in ("frozen-baseline", "0.5", "", True, {}, []):
            negative.extend([changed(case, control_value=invalid), changed(case, value=invalid, control_value=0)])
        missing = changed(case)
        del missing["control_value"]
        negative.append(missing)
    positive.append(changed(evaluation, gate_id=gate, status="NOT_COMPUTABLE", reviewer=None))
for gate in ("E0", "E4", "E5", "E6", "E7", "E8"):
    for status in ("PASS", "FAIL"):
        positive.append(gate_case(gate, status, snapshot_ref=ref, control_value=None))

encoder = {"schema_version": "athanor.encoder.v1", "model_ref": None, "snapshot_ref": ref,
           "outcome": "unavailable", "family_id": None, "family_confidence": None,
           "lens_route": [], "reception_layer": None, "unbind": None,
           "epistemic": "NOT_COMPUTABLE", "reason": "Synthetic missing model", "efficacy": None}
positive.extend([encoder, changed(encoder, model_ref=ref), changed(encoder, model_ref=ref, outcome="out_of_domain"),
                 changed(encoder, model_ref=ref, outcome="classified", family_id="hermetic", family_confidence=0.5)])
negative.extend([changed(encoder, outcome="out_of_domain"),
                 changed(encoder, outcome="classified", family_id="hermetic", family_confidence=0.5)])

for disposition in ("ok", "historical_only", "refuse_or_historical_only"):
    positive.append(changed(encoder, disposition=disposition))
negative.extend(changed(encoder, disposition=value) for value in (None, "summon", 1, ""))
receipt = {"schema_version": "athanor.receipt.v1", "run_id": "synthetic", "workflow_id": "WF-004",
           "job_type": "gold_settle", "status": "SUCCEEDED", "started_at": "2026-09-13T00:00:00Z",
           "finished_at": "2026-09-13T00:00:01Z", "engine": "synthetic", "config_hash": H,
           "inputs": [ref], "outputs": [ref], "counts": {"gold": 1}, "errors": [], "epistemic": "OBSERVED"}
positive.append(receipt)
negative.append(changed(receipt, job_type="settlement"))
assert "job_type=gold_settle" in (ROOT / "specs/002-athanor-encoder/gold-settle.md").read_text(encoding="utf-8")

# Mutation controls prove each new conditional rejects its specific former hole.
for definition, bad in (("encoder", changed(encoder, outcome="out_of_domain")),
                        ("eval_result", changed(evaluation, gate_id="E1", snapshot_ref=ref))):
    mutant = copy.deepcopy(schema)
    key = next(k for k, item in mutant["$defs"].items()
               if item.get("properties", {}).get("schema_version", {}).get("const") == "athanor." + definition + ".v1")
    conditions = mutant["$defs"][key]["allOf"]
    index = next(i for i, condition in enumerate(conditions)
                 if (definition == "encoder" and "model_ref" in condition["if"]["properties"])
                 or (definition == "eval_result" and "control_value" in condition["then"]["properties"]
                     and condition["if"]["properties"].get("gate_id", {}).get("enum") == ["E1", "E2", "E3"]))
    conditions.pop(index)
    assert Draft202012Validator(mutant).is_valid(bad), "mutation control failed to reproduce original defect"
    assert not v.is_valid(bad), "corrected schema accepted original defect"

workflow = (ROOT / "specs/001-offline-retrieve/workflows.md").read_text(encoding="utf-8")
transition = next(line for line in workflow.splitlines() if line.startswith("| State transitions |"))
assert "athanor.error.v1 code UNSUPPORTED_QUERY on stderr and exit code 2" in transition
assert "packet outcome is MATCH, NO_MATCH or HISTORICAL_ONLY" in transition

for field in ("work_id", "edition_id"):
    for blank in ("", " ", "\t\n"):
        negative.append(changed(source, **{field: blank}))
negative.extend([changed(source, source_url="not a uri"), changed(source, observed_at="2026-02-30T00:00:00Z")])
for gate in ("E1", "E2", "E3", "E7"):
    for status in ("PASS", "FAIL"):
        base = changed(evaluation, gate_id=gate, status=status, snapshot_ref=ref, control_value=0)
        for boundary in (0, 1):
            if (gate in ('E1', 'E2') and status == 'FAIL'
                    or gate == 'E3' and status == 'PASS'
                    or gate == 'E7' and (status == 'PASS') == (boundary <= 0.25)):
                positive.append(changed(base, value=boundary, control_value=boundary))
            else:
                negative.append(changed(base, value=boundary, control_value=boundary))
        for invalid in (-0.01, 1.01, "balanced", True, float('nan'), float('inf')):
            negative.extend([changed(base, value=invalid), changed(base, control_value=invalid)])

handoff = {"schema_version": "athanor.handoff.v1", "pack_id": "synthetic", "intended_recipient_ref": "synthetic",
           "intended_use": "local-test", "approval_ref": ref,
           "artifacts": [{"path": "data/atoms.jsonl", "sha256": H, "license": "synthetic"}],
           "excluded_data_statement": "All real corpus data excluded", "reproduction_instructions": "synthetic only",
           "verification_refs": [ref]}
positive.append(handoff)
for path in ("../../private", "/root/file", "C:/file", "C:\\file", "a\\b", "./a", "a//b", "a/../b", "a/", "a.", "a ", "a%2fb", "CON.txt", "a/NUL", "a\n"):
    negative.append(changed(handoff, artifacts=[{"path": path, "sha256": H, "license": "synthetic"}]))
for second in ("data/atoms.jsonl", "DATA/ATOMS.JSONL", "data"):
    negative.append(changed(handoff, artifacts=handoff['artifacts'] + [{"path": second, "sha256": "b" * 64, "license": "synthetic"}]))

# Numeric gate status must match the existing strict/non-strict criteria.
for gate in ('E1', 'E2', 'E3'):
    for value, control, passes in ((0.6, 0.5, True), (0.5, 0.5, gate == 'E3'), (0.4, 0.5, False)):
        case = changed(evaluation, gate_id=gate, snapshot_ref=ref, value=value, control_value=control,
                       status='PASS' if passes else 'FAIL')
        positive.append(case)
        negative.append(changed(case, status='FAIL' if passes else 'PASS'))
for value, passes in ((0, True), (0.25, True), (0.2500000000001, False), (1, False)):
    case = changed(evaluation, gate_id='E7', snapshot_ref=ref, value=value, control_value=None,
                   status='PASS' if passes else 'FAIL')
    positive.append(case)
    negative.append(changed(case, status='FAIL' if passes else 'PASS'))

snapshot = {'schema_version': 'athanor.snapshot.v1', 'snapshot_id': 'synthetic',
            'row_manifest': ref, 'registry_ref': ref, 'config_hash': H, 'tokenizer_revision': 'synthetic',
            'grouping_version': 'synthetic', 'seed': 1,
            'split_ratios': {'train': 0.8, 'validation': 0.1, 'test': 0.1},
            'split_counts': {'train': 0, 'validation': 0, 'test': 0}, 'family_counts': {},
            'train_token_total': 0, 'train_family_tokens': {}, 'exclusion_manifest': ref, 'evidence_refs': []}
for ratios in ((0.8, 0.1, 0.1), (0.1, 0.2, 0.7), (1, 0, 0), (0.8, 0.1, 0.1000000000001)):
    positive.append(changed(snapshot, split_ratios=dict(zip(('train', 'validation', 'test'), ratios))))
for ratios in ((0.8, 0.8, 0.8), (0, 0, 0), (0.8, 0.1, 0.09), (0.8, 0.1, 0.10000000001)):
    negative.append(changed(snapshot, split_ratios=dict(zip(('train', 'validation', 'test'), ratios))))

for start, finish, passes in (
    ('2026-09-13T00:00:00Z', '2026-09-13T00:00:00Z', True),
    ('2026-09-13T00:00:00Z', '2026-09-12T23:59:59Z', False),
    ('2026-09-12T23:59:59.9Z', '2026-09-13T00:00:00Z', True),
    ('2026-09-13T00:00:00.10000001Z', '2026-09-13T00:00:00.10000000Z', False),
    ('2026-09-13T00:00:00.1Z', '2026-09-13T00:00:00.100Z', True),
):
    (positive if passes else negative).append(changed(receipt, started_at=start, finished_at=finish))

# Each former hole still passes bare schema validation, proving these semantic
# checks add protection rather than merely retesting a schema type error.
former_holes = [changed(evaluation, gate_id='E1', snapshot_ref=ref, value=0.5, control_value=0.5),
                changed(snapshot, split_ratios={'train': 0.8, 'validation': 0.8, 'test': 0.8}),
                changed(receipt, finished_at='2026-09-12T23:59:59Z')]
for bad in former_holes:
    assert v.is_valid(bad), 'former semantic defect not reproduced'
    assert not is_valid_contract(bad, schema), 'semantic defect still accepted'
for obj in positive:
    assert is_valid_contract(obj, schema), "positive rejected: " + repr(obj)
for obj in negative:
    assert not is_valid_contract(obj, schema), "negative accepted: " + repr(obj)
print(f"REVIEW_CONTRACTS_PASS positive={len(positive)} negative={len(negative)} workflow_consistency=PASS")

# Provenance: Notion Sprint 001 Hub [not inspected; prior Athanor Hub context] + Loop 805 Slice N/A + Hash: ab89a15d0ea4c39295f1918ddb521953ef1f6bbd (reviewed PR head)
