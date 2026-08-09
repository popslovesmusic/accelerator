import json
import os
from datetime import datetime

def validate_shared_source_relation_trace_map():
    registry_path = "registry/math/shared_source_relation_trace_map.json"
    result_path = "validation/results/shared_source_relation_trace_map_result.json"
    
    report = {
        "validation_id": "VAL-SSTM-VALID-001",
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
    
    # 2. trace_status_equals_CANDIDATE_SHARED_SOURCE_TRACE_MAP
    if status.get("trace_status") != "CANDIDATE_SHARED_SOURCE_TRACE_MAP":
        report["status"] = "fail"
        report["governance_violations"].append(f"trace_status_equals_CANDIDATE_SHARED_SOURCE_TRACE_MAP: FAIL (found {status.get('trace_status')})")
    else:
        report["checks_passed"].append("trace_status_equals_CANDIDATE_SHARED_SOURCE_TRACE_MAP")

    # 3. core_rule_present
    if "core_rule" not in registry:
        report["status"] = "fail"
        report["governance_violations"].append("core_rule_present: FAIL")
    else:
        report["checks_passed"].append("core_rule_present")

    # 4. trace_map_schema_present
    if "trace_map_schema" not in registry:
        report["status"] = "fail"
        report["governance_violations"].append("trace_map_schema_present: FAIL")
    else:
        report["checks_passed"].append("trace_map_schema_present")

    # 5. initial_trace_maps_present
    initial_maps = registry.get("initial_trace_maps", [])
    if not initial_maps:
        report["status"] = "fail"
        report["governance_violations"].append("initial_trace_maps_present: FAIL")
    else:
        report["checks_passed"].append("initial_trace_maps_present")

    # 6. loss_differential_present
    for m in initial_maps:
        if "loss_differential" not in m:
            report["status"] = "fail"
            report["governance_violations"].append(f"loss_differential_present: FAIL in {m.get('trace_map_id')}")
    if initial_maps:
        report["checks_passed"].append("loss_differential_present")

    # 7. conflict_records_present
    for m in initial_maps:
        if "conflict_records" not in m:
            report["status"] = "fail"
            report["governance_violations"].append(f"conflict_records_present: FAIL in {m.get('trace_map_id')}")
    if initial_maps:
        report["checks_passed"].append("conflict_records_present")

    # 8. source_identity_claim_false
    for m in initial_maps:
        if m.get("source_identity_claim") is not False:
            report["status"] = "fail"
            report["governance_violations"].append(f"source_identity_claim_false: FAIL in {m.get('trace_map_id')}")
    if initial_maps:
        report["checks_passed"].append("source_identity_claim_false")

    # 9. physical_unification_claim_false
    for m in initial_maps:
        if m.get("physical_unification_claim") is not False:
            report["status"] = "fail"
            report["governance_violations"].append(f"physical_unification_claim_false: FAIL in {m.get('trace_map_id')}")
    if initial_maps:
        report["checks_passed"].append("physical_unification_claim_false")

    # 10. forbidden_uses_include_QM_GR_unification
    forbidden = registry.get("forbidden_uses", [])
    if not any("unification" in u.lower() for u in forbidden):
        report["status"] = "fail"
        report["governance_violations"].append("forbidden_uses_include_QM_GR_unification: FAIL")
    else:
        report["checks_passed"].append("forbidden_uses_include_QM_GR_unification")

    # 11. physics_status_equals_NON_PHYSICAL_ANALOG_MODEL
    if status.get("physics_status") != "NON_PHYSICAL_ANALOG_MODEL":
        report["status"] = "fail"
        report["governance_violations"].append(f"physics_status_equals_NON_PHYSICAL_ANALOG_MODEL: FAIL (found {status.get('physics_status')})")
    else:
        report["checks_passed"].append("physics_status_equals_NON_PHYSICAL_ANALOG_MODEL")

    # 12. theorem_status_equals_NOT_PROVEN
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
    res = validate_shared_source_relation_trace_map()
    print(json.dumps(res, indent=2))
