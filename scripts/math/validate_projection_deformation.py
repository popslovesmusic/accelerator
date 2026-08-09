import json
import os
from datetime import datetime

def validate_projection_deformation():
    registry_path = "registry/math/projection_deformation_registry.json"
    result_path = "validation/results/projection_deformation_result.json"
    
    report = {
        "validation_id": "VAL-PD-VALID-001",
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

    # 3. deformation_modes_present
    modes = registry.get("deformation_modes", [])
    required_modes = ["simultaneity_flattening", "residue_erasure", "conflict_smoothing", "binary_freezing", "analog_diffusion", "identity_collapse"]
    found_modes = [m.get("mode_id") for m in modes]
    for m_id in required_modes:
        if m_id not in found_modes:
            report["status"] = "fail"
            report["governance_violations"].append(f"mode_present_{m_id}: FAIL")
        else:
            report["checks_passed"].append(f"mode_present_{m_id}")

    # 4. risk_classes_present
    classes = registry.get("risk_classes", [])
    required_classes = ["LOW_DEFORMATION", "TRACE_DISTORTION", "CONFLICT_ERASURE", "ONTOLOGY_COLLAPSE"]
    found_classes = [c.get("class_id") for c in classes]
    for c_id in required_classes:
        if c_id not in found_classes:
            report["status"] = "fail"
            report["governance_violations"].append(f"class_present_{c_id}: FAIL")
        else:
            report["checks_passed"].append(f"class_present_{c_id}")

    # 5. forbidden_claims checks
    forbidden = registry.get("forbidden_claims", [])
    if "Deformation smoothing derives physical vacuum states." not in forbidden:
        report["status"] = "fail"
        report["governance_violations"].append("forbidden_claims_include_vacuum_claim: FAIL")
    else:
        report["checks_passed"].append("forbidden_claims_include_vacuum_claim")

    # Final result logging
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_projection_deformation()
    print(json.dumps(res, indent=2))
