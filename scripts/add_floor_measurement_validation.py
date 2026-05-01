import os
import json
import pandas as pd
import subprocess
import datetime

RUN_ID = "research_floor_convergence_2026-05-01"
OUTPUT_ROOT = f"outputs/runs/{RUN_ID}"
MEASURE_DIR = f"{OUTPUT_ROOT}/measurement_validation"

os.makedirs(MEASURE_DIR, exist_ok=True)

def pde_json_to_csv(json_path, csv_path):
    with open(json_path, "r") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)
    return csv_path

def run_spectral_analysis(label, csv_path, col_name):
    print(f"[{datetime.datetime.now()}] [Spectral] Analyzing {label}...")
    out_dir = f"{MEASURE_DIR}/spectral_{label}"
    os.makedirs(out_dir, exist_ok=True)
    
    cmd = [
        "python", "tools/spectral_analysis_v1/analyze_spectrum.py",
        "--mode", "temporal",
        "--file", csv_path,
        "--col", col_name,
        "--out", out_dir
    ]
    
    subprocess.run(cmd)
    
    report_path = f"{out_dir}/spectrum_report.json"
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            return json.load(f)
    return None

def main():
    # 1. Analyze CA Floor Stability
    ca_csv = f"{OUTPUT_ROOT}/jobs/ca_extreme_rg_0.1_seed_1/metrics.csv"
    ca_spectral = run_spectral_analysis("ca_floor", ca_csv, "mean_mismatch")
    
    # 2. Analyze PDE Floor Stability
    # We need to find the nested diagnostics.json
    pde_job_dir = f"{OUTPUT_ROOT}/jobs/pde_extreme_kappa_0.5_seed_10"
    nested_dir = f"{pde_job_dir}/{pde_job_dir}"
    pde_json = f"{nested_dir}/diagnostics.json"
    pde_csv = f"{MEASURE_DIR}/pde_metrics.csv"
    
    if os.path.exists(pde_json):
        pde_json_to_csv(pde_json, pde_csv)
        pde_spectral = run_spectral_analysis("pde_floor", pde_csv, "epsilon_mean")
    else:
        print(f"Error: PDE diagnostics not found at {pde_json}")
        pde_spectral = None
    
    results = {
        "timestamp": datetime.datetime.now().isoformat(),
        "ca_spectral": ca_spectral,
        "pde_spectral": pde_spectral
    }
    
    with open(f"{MEASURE_DIR}/measurement_report.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"Measurement validation complete. Report saved to {MEASURE_DIR}/measurement_report.json")

if __name__ == "__main__":
    main()
