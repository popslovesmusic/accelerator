import numpy as np
import json
import os
from pathlib import Path
from datetime import datetime

class RelationalBasinAnalyzer:
    def __init__(self, output_dir="results/cls_004R_relational_analysis"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_sigma_r(self, orientation_vecs, threshold=0.1):
        """
        Extracts Relational Signature Sigma_R = (Wa, rho_D, chi, R_minus_i, M_dom)
        """
        magnitudes = np.linalg.norm(orientation_vecs, axis=1)
        M_dom = float(np.max(magnitudes))
        
        # 1. Rotational Character (chi)
        cross_products = []
        for i in range(len(orientation_vecs) - 1):
            v1 = orientation_vecs[i]
            v2 = orientation_vecs[i+1]
            cross = v1[0]*v2[1] - v1[1]*v2[0]
            cross_products.append(cross)
        chi = "CCW" if np.mean(cross_products) > 0 else "CW"
        
        # 2. Distinction Density (rho_D)
        # Weighted mean of magnitudes relative to M_dom
        rho_D = float(np.mean(magnitudes) / M_dom) if M_dom > 0 else 0.0
        
        # 3. Orientation Event Structure (R_minus_i)
        # Detect significant shifts in orientation angle
        angles = np.arctan2(orientation_vecs[:, 1], orientation_vecs[:, 0])
        events = []
        last_angle = angles[0]
        for a in angles[1:]:
            if abs(a - last_angle) > threshold:
                events.append(round(float(a), 2))
                last_angle = a
        R_minus_i = events
        
        # 4. Admissibility Window (Wa)
        # Classify the phase bounds
        min_angle, max_angle = np.min(angles), np.max(angles)
        Wa = {
            "lower_bound": round(float(min_angle), 4),
            "upper_bound": round(float(max_angle), 4),
            "width": round(float(max_angle - min_angle), 4)
        }
        
        signature = {
            "M_dom": round(M_dom, 4),
            "rho_D": round(rho_D, 4),
            "chi": chi,
            "R_minus_i": R_minus_i,
            "Wa": Wa,
            "id": f"SIG_R_{chi}_{round(rho_D, 2)}_{len(R_minus_i)}"
        }
        
        return signature

    def generate_synthetic_process(self, seed, noise=0.0):
        np.random.seed(seed)
        t = np.linspace(0, 2*np.pi, 200)
        
        # More complex process-like curve (superposition of two modes)
        m1 = 1.0 + np.random.uniform(-0.1, 0.1)
        m2 = 0.3 * np.sin(3*t)
        
        x = (m1 + m2) * np.cos(t)
        y = (m1 + m2) * 0.5 * np.sin(t)
        
        vecs = np.stack([x, y], axis=1)
        if noise > 0:
            vecs += np.random.normal(0, noise, vecs.shape)
            
        return vecs

    def run_validation_suite(self, n=20, perturbation=0.05):
        print(f"[CLS_004R] Commencing Relational Validation (n={n}, pert={perturbation})...")
        results = []
        
        for i in range(n):
            # Original
            vecs1 = self.generate_synthetic_process(seed=i*100)
            sig1 = self.extract_sigma_r(vecs1)
            
            # Perturbed
            vecs2 = self.generate_synthetic_process(seed=i*100, noise=perturbation)
            sig2 = self.extract_sigma_r(vecs2)
            
            # Stability Checks
            match_chi = sig1["chi"] == sig2["chi"]
            match_rho = abs(sig1["rho_D"] - sig2["rho_D"]) < perturbation
            match_wa = abs(sig1["Wa"]["width"] - sig2["Wa"]["width"]) < perturbation * 2
            
            results.append({
                "index": i,
                "sig1": sig1,
                "sig2": sig2,
                "chi_stable": match_chi,
                "rho_stable": match_rho,
                "wa_stable": match_wa
            })
            
        summary = {
            "total": n,
            "chi_stability": sum(r["chi_stable"] for r in results) / n,
            "rho_stability": sum(r["rho_stable"] for r in results) / n,
            "wa_stability": sum(r["wa_stable"] for r in results) / n
        }
        
        with open(self.output_dir / "relational_validation_results.json", "w") as f:
            json.dump({"summary": summary, "results": results}, f, indent=2)
            
        print(f"[SUCCESS] Relational validation complete.")
        print(f"  Chi Stability: {summary['chi_stability']*100}%")
        print(f"  Rho Stability: {summary['rho_stability']*100}%")
        print(f"  Wa Stability:  {summary['wa_stability']*100}%")
        
        return summary

if __name__ == "__main__":
    analyzer = RelationalBasinAnalyzer()
    analyzer.run_validation_suite()
