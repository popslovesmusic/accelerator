# Law-021: Finite Admissibility Budget Law

## 1. Definition
The **Finite Admissibility Budget Law** formalizes continuation as a budget-constrained process. It defines how finite admissibility capacity, both local and regional, limits the propagation, transport, and reinforcement of continuation events across the orientation array.

## 2. Formal Statement
Within the recursive continuation framework:

- **Orientation Array**: {-(i)_α}
- **Local Budget**: $B_A(\alpha)$ (Local admissibility capacity)
- **Regional Budget**: $B_A(U)$ (Aggregated capacity in region $U$)
- **Continuation Cost**: $Cost_A(R_\alpha) := F(transport\_flux, admissibility\_margin\_use, projection\_cost, reinforcement\_load, reconstruction\_loss)$
- **Budget Condition**: $Continue(R_\alpha)$ is admissible if and only if $Cost_A(R_\alpha) \le B_A(\alpha)$ under a declared local tolerance.

### Depletion Condition
$B_A(\alpha, n+1)$ may decrease when continuation events consume admissibility capacity through transport, projection, or reinforcement load. High-frequency or high-flux transitions deplete the local budget.

### Recovery Condition
$B_A(\alpha, n+1)$ may recover when local reconciliation stabilizes, transport flux decreases, or boundary pressure (epsilon) relaxes. Stability promotes budget restoration.

### Saturation Condition
$Saturate(\alpha)$ occurs when the continuation demand (cost) exceeds the available admissibility budget. Saturation triggers stabilizing failure modes:
- **Pruning**: Dropping low-support continuation branches.
- **Delay**: Reducing update frequency (apparent time dilation).
- **Redirection**: Forcing continuation into lower-cost channels.
- **Collapse**: Dissolving a continuation structure that cannot be maintained.
- **Horizon Formation**: Limiting the reach of influence ($H_A$).

## 3. Core Principles
- **Finite Capacity**: Continuation is not free; it requires a finite, locally resolved "support budget."
- **Cost-Benefit Admissibility**: Processes compete for budget; selection ($\delta$) is constrained by available capacity.
- **Dynamic Resource Partitioning**: Budgets are local and regional, not global; influence is limited by the ability to sustain the "cost" of propagation.
- **Stabilization Through Failure**: Saturation-triggered failures (like pruning) are essential for maintaining the integrity of the remaining continuation pathways.

## 4. Governance & Limits
- **No Physics Claim**: This law defines admissibility budgets within the Mono-Process Framework and does not claim to describe physical energy or universal thermodynamics.
- **No Energy Equivalence**: $B_A$ is not claimed to be equivalent to physical energy, work, or heat.
- **No Global Conservation**: There is no claim of global budget conservation; budgets are emergent, local/regional, and subject to depletion/recovery.
- **No Infinite Capacity**: The assumption of "infinite" admissibility for any process is explicitly blocked.
- **No Resource Substance**: Budgets are operational measures of continuation support, not a primitive governing "fluid" or "substance."

## 5. Failure Modes
- **Unbounded Continuation Assumption**: Assuming a process can propagate indefinitely without budget constraints.
- **Infinite Admissibility Budget Overclaim**: Treating $B_A$ as an inexhaustible resource.
- **Physics Energy Equivalence Leakage**: Using energy-based terminology to justify budget dynamics.
- **Global Resource Conservation Overclaim**: Assuming total regional budget must be conserved across all transitions.
- **Budget Without Cost Definition**: Using budgets without an explicit cost function ($Cost_A$).
- **Saturation Failure Suppression**: Neglecting the necessary "failure" behaviors (pruning/collapse) when budgets are exceeded.

---
[Back to Master Index](codex_master_index.md)
