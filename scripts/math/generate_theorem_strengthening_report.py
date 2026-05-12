import json
import os
import argparse
from datetime import datetime

def generate_strengthening_report(strength_reg, ladder_reg, blocker_reg):
    try:
        with open(strength_reg, 'r') as f: strength_data = json.load(f)
        with open(ladder_reg, 'r') as f: ladder_data = json.load(f)
        with open(blocker_reg, 'r') as f: blocker_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    report = {
        "theorem_proof_strengthening_report": {
            "timestamp": datetime.now().isoformat(),
            "status": "readiness_baseline_established",
            "summary": "Governed report for Phase 3 theorem proof-strengthening readiness.",
            "evidence_ladder": ladder_data.get("ladder", []),
            "criteria": strength_data.get("strengthening_criteria", {}),
            "theorem_readiness": []
        }
    }

    for entry in strength_data.get("theorem_strengthening_entries", []):
        ready_entry = {
            "theorem_id": entry["theorem_id"],
            "current_status": entry["current_status"],
            "evidence_level": entry["current_evidence_level"],
            "supported_obligations": entry["supported_obligations"],
            "blockers_total": len(entry["active_blockers"]),
            "blocker_details": []
        }
        
        for bid in entry["active_blockers"]:
            blocker = next((b for b in blocker_data["blockers"] if b["id"] == bid), None)
            if blocker:
                ready_entry["blocker_details"].append(blocker)
                
        report["theorem_proof_strengthening_report"]["theorem_readiness"].append(ready_entry)

    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate theorem proof-strengthening report.")
    parser.add_argument("--strength", default="registry/math/theorem_proof_strengthening_registry.json")
    parser.add_argument("--ladder", default="registry/math/theorem_evidence_ladder_registry.json")
    parser.add_argument("--blockers", default="registry/math/theorem_promotion_blocker_registry.json")
    parser.add_argument("--out", help="Path to save report.")
    
    args = parser.parse_args()
    report = generate_strengthening_report(args.strength, args.ladder, args.blockers)
    
    if args.out:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Strengthening report saved to {args.out}")
    else:
        print(json.dumps(report, indent=2))
