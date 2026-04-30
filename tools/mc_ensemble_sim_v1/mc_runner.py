import os
import json
import argparse
import subprocess
import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

def sample_parameter(rule):
    if rule['type'] == 'uniform':
        return np.random.uniform(rule['min'], rule['max'])
    elif rule['type'] == 'choice':
        return np.random.choice(rule['values'])
    else:
        raise ValueError(f"Unknown sampling type: {rule['type']}")

def run_trial(trial_id, target_script, base_config, scan_params, output_root):
    trial_dir = output_root / f"trial_{trial_id:04d}"
    trial_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Load base config
    with open(base_config, 'r') as f:
        config = json.load(f)
    
    # 2. Overwrite with sampled parameters
    sampled = {}
    for param, rule in scan_params.items():
        val = sample_parameter(rule)
        config[param] = val
        sampled[param] = val
    
    # 3. Save trial config
    config_path = trial_dir / "config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f)
    
    # 4. Execute simulator
    # We assume the simulator is a sim.py script that takes --config and --out
    try:
        subprocess.run(
            ["python", str(target_script), "--config", str(config_path), "--out", str(trial_dir)],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Trial {trial_id} failed: {e.stderr}")
        return None

    # 5. Read summary.json result
    summary_path = trial_dir / "summary.json"
    if not summary_path.exists():
        return None
        
    with open(summary_path, 'r') as f:
        summary = json.load(f)
        
    # Flatten: combine sampled params with final metrics
    result = {"trial_id": trial_id}
    result.update(sampled)
    
    # simulator summaries usually have a 'final_metrics' dict
    if 'final_metrics' in summary:
        for k, v in summary['final_metrics'].items():
            result[f"metric_{k}"] = v
            
    return result

def main():
    parser = argparse.ArgumentParser(description="Monte Carlo Ensemble Simulator")
    parser.add_argument("--config", type=str, required=True, help="Path to scan config JSON")
    parser.add_argument("--out", type=str, default="outputs/ensemble_run", help="Output root directory")
    args = parser.parse_args()
    
    with open(args.config, 'r') as f:
        scan_config = json.load(f)
        
    output_root = Path(args.out)
    output_root.mkdir(parents=True, exist_ok=True)
    
    target_script = Path(scan_config['target_script']).resolve()
    base_config = Path(scan_config['base_config']).resolve()
    trials = scan_config['trials']
    scan_params = scan_config['scan_params']
    
    print(f"Starting Monte Carlo ensemble: {trials} trials of {target_script.name}")
    
    results = []
    with ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(run_trial, i, target_script, base_config, scan_params, output_root)
            for i in range(trials)
        ]
        
        for i, future in enumerate(futures):
            res = future.result()
            if res:
                results.append(res)
            if i % 10 == 0:
                print(f"Progress: {i}/{trials} trials dispatched...")

    # Aggregate and Save
    df = pd.DataFrame(results)
    df.to_csv(output_root / "ensemble_results.csv", index=False)
    print(f"Ensemble complete. Results saved to {output_root / 'ensemble_results.csv'}")

    # Optional Plotting
    try:
        import matplotlib.pyplot as plt
        plot_ensemble(df, output_root)
    except ImportError:
        pass

def plot_ensemble(df, output_root):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return

    # Find two parameters to plot if possible
    # Just a simple scatter for now
    params = [c for c in df.columns if not c.startswith('metric_') and c != 'trial_id']
    metrics = [c for c in df.columns if c.startswith('metric_')]
    
    if len(params) >= 1 and len(metrics) >= 1:
        plt.figure(figsize=(10, 6))
        # Plot first param vs first metric
        scatter = plt.scatter(df[params[0]], df[metrics[0]], c=df[params[1]] if len(params) > 1 else None, cmap='viridis')
        plt.xlabel(params[0])
        plt.ylabel(metrics[0])
        if len(params) > 1:
            plt.colorbar(scatter, label=params[1])
        plt.title(f"Regime Map: {metrics[0]} vs {params[0]}")
        plt.grid(True)
        plt.savefig(output_root / "regime_map.png")
        plt.close()

if __name__ == "__main__":
    main()
