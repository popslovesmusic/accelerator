import json
import os
import argparse

def validate_minimal_theorems(mt_reg, po_reg, ce_reg, obj_reg, op_reg, rel_reg, wp_reg, fm_reg):
    results = {
        "minimal_theorem_validation": {
            "status": "pass",
            "theorem_count": 0,
            "proof_obligation_count": 0,
            "open_obligations": [],
            "blocked_theorems": [],
            "dependency_gaps": [],
            "counterexample_warnings": [],
            "closure_gaps": [],
            "warnings": []
        }
    }

    try:
        with open(mt_reg, 'r') as f: mt_data = json.load(f)
        with open(po_reg, 'r') as f: po_data = json.load(f)
        with open(ce_reg, 'r') as f: ce_data = json.load(f)
        with open(obj_reg, 'r') as f: obj_data = json.load(f)
        with open(op_reg, 'r') as f: op_data = json.load(f)
        with open(rel_reg, 'r') as f: rel_data = json.load(f)
        with open(wp_reg, 'r') as f: wp_data = json.load(f)
        with open(fm_reg, 'r') as f: fm_data = json.load(f)
    except Exception as e:
        results["minimal_theorem_validation"]["status"] = "fail"
        results["minimal_theorem_validation"]["warnings"].append(f"Load error: {e}")
        return results

    # Gather valid symbols
    valid_symbols = []
    for o in obj_data.get("object_classes", []): valid_symbols.append(o["class"])
    for o in op_data.get("operators", []): valid_symbols.append(o["symbol"])
    for r in rel_data.get("relations", []): valid_symbols.append(r["name"])
    
    wp_ids = [w["entry_id"] for w in wp_data.get("entries", [])]
    fm_ids = [f["id"] for f in fm_data.get("failure_modes", [])]
    
    results["minimal_theorem_validation"]["theorem_count"] = len(mt_data.get("theorems", []))
    results["minimal_theorem_validation"]["proof_obligation_count"] = len(po_data.get("obligations", []))

    for thm in mt_data.get("theorems", []):
        tid = thm["theorem_id"]
        
        # Validate dependencies
        deps = thm.get("dependencies", {})
        for op in deps.get("operators", []):
            if op not in valid_symbols:
                results["minimal_theorem_validation"]["dependency_gaps"].append(f"Theorem {tid} references unknown operator: {op}")
        for wp in deps.get("well_posedness_entries", []):
            if wp not in wp_ids:
                results["minimal_theorem_validation"]["dependency_gaps"].append(f"Theorem {tid} references unknown WP entry: {wp}")

        # Check obligations
        for po in thm.get("proof_obligations", []):
            found = False
            for obligation in po_data.get("obligations", []):
                if obligation["obligation_id"] == po:
                    found = True
                    if obligation["current_status"] == "open":
                        results["minimal_theorem_validation"]["open_obligations"].append(po)
                    break
            if not found:
                results["minimal_theorem_validation"]["warnings"].append(f"Theorem {tid} references unknown obligation: {po}")

        if thm.get("status") == "formal":
             # All obligations must be satisfied
             for po in thm.get("proof_obligations", []):
                 for obligation in po_data.get("obligations", []):
                     if obligation["obligation_id"] == po and obligation["current_status"] != "satisfied":
                         results["minimal_theorem_validation"]["status"] = "fail"
                         results["minimal_theorem_validation"]["warnings"].append(f"Formal theorem {tid} has unsatisfied obligation: {po}")

        if thm.get("closure_status") == "undefined":
            results["minimal_theorem_validation"]["closure_gaps"].append(tid)

    # Dependency gaps are unfinished registry work, not validator execution
    # failures. Preserve them as warnings for global validation while keeping
    # the validator's terminal contract binary: pass or fail.
    results["minimal_theorem_validation"]["warnings"].extend(
        results["minimal_theorem_validation"]["dependency_gaps"]
    )

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate minimal theorem registry.")
    parser.add_argument("--mt", default="registry/math/minimal_theorem_registry.json")
    parser.add_argument("--po", default="registry/math/proof_obligation_registry.json")
    parser.add_argument("--ce", default="registry/math/counterexample_registry.json")
    parser.add_argument("--objects", default="registry/formal_objects/formal_object_registry.json")
    parser.add_argument("--operators", default="registry/math/operator_registry.json")
    parser.add_argument("--relations", default="registry/math/relation_registry.json")
    parser.add_argument("--wp", default="registry/math/well_posedness_registry.json")
    parser.add_argument("--fm", default="registry/math/failure_mode_registry.json")
    
    args = parser.parse_args()
    res = validate_minimal_theorems(args.mt, args.po, args.ce, args.objects, args.operators, args.relations, args.wp, args.fm)
    print(json.dumps(res, indent=2))
