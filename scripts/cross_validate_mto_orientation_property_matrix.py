"""Independent cross-check of exhaustive provisional orientation property coverage."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "departments/research/reports/RT_INDUCTION_MTO_OTM_CALCULUS_001_property_matrix_result.json"
OUT = ROOT / "departments/research/reports/RT_INDUCTION_MTO_OTM_CALCULUS_001_property_matrix_cross_validation.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    cases = report.get("cases", [])
    active = [case for case in cases if case.get("active")]
    expected_active = {
        ("C_ORI_002", left, right, "valid_joint_admissibility_witness")
        for left in ("o_1", "o_2") for right in ("o_1", "o_2")
    }
    expected_active.add(("C_ORI_003", "o_1", "o_2", "valid_typed_order_witness"))
    expected_active |= {
        ("C_ORI_004", left, right, "valid_exclusive_conflict_witness")
        for left in ("o_1", "o_2") for right in ("o_1", "o_2")
    }
    observed_active = {(case["context_id"], case["left"], case["right"], case["evidence"]) for case in active}
    checks = {
        "status_pass": report.get("status") == "PASS_BOUNDED_PROPERTY_MATRIX",
        "case_count_252": report.get("case_count") == 252,
        "active_count_9": report.get("active_case_count") == 9,
        "rejected_count_243": report.get("rejected_case_count") == 243,
        "active_signatures_exact": observed_active == expected_active,
        "activation_disabled": report.get("witness_activation") == "DISABLED" and report.get("mto_selection") == "DISABLED",
        "no_unresolved_case_active": all(case["active"] is False or case["result"] in {"COMPATIBLE", "ORDERED", "CONFLICT"} for case in cases),
    }
    passed = all(checks.values())
    payload = {
        "report_id": "RT_INDUCTION_MTO_OTM_CALCULUS_001_PROPERTY_MATRIX_CROSS_VALIDATION_001",
        "status": "PASS_PROPERTY_MATRIX_CROSS_VALIDATION" if passed else "FAIL_PROPERTY_MATRIX_CROSS_VALIDATION",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "witness_activation": "DISABLED",
        "mto_selection": "DISABLED",
        "canonical_math_modified": False,
        "nonclaims": ["This cross-check validates bounded coverage and safety invariants only."],
    }
    if args.run:
        OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
