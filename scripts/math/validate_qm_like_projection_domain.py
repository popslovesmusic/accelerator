import json
import os
from datetime import datetime

def validate_qm_like_projection_domain():
    registry_path = "registry/math/qm_like_projection_domain_registry.json"
    result_path = "validation/results/qm_like_projection_domain_result.json"
    
    report = {
        "validation_id": "VAL-QMPD-VALID-001",
        "status": "pass",
        "features_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("QM-like domain registry missing")
        return report

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
        
    # 1. Domain Identification
    if registry.get("domain_status") != "CANDIDATE_BRIDGE_DOMAIN":
        report["status"] = "fail"
        report["governance_violations"].append("illegal domain status in registry")

    # 2. Feature Completeness Check
    features = registry.get("domain_features", [])
    required_features = ["distinction_by_exclusion", "symbolic_discreteness", "exclusion_thresholding"]
    registered_names = [f["name"] for f in features]
    for rf in required_features:
        if rf not in registered_names:
            report["status"] = "fail"
            report["governance_violations"].append(f"required QM-like feature missing: {rf}")
        else:
            report["features_verified"] += 1

    # 3. Governance Constraints Check
    constraints = registry.get("governance_constraints", {})
    if not constraints.get("is_analog_only") or not constraints.get("no_wave_function_derivation"):
        report["status"] = "fail"
        report["governance_violations"].append("missing mandatory governance constraints for QM-like domain")

    # 4. Forbidden Uses Check
    forbidden = registry.get("forbidden_uses", [])
    if not any("deriving" in u.lower() or "derivation" in u.lower() for u in forbidden):
        report["status"] = "fail"
        report["governance_violations"].append("missing forbidden derivation check")

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
    res = validate_qm_like_projection_domain()
    print(json.dumps(res, indent=2))
