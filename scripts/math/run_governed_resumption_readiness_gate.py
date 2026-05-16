import json
import os
from datetime import datetime

def run_resumption_gate():
    """
    Runner for Governed Resumption Readiness Gate.
    Integrates prior audit results to make a resumption decision.
    """
    drift_result = "validation/results/recursive_governance_drift_audit_result.json"
    stress_result = "validation/results/recursive_containment_stress_results.json"
    stab_result = "validation/results/adaptive_incompleteness_stabilization_results.json"
    climate_result = "validation/results/epistemic_climate_regulation_results.json"
    result_path = "validation/results/governed_resumption_readiness_result.json"
    
    report = {
        "gate_summary_id": "GRR-AUDIT-SUM-001",
        "timestamp": datetime.now().isoformat(),
        "readiness_status": "resume_denied",
        "component_verifications": {},
        "decision_rationales": [],
        "governance_compliance": True
    }

    # Helper to check if file exists and status is pass
    def check_pass(path):
        if not os.path.exists(path): return False
        with open(path, 'r') as f:
            data = json.load(f)
            return data.get("status") == "pass"

    report["component_verifications"] = {
        "MPF-RES-005": check_pass(drift_result),
        "MPF-RES-006": check_pass(stress_result),
        "MPF-RES-007": check_pass(stab_result),
        "MPF-RES-009": check_pass(climate_result)
    }

    if all(report["component_verifications"].values()):
        report["readiness_status"] = "resume_limited_local_only"
        report["decision_rationales"].append("All required governance components passed.")
    else:
        report["readiness_status"] = "resume_denied"
        report["decision_rationales"].append("One or more governance components failed or missing.")

    with open(result_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"Resumption Readiness Gate complete. Results in {result_path}")
    return report

if __name__ == "__main__":
    run_resumption_gate()
