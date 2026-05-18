import os
import subprocess
import argparse
import json
from pathlib import Path

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    
    os.makedirs(args.out, exist_ok=True)
    
    script_dir = Path(__file__).parent.resolve()
    exe_path = script_dir / "rd_sim.exe"
    config_path = os.path.abspath(args.config)
    out_dir = os.path.abspath(args.out)
    
    if not exe_path.exists():
        # Try fallback names or locations
        fallback = script_dir / "rd_sim_benchmark.exe"
        if fallback.exists():
            exe_path = fallback
        else:
            raise FileNotFoundError(f"Could not find rd_sim.exe or rd_sim_benchmark.exe in {script_dir}")
    
    exe_path = str(exe_path.resolve())
    
    setvars = r"C:\Program Files (x86)\Intel\oneAPI\setvars.bat"
    # Use a single string with shell=True, and let cmd handle the quotes
    full_cmd = f'call "{setvars}" && "{exe_path}" --config "{config_path}" --out "{out_dir}"'
    
    print(f"Executing: {full_cmd}")
    subprocess.run(full_cmd, check=True, shell=True)

if __name__ == "__main__":
    run()
