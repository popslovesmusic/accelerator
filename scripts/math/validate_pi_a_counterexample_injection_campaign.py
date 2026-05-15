import json
import os
from datetime import datetime

def validate_campaign():
    registry_path = "registry/math/pi_a_counterexample_injection_registry.json"
    doc_path = "docs/math/pi_a_counterexample_injection_campaign.md"
    runner_path = "scripts/math/run_pi_a_counterexample_campaign.py"
    result_path = "validation/results/pi_a_counterexample_injection_campaign_result.json"
    
    report = {
        "validation_id": "VAL-LTC-CAMPAIGN-001",
        "status": "pass",
        "counterexample_classes_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing campaign registry")
        return report

    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing campaign document")

    if not os.path.exists(runner_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing campaign runner script")

    with open(registry_path, 'r') as f:
        registry = json.load(f)
        report["counterexample_classes_verified"] = len(registry["counterexample_classes"])
        
        # Check for NOT_PROVEN status
        if registry["governance"]["theorem_status"] != "NOT_PROVEN":
            report["status"] = "fail"
            report["governance_violations"].append("forbidden theorem status promotion in campaign")

        # Check for scope
        if registry["governance"]["scope_status"] != "STRICTLY_LOCAL_RESTRICTED_DOMAIN":
             report["status"] = "fail"
             report["governance_violations"].append("invalid scope status in campaign")

    # Check doc for mandatory rules
    expected_rules = [
        "counterexamples must not be deleted",
        "all failures must be logged",
        "restricted-domain scope must be preserved"
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
    res = validate_campaign()
    print(json.dumps(res, indent=2))
