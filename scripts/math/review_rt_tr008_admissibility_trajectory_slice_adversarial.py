#!/usr/bin/env python3
"""Run finite negative tests against the TR-008 interface contracts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT = ROOT / "docs/theory/foundational/5_03_26 unity/math/notes/0033_rt_tr008_admissibility_trajectory_slice_adversarial_review_report.json"

CASES = [
    ("ADV-TR008-CTX-001", "proposition context drift is rejected", "context", {"declared": "P-health", "observed": "P-network"}),
    ("ADV-TR008-END-001", "trajectory start drift is rejected", "endpoints", {"trajectory": ["X", "m1", "B"], "start": "A", "stop": "B"}),
    ("ADV-TR008-END-002", "trajectory stop drift is rejected", "endpoints", {"trajectory": ["A", "m1", "X"], "start": "A", "stop": "B"}),
    ("ADV-TR008-DUP-001", "duplicate transition marker is rejected", "duplicate", {"trajectory": ["A", "m1", "m1", "B"]}),
    ("ADV-TR008-EDGE-001", "undeclared transition edge is rejected", "edge", {"trajectory": ["A", "m2", "B"], "declared_edges": [["A", "m1"], ["m1", "B"]]}),
    ("ADV-TR008-IFACE-001", "undeclared interface is rejected", "interface", {"interface": "face-9", "known": ["face-1", "face-2"]}),
    ("ADV-TR008-ORDER-001", "slice order mutation is rejected", "order", {"positions": [1, 0, 2], "declared": [0, 1, 2]}),
    ("ADV-TR008-EMPTY-001", "empty trajectory is rejected", "empty", {"trajectory": []}),
]


def rejects(contract: str, value: dict) -> bool:
    if contract == "context":
        return value["declared"] != value["observed"]
    if contract == "endpoints":
        return value["trajectory"][0] != value["start"] or value["trajectory"][-1] != value["stop"]
    if contract == "duplicate":
        return len(value["trajectory"]) != len(set(value["trajectory"]))
    if contract == "edge":
        return any(list(edge) not in value["declared_edges"] for edge in zip(value["trajectory"], value["trajectory"][1:]))
    if contract == "interface":
        return value["interface"] not in value["known"]
    if contract == "order":
        return value["positions"] != value["declared"]
    if contract == "empty":
        return not value["trajectory"]
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    results = []
    for case_id, name, contract, value in CASES:
        rejected = rejects(contract, value)
        results.append({"case_id": case_id, "name": name, "status": "REJECTED" if rejected else "ESCAPED", "detail": "REJECTED" if rejected else "invalid case escaped contract"})
    escaped = [item for item in results if item["status"] == "ESCAPED"]
    report = {
        "report_id": "0033_rt_tr008_admissibility_trajectory_slice_adversarial_review_report",
        "fixture_set_id": "0033_rt_tr008_admissibility_trajectory_slice_fixtures",
        "review_type": "finite_negative_contract_review",
        "status": "PASS" if not escaped else "FAIL",
        "claim_ceiling": "C1",
        "case_count": len(results),
        "rejected_count": len(results) - len(escaped),
        "escaped_count": len(escaped),
        "results": results,
        "limitations": [
            "This finite review tests deliberately invalid interface inputs only.",
            "It does not establish physical geometry, geodesics, causality, or topology.",
            "It does not test density redistribution or downstream RT reconstruction."
        ]
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 1 if escaped else 0


if __name__ == "__main__":
    raise SystemExit(main())
