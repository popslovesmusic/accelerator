import json
import os
import argparse

def validate_participation_measure_refinement(refine_reg, norm_reg, failure_reg):
    results = {
        "participation_measure_refinement_validation": {
            "status": "pass",
            "entry_count": 0,
            "rule_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(refine_reg, 'r') as f: refine_data = json.load(f)
        with open(norm_reg, 'r') as f: norm_data = json.load(f)
        with open(failure_reg, 'r') as f: failure_data = json.load(f)
    except Exception as e:
        results["participation_measure_refinement_validation"]["status"] = "fail"
        results["participation_measure_refinement_validation"]["errors"].append(f"Load error: {e}")
        return results

    measure_classes = [mc["class"] for mc in refine_data.get("measure_classes", [])]
    rule_ids = [r["rule_id"] for r in norm_data.get("normalization_rules", [])]
    fm_ids = [fm["id"] for fm in failure_data.get("failure_modes", [])]

    # Validate Refinement Entries
    for entry in refine_data.get("refinement_entries", []):
        results["participation_measure_refinement_validation"]["entry_count"] += 1
        if entry.get("primary_class") not in measure_classes:
            results["participation_measure_refinement_validation"]["status"] = "warning"
            results["participation_measure_refinement_validation"]["warnings"].append(f"Entry {entry['target']} has unknown measure class: {entry['primary_class']}")

    # Validate Normalization Rules
    for rule in norm_data.get("normalization_rules", []):
        results["participation_measure_refinement_validation"]["rule_count"] += 1
        if rule.get("applicability") not in measure_classes:
             results["participation_measure_refinement_validation"]["status"] = "warning"
             results["participation_measure_refinement_validation"]["warnings"].append(f"Rule {rule['rule_id']} references unknown class: {rule['applicability']}")

    results["participation_measure_refinement_validation"]["failure_mode_count"] = len(fm_ids)

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate participation measure refinement registries.")
    parser.add_argument("--refine", default="registry/math/participation_measure_refinement_registry.json")
    parser.add_argument("--norm", default="registry/math/measure_normalization_registry.json")
    parser.add_argument("--failures", default="registry/math/participation_measure_failure_modes.json")
    
    args = parser.parse_args()
    res = validate_participation_measure_refinement(args.refine, args.norm, args.failures)
    print(json.dumps(res, indent=2))
