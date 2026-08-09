import json
import os
from datetime import datetime

def validate_resumption_non_globalization():
    doc_path = "docs/math/governed_resumption_readiness_gate.md"
    result_path = "validation/results/resumption_non_globalization_validation_result.json"
    
    report = {
        "validation_id": "VAL-GRR-GLOB-VALID-001",
        "status": "pass",
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(doc_path):
        report["status"] = "fail"
        return report

    with open(doc_path, 'r') as f:
        content = f.read().lower()
        if "global topology theorems" not in content or "forbidden" not in content:
             report["status"] = "fail"
             report["governance_violations"].append("missing global theorem block in documentation")

    with open(result_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_resumption_non_globalization()
    print(json.dumps(res, indent=2))
