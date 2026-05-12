import json
import os
import argparse

def trace_operator_functional_form(query_id, form_reg, symbol_reg):
    try:
        with open(form_reg, 'r') as f: form_data = json.load(f)
        with open(symbol_reg, 'r') as f: symbol_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    # Search by operator or form_id
    entries = [e for e in form_data.get("functional_form_entries", []) if query_id == e.get("operator") or query_id == e.get("primary_candidate")]
    
    if not entries:
        # Search directly in symbolic forms
        forms = [s for s in symbol_data.get("symbolic_forms", []) if query_id == s.get("form_id") or query_id == s.get("operator")]
        if not forms:
            return {"error": f"Functional form data for {query_id} not found."}
    else:
        forms = []
        for entry in entries:
            sform = next((s for s in symbol_data["symbolic_forms"] if s["form_id"] == entry["primary_candidate"]), None)
            if sform:
                forms.append(sform)

    trace = {
        "operator_functional_form_trace": {
            "query_id": query_id,
            "associated_forms": []
        }
    }

    for form in forms:
        trace["operator_functional_form_trace"]["associated_forms"].append({
            "form_id": form["form_id"],
            "operator": form["operator"],
            "expression": form["expression"],
            "description": form["description"],
            "status": form["status"],
            "characteristics": {k: v for k, v in form.items() if k not in ["form_id", "operator", "expression", "description", "status"]}
        })

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace operator functional form dependencies.")
    parser.add_argument("--query", required=True, help="Operator ID or Form ID (e.g., delta or SF-DELTA-001)")
    parser.add_argument("--form", default="registry/math/operator_functional_form_registry.json")
    parser.add_argument("--symbol", default="registry/math/candidate_symbolic_form_registry.json")
    
    args = parser.parse_args()
    res = trace_operator_functional_form(args.query, args.form, args.symbol)
    print(json.dumps(res, indent=2))
