import json
import os
import argparse

def validate_test_results(result_path, schema_path, failure_reg):
    results = {
        "phase_3_test_result_validation": {
            "status": "pass",
            "result_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(result_path, 'r') as f: report_data = json.load(f)
        with open(schema_path, 'r') as f: schema_data = json.load(f)
        with open(failure_reg, 'r') as f: failure_data = json.load(f)
    except Exception as e:
        results["phase_3_test_result_validation"]["status"] = "fail"
        results["phase_3_test_result_validation"]["errors"].append(f"Load error: {e}")
        return results

    fm_ids = [fm["id"] for fm in failure_data.get("failure_modes", [])]
    
    report = report_data.get("phase_3_stability_test_report", {})
    for res in report.get("results", []):
        results["phase_3_test_result_validation"]["result_count"] += 1
        
        # Check behavioral state
        if res.get("observed_behavior") not in ["pass", "warning", "fail", "not_executed", "inconclusive"]:
            results["phase_3_test_result_validation"]["status"] = "warning"
            results["phase_3_test_result_validation"]["errors"].append(f"Test {res['test_id']} has invalid observed_behavior: {res['observed_behavior']}")

        # Check failure modes triggered
        for fm in res.get("failure_modes_triggered", []):
            if fm not in fm_ids:
                results["phase_3_test_result_validation"]["status"] = "warning"
                results["phase_3_test_result_validation"]["errors"].append(f"Test {res['test_id']} triggered unknown failure mode: {fm}")

        # Ensure no theorem promotion
        if not res.get("theorem_implications", {}).get("must_not_promote"):
             results["phase_3_test_result_validation"]["status"] = "fail"
             results["phase_3_test_result_validation"]["errors"].append(f"Test {res['test_id']} violates must_not_promote mandate.")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate Phase 3 stability test results.")
    parser.add_argument("--path", required=True, help="Path to test results report.")
    parser.add_argument("--schema", default="registry/math/phase_3_test_result_schema.json")
    parser.add_argument("--failures", default="registry/math/phase_3_recursive_failure_modes.json")
    
    args = parser.parse_args()
    res = validate_test_results(args.path, args.schema, args.failures)
    print(json.dumps(res, indent=2))
