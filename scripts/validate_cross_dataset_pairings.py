import json
import os
import argparse
from datetime import datetime

def validate_cross_dataset_pairings():
    registry_path = "registry/cross_dataset_pairing_registry.json"
    
    if not os.path.exists(registry_path):
        print(f"Error: {registry_path} missing.")
        return

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)

    print(f"Validating Cross-Dataset Pairing Registry (v{registry.get('version')})")
    
    errors = []
    
    # 1. Check for mandatory fields in each pairing
    for pairing in registry.get("pairings", []):
        pid = pairing.get("pairing_id")
        required = ["pairing_class", "support_dataset", "adversarial_dataset", "expected_divergence", "status"]
        for field in required:
            if field not in pairing:
                errors.append(f"Pairing '{pid}' missing mandatory field: {field}")
        
        # 2. Verify that adversarial is not the same as support
        if pairing.get("support_dataset") == pairing.get("adversarial_dataset"):
            errors.append(f"Pairing '{pid}' support and adversarial datasets are identical.")

    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        return False
    
    print("Validation: PASS")
    return True

if __name__ == "__main__":
    if validate_cross_dataset_pairings():
        exit(0)
    else:
        exit(1)
