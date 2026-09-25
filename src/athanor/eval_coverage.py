from __future__ import annotations

from typing import Any


def compute_coverage(fam_counts: dict[str, int], min_support: int = 50) -> dict[str, Any]:
    unsupported = [f for f, n in fam_counts.items() if n < min_support]
    status = "COMPLETE" if not unsupported else "INCOMPLETE"
    return {"status": status, "unsupported": unsupported, "min_support": min_support}
