import json
import os
from datetime import datetime

def run_audit():
    """
    Runner for Restricted Local Proof Consistency Audit.
    Verifies symbolic segment against typing and scope constraints.
    """
    segment_registry_path = "registry/math/restricted_local_proof_segment_registry.json"
    signature_registry_path = "registry/math/operator_signature_registry.json"
    audit_result_path = "validation/results/restricted_local_proof_consistency_audit_summary.json"
    
    if not os.path.exists(segment_registry_path):
        return {"status": "fail", "reason": "segment registry missing"}

    with open(segment_registry_path, 'r') as f:
        segment_data = json.load(f)
        
    with open(signature_registry_path, 'r') as f:
        signature_data = json.load(f)

    audit_summary = {
        "audit_id": "RLP-CONS-SUM-001",
        "timestamp": datetime.now().isoformat(),
        "verifications": []
    }

    # 1. Verify Operator Typing
    for op in segment_data["operator_chain"]:
        found_signature = False
        for sig in signature_data["signatures"]:
            if sig["operator"] == op:
                found_signature = True
                audit_summary["verifications"].append({
                    "target": f"operator_typing:{op}",
                    "status": "CONSISTENT",
                    "details": f"Signature matches {sig['operation_class']}"
                })
        if not found_signature:
             audit_summary["verifications"].append({
                "target": f"operator_typing:{op}",
                "status": "FAILURE",
                "failure_class": "RLP-CF-002",
                "details": "No signature found in registry"
            })

    # 2. Verify Scope Constraints
    if segment_data["restricted_scope"] == "STRICTLY_LOCAL_RESTRICTED_DOMAIN":
         audit_summary["verifications"].append({
            "target": "scope_preservation",
            "status": "CONSISTENT",
            "details": "Restricted domain scope explicitly declared"
        })
    else:
         audit_summary["verifications"].append({
            "target": "scope_preservation",
            "status": "FAILURE",
            "failure_class": "RLP-CF-001",
            "details": "Scope violation or implicit globalization detected"
        })

    # 3. Verify Failure Geometry Links
    # (Simplified check: ensure mandatory preservations are non-empty)
    if segment_data["mandatory_preservations"]:
         audit_summary["verifications"].append({
            "target": "failure_geometry_integrity",
            "status": "CONSISTENT",
            "details": f"{len(segment_data['mandatory_preservations'])} blockers preserved"
        })

    with open(audit_result_path, 'w') as f:
        json.dump(audit_summary, f, indent=2)

    print(f"Consistency audit summary saved to {audit_result_path}")
    return audit_summary

if __name__ == "__main__":
    run_audit()
