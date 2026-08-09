import json
import os
import argparse
from datetime import datetime

def generate_symbolic_reduction_report(chain_reg, rule_reg, failure_reg):
    try:
        with open(chain_reg, 'r') as f: chain_data = json.load(f)
        with open(rule_reg, 'r') as f: rule_data = json.load(f)
        with open(failure_reg, 'r') as f: failure_data = json.load(f)
    except Exception as e:
        return {"error": f"Load error: {e}"}

    report = {
        "symbolic_reduction_chain_report": {
            "timestamp": datetime.now().isoformat(),
            "status": "baseline_established",
            "summary": "Unified Phase 2 symbolic reduction-chain baseline across scaffolded operators and theorems.",
            "reduction_rules": rule_data.get("reduction_rules", []),
            "classifications": []
        }
    }

    for entry in chain_data.get("reduction_entries", []):
        entry_report = {
            "target": entry["target"],
            "reduction_class": entry["expected_reduction_class"],
            "rules_applied": entry["rules_applied"],
            "known_failure_modes": entry["failure_modes"],
            "readiness": entry["proof_status"]
        }
        report["symbolic_reduction_chain_report"]["classifications"].append(entry_report)

    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate unified symbolic reduction report.")
    parser.add_argument("--chains", default="registry/math/symbolic_reduction_chain_registry.json")
    parser.add_argument("--rules", default="registry/math/reduction_rule_registry.json")
    parser.add_argument("--failures", default="registry/math/reduction_failure_mode_registry.json")
    parser.add_argument("--out", help="Path to save reduction report.")
    
    args = parser.parse_args()
    report = generate_symbolic_reduction_report(args.chains, args.rules, args.failures)
    
    if args.out:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Symbolic reduction report saved to {args.out}")
    else:
        print(json.dumps(report, indent=2))
