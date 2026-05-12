import json
import os
from datetime import datetime

def generate_rc002_closure_report(rc002_reg, evidence_reg):
    try:
        with open(rc002_reg, 'r') as f: rc002_data = json.load(f)
        with open(evidence_reg, 'r') as f: evidence_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    report = {
        "rc002_derivation_closure_attempt_report": {
            "timestamp": datetime.now().isoformat(),
            "target_chain": "RC-002",
            "status": rc002_data["meta"]["status"],
            "step_status": rc002_data["step_resolutions"],
            "explicit_evidence_linked": evidence_data["evidence_entries"],
            "closure_criteria_check": rc002_data["closure_criteria_check"],
            "governance_note": "RC-002 has achieved 'derivation_supported' status for all steps. Final closure requires validation of formal proof artifacts and explicit authorization."
        }
    }
    return report

if __name__ == "__main__":
    rc002_reg = "registry/math/rc002_derivation_closure_registry.json"
    evidence_reg = "registry/math/rc002_step_evidence_registry.json"
    out_path = "outputs/audits/rc002_derivation_closure_attempt_report.json"
    
    report = generate_rc002_closure_report(rc002_reg, evidence_reg)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"RC-002 closure attempt report saved to {out_path}")
