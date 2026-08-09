import json
import os
from datetime import datetime

def validate_reconstruction_neighborhoods():
    registry_path = "registry/math/reconstruction_neighborhood_registry.json"
    result_path = "validation/results/reconstruction_neighborhood_result.json"
    
    report = {
        "validation_id": "VAL-RN-VALID-001",
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

    # 3. neighborhood_classes_present
    classes = registry.get("neighborhood_classes", [])
    required_classes = ["RN_LOCAL_TRACE", "RN_PARTIAL_RECOVERABLE", "RN_CONFLICT_BOUNDARY", "RN_DEFORMATION_LIMIT", "RN_NONRECOVERABLE"]
    found_classes = [c.get("class_id") for c in classes]
    for c_id in required_classes:
        if c_id not in found_classes:
            report["status"] = "fail"
            report["governance_violations"].append(f"class_present_{c_id}: FAIL")
        else:
            report["checks_passed"].append(f"class_present_{c_id}")

    # 4. metrics_present
    metrics = registry.get("metrics", [])
    required_metrics = ["trace_overlap_density", "recoverability_locality_score", "projection_boundary_integrity", "loss_isolation_clarity"]
    found_metrics = [m.get("metric_id") for m in metrics]
    for m_id in required_metrics:
        if m_id not in found_metrics:
            report["status"] = "fail"
            report["governance_violations"].append(f"metric_present_{m_id}: FAIL")
        else:
            report["checks_passed"].append(f"metric_present_{m_id}")

    # 5. forbidden_claims checks
    forbidden = registry.get("forbidden_claims", [])
    if "Reconstruction neighborhoods represent physical spacetime regions." not in forbidden:
        report["status"] = "fail"
        report["governance_violations"].append("forbidden_claims_include_spacetime_claim: FAIL")
    else:
        report["checks_passed"].append("forbidden_claims_include_spacetime_claim")

    # Final result logging
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_reconstruction_neighborhoods()
    print(json.dumps(res, indent=2))
