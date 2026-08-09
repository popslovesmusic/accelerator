import json
import os
import argparse

def validate_xi_reconstruction_bounds():
    results = {
        "xi_reconstruction_bounds_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }

    registries = [
        "registry/math/xi_reconstruction_bounds_registry.json",
        "registry/math/xi_preimage_classification_registry.json",
        "registry/math/xi_reconstruction_failure_modes.json",
        "registry/math/xi_reconstruction_hypothesis_registry.json"
    ]

    for reg in registries:
        if not os.path.exists(reg):
            results["xi_reconstruction_bounds_validation"]["status"] = "fail"
            results["xi_reconstruction_bounds_validation"]["errors"].append(f"Registry missing: {reg}")
        else:
            try:
                with open(reg, 'r') as f:
                    data = json.load(f)
                    results["xi_reconstruction_bounds_validation"]["checks"].append(f"Loaded {reg}")
            except Exception as e:
                results["xi_reconstruction_bounds_validation"]["status"] = "fail"
                results["xi_reconstruction_bounds_validation"]["errors"].append(f"Parse error {reg}: {e}")

    # Specific check: Ensure Xi target status is correct
    bounds_reg = "registry/math/xi_reconstruction_bounds_registry.json"
    if os.path.exists(bounds_reg):
        with open(bounds_reg, 'r') as f:
            data = json.load(f).get("xi_reconstruction_bounds", {})
            if data.get("status") != "bounded_reconstruction_scaffold":
                results["xi_reconstruction_bounds_validation"]["status"] = "fail"
                results["xi_reconstruction_bounds_validation"]["errors"].append("Xi status is not bounded_reconstruction_scaffold.")

    return results

if __name__ == "__main__":
    res = validate_xi_reconstruction_bounds()
    print(json.dumps(res, indent=2))
