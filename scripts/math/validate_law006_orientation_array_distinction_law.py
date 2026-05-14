import json
import os
import argparse

def validate_law006():
    results = {
        "law006_orientation_array_distinction_law_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }

    registry_path = "registry/math/law006_orientation_array_distinction_law_registry.json"
    law_doc_path = "docs/math/law006_orientation_array_distinction_law.md"
    result_path = "outputs/math_tests/law006_orientation_array_distinction_law_result.json"

    # 1. Registry check
    if not os.path.exists(registry_path):
        results["law006_orientation_array_distinction_law_validation"]["status"] = "fail"
        results["law006_orientation_array_distinction_law_validation"]["errors"].append("LAW-006 registry missing.")
    else:
        try:
            with open(registry_path, 'r') as f:
                data = json.load(f).get("law006_orientation_array_distinction_law", {})
                
                # Check law conditions
                conds = data.get("law_conditions", [])
                if len(conds) < 8:
                    results["law006_orientation_array_distinction_law_validation"]["status"] = "fail"
                    results["law006_orientation_array_distinction_law_validation"]["errors"].append(f"Insufficient law conditions: {len(conds)}/8")
                
                # Check failure modes
                fms = data.get("failure_modes_to_preserve", [])
                if len(fms) < 8:
                    results["law006_orientation_array_distinction_law_validation"]["status"] = "fail"
                    results["law006_orientation_array_distinction_law_validation"]["errors"].append(f"Insufficient failure modes: {len(fms)}/8")
                
                # Check candidate symbolic form presence
                if not data.get("candidate_law_statement", {}).get("local_operator_form"):
                     results["law006_orientation_array_distinction_law_validation"]["status"] = "fail"
                     results["law006_orientation_array_distinction_law_validation"]["errors"].append("Local operator form missing from registry.")

                results["law006_orientation_array_distinction_law_validation"]["checks"].append("LAW-006 registry content verified.")
        except Exception as e:
            results["law006_orientation_array_distinction_law_validation"]["status"] = "fail"
            results["law006_orientation_array_distinction_law_validation"]["errors"].append(f"Registry parse error: {e}")

    # 2. Law document check
    if not os.path.exists(law_doc_path):
        results["law006_orientation_array_distinction_law_validation"]["status"] = "fail"
        results["law006_orientation_array_distinction_law_validation"]["errors"].append("LAW-006 document missing.")
    else:
        with open(law_doc_path, 'r') as f:
            content = f.read()
            # Support both LaTeX and Greek character forms
            required_terms = [
                r"-(i)_\alpha", r"\{-(i)_\alpha\}", 
                "topology", "reconciliation", "NavT", "ordering",
                "not interchangeable", "not treated as a simple unordered collection"
            ]
            for term in required_terms:
                if term not in content:
                    # Check if the Greek character version exists
                    greek_term = term.replace(r"_\alpha", "_α").replace(r"\{", "{").replace(r"\}", "}")
                    if greek_term not in content:
                        results["law006_orientation_array_distinction_law_validation"]["status"] = "warning"
                        results["law006_orientation_array_distinction_law_validation"]["warnings"].append(f"Term '{term}' (or '{greek_term}') missing from law document.")
        results["law006_orientation_array_distinction_law_validation"]["checks"].append("LAW-006 document presence and content scanned.")

    # 3. Execution result check
    if not os.path.exists(result_path):
        results["law006_orientation_array_distinction_law_validation"]["status"] = "fail"
        results["law006_orientation_array_distinction_law_validation"]["errors"].append("LAW-006 execution result missing.")
    else:
        try:
            with open(result_path, 'r') as f:
                res = json.load(f).get("law006_orientation_array_distinction_law_result", {})
                if res.get("status") != "success":
                     results["law006_orientation_array_distinction_law_validation"]["status"] = "fail"
                     results["law006_orientation_array_distinction_law_validation"]["errors"].append("LAW-006 execution result indicates failure.")
            results["law006_orientation_array_distinction_law_validation"]["checks"].append("LAW-006 execution result verified.")
        except Exception as e:
            results["law006_orientation_array_distinction_law_validation"]["status"] = "fail"
            results["law006_orientation_array_distinction_law_validation"]["errors"].append(f"Result parse error: {e}")

    return results

if __name__ == "__main__":
    res = validate_law006()
    print(json.dumps(res, indent=2))
