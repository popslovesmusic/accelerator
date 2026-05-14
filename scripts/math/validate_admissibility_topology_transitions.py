import json
import os
import argparse

def validate_topology_transitions():
    results = {
        "admissibility_topology_transitions_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }

    registries = [
        "registry/math/admissibility_topology_transition_registry.json",
        "registry/math/admissibility_basin_transition_registry.json",
        "registry/math/orientation_window_transition_registry.json",
        "registry/math/epsilon_null_bifurcation_registry.json",
        "registry/math/branch_retention_transition_registry.json",
        "registry/math/recursive_stability_transition_registry.json",
        "registry/math/admissibility_transition_hypothesis_registry.json"
    ]

    for reg in registries:
        if not os.path.exists(reg):
            results["admissibility_topology_transitions_validation"]["status"] = "fail"
            results["admissibility_topology_transitions_validation"]["errors"].append(f"Registry missing: {reg}")
        else:
            try:
                with open(reg, 'r') as f:
                    data = json.load(f)
                    results["admissibility_topology_transitions_validation"]["checks"].append(f"Loaded {reg}")
            except Exception as e:
                results["admissibility_topology_transitions_validation"]["status"] = "fail"
                results["admissibility_topology_transitions_validation"]["errors"].append(f"Parse error {reg}: {e}")

    # Specific check: Ensure critical transition types are registered
    main_reg = "registry/math/admissibility_topology_transition_registry.json"
    if os.path.exists(main_reg):
        with open(main_reg, 'r') as f:
            classes = json.load(f).get("admissibility_topology_transition", {}).get("transition_classes", [])
            has_split = any(c["id"] == "ATT-002" for c in classes)
            has_bifurcation = any(c["id"] == "ATT-005" for c in classes)
            if not has_split or not has_bifurcation:
                 results["admissibility_topology_transitions_validation"]["status"] = "fail"
                 results["admissibility_topology_transitions_validation"]["errors"].append("Critical transition classes (split/bifurcation) missing.")

    return results

if __name__ == "__main__":
    res = validate_topology_transitions()
    print(json.dumps(res, indent=2))
