import json
import os
from datetime import datetime

def validate_atlas():
    registry_path = "registry/math/pi_a_counterexample_reconciliation_atlas.json"
    doc_path = "docs/math/pi_a_counterexample_reconciliation_atlas.md"
    result_path = "validation/results/pi_a_counterexample_reconciliation_atlas_result.json"
    
    report = {
        "validation_id": "VAL-LTC-ATLAS-001",
        "status": "pass",
        "counterexamples_reconciled": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing reconciliation atlas registry")
        return report

    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing reconciliation atlas document")

    with open(registry_path, 'r') as f:
        registry = json.load(f)
        report["counterexamples_reconciled"] = len(registry["counterexample_reconciliation_entries"])
        
        # Check for NOT_PROVEN status
        if registry["governance"]["theorem_status"] != "NOT_PROVEN":
            report["status"] = "fail"
            report["governance_violations"].append("forbidden theorem status promotion in atlas")

        # Check for discharge status
        for entry in registry["counterexample_reconciliation_entries"]:
            if entry["discharge_status"] != "NOT_DISCHARGED":
                report["status"] = "fail"
                report["governance_violations"].append(f"forbidden discharge for CE {entry['counterexample_id']}")

    # Check doc for mandatory rules
    expected_rules = [
        "reconciliation is not discharge",
        "counterexamples are structural information",
        "strictly_local_restricted_domain"
    ]
    with open(doc_path, 'r') as f:
        content = f.read().lower()
        for rule in expected_rules:
            if rule not in content:
                report["status"] = "fail"
                report["governance_violations"].append(f"missing mandatory rule: {rule}")

    # Final result
    with open(result_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_atlas()
    print(json.dumps(res, indent=2))
