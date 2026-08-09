# MT-LAW-A: Reconstruction-Loss Geometry (Patch 036)

## 1. Purpose
This document formalizes the **Geometry of Information Loss** during structural transitions in MT-LAW-A. It models how the "shadow" cast by a phase shift or collapse limits the unique invertibility of past process states.

## 2. The Reconstruction shadow ($\mathcal{S}_R$)
The **Reconstruction Shadow** is the subset of the state-space history that becomes topologically non-invertible after the system intersects the Threshold Manifold $\mathcal{M}_S$.

### 2.1 Information Compression
When a basin ridge $\mathcal{R}_T$ is crossed, the local state is projected into a new basin. This projection is a many-to-one mapping; multiple distinct pre-transition trajectories may lead to the same post-transition fixed point.
- **Topological Invariant loss:** Transitions typically involve the destruction of prior topological invariants (e.g., specific residue gradients), rendering them unrecoverable from current observables.

### 2.2 Fidelity Decay Manifold
Reconstruction fidelity $F$ is modeled as a decaying function of the "distance" from the last stable Metastable Window $V(M_U)$.
$$ F(t_{past}) \propto \exp(-\lambda |t_{current} - t_{transition}|) $$
Where $\lambda$ is the **Transition Loss Coefficient**, which increases with the magnitude of the $S_C$ violation.

## 3. Geometric Non-Invertibility
The shadow $\mathcal{S}_R$ is characterized by the **Kernel of the Inversion Operator** ($\mathfrak{R}^{-1}$). Any process history falling within this kernel is "lost" to the system's structural memory, although it may persist as incoherent noise.

## 4. Constraint on TS5 Foundations
All geometric models in MT-LAW-A must respect the **Reconstruction Bound**: no geometric derivation may assume that the pre-collapse manifold structure can be uniquely recovered from post-collapse data.

## 5. Status Footer
- **Patch ID:** MT-LAW-A-TS5-036
- **Deliverable ID:** docs/math/mt_law_a_reconstruction_loss_geometry.md
- **Status:** LOSS_GEOMETRY_FORMALIZED
- **Compliance:** [Compliance Charter v2.3](../registry/compliance_charter_v2_3.json)
- **Math Registry:** [PCD_MT_LAW_A_BASIN_GEOMETRY_REGISTRY](../registry/math/mt_law_a_basin_geometry_registry.json)
