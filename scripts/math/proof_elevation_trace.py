import json
import os
import argparse

def trace_proof_elevation(query_id, readiness_reg, resolution_reg, blocker_reg):
    try:
        with open(readiness_reg, 'r') as f: readiness_data = json.load(f)
        with open(resolution_reg, 'r') as f: resolution_data = json.load(f)
        with open(blocker_reg, 'r') as f: blocker_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    # Search in readiness entries
    entries = [e for e in readiness_data.get("readiness_entries", []) if query_id == e.get("theorem_id")]
    
    if not entries:
        return {"error": f"Proof elevation readiness data for {query_id} not found."}

    trace = {
        "proof_elevation_trace": {
            "query_id": query_id,
            "readiness_status": "",
            "satisfied_blockers": [],
            "pending_proof_obligations": [],
            "blocker_resolution_details": []
        }
    }

    for entry in entries:
        trace["proof_elevation_trace"]["readiness_status"] = entry["readiness_status"]
        trace["proof_elevation_trace"]["satisfied_blockers"] = entry["satisfied_blockers"]
        trace["proof_elevation_trace"]["pending_proof_obligations"] = entry["pending_proof_obligations"]
        
        for bid in entry["satisfied_blockers"]:
            res = next((r for r in resolution_data["resolutions"] if r["blocker_id"] == bid), None)
            if res:
                trace["proof_elevation_trace"]["blocker_resolution_details"].append(res)
            else:
                trace["proof_elevation_trace"]["blocker_resolution_details"].append({"blocker_id": bid, "status": "resolved_locally_only"})

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace proof elevation readiness and resolution status.")
    parser.add_argument("--query", required=True, help="Theorem ID (e.g., MT-001)")
    parser.add_argument("--readiness", default="registry/math/formal_candidate_readiness_registry.json")
    parser.add_argument("--resolution", default="registry/math/theorem_blocker_resolution_registry.json")
    parser.add_argument("--blockers", default="registry/math/theorem_promotion_blocker_registry.json")
    
    args = parser.parse_args()
    res = trace_proof_elevation(args.query, args.readiness, args.resolution, args.blockers)
    print(json.dumps(res, indent=2))
