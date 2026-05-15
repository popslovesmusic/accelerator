import json
import os
from datetime import datetime

def run_firewall():
    """
    Runner for the Recursive Inheritance Firewall.
    Scan dependencies and classify their inheritance admissibility.
    """
    rc_exec_path = "validation/results/rc_repair_queue_execution_result.json"
    impact_audit_path = "validation/results/mpf_sim_013_constraint_geology_proof_impact_result.json"
    result_path = "validation/results/recursive_inheritance_firewall_result.json"
    
    report = {
        "firewall_id": "RIF-SUM-001",
        "timestamp": datetime.now().isoformat(),
        "status": "pass",
        "inheritance_audits": [],
        "governance": {
            "theorem_status": "NOT_PROVEN",
            "scope_status": "STRICTLY_LOCAL_RESTRICTED_DOMAIN",
            "physics_status": "NON_PHYSICAL_ANALOG_MODEL"
        }
    }

    # 1. Audit RC dependencies
    if os.path.exists(rc_exec_path):
        with open(rc_exec_path, 'r', encoding='utf-8') as f:
            rc_data = json.load(f)
            for entry in rc_data["repair_entries"]:
                audit = {
                    "source_id": entry["rc_id"],
                    "source_type": "RC_CAMPAIGN",
                    "initial_class": entry["initial_closure_class"],
                    "inheritance_class": "INHERITANCE-BLOCKED"
                }
                
                # Rule: Symbolic/Partial/Blocked are blocked
                if entry["initial_closure_class"] in ["RC-SYMBOLIC", "RC-PARTIAL", "RC-BLOCKED"]:
                    audit["inheritance_class"] = "INHERITANCE-BLOCKED"
                else:
                    audit["inheritance_class"] = "INHERITANCE-ALLOWED"
                
                report["inheritance_audits"].append(audit)

    # 2. Audit Simulation/Geology dependencies
    if os.path.exists(impact_audit_path):
        with open(impact_audit_path, 'r', encoding='utf-8') as f:
            impact_data = json.load(f)
            for entry in impact_data["audit_results"]:
                audit = {
                    "source_id": entry["geology_entry_id"],
                    "source_type": "GEOLOGY_IMPACT",
                    "initial_class": entry["impact_class"],
                    "inheritance_class": "INHERITANCE-BLOCKED"
                }
                
                if entry["impact_class"] == "CG-IMPACT-SUPPORTIVE":
                    audit["inheritance_class"] = "INHERITANCE-ALLOWED"
                elif entry["impact_class"] == "CG-IMPACT-CONDITIONAL":
                    audit["inheritance_class"] = "INHERITANCE-CONDITIONAL"
                
                report["inheritance_audits"].append(audit)

    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"Recursive inheritance firewall report emitted to {result_path}")
    return report

if __name__ == "__main__":
    run_firewall()
