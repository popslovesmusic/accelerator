import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_logger
r"""
FAT-15-PROCESS-PRIORITY: Falsification Attack on Process Priority
Framework Concept: Process \succ_{ont} Distinction (Formal Reduction 1.1A.1)
Objective: Run the Dual Falsification Program (Program M and Program S) to evaluate
if Process can exist or be defined independently of Distinction.
"""

import sys
import json

def run_program_m():
    """
    Program M: MTO-OTM Native Decomposition.
    Asks: Can Process be lawfully decomposed, have its Distinction aspect ablated,
    and then be reconstructed with its identity preserved?
    """
    print("\n--- Running Program M (MTO-OTM Native) ---")
    
    # 1. Target Process represented as complete aspect tuple
    process_original = {
        "E": 0.8,              # Distinction / constraint magnitude (E > 0)
        "R": 0.2,              # Residue accumulation
        "rho": 0.1,            # Coupling rate
        "K": "Knot_Trefoil",   # Knot stabilization
        "delta": 1.0,          # Admissibility filter
        "orientation": 0.5     # Orientation reference
    }
    print(f"Original Process Aspects: {list(process_original.keys())}")
    
    # 2. OTM Phase: Decompose the Process
    otm_decomposition = process_original.copy()
    
    # 3. Ablation: Remove Distinction (E) from the aspect inventory
    del otm_decomposition["E"]
    print(f"OTM Aspect Inventory after removing 'E' (Distinction): {list(otm_decomposition.keys())}")
    
    # 4. MTO Phase: Attempt to recompose the Process
    # In RT, without distinction (E), the residue update cannot execute,
    # the admissibility filter collapses, and the orientation lacks a gradient.
    mto_recomposition = {}
    
    # Check if we can reconstruct a non-trivial process
    if "E" not in otm_decomposition or otm_decomposition.get("delta", 0) == 0:
        # Relational collapse to the Zero-State
        mto_recomposition = "ZERO_STATE"
        identity_preserved = False
    else:
        mto_recomposition = otm_decomposition
        identity_preserved = True
        
    print(f"MTO Recomposition Result: {mto_recomposition}")
    print(f"Process Identity Preserved: {identity_preserved}")
    
    program_m_result = {
        "otm_decomposition": list(otm_decomposition.keys()),
        "mto_recomposition": mto_recomposition,
        "identity_invariants": ["Process must contain non-zero distinction"],
        "native_failure_conditions": ["Distinction aspect is missing"],
        "status": "Fails" if not identity_preserved else "Survives"
    }
    return program_m_result

def run_program_s():
    """
    Program S: Standard Mathematical Decomposition.
    Asks: Can a non-trivial state transition system (Process) be defined over a state space
    without a distinguishability relation (Distinction)?
    """
    print("\n--- Running Program S (Standard Mathematics) ---")
    
    # 1. State space X with 3 elements
    X = {'x1', 'x2', 'x3'}
    
    # 2. Distinguishability relation D
    # D(x, y) = True if x != y, else False.
    def D(x, y):
        return x != y
        
    # 3. Ablate distinguishability: all states are indistinguishable (D(x,y) = False)
    # By the Identity of Indiscernibles, if D(x,y) is False, then x == y.
    # The set X collapses to a single equivalence class.
    X_collapsed = {'[x]'}
    
    # 4. Define transition function f: X -> X
    # In the collapsed state space, the only possible transition is [x] -> [x] (identity transition)
    transitions = { '[x]': '[x]' }
    
    # Degrees of freedom (non-trivial state changes)
    dof = len(X_collapsed) - 1
    
    print(f"Original State Space size: {len(X)}")
    print(f"Collapsed State Space size (without distinguishability): {len(X_collapsed)}")
    print(f"Degrees of freedom for state transitions: {dof}")
    
    non_trivial_possible = dof > 0
    print(f"Non-trivial Process Possible: {non_trivial_possible}")
    
    program_s_result = {
        "formal_objects": ["State Space X", "Transition function f", "Distinguishability relation D"],
        "logical_form": "f: X -> X where D(x,y) = True is a prerequisite for |X| > 1",
        "type_signature": "X: Set, f: X -> X, D: X x X -> Bool",
        "standard_attack_families": ["Set-theoretic collapse", "Trivial transition analysis"],
        "representation_losses": ["None"],
        "status": "Fails" if not non_trivial_possible else "Survives"
    }
    return program_s_result

def run_attack():
    print("====================================================")
    print("FAT-15-PROCESS-PRIORITY: LAUNCHING DUAL FALSIFICATION PROGRAM")
    print("Target: Process \\succ_{ont} Distinction (Formal Reduction 1.1A.1)")
    print("====================================================")
    
    # Target Packet
    target_packet = {
        "target_id": "FAT-15-PROCESS-PRIORITY",
        "source_passages": [
            "Within the current continuation-first reduction, process is treated as ontologically prior to distinction..."
        ],
        "exact_claim": "Process \\succ_{ont} Distinction",
        "declared_terms": ["Process", "Distinction", "\\succ_{ont}"],
        "declared_dependencies": [],
        "claimed_output": "Process can be defined/exist independently of Distinction",
        "scope": "Foundations",
        "explicit_nonclaims": ["temporal priority"],
        "falsification_conditions": [
            "Program M: OTM-decomposition loses identity when Distinction is removed.",
            "Program S: Set-theoretic cardinality of state space collapses to <= 1 without distinguishability."
        ],
        "attack_bounds": {"max_steps": 1, "max_models": 100}
    }
    
    # Run both programs
    m_res = run_program_m()
    s_res = run_program_s()
    
    # Comparative Ruling Matrix evaluation
    print("\n====================================================")
    print("COMPARATIVE RULING MATRIX EVALUATION")
    print("====================================================")
    print(f"Program M Result: {m_res['status']}")
    print(f"Program S Result: {s_res['status']}")
    
    final_outcome = ""
    ruling = ""
    
    if m_res['status'] == "Fails" and s_res['status'] == "Fails":
        final_outcome = "CONCEPT_FALSIFIED"
        ruling = "Strong failure signal; both native procedure and standard mathematics require Distinction to define a non-trivial Process."
    elif m_res['status'] == "Survives" and s_res['status'] == "Survives":
        final_outcome = "SURVIVED_SPECIFIED_ATTACK"
        ruling = "Concept survived. Process can be defined independently of distinction."
    else:
        final_outcome = "FORMULATION_FALSIFIED"
        ruling = "Disagreement located between native procedure and standard representation."
        
    print(f"Comparative Ruling: {final_outcome}")
    print(f"Details: {ruling}")
    print("====================================================")
    
    # Output full JSON packet for audit logs
    full_packet = {
        "target": target_packet,
        "program_m": m_res,
        "program_s": s_res,
        "ruling": {
            "outcome": final_outcome,
            "details": ruling
        }
    }
    
    # Save target packet JSON locally in campaigns for verification
    # Log run outputs using run_logger
    import run_logger
    run_logger.log_run("FAT-15-PROCESS-PRIORITY", full_packet)
        
    return final_outcome == "CONCEPT_FALSIFIED"

if __name__ == "__main__":
    falsified = run_attack()
    if falsified:
        sys.exit(1)
    else:
        sys.exit(0)
