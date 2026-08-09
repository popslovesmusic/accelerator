import argparse
import json
import os
import time
from pathlib import Path
from fsa_cpp_wrapper import FSAEngineCPP

def run_variation(variation_config, out_dir, common_seeds):
    experiment_id = variation_config.get("name", "unnamed_variation")
    print(f"--- Running Variation: {experiment_id} ---")
    
    variation_out = Path(out_dir) / experiment_id
    os.makedirs(variation_out, exist_ok=True)
    
    results = []
    
    for seed in common_seeds:
        print(f"  Seed: {seed}")
        config = variation_config.copy()
        config["seed"] = seed
        
        num_agents = config.get("num_agents", 1000)
        n_states = config.get("n_states", 10)
        forbidden = config.get("forbidden", 9)
        res_thresh = config.get("res_thresh", 5)
        res_req = config.get("res_req", 2)
        mismatch_rate = config.get("mismatch_rate", 0.0)
        steps = config.get("steps", 100)
        start_node = config.get("start_node", 0)

        engine = FSAEngineCPP(num_agents, n_states, forbidden, res_thresh, res_req, mismatch_rate)
        engine.initialize(start_node, seed)

        start_time = time.time()
        for i in range(steps):
            engine.step()
        end_time = time.time()
        
        runtime_ms = (end_time - start_time) * 1000
        metrics = engine.get_metrics()
        metrics["runtime_ms"] = runtime_ms
        
        results.append({
            "seed": seed,
            "metrics": metrics,
            "active_history": engine.get_active_history()
        })
        
    final_output = {
        "variation_name": experiment_id,
        "results": results
    }
    
    with open(variation_out / "results.json", "w") as f:
        json.dump(final_output, f, indent=4)

def run_campaign(campaign_path, out_dir):
    with open(campaign_path, 'r') as f:
        campaign = json.load(f)
    
    base_config = campaign.get("base_config", {})
    seeds = campaign.get("seeds", [42])
    variations = campaign.get("variations", [])
    
    for var in variations:
        var_config = base_config.copy()
        var_config.update(var.get("config_override", {}))
        var_config["name"] = var.get("name")
        run_variation(var_config, out_dir, seeds)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to campaign config JSON")
    parser.add_argument("--out", required=True, help="Output directory")
    args = parser.parse_args()
    
    # Try to load setvars if available
    run_campaign(args.config, args.out)
