import json
import os
import argparse

def trace_formal_verification(query_id, artifact_reg):
    try:
        with open(artifact_reg, 'r') as f: artifact_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    # Search by entry_id or theorem_id
    entries = [e for e in artifact_data.get("artifacts", []) if query_id == e.get("artifact_id") or query_id == e.get("theorem_id")]
    
    if not entries:
        return {"error": f"Verification artifact data for {query_id} not found."}

    trace = {
        "formal_verification_trace": {
            "query_id": query_id,
            "associated_artifacts": []
        }
    }

    for entry in entries:
        artifact_trace = {
            "artifact_id": entry["artifact_id"],
            "theorem_id": entry["theorem_id"],
            "status": entry["status"],
            "checklist_file": entry["checklist_file"],
            "checklist_items": []
        }
        
        # Add metadata from checklist file if possible
        c_path = entry.get("checklist_file")
        if c_path and os.path.exists(c_path):
            with open(c_path, 'r') as cf:
                c_data = json.load(cf)
                artifact_trace["checklist_items"] = c_data.get("checklist_items", [])

        trace["formal_verification_trace"]["associated_artifacts"].append(artifact_trace)

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace formal verification artifacts.")
    parser.add_argument("--query", required=True, help="Artifact ID or Theorem ID (e.g. MT-001 or VA-MT001-001)")
    parser.add_argument("--artifacts", default="registry/math/formal_verification_artifact_registry.json")
    
    args = parser.parse_args()
    res = trace_formal_verification(args.query, args.artifacts)
    print(json.dumps(res, indent=2))
