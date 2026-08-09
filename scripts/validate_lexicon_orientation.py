import json
import subprocess
import sys
from pathlib import Path

def main():
    out_dir = Path("results/2026-05-05_run05_lexicon_val_orientation_selection")
    data_dir = out_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Tool: structural_box_sim_cpp
    # Lexicon Term: -(i) (admissibility_orientation_selection)
    # Plan: Check if alignment_success_rate increases with wider kappa.
    
    results = []
    wrapper = Path("tools/structural_box_sim_cpp/sim_governed.py")
    
    for kappa in [0.01, 0.1, 0.5]:
        config = {
            "num_nodes": 128,
            "L": 1.0,
            "kappa": kappa,
            "epsilon_source": 10.0,
            "steps": 100,
            "dt": 0.01
        }
        
        run_dir = data_dir / f"kappa_{kappa}"
        run_dir.mkdir(parents=True, exist_ok=True)
        config_path = run_dir / "sim_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        cmd = [sys.executable, str(wrapper), "--config", str(config_path), "--out", str(run_dir)]
        subprocess.run(cmd, check=True)
        
        with open(run_dir / "summary.json", 'r') as f:
            summary = json.load(f)
            asr = summary["final_metrics"].get("alignment_success_rate", 0.0)
            results.append({"kappa": kappa, "asr": asr})
            
    print("Lexicon Validation Sweep Results:")
    for res in results:
        print(f"kappa={res['kappa']}, alignment_success_rate={res['asr']}")
    
    with open(data_dir / "validation_results.json", 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
