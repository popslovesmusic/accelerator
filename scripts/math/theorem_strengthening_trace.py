import json
import os
import argparse

def trace_theorem_strengthening(query_id, strength_reg, blocker_reg):
    try:
        with open(strength_reg, 'r') as f: strength_data = json.load(f)
        with open(blocker_reg, 'r') as f: blocker_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    # Search in entries
    entries = [e for e in strength_data.get("theorem_strengthening_entries", []) if query_id == e.get("theorem_id")]
    
    if not entries:
        return {"error": f"Theorem strengthening data for {query_id} not found."}

    trace = {
        "theorem_strengthening_trace": {
            "query_id": query_id,
            "associated_entries": []
        }
    }

    for entry in entries:
        test_trace = {
            "theorem_id": entry["theorem_id"],
            "current_status": entry["current_status"],
            "evidence_level": entry["current_evidence_level"],
            "supported_obligations": entry["supported_obligations"],
            "active_blockers": []
        }
        
        for bid in entry["active_blockers"]:
            blocker = next((b for b in blocker_data["blockers"] if b["id"] == bid), None)
            if blocker:
                test_trace["active_blockers"].append(blocker)
            else:
                test_trace["active_blockers"].append({"id": bid, "status": "unresolved"})
                
        trace["theorem_strengthening_trace"]["associated_entries"].append(test_trace)

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace theorem proof-strengthening status.")
    parser.add_argument("--query", required=True, help="Theorem ID (e.g., MT-001)")
    parser.add_argument("--strength", default="registry/math/theorem_proof_strengthening_registry.json")
    parser.add_argument("--blockers", default="registry/math/theorem_promotion_blocker_registry.json")
    
    args = parser.parse_args()
    res = trace_theorem_strengthening(args.query, args.strength, args.blockers)
    print(json.dumps(res, indent=2))
