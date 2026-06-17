import os
import json
import argparse
import subprocess
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Governed wrapper for TDA Module v2 (C++)")
    parser.add_argument("--config", required=True, help="Path to config JSON")
    parser.add_argument("--out", required=True, help="Output directory")
    args = parser.parse_args()
    
    with open(args.config, 'r') as f:
        config = json.load(f)
        
    os.makedirs(args.out, exist_ok=True)
    
    # Path to binary
    exe_path = Path(__file__).parent / "tda_multi_benchmark.exe"
    
    # Use oneAPI if available
    setvars = r"C:\Program Files (x86)\Intel\oneAPI\setvars.bat"
    
    # Construct CLI command
    # Default to spatial mode
    mode = config.get("mode", "spatial")
    grid_file = config.get("grid_csv")
    threshold = config.get("threshold", 0.5)
    
    cmd = f'"{exe_path}" --mode {mode} --file "{grid_file}" --threshold {threshold} --out "{args.out}"'
    
    if os.path.exists(setvars):
        full_cmd = f'call "{setvars}" >nul 2>&1 && {cmd}'
    else:
        full_cmd = cmd
        
    print(f"Executing: {full_cmd}")
    subprocess.run(full_cmd, shell=True, check=True)
    
    # Extract results and write metrics.json
    # Matches main.cpp output: tda_report_v2.json
    report_path = Path(args.out) / "tda_report_v2.json"
    if report_path.exists():
        with open(report_path, 'r') as f:
            report = json.load(f)
            # Extract topology metrics
            metrics = report.get("topology", {})
            # If landscape mode
            if not metrics and "persistence_landscape" in report:
                metrics = report["persistence_landscape"][-1] # Take last step
            
            with open(Path(args.out) / "metrics.json", 'w') as mf:
                json.dump(metrics, mf, indent=2)

if __name__ == "__main__":
    main()
