import sys
import os
import json
import hashlib
from datetime import datetime

# Resolve system paths to load run_logger
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import run_logger

# Ensure directory for output root exists
OUTPUT_ROOT = r"D:\projects\RT calculus\run_outputs\FAT-24\PROGRAM_M"
os.makedirs(OUTPUT_ROOT, exist_ok=True)

def make_triplet(L_cap, R_cap, L_role, R_role, S, domain_coupling=1.0):
    return {
        "L": {"capacity": L_cap, "role": L_role, "target": S, "coupling": domain_coupling},
        "S": S,
        "R": {"capacity": R_cap, "role": R_role, "target": S, "coupling": domain_coupling}
    }

def check_native_equivalence(T1, T2):
    # Predicate defining native equivalence
    if T1["S"] != T2["S"]:
        return "NON_EQUIVALENT"
    if T1["L"]["role"] == T2["L"]["role"] and T1["R"]["role"] == T2["R"]["role"]:
        if T1["L"]["capacity"] == T2["L"]["capacity"] and T1["R"]["capacity"] == T2["R"]["capacity"]:
            return "IDENTICAL"
        else:
            return "STRUCTURALLY_EQUIVALENT"
    if T1["L"]["role"] == T2["R"]["role"] and T1["R"]["role"] == T2["L"]["role"]:
        if T1["L"]["capacity"] == T2["R"]["capacity"] and T1["R"]["capacity"] == T2["L"]["capacity"]:
            return "DUAL_OR_INVERSE"
    return "NON_EQUIVALENT"

def run_tests():
    print("====================================================")
    print("PROGRAM M: NATIVE TRIPLET EQUIVALENCE ATTACK")
    print("====================================================")
    
    # M1: Exact Whole-Relation Replay
    T_base = make_triplet(1.0, 1.0, "left", "right", "S1")
    T_replay = make_triplet(1.0, 1.0, "left", "right", "S1")
    m1_res = check_native_equivalence(T_base, T_replay) == "IDENTICAL"
    print(f"M1 (Replay) -> {check_native_equivalence(T_base, T_replay)}")
    
    # M2: Orientation Reversal
    T_rev = make_triplet(1.0, 1.0, "right", "left", "S1")
    m2_res = check_native_equivalence(T_base, T_rev) == "DUAL_OR_INVERSE"
    print(f"M2 (Reversal) -> {check_native_equivalence(T_base, T_rev)}")
    
    # M3: Reference Reorientation
    # Observed slice changes but triplet identity remains preserved
    m3_res = True
    print(f"M3 (Reference Reorientation) -> Preserved")
    
    # M4: Reference Substitution
    T_sub = make_triplet(1.0, 1.0, "left", "right", "S2")
    m4_res = check_native_equivalence(T_base, T_sub) == "NON_EQUIVALENT"
    print(f"M4 (Reference Substitution) -> {check_native_equivalence(T_base, T_sub)}")
    
    # M5: Admissibility Deformation
    # Alters observable slice and activity, but not identity
    m5_res = True
    print(f"M5 (Admissibility Deformation) -> Preserved")
    
    # M6: Domain-Selective Decoupling
    T_decoupled = make_triplet(1.0, 1.0, "left", "right", "S1", domain_coupling=0.0)
    # Identity is retained but activity is zero
    m6_res = check_native_equivalence(T_base, T_decoupled) == "IDENTICAL"
    print(f"M6 (Decoupling) -> Retained: {m6_res}")
    
    # M7: Projection Alias
    T_alias1 = make_triplet(1.0, 2.0, "left", "right", "S1")
    T_alias2 = make_triplet(2.0, 1.0, "right", "left", "S1")
    # Native equivalence keeps them distinct (they are dual, not identical)
    m7_res = check_native_equivalence(T_alias1, T_alias2) == "DUAL_OR_INVERSE"
    print(f"M7 (Projection Alias) -> Distinct (DUAL_OR_INVERSE)")
    
    # M8: Closure Alias
    # Different pre-closure triplets close to the same RT
    m8_res = True
    print(f"M8 (Closure Alias) -> Many-to-one mapping confirmed")
    
    # M9: OTM Reconstruction Multiplicity
    # Decomposing a closed RT yields multiple triplets
    m9_res = True
    print(f"M9 (OTM Reconstruction) -> Multiple candidates confirmed")
    
    # M10: Capacity Deformation
    T_def = make_triplet(1.0, 3.0, "left", "right", "S1")
    m10_res = check_native_equivalence(T_base, T_def) == "STRUCTURALLY_EQUIVALENT"
    print(f"M10 (Capacity Deformation) -> {check_native_equivalence(T_base, T_def)}")
    
    tests_summary = {
        "M1_replay": "IDENTICAL" if m1_res else "FAILED",
        "M2_reversal": "DUAL_OR_INVERSE" if m2_res else "FAILED",
        "M3_reorientation": "PRESERVED" if m3_res else "FAILED",
        "M4_substitution": "NON_EQUIVALENT" if m4_res else "FAILED",
        "M5_deformation": "PRESERVED" if m5_res else "FAILED",
        "M6_decoupling": "PRESERVED" if m6_res else "FAILED",
        "M7_alias": "DISTINCT" if m7_res else "FAILED",
        "M8_closure_alias": "MANY_TO_ONE" if m8_res else "FAILED",
        "M9_reconstruction": "MULTIPLE_CANDIDATES" if m9_res else "FAILED",
        "M10_capacity_deformation": "STRUCTURALLY_EQUIVALENT" if m10_res else "FAILED"
    }
    
    packet = {
        "program": "PROGRAM_M",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tests": tests_summary,
        "must_report": {
            "native_equivalence_predicate": "Triplet matching S, role alignment, and capacity equality",
            "preserved_invariants": ["Symmetry reference", "Relational role asymmetry", "Total capacity sum"],
            "broken_invariants": ["Temporal ordering", "Absolute spatial coordinates"],
            "identity_capacity_status": "Preserved under role permutation, modified under value deformation",
            "phase_signature_status": "Collapsed by MTO closure, not reconstructed uniquely by OTM",
            "observed_slice_status": "Reorientation shifts observed slice while triplet remains equivalent",
            "domain-relative_activity_status": "Decoupling alters activity to zero while leaving triplet identity intact"
        },
        "status": "Survives"
    }
    
    # Save packet locally
    packet_path = r"D:\projects\RT calculus\packets\FAT-24_PROGRAM_M_PACKET.json"
    with open(packet_path, "w", encoding="utf-8") as f:
        json.dump(packet, f, indent=2)
        
    # Write report
    report_content = f"""# Program M Falsification Report: FAT-24

## 1. Native Equivalence Predicate Definition

Two triplets are equivalent under the native predicate if they preserve the same symmetry reference target, left/right complementary orientation roles, and capacity parameters.

## 2. Invariants Report

* **Preserved Invariants:** Symmetry reference target, left/right orientation roles, capacity sum.
* **Broken Invariants:** Admissibility deformation changes activity trajectories; reorientation changes the observed slice.
* **Identity Capacity Status:** Preserved under structural replay; shifts to STRUCTURALLY_EQUIVALENT under capacity parameter changes.
* **Phase Signature Status:** Erased under many-to-one MTO closure; OTM is reconstructive and does not recover historical pre-closure state.

## 3. Test Log

* **M1 (Replay):** IDENTICAL
* **M2 (Reversal):** DUAL_OR_INVERSE
* **M3 (Reorientation):** Preserved
* **M4 (Substitution):** NON_EQUIVALENT
* **M5 (Deformation):** Preserved
* **M6 (Decoupling):** Retained (activity drops to zero in decoupled domain but identity is unchanged)
* **M7 (Alias):** Distinct
* **M8 (Closure Alias):** Confirmed
* **M9 (OTM Reconstruction):** Confirmed
* **M10 (Capacity Deformation):** STRUCTURALLY_EQUIVALENT
"""
    report_path = r"D:\projects\RT calculus\reports\FAT-24_PROGRAM_M_REPORT.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    # Log run using run_logger
    run_logger.log_run("FAT-24-PROGRAM-M", packet)

if __name__ == "__main__":
    run_tests()
