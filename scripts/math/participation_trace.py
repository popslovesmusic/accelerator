import json
import os
import argparse

def trace_participation(law_id, law_reg):
    try:
        with open(law_reg, 'r') as f: law_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    law = next((l for l in law_data.get("laws", []) if l["law_id"] == law_id), None)
    if not law:
        return {"error": f"Law {law_id} not found in {law_reg}"}

    trace = {
        "trace": {
            "law_id": law["law_id"],
            "source_expression": law["source_expression"],
            "derivation_steps": [
                {
                    "step": 1,
                    "expression": law["source_expression"],
                    "description": "Fundamental non-null mismatch condition."
                },
                {
                    "step": 2,
                    "expression": "alpha | E_alpha != 0",
                    "description": "Identification of loci satisfying the non-null condition."
                },
                {
                    "step": 3,
                    "expression": "participation_space",
                    "description": "Formalization of the set of participating loci."
                },
                {
                    "step": 4,
                    "expression": "participation_density = measure(participation_space) / measure(domain)",
                    "description": "Quantification of participation within the addressable domain."
                }
            ],
            "aspect": law["aspect"],
            "closure_status": law["closure_status"],
            "provisional_status": law["provisional_status"]
        }
    }
    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace participation law derivation.")
    parser.add_argument("--query", required=True, help="Law ID to trace (e.g., MPF-PV-001)")
    parser.add_argument("--laws", default="registry/math/participation_law_registry.json")
    
    args = parser.parse_args()
    res = trace_participation(args.query, args.laws)
    print(json.dumps(res, indent=2))
