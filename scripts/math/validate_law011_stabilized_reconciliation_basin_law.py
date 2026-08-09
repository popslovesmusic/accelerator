import json
import os

def validate_law011():
    results = {
        "law011_stabilized_reconciliation_basin_law_validation": {
            "status": "pass",
            "checks": [],
            "warnings": [],
            "errors": []
        }
    }

    registry_path = "registry/math/law011_stabilized_reconciliation_basin_law_registry.json"
    law_doc_path = "docs/math/law011_stabilized_reconciliation_basin_law.md"
    result_path = "outputs/math_tests/law011_stabilized_reconciliation_basin_law_result.json"

    # 1. Registry check
    if not os.path.exists(registry_path):
        results["law011_stabilized_reconciliation_basin_law_validation"]["status"] = "fail"
        results["law011_stabilized_reconciliation_basin_law_validation"]["errors"].append("LAW-011 registry missing.")
    else:
        try:
            with open(registry_path, 'r') as f:
                data = json.load(f)
                
                # Check law conditions
                conds = data.get("law_conditions", [])
                if len(conds) < 8:
                    results["law011_stabilized_reconciliation_basin_law_validation"]["status"] = "fail"
                    results["law011_stabilized_reconciliation_basin_law_validation"]["errors"].append(f"Insufficient law conditions: {len(conds)}/8")
                
                # Check failure modes
                fms = data.get("failure_modes_to_preserve", [])
                if len(fms) < 8:
                    results["law011_stabilized_reconciliation_basin_law_validation"]["status"] = "fail"
                    results["law011_stabilized_reconciliation_basin_law_validation"]["errors"].append(f"Insufficient failure modes: {len(fms)}/8")
                
                results["law011_stabilized_reconciliation_basin_law_validation"]["checks"].append("LAW-011 registry content verified.")
        except Exception as e:
            results["law011_stabilized_reconciliation_basin_law_validation"]["status"] = "fail"
            results["law011_stabilized_reconciliation_basin_law_validation"]["errors"].append(f"Registry parse error: {e}")

    # 2. Law document check
    if not os.path.exists(law_doc_path):
        results["law011_stabilized_reconciliation_basin_law_validation"]["status"] = "fail"
        results["law011_stabilized_reconciliation_basin_law_validation"]["errors"].append("LAW-011 document missing.")
    else:
        with open(law_doc_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            required_terms = [
                "{-(i)_α}", "reconciliation event", "basin candidate",
                "persistence condition", "bounded drift", "finite flux",
                "no static attractor", "no global equilibrium"
            ]
            for term in required_terms:
                if term.lower() not in content:
                    results["law011_stabilized_reconciliation_basin_law_validation"]["status"] = "warning"
                    results["law011_stabilized_reconciliation_basin_law_validation"]["warnings"].append(f"Term '{term}' missing from law document.")
        results["law011_stabilized_reconciliation_basin_law_validation"]["checks"].append("LAW-011 document presence and content scanned.")

    # 3. Execution result check
    if not os.path.exists(result_path):
        results["law011_stabilized_reconciliation_basin_law_validation"]["status"] = "fail"
        results["law011_stabilized_reconciliation_basin_law_validation"]["errors"].append("LAW-011 execution result missing.")
    else:
        try:
            with open(result_path, 'r') as f:
                res = json.load(f).get("law011_stabilized_reconciliation_basin_law_result", {})
                if res.get("status") != "success":
                     results["law011_stabilized_reconciliation_basin_law_validation"]["status"] = "fail"
                     results["law011_stabilized_reconciliation_basin_law_validation"]["errors"].append("LAW-011 execution result indicates failure.")
            results["law011_stabilized_reconciliation_basin_law_validation"]["checks"].append("LAW-011 execution result verified.")
        except Exception as e:
            results["law011_stabilized_reconciliation_basin_law_validation"]["status"] = "fail"
            results["law011_stabilized_reconciliation_basin_law_validation"]["errors"].append(f"Result parse error: {e}")

    return results

if __name__ == "__main__":
    res = validate_law011()
    print(json.dumps(res, indent=2))
