import json
import os
from datetime import datetime

def validate_cross_projection_loss_differential_matrix():
    registry_path = "registry/math/cross_projection_loss_differential_matrix.json"
    result_path = "validation/results/cross_projection_loss_differential_matrix_result.json"
    
    report = {
        "validation_id": "VAL-CPLDM-VALID-001",
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
        
    status = registry.get("status", {})
    
    # 2. matrix_status_equals_CANDIDATE_CROSS_PROJECTION_LOSS_DIFFERENTIAL
    if status.get("matrix_status") != "CANDIDATE_CROSS_PROJECTION_LOSS_DIFFERENTIAL":
        report["status"] = "fail"
        report["governance_violations"].append(f"matrix_status_equals_CANDIDATE_CROSS_PROJECTION_LOSS_DIFFERENTIAL: FAIL (found {status.get('matrix_status')})")
    else:
        report["checks_passed"].append("matrix_status_equals_CANDIDATE_CROSS_PROJECTION_LOSS_DIFFERENTIAL")

    # 3. core_rule_present
    if "core_rule" not in registry:
        report["status"] = "fail"
        report["governance_violations"].append("core_rule_present: FAIL")
    else:
        report["checks_passed"].append("core_rule_present")

    # 4. matrix_schema_present
    if "matrix_schema" not in registry:
        report["status"] = "fail"
        report["governance_violations"].append("matrix_schema_present: FAIL")
    else:
        report["checks_passed"].append("matrix_schema_present")

    # 5. initial_matrix_records_present
    records = registry.get("initial_matrix_records", [])
    if not records:
        report["status"] = "fail"
        report["governance_violations"].append("initial_matrix_records_present: FAIL")
    else:
        report["checks_passed"].append("initial_matrix_records_present")

    # 6. qm_preserved_features_present
    for r in records:
        if "qm_preserved_features" not in r:
            report["status"] = "fail"
            report["governance_violations"].append(f"qm_preserved_features_present: FAIL in {r.get('matrix_id')}")
    if records:
        report["checks_passed"].append("qm_preserved_features_present")

    # 7. gr_preserved_features_present
    for r in records:
        if "gr_preserved_features" not in r:
            report["status"] = "fail"
            report["governance_violations"].append(f"gr_preserved_features_present: FAIL in {r.get('matrix_id')}")
    if records:
        report["checks_passed"].append("gr_preserved_features_present")

    # 8. qm_distortion_risks_present
    for r in records:
        if "qm_distortion_risks" not in r:
            report["status"] = "fail"
            report["governance_violations"].append(f"qm_distortion_risks_present: FAIL in {r.get('matrix_id')}")
    if records:
        report["checks_passed"].append("qm_distortion_risks_present")

    # 9. gr_distortion_risks_present
    for r in records:
        if "gr_distortion_risks" not in r:
            report["status"] = "fail"
            report["governance_violations"].append(f"gr_distortion_risks_present: FAIL in {r.get('matrix_id')}")
    if records:
        report["checks_passed"].append("gr_distortion_risks_present")

    # 10. physical_unification_claim_false
    for r in records:
        if r.get("physical_unification_claim") is not False:
            report["status"] = "fail"
            report["governance_violations"].append(f"physical_unification_claim_false: FAIL in {r.get('matrix_id')}")
    if records:
        report["checks_passed"].append("physical_unification_claim_false")

    # 11. forbidden_uses_include_QM_GR_complementarity_proof
    forbidden = registry.get("forbidden_uses", [])
    if not any("complementarity" in u.lower() for u in forbidden):
        report["status"] = "fail"
        report["governance_violations"].append("forbidden_uses_include_QM_GR_complementarity_proof: FAIL")
    else:
        report["checks_passed"].append("forbidden_uses_include_QM_GR_complementarity_proof")

    # 12. physics_status_equals_NON_PHYSICAL_ANALOG_MODEL
    if status.get("physics_status") != "NON_PHYSICAL_ANALOG_MODEL":
        report["status"] = "fail"
        report["governance_violations"].append(f"physics_status_equals_NON_PHYSICAL_ANALOG_MODEL: FAIL (found {status.get('physics_status')})")
    else:
        report["checks_passed"].append("physics_status_equals_NON_PHYSICAL_ANALOG_MODEL")

    # 13. theorem_status_equals_NOT_PROVEN
    if status.get("theorem_status") != "NOT_PROVEN":
        report["status"] = "fail"
        report["governance_violations"].append(f"theorem_status_equals_NOT_PROVEN: FAIL (found {status.get('theorem_status')})")
    else:
        report["checks_passed"].append("theorem_status_equals_NOT_PROVEN")

    # Final result logging
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_cross_projection_loss_differential_matrix()
    print(json.dumps(res, indent=2))
