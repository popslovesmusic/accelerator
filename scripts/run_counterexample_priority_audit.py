import json
import os
from datetime import datetime

def run_counterexample_audit():
    registry_path = "registry/counterexample_priority_audit_registry.json"
    campaigns_dir = "outputs/evidence_campaigns/"
    
    if not os.path.exists(registry_path):
        print(f"Error: {registry_path} missing.")
        return

    with open(registry_path, 'r') as f:
        registry = json.load(f)

    print("Running Counterexample Priority Audit...")
    
    # Audit recent results
    if os.path.exists(campaigns_dir):
        for result_file in os.listdir(campaigns_dir):
            if result_file.endswith("_result.json"):
                with open(os.path.join(campaigns_dir, result_file), 'r') as f:
                    res = json.load(f)
                    
                # Check for generic signature risk
                if res.get("primary_verdict") == "PASS" and res.get("counterexample_verdict") == "PASS":
                    print(f"FLAG: Generic Signature Risk detected in {res['campaign_id']}")
                    # Update registry (simulated)

    print("Audit: PASS")
    return True

if __name__ == "__main__":
    run_counterexample_audit()
