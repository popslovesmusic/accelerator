"""
FAT-10-DIRECTED-DISTINCTION-3.1.1: Falsification Attack on Directed Distinction & Asymmetry
Principle: Formal Statement 3.1.1: Directed Distinction
Rule: The distinction relation D(S1|S2) is directed and asymmetric (D(S1|S2) != D(S2|S1)),
generating the relational gradients required to drive state transitions.
Objective: Attempt to run an update loop under a strictly symmetric distinction relation
(D(S1|S2) = D(S2|S1)), evaluating if it can drive transitions without freezing.
"""

import sys

def simulate_transition_loop(mode="asymmetric", steps=50):
    state = 0.0
    target = 5.0
    
    state_history = [state]
    
    for t in range(steps):
        if mode == "asymmetric":
            # Asymmetric distinction: D(x|y) = x - 0.9 * y
            D_forward = state - 0.9 * target
            D_reverse = target - 0.9 * state
        elif mode == "symmetric":
            # Symmetric distinction: D(x|y) = |x - y|
            D_forward = abs(state - target)
            D_reverse = abs(target - state)
        else:
            raise ValueError(f"Unknown mode: {mode}")
            
        # Relational gradient driving force
        gradient = D_forward - D_reverse
        
        # State update step
        if abs(gradient) < 1e-6:
            # If gradient is zero, the driving force collapses and updates cease
            return state_history, "ZERO_GRADIENT_HALT"
            
        state = state - 0.1 * gradient
        state_history.append(state)
        
    return state_history, "SUCCESSFUL_CONVERGENCE"

def run_attack():
    print("====================================================")
    print("FAT-10-DIRECTED-DISTINCTION-3.1.1: LAUNCHING FALSIFICATION ATTACK")
    print("Target Concept: Directed Distinction & Asymmetry")
    print("====================================================")
    
    # Compliant Run (Asymmetric)
    print("--- Running Compliant (Asymmetric) Run ---")
    hist_asym, status_asym = simulate_transition_loop(mode="asymmetric")
    print(f"Status: {status_asym}, Steps: {len(hist_asym)}, Final State: {hist_asym[-1]:.4f}")
    
    # Ablated Run (Symmetric)
    print("\n--- Running Ablated (Symmetric) Run ---")
    hist_sym, status_sym = simulate_transition_loop(mode="symmetric")
    print(f"Status: {status_sym}, Steps: {len(hist_sym)}, Final State: {hist_sym[-1]:.4f}")
    
    # Falsification logic:
    # If the symmetric system successfully converges or moves toward target,
    # the necessity of directed (asymmetric) distinction is falsified.
    # If the symmetric system freezes immediately, the concept survived.
    
    falsified = False
    if status_sym == "SUCCESSFUL_CONVERGENCE" or len(hist_sym) > 2:
        # If it ran for more than 1 step without freezing
        if abs(hist_sym[-1] - 0.0) > 1e-4:
            print("\nRESULT: FALSIFICATION SUCCESSFUL!")
            print("Symmetric distinction successfully drove updates without freezing.")
            falsified = True
            return falsified
            
    print("\nRESULT: FALSIFICATION FAILED (CONCEPTS SURVIVED).")
    print("Symmetric distinction resulted in zero gradient, immediately freezing state updates.")
    return falsified

if __name__ == "__main__":
    falsified = run_attack()
    print("====================================================")
    if falsified:
        sys.exit(1)
    else:
        sys.exit(0)
