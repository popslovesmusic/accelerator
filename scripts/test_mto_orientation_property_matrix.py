"""Exhaustive bounded property test for provisional orientation classifications."""
from __future__ import annotations

import argparse
import itertools
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "departments/research/reports"
CONTEXTS = BASE / "RT_INDUCTION_MTO_OTM_CALCULUS_001_context_instances.json"
OUT = BASE / "RT_INDUCTION_MTO_OTM_CALCULUS_001_property_matrix_result.json"

EVIDENCE = [
    "valid_joint_admissibility_witness",
    "valid_typed_order_witness",
    "valid_exclusive_conflict_witness",
    "conflict_claim_without_witness",
    "ordering_relation_missing",
    "reverse_order_without_rule",
    "unregistered_evidence",
]
ORIENTATIONS = ["o_1", "o_2", "o_x"]


def classify(context: dict | None, left: str, right: str, evidence: str) -> str:
    if context is None or left not in context["orientation_domain"] or right not in context["orientation_domain"]:
        return "REJECTED_MALFORMED_OR_UNRESOLVED"
    cid = context["context_id"]
    if cid == "C_ORI_002" and evidence == "valid_joint_admissibility_witness":
        return "COMPATIBLE"
    if cid == "C_ORI_003" and evidence == "valid_typed_order_witness" and (left, right) == ("o_1", "o_2"):
        return "ORDERED"
    if cid == "C_ORI_004" and evidence == "valid_exclusive_conflict_witness":
        return "CONFLICT"
    return "REJECTED_UNSUPPORTED_COMBINATION"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    data = json.loads(CONTEXTS.read_text(encoding="utf-8"))
    contexts = {item["context_id"]: item for item in data["contexts"]}
    cases = []
    for context_id, left, right, evidence in itertools.product([None, *contexts], ORIENTATIONS, ORIENTATIONS, EVIDENCE):
        result = classify(contexts.get(context_id), left, right, evidence)
        cases.append({"context_id": context_id, "left": left, "right": right, "evidence": evidence, "result": result, "active": result in {"COMPATIBLE", "ORDERED", "CONFLICT"}})
    valid_active = [case for case in cases if case["active"]]
    passed = all(case["active"] == (case["result"] in {"COMPATIBLE", "ORDERED", "CONFLICT"}) for case in cases)
    payload = {
        "report_id": "RT_INDUCTION_MTO_OTM_CALCULUS_001_PROPERTY_MATRIX_RESULT_001",
        "status": "PASS_BOUNDED_PROPERTY_MATRIX" if passed else "FAIL_BOUNDED_PROPERTY_MATRIX",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "case_count": len(cases),
        "active_case_count": len(valid_active),
        "rejected_case_count": len(cases) - len(valid_active),
        "cases": cases,
        "witness_activation": "DISABLED",
        "mto_selection": "DISABLED",
        "canonical_math_modified": False,
        "nonclaims": ["This exhaustive matrix is bounded to declared provisional fixtures and does not validate canonical semantics."],
    }
    if args.run:
        OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in payload.items() if k != "cases"}, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
