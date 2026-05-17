import json
import os
from datetime import datetime

def run_restricted_proof_candidate_stress_tests():
    registry_path = "registry/math/restricted_proof_candidate_stress_tests.json"
    result_path = "validation/results/restricted_proof_candidate_stress_tests_result.json"
    
    report = {
        "validation_id": "VAL-RPST-VALID-001",
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

    # 3. test_classes_present
    tests = registry.get("test_classes", [])
    required_tests = ["hidden_global_assumption_injection", "identity_equivalence_injection", "counterexample_erasure_injection", "undeclared_domain_injection", "physical_claim_injection", "proof_promotion_injection"]
    found_tests = [t.get("test_id") for t in tests]
    for t_id in required_tests:
        if t_id not in found_tests:
            report["status"] = "fail"
            report["governance_violations"].append(f"test_present_{t_id}: FAIL")
        else:
            report["checks_passed"].append(f"test_present_{t_id}")

    # 4. required_outputs_present
    outputs = registry.get("required_outputs", [])
    required_outputs = ["assumption_integrity_result", "counterexample_preservation_result", "status_promotion_safety_result", "domain_traceability_result"]
    for o_id in required_outputs:
        if o_id not in outputs:
            report["status"] = "fail"
            report["governance_violations"].append(f"output_requirement_present_{o_id}: FAIL")
        else:
            report["checks_passed"].append(f"output_requirement_present_{o_id}")

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
    res = run_restricted_proof_candidate_stress_tests()
    print(json.dumps(res, indent=2))
