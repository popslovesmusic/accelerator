import json
import os
import argparse

def validate_orientation_equivalence():
    results = {
        "orientation_sensitive_equivalence_geometry_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }

    registries = [
        "registry/math/orientation_sensitive_equivalence_geometry_registry.json",
        "registry/math/orientation_refined_preimage_registry.json",
        "registry/math/orientation_conditioned_branch_registry.json",
        "registry/math/orientation_transport_loss_registry.json",
        "registry/math/orientation_reconstruction_hypothesis_registry.json"
    ]

    for reg in registries:
        if not os.path.exists(reg):
            results["orientation_sensitive_equivalence_geometry_validation"]["status"] = "fail"
            results["orientation_sensitive_equivalence_geometry_validation"]["errors"].append(f"Registry missing: {reg}")
        else:
            try:
                with open(reg, 'r') as f:
                    data = json.load(f)
                    results["orientation_sensitive_equivalence_geometry_validation"]["checks"].append(f"Loaded {reg}")
            except Exception as e:
                results["orientation_sensitive_equivalence_geometry_validation"]["status"] = "fail"
                results["orientation_sensitive_equivalence_geometry_validation"]["errors"].append(f"Parse error {reg}: {e}")

    # Specific check: Ensure orientation-splitting is defined
    geo_reg = "registry/math/orientation_sensitive_equivalence_geometry_registry.json"
    if os.path.exists(geo_reg):
        with open(geo_reg, 'r') as f:
            classes = json.load(f).get("orientation_sensitive_equivalence_geometry", {}).get("refinement_classes", [])
            splitting_found = any(c["id"] == "OSE-002" for c in classes)
            if not splitting_found:
                 results["orientation_sensitive_equivalence_geometry_validation"]["status"] = "fail"
                 results["orientation_sensitive_equivalence_geometry_validation"]["errors"].append("Orientation-splitting class OSE-002 missing.")

    return results

if __name__ == "__main__":
    res = validate_orientation_equivalence()
    print(json.dumps(res, indent=2))
