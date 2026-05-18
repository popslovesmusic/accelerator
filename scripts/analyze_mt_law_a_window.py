import json
from pathlib import Path
import pandas as pd

def analyze_window(run_id):
    root = Path(f'results/{run_id}/jobs')
    results = []
    
    for f in root.glob('**/summary.json'):
        try:
            d = json.load(open(f))
            s = d['config']['s']
            steps = d['config']['steps']
            seed = d['config']['seed']
            
            final_active = d['final_metrics']['epsilon_active_fraction']
            
            results.append({
                's': s,
                'steps': steps,
                'seed': seed,
                'final_active': final_active
            })
        except Exception as e:
            pass
            
    if not results:
        print("No window results found.")
        return

    df = pd.DataFrame(results)
    df.to_csv(f'results/{run_id}/artifacts/window_data.csv', index=False)
    
    summary = df.groupby(['s', 'steps'])['final_active'].agg(['mean', 'std']).reset_index()
    summary.to_csv(f'results/{run_id}/artifacts/window_summary.csv', index=False)
    print("Window analysis complete. Summary:")
    print(summary)
    
    # Detect Decay (if mean at t=20000 < mean at t=1000)
    for s in summary['s'].unique():
        sub = summary[summary['s'] == s].sort_values('steps')
        if len(sub) > 1:
            decay = sub.iloc[-1]['mean'] - sub.iloc[0]['mean']
            print(f"For s={s}, delta active_fraction over {sub.iloc[-1]['steps']} steps: {decay:.4f}")

if __name__ == '__main__':
    analyze_window('2026-05-17_run04_MT-LAW-A_TS4_Validity_Windows')
