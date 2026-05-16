import json
import os
from datetime import datetime

def validate_deformation_propagation():
    registry_path = "registry/math/deformation_propagation_registry.json"
    result_path = "validation/results/deformation_propagation_result.json"
    
    report = {
        "validation_id": "VAL-DP-VALID-001",
        "status": "pass",
        "checks_passed": [],
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    # 1. registry_exists
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("registry_exists: FAIL (registry missing)")
        return report
    report["checks_passed"].append("registry_exists")

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
        
    gov = registry.get("governance_status", {})
    
    # 2. physics_status_equals_NON_PHYSICAL_ANALOG_MODEL
    if gov.get("physics_status") != "NON_PHYSICAL_ANALOG_MODEL":
        report["status"] = "fail"
        report["governance_violations"].append(f"physics_status_equals_NON_PHYSICAL_ANALOG_MODEL: FAIL (found {gov.get('physics_status')})")
    else:
        report["checks_passed"].append("physics_status_equals_NON_PHYSICAL_ANALOG_MODEL")

    # 3. propagation_classes_present
    classes = registry.get("propagation_classes", [])
    required_classes = ["DP_LOCALIZED", "DP_CORRIDOR_BOUND", "DP_CONFLICT_DIFFUSION", "DP_CASCADE", "DP_IDENTITY_COLLAPSE_RISK"]
    found_classes = [c.get("class_id") for c in classes]
    for c_id in required_classes:
        if c_id not in found_classes:
            report["status"] = "fail"
            report["governance_violations"].append(f"class_present_{c_id}: FAIL")
        else:
            report["checks_passed"].append(f"class_present_{c_id}")

    # 4. candidate_distortions_present
    distortions = registry.get("candidate_distortions", [])
    required_distortions = ["sequentialization_pressure", "projection_flattening", "recoverability_overread", "forced_unity_language", "observer_externalization"]
    found_distortions = [d.get("distortion_id") for d in distortions]
    for d_id in required_distortions:
        if d_id not in found_distortions:
            report["status"] = "fail"
            report["governance_violations"].append(f"distortion_present_{d_id}: FAIL")
        else:
            report["checks_passed"].append(f"distortion_present_{d_id}")

    # 5. hardening_boilerplate_present
    if registry.get("source_relation") != "(E≠0) ⇔R δ(E>0)":
        report["status"] = "fail"
        report["governance_violations"].append("hardening_boilerplate_source_relation: FAIL")
    else:
        report["checks_passed"].append("hardening_boilerplate_source_relation")

    # Final result logging
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_deformation_propagation()
    print(json.dumps(res, indent=2))
