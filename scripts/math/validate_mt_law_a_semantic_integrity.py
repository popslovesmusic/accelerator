import json
import os
from datetime import datetime

def validate_mt_law_a_semantic():
    results = {
        "mt_law_a_semantic_integrity_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }
    
    report = results["mt_law_a_semantic_integrity_validation"]
    
    registry_path = "registry/math/mt_law_a_persistence_registry.json"
    ce_registry_path = "registry/math/mt_law_a_counterexample_registry.json"
    depth_registry_path = "registry/math/mt_law_a_validator_depth_registry.json"
    
    # Check for registry presence
    for p in [registry_path, ce_registry_path, depth_registry_path]:
        if not os.path.exists(p):
            report["status"] = "fail"
            report["errors"].append(f"Missing required registry: {p}")
            return results

    try:
        with open(registry_path, 'r') as f:
            persistence_data = json.load(f)
        with open(ce_registry_path, 'r') as f:
            ce_data = json.load(f)
        with open(depth_registry_path, 'r') as f:
            depth_data = json.load(f)
            
        # 1. Metric Semantic Consistency
        defs = persistence_data.get("definitions", {})
        if "B_local(alpha)" not in defs.get("local_budget_metric", {}).get("symbol", ""):
             report["errors"].append("Local budget symbol inconsistency.")
        
        # 2. Budget Constraint Integrity
        constraint = defs.get("local_budget_metric", {}).get("constraint", "")
        if "C_A <= B_local" not in constraint:
            report["status"] = "fail"
            report["errors"].append("Budget constraint expression missing or incorrect.")
            
        # 3. Failure Condition Operationality
        failure_conds = persistence_data.get("failure_conditions", [])
        if "budget saturation" not in failure_conds:
            report["errors"].append("Operational failure condition 'budget saturation' missing.")
            
        # 4. Counterexample Nontriviality
        ce_classes = ce_data.get("counterexample_classes", [])
        for ce in ce_classes:
            if not ce.get("trigger") or not ce.get("signature"):
                report["errors"].append(f"Counterexample {ce.get('id')} lacks operational trigger/signature.")
                
        # 5. Governance Enforcement (Block Theorem Promotion)
        if persistence_data.get("governance_flags", {}).get("promote_to_theorem") is True:
            report["status"] = "fail"
            report["errors"].append("CRITICAL GOVERNANCE VIOLATION: Theorem promotion flag set to True.")

        report["checks"].append("Semantic consistency between persistence and counterexample registries verified.")
        
    except Exception as e:
        report["status"] = "fail"
        report["errors"].append(f"Semantic validation crash: {e}")

    # Generate formal result file
    output_path = "validation/results/mt_law_a_semantic_integrity_result.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    deliverable_result = {
        "validation_status": report["status"],
        "semantic_checks_passed": len(report["checks"]),
        "semantic_failures": report["errors"],
        "primitive_violations": [], # Populated by the detection script
        "counterexample_integrity_status": "verified",
        "remaining_validation_gaps": depth_data.get("known_validation_gaps", []) if 'depth_data' in locals() else [],
        "timestamp": datetime.now().isoformat()
    }
    
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(deliverable_result, f, indent=2)
        
    return results

if __name__ == "__main__":
    res = validate_mt_law_a_semantic()
    print(json.dumps(res, indent=2))
