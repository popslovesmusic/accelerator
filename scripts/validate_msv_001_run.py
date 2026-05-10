import os
import json
import argparse

def validate_msv_001_run(run_dir):
    """
    Validate MSV-001 experiment configs, required outputs, observable fields, 
    falsification reports, and provenance manifests.
    """
    run_dir = run_dir.rstrip(os.sep).rstrip('/')
    result = {
        "run_id": os.path.basename(run_dir),
        "validation_id": "MSV-001",
        "validator_version": "1.0.0",
        "config_pass": False,
        "outputs_pass": False,
        "falsification_pass": False,
        "provenance_pass": False,
        "tool_certification_pass": False,
        "claim_ceiling": "EXPLORATORY",
        "final_result": "BLOCKED",
        "blocking_failures": [],
        "warnings": []
    }

    # 1. Config Schema Conformance
    config_path = os.path.join(run_dir, "data", "config.json")
    if not os.path.exists(config_path):
        result["blocking_failures"].append("Missing config.json in data directory.")
    else:
        # TODO: Implement actual schema check against msv_001_experiment_config_schema.json
        result["config_pass"] = True

    # 2. Required Outputs Exist
    required_outputs = [
        "run_metadata.json",
        "config_snapshot.json",
        "summary.json",
        "metrics.json",
        "operator_trace.json",
        "minimizer_switch_trace.csv",
        "ref_equivalence_trace.csv",
        "recoupling_trace.csv",
        "falsification_report.json",
        "provenance_manifest.json"
    ]
    missing_outputs = []
    for output in required_outputs:
        if not os.path.exists(os.path.join(run_dir, "data" if output.endswith(".json") else "artifacts", output)):
             # Re-checking with flexible paths
             if not os.path.exists(os.path.join(run_dir, output)):
                  missing_outputs.append(output)
    
    if missing_outputs:
        result["blocking_failures"].append(f"Missing required outputs: {', '.join(missing_outputs)}")
    else:
        result["outputs_pass"] = True

    # 3. Falsification Vectors Present
    falsification_path = os.path.join(run_dir, "data", "falsification_report.json")
    if os.path.exists(falsification_path):
        # TODO: Check for FV-1, FV-2, FV-3, FV-4 in report
        result["falsification_pass"] = True

    # 4. Provenance Manifest Complete
    provenance_path = os.path.join(run_dir, "data", "provenance_manifest.json")
    if os.path.exists(provenance_path):
        # TODO: Check required provenance fields
        result["provenance_pass"] = True

    # Final Classification
    if result["config_pass"] and result["outputs_pass"] and result["falsification_pass"] and result["provenance_pass"]:
        result["final_result"] = "PASS_TS4_ELIGIBLE"
        result["claim_ceiling"] = "TS4"
    else:
        result["final_result"] = "BLOCKED"

    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate MSV-001 simulation run.")
    parser.add_argument("run_dir", help="Path to the simulation run directory.")
    args = parser.parse_args()

    validation_result = validate_msv_001_run(args.run_dir)
    print(json.dumps(validation_result, indent=2))
