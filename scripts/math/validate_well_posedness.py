import json
import os
import argparse

def validate_well_posedness(wp_reg, fm_reg, obj_reg, op_reg, rel_reg):
    results = {
        "well_posedness_validation": {
            "status": "pass",
            "entry_count": 0,
            "failure_mode_count": 0,
            "undefined_existence": [],
            "undefined_uniqueness": [],
            "undefined_stability": [],
            "closure_gaps": [],
            "open_questions": [],
            "warnings": []
        }
    }

    try:
        with open(wp_reg, 'r') as f: wp_data = json.load(f)
        with open(fm_reg, 'r') as f: fm_data = json.load(f)
        with open(obj_reg, 'r') as f: obj_data = json.load(f)
        with open(op_reg, 'r') as f: op_data = json.load(f)
        with open(rel_reg, 'r') as f: rel_data = json.load(f)
    except Exception as e:
        results["well_posedness_validation"]["status"] = "fail"
        results["well_posedness_validation"]["warnings"].append(f"Load error: {e}")
        return results

    # Gather valid symbols
    valid_symbols = []
    for o in obj_data.get("object_classes", []): valid_symbols.append(o["class"])
    for o in op_data.get("operators", []): valid_symbols.append(o["symbol"])
    for r in rel_data.get("relations", []): valid_symbols.append(r["name"])
    
    failure_mode_ids = [f["id"] for f in fm_data.get("failure_modes", [])]
    results["well_posedness_validation"]["failure_mode_count"] = len(failure_mode_ids)

    for entry in wp_data.get("entries", []):
        results["well_posedness_validation"]["entry_count"] += 1
        symbol = entry["target_symbol"]
        
        if symbol not in valid_symbols and entry["target_type"] != "system":
            results["well_posedness_validation"]["status"] = "warning"
            results["well_posedness_validation"]["warnings"].append(f"Well-posedness target '{symbol}' not found in formal registries.")

        if entry.get("existence_status") == "undefined":
            results["well_posedness_validation"]["undefined_existence"].append(symbol)
        if entry.get("uniqueness_status") == "undefined":
            results["well_posedness_validation"]["undefined_uniqueness"].append(symbol)
        if entry.get("stability_status") == "undefined":
            results["well_posedness_validation"]["undefined_stability"].append(symbol)
        if entry.get("closure_status") in ["undefined", "not_closed"]:
            results["well_posedness_validation"]["closure_gaps"].append(symbol)

        # Check failure modes
        for fm in entry.get("known_failure_modes", []):
            if fm not in failure_mode_ids:
                results["well_posedness_validation"]["warnings"].append(f"Entry {symbol} references unknown failure mode: {fm}")

        # Check proof status vs formal declaration
        if entry.get("existence_status") == "formal" or entry.get("uniqueness_status") == "formal":
             if entry.get("proof_status") != "formal":
                 results["well_posedness_validation"]["status"] = "fail"
                 results["well_posedness_validation"]["warnings"].append(f"Entry {symbol} declares formal status without formal proof_status.")

        results["well_posedness_validation"]["open_questions"].extend(entry.get("open_questions", []))

    if results["well_posedness_validation"]["closure_gaps"] or results["well_posedness_validation"]["warnings"]:
        if results["well_posedness_validation"]["status"] == "pass":
            results["well_posedness_validation"]["status"] = "warning"

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate well-posedness registry.")
    parser.add_argument("--wp", default="registry/math/well_posedness_registry.json")
    parser.add_argument("--fm", default="registry/math/failure_mode_registry.json")
    parser.add_argument("--objects", default="registry/formal_objects/formal_object_registry.json")
    parser.add_argument("--operators", default="registry/math/operator_registry.json")
    parser.add_argument("--relations", default="registry/math/relation_registry.json")
    
    args = parser.parse_args()
    res = validate_well_posedness(args.wp, args.fm, args.objects, args.operators, args.relations)
    print(json.dumps(res, indent=2))
