import json
import os
import argparse

def validate_boundary_case_classification(boundary_reg, binding_reg, failure_reg, theorem_reg):
    results = {
        "boundary_case_classification_validation": {
            "status": "pass",
            "class_count": 0,
            "binding_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(boundary_reg, 'r') as f: boundary_data = json.load(f)
        with open(binding_reg, 'r') as f: binding_data = json.load(f)
        with open(failure_reg, 'r') as f: failure_data = json.load(f)
        with open(theorem_reg, 'r') as f: theorem_data = json.load(f)
    except Exception as e:
        results["boundary_case_classification_validation"]["status"] = "fail"
        results["boundary_case_classification_validation"]["errors"].append(f"Load error: {e}")
        return results

    class_names = [c["class"] for c in boundary_data.get("boundary_case_classes", [])]
    status_values = binding_data.get("boundary_status_values", [])
    fm_ids = [fm["id"] for fm in failure_data.get("failure_modes", [])]
    theorem_ids = [t["theorem_id"] for t in theorem_data.get("theorems", [])]

    results["boundary_case_classification_validation"]["class_count"] = len(class_names)
    results["boundary_case_classification_validation"]["failure_mode_count"] = len(fm_ids)

    # Validate Theorem Bindings
    for binding in binding_data.get("theorem_bindings", []):
        results["boundary_case_classification_validation"]["binding_count"] += 1
        tid = binding.get("theorem_id")
        if tid not in theorem_ids:
            results["boundary_case_classification_validation"]["status"] = "warning"
            results["boundary_case_classification_validation"]["warnings"].append(f"Binding references unknown theorem: {tid}")
        
        for case in binding.get("boundary_cases", []):
            if case["case"] not in class_names:
                results["boundary_case_classification_validation"]["status"] = "warning"
                results["boundary_case_classification_validation"]["warnings"].append(f"Binding for {tid} references unknown class: {case['case']}")
            
            if case["status"] not in status_values:
                results["boundary_case_classification_validation"]["status"] = "warning"
                results["boundary_case_classification_validation"]["warnings"].append(f"Binding for {tid}/{case['case']} has unknown status: {case['status']}")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate boundary-case classification registries.")
    parser.add_argument("--boundary", default="registry/math/boundary_case_registry.json")
    parser.add_argument("--binding", default="registry/math/theorem_boundary_condition_registry.json")
    parser.add_argument("--failures", default="registry/math/boundary_case_failure_modes.json")
    parser.add_argument("--theorems", default="registry/math/minimal_theorem_registry.json")
    
    args = parser.parse_args()
    res = validate_boundary_case_classification(args.boundary, args.binding, args.failures, args.theorems)
    print(json.dumps(res, indent=2))
