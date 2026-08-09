"""
FAT-13-ORIENTATION-COHERENCE-IT: Falsification Attack on Orientation Coherence Metric Candidate
Framework Concept: Orientation Coherence Metric Candidate (Formal Statement 5.1.5)
External Discipline: Information Theory
Objective: Prove that the variance-based C_orient metric is mathematically flawed
because it misclassifies highly structured, low-entropy bimodal states as completely incoherent.
We compare:
1. Variance-based metric C_orient (mean resultant length R).
2. Information-theoretic coherence C_entropy (1 - H/H_max).
"""

import sys
import math
import collections

def c_orient(orientations):
    """
    Computes the circular variance-based coherence metric.
    """
    if not orientations:
        return 0.0
    n = len(orientations)
    sum_cos = sum(math.cos(theta) for theta in orientations)
    sum_sin = sum(math.sin(theta) for theta in orientations)
    mean_cos = sum_cos / n
    mean_sin = sum_sin / n
    return math.sqrt(mean_cos**2 + mean_sin**2)

def c_entropy(orientations, num_bins=36):
    """
    Computes the information-theoretic coherence based on Shannon Entropy.
    """
    if not orientations:
        return 0.0
    # Bin the angles into num_bins equal intervals in [-pi, pi]
    bin_size = 2 * math.pi / num_bins
    bins = []
    for theta in orientations:
        # Map to [-pi, pi]
        theta_mapped = (theta + math.pi) % (2 * math.pi) - math.pi
        bin_idx = int((theta_mapped + math.pi) / bin_size)
        bin_idx = min(bin_idx, num_bins - 1)
        bins.append(bin_idx)
        
    counts = collections.Counter(bins)
    n = len(orientations)
    entropy = 0.0
    for count in counts.values():
        p = count / n
        entropy -= p * math.log2(p)
        
    # Max entropy is log2(num_bins)
    h_max = math.log2(num_bins)
    return 1.0 - (entropy / h_max)

def run_attack():
    print("====================================================")
    print("FAT-13-ORIENTATION-COHERENCE-IT: INFORMATION THEORY ATTACK")
    print("====================================================")
    
    # Construct a bimodal structured state: half pointing at 0, half pointing at pi
    n_samples = 1000
    bimodal_orientations = []
    for i in range(n_samples):
        if i % 2 == 0:
            bimodal_orientations.append(0.0)
        else:
            bimodal_orientations.append(math.pi)
            
    score_rt = c_orient(bimodal_orientations)
    score_it = c_entropy(bimodal_orientations)
    
    print("Bimodal Structured State (Bipolar Alignment):")
    print(f"  Variance-based C_orient: {score_rt:.6f} (classifies as fully incoherent)")
    print(f"  Information Theory C_entropy: {score_it:.6f} (classifies as highly coherent)")
    
    # Falsification logic:
    # If the variance-based metric gives a score < 0.01 for a bimodal structured state
    # while the entropy-based metric correctly identifies it as highly coherent (> 0.7),
    # the variance-based coherence metric is falsified.
    
    falsified = False
    if score_rt < 0.01 and score_it > 0.7:
        print("\nRESULT: FALSIFICATION SUCCESSFUL!")
        print("The variance-based metric fails to detect multi-modal structured coherence.")
        print("It treats bipolar alignment as completely random, violating Information Theory.")
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
