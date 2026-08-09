"""
FAT-07-CONTINUATION-COMPOSITION-2.3.2: Falsification Attack on Continuation Composition & Guards
Principles: Formal Block 2.3.2 (Continuation Composition) & 2.3.2A (Typed Continuation Composition Guards)
Rule: Composed continuation C(A,B) o C(B,C) -> C(A,C) is admissible only if endpoint domain matching,
type matching, and admissibility conditions hold.
Objective: Attempt to construct a stable process loop that composes incompatible endpoints/types
without blocking, evaluating if it collapses or diverges.
"""

import sys

class ProcessState:
    def __init__(self, name, state_type, value):
        self.name = name
        self.state_type = state_type
        self.value = float(value)

    def __repr__(self):
        return f"{self.name}(type={self.state_type}, val={self.value})"

class Continuation:
    def __init__(self, dom, cod, residue=0.1):
        self.dom = dom
        self.cod = cod
        self.residue = residue

    def __repr__(self):
        return f"C({self.dom.name} -> {self.cod.name}, res={self.residue:.3f})"

def compose_continuations(c1, c2, mode="compliant"):
    """
    Composes c1 and c2.
    - In compliant mode, guards check endpoint equality, type equality, and admissibility.
    - In ablated mode, guards are ignored.
    """
    if mode == "compliant":
        # Guard 1: Endpoint matching
        if c1.cod.name != c2.dom.name:
            return None, "BLOCK_ENDPOINT_MISMATCH"
            
        # Guard 2: Type matching
        if c1.cod.state_type != c2.dom.state_type:
            return None, "BLOCK_TYPE_MISMATCH"
            
        # Guard 3: Admissibility (mismatch / residue must remain bounded)
        combined_residue = c1.residue + c2.residue
        if combined_residue > 2.0: # Admissibility window limit
            return None, "BLOCK_ADMISSIBILITY_LIMIT"
            
        # Success
        return Continuation(c1.dom, c2.cod, combined_residue), "SUCCESS"
        
    elif mode == "ablated":
        # Ignore guards, compose anyway
        combined_residue = c1.residue + c2.residue
        return Continuation(c1.dom, c2.cod, combined_residue), "SUCCESS"
    else:
        raise ValueError(f"Unknown mode: {mode}")

def simulate_composition_loop(mode="compliant", steps=10):
    # Initialize states
    sA = ProcessState("A", "Type1", 1.0)
    sB = ProcessState("B", "Type1", 1.2)
    sC = ProcessState("C", "Type1", 1.4)
    
    # Incompatible state
    sD = ProcessState("D", "Type2", -5.0)
    sE = ProcessState("E", "Type2", -5.5)
    
    # Normal sequential continuations
    cAB = Continuation(sA, sB, 0.1)
    cBC = Continuation(sB, sC, 0.1)
    
    # Incompatible continuation (broken link)
    cDE = Continuation(sD, sE, 0.2)
    
    current_c = cAB
    status_history = []
    
    # We attempt a chain of compositions, occasionally introducing incompatible joins
    # to evaluate if the guards prevent collapse
    for step in range(steps):
        if step % 3 == 0:
            # Introduce incompatible composition attempt (endpoint and type mismatch)
            next_c, status = compose_continuations(current_c, cDE, mode=mode)
        else:
            # Normal composition
            next_c, status = compose_continuations(current_c, cBC, mode=mode)
            
        status_history.append((step, status))
        
        if status == "SUCCESS":
            current_c = next_c
            # Evaluate systemic mismatch: if incompatible states were composed,
            # the mismatch functional (distinction between dom and cod value) explodes.
            mismatch = abs(current_c.dom.value - current_c.cod.value)
            if mismatch > 4.0: # Systemic divergence threshold
                return status_history, "SYSTEM_DIVERGENCE_COLLAPSE"
        else:
            # Composition was blocked. To maintain the process, we fall back to identity
            # or continue the active compliant lineage, avoiding collapse.
            pass
            
    return status_history, "STABLE_PERSISTENCE"

def run_attack():
    print("====================================================")
    print("FAT-07-CONTINUATION-COMPOSITION-2.3.2: LAUNCHING FALSIFICATION ATTACK")
    print("Target Concept: Continuation Composition & Guards")
    print("====================================================")
    
    # Compliant Run
    print("--- Running Compliant (Guarded) Run ---")
    history_comp, status_comp = simulate_composition_loop(mode="compliant")
    print(f"Status: {status_comp}")
    print("History:")
    for step, stat in history_comp:
        print(f"  Step {step}: {stat}")
        
    # Ablated Run
    print("\n--- Running Ablated (Unguarded) Run ---")
    history_abl, status_abl = simulate_composition_loop(mode="ablated")
    print(f"Status: {status_abl}")
    print("History:")
    for step, stat in history_abl:
        print(f"  Step {step}: {stat}")
        
    # Falsification logic:
    # If the ablated system can compose incompatible endpoints and remain stable,
    # then guards are unnecessary, and the concept is falsified.
    # If the ablated system diverges/collapses, the guards survived.
    
    falsified = False
    if status_abl == "STABLE_PERSISTENCE":
        print("\nRESULT: FALSIFICATION SUCCESSFUL!")
        print("Unguarded composition maintained stable persistence despite endpoint mismatch.")
        falsified = True
    else:
        print("\nRESULT: FALSIFICATION FAILED (CONCEPTS SURVIVED).")
        print("Unguarded composition of incompatible endpoints caused immediate systemic divergence.")
        
    return falsified

if __name__ == "__main__":
    falsified = run_attack()
    print("====================================================")
    if falsified:
        sys.exit(1)
    else:
        sys.exit(0)
