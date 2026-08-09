import json
import os
from datetime import datetime

def validate_projection_boundary_governance():
    registry_path = "registry/math/projection_boundary_governance_registry.json"
    result_path = "validation/results/projection_boundary_governance_result.json"
    
    report = {
        "validation_id": "VAL-PBG-VALID-001",
        "status": "pass",
        "domains_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("projection governance registry missing")
        return report

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
        
    # 1. Governance Status Check
    gov = registry.get("governance_status", {})
    if gov.get("governance_status") != "CANDIDATE_BOUNDARY_GOVERNANCE":
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
    if rule.get("name") != "projection_not_primitive_rule":
        report["status"] = "fail"
        report["governance_violations"].append("missing core projection rule")

    # 3. Domain Check
    required_domains = ["arithmetic_like", "topology_like", "geometry_like", "QM_like", "GR_like"]
    registered_domains = [d["domain"] for d in registry.get("projection_domains", [])]
    for d in required_domains:
        if d not in registered_domains:
            report["status"] = "fail"
            report["governance_violations"].append(f"required projection domain missing: {d}")
        else:
            report["domains_verified"] += 1

    # 4. Formal Seed Rules
    formal = registry.get("formal_seed", {})
    required_formal_rules = ["loss_rule", "traceability_rule", "non_identity_rule"]
    for r in required_formal_rules:
        if r not in formal:
            report["status"] = "fail"
            report["governance_violations"].append(f"missing mandatory formal rule: {r}")

    # 5. Schema Check
    if not registry.get("projection_record_schema"):
        report["status"] = "fail"
        report["governance_violations"].append("missing projection record schema")

    # 6. Forbidden Claims Check
    forbidden = registry.get("forbidden_uses", [])
    if not any("completed unification" in u.lower() for u in forbidden):
        report["status"] = "fail"
        report["governance_violations"].append("missing forbidden unification claim check")

    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_projection_boundary_governance()
    print(json.dumps(res, indent=2))
