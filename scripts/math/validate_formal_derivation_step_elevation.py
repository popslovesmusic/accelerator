import json
import os
import argparse

def validate_formal_derivation_step_elevation(elevation_reg, readiness_reg, failure_reg):
    results = {
        "formal_derivation_step_elevation_validation": {
            "status": "pass",
            "target_count": 0,
            "step_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(elevation_reg, 'r') as f: elevation_data = json.load(f)
        with open(readiness_reg, 'r') as f: readiness_data = json.load(f)
        with open(failure_reg, 'r') as f: failure_data = json.load(f)
    except Exception as e:
        results["formal_derivation_step_elevation_validation"]["status"] = "fail"
        results["formal_derivation_step_elevation_validation"]["errors"].append(f"Load error: {e}")
        return results

    required_criteria = [c["requirement"] for c in readiness_data.get("readiness_criteria", [])]
    
    # Validate Elevation Entries
    for entry in elevation_data.get("elevation_entries", []):
        results["formal_derivation_step_elevation_validation"]["target_count"] += 1
        for step in entry.get("steps", []):
            results["formal_derivation_step_elevation_validation"]["step_count"] += 1
            
            # Check requirements
            satisfied = step.get("requirements_satisfied", [])
            open_reqs = step.get("open_requirements", [])
            
            for req in satisfied:
                if req not in required_criteria:
                     results["formal_derivation_step_elevation_validation"]["status"] = "warning"
                     results["formal_derivation_step_elevation_validation"]["warnings"].append(f"Target {entry['target_id']} step {step['step_id']} references unknown requirement: {req}")
            
            # Mandate: no theorem promotion occurs must be implicitly or explicitly satisfied
            # (In this validator, we check if it's listed in requirements_satisfied or if it's an open_requirement)
            # Actually, the requirement is "no theorem promotion occurs".
            
            # Check for overreach: proof_candidate or formalized target_status requires all requirements satisfied
            if step.get("target_status") in ["proof_candidate", "formalized"]:
                missing = [r for r in required_criteria if r not in satisfied]
                if missing:
                    results["formal_derivation_step_elevation_validation"]["status"] = "fail"
                    results["formal_derivation_step_elevation_validation"]["errors"].append(f"Target {entry['target_id']} step {step['step_id']} marked for {step['target_status']} but missing requirements: {missing}")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate formal derivation step elevation.")
    parser.add_argument("--elevation", default="registry/math/formal_derivation_step_elevation_registry.json")
    parser.add_argument("--readiness", default="registry/math/derivation_step_readiness_registry.json")
    parser.add_argument("--failures", default="registry/math/derivation_step_elevation_failure_modes.json")
    
    args = parser.parse_args()
    res = validate_formal_derivation_step_elevation(args.elevation, args.readiness, args.failures)
    print(json.dumps(res, indent=2))
