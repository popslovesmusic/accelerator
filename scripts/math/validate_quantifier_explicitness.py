import json
import os
import argparse

def validate_quantifier_explicitness(scope_reg, quant_reg, failure_reg, theorem_reg):
    results = {
        "quantifier_explicitness_validation": {
            "status": "pass",
            "scope_count": 0,
            "quantifier_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(scope_reg, 'r') as f: scope_data = json.load(f)
        with open(quant_reg, 'r') as f: quant_data = json.load(f)
        with open(failure_reg, 'r') as f: failure_data = json.load(f)
        with open(theorem_reg, 'r') as f: theorem_data = json.load(f)
    except Exception as e:
        results["quantifier_explicitness_validation"]["status"] = "fail"
        results["quantifier_explicitness_validation"]["errors"].append(f"Load error: {e}")
        return results

    scope_classes = [c["class"] for c in scope_data.get("scope_classes", [])]
    fm_ids = [fm["id"] for fm in failure_data.get("failure_modes", [])]
    theorem_ids = [t["theorem_id"] for t in theorem_data.get("theorems", [])]

    results["quantifier_explicitness_validation"]["scope_count"] = len(scope_classes)
    results["quantifier_explicitness_validation"]["failure_mode_count"] = len(fm_ids)

    # Validate Quantifier Entries
    for entry in quant_data.get("quantifier_entries", []):
        results["quantifier_explicitness_validation"]["quantifier_count"] += 1
        
        # Check theorem_id
        tid = entry.get("theorem_id")
        if tid not in theorem_ids:
             results["quantifier_explicitness_validation"]["status"] = "warning"
             results["quantifier_explicitness_validation"]["warnings"].append(f"Quantifier entry {entry['entry_id']} references unknown theorem: {tid}")
        
        # Check scope_type
        scope = entry.get("scope_type")
        if scope not in scope_classes:
             results["quantifier_explicitness_validation"]["status"] = "warning"
             results["quantifier_explicitness_validation"]["warnings"].append(f"Quantifier entry {entry['entry_id']} has unknown scope type: {scope}")

        # Check failure modes
        for fm in entry.get("failure_modes", []):
            if fm not in fm_ids:
                results["quantifier_explicitness_validation"]["status"] = "warning"
                results["quantifier_explicitness_validation"]["warnings"].append(f"Quantifier entry {entry['entry_id']} references unknown failure mode: {fm}")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate theorem quantifier scopes and bounds.")
    parser.add_argument("--scope", default="registry/math/quantifier_scope_registry.json")
    parser.add_argument("--quant", default="registry/math/theorem_quantifier_registry.json")
    parser.add_argument("--failures", default="registry/math/quantifier_failure_mode_registry.json")
    parser.add_argument("--theorems", default="registry/math/minimal_theorem_registry.json")
    
    args = parser.parse_args()
    res = validate_quantifier_explicitness(args.scope, args.quant, args.failures, args.theorems)
    print(json.dumps(res, indent=2))
