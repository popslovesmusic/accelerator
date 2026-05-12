import json
import os
import argparse

def validate_epsilon_null_measure(en_reg, pm_reg, failure_reg, obj_reg, law_reg):
    results = {
        "epsilon_null_measure_validation": {
            "status": "pass",
            "en_entry_count": 0,
            "pm_entry_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "closure_gaps": [],
            "open_questions": []
        }
    }

    try:
        with open(en_reg, 'r') as f: en_data = json.load(f)
        with open(pm_reg, 'r') as f: pm_data = json.load(f)
        with open(failure_reg, 'r') as f: failure_data = json.load(f)
        with open(obj_reg, 'r') as f: obj_data = json.load(f)
        with open(law_reg, 'r') as f: law_data = json.load(f)
    except Exception as e:
        results["epsilon_null_measure_validation"]["status"] = "fail"
        results["epsilon_null_measure_validation"]["warnings"].append(f"Load error: {e}")
        return results

    obj_classes = [o["class"] for o in obj_data.get("object_classes", [])]
    law_ids = [l["law_id"] for l in law_data.get("laws", [])]
    fm_ids = [fm["id"] for fm in failure_data.get("failure_modes", [])]
    en_classes = [c["class"] for c in en_data.get("epsilon_null_classes", [])]
    pm_classes = [c["class"] for c in pm_data.get("participation_measure_classes", [])]

    # Validate Epsilon Null Entries
    for entry in en_data.get("epsilon_null_entries", []):
        results["epsilon_null_measure_validation"]["en_entry_count"] += 1
        if entry.get("target_law") not in law_ids:
            results["epsilon_null_measure_validation"]["status"] = "warning"
            results["epsilon_null_measure_validation"]["warnings"].append(f"EN entry {entry['entry_id']} references unknown law: {entry['target_law']}")
        if entry.get("epsilon_class") not in en_classes:
            results["epsilon_null_measure_validation"]["status"] = "warning"
            results["epsilon_null_measure_validation"]["warnings"].append(f"EN entry {entry['entry_id']} references unknown class: {entry['epsilon_class']}")
        for fm in entry.get("failure_modes", []):
            if fm not in fm_ids:
                results["epsilon_null_measure_validation"]["status"] = "warning"
                results["epsilon_null_measure_validation"]["warnings"].append(f"EN entry {entry['entry_id']} references unknown failure mode: {fm}")

    # Validate Participation Measure Entries
    for entry in pm_data.get("measure_entries", []):
        results["epsilon_null_measure_validation"]["pm_entry_count"] += 1
        if entry.get("target_object") not in obj_classes:
            results["epsilon_null_measure_validation"]["status"] = "warning"
            results["epsilon_null_measure_validation"]["warnings"].append(f"PM entry {entry['entry_id']} references unknown object: {entry['target_object']}")
        if entry.get("measure_class") not in pm_classes:
            results["epsilon_null_measure_validation"]["status"] = "warning"
            results["epsilon_null_measure_validation"]["pm_entry_count"] += 1
            results["epsilon_null_measure_validation"]["status"] = "warning"
            results["epsilon_null_measure_validation"]["warnings"].append(f"PM entry {entry['entry_id']} references unknown class: {entry['measure_class']}")
        for fm in entry.get("failure_modes", []):
            if fm not in fm_ids:
                results["epsilon_null_measure_validation"]["status"] = "warning"
                results["epsilon_null_measure_validation"]["warnings"].append(f"PM entry {entry['entry_id']} references unknown failure mode: {fm}")

    results["epsilon_null_measure_validation"]["failure_mode_count"] = len(fm_ids)
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate epsilon_null and participation measure registries.")
    parser.add_argument("--en", default="registry/math/epsilon_null_registry.json")
    parser.add_argument("--pm", default="registry/math/participation_measure_registry.json")
    parser.add_argument("--failures", default="registry/math/null_boundary_failure_modes.json")
    parser.add_argument("--objects", default="registry/formal_objects/formal_object_registry.json")
    parser.add_argument("--laws", default="registry/math/participation_law_registry.json")
    
    args = parser.parse_args()
    res = validate_epsilon_null_measure(args.en, args.pm, args.failures, args.objects, args.laws)
    print(json.dumps(res, indent=2))
