import json
import os
import argparse

def trace_boundary_case(query_id, binding_reg, boundary_reg):
    try:
        with open(binding_reg, 'r') as f: binding_data = json.load(f)
        with open(boundary_reg, 'r') as f: boundary_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    # Search in theorem bindings
    entries = [e for e in binding_data.get("theorem_bindings", []) if query_id == e["theorem_id"]]
    
    if not entries:
        # Search by boundary class name
        entries = []
        for binding in binding_data.get("theorem_bindings", []):
            matching_cases = [c for c in binding.get("boundary_cases", []) if query_id == c["case"]]
            if matching_cases:
                entries.append({
                    "theorem_id": binding["theorem_id"],
                    "boundary_cases": matching_cases
                })

    if not entries:
        return {"error": f"Boundary case data for {query_id} not found."}

    trace = {
        "boundary_case_trace": {
            "query_id": query_id,
            "associated_entries": []
        }
    }

    for entry in entries:
        test_trace = {
            "theorem_id": entry["theorem_id"],
            "boundary_cases": []
        }
        
        for case_ref in entry["boundary_cases"]:
            case_detail = next((c for c in boundary_data["boundary_case_classes"] if c["class"] == case_ref["case"]), {"meaning": "unknown"})
            test_trace["boundary_cases"].append({
                "case": case_ref["case"],
                "meaning": case_detail["meaning"],
                "status": case_ref["status"],
                "details": case_ref.get("details", "")
            })
                
        trace["boundary_case_trace"]["associated_entries"].append(test_trace)

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace boundary-case dependencies.")
    parser.add_argument("--query", required=True, help="Theorem ID or Boundary Class Name (e.g., MT-001 or residue_drift)")
    parser.add_argument("--binding", default="registry/math/theorem_boundary_condition_registry.json")
    parser.add_argument("--boundary", default="registry/math/boundary_case_registry.json")
    
    args = parser.parse_args()
    res = trace_boundary_case(args.query, args.binding, args.boundary)
    print(json.dumps(res, indent=2))
