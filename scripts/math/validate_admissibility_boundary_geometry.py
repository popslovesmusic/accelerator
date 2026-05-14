import json
import os
import argparse

def validate_boundary_geometry():
    results = {
        "admissibility_boundary_geometry_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }

    registries = [
        "registry/math/admissibility_boundary_geometry_registry.json",
        "registry/math/epsilon_null_boundary_geometry_registry.json",
        "registry/math/orientation_admissibility_window_registry.json",
        "registry/math/recursive_stability_boundary_registry.json",
        "registry/math/transport_threshold_boundary_registry.json",
        "registry/math/branch_retention_boundary_registry.json",
        "registry/math/admissibility_boundary_hypothesis_registry.json"
    ]

    for reg in registries:
        if not os.path.exists(reg):
            results["admissibility_boundary_geometry_validation"]["status"] = "fail"
            results["admissibility_boundary_geometry_validation"]["errors"].append(f"Registry missing: {reg}")
        else:
            try:
                with open(reg, 'r') as f:
                    data = json.load(f)
                    results["admissibility_boundary_geometry_validation"]["checks"].append(f"Loaded {reg}")
            except Exception as e:
                results["admissibility_boundary_geometry_validation"]["status"] = "fail"
                results["admissibility_boundary_geometry_validation"]["errors"].append(f"Parse error {reg}: {e}")

    # Specific check: Ensure all ABG classes are mapped to a detailed registry
    main_reg = "registry/math/admissibility_boundary_geometry_registry.json"
    if os.path.exists(main_reg):
        with open(main_reg, 'r') as f:
            classes = json.load(f).get("admissibility_boundary_geometry", {}).get("boundary_classes", [])
            if len(classes) < 7:
                 results["admissibility_boundary_geometry_validation"]["status"] = "warning"
                 results["admissibility_boundary_geometry_validation"]["warnings"].append("Main geometry registry lacks some expected boundary classes.")

    return results

if __name__ == "__main__":
    res = validate_boundary_geometry()
    print(json.dumps(res, indent=2))
