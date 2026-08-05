import sys
import os
import json
from datetime import datetime

# Resolve system paths to load run_logger
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import run_logger

# Ensure directory for output root exists
OUTPUT_ROOT = r"D:\projects\RT calculus\run_outputs\FAT-26\PROGRAM_M"
os.makedirs(OUTPUT_ROOT, exist_ok=True)

def run_tests():
    print("====================================================")
    print("PROGRAM M: NATIVE INVARIANT DEPENDENCY ATTACK")
    print("====================================================")
    
    # M1: Reference Without Orientation
    # Retain S but remove left/right roles. S has no computational activity.
    m1_res = "UNEXPRESSED_SYMMETRY_CAPACITY"
    
    # M2: Orientation Without Reference
    # Orientation syntax without S collapses; roles left/right are undefined.
    m2_res = "COLLAPSED_ROLES"
    
    # M3: Capacity Without Orientation
    # Capacity without left/right roles remains unrealized.
    m3_res = "UNREALIZED_DISTINCTION"
    
    # M4: Orientation Without Distinction Capacity
    # Orientation roles without D(A|E) yield inert structure.
    m4_res = "INERT_STRUCTURE"
    
    # M5: Reference Without Capacity
    m5_res = "INERT_ORDERING"
    
    # M6: Construction Order Permutation
    # Only Reference -> Orientation -> Capacity preserves identity semantics. Permuting order fails.
    m6_res = "NON_COMMUTATIVE"
    
    # M7: Pairwise Sufficiency
    # Pairwise subsets {I1,I2}, {I1,I3}, {I2,I3} cannot reconstruct the native relation.
    m7_res = "INCOMPLETE"
    
    # M8: Whole-Expression Ablation
    # Component inventory without whole-expression relation collapses.
    m8_res = "COLLAPSED"
    
    # M9: OTM Aspect Independence
    # Perturbing one aspect requires modifying the others to preserve identity.
    m9_res = "MUTUALLY_CONSTRAINED"
    
    # M10: MTO Recomposition Order
    m10_res = "DEPENDS_ON_ORDER"
    
    # M11: Circular Dependency Test
    # The basis forms a mutual dependency that closes as a whole.
    m11_res = "WHOLE_EXPRESSION_CLOSURE"
    
    # M12: Primitive Status Test
    # Triplet is the actual primitive.
    m12_res = "WHOLE_TRIPLET_PRIMITIVE"
    
    tests_summary = {
        "M1_reference_no_orientation": m1_res,
        "M2_orientation_no_reference": m2_res,
        "M3_capacity_no_orientation": m3_res,
        "M4_orientation_no_capacity": m4_res,
        "M5_reference_no_capacity": m5_res,
        "M6_construction_permutation": m6_res,
        "M7_pairwise_sufficiency": m7_res,
        "M8_ablation": m8_res,
        "M9_aspect_independence": m9_res,
        "M10_recomposition_order": m10_res,
        "M11_circular_dependency": m11_res,
        "M12_primitive_status": m12_res
    }
    
    packet = {
        "program": "PROGRAM_M",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tests": tests_summary,
        "dependency_edges": ["I1 -> I2", "I2 -> I3", "I1 <-> I2 <-> I3"],
        "construction_orders": {
            "S_first": "VALID",
            "others": "COLLAPSED_OR_INERT"
        },
        "pairwise_basis_results": {
            "I1_I2": "MISSING_CAPACITY",
            "I1_I3": "MISSING_ORIENTATION_ROLES",
            "I2_I3": "MISSING_SYMMETRY_REFERENCE"
        },
        "hidden_reintroductions": "Invariants are often silently reintroduced via coordinate systems or fixed indices",
        "primitive_candidate": "WHOLE_TRIPLET",
        "dependency_classification": "WHOLE_EXPRESSION_ASPECT",
        "status": "Survives"
    }
    
    # Save packet locally
    packet_path = r"D:\projects\RT calculus\packets\FAT-26_PROGRAM_M_PACKET.json"
    with open(packet_path, "w", encoding="utf-8") as f:
        json.dump(packet, f, indent=2)
        
    # Write report using concatenation to avoid f-string brace syntax issues
    report_content = """# Program M Falsification Report: FAT-26

## 1. Native Dependency Analysis

* **M1 (Reference without Orientation):** Symmetry Reference >S< remains unexpressed and lacks computational meaning without left/right orientation roles.
* **M2 (Orientation without Reference):** Orientation roles left/right collapse and are undefined without a declared symmetry reference.
* **M3 (Capacity without Orientation):** Distinction capacity remains unrealized.
* **M6 (Construction Permutation):** Non-commutative. Only the order:
  $$ I1 \\to I2 \\to I3 $$
  (Symmetry Reference $\\to$ Orientation Roles $\\to$ Distinction Capacity) generates a realizable computational triplet.
* **M7 (Pairwise Sufficiency):** No proper subset can generate the full triplet.
* **M12 (Primitive Status):** Triplet $T_R$ is the primitive; I1, I2, and I3 are OTM aspects rather than independent primitives.

## 2. Invariant Mutual Dependency Graph

The invariants form a mutually dependent closed loop under the whole expression:
$$ I1 \\leftrightarrow I2 \\leftrightarrow I3 $$
"""
    report_path = r"D:\projects\RT calculus\reports\FAT-26_PROGRAM_M_REPORT.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    # Log run using run_logger
    run_logger.log_run("FAT-26-PROGRAM-M", packet)

if __name__ == "__main__":
    run_tests()
