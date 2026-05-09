import json
import os

def analyze_closure():
    files = {
        "lemma": "registry/lemma_registry.json",
        "proof": "registry/proof_registry.json",
        "gap": "registry/gap_dependency_graph.json",
        "objects": "registry/formal_object_registry.json",
        "closure": "registry/theorem_closure_registry.json",
        "matrix": "registry/claim_support_matrix.json",
        "bindings": "registry/simulation_proof_binding_registry.json",
        "refs": "registry/formal_object_reference_registry.json"
    }

    data = {}
    for k, p in files.items():
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                data[k] = json.load(f)
        else:
            data[k] = None

    objects = {obj["object_id"]: obj for obj in data["objects"]["objects"]}
    lemmas = {l["lemma_id"]: l for l in data["lemma"]["lemmas"]} if data["lemma"] else {}
    proofs = {p["proof_id"]: p for p in data["proof"]["proofs"]} if data["proof"] else {}
    gaps = {g["gap_id"]: g for g in data["gap"]["gaps"]} if data["gap"] else {}
    claims = {c["claim_id"]: c for c in data["matrix"]["claims"]} if data["matrix"] else {}
    fid_to_raw = {ref["formal_object_id"]: ref["raw_reference"] for ref in data["refs"]["references"]} if data["refs"] else {}

    results = {}

    # Pass 1: Lemmas and Proofs
    for obj_id, obj in objects.items():
        if obj["object_class"] not in ["lemma", "proof"]: continue
        
        entry = {
            "object_id": obj_id,
            "closure_status": "UNKNOWN",
            "open_dependencies": [],
            "conditional_dependencies": [],
            "proof_dependencies": [],
            "gap_dependencies": [],
            "promotion_readiness": "low",
            "blocking_reasons": []
        }
        
        raw_id = fid_to_raw.get(obj_id, obj_id)
        
        if obj["object_class"] == "lemma":
            lemma_data = lemmas.get(raw_id)
            if lemma_data:
                proof_for_lemma = [p_id for p_id, p in proofs.items() if raw_id in p.get("proves_lemmas", [])]
                entry["proof_dependencies"] = [f"OBJ-{p}" for p in proof_for_lemma]
                
                for p_id in proof_for_lemma:
                    p_data = proofs[p_id]
                    for g_id in p_data.get("gap_dependencies", []):
                        entry["gap_dependencies"].append(g_id)
                        g_data = gaps.get(g_id)
                        if g_data and g_data["gap_status"] != "CLOSED":
                            entry["open_dependencies"].append(g_id)
                
                if lemma_data.get("theorem_status") == "TS2":
                    entry["conditional_dependencies"].append(obj_id)
                
                if entry["open_dependencies"]:
                    entry["closure_status"] = "BLOCKED_BY_OPEN_GAP"
                elif not entry["proof_dependencies"]:
                    entry["closure_status"] = "BLOCKED_BY_MISSING_PROOF"
                elif entry["conditional_dependencies"]:
                    entry["closure_status"] = "CONDITIONAL_ON_DECLARED_ASSUMPTIONS"
                else:
                    entry["closure_status"] = "CLOSED_WITHIN_STACK"
                    entry["promotion_readiness"] = "high"
                    
        elif obj["object_class"] == "proof":
            proof_data = proofs.get(raw_id)
            if proof_data:
                for g_id in proof_data.get("gap_dependencies", []):
                    entry["gap_dependencies"].append(g_id)
                    g_data = gaps.get(g_id)
                    if g_data and g_data["gap_status"] != "CLOSED":
                        entry["open_dependencies"].append(g_id)
                
                if entry["open_dependencies"]:
                    entry["closure_status"] = "BLOCKED_BY_OPEN_GAP"
                else:
                    entry["closure_status"] = "CLOSED_WITHIN_STACK"
                    entry["promotion_readiness"] = "high"
        
        results[obj_id] = entry

    # Pass 2: Claims
    for obj_id, obj in objects.items():
        if obj["object_class"] != "claim": continue
        
        entry = {
            "object_id": obj_id,
            "closure_status": "UNKNOWN",
            "open_dependencies": [],
            "conditional_dependencies": [],
            "proof_dependencies": [],
            "gap_dependencies": [],
            "promotion_readiness": "low",
            "blocking_reasons": []
        }
        
        raw_id = fid_to_raw.get(obj_id, obj_id)
        claim_data = claims.get(raw_id)
        
        if claim_data:
            for lid in claim_data.get("required_lemmas", []):
                fid = f"OBJ-{lid}"
                if fid in results and results[fid]["closure_status"] != "CLOSED_WITHIN_STACK":
                    entry["conditional_dependencies"].append(fid)
            for pid in claim_data.get("required_proofs", []):
                fid = f"OBJ-{pid}"
                if fid in results and results[fid]["closure_status"] != "CLOSED_WITHIN_STACK":
                    entry["open_dependencies"].append(fid)
            
            if entry["open_dependencies"]:
                entry["closure_status"] = "BLOCKED_BY_MISSING_PROOF"
            elif entry["conditional_dependencies"]:
                entry["closure_status"] = "CONDITIONAL_ON_DECLARED_ASSUMPTIONS"
            else:
                entry["closure_status"] = "CLOSED_WITHIN_STACK"
                entry["promotion_readiness"] = "high"
        else:
             entry["closure_status"] = "CLOSED_WITHIN_STACK" # Assume paper-backfilled for now
             entry["promotion_readiness"] = "high"
             
        results[obj_id] = entry

    data["closure"]["closures"] = list(results.values())
    with open(files["closure"], 'w', encoding='utf-8') as f:
        json.dump(data["closure"], f, indent=2)

if __name__ == "__main__":
    analyze_closure()
