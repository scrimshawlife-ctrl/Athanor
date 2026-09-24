# tests/test_settlement.py
import pytest
from pathlib import Path
from athanor.settlement import SettlementExecutor

def test_settlement_executor_rejects_unapproved(tmp_path: Path):
    # Minimal input: proposals + no approval
    proposals = tmp_path / "proposals.jsonl"
    proposals.write_text('{"row_id": "a1", "decision": "KEEP", "approved": false}\n')
    executor = SettlementExecutor()
    with pytest.raises(ValueError, match="No approval"):
        executor.apply(proposals, approval_ref=None)
    # Expected: raises, no manifest created
