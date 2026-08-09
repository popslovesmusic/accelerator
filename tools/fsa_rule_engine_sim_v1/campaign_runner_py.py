import os
import json
import argparse
import numpy as np
import pandas as pd
from fsa_engine import RuleEngine, FSAAgent

def run_variation(var_config, out_dir, common_seeds):
    variation_name = var_config.get("name", "unnamed_variation")
    print(f"--- Running Variation: {variation_name} ---")
    
    var_dir = Path(out_dir) / variation_name
    os.makedirs(var_dir, exist_ok=True)
    
    results = []
    
    for seed in common_seeds:
        print(f"  Seed: {seed}")
        np.random.seed(seed)
        
        # Merge variation config
        config = var_config.copy()
        config["seed"] = seed
        
        # Handle n_agents vs num_agents discrepancy
        n_agents = config.get("n_agents", config.get("num_agents", 100))
        config["n_agents"] = n_agents
        
        engine = RuleEngine(config)
        steps = config.get("steps", 100)
        
        agents = [FSAAgent(start_node=1) for _ in range(n_agents)]
        history = []
        
        for step in range(steps):
            for agent in agents:
                agent.step(engine)
            
            active_agents = [a for a in agents if a.active]
            n_active = len(active_agents)
            avg_res = np.mean([a.residue for a in active_agents]) if n_active > 0 else 0
            
            history.append({
                "step": step,
                "active_count": n_active,
                "mean_residue": float(avg_res)
            })
            
        final_states = [a.current_state for a in agents if a.active]
        state_counts = pd.Series(final_states).value_counts().to_dict()
        
        results.append({
            "seed": seed,
            "metrics": history[-1],
            "state_distribution": {str(k): int(v) for k, v in state_counts.items()},
            "total_halted": n_agents - len(active_agents)
        })
        
    with open(var_dir / "results.json", "w") as f:
        json.dump({"variation": variation_name, "results": results}, f, indent=4)

from pathlib import Path

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
    
    run_campaign(args.config, args.out)
