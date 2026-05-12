import json
import os
import argparse

def trace_theory_induction(query_id, tit_reg, stage_reg):
    try:
        with open(tit_reg, 'r') as f: tit_data = json.load(f)
        with open(stage_reg, 'r') as f: stage_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    template = next((t for t in tit_data.get("templates", []) if t["template_id"] == query_id), None)
    if not template:
        return {"error": f"Template {query_id} not found."}

    trace = {
        "theory_induction_trace": {
            "template_id": template["template_id"],
            "name": template["name"],
            "pipeline_trace": []
        }
    }

    for sid in template["pipeline"]:
        stage = next((s for s in stage_data["stages"] if s["stage_id"] == sid), None)
        if stage:
            trace["theory_induction_trace"]["pipeline_trace"].append({
                "stage_id": stage["stage_id"],
                "name": stage["name"],
                "description": stage["description"],
                "inputs": stage["inputs"],
                "outputs": stage["outputs"]
            })

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace Theory Induction pipeline.")
    parser.add_argument("--query", required=True, help="Template ID (e.g., TIT-001)")
    parser.add_argument("--tit", default="registry/math/theory_induction_template_registry.json")
    parser.add_argument("--stages", default="registry/math/induction_stage_registry.json")
    
    args = parser.parse_args()
    res = trace_theory_induction(args.query, args.tit, args.stages)
    print(json.dumps(res, indent=2))
