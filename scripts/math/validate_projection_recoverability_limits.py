import json
import os
from datetime import datetime

def validate_projection_recoverability_limits():
    registry_path = "registry/math/projection_recoverability_limits.json"
    result_path = "validation/results/projection_recoverability_limits_result.json"
    
    report = {
        "validation_id": "VAL-PRL-VALID-001",
        "status": "pass",
        "classes_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("projection recoverability limits registry missing")
        return report

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
        
    # 1. Governance Status Check
    gov = registry.get("governance_status", {})
    if gov.get("governance_status") != "CANDIDATE_RECOVERABILITY_LIMITS":
        report["status"] = "fail"
        report["governance_violations"].append("illegal governance status in registry")
    
    if gov.get("physics_status") != "NON_PHYSICAL_ANALOG_MODEL":
        report["status"] = "fail"
        report["governance_violations"].append("physics status must be NON_PHYSICAL_ANALOG_MODEL")

    if gov.get("theorem_status") != "NOT_PROVEN":
        report["status"] = "fail"
        report["governance_violations"].append("forbidden theorem status escalation")

    # 2. Core Rule Check
    rule = registry.get("core_rule", {})
    if rule.get("name") != "projection_non_recoverability_rule":
        report["status"] = "fail"
        report["governance_violations"].append("missing core non-recoverability rule")

    # 3. Class Check
    required_classes = ["RCOV-0", "RCOV-1", "RCOV-2", "RCOV-3"]
    registered_classes = [c["class_id"] for c in registry.get("recoverability_classes", [])]
    for rc in required_classes:
        if rc not in registered_classes:
            report["status"] = "fail"
            report["governance_violations"].append(f"required recoverability class missing: {rc}")
        else:
            report["classes_verified"] += 1

    # 4. Defaults Presence
    if not registry.get("projection_recoverability_defaults"):
        report["status"] = "fail"
        report["governance_violations"].append("missing projection recoverability defaults")

    # 5. Metadata for Reentry Presence
    if not registry.get("minimum_metadata_for_reentry"):
        report["status"] = "fail"
        report["governance_violations"].append("missing minimum metadata requirements for reentry")

    # 6. Forbidden Claims Check
    forbidden = registry.get("forbidden_claims", [])
    if not any("reconstructs ⇔R by itself" in u or "reconstructs source" in u.lower() for u in forbidden):
        report["status"] = "fail"
        report["governance_violations"].append("missing forbidden self-reconstruction claim check")

    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_projection_recoverability_limits()
    print(json.dumps(res, indent=2))
