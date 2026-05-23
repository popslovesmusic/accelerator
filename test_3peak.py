import json
import subprocess
import os
from pathlib import Path

config = {
    "n_nodes": 3,
    "steps": 1000,
    "dt": 0.05,
    "K": 5.0,
    "theta_de": 1.0,
    "theta_re": 1.0,
    "P_re": 1.0,
    "omega_mean": 1.0,
    "omega_std": 0.5,
    "seed": 42
}

out_dir = "results/test_3peak"
os.makedirs(out_dir, exist_ok=True)
with open("test_config.json", "w") as f: json.dump(config, f)

subprocess.run(["python", "tools/graph_dynamics_sim_v1_cpp/sim_governed.py", "--config", "test_config.json", "--out", out_dir])

with open(Path(out_dir) / "summary.json") as f:
    print(json.load(f)["final_metrics"])
