import json
import os
import argparse

def validate_asymptotic_mapping():
    results = {
        "asymptotic_incompleteness_mapping_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }

    registries = [
        "registry/math/open_question_incompleteness_classification.json",
        "registry/math/asymptotic_incompleteness_mapping_registry.json",
        "registry/math/proof_blocking_incompleteness_registry.json",
        "registry/math/incompleteness_counterexample_obligation_registry.json"
    ]

    for reg in registries:
        if not os.path.exists(reg):
            results["asymptotic_incompleteness_mapping_validation"]["status"] = "fail"
            results["asymptotic_incompleteness_mapping_validation"]["errors"].append(f"Registry missing: {reg}")
        else:
            try:
                with open(reg, 'r') as f:
                    data = json.load(f)
                    results["asymptotic_incompleteness_mapping_validation"]["checks"].append(f"Loaded {reg}")
            except Exception as e:
                results["asymptotic_incompleteness_mapping_validation"]["status"] = "fail"
                results["asymptotic_incompleteness_mapping_validation"]["errors"].append(f"Parse error {reg}: {e}")

    # Explicit check for proof-blocking classification
    blocking_reg = "registry/math/proof_blocking_incompleteness_registry.json"
    if os.path.exists(blocking_reg):
        with open(blocking_reg, 'r') as f:
            data = json.load(f)
            blockers = data.get("proof_blocking_incompleteness", {}).get("blockers", [])
            if len(blockers) < 3:
                results["asymptotic_incompleteness_mapping_validation"]["status"] = "warning"
                results["asymptotic_incompleteness_mapping_validation"]["warnings"].append("Proof-blocking incompleteness set seems sparse.")

    return results

if __name__ == "__main__":
    res = validate_asymptotic_mapping()
    print(json.dumps(res, indent=2))
