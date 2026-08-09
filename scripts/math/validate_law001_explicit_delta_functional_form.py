import json
import os
import argparse

def validate_law001():
    results = {
        "law001_explicit_delta_functional_form_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }

    registry_path = "registry/math/law001_explicit_delta_functional_form_registry.json"
    law_doc_path = "docs/math/law001_explicit_delta_functional_form.md"
    result_path = "outputs/math_tests/law001_explicit_delta_functional_form_result.json"

    # 1. Registry check
    if not os.path.exists(registry_path):
        results["law001_explicit_delta_functional_form_validation"]["status"] = "fail"
        results["law001_explicit_delta_functional_form_validation"]["errors"].append("LAW-001 registry missing.")
    else:
        try:
            with open(registry_path, 'r') as f:
                data = json.load(f).get("law001_explicit_delta_functional_form", {})
                
                # Check law conditions
                conds = data.get("law_conditions", [])
                if len(conds) < 8:
                    results["law001_explicit_delta_functional_form_validation"]["status"] = "fail"
                    results["law001_explicit_delta_functional_form_validation"]["errors"].append(f"Insufficient law conditions: {len(conds)}/8")
                
                # Check failure modes
                fms = data.get("failure_modes_to_preserve", [])
                if len(fms) < 8:
                    results["law001_explicit_delta_functional_form_validation"]["status"] = "fail"
                    results["law001_explicit_delta_functional_form_validation"]["errors"].append(f"Insufficient failure modes: {len(fms)}/8")
                
                results["law001_explicit_delta_functional_form_validation"]["checks"].append("LAW-001 registry content verified.")
        except Exception as e:
            results["law001_explicit_delta_functional_form_validation"]["status"] = "fail"
            results["law001_explicit_delta_functional_form_validation"]["errors"].append(f"Registry parse error: {e}")

    # 2. Law document check
    if not os.path.exists(law_doc_path):
        results["law001_explicit_delta_functional_form_validation"]["status"] = "fail"
        results["law001_explicit_delta_functional_form_validation"]["errors"].append("LAW-001 document missing.")
    else:
        with open(law_doc_path, 'r') as f:
            content = f.read()
            required_terms = ["epsilon_null", "Pi_A", "NavT", "CSI", "multi-valued"]
            for term in required_terms:
                if term not in content:
                    results["law001_explicit_delta_functional_form_validation"]["status"] = "warning"
                    results["law001_explicit_delta_functional_form_validation"]["warnings"].append(f"Term '{term}' missing from law document.")
        results["law001_explicit_delta_functional_form_validation"]["checks"].append("LAW-001 document presence and content scanned.")

    # 3. Execution result check
    if not os.path.exists(result_path):
        results["law001_explicit_delta_functional_form_validation"]["status"] = "fail"
        results["law001_explicit_delta_functional_form_validation"]["errors"].append("LAW-001 execution result missing.")
    else:
        try:
            with open(result_path, 'r') as f:
                res = json.load(f).get("law001_explicit_delta_functional_form_result", {})
                if res.get("status") != "success":
                     results["law001_explicit_delta_functional_form_validation"]["status"] = "fail"
                     results["law001_explicit_delta_functional_form_validation"]["errors"].append("LAW-001 execution result indicates failure.")
            results["law001_explicit_delta_functional_form_validation"]["checks"].append("LAW-001 execution result verified.")
        except Exception as e:
            results["law001_explicit_delta_functional_form_validation"]["status"] = "fail"
            results["law001_explicit_delta_functional_form_validation"]["errors"].append(f"Result parse error: {e}")

    return results

if __name__ == "__main__":
    res = validate_law001()
    print(json.dumps(res, indent=2))
