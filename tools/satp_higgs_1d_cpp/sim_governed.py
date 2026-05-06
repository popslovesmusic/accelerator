import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Governed wrapper for SATP+Higgs 1D Engine (C++)")
    parser.add_argument("--config", type=Path, required=True, help="Path to config JSON")
    parser.add_argument("--out", type=Path, required=True, help="Output directory")
    args = parser.parse_args()

    # Load config
    with open(args.config, 'r') as f:
        config = json.load(f)

    # Ensure output directory exists
    args.out.mkdir(parents=True, exist_ok=True)

    # Path to dase_cli and oneAPI setvars
    cli_path = r"D:\projects\acellorator\tools\Simulation_engines_extracted_2026-04-25\bin\uhd770\dase_cli_json_uhd770.exe"
    setvars_path = r"C:\Program Files (x86)\Intel\oneAPI\setvars.bat"
    
    # Run commands via stdin with oneAPI environment
    full_cmd = f'call "{setvars_path}" >nul 2>&1 && "{cli_path}"'

    process = subprocess.Popen(
        full_cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=True
    )

    outputs = []
    
    # 1. Create Engine
    create_cmd = {"command": "create_engine", "params": {
        "engine_type": "satp_higgs_1d",
        "num_nodes": config.get("num_nodes", 1024)
    }}
    process.stdin.write(json.dumps(create_cmd) + "\n")
    process.stdin.flush()
    line = process.stdout.readline()
    engine_id = None
    if line:
        try:
            out = json.loads(line)
            outputs.append(out)
            if "result" in out and "engine_id" in out["result"]:
                engine_id = out["result"]["engine_id"]
        except json.JSONDecodeError:
            print(f"Warning: Could not decode line: {line}")

    if engine_id:
        # 2. Run Mission
        run_cmd = {"command": "run_mission", "params": {
            "engine_id": engine_id,
            "num_steps": config.get("steps", 1000)
        }}
        process.stdin.write(json.dumps(run_cmd) + "\n")
        process.stdin.flush()
        line = process.stdout.readline()
        if line:
            try: outputs.append(json.loads(line))
            except: pass

        # 3. Get Metrics
        metrics_cmd = {"command": "get_metrics", "params": {"engine_id": engine_id}}
        process.stdin.write(json.dumps(metrics_cmd) + "\n")
        process.stdin.flush()
        line = process.stdout.readline()
        if line:
            try: outputs.append(json.loads(line))
            except: pass

        # 4. Destroy Engine
        destroy_cmd = {"command": "destroy_engine", "params": {"engine_id": engine_id}}
        process.stdin.write(json.dumps(destroy_cmd) + "\n")
        process.stdin.flush()
        line = process.stdout.readline()
        if line:
            try: outputs.append(json.loads(line))
            except: pass
    else:
        print("Error: Could not obtain engine_id from create_engine")

    process.stdin.close()
    process.wait()

    # Save outputs
    with open(args.out / "raw_outputs.json", 'w') as f:
        json.dump(outputs, f, indent=2)

    # Extract metrics for the final report
    metrics = {
        "phi_rms": 0.0,
        "h_rms": 0.0,
        "status": "success" if process.returncode == 0 else "failed"
    }

    for out in outputs:
        if out.get("command") == "get_metrics":
            if "result" in out:
                res = out["result"]
                # Extract all scientific and performance metrics from result
                metrics.update(res)
                if "metrics" in res:
                    metrics.update(res["metrics"])
            elif "metrics" in out:
                metrics.update(out["metrics"])

    with open(args.out / "metrics.json", 'w') as f:
        json.dump(metrics, f, indent=2)

    print(f"Simulation complete. Outputs in {args.out}")

if __name__ == "__main__":
    main()
