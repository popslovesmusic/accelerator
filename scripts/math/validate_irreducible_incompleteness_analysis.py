import json
import os
import argparse

def validate_irreducible_analysis():
    results = {
        "irreducible_incompleteness_analysis_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }

    registries = [
        "registry/math/irreducible_incompleteness_analysis_registry.json",
        "registry/math/incompleteness_irreducibility_decision_registry.json",
        "registry/math/incompleteness_refinement_path_registry.json",
        "registry/math/incompleteness_to_hypothesis_conversion_registry.json"
    ]

    for reg in registries:
        if not os.path.exists(reg):
            results["irreducible_incompleteness_analysis_validation"]["status"] = "fail"
            results["irreducible_incompleteness_analysis_validation"]["errors"].append(f"Registry missing: {reg}")
        else:
            try:
                with open(reg, 'r') as f:
                    data = json.load(f)
                    results["irreducible_incompleteness_analysis_validation"]["checks"].append(f"Loaded {reg}")
            except Exception as e:
                results["irreducible_incompleteness_analysis_validation"]["status"] = "fail"
                results["irreducible_incompleteness_analysis_validation"]["errors"].append(f"Parse error {reg}: {e}")

    # Specific check: ensure irreducible targets are classified in analysis
    analysis_reg = "registry/math/irreducible_incompleteness_analysis_registry.json"
    if os.path.exists(analysis_reg):
        with open(analysis_reg, 'r') as f:
            logs = json.load(f).get("irreducible_incompleteness_analysis", {}).get("analysis_log", [])
            irreducible_count = sum(1 for log in logs if "irreducible" in log["root_cause"])
            if irreducible_count < 4:
                 results["irreducible_incompleteness_analysis_validation"]["status"] = "warning"
                 results["irreducible_incompleteness_analysis_validation"]["warnings"].append("Irreducible feature identification seems incomplete.")

    return results

if __name__ == "__main__":
    res = validate_irreducible_analysis()
    print(json.dumps(res, indent=2))
