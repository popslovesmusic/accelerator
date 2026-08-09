import os
import json
import subprocess
import pandas as pd
import numpy as np
import datetime
from pathlib import Path

# Metadata
RUN_ID = "research_resolution_falsification_2026-05-03"
OUTPUT_ROOT = Path(f"outputs/runs/{RUN_ID}")
LOGS_DIR = OUTPUT_ROOT / "logs"
JOBS_DIR = OUTPUT_ROOT / "jobs"

os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(JOBS_DIR, exist_ok=True)

def run_falsification():
    # Parameters
    nx = 256 # Standard resolution
    s = 0.12 # Near threshold
    seeds = [42, 43, 44]
    
    results = []
    
    # Base config template
    base_config = {
        "nx": nx,
        "s": s,
        "dt": 1e-4,
        "length": 1.0,
        "steps": 3000,
        "s_duration": 2000,
        "initial_condition": {
            "epsilon_kind": "gaussian",
            "amplitude": 0.32,
            "sigma": 0.08,
            "seed": 42
        }
    }

    # FV-3: Primitive Reduction
    fv3_tests = [
        {"name": "kappa_0", "params": {"kappa": 0.0}},
        {"name": "lambda_R_0", "params": {"lambda_R": 0.0}},
        {"name": "h_0", "params": {"h": 0.0}}
    ]
    
    # FV-4: Adversarial Initialization
    fv4_tests = [
        {"name": "uniform_noise", "params": {
            "initial_condition": {
                "epsilon_kind": "uniform",
                "epsilon_base": 0.0,
                "noise_std": 0.2
            }
        }}
    ]

    all_tests = []
    for test in fv3_tests:
        all_tests.append({"vector": "FV-3", "name": f"pde_{test['name']}", "params": test["params"], "mechanism": "pde"})
    for test in fv4_tests:
        all_tests.append({"vector": "FV-4", "name": f"pde_{test['name']}", "params": test["params"], "mechanism": "pde"})

    # Agent Falsification
    # FV-3: kappa=0
    all_tests.append({"vector": "FV-3", "name": "agent_kappa_0", "params": {"K_phi": 0.0}, "mechanism": "agent"})
    # FV-4: Random Init (covered by default but let's vary)
    all_tests.append({"vector": "FV-4", "name": "agent_random_R_c", "params": {"R_c": 0.001}, "mechanism": "agent"})

    for test in all_tests:
        for seed in seeds:
            job_id = f"{test['vector']}_{test['name']}_seed_{seed}"
            out_dir = JOBS_DIR / job_id
            os.makedirs(out_dir, exist_ok=True)
            
            if test["mechanism"] == "pde":
                config = base_config.copy()
                if "initial_condition" in test["params"]:
                    config["initial_condition"] = test["params"]["initial_condition"]
                for k, v in test["params"].items():
                    if k != "initial_condition":
                        config[k] = v
                config["initial_condition"]["seed"] = seed
                cmd = ["python", "tools/structural_box_sim_cpp/sim_governed.py"]
            else:
                config = {"agent_count": 400, "steps": 2000, "R_c": 0.1, "K_phi": 0.6, "seed": seed}
                for k, v in test["params"].items():
                    config[k] = v
                cmd = ["python", "tools/agent_based_sim_v1_cpp/sim_governed.py"]
            
            config_path = out_dir / "config.json"
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
            
            print(f"[{datetime.datetime.now()}] [{test['vector']}] Running {test['name']}, seed={seed}")
            
            full_cmd = cmd + ["--config", str(config_path), "--out", str(out_dir)]
            
            with open(LOGS_DIR / f"{job_id}.stdout.log", "w") as f_out, \
                 open(LOGS_DIR / f"{job_id}.stderr.log", "w") as f_err:
                subprocess.run(full_cmd, stdout=f_out, stderr=f_err)
            
            summary_path = out_dir / "summary.json"
            if summary_path.exists():
                with open(summary_path, "r") as f:
                    summary = json.load(f)
                metrics = summary.get("final_metrics", summary.get("metrics", {}))
                results.append({
                    "vector": test["vector"],
                    "test_name": test["name"],
                    "mechanism": test["mechanism"],
                    "seed": seed,
                    "alignment_success_rate": metrics.get("alignment_success_rate", metrics.get("order_parameter", 0.0)),
                    "epsilon_max": metrics.get("epsilon_max", 0.0),
                    "output_dir": str(out_dir)
                })

    return results

def main():
    print(f"Starting Falsification Research: {RUN_ID}")
    
    results = run_falsification()
    
    # Save results
    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_ROOT / "falsification_results.csv", index=False)
    
    # Synthesis
    summary = df.groupby(["vector", "test_name"])["alignment_success_rate"].mean().reset_index()
    summary.to_csv(OUTPUT_ROOT / "falsification_synthesis.csv", index=False)

    manifest = {
        "run_id": RUN_ID,
        "timestamp": datetime.datetime.now().isoformat(),
        "total_runs": len(results),
        "status": "completed"
    }
    with open(OUTPUT_ROOT / "run_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
        
    print(f"Falsification run complete. Manifest saved to {OUTPUT_ROOT}/run_manifest.json")

if __name__ == "__main__":
    main()
