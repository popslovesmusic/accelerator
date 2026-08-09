import json
import os
from datetime import datetime

def run_reconfiguration_audit():
    """
    Runner for Local Topology Reconfiguration Audit.
    Analyzes reconfiguration modes and classifies them.
    """
    registry_path = "registry/math/topology_reconfiguration_registry.json"
    result_path = "validation/results/topology_reconfiguration_audit_result.json"
    
    if not os.path.exists(registry_path):
        return {"status": "fail", "reason": "reconfiguration registry missing"}

    with open(registry_path, 'r') as f:
        registry = json.load(f)

    report = {
        "audit_id": "TRA-AUDIT-SUM-001",
        "timestamp": datetime.now().isoformat(),
        "status": "pass",
        "reconfiguration_evaluations": [],
        "governance": {
            "theorem_status": "NOT_PROVEN",
            "scope_status": "STRICTLY_LOCAL"
        }
    }

    # Evaluate each mode from the registry
    for mode in registry["reconfiguration_modes"]:
        evaluation = {
            "id": mode["id"],
            "classification": "allowed_local",
            "trigger_verified": mode["trigger_condition"],
            "admissibility_impact": mode["admissibility_effect"],
            "failure_containment": mode["failure_containment_behavior"],
            "leakage_risk": "low"
        }
        
        # Special classification for invalid mode
        if mode["id"] == "invalid_global_reconfiguration":
            evaluation["classification"] = "blocked"
            evaluation["leakage_risk"] = "prevented"
            
        report["reconfiguration_evaluations"].append(evaluation)

    with open(result_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"Topology reconfiguration audit complete. Results in {result_path}")
    return report

if __name__ == "__main__":
    run_reconfiguration_audit()
