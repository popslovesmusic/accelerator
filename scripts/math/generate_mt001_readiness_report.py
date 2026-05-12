import json
import os
from datetime import datetime

def generate_mt001_readiness_report(readiness_reg):
    try:
        with open(readiness_reg, 'r') as f: readiness_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    report = {
        "mt001_formal_candidate_readiness_report": {
            "timestamp": datetime.now().isoformat(),
            "theorem_id": "MT-001",
            "name": "Projection Idempotence Under Stable Admissibility",
            "readiness_level": readiness_data["readiness_summary"]["readiness_level"],
            "blocker_resolution_status": readiness_data["blocker_status"],
            "criteria_check": readiness_data["readiness_criteria_check"],
            "pending_requirements": readiness_data["pending_requirements"],
            "governance_note": "Theorem status remains 'scaffolded' per current evidence. Elevation to 'formal_candidate' requires formal proof artifact and explicit authorization."
        }
    }
    return report

if __name__ == "__main__":
    readiness_reg = "registry/math/mt001_formal_candidate_readiness_registry.json"
    out_path = "outputs/audits/mt001_formal_candidate_readiness_report.json"
    
    report = generate_mt001_readiness_report(readiness_reg)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"MT-001 readiness report saved to {out_path}")
