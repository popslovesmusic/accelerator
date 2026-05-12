import json
import os
from datetime import datetime

def generate_rc001_closure_report(rc001_reg, evidence_reg):
    try:
        with open(rc001_reg, 'r') as f: rc001_data = json.load(f)
        with open(evidence_reg, 'r') as f: evidence_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    report = {
        "rc001_derivation_closure_attempt_report": {
            "timestamp": datetime.now().isoformat(),
            "target_chain": "RC-001",
            "status": rc001_data["meta"]["status"],
            "step_status": rc001_data["step_resolutions"],
            "explicit_evidence_linked": evidence_data["evidence_entries"],
            "closure_criteria_check": rc001_data["closure_criteria_check"],
            "governance_note": "RC-001 remains in 'strengthening_attempt_in_progress' and cannot be closed due to active blocker GAP-001."
        }
    }
    return report

if __name__ == "__main__":
    rc001_reg = "registry/math/rc001_derivation_closure_registry.json"
    evidence_reg = "registry/math/rc001_step_evidence_registry.json"
    out_path = "outputs/audits/rc001_derivation_closure_attempt_report.json"
    
    report = generate_rc001_closure_report(rc001_reg, evidence_reg)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"RC-001 closure attempt report saved to {out_path}")
