# TDA Adjacency Threshold Policy (AUDIT-003)

This document defines the policy for converting adjacency matrices to graphs within the TDA module.

## 1. Objective
To prevent numerical noise in weighted adjacency matrices from creating spurious topological connections during graph construction in `NetworkX`.

## 2. Threshold Policy
- **Parameter:** `adjacency_threshold`
- **Application:** Applied to the absolute magnitude of all entries in the adjacency matrix before `nx.from_numpy_array`.
- **Logic:** $A_{ij} = 0$ if $|A_{ij}| \leq \text{threshold}$, else $A_{ij}$ is preserved.

## 3. Default Behavior
- **Current Default:** `0.0`
- **Rationale:** Preserves backward compatibility with legacy results where any non-zero value was treated as an edge.
- **Risk:** High sensitivity to floating-point noise (e.g., $10^{-16}$).

## 4. Recommended Configuration
- For research runs requiring high topological robustness, a threshold of $10^{-12}$ or higher is recommended.
- The threshold must be explicitly documented in simulation configurations or paper metadata if non-default.

## 5. Governance Constraints
- **Claimhumility:** Topological claims based on default (0.0) thresholds must acknowledge the risk of numerical artifacts if signal noise is present.
- **Verification:** Any `implementation_verified` topological claim must pass the noise-guard test suite with an appropriate threshold.
