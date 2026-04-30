import os
import json
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from tda_engine import compute_spatial_topology, compute_network_topology

def analyze_directory(input_dir, threshold, mode, output_file):
    input_path = Path(input_dir)
    results = []
    
    # Check if input is a single NPZ file or a directory
    if input_path.is_file() and input_path.suffix == '.npz':
        print(f"Analyzing snapshot sequence in single file: {input_path}")
        data = np.load(input_path)
        
        # Check for sequences (shape (N, ...))
        for key in ['epsilon_snapshots', 'rho_snapshots', 'residue_snapshots']:
            if key in data:
                sequence = data[key]
                print(f"Processing sequence: {key} (Shape: {sequence.shape})")
                for step, grid in enumerate(sequence):
                    if grid.ndim == 1:
                        # 1D TDA (not usual but possible)
                        metrics = compute_spatial_topology(grid.reshape(1, -1), threshold=threshold)
                    else:
                        metrics = compute_spatial_topology(grid, threshold=threshold)
                    metrics['step'] = step
                    results.append(metrics)
                break
    else:
        snapshots_dir = input_path / "snapshots"
        if snapshots_dir.exists():
            print(f"Analyzing snapshots in {snapshots_dir} (Mode: {mode})...")
            snapshot_files = sorted(list(snapshots_dir.glob("*.npz")))
            
            for snap_file in snapshot_files:
                data = np.load(snap_file)
                step = int(data.get('step', -1))
                
                if mode == 'spatial':
                    # Try common keys
                    grid = None
                    for key in ['state', 'epsilon', 'D', 'rho']:
                        if key in data:
                            grid = data[key]
                            break
                    if grid is None:
                        grid = data[data.files[0]]
                    
                    # Ensure 2D
                    if grid.ndim > 2:
                        grid = grid[0]
                    elif grid.ndim == 1:
                        grid = grid.reshape(1, -1)
                    
                    metrics = compute_spatial_topology(grid, threshold=threshold)
                else:
                    # Network Mode
                    if 'A' in data:
                        adj = data['A']
                        metrics = compute_network_topology(adj)
                    else:
                        continue

                metrics['step'] = step
                results.append(metrics)
                
                if len(results) % 10 == 0:
                    print(f"Processed {len(results)} snapshots...")

    if results:
        df_results = pd.DataFrame(results)
        df_results.to_csv(output_file, index=False)
        print(f"Topology evolution saved to {output_file}")
        
        # Optional Plotting
        try:
            import matplotlib.pyplot as plt
            plot_topology(df_results, Path(output_file).parent)
        except ImportError:
            pass

def plot_topology(df, output_dir):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        return

    plots_dir = output_dir / "plots_tda"
    plots_dir.mkdir(parents=True, exist_ok=True)
    
    plt.figure(figsize=(10, 5))
    plt.plot(df['step'], df['count'], label='Component Count (Betti-0)')
    plt.xlabel('Step')
    plt.ylabel('Count')
    plt.title('Topological Fragmentation')
    plt.grid(True)
    plt.savefig(plots_dir / "fragmentation.png")
    plt.close()
    
    plt.figure(figsize=(10, 5))
    plt.plot(df['step'], df['max_size'], label='Max Component Size', color='green')
    plt.xlabel('Step')
    plt.ylabel('Area (pixels / nodes)')
    plt.title('Largest Structure Persistence')
    plt.grid(True)
    plt.savefig(plots_dir / "max_structure.png")
    plt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Topological Data Analysis Module")
    parser.add_argument("--dir", type=str, required=True, help="Simulation output directory or NPZ file")
    parser.add_argument("--mode", type=str, choices=['spatial', 'network'], default='spatial')
    parser.add_argument("--threshold", type=float, default=0.5, help="Threshold for spatial mask")
    parser.add_argument("--out", type=str, default="topology_evolution.csv", help="Output CSV filename")
    args = parser.parse_args()
    
    input_path = Path(args.dir)
    if input_path.is_file():
        output_path = input_path.parent / args.out
    else:
        output_path = input_path / args.out
        
    os.makedirs(output_path.parent, exist_ok=True)
    analyze_directory(args.dir, args.threshold, args.mode, str(output_path))
