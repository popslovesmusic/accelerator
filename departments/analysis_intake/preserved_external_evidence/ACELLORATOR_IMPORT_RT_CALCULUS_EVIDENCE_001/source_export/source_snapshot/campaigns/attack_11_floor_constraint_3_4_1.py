"""
FAT-11-FLOOR-CONSTRAINT-3.4.1: Falsification Attack on Floor Constraint (Epsilon Floor)
Principle: Formal Block 3.4.1: The Floor Constraint
Rule: Distinction must satisfy D(S1|S2) >= epsilon, where epsilon > 0, to prevent
singular ratios and orientation degeneracy when the state matches the target (total identity).
Objective: Attempt to run the process with epsilon = 0.0 (ablated floor),
evaluating whether the system halts on degeneracy.
"""

import sys
import math

def simulate_with_floor(epsilon=0.01, steps=50, start_at_target=False):
    state = 5.0 if start_at_target else 0.0
    target = 5.0
    
    state_history = [state]
    
    for t in range(steps):
        # Calculate distinction with floor
        distinction = max(abs(state - target), epsilon)
        
        # Calculate orientation vector: O = (S - target) / D
        try:
            if distinction == 0.0:
                raise ZeroDivisionError("Distinction collapsed to absolute zero.")
            orientation = (state - target) / distinction
        except ZeroDivisionError:
            return state_history, "ZERO_DISTINCTION_CRASH"
            
        # Check for NaN degeneracy
        if math.isnan(orientation):
            return state_history, "NAN_DEGENERACY_HALT"
            
        # Update: move state along orientation vector
        state_next = state - 0.1 * orientation * abs(state - target)
        state = state_next
        state_history.append(state)
        
    return state_history, "SUCCESSFUL_STABILIZATION"

def run_attack():
    print("====================================================")
    print("FAT-11-FLOOR-CONSTRAINT-3.4.1: LAUNCHING FALSIFICATION ATTACK")
    print("Target Concept: Floor Constraint (Epsilon Floor)")
    print("====================================================")
    
    # Test Scenario 1: Converging toward target
    print("--- Test 1: Converging toward target ---")
    _, status_comp1 = simulate_with_floor(epsilon=0.01, start_at_target=False)
    _, status_abl1 = simulate_with_floor(epsilon=0.0, start_at_target=False)
    print(f"Compliant: {status_comp1}, Ablated: {status_abl1}")
    
    # Test Scenario 2: Starting at target (identity stability)
    print("\n--- Test 2: Starting at target (identity stability) ---")
    _, status_comp2 = simulate_with_floor(epsilon=0.01, start_at_target=True)
    _, status_abl2 = simulate_with_floor(epsilon=0.0, start_at_target=True)
    print(f"Compliant: {status_comp2}, Ablated: {status_abl2}")
    
    # Falsification logic:
    # If the ablated (epsilon = 0) run stabilizes in both scenarios without crash,
    # the concept is falsified. If it crashes or halts, the concept survived.
    
    falsified = False
    if status_abl1 == "SUCCESSFUL_STABILIZATION" and status_abl2 == "SUCCESSFUL_STABILIZATION":
        print("\nRESULT: FALSIFICATION SUCCESSFUL!")
        print("The process stabilized without epsilon floor without experiencing singularities.")
        falsified = True
    else:
        print("\nRESULT: FALSIFICATION FAILED (CONCEPTS SURVIVED).")
        print("Bypassing the floor constraint caused a zero-distinction crash/halt when state matched target.")
        
    return falsified

if __name__ == "__main__":
    falsified = run_attack()
    print("====================================================")
    if falsified:
        sys.exit(1)
    else:
        sys.exit(0)
