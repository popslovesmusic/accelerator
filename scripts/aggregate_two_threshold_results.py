import json
import os
import glob
import pandas as pd
import argparse

def aggregate(dir_path):
    results = []
    summary_files = glob.glob(os.path.join(dir_path, "**/summary.json"), recursive=True)
    
    for f in summary_files:
        try:
            with open(f, 'r') as j:
                data = json.load(j)
                config = data["config"]
                metrics = data["final_metrics"]
                
                # Check for tool type and handle flat/nested configs
                if "agent_count" in config:
                    tool = "agent"
                    s = config.get("mismatch_rate", 0)
                    kappa = config.get("kappa", 0)
                    obs = metrics.get("order_parameter", 0)
                else:
                    tool = "box"
                    # Handle flat config for structural_box_sim_cpp
                    if "model" in config:
                        s = config["model"].get("s", 0)
                        kappa = config["model"].get("kappa", 0)
                    else:
                        s = config.get("s", 0)
                        kappa = config.get("kappa", 0)
                    
                    obs = metrics.get("alignment_success_rate", metrics.get("epsilon_active_fraction", 0))
                
                mode = "warm" if "warm" in f else "cold"
                seed = config.get("seed", 1000)
                
                results.append({
                    "tool": tool,
                    "s": s,
                    "kappa": kappa,
                    "mode": mode,
                    "seed": seed,
                    "obs": obs
                })
        except Exception as e:
            print(f"Error processing {f}: {e}")
            
    df = pd.DataFrame(results)
    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True)
    args = parser.parse_args()
    
    df = aggregate(args.dir)
    print(df.to_string())
    df.to_csv(os.path.join(args.dir, "aggregated_results.csv"), index=False)
