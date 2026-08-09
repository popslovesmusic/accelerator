import json
import os
import math
from pathlib import Path

def run_discrete_ratchet_model(epsilon_ramp, theta, delta_R, gamma_R, steps_per_eps):
    residue = 0.0
    history = []
    
    # Ramp Up
    for eps in epsilon_ramp:
        active_sum = 0
        for _ in range(steps_per_eps):
            # Selection rule: epsilon must exceed base theta + accumulated residue
            is_active = 1 if eps > (theta + residue) else 0
            active_sum += is_active
            # Inscription rule
            residue = residue + delta_R * is_active - gamma_R * residue
            residue = max(0.0, residue)
        
        history.append({
            "phase": "up",
            "epsilon": eps,
            "active_fraction": active_sum / steps_per_eps,
            "mean_residue": residue
        })

    # Ramp Down
    for eps in reversed(epsilon_ramp):
        active_sum = 0
        for _ in range(steps_per_eps):
            is_active = 1 if eps > (theta + residue) else 0
            active_sum += is_active
            residue = residue + delta_R * is_active - gamma_R * residue
            residue = max(0.0, residue)
            
        history.append({
            "phase": "down",
            "epsilon": eps,
            "active_fraction": active_sum / steps_per_eps,
            "mean_residue": residue
        })
        
    return history

# Campaign: RATCHET-HYSTERESIS-002 (Python Reference Model)
run_dir = Path("results/2026-05-21_run03_Ratchet_Hysteresis_Validation/data/python_ref")
os.makedirs(run_dir, exist_ok=True)

epsilon_ramp = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
results = run_discrete_ratchet_model(epsilon_ramp, theta=0.3, delta_R=0.2, gamma_R=0.05, steps_per_eps=50)

with open(run_dir / "summary.json", "w") as f:
    json.dump({"final_metrics": results[-1], "full_history": results, "status": "completed"}, f, indent=2)

print(f"Python Reference Model Complete. Results saved to {run_dir}")
