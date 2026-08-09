import json
import os
from datetime import datetime

def run_admission_gate():
    """
    Runner for the Recursive Dependency Admission Gate.
    Evaluate dependencies from the inheritance firewall and assign admission classes.
    """
    firewall_report_path = "validation/results/recursive_inheritance_firewall_result.json"
    result_path = "validation/results/recursive_dependency_admission_gate_result.json"
    
    if not os.path.exists(firewall_report_path):
        return {"status": "fail", "reason": "firewall report missing"}

    with open(firewall_report_path, 'r', encoding='utf-8') as f:
        firewall_data = json.load(f)

    report = {
        "gate_id": "RDAG-SUM-001",
        "timestamp": datetime.now().isoformat(),
        "status": "pass",
        "admission_entries": [],
        "governance": {
            "theorem_status": "NOT_PROVEN",
            "scope_status": "STRICTLY_LOCAL_RESTRICTED_DOMAIN",
            "physics_status": "NON_PHYSICAL_ANALOG_MODEL"
        }
    }

    # Admission Logic based on Firewall Inheritance Class
    for audit in firewall_data["inheritance_audits"]:
        entry = {
            "dependency_id": audit["source_id"],
            "source_family": audit["source_type"].split("_")[0],
            "inheritance_class": audit["inheritance_class"],
            "admission_class": "ADMISSION-DENIED",
            "allowed_targets": [],
            "required_constraints": [],
            "proof_eligibility_effect": "blocked"
        }
        
        if audit["inheritance_class"] == "INHERITANCE-ALLOWED":
            entry["admission_class"] = "ADMISSION-GRANTED"
            entry["allowed_targets"] = ["theorem_facing_review", "simulation_stress_testing"]
            entry["proof_eligibility_effect"] = "eligible"
            
        elif audit["inheritance_class"] == "INHERITANCE-CONDITIONAL":
            entry["admission_class"] = "ADMISSION-CONDITIONAL"
            entry["allowed_targets"] = ["theorem_facing_review", "simulation_stress_testing"]
            entry["required_constraints"] = ["Strict adherence to local scope boundary."]
            entry["proof_eligibility_effect"] = "review_required"
            
        elif audit["inheritance_class"] == "INHERITANCE-BLOCKED":
            entry["admission_class"] = "ADMISSION-STRESS-ONLY"
            entry["allowed_targets"] = ["simulation_stress_testing", "failure_geometry_reference"]
            entry["proof_eligibility_effect"] = "stress_only"
            
        elif audit["inheritance_class"] == "INHERITANCE-QUARANTINED":
            entry["admission_class"] = "ADMISSION-QUARANTINED"
            entry["allowed_targets"] = ["historical_reference"]
            entry["proof_eligibility_effect"] = "quarantined"
            
        report["admission_entries"].append(entry)

    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"Recursive dependency admission report emitted to {result_path}")
    return report

if __name__ == "__main__":
    run_admission_gate()
