import os
import json
import argparse
import importlib.util
import numpy as np
import pandas as pd
from pathlib import Path

def load_engine_class(module_path, class_name):
    spec = importlib.util.spec_from_file_location("engine_module", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, class_name)

def run_bifurcation(config_path, output_dir):
    with open(config_path, 'r') as f:
        scan_config = json.load(f)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Load the target engine
    engine_module_path = Path(scan_config['engine_module']).resolve()
    engine_class = load_engine_class(engine_module_path, scan_config['engine_class'])
    
    # 2. Load base config for the engine
    base_config_path = Path(scan_config['base_config']).resolve()
    with open(base_config_path, 'r') as f:
        engine_config = json.load(f)
    
    # 3. Instantiate the engine
    engine = engine_class(engine_config)
    
    # 4. Prepare the ramp
    ramp = scan_config['ramp_params']
    param_name = ramp['parameter']
    start_val = ramp['start']
    end_val = ramp['end']
    n_plateaus = ramp['steps']
    steps_per_plateau = ramp['steps_per_plateau']
    dt = engine_config.get('dt', 0.05)
    
    # Trackers
    results = []
    
    # Initialize state (we assume the sim.py usually does this, so we mirror it)
    # Most engines take phi or state as input to their step methods.
    # We need a generic way to handle the state.
    # For now, let's assume Kuramoto-like behavior where we manage phi.
    n = engine_config.get('n_oscillators', engine_config.get('n_agents', 100))
    state = np.random.uniform(0, 2 * np.pi, size=n) if 'Kuramoto' in scan_config['engine_class'] else np.random.normal(0, 0.1, size=(5, n))

    print(f"Starting bifurcation ramp for {param_name} from {start_val} to {end_val}...")
    
    param_values = np.linspace(start_val, end_val, n_plateaus)
    
    for i, val in enumerate(param_values):
        # Update engine parameter
        setattr(engine, param_name, val)
        
        # Step through the plateau
        for _ in range(steps_per_plateau):
            # Try different step method names based on our ecosystem
            if hasattr(engine, 'step_rk4'):
                state = engine.step_rk4(state, dt)
            elif hasattr(engine, 'evolve'):
                engine.evolve()
            elif hasattr(engine, 'step'):
                state = engine.step()
                
        # Record metrics at end of plateau
        if hasattr(engine, 'compute_metrics'):
            metrics = engine.compute_metrics(state)
        elif hasattr(engine, 'get_metrics'):
            metrics = engine.get_metrics()
        else:
            metrics = {}
            
        metrics[param_name] = val
        metrics['plateau_index'] = i
        results.append(metrics)
        
        if i % 5 == 0:
            print(f"Plateau {i}/{n_plateaus}: {param_name} = {val:.4f}")

    # Aggregate and Save
    df = pd.DataFrame(results)
    df.to_csv(os.path.join(output_dir, 'bifurcation_trace.csv'), index=False)
    print(f"Bifurcation trace saved to {output_dir}")

    # Optional Plotting
    try:
        import matplotlib.pyplot as plt
        plot_bifurcation(df, param_name, output_dir)
    except ImportError:
        pass

def plot_bifurcation(df, param_name, output_dir):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return

    plots_dir = os.path.join(output_dir, 'plots')
    os.makedirs(plots_dir, exist_ok=True)
    
    # Identify the primary observable (the first metric that isn't the parameter)
    observables = [c for c in df.columns if c not in [param_name, 'plateau_index', 'step', 'time']]
    
    if observables:
        plt.figure(figsize=(10, 6))
        plt.plot(df[param_name], df[observables[0]], marker='o', markersize=3, alpha=0.7)
        plt.xlabel(param_name)
        plt.ylabel(observables[0])
        plt.title(f"Bifurcation Diagram: {observables[0]} vs {param_name}")
        plt.grid(True)
        plt.savefig(os.path.join(plots_dir, 'bifurcation_diagram.png'))
        plt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bifurcation / Continuation Analyzer")
    parser.add_argument("--config", type=str, required=True, help="Path to scan config JSON")
    parser.add_argument("--out", type=str, default="outputs/bifurcation_run", help="Output directory")
    args = parser.parse_args()
    
    run_bifurcation(args.config, args.out)
