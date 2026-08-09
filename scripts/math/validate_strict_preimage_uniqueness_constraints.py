import json
import os
import argparse

def validate_uniqueness_constraints():
    results = {
        "strict_preimage_uniqueness_constraints_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }

    registries = [
        "registry/math/strict_preimage_uniqueness_constraints_registry.json",
        "registry/math/orientation_preimage_splitting_registry.json",
        "registry/math/preimage_failure_mode_registry.json",
        "registry/math/local_reconstructability_constraint_registry.json",
        "registry/math/preimage_uniqueness_hypothesis_registry.json"
    ]

    for reg in registries:
        if not os.path.exists(reg):
            results["strict_preimage_uniqueness_constraints_validation"]["status"] = "fail"
            results["strict_preimage_uniqueness_constraints_validation"]["errors"].append(f"Registry missing: {reg}")
        else:
            try:
                with open(reg, 'r') as f:
                    data = json.load(f)
                    results["strict_preimage_uniqueness_constraints_validation"]["checks"].append(f"Loaded {reg}")
            except Exception as e:
                results["strict_preimage_uniqueness_constraints_validation"]["status"] = "fail"
                results["strict_preimage_uniqueness_constraints_validation"]["errors"].append(f"Parse error {reg}: {e}")

    # Specific check: separation of local uniqueness and global blocking
    strict_reg = "registry/math/strict_preimage_uniqueness_constraints_registry.json"
    if os.path.exists(strict_reg):
        with open(strict_reg, 'r') as f:
            classes = json.load(f).get("strict_preimage_uniqueness_constraints", {}).get("constraint_classes", [])
            has_local = any(c["id"] == "SPU-001" for c in classes)
            has_global_blocked = any(c["id"] == "SPU-004" for c in classes)
            if not has_local or not has_global_blocked:
                 results["strict_preimage_uniqueness_constraints_validation"]["status"] = "fail"
                 results["strict_preimage_uniqueness_constraints_validation"]["errors"].append("Local vs Global uniqueness separation missing in constraint classes.")

    return results

if __name__ == "__main__":
    res = validate_uniqueness_constraints()
    print(json.dumps(res, indent=2))
