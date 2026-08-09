import json
import os
import argparse

def validate_equivalence_geometry():
    results = {
        "reconstruction_equivalence_geometry_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }

    registries = [
        "registry/math/reconstruction_equivalence_geometry_registry.json",
        "registry/math/reconstruction_preimage_family_registry.json",
        "registry/math/observable_indistinguishability_class_registry.json",
        "registry/math/recursive_equivalence_basin_registry.json",
        "registry/math/reconstruction_equivalence_hypothesis_registry.json"
    ]

    for reg in registries:
        if not os.path.exists(reg):
            results["reconstruction_equivalence_geometry_validation"]["status"] = "fail"
            results["reconstruction_equivalence_geometry_validation"]["errors"].append(f"Registry missing: {reg}")
        else:
            try:
                with open(reg, 'r') as f:
                    data = json.load(f)
                    results["reconstruction_equivalence_geometry_validation"]["checks"].append(f"Loaded {reg}")
            except Exception as e:
                results["reconstruction_equivalence_geometry_validation"]["status"] = "fail"
                results["reconstruction_equivalence_geometry_validation"]["errors"].append(f"Parse error {reg}: {e}")

    # Specific check: Ensure all operators from geometry are mapped to preimage families
    geo_reg = "registry/math/reconstruction_equivalence_geometry_registry.json"
    fam_reg = "registry/math/reconstruction_preimage_family_registry.json"
    if os.path.exists(geo_reg) and os.path.exists(fam_reg):
        with open(geo_reg, 'r') as f: geo_ops = [c["source_operator"] for c in json.load(f).get("reconstruction_equivalence_geometry", {}).get("equivalence_classes", [])]
        with open(fam_reg, 'r') as f: fam_ops = [m["operator"] for m in json.load(f).get("reconstruction_preimage_family", {}).get("operator_family_mapping", [])]
        
        # Note: REC-EQ-005 Xi doesn't necessarily have a family mapping yet as it's a basin candidate
        for op in geo_ops:
            if op not in fam_ops and op not in ["Xi", "observable_projection"]:
                 results["reconstruction_equivalence_geometry_validation"]["status"] = "warning"
                 results["reconstruction_equivalence_geometry_validation"]["warnings"].append(f"Operator {op} in geometry lacks preimage family mapping.")

    return results

if __name__ == "__main__":
    res = validate_equivalence_geometry()
    print(json.dumps(res, indent=2))
