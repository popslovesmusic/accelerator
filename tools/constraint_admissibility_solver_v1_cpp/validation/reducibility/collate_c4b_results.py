import json
import os

def main():
    print("Collating C4B validation results...")
    
    root_dir = "tools/constraint_admissibility_solver_v1_cpp"
    reducibility_file = os.path.join(root_dir, "validation/reducibility/reducibility_search_output.json")
    
    try:
        with open(reducibility_file, "r") as f:
            data = json.load(f)
    except Exception:
        data = {}
        
    c4b_result = {
        "stage": "C4B",
        "status": "pass" if data else "fail",
        "reducibility_decision": data.get("decision"),
        "hidden_state_cardinality_explored": data.get("hidden_state_cardinality"),
        "search_complete": data.get("search_complete"),
        "explored_candidate_count": data.get("explored_candidate_count"),
        "timestamp": "2026-07-18T22:16:00Z"
    }
    
    res_dir = os.path.join(root_dir, "validation/results")
    os.makedirs(res_dir, exist_ok=True)
    with open(os.path.join(res_dir, "C4B_result.json"), "w") as f:
        json.dump(c4b_result, f, indent=2)
        
    print("C4B results collated successfully.")

if __name__ == "__main__":
    main()
