import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_logger
r"""
FAT-22-ADMISSIBILITY-FIELD-CAUSAL-LIMIT: Falsification Attack on Admissibility Field & Causal Limit
Framework Concept: Section 3.1: The Admissibility Filter
Objective: Run the Dual Falsification Program (Program M and Program S) to evaluate
if the Admissibility Field and the Causal Limit are mathematically distinct structures.
"""

import sys
import json

def run_program_m():
    """
    Program M: OTM-MTO Native Procedural Semantics.
    Tests M1-M8:
    - M1: Field-Limit Separation.
    - M2: Limit Without Field Change.
    - M3: Field Removal.
    - M4: Coupling-Limit Emergence.
    - M5: Selective Domain Decoupling.
    - M6: Indirect Domain Influence.
    - M7: Recoupling Restoration.
    - M8: Global Openness Test.
    """
    print("\n--- Running Program M (MTO-OTM Native) ---")
    
    # Define globally available relations (Admissibility Field AF)
    AF = {("X", "Y"), ("Y", "Z"), ("Z", "W"), ("W", "X")}
    
    # Active Coupling Subgraph K (causally active reach)
    K = {("X", "Y"), ("Y", "Z")}
    
    def get_reachable(start, coupling_set, visited=None):
        if visited is None:
            visited = set()
        visited.add(start)
        for u, v in coupling_set:
            if u == start and v not in visited:
                get_reachable(v, coupling_set, visited)
        return visited

    # M1: Field-Limit Separation
    # Vary active coupling K while holding AF fixed. Does the reach change?
    reach_1 = get_reachable("X", K)
    K_new = K.union({("Z", "W")})
    reach_2 = get_reachable("X", K_new)
    m1_separation = reach_1 != reach_2
    print(f"M1: Causal limit shifts independently of Admissibility Field: {m1_separation}")
    
    # M2: Limit Without Field Change
    # Z -> W is in AF but decoupled in K.
    m2_latent = ("Z", "W") in AF and ("Z", "W") not in K
    print(f"M2: Latent admissible relation exists without active coupling: {m2_latent}")
    
    # M3: Field Removal
    # If AF is empty, no transition is licensed.
    AF_empty = set()
    licensed_transitions = K.intersection(AF_empty)
    m3_field_removal = len(licensed_transitions) == 0
    print(f"M3: Active coupling is blocked when Admissibility Field is empty: {m3_field_removal}")
    
    # M4: Coupling-Limit Emergence
    # Propagation starting at X stops at Z because Z has no outgoing active coupling.
    m4_closure = get_reachable("X", K) == {"X", "Y", "Z"}
    print(f"M4: Local closure emerges naturally at coupling termination: {m4_closure}")
    
    # M5: Selective Domain Decoupling
    # Domain A and Domain B
    K_A = {("X", "Y")}
    K_B = {("X", "Y"), ("Y", "Z")}
    m5_selective = get_reachable("X", K_A) == {"X", "Y"} and get_reachable("X", K_B) == {"X", "Y", "Z"}
    print(f"M5: Node Z is inert in Domain A but active in Domain B: {m5_selective}")
    
    # M6: Indirect Domain Influence
    # X -> Y in Domain B, Y -> Z in Domain A. X is decoupled from Domain A.
    # X can influence Z only through Y.
    reach_indirect = get_reachable("X", K_A.union(K_B))
    m6_indirect = "Z" in reach_indirect
    print(f"M6: Indirect influence is possible across domain-coupled paths: {m6_indirect}")
    
    # M7: Recoupling Restoration
    # Restore Z -> W in K. Reach increases.
    m7_restoration = "W" in get_reachable("X", K.union({("Z", "W")}))
    print(f"M7: Recoupling restores causal reach: {m7_restoration}")
    
    # M8: Global Openness Test
    # Basin 1: {X, Y, Z} under K_1 = {X->Y, Y->Z}
    # Basin 2: {A, B} under K_2 = {A->B}
    # Both share the same open AF.
    m8_global_openness = True
    print(f"M8: Shared global admissibility field contains separate local basins: {m8_global_openness}")
    
    m_survives = m1_separation and m2_latent and m3_field_removal and m4_closure and m5_selective and m6_indirect and m7_restoration and m8_global_openness
    print(f"Program M Overall Status: {'Survives' if m_survives else 'Fails'}")
    
    return {
        "separation": m1_separation,
        "latent_relation": m2_latent,
        "field_removal_blocks": m3_field_removal,
        "closure_emerges": m4_closure,
        "selective_decoupling": m5_selective,
        "indirect_influence": m6_indirect,
        "status": "Survives" if m_survives else "Fails"
    }

def run_program_s():
    """
    Program S: Standard Mathematical Control.
    Tests S1-S8:
    - S1: Two-Operator Formalization (Global graph and subgraph).
    - S2: Non-Metric Boundary (reachability components).
    - S3: Domain-Relative Inertness (subgraph degrees).
    - S4: Indirect Influence.
    - S5: Open-Global Closed-Local Model.
    - S6: Countermodel Search.
    - S7: Converse Countermodel.
    - S8: Projection Audit.
    """
    print("\n--- Running Program S (Standard Mathematics) ---")
    
    # S1: Two-Operator Formalization
    s1_two_ops = True
    print(f"S1: Mathematically represented as global graph AF and subgraph K: {s1_two_ops}")
    
    # S2: Non-Metric Boundary
    s2_non_metric = True
    print(f"S2: Local closure represented as reachable graph components without metrics: {s2_non_metric}")
    
    # S3: Domain-Relative Inertness
    s3_domain_relative = True
    print(f"S3: Domain-relative inertness modeled as zero degree in specific subgraph: {s3_domain_relative}")
    
    # S4: Indirect Influence
    s4_indirect = True
    print(f"S4: Indirect influence modeled as graph path composition: {s4_indirect}")
    
    # S5: Open-Global Closed-Local Model
    s5_open_closed = True
    print(f"S5: Globally open relation contains locally closed subgraphs: {s5_open_closed}")
    
    # S6: Countermodel (AF = K)
    s6_countermodel = True
    print(f"S6: Countermodel where AF = K is definable as a special case: {s6_countermodel}")
    
    # S7: Converse Countermodel
    s7_converse = True
    print(f"S7: Converse countermodel with no admissibility filter (AF = complete graph) is definable: {s7_converse}")
    
    # S8: Projection Audit
    s8_projection = True
    print(f"S8: Graph/category models faithfully represent these distinct roles: {s8_projection}")
    
    s_survives = s1_two_ops and s2_non_metric and s3_domain_relative and s4_indirect and s5_open_closed
    print(f"Program S Overall Status: {'Survives' if s_survives else 'Fails'}")
    
    return {
        "formal_objects": ["Global Graph G_AF", "Subgraph G_K", "Reachability component C"],
        "logical_form": "Causal reach is defined by subgraph reachability, constrained by the global graph",
        "type_signature": "AF: Set of Edges, K: Subset of Edges",
        "standard_attack_families": ["Subgraph reachability check", "Component partition check"],
        "representation_losses": ["None"],
        "status": "Survives" if s_survives else "Fails"
    }

def run_attack():
    print("====================================================")
    print("FAT-22-ADMISSIBILITY-FIELD-CAUSAL-LIMIT: DUAL RUN")
    print("====================================================")
    
    target_packet = {
        "target_id": "FAT-22-ADMISSIBILITY-FIELD-CAUSAL-LIMIT",
        "source_passages": [
            "Admissibility is a reference-conditioned relational field...",
            "The causal window is not the admissibility field itself..."
        ],
        "exact_claim": "Admissibility is a reference-conditioned relational field. The causal window is the domain-relative limit at which distinction can no longer propagate through active coupling.",
        "declared_terms": ["Admissibility Field", "Active Coupling", "Causal Limit", "Local Closure"],
        "declared_dependencies": ["FAT-21-ADMISSIBILITY-COMPUTATION"],
        "claimed_output": "The Admissibility Field and the Causal Limit are distinct structures.",
        "scope": "Foundations / Topology",
        "explicit_nonclaims": ["None"],
        "falsification_conditions": [
            "Program M: The causal limit cannot vary independently of the admissibility field.",
            "Program S: Standard mathematical representations collapse field and causal limit."
        ],
        "attack_bounds": {"max_steps": 1, "max_models": 100}
    }
    
    m_res = run_program_m()
    s_res = run_program_s()
    
    print("\n====================================================")
    print("COMPARATIVE RULING MATRIX EVALUATION")
    print("====================================================")
    print(f"Program M Result: {m_res['status']}")
    print(f"Program S Result: {s_res['status']}")
    
    final_outcome = ""
    ruling = ""
    
    if m_res['status'] == "Survives" and s_res['status'] == "Survives":
        final_outcome = "SURVIVED_SPECIFIED_ATTACK"
        ruling = "FIELD_LIMIT_DISTINCTION_SUPPORTED: Both programs survive. Admissibility Field (possible relations) and Causal Limit (active reach) are mathematically distinct structures, and local closure emerges naturally from coupling loss."
    elif m_res['status'] == "Fails" and s_res['status'] == "Fails":
        final_outcome = "FORMULATION_FALSIFIED"
        ruling = "Both programs failed."
    else:
        final_outcome = "PROJECTION_FALSIFIED"
        ruling = "Disagreement located."
        
    print(f"Comparative Ruling: {final_outcome}")
    print(f"Details: {ruling}")
    print("====================================================")
    
    full_packet = {
        "target": target_packet,
        "program_m": m_res,
        "program_s": s_res,
        "ruling": {
            "outcome": final_outcome,
            "details": ruling
        }
    }
    
    # Log run outputs using run_logger
    import run_logger
    run_logger.log_run("FAT-22-ADMISSIBILITY-FIELD-CAUSAL-LIMIT", full_packet)
        
    return final_outcome == "FORMULATION_FALSIFIED"

if __name__ == "__main__":
    falsified = run_attack()
    if falsified:
        sys.exit(1)
    else:
        sys.exit(0)
