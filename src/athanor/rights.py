from __future__ import annotations

from typing import Any


class RightsJoiner:
    def join(self, decision: dict[str, Any], reception: dict[str, Any] | None = None) -> dict[str, Any]:
        if reception is None or not reception.get("reception_scope"):
            raise ValueError("Missing reception scope")
        return {**decision, "reception": reception["reception_scope"], "rights": "OBSERVED"}
