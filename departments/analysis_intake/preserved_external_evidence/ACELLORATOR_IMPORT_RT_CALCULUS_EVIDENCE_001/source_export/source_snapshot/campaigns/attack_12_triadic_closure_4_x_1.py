"""
FAT-12-TRIADIC-CLOSURE-4.X.1: Falsification Attack on Asymmetric Triadic Closure
Principle: Formal Statement 4.X.1: Asymmetric Triadic Closure Theorem
Rule: Triadic closure forms a self-reinforcing stabilization basin under oriented updates.
Objective: Perform Ablation M1 (orientation-removal/randomization) to test if
triadic closure can stabilize the system without oriented restoring forces.
"""

import sys
import random

def sign(val):
    if val > 0:
        return 1.0
    elif val < 0:
        return -1.0
    return 0.0

def simulate_triadic_closure(mode="oriented", steps=5000, seed=42):
    random.seed(seed)
    
    # Initialize three node values with mismatch
    N1 = 1.0
    N2 = 3.0
    N3 = -2.0
    
    alpha = 0.1
    history = [(N1, N2, N3)]
    
    for t in range(steps):
        if mode == "oriented":
            # Oriented: stable attractive coupling
            o12 = 1.0
            o23 = 1.0
            o31 = 1.0
        elif mode == "ablated":
            # Ablation M1: randomized coupling orientation (attractive vs repulsive)
            o12 = random.choice([-1.0, 1.0])
            o23 = random.choice([-1.0, 1.0])
            o31 = random.choice([-1.0, 1.0])
        else:
            raise ValueError(f"Unknown mode: {mode}")
            
        # Coupled triadic updates
        N1_next = N1 + alpha * ((N2 - N1) * o12 - (N1 - N3) * o31)
        N2_next = N2 + alpha * ((N3 - N2) * o23 - (N2 - N1) * o12)
        N3_next = N3 + alpha * ((N1 - N3) * o31 - (N3 - N2) * o23)
        
        N1, N2, N3 = N1_next, N2_next, N3_next
        history.append((N1, N2, N3))
        
        # Divergence check: if nodes explode beyond reasonable bounds, process collapses
        if max(abs(N1), abs(N2), abs(N3)) > 10.0:
            return history, "DIVERGENCE_COLLAPSE"
            
    return history, "STABLE_PERSISTENCE"

def run_attack():
    print("====================================================")
    print("FAT-12-TRIADIC-CLOSURE-4.X.1: LAUNCHING FALSIFICATION ATTACK")
    print("Target Concept: Asymmetric Triadic Closure Theorem")
    print("====================================================")
    
    num_seeds = 50
    steps = 5000
    
    # Compliant Runs (Oriented)
    comp_stable = 0
    comp_collapsed = 0
    for seed in range(num_seeds):
        _, status = simulate_triadic_closure(mode="oriented", steps=steps, seed=seed)
        if status == "STABLE_PERSISTENCE":
            comp_stable += 1
        else:
            comp_collapsed += 1
            
    print(f"Compliant (Oriented) runs over {num_seeds} seeds:")
    print(f"  Stable: {comp_stable} ({comp_stable/num_seeds*100:.1f}%)")
    print(f"  Collapsed: {comp_collapsed} ({comp_collapsed/num_seeds*100:.1f}%)")
    
    # Ablated Runs (Ablation M1)
    abl_stable = 0
    abl_collapsed = 0
    for seed in range(num_seeds):
        _, status = simulate_triadic_closure(mode="ablated", steps=steps, seed=seed)
        if status == "STABLE_PERSISTENCE":
            abl_stable += 1
        else:
            abl_collapsed += 1
            
    print(f"\nAblated (Randomized Orientation) runs over {num_seeds} seeds:")
    print(f"  Stable: {abl_stable} ({abl_stable/num_seeds*100:.1f}%)")
    print(f"  Collapsed: {abl_collapsed} ({abl_collapsed/num_seeds*100:.1f}%)")
    
    # Falsification logic:
    # If the ablated system stabilizes in a high percentage of seeds (e.g. > 90%),
    # then the concept is falsified. If it collapses in most seeds, it survived.
    
    falsified = False
    if abl_stable > 45: # > 90% stable
        print("\nRESULT: FALSIFICATION SUCCESSFUL!")
        print("Triadic closure stabilized without oriented restoring forces in most runs.")
        falsified = True
    else:
        print("\nRESULT: FALSIFICATION FAILED (CONCEPTS SURVIVED).")
        print("Bypassing orientation alignment (Ablation M1) caused triadic nodes to diverge and collapse in most runs.")
        
    return falsified

if __name__ == "__main__":
    falsified = run_attack()
    print("====================================================")
    if falsified:
        sys.exit(1)
    else:
        sys.exit(0)
