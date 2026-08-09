import json
import os
import argparse

def validate_symbolic_reduction_chains(chain_reg, rule_reg, failure_reg, op_reg, theorem_reg):
    results = {
        "symbolic_reduction_chain_validation": {
            "status": "pass",
            "chain_count": 0,
            "rule_count": 0,
            "failure_mode_count": 0,
            "warnings": [],
            "closure_gaps": [],
            "open_questions": []
        }
    }

    try:
        with open(chain_reg, 'r', encoding='utf-8') as f: chain_data = json.load(f)
        with open(rule_reg, 'r', encoding='utf-8') as f: rule_data = json.load(f)
        with open(failure_reg, 'r', encoding='utf-8') as f: failure_data = json.load(f)
        with open(op_reg, 'r', encoding='utf-8') as f: op_data = json.load(f)
        with open(theorem_reg, 'r', encoding='utf-8') as f: theorem_data = json.load(f)
    except Exception as e:
        results["symbolic_reduction_chain_validation"]["status"] = "fail"
        results["symbolic_reduction_chain_validation"]["warnings"].append(f"Load error: {e}")
        return results

    op_symbols = [op["symbol"] for op in op_data.get("operators", [])]
    op_symbols.extend(["branch_pruning", "orientation_minimization", "observable_projection", "residue_update", "NavT", "Pi_A", "delta"])
    
    theorem_ids = [t["theorem_id"] for t in theorem_data.get("theorems", [])]
    fm_ids = [fm["id"] for fm in failure_data.get("failure_modes", [])]
    rule_ids = [r["rule_id"] for r in rule_data.get("reduction_rules", [])]
    reduction_classes = [rc["class"] for rc in chain_data.get("reduction_classes", [])]

    # Validate Rules
    for rule in rule_data.get("reduction_rules", []):
        results["symbolic_reduction_chain_validation"]["rule_count"] += 1
        if not rule.get("expression"):
             results["symbolic_reduction_chain_validation"]["status"] = "warning"
             results["symbolic_reduction_chain_validation"]["warnings"].append(f"Reduction rule {rule['rule_id']} missing expression.")

    # Validate Reduction Entries
    for entry in chain_data.get("reduction_entries", []):
        results["symbolic_reduction_chain_validation"]["chain_count"] += 1
        
        # Check target (operator composition or theorem)
        target = entry.get("target")
        # Use a more robust check for composition characters
        is_composite = " \u2218 " in target or " o " in target
        
        if not is_composite and target not in op_symbols and target not in theorem_ids:
             results["symbolic_reduction_chain_validation"]["status"] = "warning"
             results["symbolic_reduction_chain_validation"]["warnings"].append(f"Reduction entry {entry['entry_id']} references unknown target: {target}")
        
        # Check expected reduction class
        if entry.get("expected_reduction_class") not in reduction_classes:
             results["symbolic_reduction_chain_validation"]["status"] = "warning"
             results["symbolic_reduction_chain_validation"]["warnings"].append(f"Reduction entry {entry['entry_id']} references unknown class: {entry['expected_reduction_class']}")

        # Check rules applied
        for rid in entry.get("rules_applied", []):
            if rid not in rule_ids:
                results["symbolic_reduction_chain_validation"]["status"] = "warning"
                results["symbolic_reduction_chain_validation"]["warnings"].append(f"Reduction entry {entry['entry_id']} references unknown rule: {rid}")

        # Check failure modes
        for fm in entry.get("failure_modes", []):
            if fm not in fm_ids:
                results["symbolic_reduction_chain_validation"]["status"] = "warning"
                results["symbolic_reduction_chain_validation"]["warnings"].append(f"Reduction entry {entry['entry_id']} references unknown failure mode: {fm}")

    results["symbolic_reduction_chain_validation"]["failure_mode_count"] = len(fm_ids)

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate symbolic reduction-chain registries.")
    parser.add_argument("--chains", default="registry/math/symbolic_reduction_chain_registry.json")
    parser.add_argument("--rules", default="registry/math/reduction_rule_registry.json")
    parser.add_argument("--failures", default="registry/math/reduction_failure_mode_registry.json")
    parser.add_argument("--operators", default="registry/math/operator_registry.json")
    parser.add_argument("--theorems", default="registry/math/minimal_theorem_registry.json")
    
    args = parser.parse_args()
    res = validate_symbolic_reduction_chains(args.chains, args.rules, args.failures, args.operators, args.theorems)
    print(json.dumps(res, indent=2))
