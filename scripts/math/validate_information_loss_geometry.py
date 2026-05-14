import json
import os
import argparse

def validate_loss_geometry():
    results = {
        "information_loss_geometry_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }

    registries = [
        "registry/math/information_loss_geometry_registry.json",
        "registry/math/operator_loss_classification_registry.json",
        "registry/math/reconstruction_ambiguity_geometry_registry.json",
        "registry/math/loss_accumulation_under_recursion_registry.json",
        "registry/math/information_loss_theorem_hypothesis_registry.json"
    ]

    for reg in registries:
        if not os.path.exists(reg):
            results["information_loss_geometry_validation"]["status"] = "fail"
            results["information_loss_geometry_validation"]["errors"].append(f"Registry missing: {reg}")
        else:
            try:
                with open(reg, 'r') as f:
                    data = json.load(f)
                    results["information_loss_geometry_validation"]["checks"].append(f"Loaded {reg}")
            except Exception as e:
                results["information_loss_geometry_validation"]["status"] = "fail"
                results["information_loss_geometry_validation"]["errors"].append(f"Parse error {reg}: {e}")

    # Specific check: ensure recursive loss accumulation is classified
    recursive_reg = "registry/math/loss_accumulation_under_recursion_registry.json"
    if os.path.exists(recursive_reg):
        with open(recursive_reg, 'r') as f:
            data = json.load(f).get("loss_accumulation_under_recursion", {})
            mapping = data.get("operator_recursion_mapping", [])
            if len(mapping) < 2:
                 results["information_loss_geometry_validation"]["status"] = "warning"
                 results["information_loss_geometry_validation"]["warnings"].append("Recursive loss mapping seems incomplete.")

    return results

if __name__ == "__main__":
    res = validate_loss_geometry()
    print(json.dumps(res, indent=2))
