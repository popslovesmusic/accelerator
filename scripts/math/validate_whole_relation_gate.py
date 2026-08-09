import json
import os
import glob
from datetime import datetime

def validate_whole_relation_gate():
    registry_path = "registry/math/whole_relation_validation_gate_registry.json"
    result_path = "validation/results/whole_relation_validation_gate_result.json"
    
    report = {
        "validation_id": "VAL-PALG-GATE-AUDIT-001",
        "status": "pass",
        "checked_artifacts": [],
        "passed_checks": 0,
        "failed_checks": 0,
        "failure_conditions_detected": [],
        "recommendations": [],
        "timestamp": datetime.now().isoformat()
    }
    
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["failure_conditions_detected"].append("gate_registry_missing")
        return report

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)

    # 1. Self-Check
    if registry.get("gate_status") != "CANDIDATE_VALIDATION_GATE":
        report["status"] = "fail"
        report["failure_conditions_detected"].append("illegal_gate_status")

    # 2. Artifact Scanning
    targets = registry.get("input_targets", [])
    files_to_scan = []
    for t in targets:
        files_to_scan.extend(glob.glob(t))

    for f_path in files_to_scan:
        artifact_name = os.path.basename(f_path)
        is_md = artifact_name.endswith(".md")
        
        # Skip self and fundamental phase declaration
        is_governance_core = any(x in artifact_name for x in ["phase_registry", "declaration", "validation_gate", "trace_schema"])
        
        report["checked_artifacts"].append(artifact_name)
        
        with open(f_path, 'r', encoding='utf-8', errors='ignore') as f:
            content_raw = f.read()
            content_lower = content_raw.lower()
            
            # Check for source_relation (if not core governance)
            if not is_governance_core:
                source_check = "source_relation" in content_lower or "source_context" in content_lower
                if is_md:
                     source_check = source_check or "source relation" in content_lower
                
                if not source_check:
                    report["status"] = "fail"
                    report["failed_checks"] += 1
                    report["failure_conditions_detected"].append(f"missing_source_relation_in_{artifact_name}")
                else:
                    report["passed_checks"] += 1

            # Check for non_separability_acknowledged (if aspect or projection)
            if "aspect" in artifact_name or "projection" in artifact_name or "derived" in artifact_name:
                sep_check = "non_separability_acknowledged" in content_lower
                if is_md:
                     sep_check = sep_check or "non-separability acknowledged" in content_lower
                
                if not sep_check:
                    report["status"] = "fail"
                    report["failed_checks"] += 1
                    report["failure_conditions_detected"].append(f"missing_non_separability_acknowledgment_in_{artifact_name}")
                else:
                    report["passed_checks"] += 1

            # Check for primitive_status escalation
            if '"primitive_status": true' in content_lower.replace(" ", ""):
                report["status"] = "fail"
                report["failed_checks"] += 1
                report["failure_conditions_detected"].append(f"unauthorized_primitive_promotion_in_{artifact_name}")

            # Check for blocked language
            blocked = [
                "proof of reality", "unified physics", "replacing arithmetic", 
                "standard arithmetic is wrong", "universal unification"
            ]
            for phrase in blocked:
                if phrase in content_lower:
                    # HEURISTIC: Check if it's in a negative context (forbidden/banned/etc)
                    # We check the surrounding text in the raw content to see if it's within a specific JSON key or MD section
                    pos = content_lower.find(phrase)
                    context_start = max(0, pos-200)
                    context_end = min(len(content_lower), pos+phrase.length+200 if hasattr(phrase, 'length') else pos+len(phrase)+200)
                    context_area = content_lower[context_start:pos]
                    
                    is_safe = any(neg in context_area for neg in ["forbidden", "banned", "prohibited", "invalid", "reject", "block", "must not"])
                    
                    if not is_safe:
                        report["status"] = "fail"
                        report["failed_checks"] += 1
                        report["failure_conditions_detected"].append(f"blocked_language_detected_in_{artifact_name}:_{phrase}")

    if report["failed_checks"] > 0:
        report["status"] = "fail"

    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    res = validate_whole_relation_gate()
    print(json.dumps(res, indent=2))
