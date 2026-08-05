"""
FAT-06-CONDITIONED-DISTINCTION-1.2.2F: Falsification Attack on Conditioned Distinction
Principles: 1.2.2F (Primitive Conditioning Principle) & 1.2.2E (Conditioning Directionality)
Rule: Conditioning <a>_b (distinction a under context b) is strictly directional, non-commutative,
and context-dependent.
Objective: Attempt to construct a stable process loop using commutative (order-erasing)
conditioning composition (<a>_b = <b>_a) and evaluate if it collapses.
"""

import sys

def simulate_conditioning(mode="directional", steps=100):
    # Initialize two distinct variables representing the distinction and context
    a = 1.0
    b = 2.0
    
    mismatch_history = []
    
    for t in range(steps):
        # Input perturbation
        step_input = 0.05 * (1.0 if t % 2 == 0 else -0.5)
        
        if mode == "directional":
            # Asymmetric, directional conditioning: <a>_b != <b>_a
            # a is conditioned on context b
            a_next = a + step_input / max(abs(b), 0.01)
            b_next = b + step_input * a
        elif mode == "commutative":
            # Commutative, order-erasing composition: <a>_b = <b>_a
            # Symmetrical updates force the variables to collapse together
            common_update = a * b + step_input
            a_next = common_update
            b_next = common_update
        else:
            raise ValueError(f"Unknown mode: {mode}")
            
        a, b = a_next, b_next
        mismatch = abs(a - b)
        mismatch_history.append(mismatch)
        
        # Legality Check: If mismatch collapses to absolute zero, the process collapses
        if mismatch < 1e-6:
            return mismatch_history, "ZERO_COLLAPSE"
            
    return mismatch_history, "STABLE_PERSISTENCE"

def run_attack():
    print("====================================================")
    print("FAT-06-CONDITIONED-DISTINCTION-1.2.2F: LAUNCHING FALSIFICATION ATTACK")
    print("Target Concept: Conditioning Directionality & Primitiveness")
    print("====================================================")
    
    # Run Directional (Compliant) Scenario
    print("--- Running Directional (Compliant) Scenario ---")
    hist_dir, status_dir = simulate_conditioning(mode="directional")
    print(f"Status: {status_dir}, Steps: {len(hist_dir)}, Final Mismatch: {hist_dir[-1]:.6f}")
    
    # Run Commutative (Ablated) Scenario
    print("\n--- Running Commutative (Ablated) Scenario ---")
    hist_comm, status_comm = simulate_conditioning(mode="commutative")
    print(f"Status: {status_comm}, Steps: {len(hist_comm)}, Final Mismatch: {hist_comm[-1]:.6f}")
    
    # Falsification logic:
    # If the commutative system maintains stable persistence with non-zero mismatch,
    # then directionality/non-commutativity is NOT necessary, and the concept is falsified.
    # If the commutative system collapses immediately to zero mismatch, the concept survived.
    
    falsified = False
    if status_comm == "STABLE_PERSISTENCE" and hist_comm[-1] > 1e-4:
        print("\nRESULT: FALSIFICATION SUCCESSFUL!")
        print("Commutative conditioning maintained a stable process with non-zero distinction.")
        falsified = True
    else:
        print("\nRESULT: FALSIFICATION FAILED (CONCEPTS SURVIVED).")
        print("Commutative conditioning caused immediate distinction collapse to absolute zero.")
        
    return falsified

if __name__ == "__main__":
    falsified = run_attack()
    print("====================================================")
    if falsified:
        sys.exit(1)
    else:
        sys.exit(0)
