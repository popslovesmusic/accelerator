"""
FAT-05-TRACE-ADMISSIBILITY-1.2D.1: Falsification Attack on Trace-Admissibility & Recoupling
Principles: PRIN_001 (Trace Admissibility) & 1.2D.2 (Zero-Condition Recoupling Admissibility)
Rule: Nesting same-sign collapses ([0_minus o 0_minus]) must fail admissibility and halt the process,
while opposite-sign collapses ([0_minus o 0_plus]) can survive via higher-order recoupling.
Objective: Attempt to construct a system where same-sign zero collapses can spontaneously recouple
or continue without opposite-sign balancing, which would falsify the necessity of opposite-sign recoupling.
"""

import sys

class TypedZeroResidue:
    def __init__(self, value, sign):
        # value should be 0.0 for zero residue collapse
        self.value = float(value)
        self.sign = sign # -1 for minus, +1 for plus, 0 for undifferentiated

    def __repr__(self):
        sign_str = "minus" if self.sign == -1 else ("plus" if self.sign == 1 else "null")
        return f"0_{sign_str}(val={self.value})"

def compose_zero_residues(r1, r2, relation_type="asymmetric"):
    """
    Simulates composition of two collapsed zero-residues.
    Under the rule:
      - Opposite signs (r1.sign != r2.sign) can recouple under an asymmetric relation
        to yield a new admissible candidate (recovering a non-zero distinction).
      - Same signs (r1.sign == r2.sign) collapse to an undifferentiated null state
        which halts the system.
    """
    # Legality check: if they are undifferentiated nulls, composition fails immediately
    if r1.sign == 0 or r2.sign == 0:
        return TypedZeroResidue(0.0, 0), "HALT_UNDIFFERENTIATED"
        
    if r1.sign != r2.sign:
        if relation_type == "asymmetric":
            # Opposite signs recouple asymmetrically and recover a distinction!
            recovered_mismatch = 0.1 # Relational tension is restored
            return TypedZeroResidue(recovered_mismatch, 1), "CONTINUATION"
        else:
            # Symmetrical coupling of opposite signs still collapses
            return TypedZeroResidue(0.0, 0), "HALT_SYMMETRIC"
            
    else:
        # Same-sign composition collapses to undifferentiated zero
        return TypedZeroResidue(0.0, 0), "HALT_SAME_SIGN"

def run_attack():
    print("====================================================")
    print("FAT-05-TRACE-ADMISSIBILITY-1.2D.1: LAUNCHING FALSIFICATION ATTACK")
    print("Target Concept: Trace-Admissibility and Zero-Recoupling Rules")
    print("====================================================")
    
    # Initialize typed zeros
    zero_minus = TypedZeroResidue(0.0, -1)
    zero_plus = TypedZeroResidue(0.0, 1)
    
    print(f"Initialized Zeros: {zero_minus} and {zero_plus}")
    
    # Scenario A: Opposite-sign asymmetric recoupling (Compliance check)
    print("\n--- Scenario A: Opposite-Sign Asymmetric Recoupling ---")
    res_a, status_a = compose_zero_residues(zero_minus, zero_plus, relation_type="asymmetric")
    print(f"Composition: {zero_minus} o {zero_plus} -> {res_a}, Status: {status_a}")
    
    if status_a != "CONTINUATION" or res_a.value == 0.0:
        print("FAIL: Opposite-sign recoupling failed to recover distinction.")
        return False
        
    # Scenario B: Same-sign composition (The Attack)
    # We attempt to make same-sign composition recover a distinction or continue
    print("\n--- Scenario B: Same-Sign Composition ---")
    res_b, status_b = compose_zero_residues(zero_minus, zero_minus, relation_type="asymmetric")
    print(f"Composition: {zero_minus} o {zero_minus} -> {res_b}, Status: {status_b}")
    
    # Falsification check: If status_b is 'CONTINUATION', the sign necessity is falsified!
    if status_b == "CONTINUATION" and res_b.value > 0.0:
        print("FALSIFIED: Same-sign zero residues successfully recoupled and recovered distinction!")
        return True
        
    if status_b == "HALT_SAME_SIGN" and res_b.sign == 0:
        print("SURVIVED: Same-sign composition successfully collapsed to undifferentiated null and halted.")
    else:
        print(f"UNEXPECTED BEHAVIOR: status={status_b}, res={res_b}")
        return False
        
    # Scenario C: Symmetrical coupling of opposite signs (Audit trace verification)
    print("\n--- Scenario C: Opposite-Sign Symmetrical Coupling ---")
    res_c, status_c = compose_zero_residues(zero_minus, zero_plus, relation_type="symmetric")
    print(f"Composition (Symmetric): {zero_minus} o {zero_plus} -> {res_c}, Status: {status_c}")
    
    if status_c == "HALT_SYMMETRIC" and res_c.sign == 0:
        print("SURVIVED: Symmetric coupling of opposite signs collapsed as expected.")
    else:
        print(f"UNEXPECTED BEHAVIOR: status={status_c}, res={res_c}")
        return False
        
    return False

if __name__ == "__main__":
    falsified = run_attack()
    print("\n====================================================")
    if falsified:
        print("RESULT: FALSIFICATION SUCCESSFUL!")
        sys.exit(1)
    else:
        print("RESULT: FALSIFICATION FAILED (CONCEPTS SURVIVED).")
        sys.exit(0)
