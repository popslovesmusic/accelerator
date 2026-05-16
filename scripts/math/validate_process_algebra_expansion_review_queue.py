import json
import os
from datetime import datetime

def validate_process_algebra_expansion_review_queue():
    registry_path = "registry/math/process_algebra_expansion_review_queue.json"
    result_path = "validation/results/process_algebra_expansion_review_queue_result.json"
    
    report = {
        "validation_id": "VAL-PALG-QUEUE-VALID-001",
        "status": "pass",
        "queue_depth": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("queue registry missing")
        return report

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
        
    # 1. Queue Identification
    if registry.get("patch_id") != "MPF-PALG-010":
        report["status"] = "fail"
        report["governance_violations"].append("patch_id mismatch")

    # 2. Criteria Check
    if not registry.get("review_criteria"):
        report["status"] = "fail"
        report["governance_violations"].append("missing review criteria in registry")

    # 3. Item Validation
    queue = registry.get("queue", [])
    report["queue_depth"] = len(queue)
    for item in queue:
        required_fields = ["proposal_id", "expression", "status", "source_relation", "non_separability_acknowledged"]
        for field in required_fields:
            if field not in item:
                report["status"] = "fail"
                report["governance_violations"].append(f"item {item.get('proposal_id', 'unknown')} missing required field: {field}")
        
        if item.get("non_separability_acknowledged") is not True:
             report["status"] = "fail"
             report["governance_violations"].append(f"item {item.get('proposal_id')} failed non-separability acknowledgment")

    # 4. Governance Status
    gov = registry.get("governance_status", {})
    if gov.get("physics_status") != "NON_PHYSICAL_ANALOG_MODEL":
        report["status"] = "fail"
        report["governance_violations"].append("physics status must be NON_PHYSICAL_ANALOG_MODEL")
    if gov.get("theorem_status") != "NOT_PROVEN":
        report["status"] = "fail"
        report["governance_violations"].append("forbidden theorem status escalation")

    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_process_algebra_expansion_review_queue()
    print(json.dumps(res, indent=2))
