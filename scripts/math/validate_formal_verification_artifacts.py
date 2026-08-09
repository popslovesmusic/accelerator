import json
import os
import argparse

def validate_formal_verification_artifacts(artifact_reg, theorem_reg, failure_reg):
    results = {
        "formal_verification_artifact_validation": {
            "status": "pass",
            "artifact_count": 0,
            "checklist_item_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(artifact_reg, 'r') as f: artifact_data = json.load(f)
        with open(theorem_reg, 'r') as f: theorem_data = json.load(f)
        with open(failure_reg, 'r') as f: failure_data = json.load(f)
    except Exception as e:
        results["formal_verification_artifact_validation"]["status"] = "fail"
        results["formal_verification_artifact_validation"]["errors"].append(f"Load error: {e}")
        return results

    theorem_ids = [t["theorem_id"] for t in theorem_data.get("theorems", [])]
    fm_ids = [fm["id"] for fm in failure_data.get("failure_modes", [])]
    
    for artifact in artifact_data.get("artifacts", []):
        results["formal_verification_artifact_validation"]["artifact_count"] += 1
        tid = artifact["theorem_id"]
        
        if tid not in theorem_ids:
            results["formal_verification_artifact_validation"]["status"] = "warning"
            results["formal_verification_artifact_validation"]["warnings"].append(f"Artifact {artifact['artifact_id']} references unknown theorem: {tid}")
        
        checklist_path = artifact.get("checklist_file")
        if checklist_path and not os.path.exists(checklist_path):
            results["formal_verification_artifact_validation"]["status"] = "fail"
            results["formal_verification_artifact_validation"]["errors"].append(f"Checklist file missing: {checklist_path}")
        elif checklist_path:
            try:
                with open(checklist_path, 'r') as cf:
                    c_data = json.load(cf)
                    results["formal_verification_artifact_validation"]["checklist_item_count"] += len(c_data.get("checklist_items", []))
            except Exception as ce:
                results["formal_verification_artifact_validation"]["status"] = "fail"
                results["formal_verification_artifact_validation"]["errors"].append(f"Checklist file parse error {checklist_path}: {ce}")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate formal verification artifacts.")
    parser.add_argument("--artifacts", default="registry/math/formal_verification_artifact_registry.json")
    parser.add_argument("--theorems", default="registry/math/minimal_theorem_registry.json")
    parser.add_argument("--failures", default="registry/math/proof_verification_failure_modes.json")
    
    args = parser.parse_args()
    res = validate_formal_verification_artifacts(args.artifacts, args.theorems, args.failures)
    print(json.dumps(res, indent=2))
