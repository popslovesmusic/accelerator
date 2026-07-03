import json
import os
import argparse

def validate_formal_proof_artifacts(artifact_reg, theorem_reg):
    results = {
        "formal_proof_artifact_validation": {
            "status": "pass",
            "artifact_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(artifact_reg, 'r') as f: artifact_data = json.load(f)
        with open(theorem_reg, 'r') as f: theorem_data = json.load(f)
    except Exception as e:
        results["formal_proof_artifact_validation"]["status"] = "fail"
        results["formal_proof_artifact_validation"]["errors"].append(f"Load error: {e}")
        return results

    theorem_ids = [t["theorem_id"] for t in theorem_data.get("theorems", [])]
    
    for artifact in artifact_data.get("artifacts", []):
        results["formal_proof_artifact_validation"]["artifact_count"] += 1
        tid = artifact["theorem_id"]
        
        # Check theorem reference
        if tid not in theorem_ids:
            results["formal_proof_artifact_validation"]["status"] = "warning"
            results["formal_proof_artifact_validation"]["warnings"].append(f"Artifact {artifact['artifact_id']} references unknown theorem: {tid}")
        
        # Check files existence
        proof_path = artifact.get("proof_file")
        if proof_path and not os.path.exists(proof_path):
            results["formal_proof_artifact_validation"]["status"] = "fail"
            results["formal_proof_artifact_validation"]["errors"].append(f"Proof file missing: {proof_path}")
            
        verify_path = artifact.get("verification_file")
        if verify_path and not os.path.exists(verify_path):
            results["formal_proof_artifact_validation"]["status"] = "fail"
            results["formal_proof_artifact_validation"]["errors"].append(f"Verification file missing: {verify_path}")
        elif verify_path:
            # Check verification content
            try:
                with open(verify_path, 'r') as vf:
                    v_data = json.load(vf)
                    if v_data.get("formal_verification", {}).get("must_not_promote"):
                         results["formal_proof_artifact_validation"]["status"] = "fail"
                         results["formal_proof_artifact_validation"]["errors"].append(f"Artifact {tid} still has an active must_not_promote mandate.")
            except Exception as ve:
                results["formal_proof_artifact_validation"]["status"] = "fail"
                results["formal_proof_artifact_validation"]["errors"].append(f"Verification file parse error {verify_path}: {ve}")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate formal proof artifacts.")
    parser.add_argument("--artifacts", default="registry/math/formal_proof_artifact_registry.json")
    parser.add_argument("--theorems", default="registry/math/minimal_theorem_registry.json")
    
    args = parser.parse_args()
    res = validate_formal_proof_artifacts(args.artifacts, args.theorems)
    print(json.dumps(res, indent=2))
