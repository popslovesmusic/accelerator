import os
import json
import argparse
import subprocess
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.optimize import minimize

def run_simulation_and_get_score(params_vector, param_names, target_script, base_config, target_metric_path, trial_dir):
    trial_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Load base config
    with open(base_config, 'r') as f:
        config = json.load(f)
    
    # 2. Update with optimization params
    sampled = {}
    for i, name in enumerate(param_names):
        val = float(params_vector[i])
        config[name] = val
        sampled[name] = val
    
    # 3. Save trial config
    config_path = trial_dir / "config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f)
    
    # 4. Execute simulator
    try:
        subprocess.run(
            ["python", str(target_script), "--config", str(config_path), "--out", str(trial_dir)],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError:
        return 1e12 # Return large penalty for failure
    
    # 5. Read summary.json result
    summary_path = trial_dir / "summary.json"
    if not summary_path.exists():
        return 1e12
        
    with open(summary_path, 'r') as f:
        summary = json.load(f)
    
    # Extract target metric (e.g. final_metrics.order_parameter)
    # Using simple recursive lookup
    val = summary
    for part in target_metric_path.split('.'):
        if part in val:
            val = val[part]
        else:
            return 1e12
            
    # Return negative since optimizers minimize
    return -float(val), sampled

def main():
    parser = argparse.ArgumentParser(description="Constraint / Parameter Optimizer")
    parser.add_argument("--config", type=str, required=True, help="Path to optimization config JSON")
    parser.add_argument("--out", type=str, default="outputs/optimization_run", help="Output root directory")
    args = parser.parse_args()
    
    with open(args.config, 'r') as f:
        opt_config = json.load(f)
        
    output_root = Path(args.out)
    output_root.mkdir(parents=True, exist_ok=True)
    
    target_script = Path(opt_config['target_script']).resolve()
    base_config = Path(opt_config['base_config']).resolve()
    target_metric = opt_config['target_metric']
    search_params = opt_config['search_params']
    param_names = list(search_params.keys())
    bounds = [search_params[name] for name in param_names]
    
    eval_count = 0
    trace = []
    
    def objective(x):
        nonlocal eval_count
        eval_count += 1
        trial_dir = output_root / f"eval_{eval_count:04d}"
        score, sampled = run_simulation_and_get_score(
            x, param_names, target_script, base_config, target_metric, trial_dir
        )
        
        entry = {"eval": eval_count, "score": -score} # record positive score
        entry.update(sampled)
        trace.append(entry)
        
        print(f"Eval {eval_count}: {sampled} -> Score = {-score:.4f}")
        return score

    print(f"Starting optimization: {opt_config['method']} for {opt_config['max_evals']} evals...")
    
    initial_guess = [np.mean(b) for b in bounds]
    
    if opt_config['method'] == 'nelder-mead':
        res = minimize(objective, initial_guess, method='Nelder-Mead', 
                       options={'maxiter': opt_config['max_evals']},
                       bounds=bounds)
        best_x = res.x
    else:
        # Random Search
        best_score = 1e12
        best_x = initial_guess
        for _ in range(opt_config['max_evals']):
            x = [np.random.uniform(b[0], b[1]) for b in bounds]
            score = objective(x)
            if score < best_score:
                best_score = score
                best_x = x

    # Aggregation
    df = pd.DataFrame(trace)
    df.to_csv(output_root / "optimization_trace.csv", index=False)
    
    # Save best config
    with open(base_config, 'r') as f:
        best_config = json.load(f)
    for i, name in enumerate(param_names):
        best_config[name] = float(best_x[i])
        
    with open(output_root / "best_config.json", 'w') as f:
        json.dump(best_config, f, indent=2)
        
    print(f"Optimization complete. Best configuration saved to {output_root / 'best_config.json'}")

if __name__ == "__main__":
    main()
