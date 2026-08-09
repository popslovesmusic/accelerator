import json
import os
from datetime import datetime

def validate_topology_constraints():
    registry_path = "registry/math/topology_evolution_resumption_constraints.json"
    val_out_path = "validation/results/topology_resumption_constraints_validation_result.json"
    
    report = {
        "validation_id": "VAL-TER-REG-VALID-001",
        "status": "pass",
        "constraints_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        return report

    with open(registry_path, 'r') as f:
        registry = json.load(f)
        report["constraints_verified"] = len(registry["resumption_constraints"]["allowed"]) + len(registry["resumption_constraints"]["forbidden"])
        
        # Check for mandatory forbidden claims
        forbidden = registry["resumption_constraints"]["forbidden"]
        if "physical_unification_claims" not in forbidden or "proof_completion_claims" not in forbidden:
             report["status"] = "fail"
             report["governance_violations"].append("missing mandatory forbidden constraints (physics or proof completion)")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_topology_constraints()
    print(json.dumps(res, indent=2))
