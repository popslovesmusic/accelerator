import json
from pathlib import Path
import pandas as pd

def analyze_recovery(run_id):
    root = Path(f'results/{run_id}/jobs')
    results = []
    
    # Baseline from Patch 012 at s=0.05 (approx 0.332)
    baseline_active = 0.332
    
    for f in root.glob('**/summary.json'):
        try:
            d = json.load(open(f))
            # Find the perturbation level from the job_id or config
            # In multi_sim_runner, config_seeded.json contains the 'sequence'
            # but sim_governed.py might not store the full sequence in summary.json['config']
            # Let's check the path
            p_str = f.parts[-3] # 'perturb_0.10'
            s_perturb = float(p_str.split('_')[1])
            seed = d['config']['seed']
            
            recovered_active = d['final_metrics']['epsilon_active_fraction']
            
            results.append({
                's_perturb': s_perturb,
                'seed': seed,
                'recovered_active': recovered_active,
                'is_hysteresis': abs(recovered_active - baseline_active) > 0.05
            })
        except Exception as e:
            print(f"Error analyzing {f}: {e}")
            
    if not results:
        print("No recovery results found.")
        return

    df = pd.DataFrame(results)
    df.to_csv(f'results/{run_id}/artifacts/recovery_data.csv', index=False)
    
    summary = df.groupby('s_perturb')['recovered_active'].agg(['mean', 'std']).reset_index()
    summary['baseline'] = baseline_active
    summary['hysteresis_detected'] = (summary['mean'] - baseline_active).abs() > 0.05
    
    summary.to_csv(f'results/{run_id}/artifacts/recovery_summary.csv', index=False)
    print("Recovery analysis complete. Summary:")
    print(summary)

if __name__ == '__main__':
    analyze_recovery('2026-05-17_run03_MT-LAW-A_TS4_Recovery_Dynamics')
