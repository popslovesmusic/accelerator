import json
import os
import argparse
from datetime import datetime

def validate_campaign_templates():
    registry_path = "registry/evidence_campaign_template_registry.json"
    
    if not os.path.exists(registry_path):
        print(f"Error: {registry_path} missing.")
        return

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)

    print(f"Validating Evidence Campaign Template Registry (v{registry.get('version')})")
    
    errors = []
    
    # 1. Check for mandatory fields in each template
    for tpl in registry.get("templates", []):
        tid = tpl.get("template_id")
        required = ["prediction_binding_id", "primary_dataset", "counterexample_dataset", "null_model", "proxy_metrics", "falsification_vectors"]
        for field in required:
            if field not in tpl:
                errors.append(f"Template '{tid}' missing mandatory field: {field}")
        
        # 2. Verify that counterexample is not the same as primary
        if tpl.get("primary_dataset") == tpl.get("counterexample_dataset"):
            errors.append(f"Template '{tid}' primary and counterexample datasets are identical.")

    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        return False
    
    print("Validation: PASS")
    return True

if __name__ == "__main__":
    if validate_campaign_templates():
        exit(0)
    else:
        exit(1)
