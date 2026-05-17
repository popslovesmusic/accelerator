import json
import os
import argparse
from datetime import datetime

def index_equivalence_failure(failure_data):
    registry_path = "registry/equivalence_failure_registry.json"
    
    if not os.path.exists(registry_path):
        print(f"Error: {registry_path} missing.")
        return

    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)

    # Standardize failure entry
    entry = {
        "failure_id": f"FAIL-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "tool_name": failure_data.get("tool_name"),
        "reference_baseline": failure_data.get("reference_baseline"),
        "failure_class": failure_data.get("failure_class"),
        "seed": failure_data.get("seed"),
        "metric_divergence": failure_data.get("metric_divergence"),
        "artifact_path": failure_data.get("artifact_path"),
        "governance_boilerplate": {
            "source_relation": "(E≠0) ⇔R δ(E>0)",
            "non_separability_acknowledged": True
        }
    }

    registry["failure_records"].append(entry)

    with open(registry_path, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2)
    
    print(f"Successfully indexed failure {entry['failure_id']} for tool {entry['tool_name']}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Index implementation-equivalence failures.")
    parser.add_argument("--tool", required=True, help="Name of the tool that failed.")
    parser.add_argument("--ref", required=True, help="Name of the reference baseline.")
    parser.add_argument("--fclass", required=True, help="Class of the failure.")
    parser.add_argument("--seed", type=int, help="Seed that caused the failure.")
    parser.add_argument("--divergence", type=float, help="Magnitude of the metric divergence.")
    parser.add_argument("--artifact", help="Path to the archived failure artifact.")

    args = parser.parse_args()

    data = {
        "tool_name": args.tool,
        "reference_baseline": args.ref,
        "failure_class": args.fclass,
        "seed": args.seed,
        "metric_divergence": args.divergence,
        "artifact_path": args.artifact
    }

    index_equivalence_failure(data)
