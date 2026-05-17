import json
import os
from datetime import datetime

def validate_law_supersession_trace():
    registry_path = "registry/math/law_supersession_trace_registry.json"
    result_path = "validation/results/law_supersession_trace_result.json"
    
    report = {
        "validation_id": "VAL-LST-VALID-001",
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

    # 3. traces_present
    traces = registry.get("supersession_traces", [])
    if len(traces) < 34:
        report["status"] = "fail"
        report["governance_violations"].append(f"trace_coverage: FAIL (found {len(traces)} laws, expected 34)")
    else:
        report["checks_passed"].append("trace_coverage_complete")

    # 4. non_deletion_check
    all_not_deleted = all(t.get("not_deleted") is True for t in traces)
    if not all_not_deleted:
        report["status"] = "fail"
        report["governance_violations"].append("non_deletion_integrity: FAIL (some laws marked deleted)")
    else:
        report["checks_passed"].append("non_deletion_integrity_maintained")

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
    res = validate_law_supersession_trace()
    print(json.dumps(res, indent=2))
