import json
import os

def validate_law009():
    results = {
        "law009_apparent_temporality_projection_law_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }

    registry_path = "registry/math/law009_apparent_temporality_projection_law_registry.json"
    law_doc_path = "docs/math/law009_apparent_temporality_projection_law.md"
    result_path = "outputs/math_tests/law009_apparent_temporality_projection_law_result.json"

    # 1. Registry check
    if not os.path.exists(registry_path):
        results["law009_apparent_temporality_projection_law_validation"]["status"] = "fail"
        results["law009_apparent_temporality_projection_law_validation"]["errors"].append("LAW-009 registry missing.")
    else:
        try:
            with open(registry_path, 'r') as f:
                data = json.load(f)
                
                # Check law conditions
                conds = data.get("law_conditions", [])
                if len(conds) < 8:
                    results["law009_apparent_temporality_projection_law_validation"]["status"] = "fail"
                    results["law009_apparent_temporality_projection_law_validation"]["errors"].append(f"Insufficient law conditions: {len(conds)}/8")
                
                # Check failure modes
                fms = data.get("failure_modes_to_preserve", [])
                if len(fms) < 8:
                    results["law009_apparent_temporality_projection_law_validation"]["status"] = "fail"
                    results["law009_apparent_temporality_projection_law_validation"]["errors"].append(f"Insufficient failure modes: {len(fms)}/8")
                
                results["law009_apparent_temporality_projection_law_validation"]["checks"].append("LAW-009 registry content verified.")
        except Exception as e:
            results["law009_apparent_temporality_projection_law_validation"]["status"] = "fail"
            results["law009_apparent_temporality_projection_law_validation"]["errors"].append(f"Registry parse error: {e}")

    # 2. Law document check
    if not os.path.exists(law_doc_path):
        results["law009_apparent_temporality_projection_law_validation"]["status"] = "fail"
        results["law009_apparent_temporality_projection_law_validation"]["errors"].append("LAW-009 document missing.")
    else:
        with open(law_doc_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            required_terms = [
                "{-(i)_α}", "apparent temporality", "recursion density", 
                "projection", "no primitive time", "ordered reconciliation",
                "no absolute time", "no physics claim"
            ]
            for term in required_terms:
                if term not in content:
                    results["law009_apparent_temporality_projection_law_validation"]["status"] = "warning"
                    results["law009_apparent_temporality_projection_law_validation"]["warnings"].append(f"Term '{term}' missing from law document.")
        results["law009_apparent_temporality_projection_law_validation"]["checks"].append("LAW-009 document presence and content scanned.")

    # 3. Execution result check
    if not os.path.exists(result_path):
        results["law009_apparent_temporality_projection_law_validation"]["status"] = "fail"
        results["law009_apparent_temporality_projection_law_validation"]["errors"].append("LAW-009 execution result missing.")
    else:
        try:
            with open(result_path, 'r') as f:
                res = json.load(f).get("law009_apparent_temporality_projection_law_result", {})
                if res.get("status") != "success":
                     results["law009_apparent_temporality_projection_law_validation"]["status"] = "fail"
                     results["law009_apparent_temporality_projection_law_validation"]["errors"].append("LAW-009 execution result indicates failure.")
            results["law009_apparent_temporality_projection_law_validation"]["checks"].append("LAW-009 execution result verified.")
        except Exception as e:
            results["law009_apparent_temporality_projection_law_validation"]["status"] = "fail"
            results["law009_apparent_temporality_projection_law_validation"]["errors"].append(f"Result parse error: {e}")

    return results

if __name__ == "__main__":
    res = validate_law009()
    print(json.dumps(res, indent=2))
