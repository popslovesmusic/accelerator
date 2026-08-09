import json
import os
import argparse

def validate_stress_tests():
    results = {
        "proof_candidate_stress_test_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }

    test_reg = "registry/math/proof_candidate_stress_test_registry.json"
    case_reg = "registry/math/proof_candidate_adversarial_case_registry.json"
    fm_reg = "registry/math/proof_candidate_stress_failure_modes.json"

    try:
        with open(test_reg, 'r') as f: tests = json.load(f).get("proof_candidate_stress_tests", {}).get("tests", [])
        with open(case_reg, 'r') as f: cases = json.load(f).get("proof_candidate_adversarial_cases", {}).get("cases", [])
        with open(fm_reg, 'r') as f: fms = json.load(f).get("proof_candidate_stress_failure_modes", {}).get("failure_modes", [])
    except Exception as e:
        results["proof_candidate_stress_test_validation"]["status"] = "fail"
        results["proof_candidate_stress_test_validation"]["errors"].append(f"Load error: {e}")
        return results

    case_ids = [c["case_id"] for c in cases]
    fm_ids = [fm["id"] for fm in fms]

    for test in tests:
        target = test["target"]
        for cid in test.get("adversarial_cases", []):
            if cid not in case_ids:
                results["proof_candidate_stress_test_validation"]["status"] = "fail"
                results["proof_candidate_stress_test_validation"]["errors"].append(f"Test {test['test_id']} references unknown case: {cid}")
            else:
                # Check case vs target consistency
                case = next(c for c in cases if c["case_id"] == cid)
                if case["target"] != target:
                     results["proof_candidate_stress_test_validation"]["status"] = "warning"
                     results["proof_candidate_stress_test_validation"]["warnings"].append(f"Case {cid} target ({case['target']}) mismatch with test target ({target})")

    for case in cases:
        efm = case.get("expected_failure_mode")
        if efm and efm not in fm_ids:
             results["proof_candidate_stress_test_validation"]["status"] = "fail"
             results["proof_candidate_stress_test_validation"]["errors"].append(f"Case {case['case_id']} references unknown failure mode: {efm}")

    results["proof_candidate_stress_test_validation"]["checks"].append(f"Validated {len(tests)} stress tests and {len(cases)} adversarial cases.")
    
    return results

if __name__ == "__main__":
    res = validate_stress_tests()
    print(json.dumps(res, indent=2))
