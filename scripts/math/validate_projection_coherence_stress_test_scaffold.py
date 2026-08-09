import json
import os
from datetime import datetime

def validate_projection_coherence_stress_test_scaffold():
    registry_path = "registry/math/projection_coherence_stress_test_scaffold.json"
    result_path = "validation/results/projection_coherence_stress_test_scaffold_result.json"
    
    report = {
        "validation_id": "VAL-PCST-VALID-001",
        "status": "pass",
        "classes_verified": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("stress test scaffold registry missing")
        return report

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
        
    # 1. Scaffold Identification
    if registry.get("scaffold_status") != "CANDIDATE_STRESS_TEST_SCAFFOLD":
        report["status"] = "fail"
        report["governance_violations"].append("illegal scaffold status in registry")

    # 2. Test Class Completeness Check
    classes = registry.get("stress_test_classes", [])
    required_tests = ["PCST-001", "PCST-002", "PCST-003", "PCST-004", "PCST-005", "PCST-006"]
    registered_ids = [c["test_id"] for c in classes]
    for rt in required_tests:
        if rt not in registered_ids:
            report["status"] = "fail"
            report["governance_violations"].append(f"required stress test class missing: {rt}")
        else:
            report["classes_verified"] += 1

    # 3. Schema and Behavior Check
    if not registry.get("stress_test_record_schema"):
        report["status"] = "fail"
        report["governance_violations"].append("missing stress test record schema")

    if not registry.get("required_test_behaviors"):
        report["status"] = "fail"
        report["governance_violations"].append("missing required test behaviors in registry")

    # 4. Forbidden Outcomes Check
    forbidden = registry.get("forbidden_outcomes", [])
    if not any("unification" in u.lower() for u in forbidden):
        report["status"] = "fail"
        report["governance_violations"].append("missing forbidden qm/gr unification claim check")
    if not any("recoverability overclaim" in u.lower() for u in forbidden):
        report["status"] = "fail"
        report["governance_violations"].append("missing forbidden recoverability overclaim check")

    # 5. Governance Status Invariants
    gov = registry.get("governance_status", {})
    if gov.get("physics_status") != "NON_PHYSICAL_ANALOG_MODEL":
        report["status"] = "fail"
        report["governance_violations"].append("physics status must be NON_PHYSICAL_ANALOG_MODEL")
    if gov.get("theorem_status") != "NOT_PROVEN":
        report["status"] = "fail"
        report["governance_violations"].append("forbidden theorem status escalation")

    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_projection_coherence_stress_test_scaffold()
    print(json.dumps(res, indent=2))
