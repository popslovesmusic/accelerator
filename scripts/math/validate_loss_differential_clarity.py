import json
import os
from datetime import datetime

def validate_loss_differential_clarity():
    registry_path = "registry/math/loss_differential_clarity_metric.json"
    result_path = "validation/results/loss_differential_clarity_result.json"
    
    report = {
        "validation_id": "VAL-LDC-VALID-001",
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

    # 3. metrics_present
    metrics = registry.get("metrics", [])
    required_metrics = [
        "qm_loss_clarity",
        "gr_loss_clarity",
        "loss_differential_separation",
        "distortion_risk_explicitness",
        "overreading_risk_score"
    ]
    found_metrics = [m.get("metric_id") for m in metrics]
    for m_id in required_metrics:
        if m_id not in found_metrics:
            report["status"] = "fail"
            report["governance_violations"].append(f"metric_present_{m_id}: FAIL")
        else:
            report["checks_passed"].append(f"metric_present_{m_id}")

    # 4. clarity_requirements_present
    if "clarity_requirements" not in registry:
        report["status"] = "fail"
        report["governance_violations"].append("clarity_requirements_present: FAIL")
    else:
        report["checks_passed"].append("clarity_requirements_present")

    # 5. forbidden_claims checks
    forbidden = registry.get("forbidden_claims", [])
    if "Loss differential clarity proves physical complementarity." not in forbidden:
        report["status"] = "fail"
        report["governance_violations"].append("forbidden_claims_include_complementarity_claim: FAIL")
    else:
        report["checks_passed"].append("forbidden_claims_include_complementarity_claim")

    # Final result logging
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_loss_differential_clarity()
    print(json.dumps(res, indent=2))
