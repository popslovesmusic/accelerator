import json
import os
import argparse

def trace_theorem(query, mt_reg, po_reg, ce_reg):
    try:
        with open(mt_reg, 'r') as f: mt_data = json.load(f)
        with open(po_reg, 'r') as f: po_data = json.load(f)
        with open(ce_reg, 'r') as f: ce_data = json.load(f)
    except Exception as e:
        return {"error": str(e)}

    trace = {
        "query": query,
        "matching_theorems": [],
        "associated_obligations": [],
        "associated_counterexamples": [],
        "warnings": []
    }

    # Find theorems
    for thm in mt_data.get("theorems", []):
        if query.lower() in thm["theorem_id"].lower() or query.lower() in thm["name"].lower():
            trace["matching_theorems"].append(thm)
            
            # Resolve obligations
            for po_id in thm.get("proof_obligations", []):
                for po in po_data.get("obligations", []):
                    if po["obligation_id"] == po_id:
                        trace["associated_obligations"].append(po)
            
            # Resolve counterexamples
            for ce in ce_data.get("counterexamples", []):
                if ce["theorem_id"] == thm["theorem_id"]:
                    trace["associated_counterexamples"].append(ce)

    if not trace["matching_theorems"]:
        trace["warnings"].append(f"No theorems found for query: {query}")

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace theorem dependencies.")
    parser.add_argument("--query", required=True, help="Theorem ID or name fragment.")
    parser.add_argument("--mt", default="registry/math/minimal_theorem_registry.json")
    parser.add_argument("--po", default="registry/math/proof_obligation_registry.json")
    parser.add_argument("--ce", default="registry/math/counterexample_registry.json")
    
    args = parser.parse_args()
    res = trace_theorem(args.query, args.mt, args.po, args.ce)
    print(json.dumps(res, indent=2))
