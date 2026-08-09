import json
import os
from datetime import datetime

def validate_projection_failure_mode_atlas():
    registry_path = "registry/math/projection_failure_mode_atlas.json"
    result_path = "validation/results/projection_failure_mode_atlas_result.json"
    
    report = {
        "validation_id": "VAL-PFM-VALID-001",
        "status": "pass",
        "modes_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("projection failure mode atlas registry missing")
        return report

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
        
    # 1. Atlas Identification
    if registry.get("atlas_status") != "CANDIDATE_FAILURE_MODE_ATLAS":
        report["status"] = "fail"
        report["governance_violations"].append("illegal atlas status in registry")

    # 2. Failure Mode Completeness Check
    modes = registry.get("failure_mode_classes", [])
    required_mode_subsets = [
        "equality", "implication", "composition", "biconditional",
        "geometry", "persistence", "orientation", "physical_escalation"
    ]
    
    mode_names_lower = " ".join([m["name"].lower() for m in modes])
    for rs in required_mode_subsets:
        if rs not in mode_names_lower:
            report["status"] = "fail"
            report["governance_violations"].append(f"required failure mode category missing: {rs}")
        else:
            report["modes_verified"] += 1

    # 3. Critical Severity Check
    critical_modes = [m for m in modes if m.get("severity") == "CRITICAL"]
    if not critical_modes:
        report["status"] = "fail"
        report["governance_violations"].append("no critical failure modes identified in atlas")

    # 4. Mitigation and Schema Check
    if not registry.get("failure_record_schema"):
        report["status"] = "fail"
        report["governance_violations"].append("missing failure record schema")

    if not registry.get("mitigation_rules"):
        report["status"] = "fail"
        report["governance_violations"].append("missing mitigation rules in registry")

    # 5. Forbidden Uses Check
    forbidden = registry.get("forbidden_uses", [])
    if not any("physical evidence" in u.lower() for u in forbidden):
        report["status"] = "fail"
        report["governance_violations"].append("missing forbidden physical evidence check")

    # 6. Governance Status Invariants
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
    res = validate_projection_failure_mode_atlas()
    print(json.dumps(res, indent=2))
