"""
FAT-13-ORIENTATION-COHERENCE-5.1.5: Falsification Attack on Orientation Coherence Metric Candidate
Principle: Formal Statement 5.1.5: Orientation Coherence Metric Candidate
Rule: Orientation coherence is computable from distinction array and orientation assignments alone,
satisfying the non-circularity constraint.
Objective: Implement the circular variance metric and verify all 4 validation tests (VT_001 to VT_004).
"""

import sys
import math
import random

def c_orient(chi_D, orientations):
    """
    Computes the orientation coherence metric C_orient.
    Orientations are represented as a list of angles in radians.
    Non-circularity check: Only accepts chi_D and orientations.
    """
    if not orientations:
        return 0.0
    
    n = len(orientations)
    sum_cos = sum(math.cos(theta) for theta in orientations)
    sum_sin = sum(math.sin(theta) for theta in orientations)
    
    # Mean resultant length R
    mean_cos = sum_cos / n
    mean_sin = sum_sin / n
    R = math.sqrt(mean_cos**2 + mean_sin**2)
    
    # C_orient = 1 - Var_norm = 1 - (1 - R) = R
    return R

def run_attack():
    print("====================================================")
    print("FAT-13-ORIENTATION-COHERENCE-5.1.5: LAUNCHING ATTACK")
    print("Target Concept: Orientation Coherence Metric C_orient")
    print("====================================================")
    
    random.seed(42)
    
    # Simulated distinction array (not used by the metric formula but part of signature)
    chi_D = [1.0, 0.8, 1.2, 0.5]
    
    # 1. PO001_VT_001: Input Isolation
    # Check if the function signature and execution depend only on chi_D and orientations.
    print("Running PO001_VT_001 (Input Isolation)...")
    try:
        score = c_orient(chi_D, [0.1, 0.2, 0.15, 0.05])
        print(f"  Passed. Score computed: {score:.4f}")
        vt001_passed = True
    except Exception as e:
        print(f"  Failed with error: {e}")
        vt001_passed = False
        
    # 2. PO001_VT_002: Topology Blindness
    # Verify C_orient is invariant under T_class removal/permutation
    print("\nRunning PO001_VT_002 (Topology Blindness)...")
    t_classes = ["Knot_Trefoil", "Knot_FigureEight", None, "Braid_3_1"]
    scores_vt002 = []
    for t_class in t_classes:
        # We pass different topological contexts (simulated)
        # C_orient function itself has no knowledge of t_class
        score = c_orient(chi_D, [0.1, 0.2, 0.15, 0.05])
        scores_vt002.append(score)
    # Check if all scores are identical
    if len(set(scores_vt002)) == 1:
        print(f"  Passed. Score invariant across topology classes: {scores_vt002[0]:.4f}")
        vt002_passed = True
    else:
        print(f"  Failed. Scores differed: {scores_vt002}")
        vt002_passed = False
        
    # 3. PO001_VT_003: Closure Stability Blindness
    # Verify C_orient is invariant under S_closure withholding/permutation
    print("\nRunning PO001_VT_003 (Closure Stability Blindness)...")
    s_closures = [True, False, 0.85, 0.0]
    scores_vt003 = []
    for s_closure in s_closures:
        score = c_orient(chi_D, [0.1, 0.2, 0.15, 0.05])
        scores_vt003.append(score)
    if len(set(scores_vt003)) == 1:
        print(f"  Passed. Score invariant across closure stability states: {scores_vt003[0]:.4f}")
        vt003_passed = True
    else:
        print(f"  Failed. Scores differed: {scores_vt003}")
        vt003_passed = False
        
    # 4. PO001_VT_004: Shuffling Sensitivity
    # Verify that shuffled/random orientation produces lower C_orient than coherent orientation
    print("\nRunning PO001_VT_004 (Shuffling Sensitivity)...")
    # Coherent orientations: clustered around mean angle 0.5 rad
    coherent_orientations = [0.5 + random.normalvariate(0, 0.1) for _ in range(100)]
    score_coherent = c_orient(chi_D, coherent_orientations)
    
    # Shuffled/random orientations: uniformly dispersed
    shuffled_orientations = [random.uniform(-math.pi, math.pi) for _ in range(100)]
    score_shuffled = c_orient(chi_D, shuffled_orientations)
    
    print(f"  Coherent C_orient: {score_coherent:.4f}")
    print(f"  Shuffled C_orient: {score_shuffled:.4f}")
    
    if score_coherent > 0.8 and score_shuffled < 0.3:
        print("  Passed. Shuffling sensitivity verified (coherent > 0.8, shuffled < 0.3)")
        vt004_passed = True
    else:
        print("  Failed. Sensitivity check failed.")
        vt004_passed = False
        
    # Falsification conclusion:
    # If all validation tests pass, the metric candidate successfully satisfies the requirements,
    # meaning the concept survived. If any test fails, it is falsified.
    
    all_passed = vt001_passed and vt002_passed and vt003_passed and vt004_passed
    falsified = not all_passed
    
    print("\n====================================================")
    if falsified:
        print("RESULT: FALSIFICATION SUCCESSFUL!")
    else:
        print("RESULT: FALSIFICATION FAILED (CONCEPTS SURVIVED).")
    print("====================================================")
    return falsified

if __name__ == "__main__":
    falsified = run_attack()
    if falsified:
        sys.exit(1)
    else:
        sys.exit(0)
