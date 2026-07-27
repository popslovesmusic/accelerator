import json
from pathlib import Path

from pi_a_local_adapter import PiALocalAdapter


OUTPUT = Path(__file__).with_name("pi_a_bound_adapter_review.json")


def main():
    adapter = PiALocalAdapter()
    cases = [
        {"id": "missing_projection_scope", "obligation": "PO-010-001", "input": {"already_in_Im_Pi_A": True, "admissibility_budget_non_exhausted": True}, "expected": "INVALID_INPUT_CONTRACT"},
        {"id": "missing_composition_signature", "obligation": "PO-010-002", "input": {"MT_001_dependency_active": True, "composition_scope_local_only": True}, "expected": "INVALID_INPUT_CONTRACT"},
        {"id": "missing_failure_inventory", "obligation": "PO-010-003", "input": {"failure_geometry_links_present": True, "excluded_domains_declared": True}, "expected": "INVALID_INPUT_CONTRACT"},
        {"id": "closed_budget", "obligation": "PO-010-001", "input": {"already_in_Im_Pi_A": True, "local_domain_declared": True, "admissibility_budget_non_exhausted": False}, "expected": "MEMBERSHIP_NOT_ESTABLISHED"},
        {"id": "untyped_composition", "obligation": "PO-010-002", "input": {"MT_001_dependency_active": True, "Pi_A_signature_typed": False, "composition_scope_local_only": True}, "expected": "COMPOSITION_BLOCKED"},
        {"id": "missing_counterexample_discharge", "obligation": "PO-010-003", "input": {"failure_geometry_links_present": True, "excluded_domains_declared": True, "counterexamples_not_discharged": False}, "expected": "EXCLUSION_BLOCKED"}
    ]
    outcomes = []
    for case in cases:
        actual = adapter.evaluate(case)
        outcomes.append({"id": case["id"], "expected": case["expected"], "actual": actual, "match": actual == case["expected"]})
    result = {
        "review_id": "PI_A_BOUND_ADAPTER_REVIEW_20260726_001",
        "status": "PASS_FAIL_CLOSED_REVIEW" if all(item["match"] for item in outcomes) else "FAIL",
        "cases_passed": sum(item["match"] for item in outcomes),
        "cases_total": len(outcomes),
        "outcomes": outcomes,
        "claim_boundary": "Review covers adapter contract behavior only; it does not discharge Pi_A proof obligations."
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
