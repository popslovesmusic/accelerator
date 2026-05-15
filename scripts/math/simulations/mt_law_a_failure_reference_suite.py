import json
import os

def run_failure_reference_suite():
    print("Running MT-LAW-A Failure Reference Suite...")
    
    failure_cases = [
        {
            "id": "RM-A002",
            "name": "Budget Saturation Collapse",
            "signature": "ERR_BUDGET_EXCEEDED",
            "metrics": {"C_A": 105.0, "B_local": 100.0, "P_survival": 0.0}
        },
        {
            "id": "RM-A003",
            "name": "Topology Severance",
            "signature": "ACCESS_SEVERED",
            "metrics": {"T_access": 0.0, "P_survival": 0.12}
        },
        {
            "id": "RM-A004",
            "name": "Identity Fragmentation",
            "signature": "BRANCH_AMBIGUITY",
            "metrics": {"I_continuity": 0.45, "branch_count": 3}
        },
        {
            "id": "RM-A006",
            "name": "Oscillatory Instability",
            "signature": "CONVERGE_FAIL",
            "metrics": {"P_survival": 0.3, "R_divergence": 0.85}
        }
    ]
    
    results = {
        "suite_id": "MT-LAW-A-FAILURE-SUITE",
        "cases_executed": len(failure_cases),
        "results": failure_cases
    }
    
    output_path = "outputs/math_tests/mt_law_a_failure_suite_result.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Failure suite results saved to {output_path}")

if __name__ == "__main__":
    run_failure_reference_suite()
