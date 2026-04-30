import os
import json
import subprocess
import pandas as pd
import numpy as np

RESEARCH_DIR = "research_epsilon_identity_v1"
AGENT_SIM_DIR = "agent_based_sim_v1"
BOX_SIM_DIR = "structural_box_sim_v2"

def run_agent_sim():
    mismatch_rates = [0.0, 0.001, 0.01, 0.1]
    seeds = [42, 43, 44]
    
    results = []
    
    for rate in mismatch_rates:
        for seed in seeds:
            out_dir = os.path.join(RESEARCH_DIR, f"agent_rate_{rate}_seed_{seed}")
            config = {
                "n_agents": 100,
                "steps": 1000,
                "dt": 0.05,
                "kappa": 1.0,
                "R_c": 1.5,
                "K_phi": 2.0,
                "omega_mean": 1.0,
                "omega_std": 0.1,
                "mismatch_rate": rate,
                "residue_decay": 0.001,
                "seed": seed
            }
            config_path = os.path.join(RESEARCH_DIR, f"config_agent_{rate}_{seed}.json")
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
            
            print(f"Running Agent Sim: rate={rate}, seed={seed}")
            subprocess.run([
                "python", os.path.join(AGENT_SIM_DIR, "sim.py"),
                "--config", config_path,
                "--out", out_dir
            ], capture_output=True)
            
            metrics_path = os.path.join(out_dir, "metrics.csv")
            if os.path.exists(metrics_path):
                df = pd.read_csv(metrics_path)
                final_row = df.iloc[-1]
                results.append({
                    "model": "agent",
                    "param": rate,
                    "seed": seed,
                    "mismatch": final_row["mismatch_mean"],
                    "order": final_row["order_parameter"],
                    "residue": final_row["residue_mean"]
                })
    return results

def run_box_sim():
    s_values = [0.0, 0.005, 0.01, 0.05]
    seeds = [1000, 1001, 1002]
    
    results = []
    
    # Load base config
    base_config_path = os.path.join(BOX_SIM_DIR, "configs", "default.json")
    with open(base_config_path, "r") as f:
        base_config = json.load(f)
        
    for s in s_values:
        for seed in seeds:
            out_dir = os.path.join("..", RESEARCH_DIR, f"box_s_{s}_seed_{seed}") # Relative to configs dir
            config = base_config.copy()
            config["model"]["s"] = s
            config["initial_condition"]["seed"] = seed
            
            config_path = os.path.join(RESEARCH_DIR, f"config_box_{s}_{seed}.json")
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
            
            print(f"Running Box Sim: s={s}, seed={seed}")
            subprocess.run([
                "python", os.path.join(BOX_SIM_DIR, "sim.py"),
                "--config", config_path,
                "--out", out_dir
            ], capture_output=True)
            
            # Box sim outputs summary.json in out_dir resolved relative to config
            # config is in RESEARCH_DIR, out is ../RESEARCH_DIR/... 
            # so it should be in RESEARCH_DIR/box_s_{s}_seed_{seed}
            summary_path = os.path.join(RESEARCH_DIR, f"box_s_{s}_seed_{seed}", "summary.json")
            if os.path.exists(summary_path):
                with open(summary_path, "r") as f:
                    summary = json.load(f)
                final = summary["final"]
                results.append({
                    "model": "box",
                    "param": s,
                    "seed": seed,
                    "mismatch": final["epsilon_mean"],
                    "order": final.get("epsilon_active_fraction", 0), # Using activity fraction as identity proxy
                    "residue": final["residue_mean"]
                })
    return results

def main():
    agent_results = run_agent_sim()
    box_results = run_box_sim()
    
    all_results = agent_results + box_results
    df = pd.DataFrame(all_results)
    df.to_csv(os.path.join(RESEARCH_DIR, "all_results.csv"), index=False)
    print("All simulations complete. Results saved to all_results.csv")

if __name__ == "__main__":
    main()
