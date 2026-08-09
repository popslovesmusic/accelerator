import os
import json
import numpy as np
import pandas as pd
from pathlib import Path
import concurrent.futures
from datetime import datetime

class ARTSim:
    def __init__(self, N, epsilon, model_type="M0_full_aRT", seed=42):
        self.N = N
        self.epsilon = epsilon
        self.model_type = model_type
        self.seed = seed
        np.random.seed(seed)
        
        self.chi_D = np.random.rand(N, N)
        np.fill_diagonal(self.chi_D, 0)
        
        self.R = np.zeros((N, N))
        self.I_minus = np.random.rand(N, N)
        np.fill_diagonal(self.I_minus, 0)
        
        # Used for M3 substitution
        self.R_alt = np.zeros((N, N)) 
        
        self.collapse = False
        self.history = []
        self.perturbation_time = 500

    def step(self, t):
        if self.collapse:
            return

        # Pre-update global state
        E_global = np.sum(self.chi_D)
        if E_global == 0:
            self.collapse = True
            return

        # Continuous alternative process for M3 (a stable R generator)
        self.R_alt = 0.95 * self.R_alt + 0.05 * (np.random.rand(self.N, self.N) > 0.5).astype(float)
        
        # Apply Perturbations (Static or Dynamic depending on model)
        current_I = self.I_minus
        current_R = self.R
        current_chi_D = self.chi_D.copy()
        
        if self.model_type == "M1_simple_ablation":
            current_I = np.zeros((self.N, self.N))
        elif self.model_type == "M2_substituted_orientation" and t > self.perturbation_time:
            # Shift orientation every 10 steps after t=500 to keep it a substituted but coherent field
            if t % 10 == 0:
                self.I_minus = np.random.rand(self.N, self.N)
                np.fill_diagonal(self.I_minus, 0)
            current_I = self.I_minus
        elif self.model_type == "M3_substituted_residue" and t > self.perturbation_time:
            current_R = self.R_alt
        # Admissibility
        A_adm = (current_R > 0.05) | (np.random.rand(self.N, self.N) < 0.02)
        np.fill_diagonal(A_adm, 0)
        
        if self.model_type == "M4_random_shuffle" and t > self.perturbation_time:
            # We break the specific topological binding between the distinct RT members.
            # We apply independent random permutations to A_adm and target computation.
            perm1 = np.random.permutation(self.N * self.N)
            perm2 = np.random.permutation(self.N * self.N)
            
            A_adm = A_adm.flatten()[perm1].reshape(self.N, self.N)
            current_I = current_I.flatten()[perm2].reshape(self.N, self.N)
            
        elif self.model_type == "M5_trace_preserving" and t > self.perturbation_time:
            # Deform the array consistently (roll by 1)
            current_chi_D = np.roll(self.chi_D, shift=(1,1), axis=(0,1))
            current_I = np.roll(self.I_minus, shift=(1,1), axis=(0,1))
            current_R = np.roll(self.R, shift=(1,1), axis=(0,1))

        # Arbitration (Indirect pressure based on current chi_D)
        indirect_pressure = current_chi_D @ current_chi_D
        max_p = np.max(indirect_pressure)
        if max_p > 0:
            indirect_pressure /= max_p
            
        target = 0.5 * current_I + 0.5 * indirect_pressure
        dq = (target - current_chi_D) * 0.1

        # Realization Delta (with natural decay to prevent automatic dense saturation)
        new_chi_D = current_chi_D * 0.95 + dq * A_adm
        
        # Floor Rule
        new_chi_D[new_chi_D < self.epsilon] = 0.0
            
        np.clip(new_chi_D, 0.0, 1.0, out=new_chi_D)
        np.fill_diagonal(new_chi_D, 0)

        # Commit State
        self.chi_D = new_chi_D
        self.R = 0.95 * current_R + 0.05 * self.chi_D

        self._update_metrics(t)

    def _update_metrics(self, t):
        E_global = np.sum(self.chi_D)
        survival_rate = np.sum(self.chi_D > self.epsilon) / (self.N * (self.N - 1))
        
        # Triadic Closure Detection
        B = (self.chi_D > self.epsilon) & (np.abs(self.chi_D - self.chi_D.T) > 1e-3)
        B_int = B.astype(int)
        
        T = np.einsum('ij,jk,ki->ijk', B_int, B_int, B_int) > 0
        idx = np.arange(self.N)
        T[idx, idx, :] = False
        T[:, idx, idx] = False
        T[idx, :, idx] = False
        
        tc_count = np.sum(T) // 3

        self.history.append({
            "iteration": t,
            "E_global": E_global,
            "survival_rate": survival_rate,
            "tc_count": tc_count
        })

    def run(self, iterations):
        for t in range(iterations):
            self.step(t)
            
        final_metrics = self.history[-1] if self.history else {}
        
        # Calculate divergence before and after perturbation
        pre_perturb = next((h["tc_count"] for h in self.history if h["iteration"] == 499), 0)
        post_perturb = final_metrics.get("tc_count", 0)
        
        # Recovery ratio: how many closures survived the perturbation?
        recovery_ratio = post_perturb / pre_perturb if pre_perturb > 0 else 0.0
        
        return {
            "model": self.model_type,
            "seed": self.seed,
            "E_global": final_metrics.get("E_global", 0),
            "survival_rate": final_metrics.get("survival_rate", 0),
            "final_tc_count": post_perturb,
            "recovery_ratio": recovery_ratio,
            "collapse": self.collapse
        }

def run_campaign(N=64, iterations=1000, epsilon=0.05, num_seeds=20):
    models = [
        "M0_full_aRT", 
        "M1_simple_ablation", 
        "M2_substituted_orientation", 
        "M3_substituted_residue", 
        "M4_random_shuffle", 
        "M5_trace_preserving"
    ]
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    out_dir = Path(f"results/{date_str}_run01_MPF_SIM_ART_001")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    print(f"Starting aRT Deformation Campaign (N={N}, iter={iterations}, seeds={num_seeds})")
    
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = []
        for model in models:
            for seed in range(num_seeds):
                sim = ARTSim(N, epsilon, model, seed)
                futures.append(executor.submit(sim.run, iterations))
                
        for i, f in enumerate(concurrent.futures.as_completed(futures)):
            res = f.result()
            results.append(res)
            if (i+1) % 20 == 0:
                print(f"  Progress: {i+1}/{len(models)*num_seeds} trials completed.")
                
    df = pd.DataFrame(results)
    df.to_csv(out_dir / "metrics_by_seed.csv", index=False)
    
    summary = df.groupby("model").agg({
        "E_global": "mean",
        "survival_rate": "mean",
        "final_tc_count": "mean",
        "recovery_ratio": "mean",
        "collapse": "mean"
    }).reset_index()
    
    print("\nSimulation Summary:")
    print(summary.to_string(index=False))
    
    m0_rec = summary.loc[summary["model"] == "M0_full_aRT", "recovery_ratio"].values[0]
    m1_rec = summary.loc[summary["model"] == "M1_simple_ablation", "recovery_ratio"].values[0]
    m2_rec = summary.loc[summary["model"] == "M2_substituted_orientation", "recovery_ratio"].values[0]
    m3_rec = summary.loc[summary["model"] == "M3_substituted_residue", "recovery_ratio"].values[0]
    m4_rec = summary.loc[summary["model"] == "M4_random_shuffle", "recovery_ratio"].values[0]
    m5_rec = summary.loc[summary["model"] == "M5_trace_preserving", "recovery_ratio"].values[0]
    
    m4_surv = summary.loc[summary["model"] == "M4_random_shuffle", "survival_rate"].values[0]
    m0_surv = summary.loc[summary["model"] == "M0_full_aRT", "survival_rate"].values[0]
    
    audit = {
        "ART_SIM_001_M1_fails": "PASS" if m1_rec < 0.5 * m0_rec else "FAIL",
        "ART_SIM_002_M2_survives": "PASS" if m2_rec > 0.5 * m0_rec else "FAIL",
        "ART_SIM_003_M3_survives": "PASS" if m3_rec > 0.5 * m0_rec else "FAIL",
        "ART_SIM_004_M4_fails": "PASS" if m4_rec < 0.5 * m0_rec or m4_surv > 0.99 else "FAIL",
        "ART_SIM_005_M5_survives": "PASS" if m5_rec > 0.5 * m0_rec else "FAIL"
    }
    
    with open(out_dir / "falsification_audit.json", "w") as f:
        json.dump(audit, f, indent=2)
        
    with open(out_dir / "simulation_summary.md", "w") as f:
        f.write("# MPF_SIM_ART_001 Summary\n\n")
        f.write("Exploratory validation of Whole-Expression RT deformations vs isolated component ablation.\n\n")
        f.write("```\n")
        f.write(summary.to_string(index=False))
        f.write("\n```\n")

    print(f"\nCampaign completed. Artifacts saved to {out_dir}")

if __name__ == "__main__":
    run_campaign()
