import json
import os
import argparse

def validate_structural_classification():
    results = {
        "structural_incompleteness_classification_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }

    registries = [
        "registry/math/structural_incompleteness_classification_registry.json",
        "registry/math/irreducible_incompleteness_registry.json",
        "registry/math/removable_incompleteness_registry.json",
        "registry/math/incompleteness_to_theorem_hypothesis_registry.json"
    ]

    for reg in registries:
        if not os.path.exists(reg):
            results["structural_incompleteness_classification_validation"]["status"] = "fail"
            results["structural_incompleteness_classification_validation"]["errors"].append(f"Registry missing: {reg}")
        else:
            try:
                with open(reg, 'r') as f:
                    data = json.load(f)
                    results["structural_incompleteness_classification_validation"]["checks"].append(f"Loaded {reg}")
            except Exception as e:
                results["structural_incompleteness_classification_validation"]["status"] = "fail"
                results["structural_incompleteness_classification_validation"]["errors"].append(f"Parse error {reg}: {e}")

    # Integrity check: separation of removable and irreducible
    irr_reg = "registry/math/irreducible_incompleteness_registry.json"
    rem_reg = "registry/math/removable_incompleteness_registry.json"
    if os.path.exists(irr_reg) and os.path.exists(rem_reg):
        with open(irr_reg, 'r') as f: irr_ids = [e["target"] for e in json.load(f).get("entries", [])]
        with open(rem_reg, 'r') as f: rem_ids = [e["target"] for e in json.load(f).get("entries", [])]
        overlap = set(irr_ids).intersection(set(rem_ids))
        if overlap:
             results["structural_incompleteness_classification_validation"]["status"] = "fail"
             results["structural_incompleteness_classification_validation"]["errors"].append(f"Classification overlap detected for targets: {overlap}")

    return results

if __name__ == "__main__":
    res = validate_structural_classification()
    print(json.dumps(res, indent=2))
