import json
import os
import argparse
from datetime import datetime

def generate_stability_baseline_report(baseline_reg, metric_reg, failure_reg):
    try:
        with open(baseline_reg, 'r') as f: baseline_data = json.load(f)
        with open(metric_reg, 'r') as f: metric_data = json.load(f)
        with open(failure_reg, 'r') as f: failure_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    report = {
        "operational_stability_baseline_report": {
            "timestamp": datetime.now().isoformat(),
            "status": "baseline_established",
            "summary": "Unified Phase 2 operational-stability baseline across scaffolded operators and theorems.",
            "metrics": metric_data.get("stability_metrics", []),
            "classifications": []
        }
    }

    for entry in baseline_data.get("baseline_entries", []):
        entry_report = {
            "target": entry["target"],
            "stability_class": entry["expected_class"],
            "metrics_applied": entry["associated_metrics"],
            "known_instability_modes": entry["failure_modes"],
            "readiness": entry["proof_status"]
        }
        report["operational_stability_baseline_report"]["classifications"].append(entry_report)

    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate unified stability baseline report.")
    parser.add_argument("--baseline", default="registry/math/operational_stability_baseline_registry.json")
    parser.add_argument("--metrics", default="registry/math/stability_metric_registry.json")
    parser.add_argument("--failures", default="registry/math/stability_failure_mode_registry.json")
    parser.add_argument("--out", help="Path to save baseline report.")
    
    args = parser.parse_args()
    report = generate_stability_baseline_report(args.baseline, args.metrics, args.failures)
    
    if args.out:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Stability baseline report saved to {args.out}")
    else:
        print(json.dumps(report, indent=2))
