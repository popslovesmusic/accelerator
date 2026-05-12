import json
import os
import argparse

def validate_operational_stability(stability_reg, test_reg, failure_regs, obj_reg, op_reg, law_reg):
    results = {
        "operational_stability_validation": {
            "status": "pass",
            "test_count": 0,
            "case_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "closure_gaps": [],
            "open_questions": []
        }
    }

    try:
        with open(stability_reg, 'r') as f: stability_data = json.load(f)
        with open(test_reg, 'r') as f: test_data = json.load(f)
        
        fm_ids = []
        for ffile in failure_regs:
            if os.path.exists(ffile):
                with open(ffile, 'r') as f:
                    fdata = json.load(f)
                    fm_ids.extend([fm["id"] for fm in fdata.get("failure_modes", [])])
        
        with open(obj_reg, 'r') as f: obj_data = json.load(f)
        with open(op_reg, 'r') as f: op_data = json.load(f)
        
        # Collect law IDs for validator reference check
        law_ids = []
        for lfile in law_reg:
            if os.path.exists(lfile):
                with open(lfile, 'r') as f:
                    ldata = json.load(f)
                    law_ids.extend([l["law_id"] for l in ldata.get("laws", [])])

    except Exception as e:
        results["operational_stability_validation"]["status"] = "fail"
        results["operational_stability_validation"]["warnings"].append(f"Load error: {e}")
        return results

    obj_classes = [o["class"] for o in obj_data.get("object_classes", [])]
    op_symbols = [op["symbol"] for op in op_data.get("operators", [])]

    # Validate Stability Tests
    for test in stability_data.get("stability_tests", []):
        results["operational_stability_validation"]["test_count"] += 1
        
        # Check target validator
        if test.get("target_validator") not in law_ids:
             results["operational_stability_validation"]["status"] = "warning"
             results["operational_stability_validation"]["warnings"].append(f"Stability test {test['test_id']} references unknown validator: {test['target_validator']}")
        
        # Check input objects
        for obj in test.get("input_objects", []):
            if obj not in obj_classes:
                results["operational_stability_validation"]["status"] = "warning"
                results["operational_stability_validation"]["warnings"].append(f"Stability test {test['test_id']} references unknown input object: {obj}")
        
        # Check operators
        for op in test.get("operators", []):
            if op not in op_symbols:
                results["operational_stability_validation"]["status"] = "warning"
                results["operational_stability_validation"]["warnings"].append(f"Stability test {test['test_id']} references unknown operator: {op}")
        
        # Check failure modes
        for fm in test.get("failure_modes", []):
            if fm not in fm_ids:
                results["operational_stability_validation"]["status"] = "warning"
                results["operational_stability_validation"]["warnings"].append(f"Stability test {test['test_id']} references unknown failure mode: {fm}")

        results["operational_stability_validation"]["open_questions"].extend(test.get("open_questions", []))

    # Validate Test Cases
    for case in test_data.get("test_cases", []):
        results["operational_stability_validation"]["case_count"] += 1
        test_ids = [t["test_id"] for t in stability_data.get("stability_tests", [])]
        if case.get("test_reference") not in test_ids:
            results["operational_stability_validation"]["status"] = "warning"
            results["operational_stability_validation"]["warnings"].append(f"Test case {case['case_id']} references unknown test: {case['test_reference']}")

    results["operational_stability_validation"]["failure_mode_count"] = len(fm_ids)

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate Phase 2 operational stability registries.")
    parser.add_argument("--stability", default="registry/math/operational_stability_registry.json")
    parser.add_argument("--tests", default="registry/math/phase_2_stability_test_registry.json")
    parser.add_argument("--failures", nargs="+", default=["registry/math/phase_2_failure_mode_registry.json", "registry/math/delta_selection_failure_modes.json"])
    parser.add_argument("--objects", default="registry/formal_objects/formal_object_registry.json")
    parser.add_argument("--operators", default="registry/math/operator_registry.json")
    parser.add_argument("--laws", nargs="+", default=[
        "registry/math/participation_law_registry.json",
        "registry/math/continuation_law_registry.json",
        "registry/math/residue_coupling_law_registry.json"
    ])
    
    args = parser.parse_args()
    res = validate_operational_stability(args.stability, args.tests, args.failures, args.objects, args.operators, args.laws)
    print(json.dumps(res, indent=2))
