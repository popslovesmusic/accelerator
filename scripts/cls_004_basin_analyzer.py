import numpy as np
import json
import os
from pathlib import Path
from datetime import datetime

class BasinAnalyzer:
    def __init__(self, output_dir="results/cls_004_basin_analysis"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_signature(self, t, orientation_vecs):
        """
        Extracts signature Sigma = (M_peak, M_valley, M_dom, leg_order, rotation, quadrant_occupancy)
        orientation_vecs: Nx2 array of (x, y) orientation components
        """
        magnitudes = np.linalg.norm(orientation_vecs, axis=1)
        
        # 1. Locate peak and valley
        peak_idx = np.argmax(magnitudes)
        valley_idx = np.argmin(magnitudes)
        
        M_peak = float(magnitudes[peak_idx])
        M_valley = float(magnitudes[valley_idx])
        
        # 5. dominant magnitude
        M_dom = max(M_peak, M_valley)
        
        # 4. Leg order
        leg_order = ["peak", "valley"] if peak_idx < valley_idx else ["valley", "peak"]
        
        # 6. Rotation (CW or CCW)
        # Simplified: check cross product sign of consecutive vectors
        cross_products = []
        for i in range(len(orientation_vecs) - 1):
            v1 = orientation_vecs[i]
            v2 = orientation_vecs[i+1]
            cross = v1[0]*v2[1] - v1[1]*v2[0]
            cross_products.append(cross)
        
        avg_cross = np.mean(cross_products)
        rotation = "CCW" if avg_cross > 0 else "CW"
        
        # 7. Quadrant occupancy
        quadrants = []
        for v in orientation_vecs:
            if v[0] >= 0 and v[1] >= 0: q = "++"
            elif v[0] >= 0 and v[1] < 0: q = "+-"
            elif v[0] < 0 and v[1] < 0: q = "--"
            else: q = "-+"
            
            if not quadrants or quadrants[-1] != q:
                quadrants.append(q)
        
        signature = {
            "M_peak": round(M_peak, 4),
            "M_valley": round(M_valley, 4),
            "M_dom": round(M_dom, 4),
            "leg_order": leg_order,
            "rotation": rotation,
            "quadrant_occupancy": quadrants
        }
        
        # Generate hash-like string for signature
        sig_str = f"SIG_{M_dom}_{rotation}_{''.join(quadrants)}"
        signature["id"] = sig_str
        
        return signature

    def generate_basin(self, seed, noise=0.0):
        """
        Generates a synthetic basin curve.
        """
        np.random.seed(seed)
        t = np.linspace(0, 2*np.pi, 100)
        
        # Base parameters
        base_mag = 1.0 + np.random.uniform(-0.2, 0.2)
        eccentricity = np.random.uniform(0.1, 0.5)
        phase_offset = np.random.uniform(0, 2*np.pi)
        
        # Elliptical-like orbit in orientation space
        x = base_mag * np.cos(t + phase_offset)
        y = (base_mag * eccentricity) * np.sin(t + phase_offset)
        
        orientation_vecs = np.stack([x, y], axis=1)
        
        if noise > 0:
            orientation_vecs += np.random.normal(0, noise, orientation_vecs.shape)
            
        return t, orientation_vecs

    def run_collision_test(self, n=20):
        print(f"[TEST 2] Commencing Collision Test (n={n})...")
        signatures = {}
        collisions = []
        
        for i in range(n):
            t, vecs = self.generate_basin(seed=i)
            sig = self.extract_signature(t, vecs)
            sig_id = sig["id"]
            
            if sig_id in signatures:
                print(f"  [COLLISION] Basin {i} matches Basin {signatures[sig_id]['index']}")
                collisions.append((i, signatures[sig_id]['index']))
            else:
                signatures[sig_id] = {"index": i, "sig": sig}
        
        result = {
            "total_basins": n,
            "unique_signatures": len(signatures),
            "collisions": collisions,
            "is_class_marker": len(collisions) > 0
        }
        
        with open(self.output_dir / "collision_test_results.json", "w") as f:
            json.dump(result, f, indent=2)
            
        print(f"[SUCCESS] Collision test complete. Class Marker: {result['is_class_marker']}")
        return result

    def run_prediction_test(self, n=5, perturbation=0.05):
        print(f"[TEST 3] Commencing Prediction Test (n={n}, pert={perturbation})...")
        results = []
        
        for i in range(n):
            # Original
            t1, vecs1 = self.generate_basin(seed=i*100)
            sig1 = self.extract_signature(t1, vecs1)
            
            # Perturbed
            t2, vecs2 = self.generate_basin(seed=i*100, noise=perturbation)
            sig2 = self.extract_signature(t2, vecs2)
            
            match_dom = abs(sig1["M_dom"] - sig2["M_dom"]) < perturbation * 2
            match_rot = sig1["rotation"] == sig2["rotation"]
            match_quad = sig1["quadrant_occupancy"] == sig2["quadrant_occupancy"]
            
            results.append({
                "basin_index": i,
                "original_sig": sig1["id"],
                "perturbed_sig": sig2["id"],
                "dom_stable": match_dom,
                "rot_stable": match_rot,
                "quad_stable": match_quad
            })
            
        with open(self.output_dir / "prediction_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
            
        print(f"[SUCCESS] Prediction test complete.")
        return results

if __name__ == "__main__":
    analyzer = BasinAnalyzer()
    
    # Test 1: Signature Extraction (Manual Example)
    t = np.linspace(0, 2*np.pi, 10)
    vecs = np.stack([np.cos(t), np.sin(t)], axis=1) # CCW Circle
    sig = analyzer.extract_signature(t, vecs)
    print(f"[TEST 1] Example Signature: {json.dumps(sig, indent=2)}")
    
    # Test 2
    analyzer.run_collision_test(20)
    
    # Test 3
    analyzer.run_prediction_test(20)
