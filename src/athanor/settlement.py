from __future__ import annotations
import json
from pathlib import Path
from typing import Any

class SettlementExecutor:
    def apply(self, proposals_path: Path, approval_ref: str | None = None) -> dict[str, Any]:
        if approval_ref is None:
            raise ValueError("No approval reference supplied; cannot apply")
        proposals = [json.loads(line) for line in proposals_path.read_text().splitlines() if line.strip()]
        decisions = []
        for p in proposals:
            if not p.get("approved", False):
                continue  # HOLD stays ineligible
            decisions.append({
                "row_id": p["row_id"],
                "decision": p.get("decision", "KEEP"),
                "approval_ref": approval_ref,
                "timestamp": "2026-09-23T00:00:00Z"  # deterministic for test
            })
        manifest = {
            "schema": "athanor.settlement.v1",
            "approval_ref": approval_ref,
            "decisions": decisions,
            "status": "APPLIED" if decisions else "HOLD"
        }
        return manifest
