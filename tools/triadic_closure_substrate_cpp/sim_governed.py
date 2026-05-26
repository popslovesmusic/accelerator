import argparse
import json
import subprocess
import sys
import os

def main():
    parser = argparse.ArgumentParser(description="Triadic Closure Substrate Engine Wrapper")
    parser.add_argument("--config", type=str, required=True, help="Path to config JSON")
    parser.add_argument("--out", type=str, required=True, help="Output directory")
    args = parser.parse_args()

    # Load config
    try:
        with open(args.config, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Config file not found at {args.config}")
        sys.exit(1)

    # Extract params
    triads = config.get("triads", 256)
    steps = config.get("steps", 1000)
    dt = config.get("dt", 0.01)
    floor = config.get("floor", 0.05)
    dyad_mode = config.get("dyad_mode", False)
    disable_residue = config.get("disable_residue", False)
    disable_recursive = config.get("disable_recursive", False)
    seed = config.get("seed", 42)

    # Prepare output path
    os.makedirs(args.out, exist_ok=True)
    summary_path = os.path.join(args.out, "summary.json")

    # Locate executable
    exe_path = os.path.join(os.path.dirname(__file__), "triadic_sim.exe")
    if not os.path.exists(exe_path):
        print(f"Error: Executable not found at {exe_path}. Did you build it?")
        sys.exit(1)

    # Execute
    cmd = [
        exe_path,
        "--triads", str(triads),
        "--steps", str(steps),
        "--dt", str(dt),
        "--floor", str(floor),
        "--seed", str(seed),
        "--out", summary_path
    ]
    
    if dyad_mode: cmd.append("--dyad-mode")
    if disable_residue: cmd.append("--disable-residue")
    if disable_recursive: cmd.append("--disable-recursive")
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Engine execution failed!")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        sys.exit(result.returncode)

    print(result.stdout)
    print(f"Simulation complete. Outputs saved to {args.out}")

if __name__ == "__main__":
    main()
