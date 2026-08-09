import json
import os
from datetime import datetime

def validate_mt_law_a_foundation():
    results = {
        "mt_law_a_definition_tightening_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }
    
    report = results["mt_law_a_definition_tightening_validation"]
    
    registry_path = "registry/math/mt_law_a_persistence_registry.json"
    doc_path = "docs/math/mt_law_a_bounded_continuation_persistence_definition.md"
    
    # 1. Registry Check
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A registry missing.")
    else:
        try:
            with open(registry_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Check for metrics
                defs = data.get("definitions", {})
                required_metrics = ["persistence_metric", "admissibility_cost_metric", "local_budget_metric"]
                for m in required_metrics:
                    if m not in defs:
                        report["status"] = "fail"
                        report["errors"].append(f"Missing metric definition: {m}")
                
                # Check for failure conditions
                if not data.get("failure_conditions"):
                    report["errors"].append("Missing failure conditions in registry.")
                
                # Check governance (promotion blocked)
                gov = data.get("governance_flags", {})
                if gov.get("promote_to_theorem") is True:
                    report["status"] = "fail"
                    report["errors"].append("Theorem promotion must be blocked in foundation phase.")
                
                report["checks"].append("MT-LAW-A registry structure verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Registry parse error: {e}")

    # 2. Document Check
    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A foundation document missing.")
    else:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            required_sections = [
                "purpose", "dependency laws", "persistence definition",
                "admissibility-cost definition", "local budget definition",
                "persistence failure conditions", "identity continuity constraints",
                "operational metrics", "simulation alignment notes",
                "counterexample obligations", "governance constraints",
                "status footer"
            ]
            for section in required_sections:
                if section not in content:
                    report["status"] = "fail"
                    report["errors"].append(f"Section '{section}' missing from foundation document.")
            
            # Governance compliance check
            required_lang = [
                "bounded admissible continuation", "failure-preserving",
                "projectional", "nonprimitive geometry", "finite-budget constrained"
            ]
            for lang in required_lang:
                if lang not in content:
                    report["status"] = "warning"
                    report["warnings"].append(f"Required governance terminology missing: '{lang}'")

            # Status footer check
            if "ts0_definitional_foundation" not in content or "not_proven" not in content:
                 report["status"] = "fail"
                 report["errors"].append("Mandatory status footer incorrect or missing.")

        report["checks"].append("MT-LAW-A document presence and content scanned.")

    # Generate result file
    output_path = "validation/results/mt_law_a_definition_tightening_result.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Format result for the specific deliverable requirements
    deliverable_result = {
        "validation_status": report["status"],
        "missing_sections": [s for s in required_sections if s not in content] if 'content' in locals() else required_sections,
        "governance_violations": report["errors"] + report["warnings"],
        "definition_integrity": "high" if report["status"] == "pass" else "compromised",
        "timestamp": datetime.now().isoformat()
    }
    
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(deliverable_result, f, indent=2)
        
    return results

if __name__ == "__main__":
    res = validate_mt_law_a_foundation()
    print(json.dumps(res, indent=2))
