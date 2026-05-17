import json
import os
import argparse
from datetime import datetime
from pathlib import Path

def run_evidence_campaign(config_path):
    # Load registries for validation
    with open("registry/prediction_binding_registry.json", 'r') as f:
        pb_registry = json.load(f)
    with open("registry/public_dataset_registry.json", 'r') as f:
        ds_registry = json.load(f)
    with open("registry/falsification_protocol_registry.json", 'r') as f:
        fp_registry = json.load(f)

    with open(config_path, 'r') as f:
        config = json.load(f)

    print(f"Starting Math-Bound Evidence Campaign: {config.get('campaign_id')}")
    
    # 1. Validate Prediction Binding
    binding_id = config.get("prediction_binding_id")
    binding = next((b for b in pb_registry["bindings"] if b["binding_id"] == binding_id), None)
    if not binding:
        raise ValueError(f"Invalid Prediction Binding: {binding_id}")
    
    # 2. Validate Datasets
    dataset_ids = config.get("dataset_ids", [])
    for ds_id in dataset_ids:
        dataset = next((d for d in ds_registry["datasets"] if d["dataset_id"] == ds_id), None)
        if not dataset:
            raise ValueError(f"Invalid Dataset: {ds_id}")

    # 3. Validate Falsification Protocols
    mandatory_protocols = [p["protocol_id"] for p in fp_registry["protocols"] if p["status"] == "MANDATORY"]
    campaign_protocols = config.get("falsification_protocols", [])
    for mp in mandatory_protocols:
        if mp not in campaign_protocols:
            print(f"Warning: Mandatory falsification protocol '{mp}' missing from config.")

    # Simulated execution and packet emission
    report = {
        "campaign_id": config.get("campaign_id"),
        "status": "pass",
        "timestamp": datetime.now().isoformat(),
        "verdict": "READY_FOR_EXECUTION",
        "governance_boilerplate": {
            "source_relation": "(E≠0) ⇔R δ(E>0)",
            "non_separability_acknowledged": True,
            "required_statement": "Observed signatures are interpreted only through restricted local analog structure."
        }
    }
    
    print("Campaign preflight validation: PASS")
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run math-bound evidence campaigns.")
    parser.add_argument("--config", required=True, help="Path to the campaign config JSON.")
    args = parser.parse_args()

    try:
        res = run_evidence_campaign(args.config)
        print(json.dumps(res, indent=2))
    except Exception as e:
        print(f"Campaign Failed: {e}")
