import json
import os
from datetime import datetime

def validate_mt_law_a_sketch():
    results = {
        "mt_law_a_local_proof_sketch_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }
    
    report = results["mt_law_a_local_proof_sketch_validation"]
    
    registry_path = "registry/math/mt_law_a_local_proof_registry.json"
    doc_path = "docs/math/mt_law_a_local_proof_sketch.md"
    
    # 1. Registry Check
    if not os.path.exists(registry_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A local proof registry missing.")
    else:
        try:
            with open(registry_path, 'r') as f:
                data = json.load(f)
                
                # Check required fields
                required_fields = [
                    "local_assumptions", "local_constraints", "proof_sketch_steps", 
                    "blocked_regions", "remaining_obligations", "counterexample_status", 
                    "nonuniversality_flags", "governance_flags", "nonuniversality_declaration",
                    "global_scope_blocked", "physics_mapping_blocked", "unresolved_blockers_preserved"
                ]
                for field in required_fields:
                    if field not in data:
                        report["status"] = "fail"
                        report["errors"].append(f"Missing required field in registry: {field}")
                
                # Check that counterexamples are not discharged
                status = data.get("counterexample_status", {})
                for ce, s in status.items():
                    if s != "not discharged":
                        report["status"] = "fail"
                        report["errors"].append(f"Counterexample {ce} incorrectly marked as {s}. Must be 'not discharged'.")
                
                # Check governance (promotion blocked)
                gov = data.get("governance_flags", {})
                if gov.get("proof_status") != "TS3_local_argument_only":
                    report["status"] = "fail"
                    report["errors"].append(f"Incorrect proof status: {gov.get('proof_status')}. Must be 'TS3_local_argument_only'.")
                
                if not data.get("global_scope_blocked") or not data.get("physics_mapping_blocked"):
                    report["status"] = "fail"
                    report["errors"].append("Registry must explicitly block global scope and physics mapping.")

                report["checks"].append("MT-LAW-A local proof registry structure verified.")
        except Exception as e:
            report["status"] = "fail"
            report["errors"].append(f"Registry parse error: {e}")

    # 2. Document Check
    if not os.path.exists(doc_path):
        report["status"] = "fail"
        report["errors"].append("MT-LAW-A local proof sketch document missing.")
    else:
        with open(doc_path, 'r') as f:
            content = f.read().lower()
            required_sections = [
                "purpose", "local scope declaration", "dependency chain",
                "declared assumptions", "persistence conditions",
                "admissibility budget conditions", "topology accessibility conditions",
                "identity continuity conditions", "local continuation argument",
                "failure boundary preservation", "counterexample non-discharge declaration",
                "known blockers", "non-universality declaration",
                "open proof obligations", "status footer"
            ]
            for section in required_sections:
                if section not in content:
                    report["status"] = "fail"
                    report["errors"].append(f"Section '{section}' missing from sketch document.")
            
            # Check for non-universality language
            required_lang = [
                "bounded local admissibility domain",
                "does not establish universal persistence",
                "does not establish global closure",
                "does not establish empirical or physical equivalence",
                "counterexamples and unresolved blockers remain active",
                "topology severance divergence hotspots remain unresolved",
                "identity continuity ambiguity remains unresolved"
            ]
            for lang in required_lang:
                if lang not in content:
                    report["status"] = "fail"
                    report["errors"].append(f"Strong non-universality language missing: '{lang}'")

            # Status footer check
            if "ts3_local_argument_only" not in content or "not_proven" not in content:
                 report["status"] = "fail"
                 report["errors"].append("Mandatory status footer incorrect or missing.")

        report["checks"].append("MT-LAW-A sketch document presence and content scanned.")

    # Generate formal result file
    output_path = "validation/results/mt_law_a_local_proof_nonuniversality_hardening_result.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    deliverable_result = {
        "validation_status": report["status"],
        "nonuniversality_verified": True if report["status"] == "pass" else False,
        "scope_limit_verified": True if "local scope declaration" in locals() else False, # Simplified check
        "global_claim_absence_verified": True if "global closure" not in content or "does not establish global closure" in content else False,
        "physics_claim_absence_verified": True if "physical equivalence" not in content or "does not establish empirical or physical equivalence" in content else False,
        "timestamp": datetime.now().isoformat()
    }
    
    # Logic fix for scope_limit_verified
    deliverable_result["scope_limit_verified"] = "local restricted domain" in content or "bounded local admissibility domain" in content

    with open(output_path, "w") as f:
        json.dump(deliverable_result, f, indent=2)
        
    return results

if __name__ == "__main__":
    res = validate_mt_law_a_sketch()
    print(json.dumps(res, indent=2))
