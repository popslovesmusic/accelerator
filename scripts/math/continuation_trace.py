import json
import os
import argparse

def trace_continuation(law_id, law_reg):
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
                    "description": "Fundamental continuation requirement where mismatch exceeds zero."
                },
                {
                    "step": 2,
                    "expression": "Pi_A(candidate, admissibility_window) -> candidate",
                    "description": "Filtering of candidate transitions through the admissibility projection."
                },
                {
                    "step": 3,
                    "expression": "continuation_space = { candidate | Pi_A(candidate, window) == candidate AND residue_constraint satisfied }",
                    "description": "Formalization of the set of legal continuation events."
                },
                {
                    "step": 4,
                    "expression": "continuation_event = delta(continuation_space)",
                    "description": "Selection and realization of a specific update event from the legal space."
                },
                {
                    "step": 5,
                    "expression": "transition_flux = measure(continuation_events)",
                    "description": "Quantification of actualized propagation events."
                }
            ],
            "aspect": law["aspect"],
            "closure_status": law["closure_status"],
            "provisional_status": law["provisional_status"]
        }
    }
    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace continuation law derivation.")
    parser.add_argument("--query", required=True, help="Law ID to trace (e.g., MPF-CV-001)")
    parser.add_argument("--laws", default="registry/math/continuation_law_registry.json")
    
    args = parser.parse_args()
    res = trace_continuation(args.query, args.laws)
    print(json.dumps(res, indent=2))
