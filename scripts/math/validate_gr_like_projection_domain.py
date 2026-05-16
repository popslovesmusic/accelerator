import json
import os
from datetime import datetime

def validate_gr_like_projection_domain():
    registry_path = "registry/math/gr_like_projection_domain_registry.json"
    result_path = "validation/results/gr_like_projection_domain_result.json"
    
    report = {
        "validation_id": "VAL-GRPD-VALID-001",
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
    
    # 2. domain_status_equals_CANDIDATE_GR_LIKE_PROJECTION_DOMAIN
    if status.get("domain_status") != "CANDIDATE_GR_LIKE_PROJECTION_DOMAIN":
        report["status"] = "fail"
        report["governance_violations"].append(f"domain_status_equals_CANDIDATE_GR_LIKE_PROJECTION_DOMAIN: FAIL (found {status.get('domain_status')})")
    else:
        report["checks_passed"].append("domain_status_equals_CANDIDATE_GR_LIKE_PROJECTION_DOMAIN")

    # 3. domain_definition_present
    if "domain_definition" not in registry:
        report["status"] = "fail"
        report["governance_violations"].append("domain_definition_present: FAIL")
    else:
        report["checks_passed"].append("domain_definition_present")

    # 4. governed_feature_classes_include_GRP001_to_GRP006
    features = registry.get("governed_feature_classes", [])
    feature_ids = [f.get("feature_id") for f in features]
    required_features = [f"GRP-{str(i).zfill(3)}" for i in range(1, 7)]
    missing_features = [rf for rf in required_features if rf not in feature_ids]
    if missing_features:
        report["status"] = "fail"
        report["governance_violations"].append(f"governed_feature_classes_include_GRP001_to_GRP006: FAIL (missing {missing_features})")
    else:
        report["checks_passed"].append("governed_feature_classes_include_GRP001_to_GRP006")

    # 5. projection_relationships_present
    if "projection_relationships" not in registry:
        report["status"] = "fail"
        report["governance_violations"].append("projection_relationships_present: FAIL")
    else:
        report["checks_passed"].append("projection_relationships_present")

    # 6. domain_record_schema_present
    if "domain_record_schema" not in registry:
        report["status"] = "fail"
        report["governance_violations"].append("domain_record_schema_present: FAIL")
    else:
        report["checks_passed"].append("domain_record_schema_present")

    # 7. governance_rules_present
    if "governance_rules" not in registry:
        report["status"] = "fail"
        report["governance_violations"].append("governance_rules_present: FAIL")
    else:
        report["checks_passed"].append("governance_rules_present")

    # 8-9. forbidden_uses checks
    forbidden = registry.get("forbidden_uses", [])
    required_forbidden = [
        ("Claiming GR-like equals general relativity.", "forbidden_uses_include_GR_equals_general_relativity"),
        ("Claiming derivation of spacetime curvature, Einstein field equations, or physical gravitation.", "forbidden_uses_include_Einstein_field_equations_or_physical_gravitation")
    ]
    for use, check_name in required_forbidden:
        if use not in forbidden:
            report["status"] = "fail"
            report["governance_violations"].append(f"{check_name}: FAIL (missing '{use}')")
        else:
            report["checks_passed"].append(check_name)

    # 10. physics_status_equals_NON_PHYSICAL_ANALOG_MODEL
    if status.get("physics_status") != "NON_PHYSICAL_ANALOG_MODEL":
        report["status"] = "fail"
        report["governance_violations"].append(f"physics_status_equals_NON_PHYSICAL_ANALOG_MODEL: FAIL (found {status.get('physics_status')})")
    else:
        report["checks_passed"].append("physics_status_equals_NON_PHYSICAL_ANALOG_MODEL")

    # 11. theorem_status_equals_NOT_PROVEN
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
    res = validate_gr_like_projection_domain()
    print(json.dumps(res, indent=2))
