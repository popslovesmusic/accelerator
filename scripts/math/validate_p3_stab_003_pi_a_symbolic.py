import json
import os
import argparse

def validate_p3_stab_003_symbolic(result_path, scaffold_reg):
    results = {
        "p3_stab_003_symbolic_validation": {
            "status": "pass",
            "errors": [],
            "warnings": []
        }
    }

    try:
        with open(result_path, 'r') as f: report_data = json.load(f)
        with open(scaffold_reg, 'r') as f: scaffold_data = json.load(f)
    except Exception as e:
        results["p3_stab_003_symbolic_validation"]["status"] = "fail"
        results["p3_stab_003_symbolic_validation"]["errors"].append(f"Load error: {e}")
        return results

    report_entries = report_data.get("phase_3_stability_test_report", {}).get("results", [])
    test_result = next((r for r in report_entries if r["test_id"] == "P3-STAB-003"), None)
    
    if not test_result:
        results["p3_stab_003_symbolic_validation"]["status"] = "fail"
        results["p3_stab_003_symbolic_validation"]["errors"].append("Test result P3-STAB-003 not found in report.")
        return results

    # Check that all conditions were checked
    scaffold_conditions = [c["condition_id"] for c in scaffold_data.get("symbolic_stability_conditions", [])]
    checked_conditions = test_result.get("conditions_checked", [])
    for cond in scaffold_conditions:
        if cond not in checked_conditions:
            results["p3_stab_003_symbolic_validation"]["status"] = "warning"
            results["p3_stab_003_symbolic_validation"]["warnings"].append(f"Condition {cond} not explicitly checked in result.")

    # Governance check: must not promote
    if not test_result.get("theorem_implications", {}).get("must_not_promote"):
         results["p3_stab_003_symbolic_validation"]["status"] = "fail"
         results["p3_stab_003_symbolic_validation"]["errors"].append("Governance violation: must_not_promote mandate not found or false.")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate P3-STAB-003 symbolic stability evidence.")
    parser.add_argument("--path", required=True, help="Path to test results report.")
    parser.add_argument("--reg", default="registry/math/pi_a_symbolic_stability_registry.json")
    
    args = parser.parse_args()
    res = validate_p3_stab_003_symbolic(args.path, args.reg)
    print(json.dumps(res, indent=2))
