import json
import os
import argparse

def validate_asymmetry_formalization():
    results = {
        "continuation_reconstruction_asymmetry_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }

    registries = [
        "registry/math/continuation_reconstruction_asymmetry_registry.json",
        "registry/math/reconstruction_loss_classification_registry.json",
        "registry/math/reconstructability_condition_registry.json",
        "registry/math/continuation_vs_reconstruction_operator_registry.json",
        "registry/math/reconstruction_hypothesis_conversion_registry.json"
    ]

    for reg in registries:
        if not os.path.exists(reg):
            results["continuation_reconstruction_asymmetry_validation"]["status"] = "fail"
            results["continuation_reconstruction_asymmetry_validation"]["errors"].append(f"Registry missing: {reg}")
        else:
            try:
                with open(reg, 'r') as f:
                    data = json.load(f)
                    results["continuation_reconstruction_asymmetry_validation"]["checks"].append(f"Loaded {reg}")
            except Exception as e:
                results["continuation_reconstruction_asymmetry_validation"]["status"] = "fail"
                results["continuation_reconstruction_asymmetry_validation"]["errors"].append(f"Parse error {reg}: {e}")

    # Specific check: Ensure forward vs inverse role separation
    op_reg = "registry/math/continuation_vs_reconstruction_operator_registry.json"
    if os.path.exists(op_reg):
        with open(op_reg, 'r') as f:
            ops = json.load(f).get("operator_relations", [])
            for op in ops:
                if op["symbol"] != "Xi":
                    if "forward_role" not in op or "inverse_role" not in op:
                        results["continuation_reconstruction_asymmetry_validation"]["status"] = "fail"
                        results["continuation_reconstruction_asymmetry_validation"]["errors"].append(f"Operator {op['symbol']} missing role separation.")

    return results

if __name__ == "__main__":
    res = validate_asymmetry_formalization()
    print(json.dumps(res, indent=2))
