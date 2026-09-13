"""Reusable advisory contract regressions; no Git history, runtime or network needed."""
import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
REL = "specs/contracts/proposed.v1.schema.json"
schema = json.loads((ROOT / REL).read_text(encoding="utf-8"))
Draft202012Validator.check_schema(schema)
v = Draft202012Validator(schema)
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
        case = changed(evaluation, gate_id=gate, status=status, control_value=0)
        positive.extend([case, changed(case, snapshot_ref=ref)])
        negative.extend([changed(case, artifact_ref=None), changed(case, output_refs=[]), changed(case, support=0), changed(case, value=None)])
for gate in ("E1", "E2", "E3", "E7"):
    for status in ("PASS", "FAIL"):
        case = changed(evaluation, gate_id=gate, status=status, control_value=0)
        negative.append(case)
        positive.append(changed(case, snapshot_ref=ref))
negative.extend([changed(evaluation, gate_id="FUTURE_GATE"), changed(evaluation, gate_id="FUTURE_GATE", snapshot_ref=ref)])
positive.append(changed(evaluation, gate_id="E1", status="NOT_COMPUTABLE", value=None, support=0, artifact_ref=None, output_refs=[], reviewer=None, reason="Dataset absent"))

# Every executed gate needs an attributable reviewer, including content-review gates.
for gate in ("E0", "E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8"):
    for status in ("PASS", "FAIL"):
        case = changed(evaluation, gate_id=gate, status=status, snapshot_ref=ref, control_value=0)
        positive.append(case)
        for reviewer in (None, "", "   "):
            negative.append(changed(case, reviewer=reviewer))
        missing = changed(case)
        del missing["reviewer"]
        negative.append(missing)

# Executed comparison gates cannot omit their control; zero remains legitimate.
for gate in ("E1", "E2", "E3"):
    for status in ("PASS", "FAIL"):
        case = changed(evaluation, gate_id=gate, status=status, snapshot_ref=ref)
        negative.append(case)
        positive.extend([changed(case, control_value=0), changed(case, control_value="frozen-baseline")])
        missing = changed(case)
        del missing["control_value"]
        negative.append(missing)
    positive.append(changed(evaluation, gate_id=gate, status="NOT_COMPUTABLE", reviewer=None))
for gate in ("E0", "E4", "E5", "E6", "E7", "E8"):
    for status in ("PASS", "FAIL"):
        positive.append(changed(evaluation, gate_id=gate, status=status, snapshot_ref=ref, control_value=None))

encoder = {"schema_version": "athanor.encoder.v1", "model_ref": None, "snapshot_ref": ref,
           "outcome": "unavailable", "family_id": None, "family_confidence": None,
           "lens_route": [], "reception_layer": None, "unbind": None,
           "epistemic": "NOT_COMPUTABLE", "reason": "Synthetic missing model", "efficacy": None}
positive.extend([encoder, changed(encoder, model_ref=ref), changed(encoder, model_ref=ref, outcome="out_of_domain"),
                 changed(encoder, model_ref=ref, outcome="classified", family_id="hermetic", family_confidence=0.5)])
negative.extend([changed(encoder, outcome="out_of_domain"),
                 changed(encoder, outcome="classified", family_id="hermetic", family_confidence=0.5)])

# Mutation controls prove each new conditional rejects its specific former hole.
for definition, bad in (("encoder", changed(encoder, outcome="out_of_domain")),
                        ("eval_result", changed(evaluation, gate_id="E1", snapshot_ref=ref))):
    mutant = copy.deepcopy(schema)
    key = next(k for k, item in mutant["$defs"].items()
               if item.get("properties", {}).get("schema_version", {}).get("const") == "athanor." + definition + ".v1")
    mutant["$defs"][key]["allOf"].pop()
    assert Draft202012Validator(mutant).is_valid(bad), "mutation control failed to reproduce original defect"
    assert not v.is_valid(bad), "corrected schema accepted original defect"

workflow = (ROOT / "specs/001-offline-retrieve/workflows.md").read_text(encoding="utf-8")
transition = next(line for line in workflow.splitlines() if line.startswith("| State transitions |"))
assert "athanor.error.v1 code UNSUPPORTED_QUERY on stderr and exit code 2" in transition
assert "packet outcome is MATCH, NO_MATCH or HISTORICAL_ONLY" in transition

for obj in positive:
    assert v.is_valid(obj), "positive rejected: " + repr(obj)
for obj in negative:
    assert not v.is_valid(obj), "negative accepted: " + repr(obj)
print(f"REVIEW_CONTRACTS_PASS positive={len(positive)} negative={len(negative)} workflow_consistency=PASS")

# Provenance: Notion Sprint 001 Hub [not inspected; prior Athanor Hub context] + Loop 805 Slice N/A + Hash: ab89a15d0ea4c39295f1918ddb521953ef1f6bbd (reviewed PR head)
