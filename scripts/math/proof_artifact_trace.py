import json
import os
import argparse

def trace_proof_artifact(query_id, artifact_reg):
    try:
        with open(artifact_reg, 'r') as f: artifact_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    # Search by entry_id or theorem_id
    entries = [e for e in artifact_data.get("artifacts", []) if query_id == e.get("artifact_id") or query_id == e.get("theorem_id")]
    
    if not entries:
        return {"error": f"Proof artifact data for {query_id} not found."}

    trace = {
        "proof_artifact_trace": {
            "query_id": query_id,
            "associated_artifacts": []
        }
    }

    for entry in entries:
        artifact_trace = {
            "artifact_id": entry["artifact_id"],
            "theorem_id": entry["theorem_id"],
            "evidence_level": entry["evidence_level"],
            "status": entry["status"],
            "files": {
                "proof_prose": entry["proof_file"],
                "formal_verification": entry["verification_file"]
            }
        }
        
        # Add metadata from verification file if possible
        v_path = entry.get("verification_file")
        if v_path and os.path.exists(v_path):
            with open(v_path, 'r') as vf:
                v_data = json.load(vf)
                artifact_trace["verification_summary"] = v_data.get("formal_verification", {})

        trace["proof_artifact_trace"]["associated_artifacts"].append(artifact_trace)

    return trace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trace formal proof artifacts.")
    parser.add_argument("--query", required=True, help="Artifact ID or Theorem ID (e.g. MT-001 or PA-MT001-001)")
    parser.add_argument("--artifacts", default="registry/math/formal_proof_artifact_registry.json")
    
    args = parser.parse_args()
    res = trace_proof_artifact(args.query, args.artifacts)
    print(json.dumps(res, indent=2))
