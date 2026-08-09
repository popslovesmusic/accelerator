import json
import os
from datetime import datetime

def validate_resolution():
    registry_path = "registry/math/mt_law_a_foundations_resolution_registry.json"
    doc_path = "docs/math/mt_law_a_foundations_resolution.md"
    result_path = "validation/results/mt_law_a_foundations_resolution_result.json"
    
    report = {
        "resolution_id": "RES-MT-LAW-A-FOUNDATIONS-001",
        "status": "pass",
        "continuation_authorized": False,
        "blockers_preserved": 0,
        "governance_violations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing resolution registry")
        return report

    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["governance_violations"].append("missing resolution document")

    with open(registry_path, 'r') as f:
        registry = json.load(f)
        
        # Check continuation status
        if registry["continuation_status"] == "FOUNDATION_CONTINUATION_ALLOWED_WITH_OPEN_BLOCKERS":
            report["continuation_authorized"] = True
        else:
             report["status"] = "fail"
             report["governance_violations"].append("continuation not authorized in registry")

        # Check blockers
        mandatory_blockers = [
            "topology severance divergence hotspots",
            "identity continuity ambiguity",
            "reconstruction equivalence incompleteness",
            "oscillatory non-stabilization regions",
            "cross-mechanism divergence regions",
            "threshold-sensitive metastability"
        ]
        for blocker in mandatory_blockers:
            if blocker in registry["open_blockers"]:
                report["blockers_preserved"] += 1
            else:
                report["status"] = "fail"
                report["governance_violations"].append(f"mandatory blocker '{blocker}' missing from registry")

        # Check for NOT_PROVEN status
        if registry["governance"]["theorem_status"] != "NOT_PROVEN":
            report["status"] = "fail"
            report["governance_violations"].append("forbidden theorem status promotion")

    # Check for forbidden outcomes in document
    forbidden_outcomes = [
        "THEOREM_PROVEN",
        "TS5_READY",
        "COUNTEREXAMPLES_DISCHARGED",
        "GLOBAL_CLOSURE_COMPLETE",
        "PHYSICS_MAPPING_CONFIRMED"
    ]
    with open(doc_path, 'r') as f:
        doc_content = f.read()
        for outcome in forbidden_outcomes:
            if outcome in doc_content:
                report["status"] = "fail"
                report["governance_violations"].append(f"forbidden outcome '{outcome}' detected in document")

    # Final result
    with open(result_path, 'w') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_resolution()
    print(json.dumps(res, indent=2))
