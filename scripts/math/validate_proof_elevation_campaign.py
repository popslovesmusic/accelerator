import json
import os
import argparse

def validate_proof_elevation_campaign(campaign_reg, resolution_reg, readiness_reg, theorem_reg, blocker_reg):
    results = {
        "proof_elevation_campaign_validation": {
            "status": "pass",
            "campaign_status": "unknown",
            "resolution_count": 0,
            "readiness_entry_count": 0,
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(campaign_reg, 'r') as f: campaign_data = json.load(f)
        with open(resolution_reg, 'r') as f: resolution_data = json.load(f)
        with open(readiness_reg, 'r') as f: readiness_data = json.load(f)
        with open(theorem_reg, 'r') as f: theorem_data = json.load(f)
        with open(blocker_reg, 'r') as f: blocker_data = json.load(f)
    except Exception as e:
        results["proof_elevation_campaign_validation"]["status"] = "fail"
        results["proof_elevation_campaign_validation"]["errors"].append(f"Load error: {e}")
        return results

    results["proof_elevation_campaign_validation"]["campaign_status"] = campaign_data["campaign"]["status"]
    
    theorem_ids = [t["theorem_id"] for t in theorem_data.get("theorems", [])]
    blocker_ids = [b["id"] for b in blocker_data.get("blockers", [])]
    
    # Validate Resolutions
    for res in resolution_data.get("resolutions", []):
        results["proof_elevation_campaign_validation"]["resolution_count"] += 1
        if res["blocker_id"] not in blocker_ids:
            results["proof_elevation_campaign_validation"]["status"] = "warning"
            results["proof_elevation_campaign_validation"]["warnings"].append(f"Resolution entry references unknown blocker: {res['blocker_id']}")

    # Validate Readiness
    for entry in readiness_data.get("readiness_entries", []):
        results["proof_elevation_campaign_validation"]["readiness_entry_count"] += 1
        if entry["theorem_id"] not in theorem_ids:
             results["proof_elevation_campaign_validation"]["status"] = "warning"
             results["proof_elevation_campaign_validation"]["warnings"].append(f"Readiness entry references unknown theorem: {entry['theorem_id']}")
        
        # Check satisfied blockers
        for bid in entry.get("satisfied_blockers", []):
            if bid not in blocker_ids:
                 results["proof_elevation_campaign_validation"]["status"] = "warning"
                 results["proof_elevation_campaign_validation"]["warnings"].append(f"Readiness entry for {entry['theorem_id']} references unknown satisfied blocker: {bid}")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate Proof Elevation Campaign registries.")
    parser.add_argument("--campaign", default="registry/math/proof_elevation_campaign_registry.json")
    parser.add_argument("--resolution", default="registry/math/theorem_blocker_resolution_registry.json")
    parser.add_argument("--readiness", default="registry/math/formal_candidate_readiness_registry.json")
    parser.add_argument("--theorems", default="registry/math/minimal_theorem_registry.json")
    parser.add_argument("--blockers", default="registry/math/theorem_promotion_blocker_registry.json")
    
    args = parser.parse_args()
    res = validate_proof_elevation_campaign(args.campaign, args.resolution, args.readiness, args.theorems, args.blockers)
    print(json.dumps(res, indent=2))
