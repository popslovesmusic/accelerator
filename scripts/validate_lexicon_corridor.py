import json
import subprocess
import sys
from pathlib import Path

def main():
    out_dir = Path("results/2026-05-05_run07_lexicon_val_corridor")
    data_dir = out_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    config = {
        "grid_size": 64,
        "dt": 0.05,
        "steps": 1000,
        "seed": 42,
        "D_diff": 0.1,
        "S_diff": 0.5,
        "beta": 2.0,
        "growth_thresh": 0.2,
        "domain_decay": 0.01,
        "signal_decay": 0.05,
        "source_pos": [32, 32],
        "source_radius": 2.0,
        "source_strength": 1.0
    }
    
    config_path = data_dir / "sim_config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
        
    wrapper = Path("tools/rd_moving_boundary_sim_v1/sim.py")
    subprocess.run([sys.executable, str(wrapper), "--config", str(config_path), "--out", str(data_dir)], check=True)
    
    # Run TDA
    tda_wrapper = Path("tools/tda_module_v2_cpp/sim_governed.py")
    # tda_module_v2_cpp expects --config with grid_csv and threshold
    tda_config = {
        "grid_csv": str(data_dir / "final_S_field.csv"),
        "threshold": 0.1,
        "persistence_min": 0.05
    }
    tda_config_path = data_dir / "tda_config.json"
    with open(tda_config_path, 'w') as f:
        json.dump(tda_config, f, indent=2)
        
    tda_out_dir = data_dir / "tda"
    subprocess.run([sys.executable, str(tda_wrapper), "--config", str(tda_config_path), "--out", str(tda_out_dir)], check=True)

if __name__ == "__main__":
    main()
