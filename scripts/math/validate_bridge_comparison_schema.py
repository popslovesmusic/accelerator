import json
import os
from datetime import datetime

def validate_bridge_comparison_schema():
    registry_path = "registry/math/bridge_comparison_schema.json"
    result_path = "validation/results/bridge_comparison_schema_result.json"
    
    report = {
        "validation_id": "VAL-BCS-VALID-001",
        "status": "pass",
        "schema_components_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("bridge comparison schema registry missing")
        return report

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
        
    # 1. Schema Identification
    if registry.get("schema_status") != "CANDIDATE_BRIDGE_SCHEMA":
        report["status"] = "fail"
        report["governance_violations"].append("illegal schema status in registry")

    # 2. Structural Completeness Check
    schema = registry.get("comparison_schema", {})
    required_keys = ["source_relation", "shared_trace_id", "feature_alignment", "differential_loss", "coherence_class"]
    for rk in required_keys:
        if rk not in schema:
            report["status"] = "fail"
            report["governance_violations"].append(f"required schema field missing: {rk}")
        else:
            report["schema_components_verified"] += 1

    # 3. Governance Rules Check
    rules = registry.get("comparison_rules", [])
    if not any("shared source_relation" in r["rule"] for r in rules):
        report["status"] = "fail"
        report["governance_violations"].append("missing mandatory traceability rule")
    
    if not any("differential loss" in r["rule"].lower() for r in rules):
        report["status"] = "fail"
        report["governance_violations"].append("missing mandatory differential loss rule")

    # 4. Forbidden Outcomes Check
    forbidden = registry.get("forbidden_outcomes", [])
    if not any("unification" in u.lower() for u in forbidden):
        report["status"] = "fail"
        report["governance_violations"].append("missing forbidden unification check")

    # 5. Governance Status Invariants
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
    res = validate_bridge_comparison_schema()
    print(json.dumps(res, indent=2))
