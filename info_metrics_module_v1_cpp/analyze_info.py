import os
import json
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
import zlib

try:
    from metrics_cpp_wrapper import MetricsEngineCPP
    HAS_CPP = True
except Exception as e:
    print(f"Warning: Could not load C++ Metrics Engine: {e}")
    HAS_CPP = False

def compute_complexity(data):
    if len(data) == 0:
        return 0.0
    byte_data = data.tobytes()
    return len(zlib.compress(byte_data)) / len(byte_data)

def analyze_directory(input_dir, output_file):
    input_path = Path(input_dir)
    snapshots_dir = input_path / "snapshots"
    
    results = []
    engine = MetricsEngineCPP() if HAS_CPP else None
    
    if snapshots_dir.exists():
        print(f"Analyzing snapshots in {snapshots_dir} using {'GPU (SYCL)' if HAS_CPP else 'CPU (NumPy)'}...")
        snapshot_files = sorted(list(snapshots_dir.glob("*.npz")))
        
        for snap_file in snapshot_files:
            data = np.load(snap_file)
            state = data['state']
            if 'alive' in data:
                alive = data['alive']
                active_state = state[alive]
            else:
                active_state = state
            
            flat_state = active_state.flatten().astype(np.float32)
            step = int(data.get('step', -1))
            
            if HAS_CPP:
                entropy_val = engine.compute_entropy(flat_state, bins=100)
            else:
                # Fallback to numpy
                counts, _ = np.histogram(flat_state, bins=100)
                probs = counts[counts > 0] / len(flat_state)
                entropy_val = -np.sum(probs * np.log2(probs))
            
            complexity_val = compute_complexity(flat_state)
            
            results.append({
                "step": step,
                "entropy": float(entropy_val),
                "complexity": float(complexity_val)
            })
            
            if len(results) % 5 == 0:
                print(f"Processed {len(results)} snapshots...")

    if results:
        df_results = pd.DataFrame(results)
        df_results.to_csv(output_file, index=False)
        print(f"Info report saved to {output_file}")
        
        summary = {
            "mean_entropy": float(df_results['entropy'].mean()),
            "mean_complexity": float(df_results['complexity'].mean()),
            "status": "completed",
            "engine": "SYCL/UHD770" if HAS_CPP else "NumPy/CPU"
        }
        with open(Path(output_file).parent / "info_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze Information Metrics (Upgraded SYCL)")
    parser.add_argument("--dir", type=str, required=True, help="Simulation output directory")
    parser.add_argument("--out", type=str, default="info_evolution.csv", help="Output CSV filename")
    args = parser.parse_args()
    
    analyze_directory(args.dir, os.path.join(args.dir, args.out))
