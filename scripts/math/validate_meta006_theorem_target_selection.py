import json
import os

def validate_meta006():
    results = {
        "meta006_theorem_target_selection_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }
    
    report = results["meta006_theorem_target_selection_validation"]
    
    registry_path = "registry/math/meta006_theorem_target_selection_registry.json"
    doc_path = "docs/math/theorem_target_selection_and_strengthening_plan.md"
    
    # 1. Registry check
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["errors"].append("META-006 registry missing.")
    else:
        try:
            with open(registry_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Check for targets
                targets = data.get("selected_targets", [])
                if len(targets) < 4:
                    report["status"] = "fail"
                    report["errors"].append(f"Insufficient theorem targets: {len(targets)}/4")
                
                # Check for highest priority
                has_highest = any(t.get("priority") == "highest" and t.get("id") == "MT-LAW-A" for t in targets)
                if not has_highest:
                    report["status"] = "fail"
                    report["errors"].append("Highest priority MT-LAW-A missing in registry.")
                
                # Check for dependencies and blockers
                for t in targets:
                    if not t.get("depends_on"):
                        report["errors"].append(f"Target {t.get('id')} missing dependencies.")
                    if not t.get("proof_blockers"):
                        report["errors"].append(f"Target {t.get('id')} missing proof blockers.")

                # Check governance
                gov = data.get("governance", {})
                if not gov.get("no_law_expansion"):
                    report["status"] = "fail"
                    report["errors"].append("Governance failed to block new law expansion.")
                
                report["checks"].append("META-006 registry content verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Registry parse error: {e}")

    # 2. Document check
    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["errors"].append("META-006 document missing.")
    else:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            required_sections = [
                "executive summary", "high-priority theorem targets",
                "strengthening roadmap", "phase 1: definition tightening",
                "phase 2: counterexample obligations", "phase 3: simulation targets",
                "governance constraints"
            ]
            for section in required_sections:
                if section not in content:
                    report["status"] = "fail"
                    report["errors"].append(f"Section '{section}' missing from document.")
            
            # Check for specific targets
            for tid in ["mt-law-a", "mt-law-b", "mt-law-c", "mt-law-d"]:
                if tid not in content:
                    report["status"] = "fail"
                    report["errors"].append(f"Target {tid} missing from document.")

        report["checks"].append("META-006 document presence and content scanned.")

    output_path = "outputs/audits/meta006_validation_report.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(results, f, indent=2)
        
    return results

if __name__ == "__main__":
    res = validate_meta006()
    print(json.dumps(res, indent=2))
