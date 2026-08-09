import json
import os
from datetime import datetime

def validate_semantic_translation_corridors():
    registry_path = "registry/math/semantic_translation_corridor_registry.json"
    result_path = "validation/results/semantic_translation_corridor_result.json"
    
    report = {
        "validation_id": "VAL-STC-VALID-001",
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

    # 3. corridor_classes_present
    classes = registry.get("corridor_classes", [])
    required_classes = ["STC_PARTIAL_ALIGNMENT", "STC_TRACE_COMPATIBLE", "STC_CONFLICT_LOCKED", "STC_DEFORMATION_HEAVY", "STC_TRANSLATION_BLOCKED"]
    found_classes = [c.get("class_id") for c in classes]
    for c_id in required_classes:
        if c_id not in found_classes:
            report["status"] = "fail"
            report["governance_violations"].append(f"class_present_{c_id}: FAIL")
        else:
            report["checks_passed"].append(f"class_present_{c_id}")

    # 4. corridor_properties_present
    props = registry.get("corridor_properties", [])
    required_props = ["semantic_trace_overlap", "conflict_preservation_requirement", "translation_loss_visibility", "recoverability_stability"]
    found_props = [p.get("property_id") for p in props]
    for p_id in required_props:
        if p_id not in found_props:
            report["status"] = "fail"
            report["governance_violations"].append(f"property_present_{p_id}: FAIL")
        else:
            report["checks_passed"].append(f"property_present_{p_id}")

    # 5. hardening_boilerplate_present
    if registry.get("source_relation") != "(E≠0) ⇔R δ(E>0)":
        report["status"] = "fail"
        report["governance_violations"].append("hardening_boilerplate_source_relation: FAIL")
    else:
        report["checks_passed"].append("hardening_boilerplate_source_relation")

    # 6. forbidden_claims checks
    forbidden = registry.get("forbidden_claims", [])
    if "Perfect semantic translation proves physical substrate identity." not in forbidden:
        report["status"] = "fail"
        report["governance_violations"].append("forbidden_claims_include_identity_claim: FAIL")
    else:
        report["checks_passed"].append("forbidden_claims_include_identity_claim")

    # Final result logging
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_semantic_translation_corridors()
    print(json.dumps(res, indent=2))
