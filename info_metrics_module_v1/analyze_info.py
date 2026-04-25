import os
import json
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from metrics_engine import compute_entropy, compute_complexity, compute_mutual_information

def analyze_directory(input_dir, output_file):
    input_path = Path(input_dir)
    snapshots_dir = input_path / "snapshots"
    
    results = []
    
    if snapshots_dir.exists():
        print(f"Analyzing snapshots in {snapshots_dir}...")
        snapshot_files = sorted(list(snapshots_dir.glob("*.npz")))
        
        for snap_file in snapshot_files:
            data = np.load(snap_file)
            state = data['state']
            if 'alive' in data:
                alive = data['alive']
                active_state = state[alive]
            else:
                active_state = state
            
            # Compute info metrics for the whole state (flattened)
            # or specifically for the first column (e.g. x)
            # We'll do it for the flattened active state to capture total system info
            flat_state = active_state.flatten()
            
            step = int(data.get('step', -1))
            
            entropy_val = compute_entropy(flat_state)
            complexity_val = compute_complexity(flat_state)
            
            # Temporal MI with previous if possible
            mi_val = 0.0
            if len(results) > 0:
                # This is just a placeholder logic for temporal MI
                # In a real tool we might want to load the previous state explicitly
                pass

            results.append({
                "step": step,
                "entropy": float(entropy_val),
                "complexity": float(complexity_val)
            })
            
            if len(results) % 5 == 0:
                print(f"Processed {len(results)} snapshots...")

    else:
        print(f"No snapshots found in {input_dir}. Checking metrics.csv...")
        metrics_path = input_path / "metrics.csv"
        if metrics_path.exists():
            df = pd.read_csv(metrics_path)
            # We can compute entropy of specific columns over time
            # But the 'tools.json' implies measuring the state structure.
            print("Metric-only analysis not fully implemented. Snapshots recommended.")
            return

    if results:
        df_results = pd.DataFrame(results)
        df_results.to_csv(output_file, index=False)
        print(f"Info report saved to {output_file}")
        
        # Save summary
        summary = {
            "mean_entropy": float(df_results['entropy'].mean()),
            "mean_complexity": float(df_results['complexity'].mean()),
            "entropy_trend": float(df_results['entropy'].iloc[-1] - df_results['entropy'].iloc[0]) if len(df_results) > 1 else 0.0,
            "status": "completed"
        }
        summary_path = Path(output_file).parent / "info_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
            
        # Optional Plotting
        try:
            import matplotlib.pyplot as plt
            plot_info(df_results, Path(output_file).parent)
        except ImportError:
            pass

def plot_info(df, output_dir):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return

    plots_dir = output_dir / "plots_info"
    plots_dir.mkdir(parents=True, exist_ok=True)
    
    plt.figure(figsize=(10, 5))
    plt.plot(df['step'], df['entropy'], label='Shannon Entropy')
    plt.xlabel('Step')
    plt.ylabel('H')
    plt.title('System Entropy over Time')
    plt.grid(True)
    plt.savefig(plots_dir / "entropy_evolution.png")
    plt.close()
    
    plt.figure(figsize=(10, 5))
    plt.plot(df['step'], df['complexity'], label='Compression Complexity', color='orange')
    plt.xlabel('Step')
    plt.ylabel('Complexity Score')
    plt.title('Data Complexity (zlib ratio)')
    plt.grid(True)
    plt.savefig(plots_dir / "complexity_evolution.png")
    plt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze Information Metrics of Simulation Outputs")
    parser.add_argument("--dir", type=str, required=True, help="Simulation output directory")
    parser.add_argument("--out", type=str, default="info_evolution.csv", help="Output CSV filename")
    args = parser.parse_args()
    
    analyze_directory(args.dir, os.path.join(args.dir, args.out))
