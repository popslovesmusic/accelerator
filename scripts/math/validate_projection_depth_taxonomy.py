import json
import os
from datetime import datetime

def validate_projection_depth_taxonomy():
    registry_path = "registry/math/projection_depth_taxonomy.json"
    result_path = "validation/results/projection_depth_taxonomy_result.json"
    
    report = {
        "validation_id": "VAL-PDT-VALID-001",
        "status": "pass",
        "levels_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("projection depth taxonomy registry missing")
        return report

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
        
    # 1. Taxonomy Identification
    if registry.get("taxonomy_status") != "CANDIDATE_PROJECTION_TAXONOMY":
        report["status"] = "fail"
        report["governance_violations"].append("illegal taxonomy status")
    
    # 2. Level Completeness Check
    levels = registry.get("depth_levels", [])
    required_levels = ["PD-1", "PD-2", "PD-3", "PD-4"]
    registered_ids = [lvl["depth_id"] for lvl in levels]
    for rl in required_levels:
        if rl not in registered_ids:
            report["status"] = "fail"
            report["governance_violations"].append(f"required depth level missing: {rl}")
        else:
            report["levels_verified"] += 1
            
    for lvl in levels:
        if not lvl.get("retained_features") or not lvl.get("lost_features"):
            report["status"] = "fail"
            report["governance_violations"].append(f"missing feature mapping for level: {lvl.get('depth_id')}")
        
        # PD-3 warning check
        if lvl["depth_id"] == "PD-3" and not lvl.get("reconstruction_warning"):
             report["status"] = "fail"
             report["governance_violations"].append("missing reconstruction warning for PD-3")
             
        # PD-4 evidence block check
        if lvl["depth_id"] == "PD-4" and not lvl.get("primitive_evidence_blocked"):
             report["status"] = "fail"
             report["governance_violations"].append("missing primitive evidence block for PD-4")

    # 3. Rule and Constraint Check
    if not registry.get("depth_governance_rules"):
        report["status"] = "fail"
        report["governance_violations"].append("missing depth governance rules in registry")

    if not registry.get("operator_depth_assignments"):
        report["status"] = "fail"
        report["governance_violations"].append("missing operator depth assignments")

    # 4. Governance Status Invariants
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
    res = validate_projection_depth_taxonomy()
    print(json.dumps(res, indent=2))
