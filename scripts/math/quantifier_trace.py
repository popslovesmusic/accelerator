import json
import os
import argparse

def trace_quantifier(query_id, quant_reg, scope_reg):
    try:
        with open(quant_reg, 'r') as f: quant_data = json.load(f)
        with open(scope_reg, 'r') as f: scope_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    # Search by entry_id or theorem_id
    entries = [e for e in quant_data.get("quantifier_entries", []) if e["entry_id"] == query_id or e["theorem_id"] == query_id]
    
    if not entries:
        return {"error": f"Quantifier data for {query_id} not found."}

    trace = {
        "quantifier_trace": {
            "query_id": query_id,
            "associated_entries": []
        }
    }

    for entry in entries:
        scope = next((s for s in scope_data["scope_classes"] if s["class"] == entry["scope_type"]), {"meaning": "unknown"})
        
        trace["quantifier_trace"]["associated_entries"].append({
            "entry_id": entry["entry_id"],
            "theorem_id": entry["theorem_id"],
            "statement_target": entry["statement_target"],
            "required_quantifier": entry["required_quantifier"],
            "scope_type": entry["scope_type"],
            "scope_meaning": scope["meaning"],
            "definitions": entry["definitions"],
            "failure_risks": entry["failure_modes"],
            "proof_status": entry["proof_status"]
        })

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace theorem quantifier bounds.")
    parser.add_argument("--query", required=True, help="Entry ID or Theorem ID (e.g., TQ-001 or MT-001)")
    parser.add_argument("--quant", default="registry/math/theorem_quantifier_registry.json")
    parser.add_argument("--scope", default="registry/math/quantifier_scope_registry.json")
    
    args = parser.parse_args()
    res = trace_quantifier(args.query, args.quant, args.scope)
    print(json.dumps(res, indent=2))
