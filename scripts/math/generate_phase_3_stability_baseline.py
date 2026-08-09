import json
import os
import argparse
from datetime import datetime

def generate_phase_3_stability_baseline_report(baseline_reg, pert_reg, failure_reg):
    try:
        with open(baseline_reg, 'r') as f: baseline_data = json.load(f)
        with open(pert_reg, 'r') as f: pert_data = json.load(f)
        with open(failure_reg, 'r') as f: failure_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    report = {
        "phase_3_formal_stability_baseline_report": {
            "timestamp": datetime.now().isoformat(),
            "status": "phase_3_baseline_established",
            "summary": "Unified Phase 3 formal stability baseline across recursive operator systems and theorem scaffolds.",
            "perturbation_classes": pert_data.get("perturbation_classes", []),
            "baseline_tests": []
        }
    }

    for entry in baseline_data.get("baseline_tests", []):
        entry_report = {
            "test_id": entry["test_id"],
            "target": entry["target"],
            "domain": entry["domain"],
            "perturbation_class": entry["perturbation_class"],
            "expected_behavior": entry["expected_behavior"],
            "known_instability_modes": entry["failure_modes"],
            "readiness": entry["proof_status"]
        }
        report["phase_3_formal_stability_baseline_report"]["baseline_tests"].append(entry_report)

    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate unified Phase 3 stability baseline report.")
    parser.add_argument("--baseline", default="registry/math/phase_3_stability_baseline_registry.json")
    parser.add_argument("--perturbations", default="registry/math/phase_3_perturbation_test_registry.json")
    parser.add_argument("--failures", default="registry/math/phase_3_recursive_failure_modes.json")
    parser.add_argument("--out", help="Path to save Phase 3 baseline report.")
    
    args = parser.parse_args()
    report = generate_phase_3_stability_baseline_report(args.baseline, args.perturbations, args.failures)
    
    if args.out:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Phase 3 stability baseline report saved to {args.out}")
    else:
        print(json.dumps(report, indent=2))
