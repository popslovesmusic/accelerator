import json
import os
import sys

def validate_codex_layer():
    registry_path = "registry/math/meta003_mathematical_codex_layer_registry.json"
    result_path = "outputs/math_tests/meta003_mathematical_codex_layer_result.json"
    
    results_report = {
        "mathematical_codex_layer_validation": {
            "status": "pass",
            "warnings": [],
            "errors": []
        }
    }
    
    if not os.path.exists(registry_path):
        results_report["mathematical_codex_layer_validation"]["status"] = "fail"
        results_report["mathematical_codex_layer_validation"]["errors"].append(f"Registry not found: {registry_path}")
        print(json.dumps(results_report, indent=2))
        return
        
    if not os.path.exists(result_path):
        results_report["mathematical_codex_layer_validation"]["status"] = "fail"
        results_report["mathematical_codex_layer_validation"]["errors"].append(f"Results not found: {result_path}")
        print(json.dumps(results_report, indent=2))
        return

    try:
        with open(registry_path, "r") as f: registry = json.load(f)
        with open(result_path, "r") as f: results = json.load(f)
    except Exception as e:
        results_report["mathematical_codex_layer_validation"]["status"] = "fail"
        results_report["mathematical_codex_layer_validation"]["errors"].append(f"JSON Load error: {e}")
        print(json.dumps(results_report, indent=2))
        return

    # Check for presence of codex volumes and index
    volumes = registry["codex_layer"]["volumes"]
    for vol in volumes:
        if not os.path.exists(vol["file_path"]):
            results_report["mathematical_codex_layer_validation"]["status"] = "warning"
            results_report["mathematical_codex_layer_validation"]["warnings"].append(f"Codex volume missing: {vol['file_path']}")
            
    if not os.path.exists(registry["codex_layer"]["master_index"]):
        results_report["mathematical_codex_layer_validation"]["status"] = "fail"
        results_report["mathematical_codex_layer_validation"]["errors"].append(f"Master index missing: {registry['codex_layer']['master_index']}")

    # Governance check
    if not results.get("governance_adherence", {}).get("no_theorem_elevation", False):
        results_report["mathematical_codex_layer_validation"]["status"] = "fail"
        results_report["mathematical_codex_layer_validation"]["errors"].append("Governance violation: theorem elevation not explicitly blocked in results.")

    print(json.dumps(results_report, indent=2))

if __name__ == "__main__":
    validate_codex_layer()
