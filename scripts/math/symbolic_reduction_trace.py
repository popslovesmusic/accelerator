import json
import os
import argparse

def trace_symbolic_reduction(query_id, chain_reg, rule_reg):
    try:
        with open(chain_reg, 'r', encoding='utf-8') as f: chain_data = json.load(f)
        with open(rule_reg, 'r', encoding='utf-8') as f: rule_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    # Search in entries (by entry_id, target, or rules_applied)
    entries = [e for e in chain_data.get("reduction_entries", []) if query_id == e.get("entry_id") or query_id == e.get("target") or query_id in e.get("target", "") or query_id in e.get("rules_applied", [])]
    
    if not entries:
        return {"error": f"Symbolic reduction data for {query_id} not found."}

    trace = {
        "symbolic_reduction_trace": {
            "query_id": query_id,
            "associated_entries": []
        }
    }

    for entry in entries:
        entry_trace = {
            "entry_id": entry["entry_id"],
            "target": entry["target"],
            "expected_reduction_class": entry["expected_reduction_class"],
            "rules_applied": [],
            "failure_risks": entry["failure_modes"],
            "proof_status": entry["proof_status"]
        }
        
        for rid in entry["rules_applied"]:
            rule = next((r for r in rule_data["reduction_rules"] if r["rule_id"] == rid), None)
            if rule:
                entry_trace["rules_applied"].append(rule)
            else:
                entry_trace["rules_applied"].append({"rule_id": rid, "status": "unresolved"})
                
        trace["symbolic_reduction_trace"]["associated_entries"].append(entry_trace)

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace symbolic reduction chains.")
    parser.add_argument("--query", required=True, help="Target ID, Rule ID, or Entry ID (e.g., MT-001 or RR-001)")
    parser.add_argument("--chains", default="registry/math/symbolic_reduction_chain_registry.json")
    parser.add_argument("--rules", default="registry/math/reduction_rule_registry.json")
    
    args = parser.parse_args()
    res = trace_symbolic_reduction(args.query, args.chains, args.rules)
    print(json.dumps(res, indent=2))
