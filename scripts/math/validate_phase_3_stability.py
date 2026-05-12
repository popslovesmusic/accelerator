import json
import os
import argparse

def validate_phase_3_stability(baseline_reg, perturbation_reg, failure_reg, op_reg, theorem_reg):
    results = {
        "phase_3_stability_validation": {
            "status": "pass",
            "test_count": 0,
            "perturbation_class_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "closure_gaps": [],
            "open_questions": []
        }
    }

    try:
        with open(baseline_reg, 'r') as f: baseline_data = json.load(f)
        with open(perturbation_reg, 'r') as f: pert_data = json.load(f)
        with open(failure_reg, 'r') as f: failure_data = json.load(f)
        with open(op_reg, 'r') as f: op_data = json.load(f)
        with open(theorem_reg, 'r') as f: theorem_data = json.load(f)
    except Exception as e:
        results["phase_3_stability_validation"]["status"] = "fail"
        results["phase_3_stability_validation"]["warnings"].append(f"Load error: {e}")
        return results

    op_symbols = [op["symbol"] for op in op_data.get("operators", [])]
    # Add non-primitive targets
    op_symbols.extend(["branch_pruning", "orientation_minimization", "observable_projection", "residue_update", "NavT", "Pi_A", "delta", "symbolic_reduction_chains"])
    
    theorem_ids = [t["theorem_id"] for t in theorem_data.get("theorems", [])]
    fm_ids = [fm["id"] for fm in failure_data.get("failure_modes", [])]
    pert_classes = [c["class"] for c in pert_data.get("perturbation_classes", [])]
    stab_domains = baseline_data.get("stability_test_domains", [])

    # Validate Baseline Tests
    for test in baseline_data.get("baseline_tests", []):
        results["phase_3_stability_validation"]["test_count"] += 1
        
        # Check target
        target = test.get("target")
        if target not in op_symbols and target not in theorem_ids:
             results["phase_3_stability_validation"]["status"] = "warning"
             results["phase_3_stability_validation"]["warnings"].append(f"Phase 3 test {test['test_id']} references unknown target: {target}")
        
        # Check domain
        if test.get("domain") not in stab_domains:
             results["phase_3_stability_validation"]["status"] = "warning"
             results["phase_3_stability_validation"]["warnings"].append(f"Phase 3 test {test['test_id']} references unknown domain: {test['domain']}")

        # Check perturbation class
        if test.get("perturbation_class") not in pert_classes:
             results["phase_3_stability_validation"]["status"] = "warning"
             results["phase_3_stability_validation"]["warnings"].append(f"Phase 3 test {test['test_id']} references unknown perturbation class: {test['perturbation_class']}")

        # Check failure modes
        for fm in test.get("failure_modes", []):
            if fm not in fm_ids:
                results["phase_3_stability_validation"]["status"] = "warning"
                results["phase_3_stability_validation"]["warnings"].append(f"Phase 3 test {test['test_id']} references unknown failure mode: {fm}")

    results["phase_3_stability_validation"]["perturbation_class_count"] = len(pert_classes)
    results["phase_3_stability_validation"]["failure_mode_count"] = len(fm_ids)

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate Phase 3 stability baseline registries.")
    parser.add_argument("--baseline", default="registry/math/phase_3_stability_baseline_registry.json")
    parser.add_argument("--perturbations", default="registry/math/phase_3_perturbation_test_registry.json")
    parser.add_argument("--failures", default="registry/math/phase_3_recursive_failure_modes.json")
    parser.add_argument("--operators", default="registry/math/operator_registry.json")
    parser.add_argument("--theorems", default="registry/math/minimal_theorem_registry.json")
    
    args = parser.parse_args()
    res = validate_phase_3_stability(args.baseline, args.perturbations, args.failures, args.operators, args.theorems)
    print(json.dumps(res, indent=2))
