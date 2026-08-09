import json
import os
import argparse
from datetime import datetime

def generate_proof_elevation_report(campaign_reg, resolution_reg, readiness_reg, blocker_reg):
    try:
        with open(campaign_reg, 'r') as f: campaign_data = json.load(f)
        with open(resolution_reg, 'r') as f: resolution_data = json.load(f)
        with open(readiness_reg, 'r') as f: readiness_data = json.load(f)
        with open(blocker_reg, 'r') as f: blocker_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    report = {
        "proof_elevation_campaign_report": {
            "timestamp": datetime.now().isoformat(),
            "campaign_id": campaign_data["campaign"]["campaign_id"],
            "status": campaign_data["campaign"]["status"],
            "summary": "Governed report for PROOF-ELEVATION-CAMPAIGN-001.",
            "blocker_resolutions": resolution_data.get("resolutions", []),
            "theorem_readiness": []
        }
    }

    for entry in readiness_data.get("readiness_entries", []):
        ready_entry = {
            "theorem_id": entry["theorem_id"],
            "readiness_status": entry["readiness_status"],
            "satisfied_blockers": entry["satisfied_blockers"],
            "pending_proof_obligations": entry["pending_proof_obligations"],
            "readiness_notes": entry["readiness_notes"]
        }
        report["proof_elevation_campaign_report"]["theorem_readiness"].append(ready_entry)

    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate proof elevation campaign report.")
    parser.add_argument("--campaign", default="registry/math/proof_elevation_campaign_registry.json")
    parser.add_argument("--resolution", default="registry/math/theorem_blocker_resolution_registry.json")
    parser.add_argument("--readiness", default="registry/math/formal_candidate_readiness_registry.json")
    parser.add_argument("--blockers", default="registry/math/theorem_promotion_blocker_registry.json")
    parser.add_argument("--out", help="Path to save campaign report.")
    
    args = parser.parse_args()
    report = generate_proof_elevation_report(args.campaign, args.resolution, args.readiness, args.blockers)
    
    if args.out:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Proof elevation report saved to {args.out}")
    else:
        print(json.dumps(report, indent=2))
