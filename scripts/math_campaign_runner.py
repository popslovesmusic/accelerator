import argparse
import json
import os
import time
import subprocess
import sys
from pathlib import Path

def run_variation(tool, base_config, variation, seeds, out_dir):
    var_name = variation.get("name", "base")
    print(f"--- Running {tool} Variation: {var_name} ---")
    
    var_dir = Path(out_dir) / f"{tool}_{var_name}"
    os.makedirs(var_dir, exist_ok=True)
    
    results = []
    
    # Discovery of wrapper
    wrapper_candidates = [
        Path(f"tools/{tool}/sim_governed.py"),
        Path(f"tools/{tool}/run_signal_scope.py"),
        Path(f"tools/{tool}/sim.py")
    ]
    wrapper = None
    for cand in wrapper_candidates:
        if cand.exists():
            wrapper = cand
            break
            
    if not wrapper:
        print(f"Error: No wrapper found for {tool}")
        return
        
    for seed in seeds:
        print(f"  Seed: {seed}")
        config = base_config.copy()
        config.update(variation.get("config_override", {}))
        config["seed"] = seed
        
        seed_dir = var_dir / f"seed_{seed}"
        os.makedirs(seed_dir, exist_ok=True)
        config_path = seed_dir / "sim_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        cmd = [sys.executable, str(wrapper), "--config", str(config_path), "--out", str(seed_dir)]
        # Add seed override only for specific tools known to support it at CLI level
        if "signal_scope" in tool or "rule_engine" in tool:
             cmd.extend(["--seed", str(seed)])
             
        subprocess.run(cmd, capture_output=True)
        
        # Discovery of metrics
        summary_path = seed_dir / "summary.json"
        metrics_path = seed_dir / "metrics.json"
        
        found_metrics = {}
        if summary_path.exists():
            with open(summary_path, 'r') as f:
                res = json.load(f)
                # handle both summary structures
                found_metrics = res.get("final_metrics", res.get("metrics", {}))
                if not found_metrics and "result" in res:
                     found_metrics = res["result"]
        elif metrics_path.exists():
            with open(metrics_path, 'r') as f:
                found_metrics = json.load(f)
                
        if found_metrics:
            results.append({"seed": seed, "metrics": found_metrics})
        else:
            print(f"  Warning: No metrics for seed {seed}")

    with open(var_dir / "results.json", 'w') as f:
        json.dump({"variation": var_name, "results": results}, f, indent=4)

def run_campaign(campaign_path, out_dir):
    with open(campaign_path, 'r') as f:
        campaign = json.load(f)
        
    seeds = campaign.get("seeds", [42])
    components = campaign.get("components", [])
    
    for comp in components:
        tool = comp.get("tool")
        base_config = comp.get("base_config", {})
        variations = comp.get("variations", [{"name": "default", "config_override": {}}])
        
        for var in variations:
            run_variation(tool, base_config, var, seeds, out_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    
    run_campaign(args.config, args.out)
