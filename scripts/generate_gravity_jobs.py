import json
import os

jobs = []

for seed in range(1, 26):
    # Structural Box C++ (PDE)
    jobs.append({
        "job_id": f"gravity_box_cpp_seed_{seed}",
        "tool": "structural_box_sim_cpp",
        "config": "tools/structural_box_sim_v2/configs/default.json",
        "overrides": {
            "initial_condition.residue_kind": "gaussian_bump",
            "initial_condition.residue_amplitude": 5.0,
            "initial_condition.residue_sigma": 0.1,
            "initial_condition.seed": seed
        }
    })

    # CA Admissibility C++ (Discrete)
    jobs.append({
        "job_id": f"gravity_ca_cpp_seed_{seed}",
        "tool": "ca_admissibility_sim_v1_cpp",
        "config": "configs/examples/ca_residue_test.json",
        "overrides": {
            "source_strength": 5.0,
            "seed": seed
        }
    })

run_config = {
  "run_id": "2026-05-22_run01_gravity_hypothesis",
  "governance": {
    "dry_run_first": False,
    "stop_on_failure": False
  },
  "execution": {
    "max_workers": 8
  },
  "jobs": jobs
}

os.makedirs("configs/multi_runs", exist_ok=True)
with open("configs/multi_runs/gravity_hypothesis_run.json", "w") as f:
    json.dump(run_config, f, indent=2)

print("Generated gravity_hypothesis_run.json")
