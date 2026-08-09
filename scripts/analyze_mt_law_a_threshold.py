import json
from pathlib import Path
import pandas as pd

def analyze(run_id):
    root = Path(f'results/{run_id}/jobs')
    results = []
    
    # Box
    for f in root.glob('structural_box/**/summary.json'):
        try:
            d = json.load(open(f))
            s = d['config']['s']
            seed = d['config']['seed']
            results.append({
                'mechanism': 'structural_box',
                'param': s,
                'seed': seed,
                'active_fraction': d['final_metrics']['epsilon_active_fraction']
            })
        except Exception as e:
            print(f'Error reading {f}: {e}')
        
    # Stochastic
    for f in list(root.glob('stochastic/**/summary.json')) + list(root.glob('stochastic_sensitive/**/summary.json')):
        try:
            d = json.load(open(f))
            sigma = d['config']['sigma']
            seed = d['config']['seed']
            mechanism = 'stochastic'
            if 'stochastic_sensitive' in str(f):
                mechanism = 'stochastic_sensitive'
            results.append({
                'mechanism': mechanism,
                'param': sigma,
                'seed': seed,
                'active_fraction': d['final_metrics']['crossing_fraction']
            })
        except Exception as e:
            print(f'Error reading {f}: {e}')
        
    if not results:
        print('No results found.')
        return

    df = pd.DataFrame(results)
    df.to_csv(f'results/{run_id}/artifacts/threshold_data.csv', index=False)
    
    summary = df.groupby(['mechanism', 'param'])['active_fraction'].agg(['mean', 'std']).reset_index()
    summary.to_csv(f'results/{run_id}/artifacts/threshold_summary.csv', index=False)
    print('Analysis complete. Summary:')
    print(summary)

if __name__ == '__main__':
    analyze('2026-05-17_run01_MT-LAW-A_TS4_FV2_Threshold_Verification')
