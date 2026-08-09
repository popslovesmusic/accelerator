import os
import json
import subprocess
import numpy as np
import pandas as pd
from pathlib import Path
import concurrent.futures

class SigmaRMapper:
    def __init__(self, engine_exe, base_results_dir):
        self.engine_exe = Path(engine_exe)
        self.base_results_dir = Path(base_results_dir)
        self.base_results_dir.mkdir(parents=True, exist_ok=True)
        self.nx = 256
        self.ny = 256

    def load_snapshot(self, snapshot_path):
        n = self.nx * self.ny
        with open(snapshot_path, "rb") as f:
            epsilon = np.frombuffer(f.read(n * 4), dtype=np.float32)
            R = np.frombuffer(f.read(n * 4), dtype=np.float32)
            A = np.frombuffer(f.read(n * 4), dtype=np.float32)
            Ix = np.frombuffer(f.read(n * 4), dtype=np.float32)
            Iy = np.frombuffer(f.read(n * 4), dtype=np.float32)
        return {
            "epsilon": epsilon.reshape(self.ny, self.nx),
            "R": R.reshape(self.ny, self.nx),
            "A": A.reshape(self.ny, self.nx),
            "Ix": Ix.reshape(self.ny, self.nx),
            "Iy": Iy.reshape(self.ny, self.nx)
        }

    def extract_sigma_r(self, fields):
        Ix, Iy = fields["Ix"], fields["Iy"]
        R = fields["R"]
        A = fields["A"]
        
        # Focus on the 'active' part of the basin (A > 0.5)
        mask = A > 0.5
        if not np.any(mask):
            return None
            
        active_Ix = Ix[mask]
        active_Iy = Iy[mask]
        active_R = R[mask]
        
        # 1. Rotational Character (chi)
        # Simplified: cross product of mean orientation with a reference
        # Better: Average curl/vorticity in the basin
        # For now, let's use the mean angle progression if we had timeseries, 
        # but here we have a snapshot. We'll use the skew of the orientation.
        angles = np.arctan2(active_Iy, active_Ix)
        chi = "CCW" if np.mean(angles) > 0 else "CW"
        
        # 2. Distinction Density (rho_D)
        M_dom = np.max(active_R)
        rho_D = np.mean(active_R) / M_dom if M_dom > 0 else 0.0
        
        # 3. Admissibility Window (Wa)
        min_a, max_a = np.min(angles), np.max(angles)
        Wa_width = max_a - min_a
        
        # 4. Orientation Event Count (R_minus_i)
        # Spatial discontinuities in orientation
        grad_x = np.gradient(Ix)
        grad_y = np.gradient(Iy)
        grad_mag = np.sqrt(grad_x[0]**2 + grad_x[1]**2 + grad_y[0]**2 + grad_y[1]**2)
        events = np.sum(grad_mag[mask] > 0.5) # Threshold for an 'event'
        
        return {
            "chi": chi,
            "rho_D": round(float(rho_D), 4),
            "Wa_width": round(float(Wa_width), 4),
            "events": int(events),
            "M_dom": round(float(M_dom), 4)
        }

    def run_trial(self, seed, alpha_I, beta_I, perturbation_mode=None):
        trial_name = f"seed_{seed}_a{alpha_I}_b{beta_I}"
        if perturbation_mode:
            trial_name += f"_{perturbation_mode}"
        
        out_dir = self.base_results_dir / trial_name
        out_dir.mkdir(parents=True, exist_ok=True)
        
        config = {
            "nx": self.nx,
            "ny": self.ny,
            "seed": seed,
            "steps": 2000,
            "alpha_I": alpha_I,
            "beta_I": beta_I,
            "snapshot_interval": 1999
        }
        
        if perturbation_mode:
            config["falsification_mode"] = perturbation_mode
            config["falsification_intensity"] = 0.05
            
        config_path = out_dir / "config.json"
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
            
        subprocess.run([str(self.engine_exe), str(config_path), str(out_dir)], capture_output=True)
        
        summary_path = out_dir / "summary_metrics.json"
        snapshot_path = out_dir / "field_snapshot_1999.bin"
        
        if not snapshot_path.exists():
            return None
            
        fields = self.load_snapshot(snapshot_path)
        sigma_r = self.extract_sigma_r(fields)
        
        with open(summary_path, "r") as f:
            metrics = json.load(f)
            
        return {
            "seed": seed,
            "alpha_I": alpha_I,
            "beta_I": beta_I,
            "perturbation_mode": perturbation_mode,
            "sigma_r": sigma_r,
            "metrics": metrics,
            "survived": metrics["final_residue_coherence"] > 0.1
        }

    def run_campaign(self, num_seeds=4):
        print(f"Starting Sigma_R Mapping Campaign with {num_seeds} seeds and beta_I sweep...")
        
        beta_sweep = [0.8, 0.5, 0.2, 0.1]
        all_results = []
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for b in beta_sweep:
                for s in range(num_seeds):
                    # Baseline
                    futures.append(executor.submit(self.run_trial, s, 0.2, b))
                    # Perturbed
                    futures.append(executor.submit(self.run_trial, s, 0.2, b, "FV_003_admissibility_narrowing"))
            
            for f in concurrent.futures.as_completed(futures):
                res = f.result()
                if res: all_results.append(res)
                
        # Analysis
        analysis = []
        for b_val in beta_sweep:
            for s in range(num_seeds):
                baseline = next((x for x in all_results if x["seed"] == s and x["beta_I"] == b_val and x["perturbation_mode"] is None), None)
                perturbed = next((x for x in all_results if x["seed"] == s and x["beta_I"] == b_val and x["perturbation_mode"] == "FV_003_admissibility_narrowing"), None)
                
                if baseline and perturbed:
                    analysis.append({
                        "seed": s,
                        "beta_I": b_val,
                        "sigma_r": baseline["sigma_r"],
                        "baseline_coherence": baseline["metrics"]["final_residue_coherence"],
                        "perturbed_coherence": perturbed["metrics"]["final_residue_coherence"],
                        "survived": perturbed["survived"]
                    })
        
        with open(self.base_results_dir / "campaign_analysis.json", "w") as f:
            json.dump(analysis, f, indent=2)
            
        print(f"Campaign complete. Analysis saved to {self.base_results_dir / 'campaign_analysis.json'}")
        return analysis

if __name__ == "__main__":
    engine = "engines/procedural_pde_engine/build/Release/procedural_pde_engine.exe"
    results_dir = "results/2026-06-17_run01_SigmaR_Predictive_Mapping"
    mapper = SigmaRMapper(engine, results_dir)
    mapper.run_campaign(num_seeds=16)
