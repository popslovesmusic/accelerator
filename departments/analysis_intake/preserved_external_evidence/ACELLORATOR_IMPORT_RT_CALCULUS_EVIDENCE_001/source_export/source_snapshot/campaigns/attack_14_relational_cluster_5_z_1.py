"""
FAT-14-RELATIONAL-CLUSTER-5.Z.1: Falsification Attack on Relational Cluster
Framework Concept: Relational Cluster (Formal Block 5.Z.1)
External Discipline: Topology and Graph Theory
Objective: Show that the topological definition of a Relational Cluster contains
a logical contradiction. The definition requires:
1. beta_0(C) = 1 (single connected component).
2. Every pair in C must be aligned (complete graph / clique).
In Topology and Graph Theory, a single connected component (beta_0 = 1) does
not require pairwise connectivity (a clique). We construct a counterexample
chain A - B - C where beta_0 = 1, but A and C are not aligned, violating the clique axiom.
"""

import sys

def compute_betti_0(nodes, adjacency):
    """
    Computes the zeroth Betti number (number of connected components) of a graph.
    """
    visited = set()
    components = 0
    for node in nodes:
        if node not in visited:
            components += 1
            # BFS/DFS to mark all reachable nodes
            queue = [node]
            visited.add(node)
            while queue:
                current = queue.pop(0)
                for neighbor in adjacency.get(current, []):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
    return components

def run_attack():
    print("====================================================")
    print("FAT-14-RELATIONAL-CLUSTER-5.Z.1: TOPOLOGICAL ATTACK")
    print("====================================================")
    
    # Loci (processes)
    nodes = ['A', 'B', 'C']
    
    # Phase orientations (in radians)
    phases = {
        'A': 0.0,
        'B': 0.8,
        'C': 1.6
    }
    
    # Alignment threshold
    threshold = 1.05 # ~pi/3 radians
    
    # Determine pairwise alignment
    alignment = {}
    adjacency = {node: [] for node in nodes}
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            n1, n2 = nodes[i], nodes[j]
            diff = abs(phases[n1] - phases[n2])
            aligned = diff < threshold
            alignment[(n1, n2)] = aligned
            if aligned:
                adjacency[n1].append(n2)
                adjacency[n2].append(n1)
                
    print("Pairwise Alignments (Aligned Asymmetry):")
    for (n1, n2), val in alignment.items():
        print(f"  {n1} <-> {n2}: {val} (diff: {abs(phases[n1]-phases[n2]):.2f} rad)")
        
    # Compute Betti-0 (connected components)
    betti_0 = compute_betti_0(nodes, adjacency)
    print(f"\nTopological Connected Components (Betti-0): {betti_0}")
    
    # Check if the cluster forms a complete graph (clique)
    all_pairs_aligned = all(alignment.values())
    print(f"Pairwise Clique Condition (all pairs aligned): {all_pairs_aligned}")
    
    # Falsification logic:
    # If Betti-0 is 1 (the cluster is a single connected component) but the pairwise
    # clique condition is False, the definition contains a topological contradiction
    # (equating connectedness with completeness), and the concept is falsified.
    
    falsified = False
    if betti_0 == 1 and not all_pairs_aligned:
        print("\nRESULT: FALSIFICATION SUCCESSFUL!")
        print("A connected cluster (Betti-0 = 1) exists that violates the pairwise clique condition.")
        print("The definition's equivalence between Betti-0 connectedness and pairwise alignment is topologically inconsistent.")
        falsified = True
    else:
        print("\nRESULT: FALSIFICATION FAILED.")
        
    return falsified

if __name__ == "__main__":
    falsified = run_attack()
    if falsified:
        sys.exit(1)
    else:
        sys.exit(0)
