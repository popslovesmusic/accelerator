import json
import os
from datetime import datetime

def validate_projection_induced_geometry():
    registry_path = "registry/math/projection_induced_geometry_governance.json"
    result_path = "validation/results/projection_induced_geometry_result.json"
    
    report = {
        "validation_id": "VAL-PIGG-VALID-001",
        "status": "pass",
        "classes_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("geometry governance registry missing")
        return report

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
        
    # 1. Governance Status Check
    gov = registry.get("governance_status", {})
    if gov.get("governance_status") != "CANDIDATE_PROJECTION_GEOMETRY":
        report["status"] = "fail"
        report["governance_violations"].append("illegal governance status in registry")
    
    if gov.get("physics_status") != "NON_PHYSICAL_ANALOG_MODEL":
        report["status"] = "fail"
        report["governance_violations"].append("physics status must be NON_PHYSICAL_ANALOG_MODEL")

    if gov.get("theorem_status") != "NOT_PROVEN":
        report["status"] = "fail"
        report["governance_violations"].append("forbidden theorem status escalation")

    # 2. Core Definition Check
    definition = registry.get("core_definition", {})
    if not definition.get("canonical_statement") or not definition.get("non_primitive_rule"):
        report["status"] = "fail"
        report["governance_violations"].append("missing core definition components")

    # 3. Class Check
    required_classes = ["PGEO-1", "PGEO-2", "PGEO-3", "PGEO-4", "PGEO-5"]
    registered_classes = [c["class_id"] for c in registry.get("geometry_like_classes", [])]
    for gc in required_classes:
        if gc not in registered_classes:
            report["status"] = "fail"
            report["governance_violations"].append(f"required geometry-like class missing: {gc}")
        else:
            report["classes_verified"] += 1

    # 4. Governance Rules Check
    rules = registry.get("governance_rules", [])
    if not any("physical spacetime" in r["rule"] for r in rules):
        report["status"] = "fail"
        report["governance_violations"].append("missing forbidden physical spacetime claim rule")

    # 5. Schema Check
    schema = registry.get("geometry_projection_schema", {})
    if not schema or schema.get("physical_spacetime_claim") is not False:
        report["status"] = "fail"
        report["governance_violations"].append("missing or invalid geometry projection schema")

    # 6. Forbidden Claims Check
    forbidden = registry.get("forbidden_uses", [])
    if not any("GR" in u for u in forbidden):
        report["status"] = "fail"
        report["governance_violations"].append("missing forbidden proof of GR check")

    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_projection_induced_geometry()
    print(json.dumps(res, indent=2))
