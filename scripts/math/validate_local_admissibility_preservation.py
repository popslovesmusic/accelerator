import json
import os
from datetime import datetime

def validate_admissibility_preservation():
    result_path = "validation/results/local_topology_evolution_audit.json"
    val_out_path = "validation/results/local_admissibility_preservation_validation_result.json"
    
    report = {
        "validation_id": "VAL-RLT-ADM-VALID-001",
        "status": "pass",
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(result_path):
        report["status"] = "warning"
        return report

    with open(result_path, 'r') as f:
        data = json.load(f)
        if not data.get("locality_preserved"):
             report["status"] = "fail"
             report["governance_violations"].append("locality preservation verification failed")

    with open(val_out_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_admissibility_preservation()
    print(json.dumps(res, indent=2))
