import os
import subprocess
import json
import datetime

RUN_ID = "research_one_process_stability_2026-05-01"
OUTPUT_ROOT = f"outputs/runs/{RUN_ID}"
MEASURE_DIR = f"{OUTPUT_ROOT}/measurement_validation"

os.makedirs(MEASURE_DIR, exist_ok=True)

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
    # 1. Analyze CA stability
    ca_csv = f"{OUTPUT_ROOT}/jobs/ca_rg_0.1_seed_1/metrics.csv"
    ca_spectral = run_spectral_analysis("ca_stability", ca_csv, "active_fraction")
    
    # 2. Analyze ABM stability
    abm_csv = f"{OUTPUT_ROOT}/jobs/abm_mr_0.05_seed_1/metrics.csv"
    abm_spectral = run_spectral_analysis("abm_stability", abm_csv, "order_parameter")
    
    results = {
        "timestamp": datetime.datetime.now().isoformat(),
        "ca_spectral": ca_spectral,
        "abm_spectral": abm_spectral
    }
    
    with open(f"{MEASURE_DIR}/measurement_report.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"Measurement validation complete. Report saved to {MEASURE_DIR}/measurement_report.json")

if __name__ == "__main__":
    main()
