import json
import os
import argparse

def validate_rc002_counterexample_obligation(global_reg, target_reg, review_reg):
    results = {
        "rc002_counterexample_obligation_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }

    try:
        with open(global_reg, 'r') as f: g_data = json.load(f).get("proof_candidate_counterexample_obligation", {}).get("obligations", [])
        with open(target_reg, 'r') as f: t_data = json.load(f).get("rc002_counterexample_obligation", {}).get("obligations", [])
        with open(review_reg, 'r') as f: r_data = json.load(f).get("rc002_counterexample_review", {}).get("reviews", [])
    except Exception as e:
        results["rc002_counterexample_obligation_validation"]["status"] = "fail"
        results["rc002_counterexample_obligation_validation"]["errors"].append(f"Load error: {e}")
        return results

    # Consistency check: CEO-RC002-01
    g_ceo = next((o for o in g_data if o["obligation_id"] == "CEO-RC002-01"), None)
    t_ceo = next((o for o in t_data if o["id"] == "CEO-RC002-01"), None)
    r_ceo = next((r for r in r_data if r["obligation_id"] == "CEO-RC002-01"), None)

    if not g_ceo or not t_ceo or not r_ceo:
        results["rc002_counterexample_obligation_validation"]["status"] = "fail"
        results["rc002_counterexample_obligation_validation"]["errors"].append("CEO-RC002-01 missing from one or more registries.")
        return results

    if g_ceo["status"] != t_ceo["status"]:
        results["rc002_counterexample_obligation_validation"]["status"] = "fail"
        results["rc002_counterexample_obligation_validation"]["errors"].append(f"Status mismatch between global ({g_ceo['status']}) and target ({t_ceo['status']}) registries.")

    if t_ceo["status"] == "discharged" and r_ceo["status"] not in ["discharged_by_existing_boundary_condition", "discharged_by_existing_failure_mode"]:
        results["rc002_counterexample_obligation_validation"]["status"] = "fail"
        results["rc002_counterexample_obligation_validation"]["errors"].append(f"Discharge claimed in tracker but review status is {r_ceo['status']}.")

    results["rc002_counterexample_obligation_validation"]["checks"].append("CEO-RC002-01 registry consistency verified.")
    
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate RC-002 counterexample obligation.")
    parser.add_argument("--global_reg", default="registry/math/proof_candidate_counterexample_obligation_registry.json")
    parser.add_argument("--target_reg", default="registry/math/rc002_counterexample_obligation_registry.json")
    parser.add_argument("--review_reg", default="registry/math/rc002_counterexample_review_registry.json")
    
    args = parser.parse_args()
    res = validate_rc002_counterexample_obligation(args.global_reg, args.target_reg, args.review_reg)
    print(json.dumps(res, indent=2))
