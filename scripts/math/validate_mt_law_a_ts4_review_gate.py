import json
import os
from datetime import datetime

def validate_mt_law_a_ts4_gate():
    results = {
        "mt_law_a_ts4_review_gate_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }
    
    report = results["mt_law_a_ts4_review_gate_validation"]
    
    registry_path = "registry/math/mt_law_a_ts4_review_gate_registry.json"
    gate_doc_path = "docs/math/mt_law_a_ts4_review_gate.md"
    
    # 1. Registry Check
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A TS4 review gate registry missing.")
    else:
        try:
            with open(registry_path, 'r') as f:
                data = json.load(f)
                
                # Check Preconditions
                preconditions = data.get("preconditions", [])
                if len(preconditions) < 5:
                    report["status"] = "fail"
                    report["errors"].append(f"Insufficient preconditions: {len(preconditions)}/5")
                for pre in preconditions:
                    if pre.get("status") != "VERIFIED":
                        report["status"] = "fail"
                        report["errors"].append(f"Precondition '{pre.get('id')}' not verified.")
                
                # Check Mandatory Blockers
                required_blockers = [
                    "topology severance divergence hotspots",
                    "identity continuity ambiguity",
                    "reconstruction equivalence incompleteness",
                    "oscillatory non-stabilization regions",
                    "cross-mechanism divergence regions",
                    "threshold-sensitive metastability"
                ]
                found_blockers = data.get("mandatory_open_blockers", [])
                for blocker in required_blockers:
                    if blocker not in found_blockers:
                        report["status"] = "fail"
                        report["errors"].append(f"Mandatory open blocker '{blocker}' missing from registry.")
                
                # Check Forbidden Outcomes
                forbidden = [
                    "THEOREM_PROVEN",
                    "UNIVERSALLY_VALID",
                    "GLOBAL_CLOSURE_COMPLETE",
                    "COUNTEREXAMPLES_DISCHARGED",
                    "PHYSICS_MAPPING_CONFIRMED"
                ]
                registered_forbidden = data.get("forbidden_review_outcomes", [])
                for f_outcome in forbidden:
                    if f_outcome not in registered_forbidden:
                        report["status"] = "fail"
                        report["errors"].append(f"Forbidden outcome '{f_outcome}' missing from registry.")

                report["checks"].append("MT-LAW-A TS4 review gate registry verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Registry parse error: {e}")

    # 2. Document Check
    if not os.path.exists(gate_doc_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A TS4 review gate document missing.")
    else:
        with open(gate_doc_path, 'r') as f:
            content = f.read().lower()
            required_sections = [
                "purpose", "restricted-domain ts4 scope", "required preconditions",
                "mandatory open blockers", "counterexample preservation requirements",
                "failure boundary preservation requirements", "cross-mechanism limitation requirements",
                "governance constraints", "forbidden escalations", "review outcome conditions",
                "status footer"
            ]
            for section in required_sections:
                if section not in content:
                    report["status"] = "fail"
                    report["errors"].append(f"Section '{section}' missing from document.")
            
            # Check for Precondition IDs in document
            for i in range(1, 6):
                if f"pre-a00{i}" not in content:
                    report["errors"].append(f"Precondition ID PRE-A00{i} missing in document.")

            # Check for Review Condition IDs in document
            for i in range(1, 6):
                if f"rc-a00{i}" not in content:
                    report["errors"].append(f"Review Condition ID RC-A00{i} missing in document.")

            # Status footer check
            if "ts4_review_gate_only" not in content or "not_proven" not in content:
                 report["status"] = "fail"
                 report["errors"].append("Mandatory status footer incorrect or missing.")

        report["checks"].append("MT-LAW-A TS4 review gate document presence and content scanned.")

    # Generate formal result file
    output_path = "validation/results/mt_law_a_ts4_review_gate_result.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    deliverable_result = {
        "validation_status": report["status"],
        "preconditions_verified": len([p for p in data.get("preconditions", []) if p.get("status") == "VERIFIED"]) if 'data' in locals() else 0,
        "governance_violations": report["errors"] + report["warnings"],
        "timestamp": datetime.now().isoformat()
    }
    
    with open(output_path, "w") as f:
        json.dump(deliverable_result, f, indent=2)
        
    return results

if __name__ == "__main__":
    res = validate_mt_law_a_ts4_gate()
    print(json.dumps(res, indent=2))
