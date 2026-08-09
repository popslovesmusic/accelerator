import json
import os
import argparse
from datetime import datetime

def index_evidence_negative_result(failure_data):
    registry_path = "registry/evidence_negative_result_registry.json"
    
    if not os.path.exists(registry_path):
        print(f"Error: {registry_path} missing.")
        return

    with open(registry_path, 'r') as f:
        registry = json.load(f)

    # Standardize failure entry
    entry = {
        "result_id": f"EC-NEG-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "campaign_id": failure_data.get("campaign_id"),
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

    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2)
    
    print(f"Successfully indexed negative evidence {entry['result_id']} for campaign {entry['campaign_id']}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Index negative or null campaign results.")
    parser.add_argument("--campaign", required=True, help="ID of the campaign.")
    parser.add_argument("--fclass", required=True, help="Class of the failure.")
    parser.add_argument("--verdict", default="NULL_SUPPORT", help="Verdict of the campaign.")
    parser.add_argument("--packet", help="Path to the evidence packet.")

    args = parser.parse_args()

    data = {
        "campaign_id": args.campaign,
        "failure_class": args.fclass,
        "verdict": args.verdict,
        "packet_path": args.packet
    }

    index_evidence_negative_result(data)
