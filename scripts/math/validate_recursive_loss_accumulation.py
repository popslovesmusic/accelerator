import json
import os
import argparse

def validate_recursive_loss():
    results = {
        "recursive_loss_accumulation_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }

    registries = [
        "registry/math/recursive_loss_accumulation_registry.json",
        "registry/math/recursive_reconstruction_ambiguity_registry.json",
        "registry/math/loss_saturation_basin_registry.json",
        "registry/math/recursive_loss_failure_modes.json",
        "registry/math/recursive_loss_hypothesis_registry.json"
    ]

    for reg in registries:
        if not os.path.exists(reg):
            results["recursive_loss_accumulation_validation"]["status"] = "fail"
            results["recursive_loss_accumulation_validation"]["errors"].append(f"Registry missing: {reg}")
        else:
            try:
                with open(reg, 'r') as f:
                    data = json.load(f)
                    results["recursive_loss_accumulation_validation"]["checks"].append(f"Loaded {reg}")
            except Exception as e:
                results["recursive_loss_accumulation_validation"]["status"] = "fail"
                results["recursive_loss_accumulation_validation"]["errors"].append(f"Parse error {reg}: {e}")

    # Specific check: address the incomplete warning from the previous task
    acc_reg = "registry/math/recursive_loss_accumulation_registry.json"
    if os.path.exists(acc_reg):
        with open(acc_reg, 'r') as f:
            mappings = json.load(f).get("recursive_loss_accumulation", {}).get("operator_dynamics_mapping", [])
            if len(mappings) >= 4:
                results["recursive_loss_accumulation_validation"]["checks"].append("Recursive loss mapping expanded to core operators.")
            else:
                 results["recursive_loss_accumulation_validation"]["status"] = "warning"
                 results["recursive_loss_accumulation_validation"]["warnings"].append("Recursive loss mapping still lacks some operator coverage.")

    return results

if __name__ == "__main__":
    res = validate_recursive_loss()
    print(json.dumps(res, indent=2))
