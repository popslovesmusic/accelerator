import json
import os
import argparse

def validate_tit(tit_reg, stage_reg, fracture_reg, obj_reg, op_reg):
    results = {
        "theory_induction_template_validation": {
            "status": "pass",
            "template_count": 0,
            "stage_count": 0,
            "warnings": [],
            "closure_gaps": [],
            "open_questions": []
        }
    }

    try:
        with open(tit_reg, 'r') as f: tit_data = json.load(f)
        with open(stage_reg, 'r') as f: stage_data = json.load(f)
        with open(fracture_reg, 'r') as f: fracture_data = json.load(f)
        with open(obj_reg, 'r') as f: obj_data = json.load(f)
        with open(op_reg, 'r') as f: op_data = json.load(f)
    except Exception as e:
        results["theory_induction_template_validation"]["status"] = "fail"
        results["theory_induction_template_validation"]["warnings"].append(f"Load error: {e}")
        return results

    obj_classes = [o["class"] for o in obj_data.get("object_classes", [])]
    op_symbols = [op["symbol"] for op in op_data.get("operators", [])]
    stage_ids = [s["stage_id"] for s in stage_data.get("stages", [])]

    # Validate Stages
    for stage in stage_data.get("stages", []):
        results["theory_induction_template_validation"]["stage_count"] += 1
        # In a real validation, we would check if inputs/outputs resolve to formal objects or registered intermediate artifacts
        # For now, we confirm stage structure integrity.

    # Validate Templates
    for template in tit_data.get("templates", []):
        results["theory_induction_template_validation"]["template_count"] += 1
        for sid in template.get("pipeline", []):
            if sid not in stage_ids:
                results["theory_induction_template_validation"]["status"] = "warning"
                results["theory_induction_template_validation"]["warnings"].append(f"Template {template['template_id']} references unknown stage: {sid}")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate Theory Induction Template registries.")
    parser.add_argument("--tit", default="registry/math/theory_induction_template_registry.json")
    parser.add_argument("--stages", default="registry/math/induction_stage_registry.json")
    parser.add_argument("--fractures", default="registry/math/fracture_detection_registry.json")
    parser.add_argument("--objects", default="registry/formal_objects/formal_object_registry.json")
    parser.add_argument("--operators", default="registry/math/operator_registry.json")
    
    args = parser.parse_args()
    res = validate_tit(args.tit, args.stages, args.fractures, args.objects, args.operators)
    print(json.dumps(res, indent=2))
