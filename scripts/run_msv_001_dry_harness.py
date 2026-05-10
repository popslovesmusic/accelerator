import os
import json
import subprocess
import shutil

def create_mock_output(run_dir, config):
    """
    Generate mock output skeletons for MSV-001 validation.
    """
    data_dir = os.path.join(run_dir, "data")
    artifacts_dir = os.path.join(run_dir, "artifacts")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(artifacts_dir, exist_ok=True)

    # 1. config.json (Source of truth for runtime validator check)
    with open(os.path.join(data_dir, "config.json"), 'w') as f:
        json.dump(config, f, indent=2)

    # 2. JSON Outputs in data/
    json_outputs = [
        "run_metadata.json",
        "config_snapshot.json",
        "summary.json",
        "metrics.json",
        "operator_trace.json",
        "falsification_report.json",
        "provenance_manifest.json"
    ]
    for filename in json_outputs:
        with open(os.path.join(data_dir, filename), 'w') as f:
            json.dump({"mock": True, "status": "generated_by_dry_run"}, f)

    # 3. CSV Outputs in artifacts/
    csv_outputs = [
        "minimizer_switch_trace.csv",
        "ref_equivalence_trace.csv",
        "recoupling_trace.csv"
    ]
    for filename in csv_outputs:
        with open(os.path.join(artifacts_dir, filename), 'w') as f:
            f.write("step,mock_data\n0,1\n")

def run_dry_harness():
    index_path = "experiments/msv_001/configs/msv_001_reference_config_index.json"
    dry_run_root = "experiments/msv_001/dry_runs"
    
    if not os.path.exists(index_path):
        print(f"Error: Reference index {index_path} not found.")
        return

    with open(index_path, 'r') as f:
        index = json.load(f)

    for entry in index.get("configs", []):
        config_id = entry["config_id"]
        config_path = entry["path"]
        print(f"\n--- Dry-run for {config_id} ---")

        if not os.path.exists(config_path):
            print(f"Error: Config {config_path} not found.")
            continue

        with open(config_path, 'r') as f:
            config = json.load(f)

        run_dir = os.path.join(dry_run_root, config_id)
        if os.path.exists(run_dir):
            shutil.rmtree(run_dir)
        os.makedirs(run_dir)

        create_mock_output(run_dir, config)
        print(f"Mock outputs generated in {run_dir}")

        # Run the runtime validator
        print(f"Executing runtime validator for {config_id}...")
        try:
            # Note: validate_msv_001_run.py expects run_dir
            # It looks for data/ and artifacts/ inside it
            result = subprocess.run(
                ["python", "scripts/validate_msv_001_run.py", run_dir],
                capture_output=True,
                text=True
            )
            print(result.stdout)
            if result.stderr:
                print(f"Errors: {result.stderr}")
        except Exception as e:
            print(f"Failed to execute validator: {e}")

if __name__ == "__main__":
    run_dry_harness()
