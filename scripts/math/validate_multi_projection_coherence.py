import json
import os
from datetime import datetime

def validate_multi_projection_coherence():
    registry_path = "registry/math/multi_projection_coherence_governance.json"
    result_path = "validation/results/multi_projection_coherence_result.json"
    
    report = {
        "validation_id": "VAL-MPC-VALID-001",
        "status": "pass",
        "classes_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("multi-projection coherence registry missing")
        return report

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
        
    # 1. Governance Status Check
    gov = registry.get("governance_status", {})
    if gov.get("governance_status") != "CANDIDATE_MULTI_PROJECTION_COHERENCE":
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
    if rule.get("name") != "projection_agreement_not_identity_rule":
        report["status"] = "fail"
        report["governance_violations"].append("missing core agreement-not-identity rule")

    # 3. Class Check
    required_classes = ["MPC-1", "MPC-2", "MPC-3", "MPC-4"]
    registered_classes = [c["class_id"] for c in registry.get("coherence_classes", [])]
    for rc in required_classes:
        if rc not in registered_classes:
            report["status"] = "fail"
            report["governance_violations"].append(f"required coherence class missing: {rc}")
        else:
            report["classes_verified"] += 1

    # 4. Schema Presence
    if not registry.get("coherence_schema"):
        report["status"] = "fail"
        report["governance_violations"].append("missing coherence schema")

    # 5. Governance Rules Check
    if not registry.get("governance_rules"):
        report["status"] = "fail"
        report["governance_violations"].append("missing governance rules in registry")

    # 6. Forbidden Claims Check
    forbidden = registry.get("forbidden_claims", [])
    if not any("proves the source relation" in u or "proves source" in u.lower() for u in forbidden):
        report["status"] = "fail"
        report["governance_violations"].append("missing forbidden source-proof claim check")
    if not any("QM-like and GR-like" in u or "unification" in u.lower() for u in forbidden):
        report["status"] = "fail"
        report["governance_violations"].append("missing forbidden physics unification check")

    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_multi_projection_coherence()
    print(json.dumps(res, indent=2))
