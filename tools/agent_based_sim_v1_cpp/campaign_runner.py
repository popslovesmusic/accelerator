import argparse
import json
import os
import time
from pathlib import Path
from agent_cpp_wrapper import AgentEngineCPP

def run_variation(variation_config, out_dir, common_seeds):
    variation_name = variation_config.get("name", "unnamed_variation")
    print(f"--- Running Variation: {variation_name} ---")
    
    var_dir = Path(out_dir) / variation_name
    os.makedirs(var_dir, exist_ok=True)
    
    results = []
    
    for seed in common_seeds:
        print(f"  Seed: {seed}")
        
        agent_count = variation_config.get("agent_count", 1000)
        steps = variation_config.get("steps", 100)
        dt = variation_config.get("dt", 0.01)
        kappa = variation_config.get("kappa", 1.0)
        R_c = variation_config.get("R_c", 0.5)
        K_phi = variation_config.get("K_phi", 1.0)
        mismatch_rate = variation_config.get("mismatch_rate", 0.01)
        residue_decay = variation_config.get("residue_decay", 0.1)
        x_std = variation_config.get("x_std", 0.5)
        p_std = variation_config.get("p_std", 0.5)
        omega_mean = variation_config.get("omega_mean", 1.0)
        omega_std = variation_config.get("omega_std", 0.1)

        engine = AgentEngineCPP(agent_count)
        engine.set_params(kappa, R_c, K_phi, mismatch_rate, residue_decay)
        engine.initialize(seed, x_std, p_std, omega_mean, omega_std)

        start_time = time.time()
        for i in range(steps):
            engine.step(dt)
        end_time = time.time()
        
        runtime_ms = (end_time - start_time) * 1000
        metrics = engine.get_metrics()
        metrics["runtime_ms"] = runtime_ms
        
        # Save state for TDA
        seed_data_dir = var_dir / f"seed_{seed}"
        os.makedirs(seed_data_dir, exist_ok=True)
        # Assuming engine has a method to save grid/state if we want TDA
        # For now, just recording metrics
        
        results.append({
            "seed": seed,
            "metrics": metrics
        })
        
    with open(var_dir / "results.json", "w") as f:
        json.dump({"variation": variation_name, "results": results}, f, indent=4)

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
