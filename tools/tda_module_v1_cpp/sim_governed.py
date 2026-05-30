import os
import subprocess
import argparse
from pathlib import Path

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    
    os.makedirs(args.out, exist_ok=True)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # TDA v1 cpp often produces tda_benchmark.exe or similar
    exe_path = os.path.join(script_dir, "tda_benchmark.exe")
    # Check if it exists, fallback to tda_v1.exe if not
    if not os.path.exists(exe_path):
        exe_path = os.path.join(script_dir, "tda_v1.exe")
        
    config_path = os.path.abspath(args.config)
    out_dir = os.path.abspath(args.out)
    
    setvars = r"C:\Program Files (x86)\Intel\oneAPI\setvars.bat"
    full_cmd = f'call "{setvars}" && "{exe_path}" --config "{config_path}" --out "{out_dir}"'
    
    print(f"Executing: {full_cmd}")
    subprocess.run(full_cmd, check=True, shell=True)

if __name__ == "__main__":
    run()
