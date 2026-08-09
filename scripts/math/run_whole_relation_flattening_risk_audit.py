import json
import os
import glob
from datetime import datetime

def run_whole_relation_flattening_risk_audit():
    """
    Runner for Whole-Relation Flattening Risk Audit.
    Scans process algebra artifacts for symbolic collapse and escalation risks.
    """
    registry_path = "registry/math/whole_relation_flattening_risk_audit_registry.json"
    result_path = "validation/results/whole_relation_flattening_risk_audit_result.json"
    
    if not os.path.exists(registry_path):
        return {"overall_status": "FAIL", "reason": "audit registry missing"}

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)

    report = {
        "audit_id": "WRF-AUDIT-SUM-001",
        "timestamp": datetime.now().isoformat(),
        "overall_status": "PASS",
        "checked_artifacts": [],
        "detected_risks": [],
        "governance_recommendations": []
    }

    # Load targets and patterns
    targets = registry.get("audit_targets", [])
    risk_patterns = registry.get("flag_patterns", {})
    
    files_to_scan = []
    for t in targets:
        files_to_scan.extend(glob.glob(t))

    for f_path in files_to_scan:
        artifact_name = os.path.basename(f_path)
        # Skip the registry and docs of the audit itself
        if "flattening_risk_audit" in artifact_name:
            continue
            
        report["checked_artifacts"].append(artifact_name)
        
        with open(f_path, 'r', encoding='utf-8', errors='ignore') as f:
            content_lower = f.read().lower()
            
            # Scan for each risk category
            for category, patterns in risk_patterns.items():
                for pattern in patterns:
                    if pattern.lower() in content_lower:
                        # Heuristic context check: Is it in a forbidden/banned/prohibited section?
                        # We look at the 100 characters before the pattern.
                        pos = content_lower.find(pattern.lower())
                        pre_context = content_lower[max(0, pos-150):pos]
                        
                        is_negative_context = any(word in pre_context for x in ["forbidden", "banned", "prohibited", "invalid", "reject", "block"] for word in [x])
                        
                        if not is_negative_context:
                            # Map category to risk_id
                            risk_id = "UNKNOWN"
                            for rc in registry.get("risk_categories", []):
                                if rc["name"] == category:
                                    risk_id = rc["risk_id"]
                                    break
                            
                            severity = "MEDIUM"
                            if "escalation" in category:
                                severity = "CRITICAL"
                            elif "fragmentation" in category:
                                severity = "HIGH"
                                
                            risk_event = {
                                "risk_id": risk_id,
                                "category": category,
                                "severity": severity,
                                "artifact": artifact_name,
                                "excerpt": content_lower[max(0, pos-30):min(len(content_lower), pos+60)].replace("\n", " "),
                                "recommended_correction": f"Explicitly mark as projection or remove unearned claim: '{pattern}'"
                            }
                            report["detected_risks"].append(risk_event)
                            
                            if severity == "CRITICAL":
                                report["overall_status"] = "FAIL"
                            elif severity == "HIGH" and report["overall_status"] != "FAIL":
                                report["overall_status"] = "FAIL"
                            elif severity == "MEDIUM" and report["overall_status"] == "PASS":
                                report["overall_status"] = "PASS_WITH_WARNINGS"

    if report["overall_status"] == "PASS":
         report["governance_recommendations"].append("Holistic relational core appears secure.")
    else:
         report["governance_recommendations"].append("Review detected risks and ensure all reductions are marked PROJECTION_ONLY.")

    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"Whole-relation flattening risk audit complete. Results in {result_path}")
    return report

if __name__ == "__main__":
    run_whole_relation_flattening_risk_audit()
