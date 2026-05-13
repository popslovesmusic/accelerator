import json
import os
import sys

def validate_campaign():
    registry_path = "registry/math/mt_proof_elevation_campaign_registry.json"
    result_path = "outputs/math_tests/mt_proof_elevation_campaign_result.json"
    
    results_report = {
        "mt_proof_elevation_campaign_validation": {
            "status": "pass",
            "warnings": [],
            "errors": []
        }
    }
    
    if not os.path.exists(registry_path):
        results_report["mt_proof_elevation_campaign_validation"]["status"] = "fail"
        results_report["mt_proof_elevation_campaign_validation"]["errors"].append(f"Registry not found at {registry_path}")
        print(json.dumps(results_report, indent=2))
        sys.exit(0) # Return 0 so caller gets the JSON
        
    if not os.path.exists(result_path):
        results_report["mt_proof_elevation_campaign_validation"]["status"] = "fail"
        results_report["mt_proof_elevation_campaign_validation"]["errors"].append(f"Results not found at {result_path}")
        print(json.dumps(results_report, indent=2))
        sys.exit(0)
        
    try:
        with open(registry_path, "r") as f:
            registry = json.load(f)
            
        with open(result_path, "r") as f:
            results = json.load(f)
    except Exception as e:
        results_report["mt_proof_elevation_campaign_validation"]["status"] = "fail"
        results_report["mt_proof_elevation_campaign_validation"]["errors"].append(f"JSON Load error: {e}")
        print(json.dumps(results_report, indent=2))
        sys.exit(0)
        
    # Validation logic
    campaign = registry["campaigns"][0]
    
    checks = {
        "id_match": campaign["id"] == results["campaign_id"],
        "dependencies_declared": len(campaign["depends_on"]) >= 3,
        "governance_constraints_present": "governance_constraints" in campaign,
        "no_global_closure": campaign["governance_constraints"].get("must_not_claim_global_closure", False),
        "no_physics_claims": campaign["governance_constraints"].get("must_not_claim_physics_validation", False)
    }
    
    for check, passed in checks.items():
        if not passed:
            results_report["mt_proof_elevation_campaign_validation"]["status"] = "fail"
            results_report["mt_proof_elevation_campaign_validation"]["errors"].append(f"Failed check: {check}")
    
    print(json.dumps(results_report, indent=2))

if __name__ == "__main__":
    validate_campaign()
