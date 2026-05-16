import json
import os
from datetime import datetime

def validate_aspect_non_separability_principle():
    registry_path = "registry/math/aspect_non_separability_principle_registry.json"
    result_path = "validation/results/aspect_non_separability_principle_result.json"
    
    report = {
        "validation_id": "VAL-PRIN-ANSP-VALID-001",
        "status": "pass",
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("principle registry missing")
        return report

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
        
    # 1. Core Identification
    if registry.get("status") != "CANDIDATE_FOUNDATIONAL_PRINCIPLE":
        report["status"] = "fail"
        report["governance_violations"].append("illegal final principle status")

    # 2. Rule Presence
    formal = registry.get("formal_seed", {})
    required_rules = ["non_separable_relation_form", "projection_rule", "ontological_rule", "non_fragmentation_rule"]
    for rule in required_rules:
        if rule not in formal:
            report["status"] = "fail"
            report["governance_violations"].append(f"missing formal rule: {rule}")

    # 3. Forbidden Claims
    forbidden = registry.get("forbidden_uses", [])
    if not any("external glue operator" in u for u in forbidden):
        report["status"] = "fail"
        report["governance_violations"].append("missing forbidden external glue operator check")
    if not any("physical nonlocality" in u for u in forbidden):
        report["status"] = "fail"
        report["governance_violations"].append("missing forbidden physical nonlocality check")

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
    res = validate_aspect_non_separability_principle()
    print(json.dumps(res, indent=2))
