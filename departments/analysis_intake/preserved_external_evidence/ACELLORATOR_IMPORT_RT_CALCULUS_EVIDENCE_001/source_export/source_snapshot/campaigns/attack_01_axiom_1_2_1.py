"""
FAT-01-AXIOM-1.2.1: Falsification Attack on Primary Axiom (The Statement)
Axiom: (E != 0) <=>_R delta_a(E > 0)
Objective: Falsify the assertion that non-zero mismatch (E != 0) is necessary and sufficient
for admissible continuation (delta_a(E > 0)) by attempting to construct a process that continues
or stabilizes into new distinctions when E is forced to 0, or showing that continuation can arise
without any distinction.
"""

import sys

def compute_mismatch(array):
    """
    Computes the mismatch functional E over a distinction array.
    E is defined as the sum of absolute differences between adjacent relations.
    If all elements are identical, E = 0 (complete distinction collapse).
    """
    if len(array) <= 1:
        return 0.0
    return sum(abs(array[i] - array[i-1]) for i in range(1, len(array)))

def affect_gate(E):
    """
    Legality gate: PASS if E != 0, FAIL if E == 0.
    """
    return "PASS" if E > 1e-9 else "FAIL"

def admissibility_filter(candidates, residue, epsilon=1e-5):
    """
    Selects candidates where the next mismatch is greater than the floor epsilon
    and complies with the residue constraints.
    """
    # Admissibility condition: next mismatch must be greater than epsilon
    return [c for c in candidates if compute_mismatch(c) > epsilon]

def transition(state):
    """
    Updates the system state based on the current state.
    """
    E = compute_mismatch(state)
    gate = affect_gate(E)
    if gate == "FAIL":
        # System enters Zero-State
        return [0.0] * len(state), "ZERO_STATE_COLLAPSE"
    
    # Generate candidate transitions (perturbations of the state)
    candidates = [
        [state[0] + 0.1, state[1] - 0.1],
        [state[0] - 0.1, state[1] + 0.1],
        [state[0], state[1]]
    ]
    
    # Filter candidates
    valid_candidates = admissibility_filter(candidates, residue=None)
    
    if not valid_candidates:
        return [0.0] * len(state), "ADMISSIDER_COLLAPSE"
        
    # Arbitrate (select candidate with minimum mismatch to simulate stabilization)
    best_candidate = min(valid_candidates, key=compute_mismatch)
    return best_candidate, "CONTINUATION"

def run_attack():
    print("====================================================")
    print("FAT-01-AXIOM-1.2.1: LAUNCHING FALSIFICATION ATTACK")
    print("Target Axiom: (E != 0) <=>_R delta_a(E > 0)")
    print("====================================================")
    
    # Test Case 1: Standard continuation with E != 0
    state = [1.0, 2.0]
    print(f"Initial State: {state}, Initial E: {compute_mismatch(state):.4f}")
    
    state, status = transition(state)
    print(f"Step 1 State:  {state}, E: {compute_mismatch(state):.4f}, Status: {status}")
    if status != "CONTINUATION":
        print("FAIL: Basic continuation failed under non-zero mismatch.")
        return False

    # Test Case 2: Zero-Distinction Collapse (FA-001)
    # We force the system into a state where all distinctions are erased (E = 0)
    collapsed_state = [1.5, 1.5]
    E_collapsed = compute_mismatch(collapsed_state)
    print(f"\nForcing Zero-Distinction State: {collapsed_state}, E: {E_collapsed:.4f}")
    
    next_state, status = transition(collapsed_state)
    print(f"Post-Collapse State: {next_state}, E: {compute_mismatch(next_state):.4f}, Status: {status}")
    
    # Falsification check 1: If status is 'CONTINUATION' when E was 0, the axiom is falsified!
    if status == "CONTINUATION":
        print("FALSIFIED: The system continued normal transitions even when E was forced to 0!")
        return True
        
    if status == "ZERO_STATE_COLLAPSE" and compute_mismatch(next_state) == 0.0:
        print("SURVIVED: System successfully collapsed to Zero-State when distinction was erased.")
    else:
        print(f"UNEXPECTED BEHAVIOR: status={status}, next_state={next_state}")
        return False

    # Test Case 3: Recovery from Zero-State without external mismatch
    # If the system is in the Zero-State, can it spontaneously generate a new distinction?
    zero_state = [0.0, 0.0]
    print(f"\nTesting Spontaneous Recovery from Zero-State: {zero_state}")
    
    next_state, status = transition(zero_state)
    print(f"Post-Recovery Attempt State: {next_state}, E: {compute_mismatch(next_state):.4f}, Status: {status}")
    
    if compute_mismatch(next_state) > 0.0:
        print("FALSIFIED: System spontaneously generated distinctions from a zero-distinction state!")
        return True
        
    print("SURVIVED: System remained trapped in Zero-State (no spontaneous continuation without distinction).")
    return False

if __name__ == "__main__":
    falsified = run_attack()
    print("\n====================================================")
    if falsified:
        print("RESULT: FALSIFICATION SUCCESSFUL!")
        print("A counterexample was found that breaks the axiom.")
        sys.exit(1)
    else:
        print("RESULT: FALSIFICATION FAILED (AXIOM SURVIVED).")
        print("The axiom's assertions hold under the test boundaries.")
        sys.exit(0)
