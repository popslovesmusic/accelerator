import json
import os
import glob
from datetime import datetime

def validate_recursive_aspect_simultaneity():
    registry_path = "registry/math/recursive_aspect_simultaneity_validator_registry.json"
    result_path = "validation/results/recursive_aspect_simultaneity_validator_result.json"
    
    report = {
        "validator_id": "RASV",
        "checked_artifacts": [],
        "passed_checks": [],
        "failed_checks": [],
        "detected_terms": [],
        "required_corrections": [],
        "overall_status": "PASS",
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["overall_status"] = "FAIL"
        report["failed_checks"].append("registry_missing")
        return report

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)

    # 1. Governance Invariant Check
    gov = registry.get("governance_status", {})
    if gov.get("theorem_status") != "NOT_PROVEN":
        report["overall_status"] = "FAIL"
        report["failed_checks"].append("forbidden_theorem_status_escalation")

    # 2. Sequential Language Scanning
    reject_terms = []
    for check in registry.get("validator_checks", []):
        if check["check_id"] == "RASV-001":
            reject_terms = check["reject_terms"]
            
    targets = registry.get("input_targets", [])
    files_to_scan = []
    for t in targets:
        files_to_scan.extend(glob.glob(t))

    for f_path in files_to_scan:
        artifact_name = os.path.basename(f_path)
        
        # Skip validator/registry infrastructure
        if "simultaneity_validator" in artifact_name or "gate_registry" in artifact_name:
            continue
            
        report["checked_artifacts"].append(artifact_name)
        
        with open(f_path, 'r', encoding='utf-8', errors='ignore') as f:
            content_lower = f.read().lower()
            
            # 2.1 Contextual Filter: 
            # We look for sequential language specifically in "active" math fields.
            # We ignore "purpose", "patch_id", "status" as these are meta-fields.
            
            # Simple heuristic: remove metadata block if JSON
            active_content = content_lower
            if artifact_name.endswith(".json"):
                try:
                    data = json.loads(content_lower)
                    # Filter out metadata
                    filtered_data = {k: v for k, v in data.items() if k not in ["purpose", "patch_id", "status", "name"]}
                    active_content = json.dumps(filtered_data)
                except:
                    pass # Fallback to full content

            found_sequential = False
            for term in reject_terms:
                if term in active_content:
                    # Check if it's qualified by "projection" or "shorthand"
                    context_snippet = active_content[max(0, active_content.find(term)-50):active_content.find(term)+50]
                    if "projection" not in context_snippet and "shorthand" not in context_snippet:
                        report["detected_terms"].append(f"{term}_in_{artifact_name}")
                        found_sequential = True
            
            if found_sequential:
                report["overall_status"] = "FAIL"
                report["failed_checks"].append(f"sequential_language_in_{artifact_name}")
                report["required_corrections"].append(f"Remove sequential causal terms from analytical fields of {artifact_name}")

            # 3. Associativity/Transitivity Check
            if "associative" in active_content or "transitive" in active_content:
                if "block" not in active_content and "not" not in active_content and "forbidden" not in active_content:
                     report["overall_status"] = "FAIL"
                     report["failed_checks"].append(f"unlicensed_property_assumption_in_{artifact_name}")
                     report["required_corrections"].append(f"Explicitly block associativity/transitivity in {artifact_name}")

    if report["overall_status"] == "PASS":
        report["passed_checks"].append("no_sequential_collapse_detected")
        report["passed_checks"].append("no_unlicensed_algebraic_assumptions")

    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_recursive_aspect_simultaneity()
    print(json.dumps(res, indent=2))
