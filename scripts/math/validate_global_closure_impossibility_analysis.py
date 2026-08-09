import json
import os
import argparse

def validate_impossibility_analysis():
    results = {
        "global_closure_impossibility_analysis_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }

    registries = [
        "registry/math/global_closure_impossibility_registry.json",
        "registry/math/closure_status_classification_registry.json",
        "registry/math/global_closure_blocker_registry.json",
        "registry/math/impossibility_to_theorem_hypothesis_registry.json"
    ]

    for reg in registries:
        if not os.path.exists(reg):
            results["global_closure_impossibility_analysis_validation"]["status"] = "fail"
            results["global_closure_impossibility_analysis_validation"]["errors"].append(f"Registry missing: {reg}")
        else:
            try:
                with open(reg, 'r') as f:
                    data = json.load(f)
                    results["global_closure_impossibility_analysis_validation"]["checks"].append(f"Loaded {reg}")
            except Exception as e:
                results["global_closure_impossibility_analysis_validation"]["status"] = "fail"
                results["global_closure_impossibility_analysis_validation"]["errors"].append(f"Parse error {reg}: {e}")

    # Specific check: separation of local admissibility from global impossibility
    imp_reg = "registry/math/global_closure_impossibility_registry.json"
    if os.path.exists(imp_reg):
        with open(imp_reg, 'r') as f:
            targets = json.load(f).get("global_closure_impossibility", {}).get("targets", [])
            impossible_candidates = [t for t in targets if t["status"] == "formally_impossible_candidate"]
            if len(impossible_candidates) < 2:
                 results["global_closure_impossibility_analysis_validation"]["status"] = "warning"
                 results["global_closure_impossibility_analysis_validation"]["warnings"].append("Few targets classified as formally impossible candidates.")

    return results

if __name__ == "__main__":
    res = validate_impossibility_analysis()
    print(json.dumps(res, indent=2))
