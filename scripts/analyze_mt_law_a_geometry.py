import json
from pathlib import Path
import pandas as pd
import numpy as np

def analyze_geometry(run_id):
    root = Path(f'results/{run_id}/jobs')
    results = []
    
    print(f"Scanning for summary.json in {root}...")
    for f in root.glob('**/summary.json'):
        try:
            d = json.load(open(f))
            s = d['config']['s']
            kappa = d['config']['kappa']
            seed = d['config']['seed']
            
            # Metric: Active identity fraction
            active_fraction = d['final_metrics']['epsilon_active_fraction']
            
            results.append({
                's': s,
                'kappa': kappa,
                'seed': seed,
                'active_fraction': active_fraction
            })
        except Exception as e:
            pass
        
    if not results:
        print('No results found yet.')
        return

    df = pd.DataFrame(results)
    df.to_csv(f'results/{run_id}/artifacts/geometry_data.csv', index=False)
    
    # Aggregated Summary (Mean over seeds)
    summary = df.groupby(['s', 'kappa'])['active_fraction'].agg(['mean', 'std', 'count']).reset_index()
    summary.to_csv(f'results/{run_id}/artifacts/geometry_summary.csv', index=False)
    
    print(f"Analysis complete. Found {len(df)} jobs across {len(summary)} parameter points.")
    
    # Detect the "Stability Boundary" (where mean active_fraction > 0.1)
    boundary = summary[summary['mean'] > 0.1].sort_values(['s', 'kappa']).groupby('s').first().reset_index()
    boundary.to_csv(f'results/{run_id}/artifacts/stability_boundary_points.csv', index=False)
    print("Stability boundary points estimated.")

if __name__ == '__main__':
    analyze_geometry('2026-05-17_run02_MT-LAW-A_TS4_Threshold_Geometry_Mapping')
