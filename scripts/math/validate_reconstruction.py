import json
import os
import argparse

def validate_reconstruction(rec_reg, rfm_reg, obj_reg, op_reg, rel_reg):
    results = {
        "reconstruction_validation": {
            "status": "pass",
            "entry_count": 0,
            "failure_mode_count": 0,
            "undefined_inversion": [],
            "undefined_reconstruction": [],
            "non_invertible_targets": [],
            "multi_valued_targets": [],
            "missing_failure_bindings": [],
            "open_questions": [],
            "warnings": []
        }
    }

    try:
        with open(rec_reg, 'r') as f: rec_data = json.load(f)
        with open(rfm_reg, 'r') as f: rfm_data = json.load(f)
        with open(obj_reg, 'r') as f: obj_data = json.load(f)
        with open(op_reg, 'r') as f: op_data = json.load(f)
        with open(rel_reg, 'r') as f: rel_data = json.load(f)
    except Exception as e:
        results["reconstruction_validation"]["status"] = "fail"
        results["reconstruction_validation"]["warnings"].append(f"Load error: {e}")
        return results

    # Gather valid symbols
    valid_symbols = []
    for o in obj_data.get("object_classes", []): valid_symbols.append(o["class"])
    for o in op_data.get("operators", []): valid_symbols.append(o["symbol"])
    for r in rel_data.get("relations", []): valid_symbols.append(r["name"])
    # observables are a bit more loose, but we'll add REC-003 target as valid for now
    valid_symbols.append("observable_projection")
    
    failure_mode_ids = [f["id"] for f in rfm_data.get("failure_modes", [])]
    results["reconstruction_validation"]["failure_mode_count"] = len(failure_mode_ids)

    for entry in rec_data.get("entries", []):
        results["reconstruction_validation"]["entry_count"] += 1
        symbol = entry["target_symbol"]
        
        if symbol not in valid_symbols and entry["target_type"] != "observable":
            results["reconstruction_validation"]["status"] = "warning"
            results["reconstruction_validation"]["warnings"].append(f"Reconstruction target '{symbol}' not found in formal registries.")

        if entry.get("inversion_status") == "undefined":
            results["reconstruction_validation"]["undefined_inversion"].append(symbol)
        elif entry.get("inversion_status") == "non_invertible":
            results["reconstruction_validation"]["non_invertible_targets"].append(symbol)
            if not entry.get("information_loss_notes"):
                results["reconstruction_validation"]["warnings"].append(f"Non-invertible target {symbol} missing information_loss_notes.")
        elif entry.get("inversion_status") == "multi_valued":
            results["reconstruction_validation"]["multi_valued_targets"].append(symbol)

        if entry.get("reconstruction_status") == "undefined":
            results["reconstruction_validation"]["undefined_reconstruction"].append(symbol)

        # Check failure modes
        for fm in entry.get("known_failure_modes", []):
            if fm not in failure_mode_ids:
                results["reconstruction_validation"]["warnings"].append(f"Entry {symbol} references unknown failure mode: {fm}")

        # Check proof status vs formal declaration
        if entry.get("reconstruction_status") == "formal":
             if entry.get("proof_status") != "formal":
                 results["reconstruction_validation"]["status"] = "fail"
                 results["reconstruction_validation"]["warnings"].append(f"Entry {symbol} declares formal status without formal proof_status.")

        results["reconstruction_validation"]["open_questions"].extend(entry.get("open_questions", []))

    if results["reconstruction_validation"]["warnings"]:
        if results["reconstruction_validation"]["status"] == "pass":
            results["reconstruction_validation"]["status"] = "warning"

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate reconstruction registries.")
    parser.add_argument("--rec", default="registry/math/reconstruction_registry.json")
    parser.add_argument("--rfm", default="registry/math/reconstruction_failure_registry.json")
    parser.add_argument("--objects", default="registry/formal_objects/formal_object_registry.json")
    parser.add_argument("--operators", default="registry/math/operator_registry.json")
    parser.add_argument("--relations", default="registry/math/relation_registry.json")
    
    args = parser.parse_args()
    res = validate_reconstruction(args.rec, args.rfm, args.objects, args.operators, args.relations)
    print(json.dumps(res, indent=2))
