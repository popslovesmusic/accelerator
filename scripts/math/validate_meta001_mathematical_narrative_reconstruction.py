import json
import os
import sys

def validate_narrative_reconstruction():
    registry_path = "registry/math/meta001_mathematical_narrative_reconstruction_registry.json"
    result_path = "outputs/math_tests/meta001_mathematical_narrative_reconstruction_result.json"
    
    results_report = {
        "mathematical_narrative_reconstruction_validation": {
            "status": "pass",
            "warnings": [],
            "errors": []
        }
    }
    
    if not os.path.exists(registry_path):
        results_report["mathematical_narrative_reconstruction_validation"]["status"] = "fail"
        results_report["mathematical_narrative_reconstruction_validation"]["errors"].append(f"Registry not found: {registry_path}")
        print(json.dumps(results_report, indent=2))
        return
        
    if not os.path.exists(result_path):
        results_report["mathematical_narrative_reconstruction_validation"]["status"] = "fail"
        results_report["mathematical_narrative_reconstruction_validation"]["errors"].append(f"Results not found: {result_path}")
        print(json.dumps(results_report, indent=2))
        return

    try:
        with open(registry_path, "r") as f: registry = json.load(f)
        with open(result_path, "r") as f: results = json.load(f)
    except Exception as e:
        results_report["mathematical_narrative_reconstruction_validation"]["status"] = "fail"
        results_report["mathematical_narrative_reconstruction_validation"]["errors"].append(f"JSON Load error: {e}")
        print(json.dumps(results_report, indent=2))
        return

    # Check for presence of output documents
    outputs = registry["narrative_reconstruction"]["narrative_outputs"]
    for doc in outputs:
        if not os.path.exists(doc):
            results_report["mathematical_narrative_reconstruction_validation"]["status"] = "warning"
            results_report["mathematical_narrative_reconstruction_validation"]["warnings"].append(f"Narrative output missing: {doc}")

    # Governance check
    if not results.get("governance_adherence", {}).get("no_theorem_elevation", False):
        results_report["mathematical_narrative_reconstruction_validation"]["status"] = "fail"
        results_report["mathematical_narrative_reconstruction_validation"]["errors"].append("Governance violation: theorem elevation not explicitly blocked in results.")

    print(json.dumps(results_report, indent=2))

if __name__ == "__main__":
    validate_narrative_reconstruction()
