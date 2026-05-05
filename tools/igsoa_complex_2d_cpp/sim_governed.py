import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Governed wrapper for IGSOA Complex Lattice Engine (2D C++)")
    parser.add_argument("--config", type=Path, required=True, help="Path to config JSON")
    parser.add_argument("--out", type=Path, required=True, help="Output directory")
    args = parser.parse_args()

    # Load config
    with open(args.config, 'r') as f:
        config = json.load(f)

    # Ensure output directory exists
    args.out.mkdir(parents=True, exist_ok=True)

    # Path to dase_cli and oneAPI setvars
    cli_path = r"D:\projects\acellorator\tools\Simulation_engines_extracted_2026-04-25\build_cli\Release\dase_cli_json.exe"
    setvars_path = r"C:\Program Files (x86)\Intel\oneAPI\setvars.bat"
    
    # Prepare dase_cli commands
    commands = [
        {"command": "create_engine", "params": {
            "engine_type": "igsoa_complex_2d",
            "N_x": config.get("nx", 64),
            "N_y": config.get("ny", 64),
            "R_c": config.get("R_c", 2.5),
            "kappa": config.get("kappa", 1.0)
        }},
        {"command": "run_mission", "params": {
            "engine_id": "engine_000",
            "num_steps": config.get("steps", 1000)
        }},
        {"command": "get_metrics", "params": {"engine_id": "engine_000"}},
        {"command": "destroy_engine", "params": {"engine_id": "engine_000"}}
    ]

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
    for cmd in commands:
        process.stdin.write(json.dumps(cmd) + "\n")
        process.stdin.flush()
        line = process.stdout.readline()
        if line:
            try:
                outputs.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"Warning: Could not decode line: {line}")

    process.stdin.close()
    process.wait()

    # Save outputs
    with open(args.out / "raw_outputs.json", 'w') as f:
        json.dump(outputs, f, indent=2)

    # Extract metrics
    metrics = {
        "mean_phi": 0.0,
        "psi_squared_mean": 0.0,
        "entropy_rate": 0.0,
        "status": "success" if process.returncode == 0 else "failed"
    }

    for out in outputs:
        if out.get("command") == "get_metrics" and "result" in out:
            res = out["result"]
            if "metrics" in res:
                metrics.update(res["metrics"])
        elif out.get("command") == "get_metrics" and "metrics" in out:
            # Fallback for older format if still present
            metrics.update(out["metrics"])

    with open(args.out / "metrics.json", 'w') as f:
        json.dump(metrics, f, indent=2)

    print(f"Simulation complete. Outputs in {args.out}")

if __name__ == "__main__":
    main()
