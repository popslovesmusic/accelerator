#!/usr/bin/env python3
"""Run finite negative tests against the RT orientation boundary contracts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT = ROOT / "docs/theory/foundational/5_03_26 unity/math/notes/0032_rt_orientation_boundary_coupling_contracts_adversarial_review_report.json"


CASES = [
    ("ADV-ROLE-001", "identity drift is rejected", "identity_invariant", {"same_rt_id": True, "identity_preserved": False}),
    ("ADV-SUFF-001", "premature primitive stopping is rejected", "primitive_sufficiency", {"closed": False, "sufficient": True}),
    ("ADV-ORDER-001", "unjustified byte permutation is rejected", "ordered_surface", {"permutation": [2, 1, 0], "declared_order_trace": False}),
    ("ADV-COUPLE-001", "interior transport is rejected", "boundary_no_transport", {"coupling_site": "boundary", "interior_transfer": True}),
    ("ADV-PROP-001", "cross-RT propagation is rejected", "internal_carrier", {"carrier": "RT-1", "target_carrier": "RT-2", "cross_boundary_transfer": True}),
    ("ADV-CLOSE-001", "closure order loss is rejected", "closure_order", {"children": ["p1", "p2", "p3"], "output_order": ["p2", "p1", "p3"]}),
    ("ADV-EVAL-001", "scalar primitive evaluation is rejected", "orientation_field", {"evaluation_output_type": "scalar", "scalar_magnitude": 1}),
    ("ADV-BOUNDARY-001", "missing boundary condition is rejected", "boundary_condition", {"boundary_update": False}),
    ("ADV-ALIGN-001", "invalid reference alignment is rejected", "reference_alignment", {"alignment_status": "unresolved"}),
    ("ADV-ID-001", "duplicate child identity is rejected", "child_identity", {"children": ["RT-1", "RT-1"]}),
    ("ADV-DEPTH-001", "invalid bit depth is rejected", "bit_depth", {"bit_depth": -1}),
    ("ADV-DENSITY-001", "density loss during closure is rejected", "closure_density", {"density_before": 4, "density_after": 3}),
    ("ADV-ZERO-DOF-001", "zero-DOF active continuation is rejected", "zero_dof", {"dof": 0, "state": "active"}),
    ("ADV-MTO-OTM-001", "invalid MTO-OTM transition is rejected", "mto_otm", {"input_cardinality": "many", "output_cardinality": "many"}),
]


def reject(case: dict) -> tuple[bool, str]:
    contract = case["contract"]
    value = case["value"]
    if contract == "identity_invariant":
        rejected = value["same_rt_id"] and not value["identity_preserved"]
    elif contract == "primitive_sufficiency":
        rejected = not (value["closed"] and value["sufficient"])
    elif contract == "ordered_surface":
        rejected = value["permutation"] != list(range(len(value["permutation"]))) and not value["declared_order_trace"]
    elif contract == "boundary_no_transport":
        rejected = value["coupling_site"] == "boundary" and value["interior_transfer"]
    elif contract == "internal_carrier":
        rejected = value["carrier"] != value["target_carrier"] or value["cross_boundary_transfer"]
    elif contract == "closure_order":
        rejected = value["children"] != value["output_order"]
    elif contract == "orientation_field":
        rejected = value["evaluation_output_type"] == "scalar" or value["scalar_magnitude"] is not None
    elif contract == "boundary_condition":
        rejected = not value["boundary_update"]
    elif contract == "reference_alignment":
        rejected = value["alignment_status"] != "resolved"
    elif contract == "child_identity":
        rejected = len(value["children"]) != len(set(value["children"]))
    elif contract == "bit_depth":
        rejected = value["bit_depth"] < 0
    elif contract == "closure_density":
        rejected = value["density_after"] != value["density_before"]
    elif contract == "zero_dof":
        rejected = value["dof"] == 0 and value["state"] == "active"
    elif contract == "mto_otm":
        rejected = (value["input_cardinality"], value["output_cardinality"]) not in {("many", "one"), ("one", "many")}
    else:
        return False, f"unknown contract: {contract}"
    return rejected, "REJECTED" if rejected else "invalid case escaped contract"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    results = []
    for case_id, name, contract, value in CASES:
        rejected, detail = reject({"contract": contract, "value": value})
        results.append({"case_id": case_id, "name": name, "status": "REJECTED" if rejected else "ESCAPED", "detail": detail})
    escaped = [item for item in results if item["status"] == "ESCAPED"]
    report = {
        "report_id": "0032_rt_orientation_boundary_coupling_contracts_adversarial_review_report",
        "fixture_set_id": "0032_rt_orientation_boundary_coupling_contracts_fixtures",
        "review_type": "finite_negative_contract_review",
        "status": "PASS" if not escaped else "FAIL",
        "claim_ceiling": "C1",
        "case_count": len(results),
        "rejected_count": len(results) - len(escaped),
        "escaped_count": len(escaped),
        "results": results,
        "limitations": [
            "This finite review tests deliberately invalid contract inputs only.",
            "It is not a proof of the RT framework or of physical boundary behavior.",
            "It does not test unbounded recursion, geometry, transport, or external systems.",
        ],
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 1 if escaped else 0


if __name__ == "__main__":
    raise SystemExit(main())
