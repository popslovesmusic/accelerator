import argparse
import json
import subprocess
import sys
import os

def main():
    parser = argparse.ArgumentParser(description="Triadic Closure Substrate Engine Wrapper (Final Campaign Edition)")
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
    units = config.get("units", config.get("triads", 256))
    steps = config.get("steps", 1000)
    dt = config.get("dt", 0.01)
    floor = config.get("floor", 0.05)
    seed = config.get("seed", 42)
    backend = config.get("backend", "avx2")
    structure = config.get("structure", "triad")

    # Prepare output path
    os.makedirs(args.out, exist_ok=True)
    summary_path = os.path.normpath(os.path.join(args.out, "summary.json"))

    # Locate executable
    exe_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "triadic_sim.exe"))
    if not os.path.exists(exe_path):
        print(f"Error: Executable not found at {exe_path}. Did you build it?")
        sys.exit(1)

    # Build command list
    cmd = [
        f'"{exe_path}"',
        "--units", str(units),
        "--steps", str(steps),
        "--dt", str(dt),
        "--floor", str(floor),
        "--seed", str(seed),
        "--backend", str(backend),
        "--structure", str(structure),
        "--out", f'"{summary_path}"'
    ]
    
    # Falsification Flags
    flags = [
        "residue_shuffle", "residue_nullify", "recursive_cut", "orientation_scramble",
        "floor_randomize", "topology_randomize", "saturation_attack", "coupling_nullify",
        "boundary_fracture", "topology_freeze", "admissibility_lock", "residue_delay",
        "coupling_symmetry", "boundary_randomize", "topology_noise_flood"
    ]
    for flag in flags:
        if config.get(flag):
            cmd.append(f"--{flag.replace('_', '-')}")

    # Rates and Intervals
    rates = ["topology_rewire_rate", "admissibility_adapt_rate", "residue_diffusion_rate"]
    for rate in rates:
        if rate in config:
            cmd.extend([f"--{rate.replace('_', '-')}", str(config[rate])])
    
    if "sync_interval" in config:
        cmd.extend(["--sync-interval", str(config["sync_interval"])])

    env = os.environ.copy()
    setvars_path = r"C:\Program Files (x86)\Intel\oneAPI\setvars.bat"
    
    if os.path.exists(setvars_path):
        cmd_str = f'"{setvars_path}" --force >nul && {" ".join(cmd)}'
    else:
        cmd_str = " ".join(cmd)
        
    result = subprocess.run(cmd_str, capture_output=True, text=True, shell=True, env=env)
    
    if result.returncode != 0:
        print("Engine execution failed!")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        sys.exit(result.returncode)

    print(result.stdout)
    print(f"Simulation complete. Outputs saved to {args.out}")

if __name__ == "__main__":
    main()
