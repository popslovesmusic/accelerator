import json
import os
from datetime import datetime

def validate_escalation_trigger_registry():
    registry_path = "registry/escalation_trigger_registry.json"
    result_path = "validation/results/escalation_trigger_registry_result.json"
    
    report = {
        "validation_id": "VAL-ETR-VALID-001",
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

    # 2. triggers_present
    triggers = registry.get("triggers", [])
    required_ids = ["ET-001-COUNTER-DOMINANCE", "ET-002-EQUIV-FAIL", "ET-003-CLAIM-DRIFT", "ET-004-AGENT-CONFLICT"]
    found_ids = [t.get("trigger_id") for t in triggers]
    for tid in required_ids:
        if tid not in found_ids:
            report["status"] = "fail"
            report["governance_violations"].append(f"trigger_present_{tid}: FAIL")
        else:
            report["checks_passed"].append(f"trigger_present_{tid}")

    # 3. mandatory_fields_present
    for t in triggers:
        tid = t.get("trigger_id")
        required_fields = ["name", "description", "severity", "action"]
        for field in required_fields:
            if field not in t:
                report["status"] = "fail"
                report["governance_violations"].append(f"field_missing_{tid}_{field}: FAIL")
            else:
                report["checks_passed"].append(f"field_present_{tid}_{field}")

    # 4. hardening_boilerplate_present
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
    res = validate_escalation_trigger_registry()
    print(json.dumps(res, indent=2))
