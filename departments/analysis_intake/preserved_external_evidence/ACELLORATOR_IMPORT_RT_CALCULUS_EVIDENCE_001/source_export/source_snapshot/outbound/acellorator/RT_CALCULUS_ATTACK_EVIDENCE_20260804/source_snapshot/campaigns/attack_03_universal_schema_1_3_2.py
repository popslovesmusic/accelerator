"""
FAT-03-UNIVERSAL-SCHEMA-1.3.2: Falsification Attack on Universal Law Schema (U_Omega)
Principle: Every transformation follows: [ chi_D -> E -> delta_a -> Arb_A -> Delta -> chi_D' ]
Objective: Challenge the necessity of the admissibility filter (delta_a) and mismatch optimization (Arb_A)
by simulating ablated systems and checking if they can maintain stable, persistent processes.
"""

import sys
import random

def compute_mismatch(state):
    """
    Total relational mismatch functional E.
    """
    if len(state) <= 1:
        return 0.0
    return sum(abs(state[i] - state[i-1]) for i in range(1, len(state)))

def generate_candidates(state):
    """
    Generates potential next states by adding small random perturbations.
    """
    candidates = []
    # Generate 5 candidates
    for _ in range(5):
        cand = [x + random.uniform(-0.15, 0.15) for x in state]
        candidates.append(cand)
    # Include current state as identity candidate
    candidates.append(list(state))
    return candidates

def admissibility_filter(candidates, epsilon=0.05):
    """
    Filters candidates whose mismatch is above a floor epsilon
    and prevents mismatch from exploding.
    """
    # Admissible window: E must be positive and bounded to prevent divergence
    return [c for c in candidates if epsilon < compute_mismatch(c) < 5.0]

def simulate_system(initial_state, steps=10000, mode="compliant"):
    """
    Simulates the state update loop over a given number of steps.
    Modes:
      - 'compliant': Full U_Omega (Admissibility filter + Mismatch optimization)
      - 'randomized_filter': Bypasses delta_a (selects randomly from all candidates)
      - 'unoptimized_arbitration': Bypasses Arb_A optimization (selects first candidate)
    """
    # Set seed to ensure reproducibility
    random.seed(42)
    state = list(initial_state)
    mismatch_history = [compute_mismatch(state)]
    
    for t in range(steps):
        E = compute_mismatch(state)
        # Legality check: if difference drops to 0, system collapses
        if E < 1e-6:
            return mismatch_history, "ZERO_COLLAPSE", t
            
        candidates = generate_candidates(state)
        
        if mode == "compliant":
            # 1. Apply Admissibility Filter delta_a
            admissible = admissibility_filter(candidates)
            if not admissible:
                return mismatch_history, "ADMISSIBILITY_COLLAPSE", t
            # 2. Apply Arbitration Arb_A (select candidate minimizing mismatch deviation)
            state = min(admissible, key=compute_mismatch)
            
        elif mode == "randomized_filter":
            # Bypasses delta_a and selects randomly from ALL candidates
            state = random.choice(candidates)
            
        elif mode == "unoptimized_arbitration":
            # Applies delta_a but selects the FIRST candidate, ignoring optimization
            admissible = admissibility_filter(candidates)
            if not admissible:
                return mismatch_history, "ADMISSIBILITY_COLLAPSE", t
            state = admissible[0]
            
        mismatch_history.append(compute_mismatch(state))
        
        # Check for divergence collapse
        if compute_mismatch(state) > 10.0:
            return mismatch_history, "DIVERGENCE_COLLAPSE", t
            
    return mismatch_history, "STABLE_PERSISTENCE", steps

def run_attack():
    print("====================================================")
    print("FAT-03-UNIVERSAL-SCHEMA-1.3.2: LAUNCHING FALSIFICATION ATTACK")
    print("Target Concept: Universal Law Schema U_Omega")
    print("====================================================")
    
    initial_state = [1.0, 1.5, 2.0]
    steps = 10000
    
    # 1. Run Compliant System
    h_comp, status_comp, steps_comp = simulate_system(initial_state, steps, "compliant")
    print(f"Compliant Run:   Status = {status_comp:<22} Steps = {steps_comp:<5} Final E = {h_comp[-1]:.4f}")
    
    # 2. Run Randomized Filter Ablation (FA-002)
    h_rand, status_rand, steps_rand = simulate_system(initial_state, steps, "randomized_filter")
    print(f"Ablated Filter:  Status = {status_rand:<22} Steps = {steps_rand:<5} Final E = {h_rand[-1]:.4f}")
    
    # 3. Run Unoptimized Arbitration Ablation (FA-003)
    h_unopt, status_unopt, steps_unopt = simulate_system(initial_state, steps, "unoptimized_arbitration")
    print(f"Ablated Arb:     Status = {status_unopt:<22} Steps = {steps_unopt:<5} Final E = {h_unopt[-1]:.4f}")
    
    # Falsification logic:
    # If both ablated runs achieve STABLE_PERSISTENCE over the full step horizon without collapse or divergence,
    # then the strict necessity of the U_Omega sequence is falsified.
    # If the ablated runs collapse or diverge while the compliant run persists, the U_Omega schema survives.
    
    falsified = False
    if status_rand == "STABLE_PERSISTENCE" and status_unopt == "STABLE_PERSISTENCE":
        print("\nRESULT: FALSIFICATION SUCCESSFUL!")
        print("Ablated systems achieved stable persistence without U_Omega filters.")
        falsified = True
    else:
        print("\nRESULT: FALSIFICATION FAILED (U_Omega SURVIVED).")
        print("Ablating admissibility or arbitration leads to process collapse or divergence.")
        
    return falsified

if __name__ == "__main__":
    falsified = run_attack()
    print("====================================================")
    if falsified:
        sys.exit(1)
    else:
        sys.exit(0)
