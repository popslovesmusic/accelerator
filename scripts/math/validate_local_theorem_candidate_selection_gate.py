import json
import os
from datetime import datetime

def validate_selection_gate():
    registry_path = "registry/math/local_theorem_candidate_selection_registry.json"
    doc_path = "docs/math/local_theorem_candidate_selection_gate.md"
    result_path = "validation/results/local_theorem_candidate_selection_gate_result.json"
    
    report = {
        "validation_id": "VAL-LTC-GATE-001",
        "status": "pass",
        "candidates_found": 0,
        "selected_candidate": None,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing candidate selection registry")
        return report

    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing candidate selection document")

    with open(registry_path, 'r') as f:
        registry = json.load(f)
        report["candidates_found"] = len(registry["candidate_pool"])
        for candidate in registry["candidate_pool"]:
            if candidate["status"] == "SELECTED":
                report["selected_candidate"] = candidate["candidate_id"]
        
        # Check for NOT_PROVEN status
        if registry["governance"]["theorem_status"] != "NOT_PROVEN":
            report["status"] = "fail"
            report["governance_violations"].append("forbidden theorem status promotion")

    if not report["selected_candidate"]:
        report["status"] = "fail"
        report["governance_violations"].append("no candidate selected")

    # Final result
    with open(result_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_selection_gate()
    print(json.dumps(res, indent=2))
