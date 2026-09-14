#!/usr/bin/env python3
"""Retired heuristic GOLD mutator; historical artifacts remain untouched.

The old helper stamped heuristic KEEP selections OBSERVED without independently
reviewed content-bound label decisions. Use WF-004 and DEC-001/003 instead.
No flag or environment variable enables the retired mutation path.
"""
import json


def main():
    print(json.dumps({
        "status": "HOLD", "reason": "HEURISTIC_GOLD_PROMOTION_RETIRED",
        "required": ["CONTENT_BOUND_LABEL_REVIEW", "AUTHENTICATED_SCOPED_APPROVAL"],
        "corpus_mutated": False, "gold_certification": "NOT_COMPUTABLE",
    }))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
