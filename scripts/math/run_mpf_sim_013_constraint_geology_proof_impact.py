import json
import os
from datetime import datetime

def run_impact_audit():
    """
    Runner for Constraint Geology Proof-Impact Audit.
    Evaluates geology atlas entries against proof-readiness requirements.
    """
    atlas_path = "validation/results/mpf_sim_012_constraint_geology_atlas_result.json"
    result_path = "validation/results/mpf_sim_013_constraint_geology_proof_impact_result.json"
    
    if not os.path.exists(atlas_path):
        return {"status": "fail", "reason": "geology atlas missing"}

    with open(atlas_path, 'r', encoding='utf-8') as f:
        atlas_data = json.load(f)

    audit = {
        "audit_id": "SIM-IMPACT-SUM-001",
        "timestamp": datetime.now().isoformat(),
        "audit_results": [],
        "governance": {
            "theorem_status": "NOT_PROVEN",
            "scope_status": "STRICTLY_LOCAL_RESTRICTED_DOMAIN",
            "physics_status": "NON_PHYSICAL_ANALOG_MODEL"
        }
    }

    # Map geology entries to proof impact
    for entry in atlas_data["geology_entries"]:
        g_class = entry["geology_class"]
        
        impact_entry = {
            "audit_entry_id": f"AUDIT-{entry['entry_id']}",
            "geology_entry_id": entry["entry_id"],
            "geology_class": g_class,
            "impact_class": "CG-IMPACT-BLOCKING",
            "proof_eligibility_effect": "blocked",
            "globalization_risk_score": 0.0,
            "false_stability_risk_score": 0.0,
            "hysteresis_risk_score": 0.0,
            "boundary_leakage_risk_score": 0.0,
            "failure_geometry_triggered": entry["failure_geometry_links"]
        }

        # Classification Logic
        if g_class == "CG-STABLE-GROOVE":
            impact_entry["impact_class"] = "CG-IMPACT-SUPPORTIVE"
            impact_entry["proof_eligibility_effect"] = "eligible"
            impact_entry["globalization_risk_score"] = 0.05
            
        elif g_class == "CG-ELASTIC-DEFORMATION":
            impact_entry["impact_class"] = "CG-IMPACT-CONDITIONAL"
            impact_entry["proof_eligibility_effect"] = "review_required"
            impact_entry["hysteresis_risk_score"] = 0.35
            
        elif g_class == "CG-SCARRED-REGION":
            impact_entry["impact_class"] = "CG-IMPACT-BLOCKING"
            impact_entry["proof_eligibility_effect"] = "blocked"
            impact_entry["failure_geometry_triggered"] = entry["failure_geometry_links"]

        elif g_class == "CG-DECEPTIVE-GROOVE":
            impact_entry["impact_class"] = "CG-IMPACT-DECEPTIVE"
            impact_entry["proof_eligibility_effect"] = "blocked"
            impact_entry["false_stability_risk_score"] = 0.95

        audit["audit_results"].append(impact_entry)

    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(audit, f, indent=2)

    print(f"Proof-impact audit complete. Results in {result_path}")
    return audit

if __name__ == "__main__":
    run_impact_audit()
