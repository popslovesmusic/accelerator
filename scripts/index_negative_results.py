import json
import os
import argparse
from datetime import datetime

def index_negative_result(failure_data):
    registry_path = "registry/negative_result_registry.json"
    
    if not os.path.exists(registry_path):
        print(f"Error: {registry_path} missing.")
        return

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)

    # Standardize failure entry
    entry = {
        "result_id": f"NEG-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "dataset_id": failure_data.get("dataset_id"),
        "prediction_binding_id": failure_data.get("prediction_binding_id"),
        "failure_class": failure_data.get("failure_class"),
        "verdict": failure_data.get("verdict"),
        "packet_path": failure_data.get("packet_path"),
        "governance_boilerplate": {
            "source_relation": "(E≠0) ⇔R δ(E>0)",
            "non_separability_acknowledged": True,
            "required_statement": "Observed signatures are interpreted only through restricted local analog structure."
        }
    }

    registry["negative_results"].append(entry)

    with open(registry_path, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2)
    
    print(f"Successfully indexed negative result {entry['result_id']} for dataset {entry['dataset_id']}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Index negative or null dataset evidence results.")
    parser.add_argument("--dataset", required=True, help="ID of the dataset.")
    parser.add_argument("--binding", required=True, help="ID of the prediction binding.")
    parser.add_argument("--fclass", required=True, help="Class of the failure.")
    parser.add_argument("--verdict", default="NULL_SUPPORT", help="Verdict of the campaign.")
    parser.add_argument("--packet", help="Path to the evidence packet.")

    args = parser.parse_args()

    data = {
        "dataset_id": args.dataset,
        "prediction_binding_id": args.binding,
        "failure_class": args.fclass,
        "verdict": args.verdict,
        "packet_path": args.packet
    }

    index_negative_result(data)
